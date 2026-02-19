<template>
  <div class="history-trades-container">
    <div class="header-section">
      <h2 class="page-title">历史成交记录</h2>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-group">
        <span class="filter-label">选择日期区间:</span>
        <div class="date-picker-wrapper">
          <input type="date" v-model="startDate" :max="endDate || today" class="date-input" />
          <span class="date-separator">至</span>
          <input type="date" v-model="endDate" :min="startDate" :max="today" class="date-input" />
        </div>

        <!-- 策略选择器 -->
        <span class="filter-label">策略名称:</span>
        <div class="strategy-selector" v-click-outside="closeStrategyDropdown">
          <div class="selector-trigger" @click="toggleStrategyDropdown" :class="{ 'active': showStrategyDropdown }">
            <span class="selected-text">{{ selectedStrategiesText }}</span>
            <i class="dropdown-arrow"></i>
          </div>
          <div class="selector-dropdown" v-if="showStrategyDropdown">
            <div class="dropdown-item" :class="{ 'selected': selectedStrategies.length === 0 }" @click="clearStrategies">
              全部策略
            </div>
            <div 
              v-for="name in uniqueStrategyNames" 
              :key="name" 
              class="dropdown-item" 
              :class="{ 'selected': selectedStrategies.includes(name) }"
              @click="toggleStrategy(name)"
            >
              <span class="checkbox" :class="{ 'checked': selectedStrategies.includes(name) }"></span>
              {{ name }}
            </div>
          </div>
        </div>

        <button class="query-btn" @click="fetchData" :disabled="loading">
          {{ loading ? '查询中...' : '查询' }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <!-- 数据展示 -->
    <div v-else class="data-content">
      <div class="data-card">
        <div v-if="sortedTradeRecords.length === 0" class="empty-data">该时段暂无成交记录</div>
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-index sticky-col col-1">序号</th>
                <th>成交日期</th>
                <th class="sticky-col col-2">策略名称</th>
                <th>证券代码</th>
                <th>证券名称</th>
                <th>交易时间</th>
                <th>交易方向</th>
                <th>交易数量</th>
                <th>成交价格</th>
                <th>成交金额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in sortedTradeRecords" :key="item.id">
                <td class="col-index sticky-col col-1">{{ index + 1 }}</td>
                <td>{{ formatDate(item.trade_date) }}</td>
                <td class="sticky-col col-2">
                  <span class="strategy-badge" :class="getStrategyBadgeClass(item.strategy_name)">{{ item.strategy_name }}</span>
                </td>
                <td>{{ formatValueOrDash(item.security_code) }}</td>
                <td>{{ formatValueOrDash(item.security_name) }}</td>
                <td>{{ formatValueOrDash(item.trade_time) }}</td>
                <td :class="getDirectionClass(item.trade_direction)">{{ item.trade_direction }}</td>
                <td class="numeric-mono">{{ formatNumber(item.trade_quantity) }}</td>
                <td class="numeric-mono">{{ formatPrice(item.deal_price) }}</td>
                <td class="numeric-mono">{{ formatCurrency(Number(item.trade_quantity) * Number(item.deal_price)) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';

export default {
  name: 'HistoryTradeRecords',
  data() {
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    
    return {
      loading: false,
      error: null,
      tradeRecords: [],
      strategies: [],
      // 默认本月1号到今天
      today: this.formatToYMD(now),
      startDate: this.formatToYMD(firstDay),
      endDate: this.formatToYMD(now),
      // 策略选择
      selectedStrategies: [],
      showStrategyDropdown: false
    };
  },
  directives: {
    'click-outside': {
      mounted(el, binding) {
        el.clickOutsideEvent = function(event) {
          if (!(el === event.target || el.contains(event.target))) {
            binding.value(event);
          }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
      },
      unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent);
      }
    }
  },
  computed: {
    sortedTradeRecords() {
      return [...this.tradeRecords].sort((a, b) => {
        // 首先按成交日期倒序
        const dateA = a.trade_date || '';
        const dateB = b.trade_date || '';
        if (dateA !== dateB) {
          return dateB.localeCompare(dateA);
        }
        
        // 相同日期，按策略名称倒序
        const nameA = a.strategy_name || '';
        const nameB = b.strategy_name || '';
        return nameB.localeCompare(nameA, 'zh-CN');
      });
    },
    uniqueStrategyNames() {
      const names = this.strategies.map(s => s.strategy_name).filter(Boolean);
      return [...new Set(names)].sort((a, b) => a.localeCompare(b, 'zh-CN'));
    },
    selectedStrategiesText() {
      if (this.selectedStrategies.length === 0) return '全部策略';
      if (this.selectedStrategies.length === 1) return this.selectedStrategies[0];
      return `已选 ${this.selectedStrategies.length} 个策略`;
    }
  },
  methods: {
    formatToYMD(date) {
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      return `${y}-${m}-${d}`;
    },
    formatToYMDString(dateStr) {
      return dateStr.replace(/-/g, '');
    },
    async fetchData() {
      if (!this.startDate || !this.endDate) {
        this.error = '请选择完整的日期区间';
        return;
      }

      this.loading = true;
      this.error = null;
      
      try {
        const params = {
          start_date: this.formatToYMDString(this.startDate),
          end_date: this.formatToYMDString(this.endDate),
          strategy_name: this.selectedStrategies.join(',')
        };
        
        const response = await axios.get(API_ENDPOINTS.GET_TRADE_INFO, { params });
        
        if (response.data.code === 200 && response.data.data) {
          this.tradeRecords = response.data.data.latest_trade_records || [];
        } else {
          this.error = response.data.msg || '获取数据失败';
        }
      } catch (err) {
        console.error('获取历史成交记录失败:', err);
        this.error = '获取数据失败，请检查网络或登录状态';
      } finally {
        this.loading = false;
      }
    },
    toggleStrategyDropdown() {
      this.showStrategyDropdown = !this.showStrategyDropdown;
    },
    closeStrategyDropdown() {
      this.showStrategyDropdown = false;
    },
    toggleStrategy(name) {
      const index = this.selectedStrategies.indexOf(name);
      if (index > -1) {
        this.selectedStrategies.splice(index, 1);
      } else {
        this.selectedStrategies.push(name);
      }
    },
    clearStrategies() {
      this.selectedStrategies = [];
    },
    async fetchStrategies() {
      try {
        const response = await axios.get('/api/strategy/list');
        if (response.data.code === 200) {
          this.strategies = response.data.data.strategy_list || [];
        }
      } catch (error) {
        console.error('Error fetching strategies:', error);
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      if (dateStr.length === 8) {
        return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
      }
      return dateStr;
    },
    formatValueOrDash(val) {
      if (val === null || val === undefined || val === '') return '-';
      return val;
    },
    formatNumber(num) {
      if (num === null || num === undefined) return '-';
      return Number(num).toLocaleString();
    },
    formatCurrency(val) {
      if (val === null || val === undefined) return '-';
      return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatPrice(val) {
      if (val === null || val === undefined) return '-';
      return Number(val).toFixed(4);
    },
    getDirectionClass(direction) {
      if (direction === '买入') return 'text-red font-bold';
      if (direction === '卖出') return 'text-green font-bold';
      return '';
    },
    getStrategyBadgeClass(strategyName) {
      if (!strategyName) return '';
      if (!this.strategies || this.strategies.length === 0) return 'badge-color-1';
      
      const uniqueStrategies = [...new Set(this.strategies.map(s => s.strategy_name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      if (index === -1) return 'badge-color-1';
      const colorIndex = (index % 10) + 1;
      return `badge-color-${colorIndex}`;
    }
  },
  mounted() {
    this.fetchData();
    this.fetchStrategies();
  }
};
</script>

<style scoped>
.history-trades-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.header-section {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.filter-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.date-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
  font-family: inherit;
  font-size: 14px;
  color: #303133;
  transition: border-color 0.2s;
}

.date-input:focus {
  border-color: #409eff;
}

.date-separator {
  color: #909399;
  font-size: 14px;
}

/* 策略选择器样式 */
.strategy-selector {
  position: relative;
  min-width: 180px;
  cursor: pointer;
}

.selector-trigger {
  padding: 6px 12px;
  padding-right: 32px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 34px;
  transition: all 0.2s;
  position: relative;
}

.selector-trigger:hover {
  border-color: #c0c4cc;
}

.selector-trigger.active {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.selected-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  position: absolute;
  right: 12px;
  width: 8px;
  height: 8px;
  border-right: 2px solid #909399;
  border-bottom: 2px solid #909399;
  transform: translateY(-2px) rotate(45deg);
  transition: transform 0.3s;
}

.selector-trigger.active .dropdown-arrow {
  transform: translateY(2px) rotate(-135deg);
}

.selector-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  min-width: 200px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px 0;
}

.dropdown-item {
  padding: 8px 12px;
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

.dropdown-item.selected {
  color: #409eff;
  font-weight: 500;
  background-color: #f0f9eb;
}

.checkbox {
  width: 14px;
  height: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 2px;
  position: relative;
  flex-shrink: 0;
}

.checkbox.checked {
  background-color: #409eff;
  border-color: #409eff;
}

.checkbox.checked::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: 2px solid white;
  border-left: 0;
  border-top: 0;
  transform: rotate(45deg);
}

.query-btn {
  padding: 8px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.query-btn:hover {
  background-color: #66b1ff;
}

.query-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.loading-state,
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}

.data-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  white-space: nowrap;
}

.data-table th {
  background-color: #f2f6fc;
  color: #606266;
  font-weight: 600;
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid #dcdfe6;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
  background-color: #fff;
}

.col-index {
  width: 50px;
  text-align: center;
  color: #909399;
}

.numeric-mono {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 600;
}

.text-red { color: #ef4444 !important; }
.text-green { color: #10b981 !important; }
.font-bold { font-weight: 600; }

.strategy-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.badge-color-1 { background-color: #e0f2fe; color: #0369a1; }
.badge-color-2 { background-color: #cffafe; color: #0e7490; }
.badge-color-3 { background-color: #d1fae5; color: #065f46; }
.badge-color-4 { background-color: #fed7aa; color: #c2410c; }
.badge-color-5 { background-color: #fce7f3; color: #be185d; }
.badge-color-6 { background-color: #fee2e2; color: #b91c1c; }
.badge-color-7 { background-color: #fef9c3; color: #a16207; }
.badge-color-8 { background-color: #ccfbf1; color: #0f766e; }
.badge-color-9 { background-color: #ecfccb; color: #3f6212; }
.badge-color-10 { background-color: #f1f5f9; color: #334155; }

@media screen and (max-width: 768px) {
  .history-trades-container { padding: 16px; }
  .filter-group { gap: 12px; }
  .date-picker-wrapper { width: 100%; justify-content: space-between; }
  .date-input { flex: 1; min-width: 0; }
  .query-btn { width: 100%; }
  
  .sticky-col { position: sticky; z-index: 2; background-color: inherit; }
  .col-1 { left: 0; width: 40px !important; }
  .col-2 { left: 40px; box-shadow: 2px 0 5px rgba(0,0,0,0.05); }
}
</style>

<style>
/* Dark Mode Support */
body.dark-mode .history-trades-container { background-color: #1a1a1a !important; }
body.dark-mode .history-trades-container .page-title { color: #e0e0e0 !important; }
body.dark-mode .history-trades-container .filter-card,
body.dark-mode .history-trades-container .data-card,
body.dark-mode .history-trades-container .loading-state,
body.dark-mode .history-trades-container .error-state {
  background-color: #2d2d2d !important;
  border-color: #3e3e3e !important;
}
body.dark-mode .history-trades-container .filter-label { color: #b0b0b0 !important; }
body.dark-mode .history-trades-container .date-input {
  background-color: #333 !important;
  border-color: #444 !important;
  color: #e0e0e0 !important;
}
body.dark-mode .history-trades-container .selector-trigger {
  background-color: #333 !important;
  border-color: #444 !important;
  color: #e0e0e0 !important;
}
body.dark-mode .history-trades-container .selector-dropdown {
  background-color: #333 !important;
  border-color: #444 !important;
}
body.dark-mode .history-trades-container .dropdown-item {
  color: #e0e0e0 !important;
}
body.dark-mode .history-trades-container .dropdown-item:hover {
  background-color: #444 !important;
}
body.dark-mode .history-trades-container .dropdown-item.selected {
  background-color: #1e3a8a !important;
  color: #3b82f6 !important;
}
body.dark-mode .history-trades-container .checkbox {
  border-color: #555 !important;
}
body.dark-mode .history-trades-container .data-table th {
  background-color: #303030 !important;
  color: #b0b0b0 !important;
  border-bottom-color: #4c4d4f !important;
}
body.dark-mode .history-trades-container .data-table td {
  background-color: #2d2d2d !important;
  border-bottom-color: #3e3e3e !important;
  color: #e0e0e0 !important;
}
body.dark-mode .history-trades-container .strategy-badge { filter: brightness(0.8); }
</style>
