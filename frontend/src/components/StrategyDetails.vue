<template>
  <div class="strategy-details-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="page-header">
      <h2 class="page-title">策略管理</h2>
      <button class="add-btn" @click="openAddModal">
        <i class="plus-icon"></i> 新增策略
      </button>
    </div>

    <!-- Desktop Table View -->
    <div class="table-container" v-if="!isMobile">
      <table class="strategy-table">
        <thead>
          <tr>
            <th class="w-16">序号</th>
            <th>策略名称</th>
            <th>策略容量</th>
            <th>策略容量(实时)</th>
            <th>策略描述</th>
            <th style="text-align: center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(strategy, index) in sortedStrategies" :key="strategy.strategy_id">
            <td class="index-cell">{{ index + 1 }}</td>
            <td class="name-cell">
              <span class="strategy-badge" :class="getStrategyBadgeClass(strategy.strategy_name)">{{ strategy.strategy_name }}</span>
            </td>
            <td class="size-cell font-mono font-semibold">{{ formatNumber(strategy.strategy_size) }}</td>
            <td class="size-cell font-mono font-semibold">{{ formatDecimalNumber(strategy.strategy_size_new) }}</td>
            <td class="desc-cell" :title="strategy.description">{{ strategy.description }}</td>
            <td class="actions-cell">
              <button class="icon-btn edit" @click="openEditModal(strategy)" title="编辑">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button class="icon-btn delete" @click="confirmDelete(strategy)" title="删除">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="strategies.length === 0">
            <td colspan="6" class="empty-cell">暂无策略数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="cards-container" v-else>
      <div class="strategy-card" v-for="strategy in sortedStrategies" :key="strategy.strategy_id">
        <div class="card-header">
          <span class="strategy-badge" :class="getStrategyBadgeClass(strategy.strategy_name)">{{ strategy.strategy_name }}</span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">容量:</span>
            <span class="value font-mono font-semibold">{{ formatNumber(strategy.strategy_size) }}</span>
          </div>
          <div class="info-row">
            <span class="label">容量(实时):</span>
            <span class="value font-mono font-semibold">{{ formatDecimalNumber(strategy.strategy_size_new) }}</span>
          </div>
          <div class="info-row desc-row">
            <span class="label">描述:</span>
            <span class="value">{{ strategy.description }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="icon-btn edit" @click="openEditModal(strategy)" title="编辑">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
          </button>
          <button class="icon-btn delete" @click="confirmDelete(strategy)" title="删除">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </div>
      <div v-if="strategies.length === 0" class="empty-state">
        暂无策略数据
      </div>
    </div>

    <!-- Modal for Add/Edit -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑策略' : '新增策略' }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>策略名称</label>
              <input type="text" v-model="formData.strategy_name" required placeholder="请输入策略名称" />
            </div>
            <div class="form-group">
              <label>策略描述</label>
              <textarea v-model="formData.description" required placeholder="请输入策略描述"></textarea>
            </div>
            <div class="form-group">
              <label>策略容量</label>
              <input type="number" v-model="formData.strategy_size" required placeholder="请输入数字" />
            </div>
            <div class="form-group">
              <label>策略容量(实时)</label>
              <input type="number" v-model="formData.strategy_size_new" step="0.0001" required placeholder="请输入数字(可保留4位小数)" />
            </div>
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.is_online" :true-value="'1'" :false-value="'0'" />
                是否上线
              </label>
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
  name: 'StrategyDetails',
  props: {
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      strategies: [],
      isMobile: false,
      showModal: false,
      showConfirmModal: false,
      isEditing: false,
      confirmMessage: '',
      actionType: '', // 'delete', 'add', 'update'
      pendingAction: null,
      formData: {
        strategy_name: '',
        description: '',
        strategy_size: '',
        strategy_size_new: '',
        is_online: '0',
        strategy_id: null
      },
      showToast: false,
      toastMessage: ''
    };
  },
  computed: {
    sortedStrategies() {
      // Sort by strategy_id ascending
      return [...this.strategies].sort((a, b) => a.strategy_id - b.strategy_id);
    }
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },
    formatDate(dateStr) {
      if (!dateStr) return '-';
      const date = new Date(dateStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    formatNumber(num) {
        if (num === null || num === undefined) return '-';
        return num.toString();
    },
    formatDecimalNumber(num) {
        if (num === null || num === undefined) return '-';
        return Number(num).toFixed(4);
    },
    async fetchStrategies() {
      try {
        const response = await axios.get('/api/strategy/list');
        if (response.data.code === 200) {
          this.strategies = response.data.data.strategy_list || [];
        } else {
          console.error('Failed to fetch strategies:', response.data.msg);
        }
      } catch (error) {
        console.error('Error fetching strategies:', error);
      }
    },
    openAddModal() {
      this.isEditing = false;
      this.formData = {
        strategy_name: '',
        description: '',
        strategy_size: '',
        strategy_size_new: '',
        is_online: '1' // Default check
      };
      this.showModal = true;
    },
    openEditModal(strategy) {
      this.isEditing = true;
      this.formData = { ...strategy };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    confirmDelete(strategy) {
      this.pendingAction = strategy;
      this.actionType = 'delete';
      this.confirmMessage = `确定要删除策略 "${strategy.strategy_name}" 吗？此操作无法撤销。`;
      this.showConfirmModal = true;
    },
    closeConfirmModal() {
      this.showConfirmModal = false;
      this.pendingAction = null;
    },
    handleSubmit() {
       // Close edit modal first, then show confirmation modal
       this.showModal = false;
       this.pendingAction = { ...this.formData };
       this.actionType = this.isEditing ? 'update' : 'add';
       this.confirmMessage = this.isEditing 
          ? `确定要修改策略 "${this.formData.strategy_name}" 吗？` 
          : `确定要添加新策略 "${this.formData.strategy_name}" 吗？`;
       this.showConfirmModal = true;
    },
    async executeAction() {
      try {
        let response;
        let successMessage = '';
        
        if (this.actionType === 'delete') {
            response = await axios.post('/api/strategy/delete', { strategy_id: this.pendingAction.strategy_id });
            successMessage = '删除成功';
        } else if (this.actionType === 'add') {
            const payload = { ...this.pendingAction };
            delete payload.strategy_id; // Added strategies don't have ID yet
            response = await axios.post('/api/strategy/add', payload);
            successMessage = '添加成功';
        } else if (this.actionType === 'update') {
            response = await axios.post('/api/strategy/update', this.pendingAction);
            successMessage = '修改成功';
        }

        if (response && response.data.code === 200) {
            // Refresh list
            await this.fetchStrategies();
            this.closeConfirmModal();
            // Show success toast
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
    getStrategyBadgeClass(strategyName) {
      // Get all unique strategy names from the list and sort them to ensure deterministic order
      const uniqueStrategies = [...new Set(this.strategies.map(s => s.strategy_name))].sort();
      const index = uniqueStrategies.indexOf(strategyName);
      
      // If strategy not found (shouldn't happen) or list empty, return first color
      if (index === -1) return 'badge-color-1';
      
      // Cycle through 10 distinct colors
      const colorIndex = (index % 10) + 1;
      return `badge-color-${colorIndex}`;
    }
  },
  mounted() {
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
    this.fetchStrategies();
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobile);
  }
};
</script>

<style scoped>
.strategy-details-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  font-weight: 600;
  margin: 0;
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
  overflow-x: auto;
  border: 1px solid #f3f4f6;
}

.strategy-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

/* Zebra Striping */
.strategy-table tbody tr:nth-child(even) {
  background-color: #f9fafb; /* gray-50 */
}

.strategy-table tbody tr:hover {
  background-color: #f3f4f6; /* gray-100 */
}

.strategy-table th,
.strategy-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
  color: #4b5563; /* slate-600 */
  white-space: nowrap;
  font-size: 14px;
}

.strategy-table th {
  background-color: #f8fafc; /* slate-50 */
  color: #64748b; /* slate-500 */
  font-weight: 600;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.desc-cell {
  max-width: 250px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions-cell,
.card-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.card-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  justify-content: flex-end;
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

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.online {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-badge.offline {
  background-color: #f4f4f5;
  color: #909399;
}

/* Card Styles for Mobile */
.cards-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.strategy-card {
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

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-row.desc-row {
  flex-direction: column;
  gap: 4px;
}

.info-row .label {
  color: #909399;
}

.info-row .value {
  color: #606266;
}

/* Original .card-actions block removed as it's now defined above */

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
  max-width: 520px;
  padding: 36px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  animation: modalSlideIn 0.3s ease;
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
  margin-bottom: 20px;
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

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 8px;
  transition: all 0.2s;
  font-size: 14px;
  background-color: #f9fafb; /* gray-50 */
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #409EFF;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
  outline: none;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #409EFF;
  outline: none;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
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

/* Strategy Badge Styles */
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

/* Dark Mode */
.strategy-details-container.dark-mode {
  background: #1a1a1a;
}

.dark-mode .page-title,
.dark-mode .strategy-table th {
  color: #e0e0e0;
}

.dark-mode .table-container,
.dark-mode .strategy-card,
.dark-mode .modal-content {
  background: #2d2d2d;
  color: #e0e0e0;
}

.dark-mode .strategy-table tbody tr:nth-child(even) {
  background-color: #262626; /* darker row */
}

.dark-mode .strategy-table tbody tr:hover {
  background-color: #333333;
}

.dark-mode .strategy-table th,
.dark-mode .strategy-table td {
  border-bottom-color: #3d3d3d;
  background-color: #2d2d2d;
  color: #b0b0b0;
}

.dark-mode .strategy-table th {
    background-color: #363636;
    color: #fff;
}

/* Original .dark-mode .action-btn.edit and .dark-mode .action-btn.delete blocks removed */

.dark-mode .icon-btn.edit {
  background: rgba(64, 158, 255, 0.2);
  color: #409EFF;
}

.dark-mode .icon-btn.delete {
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

.dark-mode .info-row .label,
.dark-mode .form-group label {
  color: #a0a0a0;
}

.dark-mode .info-row .value {
  color: #d0d0d0;
}

.dark-mode .form-group input[type="text"],
.dark-mode .form-group input[type="number"],
.dark-mode .form-group textarea {
  background: #3d3d3d;
  border-color: #555;
  color: #e0e0e0;
}

.dark-mode .btn.cancel {
  background: #4a4a4a;
  color: #b0b0b0;
}

.dark-mode .empty-cell,
.dark-mode .empty-state {
  color: #909399;
    text-align: center;
    padding: 20px;
}

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

.plus-icon {
  /* Simple CSS plus icon if needed, or specific SVG */
  display: inline-block;
  width: 14px;
  height: 14px;
   background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='M12 4v16m8-8H4'/%3E%3C/svg%3E");
    background-size: cover;
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
</style>
