<template>
  <div class="overbuy-insight">
    <div class="header-section1">
      <h2 class="strategy-title">ETF超买情况</h2>
      <div class="summary-line">{{ summaryText }}</div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-text">加载中...</div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-text">{{ error }}</div>
      <button class="retry-button" @click="fetchData">重试</button>
    </div>
    
    <div v-else-if="overbuyData.length === 0" class="empty-container">
      <div class="empty-text">暂无数据</div>
    </div>
    
    <div v-else class="data-container">
      <div v-for="(row, rowIdx) in rowGroups" :key="`row-${rowIdx}`" class="row-group-wrapper">
        <!-- 行级工具栏：行级折叠/展开按钮放在两张卡片之上，避免误解 -->
        <div class="row-header">
          <div class="row-title"></div>
          <div class="row-actions">
            <button
              class="toggle-btn"
              @click="toggleRow(rowIdx)"
            >{{ isRowExpanded(rowIdx) ? '收起' : '展开' }}</button>
          </div>
        </div>

        <div class="row-group">
          <div v-for="item in row" :key="rowKey(item)" class="fund-card" :class="{ warning: hasWarning(item) }">
            <div class="card-header" :class="{ 'warning-header': hasWarning(item) }">
              <div class="fund-info">
                <span class="fund-code">{{ item.fund_code }}</span>
                <span class="fund-name">{{ item.fund_name }}</span>
              </div>
              <div class="card-actions">
                <div class="trade-date">{{ formatDate(item.trade_date) }}</div>
              </div>
            </div>
            
            <!-- 行级折叠：依据行开关（含预警行默认展开） -->
            <div v-if="isRowExpanded(rowIdx)" class="card-body">
              <div class="sections-grid">
                <!-- 上：超买情况部分 -->
                <div class="section-left section-card">
                  <div class="section-title">超买情况</div>
                  <div class="overbuy-grid">
                    <div v-for="days in [1, 2, 3, 4, 5, 7, 10, 12, 15, 30]" :key="days" 
                         :class="['overbuy-block', getOverbuyClass(item, days)]">
                      <div class="overbuy-header">
                        <span class="days-label">{{ days }}天</span>
                        <span v-if="getOverbuyValue(item, days) !== 0" class="warning-badge">预警</span>
                      </div>
                      <div class="overbuy-content">
                        <div class="info-row">
                          <span class="info-label">涨跌幅：</span>
                          <span class="change-value" :class="getChangeClass(getChangeValue(item, days))">
                            {{ formatPercent(getChangeValue(item, days)) }}
                          </span>
                        </div>
                        <div class="info-row">
                          <span class="info-label">预警值：</span>
                          <span class="threshold-value">{{ formatPercent(getThresholdValue(item, days)) }}</span>
                        </div>
                        <div class="info-row">
                          <span class="info-label">超买信号：</span>
                          <span class="status-value" :class="getOverbuyClass(item, days)">
                            {{ getOverbuyValue(item, days) !== 0 ? '超买' : '正常' }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 下：动量情况部分 -->
                <div class="section-right section-card">
                  <div class="section-title">动量情况</div>
                  <div class="momentum-stat-grid">
                    <div v-for="scoreKey in getScoreKeys(item)" :key="scoreKey" class="momentum-stat">
                      <div class="stat-label">{{ getScoreLabel(scoreKey) }}</div>
                      <div class="stat-value" :class="getScoreClass(item[scoreKey])">
                        {{ formatScore(item[scoreKey]) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';

export default {
  name: 'OverbuyInsight',
  data() {
    return {
      overbuyData: [],
      loading: true,
      error: null,
      expandedRows: {}
    }
  },
  computed: {
    displayData() {
      const warnings = [];
      const normals = [];
      (this.overbuyData || []).forEach(it => {
        if (this.hasWarning(it)) warnings.push(it); else normals.push(it);
      });
      if (warnings.length > 0) {
        return [...warnings, ...normals];
      }
      const isTarget = (it) => {
        const code = String(it.fund_code || '').toLowerCase();
        const name = String(it.fund_name || '');
        return code === '159915.sz' || code === 'sz159915' || code === '159915' || name.includes('创业板');
      };
      const idx = normals.findIndex(isTarget);
      if (idx > 0) {
        const preferred = normals[idx];
        const rest = normals.slice(0, idx).concat(normals.slice(idx + 1));
        return [preferred, ...rest];
      }
      return normals;
    },
    rowGroups() {
      const rows = [];
      const list = this.displayData || [];
      for (let i = 0; i < list.length; i += 2) {
        rows.push(list.slice(i, i + 2));
      }
      return rows;
    },
    totalCount() {
      return (this.overbuyData || []).length;
    },
    warningsCount() {
      return (this.overbuyData || []).reduce((acc, it) => acc + (this.hasWarning(it) ? 1 : 0), 0);
    },
    summaryText() {
      if (!this.totalCount) return '';
      if (this.warningsCount > 0) {
        const normal = this.totalCount - this.warningsCount;
        return `${this.warningsCount}只预警，${normal > 0 ? '其余正常' : '无其他'}`;
      }
      return `全部${this.totalCount}只ETF正常`;
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    rowKey(item) {
      return `${item.fund_code}-${item.trade_date}`;
    },
    rowHasWarning(row) {
      return (row || []).some(it => this.hasWarning(it));
    },
    isRowExpanded(rowIdx) {
      // 未设置过展开状态时，含预警的行默认展开
      if (this.expandedRows[rowIdx] === undefined) {
        const row = this.rowGroups[rowIdx] || [];
        return this.rowHasWarning(row);
      }
      return !!this.expandedRows[rowIdx];
    },
    toggleRow(rowIdx) {
      this.expandedRows = { ...this.expandedRows, [rowIdx]: !this.isRowExpanded(rowIdx) };
    },
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(API_ENDPOINTS.OVER_OVERBUY);
        if (response.data.code === 0 && response.data.data) {
          this.overbuyData = response.data.data;
        } else {
          this.error = '获取数据失败';
        }
      } catch (err) {
        this.error = err.response?.data?.msg || err.message || '获取数据失败';
      } finally {
        this.loading = false;
      }
    },
    
    hasWarning(item) {
      return Object.keys(item).some(key => 
        key.startsWith('over_buy') && item[key] !== 0
      );
    },
    
    getOverbuyValue(item, days) {
      if (days === 1) return item.over_buy || 0;
      return item[`over_buy_n${days}`] || 0;
    },

    getOverbuyClass(item, days) {
      const value = this.getOverbuyValue(item, days);
      return value !== 0 ? 'warning' : 'normal';
    },
    
    getChangeValue(item, days) {
      if (days === 1) return item.change_pct;
      return item[`change_pct_n${days}`];
    },
    
    getThresholdValue(item, days) {
      if (days === 1) return item.change_pct_min;
      return item[`change_pct_n${days}_min`];
    },
    
    getChangeClass(value) {
      if (!value && value !== 0) return '';
      return value > 0 ? 'positive' : 'negative';
    },
    
    formatPercent(value) {
      if (value == null || value === undefined) return 'N/A';
      return `${value.toFixed(2)}%`;
    },
    
    formatScore(value) {
      if (value == null || value === undefined) return 'N/A';
      return parseFloat(value).toFixed(5);
    },
    
    formatDate(dateStr) {
      if (!dateStr || dateStr.length !== 8) return dateStr;
      return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
    },
    
    getScoreKeys(item) {
      const order = [
        'score',
        'score_3',
        'score_3_diff',
        'score_5',
        'score_5_avg',
        'score_10_avg',
        'score_12',
        'score_26_diff'
      ];
      return order.filter(key => Object.prototype.hasOwnProperty.call(item, key));
    },
    
    getScoreLabel(key) {
      const labels = {
        'score': '动量',
        'score_3': '3日动量',
        'score_5': '5日动量',
        'score_10_avg': '10日平均动量',
        'score_12': '12日动量',
        'score_3_diff': '3日动量差值',
        'score_5_avg': '5日平均动量',
        'score_26_diff': '26日动量差值'
      };
      return labels[key] || key;
    },
    
    getScoreClass(value) {
      if (!value && value !== 0) return '';
      const numValue = parseFloat(value);
      if (isNaN(numValue)) return '';
      return numValue > 0 ? 'positive' : 'negative';
    }
  }
}
</script>

<style scoped>
.overbuy-insight { padding: 12px 20px 20px; max-width: 1400px; margin: 0 auto; }
.header-section1 { margin-bottom: 16px; }
.strategy-title { font-size: 20px; font-weight: 600; color: #333; margin: 0; }
.summary-line { margin-top: 6px; font-size: 13px; color: #666; }

.loading-container, .error-container, .empty-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; text-align: center; }
.loading-text, .error-text, .empty-text { font-size: 15px; color: #666; margin-bottom: 16px; }

.retry-button { background: #409EFF; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px; transition: background-color 0.3s; }
.retry-button:hover { background: #337ECC; }

/* 行级容器 */
.data-container { display: flex; flex-direction: column; gap: 14px; }
.row-group-wrapper { display: flex; flex-direction: column; gap: 8px; }
.row-header { display: flex; align-items: center; justify-content: space-between; padding: 6px 2px; }
.row-title { font-size: 12px; color: #666; }
.row-indicator { padding: 2px 8px; border-radius: 999px; background: #f0f2f5; color: #666; }
.row-indicator.warning { background: #fff1f0; color: #cf1322; }
.row-actions { display: flex; align-items: center; gap: 8px; }

.row-group { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }

.fund-card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; border: 1px solid #eef1f5; }
.fund-card.warning { border-color: #ffa39e; box-shadow: 0 6px 16px rgba(255, 77, 79, 0.08); }
.card-header { background: #f8f9fa; padding: 10px 14px; border-bottom: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; }
.card-header.warning-header { background: #fff1f0; border-bottom-color: #ffa39e; box-shadow: inset 4px 0 0 #ff7875; }
.fund-info { display: flex; align-items: center; gap: 10px; }
.card-actions { display: flex; align-items: center; gap: 10px; }
.toggle-btn { background: #fff; border: 1px solid #d9dfe7; color: #555; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; }
.toggle-btn:hover { border-color: #bfc7d2; }

.fund-code { font-weight: 600; color: #333; font-size: 14px; }
.fund-name { color: #666; font-size: 14px; }
.trade-date { color: #999; font-size: 12px; }

.card-body { padding: 12px; }

/* 内部：超买与动量垂直排列 */
.sections-grid { display: flex; flex-direction: column; gap: 16px; }
.section-left, .section-right { min-width: 0; }
.section-card { background: #f5f7fa; border: 1px solid #eaecef; border-radius: 8px; padding: 12px; }
.section-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid #e0e3e8; }

/* 超买：每行3列，响应式递减 */
.overbuy-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.overbuy-block { border: 1px solid #e9ecef; border-radius: 6px; padding: 8px; background: #fff; }
.overbuy-block.warning { border-color: #ffa39e; background: #fff5f5; }
.overbuy-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.days-label { font-weight: 600; color: #333; font-size: 13px; }
.warning-badge { background: #ff7875; color: white; padding: 0 6px; border-radius: 4px; font-size: 10px; font-weight: 600; line-height: 18px; }
.overbuy-content { display: flex; flex-direction: column; gap: 2px; }
.info-row { display: flex; align-items: center; gap: 6px; line-height: 1.4; }
.info-label { color: #666; font-size: 12px; }
.change-value, .threshold-value, .status-value { font-weight: 600; font-size: 12px; }
.change-value.positive { color: #389e0d; }
.change-value.negative { color: #a86161; }
.status-value.warning { color: #cf1322; font-weight: 700; }
.status-value.normal { color: #389e0d; }

/* 动量：紧凑统计卡片网格 */
.momentum-stat-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.momentum-stat { background: #fff; border: 1px solid #e9ecef; border-radius: 6px; padding: 10px; display: flex; flex-direction: column; gap: 6px; }
.stat-label { font-size: 12px; color: #666; font-weight: 600; }
.stat-value { font-size: 15px; font-weight: 700; color: #333; }
.stat-value.positive { color: #389e0d; }
.stat-value.negative { color: #a86161; }

/* 响应式：行内两列→一列；超买三列→二列→一列；动量三列→二列→一列 */
@media (max-width: 900px) { .row-group { grid-template-columns: 1fr; } .overbuy-grid { grid-template-columns: repeat(2, 1fr); } .momentum-stat-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px) { .overbuy-grid { grid-template-columns: 1fr; } .momentum-stat-grid { grid-template-columns: 1fr; } }

@media (max-width: 768px) { .overbuy-insight { padding: 10px 12px 12px; } .card-body { padding: 10px; } }
@media (max-width: 480px) { .overbuy-insight { padding: 8px 10px 10px; } .change-value, .threshold-value, .status-value { font-size: 12px; } }

.overbuy-insight {
  padding: 24px;
  min-height: calc(100vh - 64px);
}

/* Dark Mode 适配 - 全局覆盖 */
body.dark-mode .overbuy-insight {
  background-color: #1a1a1a !important;
}

body.dark-mode .overbuy-insight .strategy-title {
  color: #e0e0e0 !important;
}

body.dark-mode .overbuy-insight .summary-line {
  color: #909399 !important;
}

body.dark-mode .overbuy-insight .fund-card {
  background: #2d2d2d !important;
  border-color: #4c4d4f !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

body.dark-mode .overbuy-insight .card-header {
  background: #333333 !important;
  border-bottom-color: #409eff !important;
}

body.dark-mode .overbuy-insight .card-title,
body.dark-mode .overbuy-insight .fund-code,
body.dark-mode .overbuy-insight .fund-name {
  color: #e0e0e0 !important;
}

body.dark-mode .overbuy-insight .card-body {
  color: #e0e0e0 !important;
}

body.dark-mode .overbuy-insight .stat-label {
  color: #909399 !important;
}

body.dark-mode .overbuy-insight .stat-value {
  color: #f0f2f5 !important;
}

body.dark-mode .overbuy-insight .change-value.positive {
  color: #10b981 !important;
}

body.dark-mode .overbuy-insight .change-value.negative {
  color: #ef4444 !important;
}

body.dark-mode .overbuy-insight .threshold-value {
  color: #909399 !important;
}

body.dark-mode .overbuy-insight .status-value {
  color: #e0e0e0 !important;
}

body.dark-mode .overbuy-insight .warning-badge {
  background: #dc2626 !important;
  color: #ffffff !important;
}

body.dark-mode .overbuy-insight .retry-button {
  background: #3b82f6 !important;
  color: #ffffff !important;
}

body.dark-mode .overbuy-insight .retry-button:hover {
  background: #2563eb !important;
}
</style>
