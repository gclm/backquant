<template>
  <div class="home-page">
    <div class="header-section">
      <h2 class="page-title">数据全景</h2>
    </div>

    <div class="dashboard-grid">
      <!-- 第一行：ETF动量策略、当日市场温度和股票策略 -->
      <div class="dashboard-row three-columns">
        <!-- ETF策略卡片（合并ETF动量+行情扫描） -->
        <div class="dashboard-card">
      <div class="card-header">
            <h3 class="card-title">📈 ETF策略</h3>
            <p class="card-subtitle" v-if="etfUpdateTime">更新于: {{ formatDate(etfUpdateTime) }}</p>
      </div>
      <div class="card-content">
            <!-- ETF动量策略部分 -->
            <div class="strategy-section">
              <div class="strategy-title">
                <span>📊 动量策略</span>
                <span class="adjustment-hint" :class="getETFAdjustmentClass()" v-if="getETFAdjustmentHint()">{{ getETFAdjustmentHint() }}</span>
              </div>
              <div class="data-row" v-if="topFund">
                <span class="label">今日持仓:</span>
                <template v-if="!isAuthenticated">
                  <span class="value masked-value">***</span>
                </template>
                <template v-else-if="topFund.status === 'stop profit' || topFund.status === 'stop loss'">
                  <span class="value holding-recommendation" :class="getHoldingClass(topFund)">{{ statusText(topFund.status) }}，今日空仓</span>
                </template>
                <template v-else>
                  <span class="value">{{ topFund.fund_name }}（{{ topFund.fund_code }}）</span>
                </template>
              </div>
              <div class="data-row" v-if="topFund && topFund.status !== 'stop profit' && topFund.status !== 'stop loss'">
                <span class="label">策略得分:</span>
                <span class="value" :class="getScoreClass(topFund.score)">
                  {{ isAuthenticated ? topFund.score : '***' }}
                </span>
              </div>
              <div class="data-row" v-if="maxWeekLineData">
                <span class="label">市场移动周线:</span>
                <span class="value" :class="{ 'positive': maxWeekLineData.pct >= 0, 'negative': maxWeekLineData.pct < 0 }">
                  {{ isAuthenticated ? maxWeekLineData.pct.toFixed(2) + '%' : '***%' }}
                </span>
              </div>
            </div>
            <!-- ETF偷鸡摸狗策略部分 -->
            <div class="strategy-section">
              <div class="strategy-title">🦊 ETF扫描</div>
              <div class="data-row">
                <span class="label">扫描结果:</span>
                <span class="value">
                  <template v-if="isLoadingScan">加载中...</template>
                  <template v-else>
                    <span class="scan-badge" :class="{ 'scan-normal': warningFundCount === 0, 'scan-warning': warningFundCount > 0 }">
                      {{ warningFundCount === 0 ? '全部正常' : `异常 ${warningFundCount} 只` }}
                    </span>
                  </template>
                </span>
              </div>
            </div>
      </div>
    </div>
              
        <!-- 当日市场温度卡片 - 交换位置到中间 -->
        <div class="dashboard-card" v-if="currentMarketTemp">
          <div class="card-header">
            <h3 class="card-title">
              🌡️ 当日市场温度
              <span class="help-icon" 
                    @mouseover="showTempHelp = true" 
                    @mouseleave="showTempHelp = false">?</span>
            </h3>
            <p class="card-subtitle" v-if="currentMarketTemp.date">{{ currentMarketTemp.date }}</p>
                </div>
          <div class="card-content">
            <!-- 市场温度热力图 - 垂直温度计放右侧 -->
            <div class="temperature-matrix vertical-layout">
              <!-- 总体温度卡片 - 左侧 -->
              <div class="temp-display-container">
                <div class="total-temp-display vertical" 
                     :style="{ backgroundColor: getNewTempColor(currentMarketTemp.totalTemp, 0.2) }">
                  <div class="total-temp-label">市场总体温度</div>
                  <div class="total-temp-value" :style="{ color: '#303133', textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)' }">
                    {{ currentMarketTemp.totalTemp.toFixed(2) }}
                  </div>
                  <div class="temp-stage" :style="{ color: '#303133', textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)' }">
                    {{ getTempStageName(currentMarketTemp.totalTemp) }}
                </div>
              </div>
            </div>
            
              <!-- 垂直温度计 - 右侧 -->
              <div class="vertical-scale-container" :style="{ '--temp-percent': currentMarketTemp.totalTemp }">
                <div class="scale-label top">
                  <span class="hot-label">100 炙热</span>
                  </div>
                <div class="vertical-scale-gradient"></div>
                <div class="scale-label bottom">
                  <span class="cold-label">0 极寒</span>
                </div>
                
                <!-- 温度指示器 -->
                <div class="temp-indicator-vertical" :style="{ bottom: `${currentMarketTemp.totalTemp}%` }"></div>
              </div>
            </div>
          </div>
          
          <!-- 温度阶段说明弹窗 -->
          <div class="temp-help-popup" v-if="showTempHelp">
            <div class="popup-header">
              <h4>市场温度阶段说明</h4>
        </div>
            <div class="popup-content">
              <div class="stage-row">
                <span class="stage-name">极寒:</span>
                <span class="stage-range">0 - 10</span>
                <span class="stage-color" style="background-color: #0047AB;"></span>
      </div>
              <div class="stage-row">
                <span class="stage-name">寒冷:</span>
                <span class="stage-range">11 - 30</span>
                <span class="stage-color" style="background-color: #6C8CD5;"></span>
    </div>
              <div class="stage-row">
                <span class="stage-name">凉爽:</span>
                <span class="stage-range">31 - 50</span>
                <span class="stage-color" style="background-color: #D6E0F5;"></span>
          </div>
              <div class="stage-row">
                <span class="stage-name">一般:</span>
                <span class="stage-range">51 - 70</span>
                <span class="stage-color" style="background-color: #F7D6D6;"></span>
            </div>
              <div class="stage-row">
                <span class="stage-name">还好:</span>
                <span class="stage-range">71 - 90</span>
                <span class="stage-color" style="background-color: #E57373;"></span>
            </div>
              <div class="stage-row">
                <span class="stage-name">炙热:</span>
                <span class="stage-range">91 - 100</span>
                <span class="stage-color" style="background-color: #FF0000;"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 股票策略卡片 - 右侧 -->
        <div class="dashboard-card">
          <div class="card-header">
            <h3 class="card-title">📊 股票策略</h3>
            <p class="card-subtitle">更新于: {{ currentTime }}</p>
          </div>
          <div class="card-content">
            <!-- 大妈策略数据 -->
            <div class="strategy-section">
              <div class="strategy-title">
                <span>👵 大妈策略</span>
                <span class="adjustment-hint" :class="getDamaAdjustmentClass()" v-if="getDamaAdjustmentHint()">{{ getDamaAdjustmentHint() }}</span>
              </div>
              <div class="data-row">
                <span class="label">月涨幅:</span>
                <span class="value" :class="{ 'positive': weekPct >= 0, 'negative': weekPct < 0 }">
                  {{ isLoadingStock ? '加载中...' : (isAuthenticated ? (weekPct !== null ? weekPct.toFixed(2) + '%' : '--') : '***%') }}
                </span>
              </div>
              <div class="data-row">
                <span class="label">日涨幅(实时):</span>
                <span class="value" :class="{ 'positive': dayPct >= 0, 'negative': dayPct < 0 }">
                  {{ isLoadingStock ? '加载中...' : (isAuthenticated ? (dayPct !== null ? dayPct.toFixed(2) + '%' : '--') : '***%') }}
                </span>
              </div>
            </div>
            <!-- 国九条策略数据 -->
            <div class="strategy-section">
              <div class="strategy-title">
                <span>📋 国九条策略</span>
                <span class="adjustment-hint" :class="getNNGAdjustmentClass()" v-if="getNNGAdjustmentHint()">{{ getNNGAdjustmentHint() }}</span>
              </div>
              <div class="data-row">
                <span class="label">周涨幅:</span>
                <span class="value" :class="{ 'positive': nngWeekPct >= 0, 'negative': nngWeekPct < 0 }">
                  {{ isLoadingNNG ? '加载中...' : (isAuthenticated ? (nngWeekPct !== null ? nngWeekPct.toFixed(2) + '%' : '--') : '***%') }}
                </span>
              </div>
              <div class="data-row">
                <span class="label">日涨幅(实时):</span>
                <span class="value" :class="{ 'positive': nngDayPct >= 0, 'negative': nngDayPct < 0 }">
                  {{ isLoadingNNG ? '加载中...' : (isAuthenticated ? (nngDayPct !== null ? nngDayPct.toFixed(2) + '%' : '--') : '***%') }}
                </span>
              </div>
            </div>
            <!-- 只有在两个指标都触发预警时才显示风格预警 -->
            <div class="data-row" v-if="marketStyleData && isSmallCap">
              <span class="warning-tag full-width">
                <span class="warning-icon">⚠️</span>
                风格预警：可能切换到大盘
              </span>
            </div>
          </div>
        </div>
      </div>


    </div>

    <!-- 历史市场温度卡片 -->
    <div class="dashboard-card market-temp-card market-history-card" v-if="historyMarketTemp.length > 0">
      <div class="card-header">
        <h3 class="card-title">📊 近10日市场热力图</h3>
      </div>
      <div class="card-content">
        <!-- 分类标签行 - 现在放在顶部 -->
        <div class="history-categories-header">
          <div class="date-column-header"></div>
          <div class="category-temp-grid history-labels">
            <div class="category-column total-column">
              <div class="category-label vertical">总体</div>
            </div>
            <div class="column-spacer"></div>
            <div v-for="(cat, index) in categoryOrder" :key="index" class="category-column">
              <div class="category-label vertical">{{ cat }}</div>
            </div>
          </div>
        </div>
        
        <!-- 历史温度热力图 - 纯方块，左侧日期 -->
        <div class="history-heatmap">
          <div v-for="(temp, index) in limitedHistoryTemp" :key="index" class="history-temp-row">
            <div class="date-column">{{ formatShortDate(temp.date) }}</div>
            <div class="category-temp-row">
              <div class="category-column total-column">
                <div class="temp-square modern tight compact" 
                     :style="{ backgroundColor: getNewTempColor(temp.totalTemp) }" 
                     :title="`总温度: ${temp.totalTemp.toFixed(0)}`"
                     @click="showCategoryTooltip('总温度')">
                  <span class="temp-value small" :style="{ color: getTextColorForBackground(temp.totalTemp) }">
                    {{ temp.totalTemp.toFixed(0) }}
                  </span>
                </div>
              </div>
              <div class="column-spacer"></div>
              <div v-for="(cat, catIndex) in categoryOrder" :key="catIndex" class="category-column">
                <div class="temp-square modern tight compact" 
                     :style="{ backgroundColor: getNewTempColor(getCategoryScore(temp.categories, cat)) }" 
                     :title="`${temp.date} ${cat}: ${getCategoryScore(temp.categories, cat).toFixed(0)}`"
                     @click="showCategoryTooltip(cat)">
                  <span class="temp-value small" :style="{ color: getTextColorForBackground(getCategoryScore(temp.categories, cat)) }">
                    {{ getCategoryScore(temp.categories, cat).toFixed(0) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分类弹窗 -->
    <div class="category-tooltip" v-if="tooltipVisible" :style="tooltipStyle">
      <div class="tooltip-content">
        <div class="tooltip-title">{{ tooltipData.category }}</div>
      </div>
    </div>

    <!-- 登录提示弹窗 -->
    <div class="login-prompt" v-if="showLoginPrompt" @click="hideLoginPrompt">
      <div class="login-prompt-content" @click.stop>
        <div class="login-prompt-header">
          <h3>需要登录</h3>
          <button class="close-prompt" @click="hideLoginPrompt">&times;</button>
        </div>
        <div class="login-prompt-body">
          <p>此功能需要登录后才能查看完整数据</p>
          <button class="login-prompt-btn" @click="goToLogin">立即登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS, isProtectedAPI } from '@/config/api';


export default {
  name: 'HomePage',
  props: {
    isAuthenticated: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      etfData: [],
      weekLineData: [],
      stockData: {},
      scanData: [],
      warningFundCount: 0,
      updateTime: null,
      etfUpdateTime: null,
      stockUpdateTime: null,
      scanUpdateTime: null,
      weekPct: null,
      dayPct: null,
      nngWeekPct: null,
      nngDayPct: null,
      marketWidthData: [],
      currentMarketTemp: null,
      historyMarketTemp: [],
      tooltipVisible: false,
      tooltipData: {
        category: '',
        score: 0
      },
      tooltipStyle: {
        top: '0px',
        left: '0px'
      },
      showTempHelp: false,
      marketStyleData: null,
      isSmallCap: false,
      isLoadingStock: true,
      isLoadingNNG: true,
      isLoadingScan: true,
      adjustmentData: [],
      adjustmentUpdateTime: null,
      isLoadingAdjustment: true,
      adjustmentError: null,
      showLoginPrompt: false
    }
  },
  computed: {
    topFund() {
      if (!this.etfData.length) return null;
      const latestDate = [...this.etfData]
        .sort((a, b) => b.data_date.localeCompare(a.data_date))[0].data_date;
      return this.etfData
        .filter(item => item.data_date === latestDate)
        .sort((a, b) => b.score - a.score)[0];
    },
    maxWeekLineData() {
      if (!this.weekLineData.length) return null;
      return [...this.weekLineData].sort((a, b) => 
        new Date(b.index) - new Date(a.index)
      )[0];
    },
    sortedCategories() {
      if (!this.currentMarketTemp) return [];
      // Sort categories alphabetically by name
      return [...this.currentMarketTemp.categories].sort((a, b) => 
        a.name.localeCompare(b.name, 'zh-CN')
      );
    },
    categoryOrder() {
      if (!this.currentMarketTemp) return [];
      return this.currentMarketTemp.categories.map(cat => cat.name);
    },
    limitedHistoryTemp() {
      // 限制显示最近10天的数据
      return this.historyMarketTemp.slice(0, 10);
    },
    currentTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
  },
  methods: {
    reloadAllData() {
      this.fetchETFData();
      this.fetchWeekLineData();
      this.fetchStockData();
      this.fetchScanData();
      this.fetchMarketWidthData();
      this.fetchMarketStyleData();
      this.fetchNNGData();
      this.fetchAdjustmentData();
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      if (dateStr.length === 8) {
        return `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`;
      }
      return dateStr;
    },
    formatUpdateTime(timeStr) {
      if (!timeStr) return '';
      
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },
    formatShortDate(dateStr) {
      // 将日期格式从 YYYY-MM-DD 或 YYYYMMDD 转换为 MM-DD
      if (!dateStr) return '';
      
      let month = '', day = '';
      
      if (dateStr.includes('-')) {
        // 格式为 YYYY-MM-DD
        const parts = dateStr.split('-');
        if (parts.length === 3) {
          month = parts[1];
          day = parts[2];
        }
      } else if (dateStr.length === 8) {
        // 格式为 YYYYMMDD
        month = dateStr.slice(4, 6);
        day = dateStr.slice(6, 8);
      }
      
      return month && day ? `${month}-${day}` : dateStr;
    },
    getScoreClass(score) {
      if (score >= 80) return 'score-high';
      if (score >= 60) return 'score-medium';
      return 'score-low';
    },
    getCategoryScore(categories, categoryName) {
      const category = categories.find(c => c.name === categoryName);
      return category ? category.score : 0;
    },
    async fetchETFData() {
      // 如果是需鉴权接口且未登录，不调用接口，使用默认掩码数据
      if (isProtectedAPI(API_ENDPOINTS.ETF) && !this.isAuthenticated) {
        this.etfData = [];
        this.etfUpdateTime = null;
        this.updateTime = null;
        return;
      }
      
      try {
        const response = await axios.get(API_ENDPOINTS.ETF);
        this.etfData = response.data.data;
        this.etfUpdateTime = this.topFund?.data_date;
        this.updateTime = this.etfUpdateTime;
      } catch (error) {
        console.error('ETF数据获取失败:', error);
        this.etfData = [];
      }
    },
    async fetchWeekLineData() {
      try {
        const response = await axios.get(API_ENDPOINTS.MOVE_WEEK_LINE);
        this.weekLineData = response.data.data;
      } catch (error) {
        console.error('市场移动周线数据获取失败:', error);
      }
    },
    async fetchStockData() {
      // 如果是需鉴权接口且未登录，不调用接口，使用默认掩码数据
      if (isProtectedAPI(API_ENDPOINTS.SMALL_REAL_HQ) && !this.isAuthenticated) {
        this.weekPct = null;
        this.dayPct = null;
        this.isLoadingStock = false;
        return;
      }
      
      try {
        this.isLoadingStock = true;
        const response = await axios.get(API_ENDPOINTS.SMALL_REAL_HQ);
        this.weekPct = response.data.week_pct ? JSON.parse(response.data.week_pct) : null;
        this.dayPct = response.data.day_pct ? JSON.parse(response.data.day_pct) : null;
        
        // 格式化更新时间
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const time = response.data.min_time || '';
        this.stockUpdateTime = `${year}-${month}-${day} ${time}`;
        
        this.isLoadingStock = false;
      } catch (error) {
        console.error('股票数据获取失败:', error);
        this.isLoadingStock = false;
        this.weekPct = null;
        this.dayPct = null;
      }
    },
    async fetchMarketStyleData() {
      try {
        const response = await axios.get(API_ENDPOINTS.BIG_OR_SMALL);
        if (response.data.code === 0 && response.data.data.length > 0) {
          // Get the latest entry
          const latestData = [...response.data.data].sort((a, b) => 
            b.trade_date.localeCompare(a.trade_date)
          )[0];
          
          this.marketStyleData = latestData;
          this.isSmallCap = latestData.pct_avg_diff < -0.5 && latestData.volume_avg_ratio > 1.8;
        }
      } catch (error) {
        console.error('市场风格数据获取失败:', error);
      }
    },
    async fetchScanData() {
      try {
        this.isLoadingScan = true;
        const response = await axios.get(API_ENDPOINTS.SCAN);
        const data = response.data.data;
        
        // 重置警告基金计数
        this.warningFundCount = 0;
        
        if (data) {
          // 创建一个Set来存储有警告的基金代码（去重）
          const warningFunds = new Set();
          
          // 遍历所有基金数据
          Object.values(data).forEach(funds => {
            Object.entries(funds).forEach(([fundCode, fundData]) => {
              // 检查所有warning_开头的字段
              const hasWarning = Object.entries(fundData).some(([key, value]) => {
                return key.startsWith('warning_') && value === 1;
              });
              
              // 如果有警告，添加到Set中（自动去重）
              if (hasWarning) {
                warningFunds.add(fundCode);
              }
            });
          });
          
          // 设置警告基金数量
          this.warningFundCount = warningFunds.size;
        }
        
        this.scanUpdateTime = response.data.data_date;
        this.isLoadingScan = false;
      } catch (error) {
        console.error('扫描数据获取失败:', error);
        this.isLoadingScan = false;
      }
    },
    async fetchMarketWidthData() {
      try {
        const response = await axios.get(API_ENDPOINTS.MARKET_WIDTH);
        this.marketWidthData = response.data.data;
        
        // 处理数据，按日期分组
        const groupedByDate = {};
        
        this.marketWidthData.forEach(item => {
          const date = item.trade_date;
          if (!groupedByDate[date]) {
            groupedByDate[date] = [];
          }
          groupedByDate[date].push(item);
        });
        
        // 获取最新日期和历史日期
        const dates = Object.keys(groupedByDate).sort().reverse();
        
        if (dates.length > 0) {
          // 处理当日温度数据
          const latestDate = dates[0];
          const latestData = groupedByDate[latestDate];
          
          // 找到"合计"的数据
          const totalItem = latestData.find(item => item.category === "合计");
          
          // 找到非"合计"的数据
          const categoryItems = latestData.filter(item => 
            item.category !== "合计" && 
            item.category !== "全市场"
          ).sort((a, b) => a.category.localeCompare(b.category, 'zh-CN'));
          
          // 创建当日温度对象
          if (totalItem) {
            this.currentMarketTemp = {
              date: latestDate,
              totalTemp: totalItem.scores, // 使用合计的原始分数
              categories: categoryItems.map(item => ({
                name: item.category,
                score: item.scores
              }))
            };
          }
          
          // 处理历史温度数据（现在包含最近日期）
          this.historyMarketTemp = dates.map(date => {
            const data = groupedByDate[date];
            const histTotalItem = data.find(item => item.category === "合计");
            const histCategoryItems = data.filter(item => 
              item.category !== "合计" && 
              item.category !== "全市场"
            ).sort((a, b) => b.scores - a.scores);
            
            return {
              date: date,
              totalTemp: histTotalItem ? histTotalItem.scores : 0, // 使用合计的原始分数
              categories: histCategoryItems.map(item => ({
                name: item.category,
                score: item.scores
              }))
            };
          });
        }
      } catch (error) {
        console.error('市场宽度数据获取失败:', error);
      }
    },
    getNewTempColor(value, opacity = 1) {
      // 0: 深蓝, 50: 白色, 100: 红色
      if (value <= 50) {
        // 从深蓝到白色的渐变
        const factor = value / 50;
        return this.interpolateColor('#0047AB', '#FFFFFF', factor, opacity);
      } else {
        // 从白色到红色的渐变
        const factor = (value - 50) / 50;
        return this.interpolateColor('#FFFFFF', '#FF0000', factor, opacity);
      }
    },
    interpolateColor(color1, color2, factor, opacity = 1) {
      // Simple color interpolation
      const result = '#' + (Math.round((parseInt(color1.substring(1, 3), 16) * (1 - factor) + 
                                     parseInt(color2.substring(1, 3), 16) * factor)) << 16 |
                          Math.round((parseInt(color1.substring(3, 5), 16) * (1 - factor) + 
                                     parseInt(color2.substring(3, 5), 16) * factor)) << 8 |
                          Math.round((parseInt(color1.substring(5, 7), 16) * (1 - factor) + 
                                     parseInt(color2.substring(5, 7), 16) * factor))).toString(16).padStart(6, '0');
      return `rgba(${parseInt(result.substring(1, 3), 16)}, ${parseInt(result.substring(3, 5), 16)}, ${parseInt(result.substring(5, 7), 16)}, ${opacity})`;
    },
    getTextColorForBackground(value) {
      // 根据背景颜色决定文字颜色，确保可读性
      // 深色背景用白色文字，浅色背景用黑色文字
      if (value < 30 || value > 70) {
        return '#FFFFFF'; // 白色文字用于深蓝色和深红色背景
      } else {
        return '#000000'; // 黑色文字用于浅色背景
      }
    },
    getEnhancedTextColor(value) {
      // 增强文字颜色对比度
      if (value < 40) {
        return '#FFFFFF'; // 白色文字用于深蓝色背景
      } else if (value > 60) {
        return '#FFFFFF'; // 白色文字用于红色背景
      } else {
        return '#303133'; // 深灰色文字用于浅色背景，比黑色更柔和
      }
    },
    navigateTo(page) {
      this.$emit('navigate', page);
    },
    showCategoryTooltip(category) {
      // 显示分类弹窗，只显示分类名称
      this.tooltipData.category = category;
      this.tooltipVisible = true;
      
      // 计算弹窗位置 - 跟随鼠标
      const updateTooltipPosition = (e) => {
        this.tooltipStyle = {
          top: `${e.clientY + 10}px`,
          left: `${e.clientX + 10}px`
        };
      };

      // 添加一次性鼠标移动监听
      document.addEventListener('mousemove', updateTooltipPosition);
      
      // 点击任意位置关闭弹窗
      const closeTooltip = () => {
        this.tooltipVisible = false;
        document.removeEventListener('mousemove', updateTooltipPosition);
        document.removeEventListener('click', closeTooltip);
      };
      
      document.addEventListener('click', closeTooltip);
    },
    getTempStageName(temp) {
      if (temp <= 10) return '跌麻了，装死中';
      if (temp <= 30) return '寒冷刺骨，熊扎堆';
      if (temp <= 50) return '磨磨唧唧混日子';
      if (temp <= 70) return '局部有亮点，打酱油飘过～';
      if (temp <= 90) return '咋滴，牛快来了？';
      return '撒欢狂奔，牛市嗨起来';
    },
    statusText(status) {
      if (status === 'buy or hold') return '买入或持有';
      if (status === 'stop profit') return '止盈';
      if (status === 'stop loss') return '止损';
      if (status === 'empty position') return '空仓';
      if (status === 'overbought') return '超买';
      return status || '未知';
    },
    getHoldingClass(item) {
      if (item.status === 'buy or hold') return 'status-buy';
      if (item.status === 'stop profit') return 'status-profit';
      if (item.status === 'stop loss') return 'status-loss';
      if (item.status === 'empty position') return 'status-empty';
      return '';
    },
    async fetchNNGData() {
      // 如果是需鉴权接口且未登录，不调用接口，使用默认掩码数据
      if (isProtectedAPI(API_ENDPOINTS.REAL_NNG_HQ) && !this.isAuthenticated) {
        this.nngWeekPct = null;
        this.nngDayPct = null;
        this.isLoadingNNG = false;
        return;
      }
      
      try {
        this.isLoadingNNG = true;
        const response = await axios.get(API_ENDPOINTS.REAL_NNG_HQ);
        if (response.data) {
          this.nngWeekPct = response.data.week_pct ? parseFloat(response.data.week_pct) : null;
          this.nngDayPct = response.data.day_pct ? parseFloat(response.data.day_pct) : null;
        }
        this.isLoadingNNG = false;
      } catch (error) {
        console.error('国九条策略数据获取失败:', error);
        this.isLoadingNNG = false;
        this.nngWeekPct = null;
        this.nngDayPct = null;
      }
    },
    async fetchAdjustmentData() {
      // 如果是需鉴权接口且未登录，不调用接口，使用默认掩码数据
      if (isProtectedAPI(API_ENDPOINTS.ADJUST_LOG) && !this.isAuthenticated) {
        this.adjustmentData = [];
        this.adjustmentError = null;
        this.isLoadingAdjustment = false;
        return;
      }
      
      try {
        this.isLoadingAdjustment = true;
        this.adjustmentError = null;
        
        const response = await axios.get(API_ENDPOINTS.ADJUST_LOG);
        
        if (response.data.code === 0 && response.data.data) {
          this.adjustmentData = response.data.data;
          this.adjustmentUpdateTime = new Date().toISOString().split('T')[0];
        } else {
          this.adjustmentError = '暂无调仓建议数据';
        }
      } catch (error) {
        console.error('获取调仓建议失败:', error);
        this.adjustmentError = '获取调仓建议失败';
        this.adjustmentData = [];
      } finally {
        this.isLoadingAdjustment = false;
      }
    },
    getStrategyData(strategyName) {
      return this.adjustmentData.filter(item => item.strategy === strategyName);
    },
    getETFAdjustmentSummary() {
      const data = this.getStrategyData('ETF动量策略');
      if (!data.length) return '暂无建议';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      let summary = [];
      if (buyItems.length > 0) {
        const buyNames = buyItems.map(item => item.name).join('、');
        summary.push(`买入${buyNames}`);
      }
      if (sellItems.length > 0) {
        const sellNames = sellItems.map(item => item.name).join('、');
        summary.push(`卖出${sellNames}`);
      }
      if (holdItems.length > 0) {
        summary.push('其余持仓不变');
      }
      
      return summary.join('，');
    },
    getDamaAdjustmentSummary() {
      const data = this.getStrategyData('大妈策略');
      if (!data.length) return '暂无建议';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      let summary = [];
      if (buyItems.length > 0) {
        const buyNames = buyItems.map(item => item.name).join('、');
        summary.push(`买入${buyNames}`);
      }
      if (sellItems.length > 0) {
        const sellNames = sellItems.map(item => item.name).join('、');
        summary.push(`卖出${sellNames}`);
      }
      if (holdItems.length > 0) {
        summary.push('其余持仓不变');
      }
      
      return summary.join('，');
    },
    getNNGAdjustmentSummary() {
      const data = this.getStrategyData('国九条策略');
      if (!data.length) return '暂无建议';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      let summary = [];
      if (buyItems.length > 0) {
        const buyNames = buyItems.map(item => item.name).join('、');
        summary.push(`买入${buyNames}`);
      }
      if (sellItems.length > 0) {
        const sellNames = sellItems.map(item => item.name).join('、');
        summary.push(`卖出${sellNames}`);
      }
      if (holdItems.length > 0) {
        summary.push('其余持仓不变');
      }
      
      return summary.join('，');
    },
    getETFAdjustmentHint() {
      const data = this.getStrategyData('ETF动量策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        let parts = [];
        if (buyItems.length > 0) parts.push(`买入${buyItems.length}只`);
        if (sellItems.length > 0) parts.push(`卖出${sellItems.length}只`);
        return parts.join('，');
      }
      
      return '';
    },
    getETFAdjustmentClass() {
      const data = this.getStrategyData('ETF动量策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return 'adjustment-hold';
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        return 'adjustment-trade';
      }
      
      return '';
    },
    getDamaAdjustmentHint() {
      const data = this.getStrategyData('大妈策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        let parts = [];
        if (buyItems.length > 0) parts.push(`买入${buyItems.length}只`);
        if (sellItems.length > 0) parts.push(`卖出${sellItems.length}只`);
        return parts.join('，');
      }
      
      return '';
    },
    getDamaAdjustmentClass() {
      const data = this.getStrategyData('大妈策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return 'adjustment-hold';
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        return 'adjustment-trade';
      }
      
      return '';
    },
    getNNGAdjustmentHint() {
      const data = this.getStrategyData('国九条策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return `继续持仓${holdItems.length}只`;
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        let parts = [];
        if (buyItems.length > 0) parts.push(`买入${buyItems.length}只`);
        if (sellItems.length > 0) parts.push(`卖出${sellItems.length}只`);
        return parts.join('，');
      }
      
      return '';
    },
    getETFAdjustmentClass() {
      const data = this.getStrategyData('ETF动量策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return 'adjustment-hold';
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        return 'adjustment-trade';
      }
      
      return '';
    },
    getNNGAdjustmentClass() {
      const data = this.getStrategyData('国九条策略');
      if (!data.length) return '';
      
      const buyItems = data.filter(item => item.status === 'buy');
      const sellItems = data.filter(item => item.status === 'sell');
      const holdItems = data.filter(item => item.status === 'hold');
      
      if (buyItems.length === 0 && sellItems.length === 0 && holdItems.length > 0) {
        return 'adjustment-hold';
      }
      
      if (buyItems.length > 0 || sellItems.length > 0) {
        return 'adjustment-trade';
      }
      
      return '';
    },
    
    showLoginPromptDialog() {
      this.showLoginPrompt = true;
    },
    
    hideLoginPrompt() {
      this.showLoginPrompt = false;
    },
    
    goToLogin() {
      this.$emit('navigate', 'login');
    }
  },
  watch: {
    isAuthenticated(newVal, oldVal) {
      // 当认证状态从未登录变为已登录时，重新加载所有数据
      if (!oldVal && newVal) {
