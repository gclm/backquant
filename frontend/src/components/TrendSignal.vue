<template>
  <div class="trend-signal">
    <!-- ETF 选项卡导航 -->
    <div class="etf-tabs">
        <div
          v-for="etf in etfList"
          :key="etf.code"
          class="etf-tab"
          :class="{ 
            active: selectedTab === etf.code,
            'priority-etf': etf.code === 'sz159915' || etf.code === 'sz159995'
          }"
          @click="handleTabClick(etf.code)"
        >
          {{ etf.name }}
        </div>
      </div>

      <!-- 单实例子组件：根据选中ETF渲染 -->
      <transition name="fade-slide" mode="out-in" appear>
        <KlinePanel
          v-if="currentCode && chartDataByCode[currentCode] && !isLoading"
          :key="`${currentCode}-${chartDataByCode[currentCode]?.length || 0}`"
          :code="currentCode"
          :name="getCurrentEtfName()"
          :perfInfo="getPerfInfo(currentCode)"
          :kline="chartDataByCode[currentCode]"
          :signals="signalData"
          :isDarkMode="isDarkMode"
        />
      </transition>
      
      <!-- 加载状态显示 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-text">切换中...</div>
      </div>

      <!-- 空数据状态 -->
      <div v-if="!isLoading && (!currentCode || !chartDataByCode[currentCode])" class="empty-container">
        <div class="empty-text">暂无数据</div>
      </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';
import KlinePanel from './KlinePanel.vue';

export default {
  name: 'TrendSignal',
  components: {
    KlinePanel
  },
  props: {
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isLoading: true,
      error: null,
      chartData: [],
      signalData: [],
      // 动态获取的ETF列表
      etfList: [],
      selectedTab: '',
      loadingTimer: null,
    }
  },
  computed: {
    // 按代码分组K线数据
    chartDataByCode() {
      const grouped = {};
      this.chartData.forEach(item => {
        if (!grouped[item.code]) {
          grouped[item.code] = [];
        }
        grouped[item.code].push(item);
      });
      
      // 对每个代码的数据按时间排序
      Object.keys(grouped).forEach(code => {
        grouped[code].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
      });
      
      return grouped;
    },
    currentCode() {
      return this.selectedTab;
    }
  },
  async mounted() {
    await this.fetchEtfList();
    await this.fetchData();
    this.isLoading = false;
  },
  methods: {
    async fetchEtfList() {
      try {
        const response = await axios.get(API_ENDPOINTS.ALL_CODE_MIN);
        if (response.data.code === 0 && response.data.data) {
          // 过滤掉不需要的ETF：医药ETF、军工ETF、人工智能ETF、消费ETF
          const filteredEtfs = response.data.data.filter(etf => {
            const name = etf.name || '';
            // 排除包含特定关键词的ETF
            const excludeKeywords = ['医药', '医疗', '军工', '人工智能', 'AI', '消费', '白酒', '食品'];
            const shouldExclude = excludeKeywords.some(keyword => name.includes(keyword));

            // 排除特定代码的ETF（如果需要的话）
            const excludeCodes = []; // 可以在这里添加需要排除的特定代码

            return !shouldExclude && !excludeCodes.includes(etf.code);
          });

          // 确保包含新增的ETF
          const requiredEtfs = [
            { code: 'sh510500', name: '中证500ETF' },
            { code: 'sh512100', name: '中正1000ETF' }
          ];

          // 检查并添加缺失的必需ETF
          requiredEtfs.forEach(requiredEtf => {
            const exists = filteredEtfs.some(etf => etf.code === requiredEtf.code);
            if (!exists) {
              filteredEtfs.push(requiredEtf);
            }
          });

          // 重新排序ETF列表，确保创业板ETF和芯片ETF在前两个位置，然后是其他ETF
          const priorityEtfs = filteredEtfs.filter(etf =>
            etf.code === 'sz159915' || etf.code === 'sz159995'
          );
          const otherEtfs = filteredEtfs.filter(etf =>
            etf.code !== 'sz159915' && etf.code !== 'sz159995'
          );

          // 创业板ETF排第一，芯片ETF排第二，其他ETF按原顺序
          this.etfList = [
            ...priorityEtfs.filter(etf => etf.code === 'sz159915'),
            ...priorityEtfs.filter(etf => etf.code === 'sz159995'),
            ...otherEtfs
          ];

          // 默认选择创业板ETF
          if (this.etfList.length > 0) {
            this.selectedTab = this.etfList[0].code;
          }
        }
      } catch (err) {
        console.error('获取ETF列表失败:', err);
      }
    },
    
    getCurrentEtfName() {
      const currentEtf = this.etfList.find(etf => etf.code === this.currentCode);
      return currentEtf ? currentEtf.name : this.currentCode;
    },
    getPerfInfo(code) {
      const perf = {
        'sz159915': '【15分钟】历史回测胜率56%，超额收益220%',
        'sz159995': '【15分钟】历史回测胜率41%，超额收益226%',
        'sh512100': '【15分钟】历史回测胜率45%，超额收益94%',
        'sh510500': '【15分钟】历史回测胜率47%，超额收益103%',
      };
      return perf[code] || '';
    },
    async fetchData() {
      if (!this.selectedTab) return;
      
      this.isLoading = true;
      this.error = null;
      try {
        // 根据选中的ETF代码获取数据
        const [klineResponse, signalResponse] = await Promise.all([
          axios.get(`${API_ENDPOINTS.MIN_HQ}/${this.selectedTab}`),
          axios.get(`${API_ENDPOINTS.TREND_SIGNAL}/${this.selectedTab}`)
        ]);

        // 检查K线数据
        if (klineResponse.data.code === 0 && klineResponse.data.data) {
          this.chartData = klineResponse.data.data;
        } else {
          throw new Error('获取K线数据失败');
        }

        // 检查信号数据
        if (signalResponse.data.code === 0 && signalResponse.data.data) {
          this.signalData = signalResponse.data.data;
        } else {
          throw new Error('获取信号数据失败');
        }

        this.isLoading = false;
        // 清除加载定时器
        if (this.loadingTimer) {
          clearTimeout(this.loadingTimer);
          this.loadingTimer = null;
        }
      } catch (err) {
        console.error('获取数据失败:', err);
        this.error = err.response?.data?.msg || err.message || '获取数据失败';
        this.isLoading = false;
        // 清除加载定时器
        if (this.loadingTimer) {
          clearTimeout(this.loadingTimer);
          this.loadingTimer = null;
        }
      }
    },

    formatTimestamp(timestamp) {
      if (timestamp && timestamp.length === 12) {
        const year = timestamp.substring(0, 4);
        const month = timestamp.substring(4, 6);
        const day = timestamp.substring(6, 8);
        const hour = timestamp.substring(8, 10);
        const minute = timestamp.substring(10, 12);
        return `${year}-${month}-${day} ${hour}:${minute}`;
      }
      return timestamp;
    },

    getChangePercent(data) {
      if (!data || data.open === 0) return '0.00%';
      const change = ((data.close - data.open) / data.open * 100).toFixed(2);
      return `${change}%`;
    },

    getChangeClass(data) {
      if (!data) return '';
      const change = data.close - data.open;
      return change > 0 ? 'positive-change' : change < 0 ? 'negative-change' : '';
    },



    handleTabClick(code) {
      if (this.selectedTab === code) return; // 避免重复点击
      
      // 先更新选中的标签，让UI立即响应
      this.selectedTab = code;
      // 立即显示加载状态，不做延迟处理
      this.isLoading = true;
      this.fetchData(); // 切换标签时重新获取数据
    }
  },

  watch: {},
  
  beforeUnmount() {
    // 清理定时器
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer);
    }
  }
}
</script>

<style scoped>
.trend-signal {
  padding: 12px 20px 20px;
  max-width: 1400px;
  margin: 0 auto;
}



.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.loading-text,
.error-text,
.empty-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
}

.retry-button {
  background: #409EFF;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.retry-button:hover {
  background: #337ECC;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.chart-card {
  flex: 2;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-width: 400px;
}

.signal-card {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-width: 250px;
}

.card-header {
  background: #f8f9fa;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
}

.card-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.card-content {
  padding: 0;
}

.detail-info {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 40px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-label {
  font-size: 11px;
  color: #555;
  font-weight: 500;
  margin-right: 2px;
}

.detail-value {
  font-size: 12px;
  font-weight: 600;
  color: #333;
  min-width: 40px;
  text-align: right;
}

.positive-change {
  color: #FD1050;
}

.negative-change {
  color: #00A854;
}

.chart-wrapper {
  padding: 12px;
}

.chart {
  width: 100%;
  height: 330px;
}

.signal-table-wrapper {
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.signal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.signal-table th {
  background: #f8f9fa;
  padding: 7px 5px;
  text-align: center;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #e9ecef;
  font-size: 11px;
}

.signal-table td {
  padding: 4px 4px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s ease;
}

.signal-cell {
  text-align: center;
  width: 50px;
}

.date-cell {
  text-align: center;
  font-weight: 500;
  color: #666;
  font-size: 11px;
}

.time-cell {
  text-align: center;
  font-weight: 500;
  color: #666;
}

.signal-badge {
  display: inline-block;
  padding: 3px 7px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  color: white;
  min-width: 20px;
  text-align: center;
}

.buy-signal {
  background: #FD1050;
}

.sell-signal {
  background: #00A854;
}

.buy-row {
  background: rgba(253, 16, 80, 0.05);
}

.sell-row {
  background: rgba(0, 168, 84, 0.05);
}

.buy-row:hover {
  background: rgba(253, 16, 80, 0.1);
}

.sell-row:hover {
  background: rgba(0, 168, 84, 0.1);
}

.signal-table tr {
  transition: background-color 0.2s ease;
}

.etf-tabs {
  display: flex;
  gap: 10px;
  margin-top: 6px;
  margin-bottom: 12px;
  padding: 10px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch; /* 优化移动端滚动 */
  justify-content: space-between;
  /* 防止导航栏重新加载时的跳动 */
  min-height: 60px;
  align-items: center;
}

.etf-tab {
  padding: 8px 15px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  position: relative;
  overflow: hidden;
  /* 防止切换时的跳动 */
  transform: translateZ(0);
}

.etf-tab:hover {
  color: #333;
  border-color: #e9ecef;
  transform: translateY(-1px) translateZ(0);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.etf-tab.active {
  color: #409EFF;
  border-color: #409EFF;
  background: #e1f3ff;
  font-weight: 600;
  transform: translateY(0) translateZ(0);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.etf-tab.priority-etf {
  background: transparent;
  color: #666;
  border-color: #ddd;
  font-weight: 600;
  box-shadow: none;
  transform: translateY(0) translateZ(0);
}

.etf-tab.priority-etf:hover {
  background: #f8f9fa;
  color: #333;
  border-color: #409EFF;
  transform: translateY(-1px) translateZ(0);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.etf-tab.priority-etf.active {
  background: #e1f3ff;
  color: #409EFF;
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  transform: translateY(0) translateZ(0);
}

/* 内容切换过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(15px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 768px) {
  .trend-signal {
    padding: 10px 12px 12px;
  }
  
  .etf-tabs {
    padding: 8px 12px;
    gap: 8px;
    margin-bottom: 10px;
    min-height: 50px;
    justify-content: flex-start;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE and Edge */
  }
  
  .etf-tabs::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }
  
  .etf-tab {
    padding: 6px 12px;
    font-size: 13px;
    min-width: fit-content;
    flex-shrink: 0;
  }
  
  .chart-row { 
    flex-direction: column; 
    gap: 15px; 
  }
  
  .chart-card,
  .signal-card {
    min-width: auto;
    width: 100%;
  }
  
  .signal-card {
    min-width: 200px;
  }
  
  .detail-info {
    padding: 6px 12px;
    gap: 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .detail-info::-webkit-scrollbar {
    display: none;
  }
  
  .detail-item {
    gap: 3px;
    flex-shrink: 0;
    min-width: fit-content;
  }
  
  .detail-label {
    font-size: 10px;
  }
  
  .detail-value {
    font-size: 11px;
  }
  
  .chart-wrapper {
    padding: 10px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .chart {
    height: 280px;
    min-width: 600px; /* 确保图表内容完整显示 */
  }
  
  .signal-table-wrapper {
    padding: 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  
  .signal-table-wrapper::-webkit-scrollbar {
    display: none;
  }
  
  .signal-table {
    font-size: 11px;
    min-width: 400px; /* 确保表格内容完整显示 */
  }
  
  .signal-table th,
  .signal-table td {
    padding: 4px 2px;
    white-space: nowrap;
  }
  
  .signal-badge {
    padding: 3px 5px;
    font-size: 10px;
    min-width: 20px;
  }
  
  .date-cell {
    font-size: 10px;
  }
  
  .time-cell {
    font-size: 10px;
  }
  

  
  .loading-container,
  .empty-container {
    min-height: 300px;
    padding: 20px;
  }
  
  .loading-text,
  .empty-text {
    font-size: 14px;
    margin-bottom: 15px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .trend-signal {
    padding: 8px 10px 10px;
  }
  
  .etf-tabs {
    padding: 6px 10px;
    gap: 6px;
    margin-bottom: 8px;
  }
  
  .etf-tab {
    padding: 5px 10px;
    font-size: 12px;
  }
  
  .chart {
    height: 250px;
    min-width: 500px;
  }
  
  .signal-table {
    min-width: 350px;
  }
  
  .detail-info {
    padding: 5px 10px;
    gap: 6px;
  }
  
  .detail-label {
    font-size: 9px;
  }
  
  .detail-value {
    font-size: 10px;
  }
  
  .chart-wrapper {
    padding: 8px;
  }
  
  .signal-table-wrapper {
    padding: 10px;
  }
  
  .signal-table th,
  .signal-table td {
    padding: 3px 1px;
  }
  
  .signal-badge {
    padding: 2px 4px;
    font-size: 9px;
  }
}


/* Dark mode styles */
.trend-signal.dark-mode-active .etf-tabs {
  background: #2d2d2d;
  border-color: #4c4d4f;
}

.trend-signal.dark-mode-active .etf-tab {
  color: #b0b3b8;
}

.trend-signal.dark-mode-active .etf-tab:hover {
  color: #e0e0e0;
  border-color: #4c4d4f;
}

.trend-signal.dark-mode-active .etf-tab.active {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
  border-color: #409EFF;
}

/* Global overrides for dark mode */
:global(body.dark-mode) .trend-signal .etf-tabs {
  background: #2d2d2d;
  border-color: #4c4d4f;
}

:global(body.dark-mode) .trend-signal .etf-tab {
  color: #b0b3b8;
}

:global(body.dark-mode) .trend-signal .etf-tab:hover {
  color: #e0e0e0;
  border-color: #4c4d4f;
}

:global(body.dark-mode) .trend-signal .etf-tab.active {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
  border-color: #409EFF;
}

:global(body.dark-mode) .trend-signal .etf-tab.priority-etf:hover {
  background: rgba(64, 158, 255, 0.1);
  color: #e0e0e0;
  border-color: #409EFF;
}

:global(body.dark-mode) .trend-signal .etf-tab.priority-etf.active {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
  border-color: #409EFF;
}

.trend-signal {
  padding: 24px;
  min-height: calc(100vh - 64px);
}

/* Dark Mode 适配 - 全局覆盖 */
body.dark-mode .trend-signal {
  background-color: #1a1a1a !important;
}

body.dark-mode .trend-signal .chart-card,
body.dark-mode .trend-signal .signal-card {
  background: #2d2d2d !important;
  border-color: #4c4d4f !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}
</style> 