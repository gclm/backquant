<template>
  <div class="daily-clear-container">
    <!-- 标题部分 -->
    <div class="header-section">
      <h2 class="page-title">每日数据清算</h2>
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
      <!-- 策略日终清算表格 -->
      <div class="data-card">
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">策略日终清算</h3>
            <span v-if="dailyClearDate" class="date-badge">{{ formatDate(dailyClearDate) }}</span>
          </div>
        </div>
        
        <!-- 统计摘要 -->
        <div class="summary-bar" v-if="dailyClearSummary">
          <div class="summary-item">
            <span class="label">持仓成本</span>
            <span class="value numeric-mono">{{ formatSummaryNumber(dailyClearSummary.totalCost) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">当日市值</span>
            <span class="value numeric-mono">{{ formatSummaryNumber(dailyClearSummary.totalMarketValue) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">浮动总盈亏</span>
            <span class="value numeric-mono" :class="getProfitClass(dailyClearSummary.floatingProfit)">
              {{ formatSummaryNumber(dailyClearSummary.floatingProfit) }}
            </span>
          </div>
          <div class="summary-item">
            <span class="label">实现总盈亏</span>
            <span class="value numeric-mono" :class="getProfitClass(dailyClearSummary.totalProfit)">
              {{ formatSummaryNumber(dailyClearSummary.totalProfit) }}
            </span>
          </div>
        </div>

        <div v-if="sortedDailyClearData.length === 0" class="empty-data">暂无清算数据</div>
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-index sticky-col col-1">序号</th>
                <th class="sticky-col col-2">策略名称</th>
                <th>证券代码</th>
                <th>证券名称</th>
                <th>持仓数量</th>
                <th>持仓成本</th>
                <th>当日市值</th>
                <th>浮动盈亏</th>
                <th>策略容量</th>
                <th>实现盈亏</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in sortedDailyClearData" :key="item.id" :class="{'row-empty': isEmptyRow(item)}">
                <td class="col-index sticky-col col-1">{{ index + 1 }}</td>
                <td class="sticky-col col-2">
                  <span class="strategy-badge" :class="getStrategyBadgeClass(item.strategy_name)">{{ item.strategy_name }}</span>
                </td>
                <td>{{ formatValueOrDash(item.security_code) }}</td>
                <td>{{ formatValueOrDash(item.security_name) }}</td>
                <td class="numeric-mono">{{ formatNumber(item.hold_qty) }}</td>
                <td class="numeric-mono text-primary">{{ formatCurrency(item.total_cost) }}</td>
                <td class="numeric-mono text-primary">{{ formatCurrency(item.market_value) }}</td>
                <td :class="['numeric-mono', getProfitClass(calculateFloatingProfit(item))]">{{ formatProfit(calculateFloatingProfit(item)) }}</td>
                <td class="numeric-mono text-secondary">{{ formatCapacity(item.all_money) }}</td>
                <td :class="['numeric-mono', getProfitClass(item.realized_profit)]">{{ formatProfit(item.realized_profit) }}</td>
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
  name: 'DailyClear',
  data() {
    return {
      loading: false,
      error: null,
      dailyClearData: [],
      dailyClearDate: ''
    };
  },
  computed: {
    sortedDailyClearData() {
      // 浅拷贝并排序：优先显示有证券代码的，然后按策略名称字典序排序
      return [...this.dailyClearData].sort((a, b) => {
        const hasCodeA = !!a.security_code;
        const hasCodeB = !!b.security_code;
        
        // 有证券代码的优先
        if (hasCodeA && !hasCodeB) return -1;
        if (!hasCodeA && hasCodeB) return 1;
        
        // 同类型的按策略名称排序
        const nameA = a.strategy_name || '';
        const nameB = b.strategy_name || '';
        return nameB.localeCompare(nameA, 'zh-CN');
      });
    },
    dailyClearSummary() {
      if (!this.dailyClearData || this.dailyClearData.length === 0) return null;
      
      let totalCost = 0;
      let totalMarketValue = 0;
      let totalCapacity = 0;
      let totalProfit = 0;

      this.dailyClearData.forEach(item => {
        totalCost += Number(item.total_cost || 0);
        totalMarketValue += Number(item.market_value || 0);
        totalCapacity += Number(item.all_money || 0);
        totalProfit += Number(item.realized_profit || 0);
      });

      return {
        totalCost,
        totalMarketValue,
        totalCapacity,
        totalProfit,
        floatingProfit: totalMarketValue - totalCost
      };
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(API_ENDPOINTS.GET_LATEST_CLEAR);
        
        if (response.data.code === 200 && response.data.data) {
          const { latest_daily_clear } = response.data.data;
          
          this.dailyClearData = latest_daily_clear || [];
          
          // 提取清算日期
          if (this.dailyClearData.length > 0) {
            this.dailyClearDate = this.dailyClearData[0].clear_date;
          }
        } else {
          this.error = response.data.msg || '获取数据失败';
        }
      } catch (err) {
        console.error('获取每日清算数据失败:', err);
        // 401错误会由axios拦截器自动处理并跳转登录页
        if (!(err.response && err.response.status === 401)) {
          this.error = '网络请求失败，请稍后重试';
        }
      } finally {
        this.loading = false;
      }
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
    isEmptyRow(item) {
      // 如果没有 security_code 或者 security_name，但实现盈亏非0，则不是空仓行
      const hasNoSecurity = !item.security_code && !item.security_name;
      const hasRealizedProfit = Math.abs(Number(item.realized_profit || 0)) > 0;
      
      // 只有在没有证券且实现盈亏为0时才认为是空仓行
      return hasNoSecurity && !hasRealizedProfit;
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      // 假设格式为 YYYYMMDD
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
    formatCapacity(val) {
      // 策略容量：无小数，无逗号
      if (val === null || val === undefined) return '-';
      return Math.floor(Number(val)).toString();
    },
    formatSummaryNumber(val) {
      // 统计数据：保留两位小数，无逗号
      if (val === null || val === undefined) return '-';
      return Number(val).toFixed(2);
    },
    formatCurrency(val) {
      if (val === null || val === undefined) return '-';
      return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatProfit(val) {
       // 特殊处理：如果是0或"0.00"，不显示正负号，但如果有对齐需求可以保留
       if (val === null || val === undefined) return '-';
       return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatPrice(val) {
      if (val === null || val === undefined) return '-';
      return Number(val).toFixed(4);
    },
    calculateFloatingProfit(item) {
      // 浮动盈亏 = 当日市值 - 持仓成本
      const marketValue = Number(item.market_value || 0);
      const totalCost = Number(item.total_cost || 0);
      return marketValue - totalCost;
    },
    getProfitClass(profit) {
      const val = Number(profit);
      // 盈利：鲜红色，亏损：翠绿
      if (val > 0) return 'text-red';
      if (val < 0) return 'text-green';
      return 'text-normal'; // 0 的样式
    },
    getDirectionClass(direction) {
      if (direction === '买入') return 'text-red font-bold';
      if (direction === '卖出') return 'text-green font-bold';
      return '';
    },
    getStrategyBadgeClass(strategyName) {
      if (!strategyName) return '';
      if (!this.strategies || this.strategies.length === 0) return 'badge-color-1';
      
      // Get all unique strategy names from the global list and sort them
      const uniqueStrategies = [...new Set(this.strategies.map(s => s.strategy_name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      if (index === -1) return 'badge-color-1';
      
      // Cycle through 10 distinct colors
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
.daily-clear-container {
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
  margin: 0 0 8px 0;
  font-weight: 600;
}

.loading-state,
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
  margin-bottom: 20px;
}

.loading-state p,
.error-state p {
  color: #909399;
  font-size: 16px;
  margin: 0;
}

.error-state p {
  color: #f56c6c;
}

.data-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.data-card {
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

/* 统计栏样式 */
.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 16px;
  background-color: #ecf5ff; /* 浅蓝色背景 */
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #d9ecff;
}

.summary-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.summary-item .label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.summary-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.numeric-mono {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-weight: 600;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.card-title {
  font-size: 18px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.date-badge {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  padding: 2px 8px;
  border-radius: 4px;
}

.empty-data {
  text-align: center;
  color: #909399;
  padding: 32px 0;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
  width: 100%;
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
  transition: background-color 0.3s ease;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
  transition: border-color 0.3s ease, color 0.3s ease;
  background-color: #fff;
}

/* 空行样式 */
.row-empty td {
  background-color: #fafafa;
  color: #c0c4cc;
}

.row-empty .text-primary,
.row-empty .text-secondary,
.row-empty .text-red,
.row-empty .text-green {
   color: #c0c4cc !important;
}

.col-index {
  width: 50px;
  text-align: center;
  color: #909399;
}

.text-red {
  color: #ef4444 !important; /* 盈利：鲜红色 */
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.text-green {
  color: #10b981 !important; /* 亏损：翠绿 */
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.text-normal {
  color: #909399 !important;
}

.font-bold {
  font-weight: 600;
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.text-primary {
  color: #303133;
}

.text-secondary {
  color: #909399;
}

.text-gray-400 {
  color: #9ca3af;
}

/* 移动端固定列样式 - Scoped 保持不变 */
@media screen and (max-width: 768px) {
  .content-container, .daily-clear-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .data-content {
    gap: 16px;
  }
  
  .data-card {
    padding: 16px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .data-table th, 
  .data-table td {
    padding: 10px 8px;
    font-size: 13px;
  }
  
  .summary-bar {
    gap: 16px;
    padding: 12px;
  }
  
  .summary-item .label {
    font-size: 12px;
  }
  
  .summary-item .value {
    font-size: 14px;
  }

  .sticky-col {
    position: sticky;
    z-index: 2;
    background-color: inherit;
  }

  th.sticky-col {
    z-index: 3;
    background-color: #f2f6fc;
  }

  .col-1 {
    left: 0;
    width: 40px !important;
    min-width: 40px;
  }
  
  .col-2 {
    left: 40px;
    box-shadow: 2px 0 5px rgba(0,0,0,0.05);
  }

  .row-empty .sticky-col {
    background-color: #fafafa;
  }
}
</style>

<!-- 为了彻底解决样式覆盖问题，使用非 scoped 样式来处理暗黑模式 -->
<style>
/* Dark Mode 适配 - 全局覆盖 */
body.dark-mode .daily-clear-container {
  background-color: #1a1a1a !important;
}

body.dark-mode .daily-clear-container .page-title {
  color: #e0e0e0 !important;
}

body.dark-mode .daily-clear-container .loading-state,
body.dark-mode .daily-clear-container .error-state,
body.dark-mode .daily-clear-container .data-card {
  background-color: #2d2d2d !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

body.dark-mode .daily-clear-container .card-header {
  border-bottom-color: #409eff !important;
}

body.dark-mode .daily-clear-container .card-title {
  color: #e0e0e0 !important;
}

body.dark-mode .daily-clear-container .date-badge {
  background: rgba(64, 158, 255, 0.2) !important;
  border-color: rgba(64, 158, 255, 0.3) !important;
  color: #a0cfff !important;
}

/* 统计栏暗黑模式适配 */
body.dark-mode .daily-clear-container .summary-bar {
  background-color: #333333 !important;
  border-color: #444444 !important;
}

body.dark-mode .daily-clear-container .summary-item .label {
  color: #909399 !important;
}

body.dark-mode .daily-clear-container .summary-item .value {
  color: #f0f2f5 !important;
}

/* 表格样式适配 */
body.dark-mode .daily-clear-container .data-table th {
  background-color: #303030 !important;
  color: #b0b0b0 !important;
  border-bottom-color: #4c4d4f !important;
}

body.dark-mode .daily-clear-container .data-table td {
  background-color: #2d2d2d !important;
  border-bottom-color: #3e3e3e !important;
  color: #e0e0e0 !important;
}

/* 移动端固定列暗黑模式适配 */
@media screen and (max-width: 768px) {
  body.dark-mode .daily-clear-container th.sticky-col {
    background-color: #303030 !important;
  }
  
  body.dark-mode .daily-clear-container td.sticky-col {
    background-color: #2d2d2d !important;
  }
  
  /* 移动端空行固定列 */
  body.dark-mode .daily-clear-container .row-empty .sticky-col {
    background-color: #202020 !important;
  }
}

/* 空行暗黑模式样式 */
body.dark-mode .daily-clear-container .row-empty td {
  background-color: #202020 !important;
  color: #5c5c5c !important;
}

body.dark-mode .daily-clear-container .row-empty .text-primary,
body.dark-mode .daily-clear-container .row-empty .text-secondary,
body.dark-mode .daily-clear-container .row-empty .text-red,
body.dark-mode .daily-clear-container .row-empty .text-green {
   color: #5c5c5c !important;
}

body.dark-mode .daily-clear-container .text-primary {
  color: #e0e0e0 !important;
}

body.dark-mode .daily-clear-container .text-secondary {
  color: #a0a0a0 !important;
}

body.dark-mode .daily-clear-container .empty-data {
  color: #707070 !important;
}
/* Strategy Badge Styles - 10 Distinct Colors (No Purple) */
.strategy-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-color-1 { background-color: #e0f2fe; color: #0369a1; } /* Sky */
.badge-color-2 { background-color: #cffafe; color: #0e7490; } /* Cyan */
.badge-color-3 { background-color: #d1fae5; color: #065f46; } /* Emerald */
.badge-color-4 { background-color: #fed7aa; color: #c2410c; } /* Orange */
.badge-color-5 { background-color: #fce7f3; color: #be185d; } /* Pink */
.badge-color-6 { background-color: #fee2e2; color: #b91c1c; } /* Red */
.badge-color-7 { background-color: #fef9c3; color: #a16207; } /* Yellow */
.badge-color-8 { background-color: #ccfbf1; color: #0f766e; } /* Teal */
.badge-color-9 { background-color: #ecfccb; color: #3f6212; } /* Lime */
.badge-color-10 { background-color: #f1f5f9; color: #334155; } /* Slate */

/* Dark Mode Badge Styles */
.daily-clear-container.dark-mode .badge-color-1 { background-color: #1e3a8a; color: #93c5fd; }
.daily-clear-container.dark-mode .badge-color-2 { background-color: #164e63; color: #67e8f9; }
.daily-clear-container.dark-mode .badge-color-3 { background-color: #14532d; color: #86efac; }
.daily-clear-container.dark-mode .badge-color-4 { background-color: #7c2d12; color: #fdba74; }
.daily-clear-container.dark-mode .badge-color-5 { background-color: #831843; color: #f9a8d4; }
.daily-clear-container.dark-mode .badge-color-6 { background-color: #7f1d1d; color: #fca5a5; }
.daily-clear-container.dark-mode .badge-color-7 { background-color: #713f12; color: #fde047; }
.daily-clear-container.dark-mode .badge-color-8 { background-color: #115e59; color: #5eead4; }
.daily-clear-container.dark-mode .badge-color-9 { background-color: #365314; color: #bef264; }
.daily-clear-container.dark-mode .badge-color-10 { background-color: #334155; color: #cbd5e1; }
</style>
