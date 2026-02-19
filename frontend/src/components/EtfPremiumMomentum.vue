<template>
  <div class="etf-premium-container">
    <div class="header-section">
      <h2 class="page-title">ETF优质动量</h2>
      <span v-if="busiDate" class="date-badge">{{ formatDate(busiDate) }}</span>
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
        <div v-if="etfData.length === 0" class="empty-data">暂无数据</div>
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-index sticky-col col-1">序号</th>
                <th class="sticky-col col-2">证券代码</th>
                <th>证券名称</th>
                <th>动量得分</th>
                <th>
                  短期动量
                  <span class="tooltip-icon" title="短期动量是近两周的收益率，如果短期动量小于0，则排除">?</span>
                </th>
                <th>收盘价</th>
                <th>操作建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in etfData" :key="item.id || index" :class="getRowClass(item)">
                <td class="col-index sticky-col col-1">{{ index + 1 }}</td>
                <td class="sticky-col col-2">{{ item.etf }}</td>
                <td>{{ item.etf_name }}</td>
                <td class="numeric-mono">{{ formatNumber(item.score, 4) }}</td>
                <td :class="['numeric-mono', getReturnClass(item.short_return)]">
                  {{ formatPercent(item.short_return) }}
                </td>
                <td class="numeric-mono">{{ formatNumber(item.current_price, 4) }}</td>
                <td>
                  <span class="status-badge" :class="getStatusClass(item.status)">
                    {{ getStatusText(item.status) }}
                  </span>
                </td>
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
  name: 'EtfPremiumMomentum',
  data() {
    return {
      loading: false,
      error: null,
      etfData: [],
      busiDate: ''
    };
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(API_ENDPOINTS.GET_PREMIUM_ETF);
        
        if (response.data.code === 200 && response.data.data) {
          const { etf_premium } = response.data.data;
          this.etfData = (etf_premium || []).sort((a, b) => b.score - a.score);
          
          // 提取日期 (假设所有数据日期相同，取第一条)
          if (this.etfData.length > 0) {
            this.busiDate = this.etfData[0].busi_date;
          }
        } else {
          this.error = response.data.msg || '获取数据失败';
        }
      } catch (err) {
        console.error('获取ETF优质动量数据失败:', err);
        // 401错误会由axios拦截器自动处理并跳转登录页
        if (!(err.response && err.response.status === 401)) {
          this.error = '网络请求失败，请稍后重试';
        }
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      if (dateStr.length === 8) {
        return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)} 14:45`;
      }
      return dateStr;
    },
    formatNumber(val, decimals = 2) {
      if (val === null || val === undefined || val === '') return '-';
      return Number(val).toFixed(decimals);
    },
    formatPercent(val) {
      if (val === null || val === undefined || val === '') return '-';
      return (Number(val) * 100).toFixed(2) + '%';
    },
    getStatusText(status) {
      if (status === 'buy') return '买入';
      if (status === 'pass') return '空仓';
      return status;
    },
    getStatusClass(status) {
      if (status === 'buy') return 'status-buy';
      if (status === 'pass') return 'status-pass';
      return '';
    },
    getRowClass(item) {
      if (item.status === 'buy') return 'row-buy';
      return '';
    },
    getReturnClass(val) {
      const num = Number(val);
      // 盈利：鲜红色，亏损：翠绿
      if (num > 0) return 'text-red';
      if (num < 0) return 'text-green';
      return '';
    }
  },
  mounted() {
    this.fetchData();
  }
};
</script>

<style scoped>
.etf-premium-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.header-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.date-badge {
  font-size: 14px;
  color: #606266;
  background: #e4e7ed;
  padding: 4px 12px;
  border-radius: 4px;
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

.data-card {
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
  overflow: hidden;
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
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  color: #606266;
}

.numeric-mono {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-weight: 600;
}

.col-index {
  width: 50px;
  text-align: center;
  color: #909399;
}

.text-red {
  color: #ef4444;
  font-weight: 600;
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.text-green {
  color: #10b981;
  font-weight: 600;
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-buy {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fab6b6;
}

.status-pass {
  background-color: #f4f4f5;
  color: #909399;
  border: 1px solid #e9e9eb;
}

.tooltip-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #909399;
  color: white;
  font-size: 10px;
  margin-left: 4px;
  cursor: help;
  vertical-align: middle;
}

.row-buy {
  background-color: #fdf6ec;
}

.row-buy td {
  background-color: #fdf6ec; /* 覆盖默认白色背景 */
}

/* 移动端固定列样式 */
@media screen and (max-width: 768px) {
  .etf-premium-container {
    padding: 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .data-card {
    padding: 0;
    border-radius: 8px;
  }
  
  .data-table th, 
  .data-table td {
    padding: 10px 8px;
    font-size: 13px;
  }

  .sticky-col {
    position: sticky;
    z-index: 2;
    background-color: #fff;
  }
  
  .row-buy .sticky-col {
    background-color: #fdf6ec;
  }

  th.sticky-col {
    z-index: 3;
    background-color: #f2f6fc;
  }

  .col-1 {
    left: 0;
    width: 40px;
    min-width: 40px;
  }
  
  .col-2 {
    left: 40px;
    box-shadow: 2px 0 5px rgba(0,0,0,0.05);
  }
}
</style>

<!-- 暗黑模式适配 -->
<style>
body.dark-mode .etf-premium-container {
  background-color: #1a1a1a !important;
}

body.dark-mode .etf-premium-container .page-title {
  color: #e0e0e0 !important;
}

body.dark-mode .etf-premium-container .date-badge {
  background: #333333 !important;
  color: #a0cfff !important;
}

body.dark-mode .etf-premium-container .loading-state,
body.dark-mode .etf-premium-container .error-state,
body.dark-mode .etf-premium-container .data-card {
  background-color: #2d2d2d !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

body.dark-mode .etf-premium-container .data-table th {
  background-color: #303030 !important;
  color: #b0b0b0 !important;
  border-bottom-color: #4c4d4f !important;
}

body.dark-mode .etf-premium-container .data-table td {
  background-color: #2d2d2d !important;
  border-bottom-color: #3e3e3e !important;
  color: #e0e0e0 !important;
}

body.dark-mode .etf-premium-container .row-buy td,
body.dark-mode .etf-premium-container .row-buy .sticky-col {
  background-color: #3a2e23 !important; /* 暗黑模式下的高亮背景 */
}

body.dark-mode .etf-premium-container .sticky-col {
  background-color: #2d2d2d !important;
}

body.dark-mode .etf-premium-container th.sticky-col {
  background-color: #303030 !important;
}

body.dark-mode .etf-premium-container .empty-data {
  color: #707070 !important;
}

body.dark-mode .etf-premium-container .status-buy {
  background-color: rgba(245, 108, 108, 0.2) !important;
  border-color: rgba(245, 108, 108, 0.3) !important;
  color: #f89898 !important;
}

body.dark-mode .etf-premium-container .status-pass {
  background-color: rgba(144, 147, 153, 0.2) !important;
  border-color: rgba(144, 147, 153, 0.3) !important;
  color: #b1b3b8 !important;
}

@media screen and (max-width: 768px) {
  body.dark-mode .etf-premium-container .col-2 {
    box-shadow: 2px 0 5px rgba(0,0,0,0.3) !important;
  }
}
</style>
