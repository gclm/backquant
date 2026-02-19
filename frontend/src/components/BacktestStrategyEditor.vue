<template>
  <div class="strategy-editor-page">
    <div class="page-header">
      <div class="page-title-row">
        <h2>策略编辑</h2>
        <span class="page-tag">Python</span>
      </div>
      <p>支持 Python 语法高亮，保存后可直接在本地回测中选择策略运行。</p>
      <div class="quick-chip-row">
        <span class="quick-chip">快速加载</span>
        <span class="quick-chip">安全保存</span>
        <span class="quick-chip">一键回测</span>
      </div>
    </div>

    <section class="content-card">
      <div class="card-header">
        <h3>策略信息</h3>
      </div>

      <div class="card-body">
        <div class="form-grid">
          <div class="form-row">
            <label for="strategy-select">选择已有策略</label>
            <select id="strategy-select" v-model="selectedStrategyId" class="text-input" data-testid="strategy-select" @change="handleSelectChange">
              <option v-for="id in filteredStrategyOptions" :key="`option-${id}`" :value="id">{{ id }}</option>
            </select>
            <p v-if="strategyKeyword && !filteredStrategyOptions.length" class="meta-sub-text">没有匹配策略，请调整关键词。</p>
          </div>

          <div class="form-row">
            <label for="strategy-search">筛选关键词</label>
            <input
              id="strategy-search"
              v-model.trim="strategyKeyword"
              type="text"
              class="text-input"
              placeholder="输入关键词过滤策略列表"
            >
          </div>

          <div class="form-row">
            <label for="strategy-id">当前编辑策略 ID</label>
            <input id="strategy-id" v-model.trim="strategyId" type="text" class="text-input" placeholder="例如：demo">
          </div>
        </div>

        <div class="actions-row">
          <div class="actions-group">
            <button class="btn btn-secondary" :disabled="loadingList" @click="fetchStrategyList">
              {{ loadingList ? '刷新中...' : '刷新策略列表' }}
            </button>
            <button class="btn btn-secondary" :disabled="loadingStrategy" @click="handleLoadStrategy">
              {{ loadingStrategy ? '加载中...' : '加载策略' }}
            </button>
          </div>

          <div class="actions-group">
            <button class="btn btn-secondary" @click="handleCreateStrategy">新增策略</button>
            <button class="btn btn-primary" :disabled="savingStrategy" data-testid="save-btn" @click="handleSaveStrategy">
              {{ savingStrategy ? '保存中...' : (isExistingStrategy ? '更新策略' : '创建策略') }}
            </button>
            <button class="btn btn-danger" :disabled="!canDeleteStrategy" data-testid="delete-btn" @click="handleDeleteStrategy()">
              {{ deletingStrategy ? '删除中...' : '删除策略' }}
            </button>
            <button class="btn btn-secondary" @click="goBacktest">去本地回测</button>
          </div>
        </div>

        <p class="meta-text">当前共 {{ strategyOptions.length }} 个策略可用</p>
        <p v-if="lastLoadedAt" class="meta-sub-text">最近加载时间：{{ lastLoadedAt }}</p>

        <div class="strategy-summary">
          <div class="summary-chip">
            <span>当前策略</span>
            <strong>{{ strategyId || '-' }}</strong>
          </div>
          <div class="summary-chip">
            <span>代码长度</span>
            <strong>{{ formatCodeSize(currentStrategyMeta.size) }}</strong>
          </div>
          <div class="summary-chip">
            <span>创建时间</span>
            <strong>{{ formatMetaDate(currentStrategyMeta.created_at) }}</strong>
          </div>
          <div class="summary-chip">
            <span>更新时间</span>
            <strong>{{ formatMetaDate(currentStrategyMeta.updated_at) }}</strong>
          </div>
        </div>

        <div class="strategy-table-wrap">
          <div class="table-title-row">
            <h4>策略列表（支持增删改查）</h4>
            <span class="meta-sub-text">可在列表中直接加载或删除策略</span>
          </div>
          <div class="table-scroll">
            <table class="strategy-info-table" data-testid="strategy-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>代码长度</th>
                  <th>创建时间</th>
                  <th>更新时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredStrategyRows.length">
                  <td colspan="5" class="empty-cell">暂无策略</td>
                </tr>
                <tr
                  v-for="row in filteredStrategyRows"
                  :key="`row-${row.id}`"
                  :class="{ 'row-active': row.id === strategyId }"
                >
                  <td class="mono">{{ row.id }}</td>
                  <td>{{ formatCodeSize(row.size) }}</td>
                  <td>{{ formatMetaDate(row.created_at) }}</td>
                  <td>{{ formatMetaDate(row.updated_at) }}</td>
                  <td class="table-actions">
                    <button class="btn btn-secondary btn-mini" @click="handleLoadFromRow(row.id)">载入</button>
                    <button class="btn btn-danger btn-mini" :disabled="deletingStrategy || row.id === 'demo'" @click="handleDeleteStrategy(row.id)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <section class="content-card">
      <div class="card-header">
        <h3>Python 代码编辑器</h3>
      </div>
      <div class="card-body">
        <div class="editor-tip">支持 `Tab` 缩进与语法高亮，建议每次修改后先保存再回测。</div>
        <PythonCodeEditor v-model="strategyCode" :min-height="460" />
      </div>
    </section>

    <transition name="toast">
      <div v-if="showToast" class="success-toast" :class="toastType">
        <svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script>
import PythonCodeEditor from '@/components/PythonCodeEditor.vue';
import {
  listStrategies,
  saveStrategy,
  getStrategy,
} from '@/api/backtest';
import {
  getLocalStrategyIds,
  mergeLocalStrategyId,
  mergeLocalStrategyIds,
  removeLocalStrategyId
} from '@/utils/backtestStrategies';
import { getStrategyRenameMap, resolveCurrentStrategyId, syncStrategyRenameMap } from '@/utils/strategyRenameMap';
import { deleteStrategyCascade } from '@/utils/strategyDeletion';

const DEFAULT_TEMPLATE = `# 示例策略\ndef init(context):\n    context.s1 = "000001.XSHE"\n\ndef handle_bar(context, bar_dict):\n    pass\n`;

function unwrapDataPayload(payload) {
  if (!payload || typeof payload !== 'object') {
    return payload;
  }

  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload.data !== undefined && payload.data !== null) {
    return payload.data;
  }

  return payload;
}

function normalizeCodePayload(data) {
  const payload = unwrapDataPayload(data);
  if (!payload) {
    return '';
  }

  if (typeof payload === 'string') {
    return payload;
  }

  if (typeof payload.code === 'string') {
    return payload.code;
  }

  if (payload.strategy && typeof payload.strategy.code === 'string') {
    return payload.strategy.code;
  }

  if (payload.item && typeof payload.item.code === 'string') {
    return payload.item.code;
  }

  return '';
}

function toNumberOrNull(value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function normalizeStrategyMeta(item) {
  if (typeof item === 'string') {
    const id = item.trim();
    return id
      ? {
        id,
        created_at: '',
        updated_at: '',
        size: null
      }
      : null;
  }

  if (!item || typeof item !== 'object') {
    return null;
  }

  const id = String(item.id || item.strategy_id || item.name || '').trim();
  if (!id) {
    return null;
  }

  return {
    id,
    created_at: item.created_at || item.create_time || item.ctime || '',
    updated_at: item.updated_at || item.update_time || item.mtime || '',
    size: toNumberOrNull(item.size ?? item.code_size ?? item.bytes)
  };
}

function normalizeStrategyList(data) {
  const payload = unwrapDataPayload(data);
  if (!payload) {
    return [];
  }

  const source = Array.isArray(payload)
    ? payload
    : (Array.isArray(payload.strategies)
      ? payload.strategies
      : (Array.isArray(payload.items)
        ? payload.items
        : []));

  const dedup = new Map();
  source
    .map(normalizeStrategyMeta)
    .filter(Boolean)
    .forEach((item) => {
      dedup.set(item.id, item);
    });
  return Array.from(dedup.values());
}

function getStrategyMetaTimestamp(item) {
  const raw = item?.updated_at || item?.created_at || '';
  const ts = new Date(raw).getTime();
  return Number.isFinite(ts) ? ts : 0;
}

export default {
  name: 'BacktestStrategyEditor',
  components: {
    PythonCodeEditor
  },
  data() {
    return {
      strategyOptions: ['demo'],
      strategyMetaMap: {
        demo: {
          id: 'demo',
          created_at: '',
          updated_at: '',
          size: null
        }
      },
      strategyKeyword: '',
      selectedStrategyId: 'demo',
      strategyId: 'demo',
      strategyCode: DEFAULT_TEMPLATE,
      loadingList: false,
      loadingStrategy: false,
      savingStrategy: false,
      deletingStrategy: false,
      lastLoadedAt: '',
      showToast: false,
      toastType: 'success',
      toastMessage: '',
      toastTimer: null
    };
  },
  computed: {
    filteredStrategyOptions() {
      const keyword = (this.strategyKeyword || '').trim().toLowerCase();
      if (!keyword) {
        return this.strategyOptions;
      }

      return this.strategyOptions.filter((id) => String(id).toLowerCase().includes(keyword));
    },
    filteredStrategyRows() {
      return this.filteredStrategyOptions.map((id) => this.getStrategyMeta(id));
    },
    currentStrategyMeta() {
      const id = this.normalizeStrategyId(this.strategyId || this.selectedStrategyId || '');
      return this.getStrategyMeta(id);
    },
    isExistingStrategy() {
      const id = this.normalizeStrategyId(this.strategyId);
      return !!id && this.strategyOptions.includes(id);
    },
    canDeleteStrategy() {
      const id = this.normalizeStrategyId(this.strategyId);
      return !!id && id !== 'demo' && !this.deletingStrategy;
    }
  },
  methods: {
    normalizeStrategyId(value) {
      return String(value || '').trim();
    },
    normalizeCanonicalStrategyId(value, renameMap = null) {
      const raw = this.normalizeStrategyId(value);
      if (!raw) {
        return '';
      }
      const map = renameMap && typeof renameMap === 'object' ? renameMap : getStrategyRenameMap();
      return resolveCurrentStrategyId(raw, map) || raw;
    },
    normalizeCanonicalStrategyMetaList(list = [], renameMap = null) {
      const map = renameMap && typeof renameMap === 'object' ? renameMap : getStrategyRenameMap();
      const dedup = new Map();

      (list || []).forEach((item) => {
        if (!item || !item.id) {
          return;
        }
        const canonicalId = this.normalizeCanonicalStrategyId(item.id, map);
        if (!canonicalId) {
          return;
        }

        const nextItem = {
          ...item,
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
    getStrategyMeta(id) {
      const normalizedId = this.normalizeStrategyId(id);
      if (!normalizedId) {
        return {
          id: '',
          created_at: '',
          updated_at: '',
          size: null
        };
      }

      const raw = this.strategyMetaMap[normalizedId] || {};
      return {
        id: normalizedId,
        created_at: raw.created_at || '',
        updated_at: raw.updated_at || '',
        size: toNumberOrNull(raw.size)
      };
    },
    setStrategyMetadata(list = [], allIds = this.strategyOptions) {
      const nextMap = {};
      (allIds || []).forEach((id) => {
        const normalizedId = this.normalizeStrategyId(id);
        if (normalizedId) {
          nextMap[normalizedId] = {
            id: normalizedId,
            created_at: '',
            updated_at: '',
            size: null
          };
        }
      });

      (list || [])
        .filter((item) => item && item.id)
        .forEach((item) => {
          nextMap[item.id] = {
            ...nextMap[item.id],
            ...item,
            id: item.id
          };
        });

      this.strategyMetaMap = nextMap;
    },
    upsertStrategyMeta(item) {
      if (!item || !item.id) {
        return;
      }

      const normalizedId = this.normalizeStrategyId(item.id);
      if (!normalizedId) {
        return;
      }

      const previous = this.strategyMetaMap[normalizedId] || {
        id: normalizedId,
        created_at: '',
        updated_at: '',
        size: null
      };

      this.strategyMetaMap = {
        ...this.strategyMetaMap,
        [normalizedId]: {
          ...previous,
          ...item,
          id: normalizedId,
          size: toNumberOrNull(item.size ?? previous.size)
        }
      };
    },
    removeStrategyMeta(id) {
      const normalizedId = this.normalizeStrategyId(id);
      if (!normalizedId || !this.strategyMetaMap[normalizedId]) {
        return;
      }

      const next = { ...this.strategyMetaMap };
      delete next[normalizedId];
      this.strategyMetaMap = next;
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
    formatCodeSize(value) {
      const num = toNumberOrNull(value);
      if (num === null) {
        return '-';
      }
      return `${num} 字符`;
    },
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
    async fetchStrategyList(silent = false) {
      this.loadingList = true;
      let renameMap = getStrategyRenameMap();
      try {
        await syncStrategyRenameMap();
        renameMap = getStrategyRenameMap();
        const data = await listStrategies();
        const fromApi = this.normalizeCanonicalStrategyMetaList(normalizeStrategyList(data), renameMap);
        const apiIds = fromApi.map((item) => item.id);
        const localIds = Array.from(new Set(
          getLocalStrategyIds()
            .map((id) => this.normalizeCanonicalStrategyId(id, renameMap))
            .filter(Boolean)
        ));
        const merged = Array.from(new Set(['demo', ...apiIds, ...localIds]));
        this.strategyOptions = merged;
        this.setStrategyMetadata(fromApi, merged);
        mergeLocalStrategyIds(merged);
      } catch (error) {
        const fallback = Array.from(new Set(
          ['demo', ...getLocalStrategyIds()
            .map((id) => this.normalizeCanonicalStrategyId(id, renameMap))
            .filter(Boolean)]
        ));
        this.strategyOptions = fallback;
        this.setStrategyMetadata([], fallback);
        if (!silent) {
          this.showMessage(this.getErrorMessage(error, '获取策略列表失败，已使用本地缓存'), 'error');
        }
      } finally {
        this.loadingList = false;

        const editingId = this.normalizeCanonicalStrategyId(this.strategyId, renameMap);
        if (editingId && editingId !== this.strategyId) {
          this.strategyId = editingId;
        }
        if (editingId && !this.strategyOptions.includes(editingId)) {
          this.strategyOptions = Array.from(new Set([...this.strategyOptions, editingId]));
          this.upsertStrategyMeta({ id: editingId, size: (this.strategyCode || '').length });
        }

        const selectedId = this.normalizeCanonicalStrategyId(this.selectedStrategyId, renameMap);
        if (selectedId && selectedId !== this.selectedStrategyId) {
          this.selectedStrategyId = selectedId;
        }
        if (!this.strategyOptions.includes(this.selectedStrategyId)) {
          this.selectedStrategyId = this.strategyOptions[0] || 'demo';
        }
      }
    },
    handleSelectChange() {
      this.strategyId = this.normalizeCanonicalStrategyId(this.selectedStrategyId);
      this.selectedStrategyId = this.strategyId;
    },
    async handleLoadFromRow(id) {
      const targetId = this.normalizeCanonicalStrategyId(id);
      if (!targetId) {
        return;
      }

      this.strategyId = targetId;
      this.selectedStrategyId = targetId;
      await this.handleLoadStrategy();
    },
    async handleLoadStrategy() {
      const targetId = this.normalizeCanonicalStrategyId(this.strategyId);
      if (!targetId) {
        this.showMessage('请先填写策略 ID', 'error');
        return;
      }
      this.strategyId = targetId;

      this.loadingStrategy = true;
      try {
        const data = await getStrategy(targetId);
        this.strategyCode = normalizeCodePayload(data) || DEFAULT_TEMPLATE;
        this.lastLoadedAt = new Date().toLocaleString('zh-CN');

        const payload = unwrapDataPayload(data);
        const responseMeta = normalizeStrategyMeta(payload?.strategy || payload?.item || payload);
        const currentMeta = this.getStrategyMeta(targetId);
        const nowIso = new Date().toISOString();
        this.upsertStrategyMeta({
          id: targetId,
          created_at: responseMeta?.created_at || currentMeta.created_at || nowIso,
          updated_at: responseMeta?.updated_at || nowIso,
          size: responseMeta?.size ?? (this.strategyCode || '').length
        });

        mergeLocalStrategyId(targetId);
        if (!this.strategyOptions.includes(targetId)) {
          this.strategyOptions = Array.from(new Set([...this.strategyOptions, targetId]));
        }
        this.selectedStrategyId = targetId;
        this.showMessage('策略加载成功');
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '策略加载失败'), 'error');
      } finally {
        this.loadingStrategy = false;
      }
    },
    async handleSaveStrategy() {
      const targetId = this.normalizeCanonicalStrategyId(this.strategyId);
      if (!targetId) {
        this.showMessage('请先填写策略 ID', 'error');
        return;
      }
      this.strategyId = targetId;
      const isUpdate = this.strategyOptions.includes(targetId);

      const confirmed = window.confirm(`确认${isUpdate ? '更新' : '创建'}策略「${targetId}」吗？`);
      if (!confirmed) {
        return;
      }

      this.savingStrategy = true;
      try {
        await saveStrategy(targetId, this.strategyCode || '');
        mergeLocalStrategyId(targetId);

        if (!this.strategyOptions.includes(targetId)) {
          this.strategyOptions = Array.from(new Set([...this.strategyOptions, targetId]));
        }
        const nowIso = new Date().toISOString();
        const currentMeta = this.getStrategyMeta(targetId);
        this.upsertStrategyMeta({
          id: targetId,
          created_at: currentMeta.created_at || nowIso,
          updated_at: nowIso,
          size: (this.strategyCode || '').length
        });
        this.selectedStrategyId = targetId;
        this.showMessage(isUpdate ? '策略更新成功' : '策略创建成功');
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '策略保存失败'), 'error');
      } finally {
        this.savingStrategy = false;
      }
    },
    handleCreateStrategy() {
      const suggestedId = `strategy_${Date.now()}`;
      const input = window.prompt('请输入新策略 ID', suggestedId);
      if (input === null) {
        return;
      }

      const newId = this.normalizeStrategyId(input);
      if (!newId) {
        this.showMessage('策略 ID 不能为空', 'error');
        return;
      }
      if (/\s/.test(newId)) {
        this.showMessage('策略 ID 不能包含空白字符', 'error');
        return;
      }

      this.strategyId = newId;
      this.selectedStrategyId = newId;
      this.strategyCode = DEFAULT_TEMPLATE;
      this.lastLoadedAt = '';

      if (!this.strategyOptions.includes(newId)) {
        this.strategyOptions = Array.from(new Set([...this.strategyOptions, newId]));
      }
      this.upsertStrategyMeta({
        id: newId,
        size: DEFAULT_TEMPLATE.length
      });

      this.showMessage(`已切换到新策略：${newId}`);
    },
    async handleDeleteStrategy(targetId = '') {
      const id = this.normalizeCanonicalStrategyId(targetId || this.strategyId);
      if (!id) {
        this.showMessage('请先选择要删除的策略', 'error');
        return;
      }
      if (id === 'demo') {
        this.showMessage('demo 为内置示例策略，不支持删除', 'error');
        return;
      }

      const confirmed = window.confirm(`确认删除策略「${id}」吗？删除后无法恢复。`);
      if (!confirmed) {
        return;
      }

      this.deletingStrategy = true;
      try {
        const result = await deleteStrategyCascade(id);
        const deletedId = String(result?.strategyId || id).trim() || id;
        const deletedJobs = Number(result?.deletedJobs || 0);
        removeLocalStrategyId(deletedId);

        this.strategyOptions = this.strategyOptions.filter((item) => item !== deletedId);
        if (!this.strategyOptions.length) {
          this.strategyOptions = ['demo'];
        }
        this.removeStrategyMeta(deletedId);
        this.upsertStrategyMeta({ id: 'demo' });

        if (!this.strategyOptions.includes(this.selectedStrategyId)) {
          this.selectedStrategyId = this.strategyOptions[0];
        }
        if (this.normalizeStrategyId(this.strategyId) === deletedId) {
          this.strategyId = this.selectedStrategyId;
          this.strategyCode = DEFAULT_TEMPLATE;
          this.lastLoadedAt = '';
        }

        this.showMessage(`策略删除成功（同时删除 ${deletedJobs} 条历史任务）`);
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '策略删除失败'), 'error');
      } finally {
        this.deletingStrategy = false;
      }
    },
    goBacktest() {
      this.$router.push({
        path: '/strategies',
        query: {
          strategy_id: this.strategyId || 'demo'
        }
      });
    }
  },
  async mounted() {
    await this.fetchStrategyList(true);

    if (this.$route.query && this.$route.query.strategy_id) {
      this.strategyId = this.normalizeCanonicalStrategyId(String(this.$route.query.strategy_id));
      this.selectedStrategyId = this.strategyId;
    }

    if (this.strategyId) {
      await this.handleLoadStrategy();
    }
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
.strategy-editor-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.page-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.page-tag {
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

.page-header p {
  margin: 8px 0 0;
  color: #606266;
  font-size: 14px;
}

.quick-chip-row {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 12px;
  color: #606266;
  background: #f4f8ff;
  border: 1px solid #e1ecff;
}

.content-card {
  background: #fff;
  border: 1px solid #eef2f7;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-header {
  padding: 14px 16px;
  border-bottom: 1px solid #ebeef5;
  background: #f6faff;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.card-body {
  padding: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.form-row label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.text-input {
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

.actions-row {
  display: flex;
  gap: 12px;
  margin-top: 6px;
  flex-wrap: wrap;
  justify-content: space-between;
}

.actions-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.btn {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
  transform: translateY(-1px);
}

.btn-secondary {
  border-color: #dcdfe6;
  background: #fff;
  color: #606266;
}

.btn-secondary:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
  background: #ecf5ff;
  transform: translateY(-1px);
}

.btn-danger {
  background: #f56c6c;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #f78989;
  transform: translateY(-1px);
}

.btn-mini {
  padding: 4px 10px;
  font-size: 12px;
}

.meta-text {
  margin: 12px 0 0;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
}

.meta-sub-text {
  margin: 6px 0 0;
  color: #909399;
  font-size: 12px;
}

.strategy-summary {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.summary-chip {
  border: 1px solid #e4e8ee;
  border-radius: 10px;
  background: #f8fbff;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-chip span {
  color: #909399;
  font-size: 12px;
}

.summary-chip strong {
  color: #303133;
  font-size: 13px;
  font-weight: 600;
}

.strategy-table-wrap {
  margin-top: 14px;
  border: 1px solid #edf1f7;
  border-radius: 10px;
  overflow: hidden;
}

.table-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid #edf1f7;
  background: #f8fbff;
}

.table-title-row h4 {
  margin: 0;
  color: #303133;
  font-size: 14px;
}

.table-scroll {
  overflow-x: auto;
}

.strategy-info-table {
  width: 100%;
  border-collapse: collapse;
}

.strategy-info-table th,
.strategy-info-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #edf1f7;
  text-align: left;
  font-size: 13px;
  color: #4e5969;
  white-space: nowrap;
}

.strategy-info-table th {
  font-size: 12px;
  color: #909399;
  background: #fcfdff;
}

.strategy-info-table tbody tr:hover {
  background: #f8fbff;
}

.strategy-info-table tbody tr.row-active {
  background: #edf5ff;
}

.strategy-info-table .mono {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.editor-tip {
  border: 1px solid #e1ecff;
  background: #f4f8ff;
  color: #4e5969;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  margin-bottom: 10px;
}

.success-toast {
  position: fixed;
  top: 90px;
  right: 24px;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #fff;
  padding: 10px 14px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 2000;
  box-shadow: 0 6px 18px rgba(103, 194, 58, 0.35);
  font-size: 13px;
}

.success-toast.error {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  box-shadow: 0 6px 18px rgba(245, 108, 108, 0.35);
}

.toast-icon {
  width: 15px;
  height: 15px;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(14px);
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .actions-row {
    justify-content: flex-start;
  }

  .strategy-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 14px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .card-body {
    padding: 12px;
  }

  .success-toast {
    right: 12px;
    left: 12px;
  }

  .strategy-summary {
    grid-template-columns: 1fr;
  }

  .table-title-row {
    align-items: flex-start;
    flex-direction: column;
  }
}

body.dark-mode .page-header,
body.dark-mode .content-card {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.28);
}

body.dark-mode .card-header {
  background: #3a3a3a;
  border-color: #4c4d4f;
}

body.dark-mode .quick-chip {
  background: #3a3a3a;
  border-color: #4c4d4f;
  color: #d1d5db;
}

body.dark-mode .page-tag {
  background: rgba(64, 158, 255, 0.18);
  border-color: rgba(64, 158, 255, 0.35);
  color: #9ecfff;
}

body.dark-mode .page-header h2,
body.dark-mode .card-header h3,
body.dark-mode .text-input {
  color: #f5f7fa;
}

body.dark-mode .page-header p,
body.dark-mode .form-row label,
body.dark-mode .meta-text,
body.dark-mode .meta-sub-text {
  color: #b0b3b8;
}

body.dark-mode .text-input {
  background: #1f1f1f;
  border-color: #4c4d4f;
}

body.dark-mode .btn-secondary {
  background: #1f1f1f;
  color: #dcdfe6;
  border-color: #4c4d4f;
}

body.dark-mode .btn-secondary:hover:not(:disabled) {
  color: #66b1ff;
  border-color: #66b1ff;
  background: rgba(64, 158, 255, 0.12);
}

body.dark-mode .strategy-summary .summary-chip {
  background: #353638;
  border-color: #4c4d4f;
}

body.dark-mode .summary-chip strong,
body.dark-mode .table-title-row h4 {
  color: #f5f7fa;
}

body.dark-mode .table-title-row,
body.dark-mode .strategy-info-table th {
  background: #353638;
  border-color: #4c4d4f;
}

body.dark-mode .strategy-table-wrap,
body.dark-mode .strategy-info-table th,
body.dark-mode .strategy-info-table td {
  border-color: #4c4d4f;
}

body.dark-mode .strategy-info-table th,
body.dark-mode .strategy-info-table td,
body.dark-mode .summary-chip span {
  color: #b0b3b8;
}

body.dark-mode .strategy-info-table tbody tr:hover {
  background: #36383a;
}

body.dark-mode .strategy-info-table tbody tr.row-active {
  background: rgba(64, 158, 255, 0.16);
}

body.dark-mode .editor-tip {
  border-color: #4c4d4f;
  background: #3a3a3a;
  color: #d1d5db;
}
</style>
