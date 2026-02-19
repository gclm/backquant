<template>
  <div class="manual-clear-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="page-header">
      <h2 class="page-title">手工清算管理</h2>
      <div class="header-actions">
        <div class="custom-date-picker">
          <div class="picker-input" @click="toggleDatePicker" :class="{ 'active': showDatePicker }">
            <span class="picker-text" :class="{ 'placeholder': !selectedDate }">
              {{ selectedDate ? selectedDate : '选择清算日期' }}
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
        <button class="add-btn" @click="openAddModal">
          <i class="plus-icon"></i> 新增记录
        </button>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div class="table-container" v-if="!isMobile">
      <table class="clear-table">
        <thead>
          <tr>
            <th>清算日期</th>
            <th>策略名称</th>
            <th>证券代码</th>
            <th>证券名称</th>
            <th>持仓数量</th>
            <th>收盘价</th>
            <th>市值</th>
            <th>总成本</th>
            <th>已实现盈亏</th>
            <th class="w-20" style="text-align: center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in sortedClearRecords" :key="record.id">
            <td>{{ formatDateCompact(record.clear_date) }}</td>
            <td>
              <span class="strategy-badge" :class="getStrategyBadgeClass(record.strategy_name)">{{ record.strategy_name }}</span>
            </td>
            <td class="font-mono">{{ record.security_code }}</td>
            <td>{{ record.security_name }}</td>
            <td class="font-mono font-semibold">{{ formatNumber(record.hold_qty) }}</td>
            <td class="font-mono font-semibold">{{ formatDecimal(record.close_price) }}</td>
            <td class="font-mono font-semibold">{{ formatDecimal(record.market_value) }}</td>
            <td class="font-mono font-semibold">{{ formatDecimal(record.total_cost) }}</td>
            <td class="font-mono font-semibold" :class="getProfitClass(record.realized_profit)">{{ formatDecimal(record.realized_profit) }}</td>
            <td class="actions-cell">
              <button class="icon-btn edit" @click="openEditModal(record)" title="编辑">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button class="icon-btn delete" @click="confirmDelete(record)" title="删除">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="clearRecords.length === 0">
            <td colspan="10" class="empty-cell">{{ emptyMessage }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="cards-container" v-else>
      <div class="clear-card" v-for="record in sortedClearRecords" :key="record.id">
        <div class="card-header">
          <h3 class="card-title">{{ record.security_name }}</h3>
          <span class="card-date">{{ formatDateDisplay(record.clear_date) }}</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">策略:</span>
            <span class="value">
              <span class="strategy-badge" :class="getStrategyBadgeClass(record.strategy_name)">{{ record.strategy_name }}</span>
            </span>
          </div>
          <div class="info-row">
            <span class="label">代码:</span>
            <span class="value font-mono">{{ record.security_code }}</span>
          </div>
          <div class="info-row">
            <span class="label">持仓:</span>
            <span class="value font-mono font-semibold">{{ formatNumber(record.hold_qty) }}</span>
          </div>
          <div class="info-row">
            <span class="label">收盘价:</span>
            <span class="value font-mono font-semibold">{{ formatNumber(record.close_price) }}</span>
          </div>
          <div class="info-row">
            <span class="label">市值:</span>
            <span class="value font-mono font-semibold">{{ formatNumber(record.market_value) }}</span>
          </div>
          <div class="info-row">
            <span class="label">成本:</span>
            <span class="value font-mono font-semibold">{{ formatNumber(record.total_cost) }}</span>
          </div>
          <div class="info-row">
            <span class="label">盈亏:</span>
            <span class="value font-mono font-semibold" :class="getProfitClass(record.realized_profit)">{{ formatNumber(record.realized_profit) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="action-btn edit" @click="openEditModal(record)">编辑</button>
          <button class="action-btn delete" @click="confirmDelete(record)">删除</button>
        </div>
      </div>
      <div v-if="clearRecords.length === 0" class="empty-state">
        暂无清算数据
      </div>
    </div>

    <!-- Modal for Add/Edit -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑清算记录' : '新增清算记录' }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-row">
              <div class="form-group">
                <label>清算日期</label>
                <input 
                  type="text" 
                  v-model="formData.clear_date" 
                  required 
                  placeholder="格式: 20260119" 
                  :disabled="isEditing"
                />
              </div>
              <div class="form-group">
                <label>策略名称</label>
                <input 
                  type="text" 
                  v-model="formData.strategy_name" 
                  required 
                  placeholder="请输入策略名称" 
                  :disabled="isEditing"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>证券代码</label>
                <input type="text" v-model="formData.security_code" required placeholder="如: 510500.SH" />
              </div>
              <div class="form-group">
                <label>证券名称</label>
                <input type="text" v-model="formData.security_name" required placeholder="请输入证券名称" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>持仓数量</label>
                <input type="number" v-model="formData.hold_qty" required placeholder="请输入数字" />
              </div>
              <div class="form-group">
                <label>收盘价</label>
                <input type="number" step="0.0001" v-model="formData.close_price" required placeholder="请输入价格" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>市值</label>
                <input type="number" step="0.01" v-model="formData.market_value" required placeholder="请输入市值" />
              </div>
              <div class="form-group">
                <label>总成本</label>
                <input type="number" step="0.01" v-model="formData.total_cost" required placeholder="请输入成本" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>已实现盈亏</label>
                <input type="number" step="0.01" v-model="formData.realized_profit" required placeholder="请输入盈亏" />
              </div>
              <div class="form-group">
                <label>策略容量</label>
                <input type="number" v-model="formData.all_money" required placeholder="请输入容量" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn cancel" @click="closeModal">取消</button>
              <button type="submit" class="btn submit">确认{{ isEditing ? '修改' : '添加' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div class="modal-overlay" v-if="showConfirmModal" @click.self="closeConfirmModal">
      <div class="modal-content confirm-modal">
        <div class="modal-header">
          <h3>确认操作</h3>
          <button class="close-btn" @click="closeConfirmModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>{{ confirmMessage }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn cancel" @click="closeConfirmModal">取消</button>
          <button class="btn delete-confirm" @click="executeAction">确认</button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <transition name="toast">
      <div v-if="showToast" class="success-toast">
        <svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from '@/utils/axios';

export default {
  name: 'ManualClear',
  props: {
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      clearRecords: [],
      strategies: [],
      selectedDate: '',
      todayDate: '',
      emptyMessage: '暂无清算数据',
      isMobile: false,
      showModal: false,
      showConfirmModal: false,
      isEditing: false,
      confirmMessage: '',
      actionType: '', // 'delete', 'add', 'update'
      pendingAction: null,
      formData: {
        clear_date: '',
        strategy_name: '',
        security_code: '',
        security_name: '',
        hold_qty: '',
        close_price: '',
        market_value: '',
        total_cost: '',
        realized_profit: '',
        all_money: '',
        id: null
      },
      showToast: false,
      toastMessage: '',
      // Date Picker Data
      showDatePicker: false,
      currentViewDate: new Date(),
      weekDays: ['日', '一', '二', '三', '四', '五', '六'],
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
      startDate.setDate(startDate.getDate() - startDate.getDay()); // Start from Sunday
      
      const days = [];
      const today = new Date();
      today.setHours(0,0,0,0);

      const selectedTime = this.selectedDate ? new Date(this.selectedDate).getTime() : null;

      // Generate 42 days (6 weeks)
      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        date.setHours(0,0,0,0);
        
        const isCurrentMonth = date.getMonth() === month;
        const isToday = date.getTime() === today.getTime();
        
        let isSelected = false;
        if (selectedTime) {
             // Simple timestamp comparison since we set hours to 0
             isSelected = date.getTime() === selectedTime; 
             // Handle timezone offset if selectedDate (string) implies UTC vs Local
             // String 'YYYY-MM-DD' parses as UTC usually in Date(), but standard input writes local?
             // To be safe, compare string representation
        }
        // safer string comparison
        const dateStr = this.formatDateToYYYYMMDD(date, '-');
        isSelected = this.selectedDate === dateStr;

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
    sortedClearRecords() {
      // 对清算记录进行排序
      // 1. 优先显示有证券代码的记录
      // 2. 如果没有证券代码,优先显示已实现盈亏非0的记录
      return [...this.clearRecords].sort((a, b) => {
        const aHasCode = a.security_code && a.security_code.trim() !== '';
        const bHasCode = b.security_code && b.security_code.trim() !== '';
        
        // 如果a有代码,b没有,a排前面
        if (aHasCode && !bHasCode) return -1;
        // 如果b有代码,a没有,b排前面
        if (!aHasCode && bHasCode) return 1;
        
        // 如果都没有代码,比较已实现盈亏
        if (!aHasCode && !bHasCode) {
          const aProfit = parseFloat(a.realized_profit) || 0;
          const bProfit = parseFloat(b.realized_profit) || 0;
          const aHasProfit = aProfit !== 0;
          const bHasProfit = bProfit !== 0;
          
          // 如果a有盈亏,b没有,a排前面
          if (aHasProfit && !bHasProfit) return -1;
          // 如果b有盈亏,a没有,b排前面
          if (!aHasProfit && bHasProfit) return 1;
        }
        
        // 其他情况保持原顺序
        return 0;
      });
    }
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },
    formatNumber(num) {
      if (num === null || num === undefined) return '-';
      return num.toString();
    },
    formatDecimal(num) {
      if (num === null || num === undefined) return '-';
      return parseFloat(num).toFixed(2);
    },
    formatDateCompact(dateStr) {
      if (!dateStr) return '-';
      // Convert 20260119 to 20260119 (no dashes)
      return dateStr;
    },
    formatDateDisplay(dateStr) {
      if (!dateStr) return '-';
      // Convert 20260119 to 2026-01-19
      const year = dateStr.substring(0, 4);
      const month = dateStr.substring(4, 6);
      const day = dateStr.substring(6, 8);
      return `${year}-${month}-${day}`;
    },
    formatDateToYYYYMMDD(date, separator = '') {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${year}${separator}${month}${separator}${d}`;
    },
    toggleDatePicker() {
      this.showDatePicker = !this.showDatePicker;
      if (this.showDatePicker) {
          if (this.selectedDate) {
              this.currentViewDate = new Date(this.selectedDate);
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
      await this.fetchClearData();
    },
    handleClickOutside(e) {
        const picker = this.$el.querySelector('.custom-date-picker');
        if (picker && !picker.contains(e.target)) {
            this.closeDatePicker();
        }
    },
    async fetchClearData() {
      try {
        let url = '/api/daily_clear/list';
        
        // Convert date from YYYY-MM-DD to YYYYMMDD if selected
        if (this.selectedDate) {
          const dateParam = this.selectedDate.replace(/-/g, '');
          url = `/api/daily_clear/list?clear_date=${dateParam}`;
        }
        
        const response = await axios.get(url);
        if (response.data.code === 200) {
          this.clearRecords = response.data.data.daily_clear_list || [];
          
          // Show message if no data for selected date
          if (this.clearRecords.length === 0 && this.selectedDate) {
            this.emptyMessage = `${this.selectedDate} 暂无清算数据`;
          } else if (this.clearRecords.length === 0) {
            this.emptyMessage = '暂无清算数据';
          }
        } else {
          console.error('Failed to fetch clear data:', response.data.msg);
        }
      } catch (error) {
        console.error('Error fetching clear data:', error);
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
    openAddModal() {
      this.isEditing = false;
      this.formData = {
        clear_date: this.formatDateToYYYYMMDD(new Date()),
        strategy_name: '',
        security_code: '',
        security_name: '',
        hold_qty: '',
        close_price: '',
        market_value: '',
        total_cost: '',
        realized_profit: '0.00',
        all_money: ''
      };
      this.showModal = true;
    },
    openEditModal(record) {
      this.isEditing = true;
      this.formData = { ...record };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    confirmDelete(record) {
      this.pendingAction = record;
      this.actionType = 'delete';
      this.confirmMessage = `确定要删除 "${record.security_name}" 的清算记录吗？此操作无法撤销。`;
      this.showConfirmModal = true;
    },
    closeConfirmModal() {
      this.showConfirmModal = false;
      this.pendingAction = null;
    },
    handleSubmit() {
      this.showModal = false;
      this.pendingAction = { ...this.formData };
      this.actionType = this.isEditing ? 'update' : 'add';
      this.confirmMessage = this.isEditing 
        ? `确定要修改 "${this.formData.security_name}" 的清算记录吗？` 
        : `确定要添加 "${this.formData.security_name}" 的清算记录吗？`;
      this.showConfirmModal = true;
    },
    async executeAction() {
      try {
        let response;
        let successMessage = '';
        
        if (this.actionType === 'delete') {
          response = await axios.post('/api/daily_clear/delete', { id: this.pendingAction.id });
          successMessage = '删除成功';
        } else if (this.actionType === 'add') {
          const payload = { ...this.pendingAction };
          delete payload.id;
          delete payload.create_time;
          response = await axios.post('/api/daily_clear/add', payload);
          successMessage = '添加成功';
        } else if (this.actionType === 'update') {
          response = await axios.post('/api/daily_clear/update', this.pendingAction);
          successMessage = '修改成功';
        }

        if (response && response.data.code === 200) {
          await this.fetchClearData();
          this.closeConfirmModal();
          this.showSuccessToast(successMessage);
        } else {
          alert(response.data.msg || '操作失败');
        }
      } catch (error) {
        console.error('Action failed:', error);
        alert('操作发生错误,请稍后重试');
      }
    },
    showSuccessToast(message) {
      this.toastMessage = message;
      this.showToast = true;
      setTimeout(() => {
        this.showToast = false;
      }, 3000);
    },
    getProfitClass(profit) {
      const value = parseFloat(profit) || 0;
      if (value > 0) return 'profit-positive';
      if (value < 0) return 'profit-negative';
      if (value < 0) return 'profit-negative';
      return '';
    },
    getStrategyBadgeClass(strategyName) {
      if (!strategyName) return '';
      if (!this.strategies || this.strategies.length === 0) return 'badge-color-1';
      
      // Get all unique strategy names from the global list and sort them
      const uniqueStrategies = [...new Set(this.strategies.map(s => s.strategy_name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      if (index === -1) return 'badge-color-1';
      
      const colorIndex = (index % 10) + 1;
      return `badge-color-${colorIndex}`;
    }
  },
  mounted() {
    this.checkMobile();
    window.addEventListener('click', this.handleClickOutside);
    window.addEventListener('resize', this.checkMobile);
    
    // Set today's date for date picker max
    const today = new Date();
    this.todayDate = today.toISOString().split('T')[0];
    
    this.fetchClearData();
    this.fetchStrategies();
  },
  beforeUnmount() {
    window.removeEventListener('click', this.handleClickOutside);
    window.removeEventListener('resize', this.checkMobile);
  }
};
</script>

<style scoped>
.manual-clear-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
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
  font-size: 24px;
  color: #1e293b;
  font-weight: 600;
  margin: 0;
}

.strategy-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  line-height: 1.4;
}

/* Badge Colors */
.badge-color-0 { color: #1e40af; background-color: #dbeafe; border: 1px solid #bfdbfe; } /* Blue */
.badge-color-1 { color: #0891b2; background-color: #cffafe; border: 1px solid #a5f3fc; } /* Cyan */
.badge-color-2 { color: #15803d; background-color: #dcfce7; border: 1px solid #bbf7d0; } /* Green */
.badge-color-3 { color: #c2410c; background-color: #ffedd5; border: 1px solid #fed7aa; } /* Orange */
.badge-color-4 { color: #be185d; background-color: #fce7f3; border: 1px solid #fbcfe8; } /* Pink */

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.date-filter {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.date-filter:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

/* Table Styles */
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #f3f4f6;
  width: 100%;
}

.clear-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  table-layout: auto;
}

.clear-table tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.clear-table tbody tr:hover {
  background-color: #f3f4f6;
}

.clear-table th,
.clear-table td {
  padding: 16px 12px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563;
  font-size: 14px;
}

.clear-table th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.actions-cell {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.icon-btn {
  padding: 6px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

.icon-btn.edit {
  color: #409EFF;
  background: #ecf5ff;
}

.icon-btn.edit:hover {
  background: #409EFF;
  color: white;
}

.icon-btn.delete {
  color: #F56C6C;
  background: #fef0f0;
}

.icon-btn.delete:hover {
  background: #F56C6C;
  color: white;
}

/* Profit/Loss Color Styles */
.profit-positive {
  color: #ef4444 !important;
  font-weight: 600;
}

.profit-negative {
  color: #10b981 !important;
  font-weight: 600;
}

/* Custom Date Picker Styles */
.custom-date-picker {
  position: relative;
  min-width: 180px;
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
  padding: 0 4px;
}

.current-month {
  font-weight: 600;
  color: #303133;
}

.nav-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 4px 8px;
  color: #606266;
  font-weight: bold;
}

.nav-btn:hover {
  color: #409EFF;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  color: #606266;
}

.day-cell:hover:not(.disabled) {
  background-color: #f2f6fc;
  color: #409EFF;
}

.day-cell.other-month {
  color: #c0c4cc;
}

.day-cell.today {
  color: #409EFF;
  font-weight: 600;
}

.day-cell.selected {
  background-color: #409EFF !important;
  color: white !important;
}

.day-cell.disabled {
  cursor: not-allowed;
  color: #c0c4cc;
  background-color: #f5f7fa;
}

.form-group input:disabled {
  background-color: #f5f7fa;
  color: #909399;
  cursor: not-allowed;
}

/* Card Styles for Mobile */
.cards-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.clear-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.card-date {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-row .label {
  color: #909399;
}

.info-row .value {
  color: #606266;
}

.card-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 720px;
  padding: 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  animation: modalSlideIn 0.3s ease;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 22px;
  font-weight: 700;
}

.close-btn {
  background: #f5f5f5;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e0e0e0;
  transform: rotate(90deg);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 14px;
  background-color: #f9fafb;
}

.form-group input:focus {
  border-color: #409EFF;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
  outline: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  padding: 12px 28px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn.cancel {
  background: #f4f4f5;
  color: #909399;
}

.btn.submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn.submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn.delete-confirm {
  background: #F56C6C;
  color: white;
}

.empty-cell,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  font-size: 14px;
}

/* Success Toast */
.success-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 28px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 15px;
  z-index: 3000;
  animation: slideDown 0.3s ease;
}

.toast-icon {
  width: 24px;
  height: 24px;
  stroke-width: 3;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.plus-icon {
  display: inline-block;
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='M12 4v16m8-8H4'/%3E%3C/svg%3E");
  background-size: cover;
}

/* Dark Mode */
.manual-clear-container.dark-mode {
  background: #1a1a1a;
}

.dark-mode .page-title {
  color: #e0e0e0;
}

.dark-mode .date-filter {
  background: #2d2d2d;
  border-color: #4c4d4f;
  color: #e0e0e0;
}

.dark-mode .table-container,
.dark-mode .clear-card,
.dark-mode .modal-content {
  background: #2d2d2d;
  color: #e0e0e0;
}

.dark-mode .clear-table tbody tr:nth-child(even) {
  background-color: #262626;
}

.dark-mode .clear-table tbody tr:hover {
  background-color: #333333;
}

.dark-mode .clear-table th,
.dark-mode .clear-table td {
  border-bottom-color: #3d3d3d;
  background-color: #2d2d2d;
  color: #b0b0b0;
}

.dark-mode .clear-table th {
  background-color: #363636;
  color: #fff;
}

.dark-mode .action-btn.edit {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
  border-color: transparent;
}

.dark-mode .action-btn.delete {
  background: rgba(245, 108, 108, 0.2);
  color: #F56C6C;
  border-color: transparent;
}

.dark-mode .card-header {
  border-bottom-color: #3d3d3d;
}

.dark-mode .card-title,
.dark-mode .modal-header h3 {
  color: #e0e0e0;
}

.dark-mode .card-date {
  background: #363636;
  color: #b0b0b0;
}

.dark-mode .info-row .label,
.dark-mode .form-group label {
  color: #a0a0a0;
}

.dark-mode .info-row .value {
  color: #d0d0d0;
}

.dark-mode .form-group input[type="text"],
.dark-mode .form-group input[type="number"] {
  background: #3d3d3d;
  border-color: #555;
  color: #e0e0e0;
}

.dark-mode .btn.cancel {
  background: #4a4a4a;
  color: #b0b0b0;
}

.dark-mode .picker-input {
  background: #2d2d2d;
  border-color: #4c4d4f;
}

.dark-mode .picker-input:hover,
.dark-mode .picker-input.active {
  border-color: #409EFF;
}

.dark-mode .picker-text {
  color: #e0e0e0;
}

.dark-mode .picker-text.placeholder {
  color: #606266;
}

.dark-mode .picker-popup {
  background: #2d2d2d;
  border-color: #4c4d4f;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .current-month,
.dark-mode .nav-btn,
.dark-mode .day-cell {
  color: #e0e0e0;
}

.dark-mode .day-cell:hover:not(.disabled) {
  background-color: #3a3a3a;
}

.dark-mode .day-cell.other-month {
  color: #555;
}

.dark-mode .day-cell.disabled {
  background-color: #333;
  color: #555;
}

.dark-mode .icon-btn.edit {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
}

.dark-mode .icon-btn.delete {
  background: rgba(245, 108, 108, 0.2);
  color: #F56C6C;
}

.dark-mode .form-group input:disabled {
  background-color: #3d3d3d;
  color: #666;
}

.dark-mode .empty-cell,
.dark-mode .empty-state {
  color: #909399;
}

/* Dark mode profit/loss colors */
.dark-mode .profit-positive {
  color: #f87171 !important;
}

.dark-mode .profit-negative {
  color: #34d399 !important;
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
body.dark-mode .badge-color-1 { background-color: #1e3a8a; color: #93c5fd; }
body.dark-mode .badge-color-2 { background-color: #164e63; color: #67e8f9; }
body.dark-mode .badge-color-3 { background-color: #14532d; color: #86efac; }
body.dark-mode .badge-color-4 { background-color: #7c2d12; color: #fdba74; }
body.dark-mode .badge-color-5 { background-color: #831843; color: #f9a8d4; }
body.dark-mode .badge-color-6 { background-color: #7f1d1d; color: #fca5a5; }
body.dark-mode .badge-color-7 { background-color: #713f12; color: #fde047; }
body.dark-mode .badge-color-8 { background-color: #115e59; color: #5eead4; }
body.dark-mode .badge-color-9 { background-color: #365314; color: #bef264; }
body.dark-mode .badge-color-10 { background-color: #334155; color: #cbd5e1; }
</style>
