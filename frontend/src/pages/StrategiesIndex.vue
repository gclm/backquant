<template>
  <div class="strategies-page">
    <header class="page-header">
      <div class="page-title">
        <h2>策略管理</h2>
        <span class="page-sub">集中管理策略，编辑后可发起回测任务。</span>
      </div>

      <div class="header-actions">
        <div class="search-wrap">
          <input
            v-model.trim="keyword"
            class="text-input"
            type="text"
            placeholder="搜索策略名"
          >
        </div>

        <button class="btn btn-secondary" :disabled="loading" @click="fetchList(false)">
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button class="btn btn-danger" type="button" :disabled="!selectedIds.length || !!deletingId" @click="handleBatchDelete">
          {{ deletingId === '__batch__' ? '删除中...' : `批量删除（${selectedIds.length}）` }}
        </button>
        <button class="btn btn-primary" @click="handleCreateStrategy">
          新建策略
        </button>
      </div>
    </header>

    <section class="content-card">
      <div class="card-header">
        <div class="card-title">
          <h3>策略列表</h3>
          <div class="table-actions">
            <span class="meta">{{ filteredRows.length }} 条</span>
            <span v-if="selectedIds.length" class="meta">已选 {{ selectedIds.length }} 条</span>
          </div>
        </div>
      </div>

      <div class="card-body">
        <div v-if="errorMessage" class="inline-error">
          {{ errorMessage }}
        </div>

        <div class="table-scroll">
          <table class="table">
            <thead>
              <tr>
                <th class="check-col" style="width: 6%">
                  <input
                    class="row-checkbox"
                    type="checkbox"
                    :checked="isAllPageSelected"
                    :indeterminate.prop="isPageSelectionIndeterminate"
                    :disabled="!pageSelectableRows.length || !!deletingId"
                    title="全选当前页可删除策略"
                    @change="toggleSelectAllOnPage($event)"
                  >
                </th>
                <th style="width: 24%">名称</th>
                <th style="width: 18%">创建时间</th>
                <th style="width: 18%">最后修改</th>
                <th style="width: 34%">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!pagedRows.length">
                <td colspan="5" class="empty-cell">
                  {{ loading ? '加载中...' : '暂无策略（可点击“新建策略”）' }}
                </td>
              </tr>
              <tr
                v-for="row in pagedRows"
                :key="row.id"
                class="data-row"
                :class="{ 'is-selected': isRowSelected(row.id) }"
                @click="handleRowClick(row.id)"
              >
                <td class="row-select-cell" @click.stop>
                  <input
                    class="row-checkbox"
                    type="checkbox"
                    :checked="isRowSelected(row.id)"
                    :disabled="!isStrategyDeletable(row) || !!deletingId"
                    :title="getDeleteDisabledReason(row) || '选择策略'"
                    @change="toggleRowSelection(row.id, $event.target.checked)"
                  >
                </td>
                <td class="mono">
                  <button class="link-btn" type="button" @click.stop="goEdit(row.id)">
                    {{ row.id }}
                  </button>
                </td>
                <td>{{ formatMetaDate(row.created_at) }}</td>
                <td>{{ formatMetaDate(row.updated_at || row.created_at) }}</td>
                <td class="row-actions" @click.stop>
                  <button class="btn btn-mini btn-secondary" type="button" @click.stop="goEdit(row.id)">编辑</button>
                  <button
                    class="btn btn-mini btn-danger"
                    type="button"
                    :disabled="!!deletingId"
                    :title="getDeleteDisabledReason(row) || '删除策略'"
                    :class="{ 'is-locked': !isStrategyDeletable(row) }"
                    @click.stop="handleDelete(row.id)"
                  >
                    {{ deletingId === row.id ? '删除中...' : '删除' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pager">
          <button class="btn btn-secondary" :disabled="currentPage <= 1" @click="currentPage -= 1">上一页</button>
          <div class="pager-meta">
            第 {{ currentPage }} / {{ totalPages }} 页
            <span class="pager-split">·</span>
            每页 {{ pageSize }} 条
          </div>
          <button class="btn btn-secondary" :disabled="currentPage >= totalPages" @click="currentPage += 1">下一页</button>
        </div>
      </div>
    </section>

    <transition name="toast">
      <div v-if="showToast" class="toast" :class="toastType">
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <div v-if="showCreateModal" class="dialog-overlay" @click.self="closeCreateModal">
      <div class="dialog">
        <div class="dialog-header">
          <h3>新建策略</h3>
          <button class="dialog-close" type="button" @click="closeCreateModal">×</button>
        </div>
        <div class="dialog-body">
          <label for="strategy-id-input" class="dialog-label">策略名称</label>
          <input
            id="strategy-id-input"
            v-model.trim="createDraftId"
            class="text-input"
            type="text"
            :placeholder="createSuggestedId"
            @keyup.enter="confirmCreate"
          >
          <div class="dialog-tip">支持中文、字母、数字、下划线和中横线，且不能包含空格。</div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" type="button" @click="closeCreateModal">取消</button>
          <button class="btn btn-primary" type="button" @click="confirmCreate">确定</button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="dialog-overlay" @click.self="closeDeleteModal">
      <div class="dialog danger">
        <div class="dialog-header">
          <h3>删除确认</h3>
          <button class="dialog-close" type="button" @click="closeDeleteModal">×</button>
        </div>
        <div class="dialog-body">
          <p v-if="pendingDeleteIds.length === 1">
            确认删除策略 <span class="mono">「{{ pendingDeleteIds[0] }}」</span> 吗？删除后无法恢复。
          </p>
          <p v-else>
            确认删除已选中的 {{ pendingDeleteIds.length }} 个策略吗？删除后无法恢复。
          </p>
          <p v-if="pendingDeleteIds.length > 1" class="delete-list mono">
            {{ pendingDeleteIds.join('、') }}
          </p>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" type="button" @click="closeDeleteModal">取消</button>
          <button class="btn btn-danger" type="button" :disabled="!!deletingId" @click="confirmDelete">
            {{ deletingId ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { listStrategies } from '@/api/backtest';
import { mergeLocalStrategyIds, removeLocalStrategyId } from '@/utils/backtestStrategies';
import { normalizeStrategyList } from '@/utils/strategyNormalize';
import { getStrategyRenameMap, resolveCurrentStrategyId, syncStrategyRenameMap } from '@/utils/strategyRenameMap';
import { deleteStrategyCascade } from '@/utils/strategyDeletion';

function getStrategyMetaTimestamp(item) {
  const raw = item?.updated_at || item?.created_at || '';
  const ts = new Date(raw).getTime();
  return Number.isFinite(ts) ? ts : 0;
}

export default {
  name: 'StrategiesIndex',
  data() {
    return {
      loading: false,
      errorMessage: '',
      keyword: '',
      rows: [],
      selectedIds: [],
      currentPage: 1,
      pageSize: 10,
      deletingId: '',
      showCreateModal: false,
      createDraftId: '',
      createSuggestedId: '',
      showDeleteModal: false,
      pendingDeleteIds: [],
      showToast: false,
      toastType: 'success',
      toastMessage: '',
      toastTimer: null
    };
  },
  computed: {
    filteredRows() {
      const keyword = (this.keyword || '').trim().toLowerCase();
      if (!keyword) {
        return this.rows;
      }
      return this.rows.filter((row) => String(row.id).toLowerCase().includes(keyword));
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredRows.length / this.pageSize));
    },
    pagedRows() {
      const page = Math.min(this.currentPage, this.totalPages);
      const start = (Math.max(1, page) - 1) * this.pageSize;
      return this.filteredRows.slice(start, start + this.pageSize);
    },
    pageSelectableRows() {
      return this.pagedRows.filter((row) => this.isStrategyDeletable(row));
    },
    isAllPageSelected() {
      if (!this.pageSelectableRows.length) {
        return false;
      }
      const selectedSet = new Set(this.selectedIds);
      return this.pageSelectableRows.every((row) => selectedSet.has(row.id));
    },
    isPageSelectionIndeterminate() {
      if (!this.pageSelectableRows.length) {
        return false;
      }
      const selectedSet = new Set(this.selectedIds);
      const selectedCount = this.pageSelectableRows.filter((row) => selectedSet.has(row.id)).length;
      return selectedCount > 0 && selectedCount < this.pageSelectableRows.length;
    }
  },
  watch: {
    keyword() {
      this.currentPage = 1;
    },
    filteredRows() {
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages;
      }
    },
    rows(nextRows) {
      const idSet = new Set((nextRows || []).map((row) => String(row?.id || '').trim()).filter(Boolean));
      this.selectedIds = this.selectedIds.filter((id) => idSet.has(id));
    }
  },
  methods: {
    showMessage(message, type = 'success') {
      this.toastType = type;
      this.toastMessage = message;
      this.showToast = true;
      if (this.toastTimer) {
        clearTimeout(this.toastTimer);
      }
      this.toastTimer = setTimeout(() => {
        this.showToast = false;
      }, 2200);
    },
    getErrorMessage(error, fallback) {
      if (error && error.response && error.response.data) {
        const data = error.response.data;
        if (typeof data === 'string') {
          return data;
        }
        if (data.message) {
          return data.message;
        }
        if (data.error && typeof data.error === 'string') {
          return data.error;
        }
        if (data.error && typeof data.error === 'object' && data.error.message) {
          return data.error.message;
        }
        return fallback;
      }
      return (error && error.message) || fallback;
    },
    formatMetaDate(value) {
      if (!value) {
        return '-';
      }
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return String(value);
      }
      return date.toLocaleString('zh-CN');
    },
    normalizeCanonicalStrategyRows(rows = [], renameMap = null) {
      const map = renameMap && typeof renameMap === 'object' ? renameMap : getStrategyRenameMap();
      const dedup = new Map();

      (rows || []).forEach((item) => {
        const rawId = String(item?.id || '').trim();
        if (!rawId) {
          return;
        }
        const canonicalId = resolveCurrentStrategyId(rawId, map) || rawId;
        const nextItem = {
          ...(item || {}),
          id: canonicalId
        };

        const previous = dedup.get(canonicalId);
        if (!previous) {
          dedup.set(canonicalId, nextItem);
          return;
        }

        if (getStrategyMetaTimestamp(nextItem) >= getStrategyMetaTimestamp(previous)) {
          dedup.set(canonicalId, { ...previous, ...nextItem, id: canonicalId });
        }
      });

      return Array.from(dedup.values());
    },
    goEdit(id) {
      this.$router.push({ name: 'strategy-edit', params: { id: String(id) } });
    },
    handleRowClick(id) {
      this.goEdit(id);
    },
    isRowSelected(id) {
      const target = String(id || '').trim();
      return !!target && this.selectedIds.includes(target);
    },
    toggleRowSelection(id, checked) {
      const target = String(id || '').trim();
      if (!target) {
        return;
      }
      if (checked) {
        if (!this.selectedIds.includes(target)) {
          this.selectedIds = [...this.selectedIds, target];
        }
        return;
      }
      this.selectedIds = this.selectedIds.filter((item) => item !== target);
    },
    toggleSelectAllOnPage(event) {
      const checked = Boolean(event && event.target && event.target.checked);
      const pageIds = this.pageSelectableRows.map((row) => String(row.id || '').trim()).filter(Boolean);
      if (!pageIds.length) {
        return;
      }
      if (checked) {
        this.selectedIds = Array.from(new Set([...this.selectedIds, ...pageIds]));
        return;
      }
      const pageSet = new Set(pageIds);
      this.selectedIds = this.selectedIds.filter((id) => !pageSet.has(id));
    },
    isStrategyDeletable(row) {
      const target = row || {};
      const strategyId = String(target.id || '').trim();
      if (!strategyId) {
        return false;
      }
      if (strategyId === 'demo') {
        return false;
      }
      if (target.read_only) {
        return false;
      }
      if (target.is_builtin) {
        return false;
      }
      if (target.can_delete === false) {
        return false;
      }
      return true;
    },
    getDeleteDisabledReason(row) {
      const target = row || {};
      const strategyId = String(target.id || '').trim();
      if (!strategyId) {
        return '策略 ID 缺失，无法删除';
      }
      if (strategyId === 'demo') {
        return 'demo 为内置示例策略，不支持删除';
      }
      if (target.read_only) {
        return '只读策略不支持删除';
      }
      if (target.is_builtin) {
        return '系统内置策略不支持删除';
      }
      if (target.can_delete === false) {
        return '后端标记该策略不可删除';
      }
      return '';
    },
    handleBatchDelete() {
      if (!this.selectedIds.length) {
        this.showMessage('请先勾选要删除的策略', 'error');
        return;
      }
      const selectedSet = new Set(this.selectedIds);
      const selectedRows = this.rows.filter((row) => selectedSet.has(String(row?.id || '').trim()));
      if (!selectedRows.length) {
        this.showMessage('未找到可删除的已选策略', 'error');
        return;
      }
      const blocked = selectedRows.find((row) => !this.isStrategyDeletable(row));
      if (blocked) {
        this.showMessage(this.getDeleteDisabledReason(blocked), 'error');
        return;
      }
      this.pendingDeleteIds = selectedRows.map((row) => String(row.id).trim());
      this.showDeleteModal = true;
    },
    handleCreateStrategy() {
      this.createSuggestedId = `strategy_${Date.now()}`;
      this.createDraftId = this.createSuggestedId;
      this.showCreateModal = true;
    },
    closeCreateModal() {
      this.showCreateModal = false;
      this.createDraftId = '';
      this.createSuggestedId = '';
    },
    confirmCreate() {
      const id = String(this.createDraftId || '').trim();
      if (!id) {
        this.showMessage('策略 ID 不能为空', 'error');
        return;
      }
      if (/\s/.test(id)) {
        this.showMessage('策略 ID 不能包含空白字符', 'error');
        return;
      }
      if (!/^[A-Za-z0-9_\-\u4E00-\u9FFF]+$/.test(id)) {
        this.showMessage('策略 ID 仅支持中文、字母、数字、下划线和中横线', 'error');
        return;
      }

      this.closeCreateModal();
      this.goEdit(id);
    },
    handleDelete(id) {
      const strategyId = String(id || '').trim();
      if (!strategyId) {
        return;
      }
      const row = this.rows.find((item) => item.id === strategyId);
      const reason = this.getDeleteDisabledReason(row || { id: strategyId });
      if (reason) {
        this.showMessage(reason, 'error');
        return;
      }
      this.pendingDeleteIds = [strategyId];
      this.showDeleteModal = true;
    },
    closeDeleteModal() {
      if (this.deletingId) {
        return;
      }
      this.showDeleteModal = false;
      this.pendingDeleteIds = [];
    },
    async confirmDelete() {
      const targetIds = Array.from(
        new Set((this.pendingDeleteIds || []).map((id) => String(id || '').trim()).filter(Boolean))
      );
      if (!targetIds.length) {
        return;
      }

      this.deletingId = targetIds.length > 1 ? '__batch__' : targetIds[0];
      let deletedCount = 0;
      let deletedJobs = 0;
      const failures = [];
      try {
        for (let i = 0; i < targetIds.length; i += 1) {
          const strategyId = targetIds[i];
          try {
            const result = await deleteStrategyCascade(strategyId);
            const deletedId = String(result?.strategyId || strategyId).trim();
            this.rows = this.rows.filter((row) => row.id !== deletedId);
            removeLocalStrategyId(strategyId);
            if (deletedId && deletedId !== strategyId) {
              removeLocalStrategyId(deletedId);
            }
            this.selectedIds = this.selectedIds.filter((id) => id !== strategyId && id !== deletedId);
            deletedJobs += Number(result?.deletedJobs || 0);
            deletedCount += 1;
          } catch (error) {
            failures.push({
              id: strategyId,
              message: this.getErrorMessage(error, '策略删除失败')
            });
          }
        }

        if (!failures.length) {
          if (targetIds.length === 1) {
            this.showMessage(`策略删除成功（同时删除 ${deletedJobs} 条历史任务）`);
          } else {
            this.showMessage(`批量删除成功（策略 ${deletedCount} 条，历史任务 ${deletedJobs} 条）`);
          }
          return;
        }

        if (deletedCount > 0) {
          this.showMessage(`已删除 ${deletedCount} 条，失败 ${failures.length} 条：${failures[0].message}`, 'error');
          return;
        }

        this.showMessage(failures[0].message || '策略删除失败', 'error');
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '策略删除失败'), 'error');
      } finally {
        this.showDeleteModal = false;
        this.pendingDeleteIds = [];
        this.deletingId = '';
      }
    },
    async fetchList(silent = true) {
      this.loading = true;
      this.errorMessage = '';
      try {
        await syncStrategyRenameMap();
        const renameMap = getStrategyRenameMap();
        // 这里优先走后端列表接口；若后端未来支持分页，可在 params 中透传 page/page_size。
        const data = await listStrategies();
        const list = this.normalizeCanonicalStrategyRows(normalizeStrategyList(data), renameMap);
        const sorted = [...list].sort((a, b) => String(a.id).localeCompare(String(b.id)));
        this.rows = sorted;
        mergeLocalStrategyIds(sorted.map((item) => item.id));
      } catch (error) {
        if (!silent) {
          this.errorMessage = this.getErrorMessage(error, '获取策略列表失败');
        }
      } finally {
        this.loading = false;
      }
    }
  },
  async mounted() {
    await this.fetchList(true);
  },
  beforeUnmount() {
    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }
  }
};
</script>

<style scoped>
.strategies-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(223, 231, 242, 0.7);
}

.page-title h2 {
  margin: 0;
  font-size: 22px;
}

.page-sub {
  display: inline-block;
  margin-top: 6px;
  color: #5f6f86;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
}

.search-wrap {
  min-width: 260px;
}

.text-input {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
  color: #303133;
  background: #fff;
}

.text-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.12);
}

.content-card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-header {
  padding: 10px 14px;
  border-bottom: 1px solid #ebeef5;
  background: #f6faff;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.table-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.card-title h3 {
  margin: 0;
  font-size: 16px;
}

.meta {
  font-size: 12px;
  color: #5f6f86;
}

.hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5f6f86;
  font-size: 12px;
}

.hint-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #60a5fa;
}

.card-body {
  padding: 12px;
}

.inline-error {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 10px 12px;
  border-radius: 10px;
  margin-bottom: 12px;
}

.table-scroll {
  overflow: auto;
  border: 1px solid #eef2f7;
  border-radius: 10px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  min-width: 840px;
}

.table th,
.table td {
  padding: 8px 10px;
  border-bottom: 1px solid #eef2f7;
  text-align: left;
  font-size: 12px;
  color: #303133;
}

.table thead th {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.check-col {
  text-align: center;
}

.row-select-cell {
  text-align: center;
}

.row-checkbox {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.data-row {
  cursor: pointer;
  transition: background-color 0.18s ease;
}

.data-row:hover {
  background: #f8fbff;
}

.data-row.is-selected {
  background: #eef6ff;
}

.data-row.is-selected:hover {
  background: #e4f0ff;
}

.empty-cell {
  text-align: center;
  color: #64748b;
  padding: 16px 10px;
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 180px;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
}

.tag {
  display: inline-flex;
  align-items: center;
  border: 1px solid #d9ecff;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 999px;
  padding: 2px 9px;
  font-size: 12px;
  font-weight: 600;
}

.btn {
  border: 1px solid #d0dae7;
  background: #fff;
  color: #334155;
  padding: 7px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
}

.btn:hover:not(:disabled) {
  border-color: #9bb0c9;
}

.btn:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.btn-primary {
  background: #1f6feb;
  color: #fff;
  border-color: #1f6feb;
}

.btn-primary:hover:not(:disabled) {
  background: #1a62d1;
  border-color: #1a62d1;
}

.btn-danger {
  color: #b91c1c;
  border-color: #fecaca;
  background: #fff5f5;
}

.btn-danger:hover:not(:disabled) {
  color: #991b1b;
  border-color: #fca5a5;
  background: #ffe4e6;
}

.btn-danger.is-locked {
  opacity: 0.7;
}

.btn-secondary {
  background: #ffffff;
}

.btn-mini {
  padding: 4px 8px;
  font-size: 12px;
}

.link-btn {
  border: none;
  padding: 0;
  background: transparent;
  color: #1f6feb;
  font-weight: 700;
  cursor: pointer;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
}

.pager-meta {
  font-size: 12px;
  color: #64748b;
}

.pager-split {
  margin: 0 6px;
}

.toast {
  position: fixed;
  right: 16px;
  bottom: 18px;
  padding: 10px 12px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  font-size: 13px;
  z-index: 9999;
  background: #0f172a;
  color: #fff;
}

.toast.error {
  background: #991b1b;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  transform: translateY(6px);
  opacity: 0;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 10010;
  background: rgba(15, 23, 42, 0.46);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.dialog {
  width: min(520px, 100%);
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 18px 54px rgba(15, 23, 42, 0.25);
  overflow: hidden;
}

.dialog.danger {
  max-width: 460px;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
}

.dialog-close {
  border: 1px solid #cbd5e1;
  background: #fff;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  color: #334155;
}

.dialog-body {
  padding: 14px;
  color: #334155;
  font-size: 13px;
}

.delete-list {
  margin-top: 8px;
  color: #475569;
  line-height: 1.5;
  word-break: break-all;
}

.dialog-label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: #475569;
  font-weight: 700;
}

.dialog-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
}

@media (max-width: 720px) {
  .page-header {
    flex-direction: column;
  }
  .search-wrap {
    width: 100%;
    min-width: 0;
  }
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
