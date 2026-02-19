<template>
  <div class="adjustment-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="page-header">
      <h2 class="page-title">今日调仓</h2>
      <div class="header-actions">
        <button class="filter-btn" @click="toggleZeroPositions" :class="{ 'active': hideZeroPosition }">
          <svg class="filter-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
          </svg>
          {{ hideZeroPosition ? '显示清仓' : '隐藏清仓' }}
        </button>
        <div class="custom-date-picker">
          <div class="picker-input" @click="toggleDatePicker" :class="{ 'active': showDatePicker }">
            <span class="picker-text" :class="{ 'placeholder': !selectedDate }">
              {{ selectedDate ? formatDateDisplay(selectedDate) : '选择查询日期' }}
            </span>
            <svg class="calendar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
          </div>
          
          <div class="picker-popup" v-if="showDatePicker">
            <div class="picker-header">
              <button class="nav-btn" @click.stop="changeMonth(-1)">&lt;</button>
              <span class="current-month">{{ currentMonthLabel }}</span>
              <button class="nav-btn" @click.stop="changeMonth(1)">&gt;</button>
            </div>
            <div class="picker-body">
              <div class="weekdays">
                <span v-for="day in weekDays" :key="day">{{ day }}</span>
              </div>
              <div class="days-grid">
                <div 
                  v-for="(day, index) in calendarDays" 
                  :key="index"
                  class="day-cell"
                  :class="{
                    'current-month': day.isCurrentMonth,
                    'other-month': !day.isCurrentMonth,
                    'today': day.isToday,
                    'selected': day.isSelected,
                    'disabled': day.isDisabled
                  }"
                  @click.stop="selectDate(day)"
                >
                  {{ day.date.getDate() }}
                </div>
              </div>
            </div>
          </div>
        </div>
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

    <div class="overflow-x-auto rounded-xl border border-slate-200 shadow-sm bg-white" v-if="!isMobile">
      <table class="w-full text-left text-sm text-slate-600">
        <thead class="bg-slate-50 text-xs uppercase font-medium text-slate-500">
          <tr>
            <th class="px-4 py-3 font-semibold">日期</th>
            <th class="px-4 py-3 font-semibold">策略名称</th>
            <th class="px-4 py-3 font-semibold">证券代码</th>
            <th class="px-4 py-3 font-semibold">证券名称</th>
            <th class="px-4 py-3 font-semibold text-right">当前仓位</th>
            <th class="px-4 py-3 font-semibold text-right">仓位变化</th>
            <th class="px-4 py-3 font-semibold text-right">调仓金额</th>
            <th class="px-4 py-3 font-semibold">持仓状态</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="(record, index) in sortedAdjustmentData" 
              :key="`${record.strategy}-${record.code}`"
              :class="getRowClass(index)">
            <td class="px-4 py-3 font-sans-numeric tabular-nums">{{ formatDateDisplay(record.date) }}</td>
            <td class="px-4 py-3">
              <span class="strategy-badge" :class="getStrategyBadgeClass(record.strategy)">{{ record.strategy }}</span>
            </td>
            <td class="px-4 py-3 code-cell font-sans-numeric tabular-nums">{{ record.code }}</td>
            <td class="px-4 py-3">{{ record.name }}</td>
            <td class="px-4 py-3 weight-cell font-sans-numeric font-semibold text-right">{{ formatWeight(record.weight) }}</td>
            <td class="px-4 py-3 weight-change-cell font-sans-numeric font-semibold text-right" :class="getWeightChangeClass(record.weight_change)">
              {{ formatWeightChange(record) }}
            </td>
            <td class="px-4 py-3 estimated-amount-cell font-sans-numeric font-semibold text-right" :class="getWeightChangeClass(record.weight_change)">
              {{ formatEstimatedAmount(record) }}
            </td>
            <td class="px-4 py-3">
              <span :class="getStatusClass(record)">{{ getStatusText(record) }}</span>
            </td>
          </tr>
          <tr v-if="adjustmentData.length === 0">
            <td colspan="8" class="px-4 py-3 empty-cell">{{ emptyMessage }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="cards-container" v-else>
      <div class="adjustment-card" 
           v-for="(record, index) in sortedAdjustmentData" 
           :key="`${record.strategy}-${record.code}`"
           :class="getCardClass(index)">
        <div class="card-header">
          <h3 class="card-title">{{ record.name }}</h3>
          <span class="card-date">{{ formatDateDisplay(record.date) }}</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">策略:</span>
            <span class="value">
              <span class="strategy-badge" :class="getStrategyBadgeClass(record.strategy)">{{ record.strategy }}</span>
            </span>
          </div>
          <div class="info-row">
            <span class="label">代码:</span>
            <span class="value font-mono">{{ record.code }}</span>
          </div>
          <div class="info-row">
            <span class="label">当前仓位:</span>
            <span class="value weight-cell font-mono font-semibold">{{ formatWeight(record.weight) }}</span>
          </div>
          <div class="info-row">
            <span class="label">仓位变化:</span>
            <span class="value weight-change font-mono font-semibold" :class="getWeightChangeClass(record.weight_change)">{{ formatWeightChange(record) }}</span>
          </div>
          <div class="info-row">
            <span class="label">调仓金额:</span>
            <span class="value estimated-amount font-mono font-semibold" :class="getWeightChangeClass(record.weight_change)">{{ formatEstimatedAmount(record) }}</span>
          </div>
          <div class="info-row">
            <span class="label">状态:</span>
            <span :class="getStatusClass(record)">{{ getStatusText(record) }}</span>
          </div>
        </div>
      </div>
      <div v-if="adjustmentData.length === 0" class="empty-state">
        {{ emptyMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axios';
import { API_ENDPOINTS } from '@/config/api';

export default {
  name: 'AdjustmentRecommendation',
  props: {
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      adjustmentData: [],
      selectedDate: '',
      emptyMessage: '暂无调仓信号数据',
      isMobile: false,
      strategies: [], // 策略列表
      hideZeroPosition: false,
      // Date Picker Data
      showDatePicker: false,
      currentViewDate: new Date(),
      weekDays: ['日', '一', '二', '三', '四', '五', '六']
    };
  },
  computed: {
    currentMonthLabel() {
      const year = this.currentViewDate.getFullYear();
      const month = this.currentViewDate.getMonth() + 1;
      return `${year}年${month}月`;
    },
    calendarDays() {
      const year = this.currentViewDate.getFullYear();
      const month = this.currentViewDate.getMonth();
      
      const firstDayOfMonth = new Date(year, month, 1);
      const startDate = new Date(firstDayOfMonth);
      startDate.setDate(startDate.getDate() - startDate.getDay());
      
      const days = [];
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        date.setHours(0, 0, 0, 0);
        
        const isCurrentMonth = date.getMonth() === month;
        const isToday = date.getTime() === today.getTime();
        
        const dateStr = this.formatDateToYYYYMMDD(date, '-');
        const isSelected = this.selectedDate === dateStr;

        const dayOfWeek = date.getDay();
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isFuture = date > today;
        
        days.push({
          date,
          isCurrentMonth,
          isToday,
          isSelected,
          isDisabled: isWeekend || isFuture
        });
      }
      return days;
    },
    sortedAdjustmentData() {
      let data = this.adjustmentData;

      // Step 1: Filter zero positions if enabled
      if (this.hideZeroPosition) {
        data = data.filter(record => {
           const weight = parseFloat(record.weight) || 0;
           return Math.abs(weight) > 0.0001; // Filter out near-zero weights
        });
      }
      
      // Step 2: Sort by strategy name and position change
      const sorted = [...data].sort((a, b) => {
        // First by strategy
        if (a.strategy !== b.strategy) {
          return a.strategy.localeCompare(b.strategy, 'zh-Hans-CN');
        }
        // Then by absolute weight change (descending)
        const changeA = Math.abs(parseFloat(a.weight_change) || 0);
        const changeB = Math.abs(parseFloat(b.weight_change) || 0);
        return changeB - changeA;
      });

      return sorted;
    }
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },
    formatDateDisplay(dateStr) {
      if (!dateStr) return '-';
      // Return raw YYYYMMDD without dashes, ensure dashes are removed if present
      return dateStr.replace(/-/g, '');
    },
    formatDateToYYYYMMDD(date, separator = '') {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      return `${year}${separator}${month}${separator}${d}`;
    },
    toggleZeroPositions() {
      this.hideZeroPosition = !this.hideZeroPosition;
    },
    toggleDatePicker() {
      this.showDatePicker = !this.showDatePicker;
      if (this.showDatePicker) {
        if (this.selectedDate) {
          // Parse YYYY-MM-DD format
          const parts = this.selectedDate.split('-');
          if (parts.length === 3) {
            this.currentViewDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
          }
        } else {
          this.currentViewDate = new Date();
        }
      }
    },
    closeDatePicker() {
      this.showDatePicker = false;
    },
    changeMonth(offset) {
      const newDate = new Date(this.currentViewDate);
      newDate.setMonth(newDate.getMonth() + offset);
      this.currentViewDate = newDate;
    },
    async selectDate(day) {
      if (day.isDisabled) return;
      
      this.selectedDate = this.formatDateToYYYYMMDD(day.date, '-');
      this.showDatePicker = false;
      await this.fetchAdjustmentData();
    },
    handleClickOutside(e) {
      const picker = this.$el.querySelector('.custom-date-picker');
      if (picker && !picker.contains(e.target)) {
        this.closeDatePicker();
      }
    },
    async fetchAdjustmentData() {
      this.loading = true;
      this.error = null;
      
      try {
        let url = API_ENDPOINTS.ADJUST_LOG;
        
        // Add query_date parameter if date is selected
        if (this.selectedDate) {
          const dateParam = this.selectedDate.replace(/-/g, '');
          url = `${API_ENDPOINTS.ADJUST_LOG}?query_date=${dateParam}`;
        }
        
        const response = await axios.get(url);
        
        if (response.data.code === 0 && response.data.data) {
          this.adjustmentData = response.data.data;
          
          if (this.adjustmentData.length === 0 && this.selectedDate) {
            this.emptyMessage = `${this.selectedDate} 暂无调仓信号数据`;
          } else if (this.adjustmentData.length === 0) {
            this.emptyMessage = '暂无调仓信号数据';
          }
        } else {
          this.error = '暂无调仓信号数据';
        }
      } catch (error) {
        console.error('获取调仓信号失败:', error);
        this.error = '获取调仓信号失败,请稍后重试';
      } finally {
        this.loading = false;
      }
    },
    getStatusText(record) {
      // 优先判断止损
      if (record.stop_loss === 1) return '止损';
      
      const change = Number(record.weight_change) || 0;
      if (change > 0) return '加仓';
      if (change < 0) return '减仓';
      return '持仓';
    },
    getStatusClass(record) {
      // 优先判断止损
      if (record.stop_loss === 1) return 'status-badge status-stop-loss';
      
      const change = Number(record.weight_change) || 0;
      if (change > 0) return 'status-badge status-buy';
      if (change < 0) return 'status-badge status-sell';
      return 'status-badge status-hold';
    },
    formatWeightChange(record) {
      // 止损时显示特殊文本
      if (record.stop_loss === 1) return '以实际为准';
      
      const weightChange = record.weight_change;
      if (weightChange === null || weightChange === undefined) return '-';
      const change = Number(weightChange);
      return `${(change * 100).toFixed(2)}%`;
    },
    formatEstimatedAmount(record) {
      // 止损时显示特殊文本
      if (record.stop_loss === 1) return '以实际为准';
      
      if (!record.weight_change) return '-';
      // 查找对应策略的strategy_size
      const strategy = this.strategies.find(s => s.strategy_name === record.strategy);
      if (!strategy || !strategy.strategy_size) return '-';
      
      const change = Math.abs(Number(record.weight_change));
      const amount = Number(strategy.strategy_size) * change;
      return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    getWeightChangeClass(weightChange) {
      const change = Number(weightChange) || 0;
      if (change > 0) return 'positive-change';
      if (change < 0) return 'negative-change';
      return 'neutral-change';
    },
    getRowClass(index) {
      const record = this.sortedAdjustmentData[index];
      // 获取当前策略的背景色class
      let className = this.getStrategyBgClass(record.strategy);
      
      // 止损行添加特殊类
      if (record.stop_loss === 1) {
        className += ' stop-loss-row';
      }
      
      if (index === 0) {
        return className + ' strategy-group-start';
      }
      
      const currentStrategy = record.strategy;
      const prevStrategy = this.sortedAdjustmentData[index - 1].strategy;
      
      if (currentStrategy !== prevStrategy) {
        className += ' strategy-group-start';
      }
      
      return className;
    },
    getCardClass(index) {
      const record = this.sortedAdjustmentData[index];
      // 获取当前策略的背景色class
      let className = this.getStrategyBgClass(record.strategy);
      
      // 止损卡片添加特殊类
      if (record.stop_loss === 1) {
        className += ' stop-loss-row';
      }
      
      if (index === 0) {
        return className + ' strategy-group-start';
      }
      
      const currentStrategy = record.strategy;
      const prevStrategy = this.sortedAdjustmentData[index - 1].strategy;
      
      if (currentStrategy !== prevStrategy) {
        className += ' strategy-group-start';
      }
      
      return className;
    },
    getStrategyBgClass() {
      // 统一使用一种背景色
      return 'strategy-bg-1';
    },
    getStrategyBadgeClass(strategyName) {
      if (!this.strategies || this.strategies.length === 0) return 'badge-color-1';
      
      // Get all unique strategy names from the global list and sort them
      const uniqueStrategies = [...new Set(this.strategies.map(s => s.strategy_name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      if (index === -1) return 'badge-color-1';
      
      // Cycle through 10 distinct colors
      const colorIndex = (index % 10) + 1;
      return `badge-color-${colorIndex}`;
    },
    async fetchStrategies() {
      try {
        const response = await axios.get('/api/strategy/list');
        if (response.data.code === 200 && response.data.data) {
          this.strategies = response.data.data.strategy_list || [];
        }
      } catch (error) {
        // 静默失败,不影响主功能
      }
    },
    formatWeight(weight) {
      if (weight === null || weight === undefined) return '-';
      return `${(weight * 100).toFixed(2)}%`;
    }
  },
  mounted() {
    this.checkMobile();
    window.addEventListener('click', this.handleClickOutside);
    window.addEventListener('resize', this.checkMobile);
    this.fetchStrategies(); // 获取策略列表
    this.fetchAdjustmentData();
  },
  beforeUnmount() {
    window.removeEventListener('click', this.handleClickOutside);
    window.removeEventListener('resize', this.checkMobile);
  }
};
</script>

<style scoped>
.adjustment-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  color: #1e293b;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
  height: 40px;
}

.filter-btn:hover {
  background-color: #f8fafc;
  color: #334155;
  border-color: #cbd5e1;
}

.filter-btn.active {
  background-color: #eff6ff;
  color: #3b82f6;
  border-color: #bfdbfe;
}

.filter-icon {
  width: 16px;
  height: 16px;
}

/* Custom Date Picker Styles */
.custom-date-picker {
  position: relative;
  min-width: 200px;
}

.picker-input {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.picker-input:hover,
.picker-input.active {
  border-color: #409EFF;
}

.picker-text {
  color: #606266;
}

.picker-text.placeholder {
  color: #909399;
}

.calendar-icon {
  width: 16px;
  height: 16px;
  color: #909399;
}

.picker-popup {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid #e4e7ed;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  z-index: 2000;
  width: 280px;
  padding: 12px;
  animation: pickerSlideDown 0.2s ease;
}

@keyframes pickerSlideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.nav-btn {
  background: none;
  border: none;
  color: #606266;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 16px;
  transition: color 0.3s;
}

.nav-btn:hover {
  color: #409EFF;
}

.current-month {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.picker-body {
  display: flex;
  flex-direction: column;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekdays span {
  text-align: center;
  font-size: 12px;
  color: #909399;
  padding: 4px;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.day-cell.current-month {
  color: #606266;
}

.day-cell.other-month {
  color: #c0c4cc;
}

.day-cell.today {
  background: #ecf5ff;
  color: #409EFF;
  font-weight: 600;
}

.day-cell.selected {
  background: #409EFF;
  color: white;
  font-weight: 600;
}

.day-cell.disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  background: #f5f7fa;
}

.day-cell:not(.disabled):hover {
  background: #f5f7fa;
}

.day-cell.selected:hover {
  background: #409EFF;
}

/* Loading and Error States */
.loading-state,
.error-state {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  padding: 40px;
  text-align: center;
  border: 1px solid #f3f4f6;
}

.loading-state p,
.error-state p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
}

.error-state p {
  color: #f56c6c;
}



/* Remove old manual styles that are replaced by Tailwind classes */
/* Table Styles */
/* .table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  overflow-x: auto;
  border: 1px solid #e2e8f0;
}

.adjustment-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
} */

.adjustment-table tbody tr {
  transition: background-color 0.2s;
}

/* .adjustment-table tbody tr:hover {
  background-color: #f8fafc;
} */

/* 策略分组样式 - 按策略名称区分背景色 */
.adjustment-table tbody tr.strategy-group-start {
  border-top: 2px solid #e2e8f0;
}

/* 按策略名称分配背景色 - Tailwind hover interferes, so we enforce background color logic slightly differently */
tr.strategy-bg-1 {
  background-color: #f8fafc; /* Slate-50 */
}

/* We need to be specific to override hover sometimes, or let hover stack */
/* For this specific requirement, simple background alternate is fine. Tailwind implementation above adds hover. */

/* .adjustment-table tbody tr:hover {
  background-color: #e2e8f0;
} */

/* .adjustment-table th,
.adjustment-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  color: #475569;
  font-size: 14px;
} */

/* .adjustment-table th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.03em;
  white-space: nowrap;
} */

.strategy-cell {
  font-weight: 600;
  color: #334155;
}

.strategy-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  line-height: 1.4;
}

/* Strategy Badge Styles - 10 Distinct Colors (No Purple) */
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
.dark-mode .badge-color-1 { background-color: #1e3a8a; color: #93c5fd; }
.dark-mode .badge-color-2 { background-color: #164e63; color: #67e8f9; }
.dark-mode .badge-color-3 { background-color: #14532d; color: #86efac; }
.dark-mode .badge-color-4 { background-color: #7c2d12; color: #fdba74; }
.dark-mode .badge-color-5 { background-color: #831843; color: #f9a8d4; }
.dark-mode .badge-color-6 { background-color: #7f1d1d; color: #fca5a5; }
.dark-mode .badge-color-7 { background-color: #713f12; color: #fde047; }
.dark-mode .badge-color-8 { background-color: #115e59; color: #5eead4; }
.dark-mode .badge-color-9 { background-color: #365314; color: #bef264; }
.dark-mode .badge-color-10 { background-color: #334155; color: #cbd5e1; }

.code-cell {
  font-size: 13px;
  color: #64748b;
}

.highlight-col {
  font-weight: 600;
}

.weight-change-cell,
.estimated-amount-cell {
  font-weight: 700;
  font-size: 14px;
}

.positive-change {
  color: #dc2626 !important;
}

.negative-change {
  color: #059669 !important;
}

.neutral-change {
  color: #64748b !important;
}

.empty-cell {
  text-align: center;
  color: #94a3b8;
  padding: 40px !important;
  font-size: 14px;
}

.font-sans-numeric {
  font-family: "Inter", -apple-system, "PingFang SC", sans-serif;
  letter-spacing: -0.01em; /* Slight tightening for numbers */
}

/* Status Badge Styles - 突出显示 */
.status-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.02em;
}

.status-hold {
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
}

.status-sell {
  color: #059669;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
}

.status-buy {
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
}

.status-stop-loss {
  color: #ea580c;
  background: #ffedd5;
  border: 1px solid #fb923c;
  font-weight: 700;
}

/* 止损行边框 */
tr.stop-loss-row {
  border: 2px solid #5c7ff4ff !important;
  box-shadow: 0 0 0 1px #5c7ff4ff;
}

.adjustment-card.stop-loss-row {
  border: 2px solid #5c7ff4ff !important;
  box-shadow: 0 2px 8px rgba(251, 146, 60, 0.3);
}

/* Mobile Card View */
.cards-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.adjustment-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.adjustment-card.strategy-group-start {
  margin-top: 8px;
  border-top: 2px solid #409EFF;
}

.adjustment-card.strategy-group-start:first-child {
  margin-top: 0;
}

.card-header {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fafbfc;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-date {
  font-size: 12px;
  color: #64748b;
}

.card-body {
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.info-row .value {
  color: #1e293b;
  font-size: 14px;
  font-weight: 600;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  border: 1px solid #e2e8f0;
  font-size: 14px;
}

.font-mono {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* Responsive */
@media (max-width: 768px) {
  .adjustment-container {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 24px;
  }

  .custom-date-picker {
    width: 100%;
  }

  .picker-input {
    width: 100%;
  }
}

/* Dark Mode Styles */
body.dark-mode .adjustment-container {
  background-color: #0f172a !important;
}

body.dark-mode .page-title {
  color: #f1f5f9 !important;
}

body.dark-mode .picker-input {
  background-color: #1e293b !important;
  border-color: #334155 !important;
  color: #f1f5f9 !important;
}

body.dark-mode .picker-text {
  color: #f1f5f9 !important;
}

body.dark-mode .picker-text.placeholder {
  color: #94a3b8 !important;
}

body.dark-mode .picker-popup {
  background-color: #1e293b !important;
  border-color: #334155 !important;
}

body.dark-mode .current-month {
  color: #f1f5f9 !important;
}

body.dark-mode .nav-btn {
  color: #f1f5f9 !important;
}

body.dark-mode .day-cell.current-month {
  color: #f1f5f9 !important;
}

body.dark-mode .day-cell:not(.disabled):hover {
  background: #334155 !important;
}

body.dark-mode .loading-state,
body.dark-mode .error-state,
body.dark-mode .table-container,
body.dark-mode .adjustment-card,
body.dark-mode .empty-state {
  background-color: #1e293b !important;
  border-color: #334155 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

body.dark-mode .adjustment-table th {
  background-color: #0f172a !important;
  color: #94a3b8 !important;
  border-bottom-color: #334155 !important;
}

body.dark-mode .adjustment-table td {
  color: #cbd5e1 !important;
  border-bottom-color: #334155 !important;
}

body.dark-mode .adjustment-table tbody tr.strategy-bg-1 {
  background-color: #000000 !important; /* Pure Black */
}

/* Dark Mode Background */
body.dark-mode .adjustment-table tbody tr.strategy-bg-1 {
  background-color: #000000 !important; /* Pure Black */
}

body.dark-mode .adjustment-table tbody tr:hover {
  background-color: #1a1a1a !important;
}

body.dark-mode .strategy-cell {
  color: #f1f5f9 !important;
}

body.dark-mode .code-cell {
  color: #94a3b8 !important;
}

body.dark-mode .card-header {
  border-bottom-color: #334155 !important;
  background-color: #1a2332 !important;
}

body.dark-mode .card-title {
  color: #f1f5f9 !important;
}

body.dark-mode .info-row {
  border-bottom-color: #334155 !important;
}

body.dark-mode .info-row .value {
  color: #f1f5f9 !important;
}

body.dark-mode .status-badge {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

body.dark-mode .status-hold {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.1);
  border-color: rgba(148, 163, 184, 0.2);
}

body.dark-mode .status-sell {
  color: #059669;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
}

body.dark-mode .status-buy {
  color: #dc2626;
  background: #fee2e2;
  border: 1px solid #fca5a5;
}

body.dark-mode .status-stop-loss {
  color: #fb923c;
  background: rgba(234, 88, 12, 0.2);
  border: 1px solid rgba(251, 146, 60, 0.4);
}

body.dark-mode tr.stop-loss-row {
  border: 2px solid #fb923c !important;
  box-shadow: 0 0 0 1px #fb923c;
}

body.dark-mode .adjustment-card.stop-loss-row {
  border: 2px solid #fb923c !important;
  box-shadow: 0 2px 8px rgba(251, 146, 60, 0.4);
}

body.dark-mode .amount-input::placeholder {
  color: #64748b !important;
}

body.dark-mode .estimate-amount-input::placeholder {
  color: #64748b !important;
}

body.dark-mode .text-slate-900 {
  color: #e2e8f0 !important; /* Update dark mode text color for numbers */
}

body.dark-mode .positive-change {
  color: #f87171 !important;
}

body.dark-mode .negative-change {
  color: #34d399 !important;
}

body.dark-mode .price-up { color: #f87171; }
body.dark-mode .price-down { color: #34d399; }

/* Dark Mode Badges */
body.dark-mode .badge-color-0 { color: #60a5fa; background-color: rgba(37, 99, 235, 0.2); border-color: rgba(37, 99, 235, 0.4); }
body.dark-mode .badge-color-1 { color: #22d3ee; background-color: rgba(8, 145, 178, 0.2); border-color: rgba(8, 145, 178, 0.4); } /* Cyan */
body.dark-mode .badge-color-2 { color: #4ade80; background-color: rgba(22, 163, 74, 0.2); border-color: rgba(22, 163, 74, 0.4); }
body.dark-mode .badge-color-3 { color: #fb923c; background-color: rgba(234, 88, 12, 0.2); border-color: rgba(234, 88, 12, 0.4); }
body.dark-mode .badge-color-4 { color: #f472b6; background-color: rgba(219, 39, 119, 0.2); border-color: rgba(219, 39, 119, 0.4); }
</style>