<template>
  <div class="content-container">
    <!-- 标题部分 -->
    <div class="header-section">
      <h2 class="page-title">持仓调仓情况</h2>
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
    <div v-else class="data-layout">
      <!-- 昨日持仓头寸 -->
      <div class="position-card">
        <div class="card-header">
          <h3 class="card-title">昨日持仓头寸</h3>
          <span class="data-count">{{ positionData.length }} 条记录</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>交易日期</th>
                <th>策略名称</th>
                <th>证券代码</th>
                <th>数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in positionData" :key="item.id">
                <td>{{ item.trade_date }}</td>
                <td>{{ item.strategy_name }}</td>
                <td>{{ item.stock_code }}</td>
                <td>{{ formatNumber(item.quantity) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 昨日资金账户 -->
      <div class="account-card">
        <div class="card-header">
          <h3 class="card-title">昨日资金账户</h3>
          <span class="data-count">{{ accountData.length }} 条记录</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>交易日期</th>
                <th>总资产</th>
                <th>持仓市值</th>
                <th>可用金额</th>
                <th>自动交易</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in accountData" :key="item.id">
                <td>{{ item.trade_date }}</td>
                <td>{{ formatMoney(item.total_assets) }}</td>
                <td>{{ formatMoney(item.position_value) }}</td>
                <td>{{ formatMoney(item.available_amount) }}</td>
                <td>{{ item.auto_trade === 1 ? '是' : '否' }}</td>
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
  name: 'PositionAdjustment',

  data() {
    return {
      loading: true,
      error: null,
      positionData: [],
      accountData: []
    }
  },

  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        // 并行调用两个接口
        const [positionResponse, accountResponse] = await Promise.all([
          axios.get(API_ENDPOINTS.POSITION_INFO),
          axios.get(API_ENDPOINTS.ACCOUNT_INFO)
        ]);
        
        // 处理持仓数据
        if (positionResponse.data.code === 0 && positionResponse.data.data) {
          this.positionData = positionResponse.data.data;
        } else {
          this.positionData = [];
        }
        
        // 处理账户数据
        if (accountResponse.data.code === 0 && accountResponse.data.data) {
          this.accountData = accountResponse.data.data;
        } else {
          this.accountData = [];
        }
        
      } catch (error) {
        console.error('获取数据失败:', error);
        this.error = '功能开发中，敬请期待！';
      } finally {
        this.loading = false;
      }
    },

    formatNumber(num) {
      if (num === null || num === undefined) return '-';
      return num.toLocaleString();
    },

    formatMoney(amount) {
      if (amount === null || amount === undefined) return '-';
      return '¥' + amount.toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    }
  },

  mounted() {
    this.fetchData();
  }
}
</script>

<style scoped>
.content-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 80px);
}

.header-section {
  margin-bottom: 30px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.page-description {
  color: #909399;
  font-size: 14px;
  margin: 0;
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
  text-align: center;
  margin: 0;
}

.error-state p {
  color: #f56c6c;
}

/* 数据布局 */
.data-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.position-card,
.account-card {
  background: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 20px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08); /* shadow-sm */
  border: 1px solid #e5e7eb; /* border */
  transition: all 0.3s ease;
}

.position-card:hover,
.account-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.card-title {
  font-size: 18px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.data-count {
  font-size: 12px;
  color: #606266;
  background: #e1f3d8;
  padding: 4px 8px;
  border-radius: 12px;
  border: 1px solid #b3d8a4;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
}

.data-table th,
.data-table td {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  text-align: left;
  white-space: nowrap;
}

.data-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #606266;
  font-size: 13px;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table td {
  font-size: 13px;
  color: #303133;
}

.data-table tbody tr:hover {
  background-color: #f5f7fa;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .content-container {
    padding: 16px;
  }

  .header-section {
    margin-bottom: 20px;
  }

  .page-title {
    font-size: 22px;
  }

  .page-description {
    font-size: 13px;
  }

  .position-card,
  .account-card {
    padding: 16px;
  }

  .card-title {
    font-size: 16px;
  }

  .data-count {
    font-size: 11px;
    padding: 3px 6px;
  }

  .data-table th,
  .data-table td {
    padding: 8px 10px;
    font-size: 12px;
  }

  .table-container {
    margin: 0 -16px;
    padding: 0 16px;
  }
}

@media screen and (max-width: 480px) {
  .data-table th,
  .data-table td {
    padding: 6px 8px;
    font-size: 11px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .data-count {
    align-self: flex-end;
  }
}
</style>
