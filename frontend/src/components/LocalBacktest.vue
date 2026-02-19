<template>
  <div class="local-backtest-page">
    <div class="page-header">
      <div class="page-title-row">
        <h2>本地回测</h2>
        <span class="page-tag">RQAlpha</span>
      </div>
      <p>选择策略并配置参数后发起回测，任务完成后自动展示指标、净值曲线和交易明细。</p>
      <div class="quick-chip-row">
        <span class="quick-chip">策略管理</span>
        <span class="quick-chip">参数配置</span>
        <span class="quick-chip">结果分析</span>
      </div>
    </div>

    <div class="editor-config-grid">
      <section class="content-card">
        <div class="card-header">
          <h3>策略选择区</h3>
        </div>

        <div class="card-body">
          <div class="form-row">
            <label for="strategy-select">选择策略</label>
            <select id="strategy-select" v-model="strategyId" class="text-input">
              <option v-for="id in filteredStrategyOptions" :key="`strategy-${id}`" :value="id">{{ id }}</option>
            </select>
            <p v-if="strategyKeyword && !filteredStrategyOptions.length" class="meta-sub-text">没有匹配的策略，请调整关键词或手动输入 ID。</p>
          </div>

          <div class="form-row">
            <label for="strategy-keyword">筛选关键词</label>
            <input
              id="strategy-keyword"
              v-model.trim="strategyKeyword"
              type="text"
              class="text-input"
              placeholder="输入关键词过滤策略列表"
            >
          </div>

          <div class="form-row">
            <label for="strategy-id">或手动输入策略 ID</label>
            <input id="strategy-id" v-model.trim="strategyId" type="text" class="text-input" placeholder="例如：demo">
          </div>

          <div class="actions-row">
            <button class="btn btn-secondary" :disabled="loadingStrategyList" @click="fetchStrategyList()">
              {{ loadingStrategyList ? '刷新中...' : '刷新策略列表' }}
            </button>
            <button class="btn btn-secondary" :disabled="loadingStrategy" @click="handleLoadStrategy">
              {{ loadingStrategy ? '加载中...' : '加载策略' }}
            </button>
          </div>

          <p class="meta-text">当前共 {{ strategyOptions.length }} 个策略可用</p>
          <p v-if="lastLoadedAt" class="meta-sub-text">最近加载时间：{{ lastLoadedAt }}</p>

          <div v-if="loadedStrategyCode" class="loaded-code-wrap">
            <div class="loaded-title-row">
              <span>策略代码预览</span>
              <button class="btn btn-secondary btn-mini" @click="showLoadedCode = !showLoadedCode">
                {{ showLoadedCode ? '收起' : '展开' }}
              </button>
            </div>
            <pre v-if="showLoadedCode" class="loaded-code">{{ loadedStrategyCode }}</pre>
          </div>
        </div>
      </section>

      <section class="content-card">
        <div class="card-header">
          <h3>回测配置区</h3>
        </div>

        <div class="card-body">
          <div class="form-grid">
            <div class="form-row">
              <label for="start-date">开始日期</label>
              <div class="date-input-wrap">
                <input
                  id="start-date"
                  v-model="form.start_date"
                  type="date"
                  class="text-input"
                  :max="form.end_date || todayDate"
                  @change="handleDateInput('start_date')"
                  @blur="handleDateInput('start_date')"
                >
                <button class="btn btn-secondary btn-mini date-action-btn" type="button" @click="setDateToToday('start_date')">
                  今天
                </button>
              </div>
            </div>
            <div class="form-row">
              <label for="end-date">结束日期</label>
              <div class="date-input-wrap">
                <input
                  id="end-date"
                  v-model="form.end_date"
                  type="date"
                  class="text-input"
                  :min="form.start_date || '2005-01-01'"
                  :max="todayDate"
                  @change="handleDateInput('end_date')"
                  @blur="handleDateInput('end_date')"
                >
                <button class="btn btn-secondary btn-mini date-action-btn" type="button" @click="setDateToToday('end_date')">
                  今天
                </button>
              </div>
            </div>
            <div class="form-row">
              <label for="cash">初始资金</label>
              <input id="cash" v-model.number="form.cash" type="number" min="0" class="text-input">
            </div>
            <div class="form-row">
              <label for="benchmark">基准</label>
              <input id="benchmark" v-model.trim="form.benchmark" type="text" class="text-input">
            </div>
            <div class="form-row">
              <label for="frequency">频率</label>
              <select id="frequency" v-model="form.frequency" class="text-input">
                <option value="1d">1d</option>
              </select>
            </div>
          </div>

          <div class="date-shortcuts">
            <span class="shortcut-label">快速区间</span>
            <button class="btn btn-secondary btn-mini" type="button" @click="setDateRangeDays(30)">近1个月</button>
            <button class="btn btn-secondary btn-mini" type="button" @click="setDateRangeDays(90)">近3个月</button>
            <button class="btn btn-secondary btn-mini" type="button" @click="setDateRangeDays(180)">近6个月</button>
            <button class="btn btn-secondary btn-mini" type="button" @click="setDateRangeYearToDate">今年以来</button>
            <button class="btn btn-secondary btn-mini" type="button" @click="resetDateRangeDefault">恢复默认</button>
          </div>

          <div class="actions-row">
            <button class="btn btn-primary" :disabled="!canStartBacktest" @click="handleStartBacktest">
              {{ isStarting ? '启动中...' : (isPolling ? '回测进行中...' : '开始回测') }}
            </button>
            <button v-if="isPolling" class="btn btn-secondary" @click="stopPolling(true)">
              停止刷新
            </button>
          </div>

          <div class="job-info" v-if="jobId">
            <div class="job-row">
              <span class="label">任务 ID：</span>
              <span class="value monospace">{{ jobId }}</span>
              <button class="btn btn-secondary btn-mini" @click="copyJobId">复制</button>
            </div>
            <div class="job-row">
              <span class="label">任务状态：</span>
              <span class="status-badge" :class="statusClass">{{ jobStatusText }}</span>
            </div>
            <div class="job-row" v-if="jobError">
              <span class="label">错误信息：</span>
              <span class="value error-text">{{ jobError }}</span>
            </div>
            <div class="job-progress">
              <div class="job-progress-inner" :class="statusClass" :style="{ width: `${jobProgressPercent}%` }"></div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <section class="content-card result-card">
      <div class="card-header">
        <h3>结果展示区</h3>
      </div>

      <div class="card-body">
        <div v-if="!jobId" class="empty-block">请先启动回测任务。</div>

        <template v-else>
          <div class="status-row">
            <span>当前任务状态：</span>
            <span class="status-badge" :class="statusClass">{{ jobStatusText }}</span>
          </div>

          <div v-if="jobStatus === 'FAILED'" class="failed-box">
            <p>任务失败：{{ jobError || '未知错误' }}</p>
            <button class="btn btn-secondary" :disabled="loadingLog" @click="handleToggleLog">
              {{ loadingLog ? '加载日志中...' : (showLog ? '隐藏日志' : '查看日志') }}
            </button>
          </div>

          <div v-if="showLog" class="log-panel">
            <pre>{{ jobLog || '暂无日志' }}</pre>
          </div>

          <div v-if="jobStatus === 'FINISHED' && resultData" class="result-sections">
            <div class="summary-grid">
              <div class="summary-card" v-for="item in summaryCards" :key="item.key">
                <div class="summary-label">{{ item.label }}</div>
                <div class="summary-value">{{ formatMetricValue(item.value, item.percent) }}</div>
              </div>
            </div>

            <div class="result-section">
              <div class="section-header-row">
                <div class="section-title">净值曲线（策略 / 基准）</div>
                <div class="section-actions" v-if="equityDetailRows.length">
                  <button class="btn btn-secondary btn-mini" @click="toggleEquityDetails">
                    {{ showEquityDetails ? '收起明细' : '查看明细' }}
                  </button>
                </div>
              </div>
              <div v-if="hasEquityData" class="equity-chart-wrap">
                <canvas ref="equityChart" class="equity-chart"></canvas>
              </div>
              <div v-else class="empty-block">暂无净值数据</div>

              <div v-if="showEquityDetails && equityDetailRows.length" class="detail-panel">
                <div class="table-hint">每日净值明细支持分页查看。</div>
                <div class="table-wrapper preview-table-wrap">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>日期</th>
                        <th>净值</th>
                        <th>收益率</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in pagedEquityRows" :key="`equity-${currentEquityPage}-${idx}`">
                        <td>{{ row.date }}</td>
                        <td>{{ formatMetricValue(row.nav, false) }}</td>
                        <td>{{ formatMetricValue(row.ret, true) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="pagination" v-if="totalEquityPages > 1">
                  <button class="btn btn-secondary" :disabled="currentEquityPage === 1" @click="goPrevEquityPage">
                    上一页
                  </button>
                  <span>第 {{ currentEquityPage }} / {{ totalEquityPages }} 页</span>
                  <button class="btn btn-secondary" :disabled="currentEquityPage === totalEquityPages" @click="goNextEquityPage">
                    下一页
                  </button>
                </div>
              </div>
            </div>

            <div class="result-section">
              <div class="section-header-row">
                <div class="section-title">交易列表</div>
                <div class="section-actions" v-if="allTradeColumns.length > coreTradeColumns.length">
                  <button class="btn btn-secondary btn-mini" @click="toggleTradeFieldMode">
                    {{ showAllTradeFields ? '只看核心字段' : `查看全部字段（+${allTradeColumns.length - coreTradeColumns.length}）` }}
                  </button>
                </div>
              </div>
              <div v-if="trades.length" class="table-wrapper">
                <div class="table-hint">表格支持左右滑动查看更多字段。</div>
                <table class="data-table">
                  <thead>
                    <tr>
                      <th v-for="(key, colIndex) in displayTradeColumns" :key="key" :class="{ 'sticky-col': colIndex === 0 }">
                        {{ formatTradeColumnLabel(key) }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in pagedTrades" :key="`trade-${currentTradePage}-${idx}`">
                      <td
                        v-for="(key, colIndex) in displayTradeColumns"
                        :key="`${key}-${idx}`"
                        :class="{ 'sticky-col': colIndex === 0 }"
                      >
                        {{ formatCellValue(row[key]) }}
                      </td>
                    </tr>
                  </tbody>
                </table>

                <div class="pagination" v-if="totalTradePages > 1">
                  <button class="btn btn-secondary" :disabled="currentTradePage === 1" @click="goPrevPage">
                    上一页
                  </button>
                  <span>第 {{ currentTradePage }} / {{ totalTradePages }} 页</span>
                  <button class="btn btn-secondary" :disabled="currentTradePage === totalTradePages" @click="goNextPage">
                    下一页
                  </button>
                </div>
              </div>
              <div v-else class="empty-block">暂无交易记录</div>
            </div>
          </div>
        </template>
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
import Chart from 'chart.js/auto';
import {
  listStrategies,
  getStrategy,
  runBacktest,
  getJob,
  getResult,
  getLog
} from '@/api/backtest';
import {
  getLocalStrategyIds,
  mergeLocalStrategyId,
  mergeLocalStrategyIds
} from '@/utils/backtestStrategies';
import { getStrategyRenameMap, resolveCurrentStrategyId, syncStrategyRenameMap } from '@/utils/strategyRenameMap';

function getTodayDate() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const d = String(now.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function formatDate(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return '';
  }
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function normalizeDateString(raw) {
  if (!raw) {
    return '';
  }

  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return raw;
  }

  const digits = String(raw).replace(/\D/g, '');
  if (!/^\d{8}$/.test(digits)) {
    return '';
  }

  const normalized = `${digits.slice(0, 4)}-${digits.slice(4, 6)}-${digits.slice(6, 8)}`;
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return formatDate(date);
}

function normalizeDateKey(raw) {
  if (raw === null || raw === undefined || raw === '') {
    return '';
  }

  const text = String(raw).trim();
  const matched = text.match(/^(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
  if (matched) {
    const yyyy = matched[1];
    const mm = matched[2].padStart(2, '0');
    const dd = matched[3].padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  const normalized = normalizeDateString(text);
  if (normalized) {
    return normalized;
  }

  const fallbackDate = new Date(text);
  if (Number.isNaN(fallbackDate.getTime())) {
    return '';
  }
  return formatDate(fallbackDate);
}

function normalizeCodePayload(data) {
  if (!data) {
    return '';
  }
  if (typeof data === 'string') {
    return data;
  }
  if (typeof data.code === 'string') {
    return data.code;
  }
  if (data.data && typeof data.data.code === 'string') {
    return data.data.code;
  }
  return '';
}

function normalizeLogPayload(data) {
  if (!data) {
    return '';
  }
  if (typeof data === 'string') {
    return data;
  }
  if (typeof data.log === 'string') {
    return data.log;
  }
  if (typeof data.content === 'string') {
    return data.content;
  }
  return JSON.stringify(data, null, 2);
}

function normalizeStrategyList(data) {
  if (!data) {
    return [];
  }

  const source = Array.isArray(data)
    ? data
    : (Array.isArray(data.strategies)
      ? data.strategies
      : (Array.isArray(data.items)
        ? data.items
        : (Array.isArray(data.data) ? data.data : [])));

  return Array.from(new Set(
    source
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }
        if (item && typeof item === 'object') {
          return item.id || item.strategy_id || item.name || '';
        }
        return '';
      })
      .filter(Boolean)
  ));
}

function toNumberOrNull(value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function getValueByPath(obj, path) {
  if (!obj || !path) {
    return undefined;
  }

  const parts = String(path).split('.');
  let current = obj;
  for (let i = 0; i < parts.length; i += 1) {
    if (!current || typeof current !== 'object') {
      return undefined;
    }
    current = current[parts[i]];
  }
  return current;
}

function pickFirstAvailable(sources, keys) {
  if (!Array.isArray(sources) || !Array.isArray(keys)) {
    return undefined;
  }

  for (let i = 0; i < keys.length; i += 1) {
    const key = keys[i];
    for (let j = 0; j < sources.length; j += 1) {
      const value = getValueByPath(sources[j], key);
      if (value !== null && value !== undefined && value !== '') {
        return value;
      }
    }
  }

  return undefined;
}

const TRADE_CORE_PRIORITY = [
  'datetime',
  'date',
  'trading_datetime',
  'order_book_id',
  'symbol',
  'instrument',
  'side',
  'position_effect',
  'price',
  'quantity',
  'amount',
  'commission',
  'tax',
  'pnl',
  'status'
];

const TRADE_LABEL_MAP = {
  datetime: '成交时间',
  date: '日期',
  trading_datetime: '交易时间',
  last_price: '最新价',
  last_quantity: '成交量',
  exec_id: '成交编号',
  order_id: '委托编号',
  order_book_id: '标的代码',
  symbol: '标的',
  instrument: '合约',
  side: '方向',
  position_effect: '开平',
  price: '成交价',
  quantity: '数量',
  amount: '成交额',
  commission: '手续费',
  transaction_cost: '交易成本',
  tax: '税费',
  pnl: '盈亏',
  status: '状态'
};

export default {
  name: 'LocalBacktest',
  props: {
    isDarkMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      strategyId: 'demo',
      strategyKeyword: '',
      strategyOptions: ['demo'],
      loadingStrategyList: false,
      loadingStrategy: false,
      loadedStrategyCode: '',
      showLoadedCode: false,
      lastLoadedAt: '',

      form: {
        start_date: '2025-01-01',
        end_date: getTodayDate(),
        cash: 1000000,
        benchmark: '000300.XSHG',
        frequency: '1d'
      },

      jobId: '',
      jobStatus: '',
      jobError: '',
      resultData: null,
      showLog: false,
      jobLog: '',
      loadingLog: false,

      isStarting: false,
      isPolling: false,
      pollingRequesting: false,
      pollTimer: null,

      chart: null,
      showEquityDetails: false,
      currentEquityPage: 1,
      equityPageSize: 20,
      currentTradePage: 1,
      tradePageSize: 10,
      showAllTradeFields: false,

      showToast: false,
      toastType: 'success',
      toastMessage: '',
      toastTimer: null
    };
  },
  computed: {
    todayDate() {
      return getTodayDate();
    },
    canStartBacktest() {
      return !!this.strategyId && !this.isStarting && !this.isPolling;
    },
    filteredStrategyOptions() {
      const keyword = (this.strategyKeyword || '').trim().toLowerCase();
      if (!keyword) {
        return this.strategyOptions;
      }

      return this.strategyOptions.filter((id) => String(id).toLowerCase().includes(keyword));
    },
    statusClass() {
      const status = (this.jobStatus || 'QUEUED').toLowerCase();
      return `status-${status}`;
    },
    jobStatusText() {
      const status = (this.jobStatus || 'QUEUED').toUpperCase();
      if (status === 'RUNNING') {
        return 'RUNNING';
      }
      if (status === 'FINISHED') {
        return 'FINISHED';
      }
      if (status === 'FAILED') {
        return 'FAILED';
      }
      if (status === 'CANCELLED') {
        return 'CANCELLED';
      }
      return 'QUEUED';
    },
    jobProgressPercent() {
      const status = (this.jobStatus || 'QUEUED').toUpperCase();
      if (status === 'RUNNING') {
        return 66;
      }
      if (status === 'FINISHED') {
        return 100;
      }
      if (status === 'FAILED' || status === 'CANCELLED') {
        return 100;
      }
      return 24;
    },
    summaryPayload() {
      if (this.resultData && this.resultData.summary && typeof this.resultData.summary === 'object') {
        return this.resultData.summary;
      }
      if (this.resultData && this.resultData.result && this.resultData.result.summary && typeof this.resultData.result.summary === 'object') {
        return this.resultData.result.summary;
      }
      if (this.resultData && this.resultData.data && this.resultData.data.summary && typeof this.resultData.data.summary === 'object') {
        return this.resultData.data.summary;
      }
      return {};
    },
    summaryMetricSources() {
      return [this.summaryPayload, this.resultData];
    },
    totalReturnsMetric() {
      const fromSummary = toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, [
        'total_returns',
        'total_return',
        'returns',
        'cumulative_returns',
        'cum_returns'
      ]));
      if (fromSummary !== null) {
        return fromSummary;
      }

      if (this.equityNavSeries.length >= 2) {
        const first = this.equityNavSeries[0];
        const last = this.equityNavSeries[this.equityNavSeries.length - 1];
        if (first !== null && last !== null && first !== 0) {
          return (last - first) / first;
        }
      }

      return null;
    },
    annualizedReturnsMetric() {
      const fromSummary = toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, [
        'annualized_returns',
        'annualized_return',
        'annual_return'
      ]));
      if (fromSummary !== null) {
        return fromSummary;
      }

      if (this.totalReturnsMetric === null || this.equityDateSeries.length < 2) {
        return null;
      }

      const start = new Date(this.equityDateSeries[0]).getTime();
      const end = new Date(this.equityDateSeries[this.equityDateSeries.length - 1]).getTime();
      if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
        return null;
      }

      const years = (end - start) / (365 * 24 * 3600 * 1000);
      if (years <= 0) {
        return null;
      }

      return Math.pow(1 + this.totalReturnsMetric, 1 / years) - 1;
    },
    alphaMetric() {
      return toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, ['alpha', 'excess_returns_alpha']));
    },
    betaMetric() {
      return toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, ['beta']));
    },
    sharpeMetric() {
      return toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, ['sharpe', 'sharpe_ratio']));
    },
    maxDrawdownMetric() {
      const fromSummary = toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, [
        'max_drawdown',
        'maximum_drawdown'
      ]));
      if (fromSummary !== null) {
        return fromSummary;
      }

      if (!this.equityNavSeries.length) {
        return null;
      }

      let peak = null;
      let maxDd = null;
      for (let i = 0; i < this.equityNavSeries.length; i += 1) {
        const nav = this.equityNavSeries[i];
        if (nav === null) {
          continue;
        }

        if (peak === null || nav > peak) {
          peak = nav;
        }
        if (peak && peak > 0) {
          const drawdown = (nav - peak) / peak;
          if (maxDd === null || drawdown < maxDd) {
            maxDd = drawdown;
          }
        }
      }
      return maxDd;
    },
    winRateMetric() {
      const fromSummary = toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, [
        'win_rate',
        'winning_rate',
        'wins_rate',
        'profitability.win_rate'
      ]));
      if (fromSummary !== null) {
        return fromSummary;
      }

      const pnlKeys = ['pnl', 'profit', 'profit_loss', 'realized_pnl', 'net_pnl'];
      const pnls = this.trades
        .map((row) => toNumberOrNull(pickFirstAvailable([row], pnlKeys)))
        .filter((item) => item !== null);
      if (pnls.length) {
        const winCount = pnls.filter((item) => item > 0).length;
        return winCount / pnls.length;
      }

      const returns = this.equityReturnsSeries.filter((item) => item !== null);
      if (returns.length) {
        const winCount = returns.filter((item) => item > 0).length;
        return winCount / returns.length;
      }

      return null;
    },
    profitLossRatioMetric() {
      const fromSummary = toNumberOrNull(pickFirstAvailable(this.summaryMetricSources, [
        'profit_loss_ratio',
        'profit_loss_rate',
        'pl_ratio',
        'gain_loss_ratio'
      ]));
      if (fromSummary !== null) {
        return fromSummary;
      }

      const pnlKeys = ['pnl', 'profit', 'profit_loss', 'realized_pnl', 'net_pnl'];
      const pnls = this.trades
        .map((row) => toNumberOrNull(pickFirstAvailable([row], pnlKeys)))
        .filter((item) => item !== null);
      if (pnls.length) {
        const wins = pnls.filter((item) => item > 0);
        const losses = pnls.filter((item) => item < 0).map((item) => Math.abs(item));
        if (!wins.length) {
          return 0;
        }
        if (!losses.length) {
          return Infinity;
        }

        const avgWin = wins.reduce((acc, n) => acc + n, 0) / wins.length;
        const avgLoss = losses.reduce((acc, n) => acc + n, 0) / losses.length;
        if (avgLoss === 0) {
          return Infinity;
        }
        return avgWin / avgLoss;
      }

      const returns = this.equityReturnsSeries.filter((item) => item !== null);
      if (returns.length) {
        const wins = returns.filter((item) => item > 0);
        const losses = returns.filter((item) => item < 0).map((item) => Math.abs(item));
        if (!wins.length) {
          return 0;
        }
        if (!losses.length) {
          return Infinity;
        }
        const avgWin = wins.reduce((acc, n) => acc + n, 0) / wins.length;
        const avgLoss = losses.reduce((acc, n) => acc + n, 0) / losses.length;
        if (avgLoss === 0) {
          return Infinity;
        }
        return avgWin / avgLoss;
      }

      return null;
    },
    summaryCards() {
      return [
        { key: 'total_returns', label: '总收益', value: this.totalReturnsMetric, percent: true },
        { key: 'annualized_returns', label: '年化收益', value: this.annualizedReturnsMetric, percent: true },
        { key: 'alpha', label: '阿尔法', value: this.alphaMetric, percent: false },
        { key: 'beta', label: '贝塔', value: this.betaMetric, percent: false },
        { key: 'win_rate', label: '胜率', value: this.winRateMetric, percent: true },
        { key: 'profit_loss_ratio', label: '盈亏比', value: this.profitLossRatioMetric, percent: false },
        { key: 'sharpe', label: '夏普比率', value: this.sharpeMetric, percent: false },
        { key: 'max_drawdown', label: '最大回撤', value: this.maxDrawdownMetric, percent: true }
      ];
    },
    equityData() {
      return this.resultData && this.resultData.equity ? this.resultData.equity : {};
    },
    equityDates() {
      return Array.isArray(this.equityData.dates) ? this.equityData.dates : [];
    },
    equityAlignedLength() {
      const nav = Array.isArray(this.equityData.nav) ? this.equityData.nav : [];
      return Math.min(this.equityDates.length, nav.length);
    },
    equityNavSeries() {
      const nav = Array.isArray(this.equityData.nav) ? this.equityData.nav : [];
      return nav.slice(0, this.equityAlignedLength).map((item) => toNumberOrNull(item));
    },
    equityDateSeries() {
      return this.equityDates.slice(0, this.equityAlignedLength);
    },
    equityReturnsSeries() {
      const returns = Array.isArray(this.equityData.returns) ? this.equityData.returns : [];
      const normalizedReturns = returns.slice(0, this.equityAlignedLength).map((item) => toNumberOrNull(item));
      const hasUsableReturns = normalizedReturns.some((v) => v !== null);

      if (normalizedReturns.length === this.equityAlignedLength && hasUsableReturns) {
        return normalizedReturns;
      }

      const derived = [];
      for (let i = 0; i < this.equityNavSeries.length; i += 1) {
        const current = this.equityNavSeries[i];
        if (current === null) {
          derived.push(null);
          continue;
        }

        if (i === 0) {
          derived.push(0);
          continue;
        }

        const prev = this.equityNavSeries[i - 1];
        if (prev === null || prev === 0) {
          derived.push(null);
          continue;
        }

        derived.push((current - prev) / prev);
      }

      return derived;
    },
    hasReturnsSeries() {
      return this.equityReturnsSeries.some((v) => v !== null);
    },
    benchmarkCurve() {
      const result = this.resultData || {};
      const equity = this.equityData || {};
      const baseDates = this.equityDateSeries;

      const pairSources = [
        { dates: equity.benchmark_dates || equity.dates, values: equity.benchmark_nav },
        { dates: equity.benchmark_dates || equity.dates, values: equity.benchmark },
        { dates: equity.benchmark_dates || equity.dates, values: equity.benchmark_navs },
        { dates: result.benchmark_dates || equity.dates, values: result.benchmark_nav },
        { dates: getValueByPath(result, 'benchmark_equity.dates'), values: getValueByPath(result, 'benchmark_equity.nav') },
        { dates: getValueByPath(result, 'benchmark_curve.dates'), values: getValueByPath(result, 'benchmark_curve.nav') },
        { dates: getValueByPath(result, 'benchmark.dates'), values: getValueByPath(result, 'benchmark.nav') },
        { dates: getValueByPath(result, 'equity.benchmark_curve.dates'), values: getValueByPath(result, 'equity.benchmark_curve.nav') }
      ];

      for (let i = 0; i < pairSources.length; i += 1) {
        const source = pairSources[i];
        const normalized = this.normalizeBenchmarkSeries(source.dates, source.values, baseDates);
        if (normalized && normalized.nav.some((v) => v !== null)) {
          return normalized;
        }
      }

      const rowSources = [
        result.benchmark_portfolio,
        getValueByPath(result, 'raw.benchmark_portfolio'),
        getValueByPath(result, 'benchmark.records'),
        getValueByPath(result, 'benchmark_curve.records'),
        getValueByPath(result, 'equity.benchmark_portfolio.records'),
        getValueByPath(result, 'benchmark_equity.records')
      ];

      for (let i = 0; i < rowSources.length; i += 1) {
        const fromRows = this.parseBenchmarkRows(rowSources[i], baseDates);
        if (fromRows && fromRows.nav.some((v) => v !== null)) {
          return fromRows;
        }
      }

      return {
        dates: baseDates,
        nav: []
      };
    },
    benchmarkNavSeries() {
      return Array.isArray(this.benchmarkCurve.nav) ? this.benchmarkCurve.nav : [];
    },
    hasBenchmarkSeries() {
      return this.benchmarkNavSeries.some((v) => v !== null);
    },
    hasEquityData() {
      return this.equityDateSeries.length > 0 && this.equityNavSeries.some((v) => v !== null);
    },
    equityDetailRows() {
      const size = Math.min(this.equityDateSeries.length, this.equityNavSeries.length);
      const rows = [];

      for (let i = 0; i < size; i += 1) {
        rows.push({
          date: this.equityDateSeries[i],
          nav: this.equityNavSeries[i],
          ret: this.equityReturnsSeries[i]
        });
      }

      return rows;
    },
    totalEquityPages() {
      if (!this.equityDetailRows.length) {
        return 1;
      }
      return Math.max(1, Math.ceil(this.equityDetailRows.length / this.equityPageSize));
    },
    pagedEquityRows() {
      const start = (this.currentEquityPage - 1) * this.equityPageSize;
      return this.equityDetailRows.slice(start, start + this.equityPageSize);
    },
    tradesRaw() {
      if (!this.resultData) {
        return [];
      }

      if (Array.isArray(this.resultData.trades)) {
        return this.resultData.trades;
      }

      if (this.resultData.trades && Array.isArray(this.resultData.trades.items)) {
        return this.resultData.trades.items;
      }

      if (this.resultData.trades && Array.isArray(this.resultData.trades.records)) {
        return this.resultData.trades.records;
      }

      return [];
    },
    tradeColumnCandidates() {
      if (!this.resultData) {
        return [];
      }

      const candidate = [];
      const pushColumns = (list) => {
        if (!Array.isArray(list)) {
          return;
        }
        list.forEach((item) => {
          if (typeof item === 'string' && item && !candidate.includes(item)) {
            candidate.push(item);
          }
        });
      };

      pushColumns(this.resultData.trade_columns);
      pushColumns(this.resultData.trade_keys);

      if (this.resultData.trades && typeof this.resultData.trades === 'object') {
        pushColumns(this.resultData.trades.columns);
        pushColumns(this.resultData.trades.keys);
      }

      return candidate;
    },
    trades() {
      const rows = this.tradesRaw;
      if (!rows.length) {
        return [];
      }

      const first = rows.find((row) => row !== null && row !== undefined);
      if (!first) {
        return [];
      }

      if (!Array.isArray(first)) {
        return rows
          .filter((row) => row && typeof row === 'object' && !Array.isArray(row))
          .map((row) => ({ ...row }));
      }

      const columnKeys = this.tradeColumnCandidates.length === first.length
        ? this.tradeColumnCandidates
        : first.map((_, index) => `col_${index + 1}`);

      return rows.map((row) => {
        if (!Array.isArray(row)) {
          if (row && typeof row === 'object') {
            return { ...row };
          }
          return { value: row };
        }

        const mapped = {};
        columnKeys.forEach((key, index) => {
          mapped[key] = row[index];
        });
        return mapped;
      });
    },
    allTradeColumns() {
      if (!this.trades.length) {
        return [];
      }

      const collected = new Set();
      this.trades.slice(0, 80).forEach((row) => {
        if (row && typeof row === 'object') {
          Object.keys(row).forEach((key) => {
            collected.add(key);
          });
        }
      });

      const rowKeys = Array.from(collected);
      if (!rowKeys.length) {
        return [];
      }

      const orderedByCandidate = this.tradeColumnCandidates.filter((key) => collected.has(key));
      if (orderedByCandidate.length) {
        const remain = rowKeys.filter((key) => !orderedByCandidate.includes(key));
        return [...orderedByCandidate, ...remain];
      }

      return rowKeys;
    },
    coreTradeColumns() {
      if (!this.allTradeColumns.length) {
        return [];
      }

      const preferred = TRADE_CORE_PRIORITY.filter((key) => this.allTradeColumns.includes(key));
      if (preferred.length) {
        return preferred;
      }

      return this.allTradeColumns.slice(0, Math.min(8, this.allTradeColumns.length));
    },
    displayTradeColumns() {
      if (this.showAllTradeFields) {
        return this.allTradeColumns;
      }
      return this.coreTradeColumns;
    },
    totalTradePages() {
      if (!this.trades.length) {
        return 1;
      }
      return Math.max(1, Math.ceil(this.trades.length / this.tradePageSize));
    },
    pagedTrades() {
      const start = (this.currentTradePage - 1) * this.tradePageSize;
      return this.trades.slice(start, start + this.tradePageSize);
    }
  },
  watch: {
    resultData() {
      this.showEquityDetails = false;
      this.currentEquityPage = 1;
      this.showAllTradeFields = false;
      this.currentTradePage = 1;
      this.$nextTick(() => {
        this.renderEquityChart();
      });
    },
    isDarkMode() {
      this.$nextTick(() => {
        this.renderEquityChart();
      });
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
        return data.message || data.error || fallback;
      }
      return (error && error.message) || fallback;
    },
    normalizeCanonicalStrategyId(id, renameMap = null) {
      const rawId = String(id || '').trim();
      if (!rawId) {
        return '';
      }
      const map = renameMap && typeof renameMap === 'object' ? renameMap : getStrategyRenameMap();
      return resolveCurrentStrategyId(rawId, map) || rawId;
    },
    normalizeCanonicalStrategyIds(ids = [], renameMap = null) {
      const map = renameMap && typeof renameMap === 'object' ? renameMap : getStrategyRenameMap();
      return Array.from(new Set(
        (ids || [])
          .map((id) => this.normalizeCanonicalStrategyId(id, map))
          .filter(Boolean)
      ));
    },
    async fetchStrategyList(silent = false) {
      this.loadingStrategyList = true;
      let renameMap = getStrategyRenameMap();
      try {
        await syncStrategyRenameMap();
        renameMap = getStrategyRenameMap();
        const data = await listStrategies();
        const fromApi = this.normalizeCanonicalStrategyIds(normalizeStrategyList(data), renameMap);
        const localIds = this.normalizeCanonicalStrategyIds(getLocalStrategyIds(), renameMap);
        const merged = Array.from(new Set(['demo', ...fromApi, ...localIds]));
        this.strategyOptions = merged;
        mergeLocalStrategyIds(merged);
      } catch (error) {
        const localIds = this.normalizeCanonicalStrategyIds(getLocalStrategyIds(), renameMap);
        this.strategyOptions = Array.from(new Set(['demo', ...localIds]));
        if (!silent) {
          this.showMessage(this.getErrorMessage(error, '获取策略列表失败，已使用本地缓存'), 'error');
        }
      } finally {
        this.loadingStrategyList = false;

        const canonicalCurrent = this.normalizeCanonicalStrategyId(this.strategyId, renameMap);
        if (canonicalCurrent && canonicalCurrent !== this.strategyId) {
          this.strategyId = canonicalCurrent;
        }
        if (this.strategyId && !this.strategyOptions.includes(this.strategyId)) {
          this.strategyOptions = Array.from(new Set([...this.strategyOptions, this.strategyId]));
        }
      }
    },
    async handleLoadStrategy() {
      const strategyId = this.normalizeCanonicalStrategyId(this.strategyId);
      if (!strategyId) {
        this.showMessage('请先选择或输入策略 ID', 'error');
        return;
      }
      this.strategyId = strategyId;

      this.loadingStrategy = true;
      try {
        const data = await getStrategy(strategyId);
        this.loadedStrategyCode = normalizeCodePayload(data);
        this.lastLoadedAt = new Date().toLocaleString('zh-CN');
        this.showLoadedCode = false;

        mergeLocalStrategyId(strategyId);
        if (!this.strategyOptions.includes(strategyId)) {
          this.strategyOptions = Array.from(new Set([...this.strategyOptions, strategyId]));
        }

        this.showMessage('策略加载成功');
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '策略加载失败'), 'error');
      } finally {
        this.loadingStrategy = false;
      }
    },
    normalizeDateField(field) {
      const normalized = normalizeDateString(this.form[field]);
      if (!normalized) {
        return false;
      }
      this.form[field] = normalized;
      return true;
    },
    clampDateRange(changedField) {
      if (!this.form.start_date || !this.form.end_date) {
        return;
      }
      if (this.form.start_date <= this.form.end_date) {
        return;
      }

      if (changedField === 'start_date') {
        this.form.end_date = this.form.start_date;
      } else {
        this.form.start_date = this.form.end_date;
      }
    },
    handleDateInput(field) {
      if (!this.normalizeDateField(field)) {
        if (field === 'end_date') {
          this.form.end_date = this.todayDate;
        } else {
          this.form.start_date = '2025-01-01';
        }
      }

      if (this.form.end_date > this.todayDate) {
        this.form.end_date = this.todayDate;
      }
      this.clampDateRange(field);
    },
    setDateToToday(field) {
      this.form[field] = this.todayDate;
      this.clampDateRange(field);
    },
    setDateRangeDays(days) {
      const end = new Date(this.todayDate);
      const start = new Date(end);
      start.setDate(start.getDate() - Math.max(1, Number(days)) + 1);

      this.form.start_date = formatDate(start);
      this.form.end_date = formatDate(end);
      this.showMessage(`已切换为近${days}天区间`);
    },
    setDateRangeYearToDate() {
      const end = new Date(this.todayDate);
      const start = new Date(end.getFullYear(), 0, 1);
      this.form.start_date = formatDate(start);
      this.form.end_date = formatDate(end);
      this.showMessage('已切换为今年以来');
    },
    resetDateRangeDefault() {
      this.form.start_date = '2025-01-01';
      this.form.end_date = this.todayDate;
      this.showMessage('已恢复默认日期区间');
    },
    async handleStartBacktest() {
      if (!this.canStartBacktest) {
        return;
      }
      const strategyId = this.normalizeCanonicalStrategyId(this.strategyId);
      if (!strategyId) {
        this.showMessage('请先选择或输入策略 ID', 'error');
        return;
      }
      this.strategyId = strategyId;

      this.handleDateInput('start_date');
      this.handleDateInput('end_date');

      this.isStarting = true;
      this.resultData = null;
      this.jobError = '';
      this.showLog = false;
      this.jobLog = '';

      try {
        const payload = {
          strategy_id: strategyId,
          start_date: this.form.start_date,
          end_date: this.form.end_date,
          cash: Number(this.form.cash),
          benchmark: this.form.benchmark,
          frequency: this.form.frequency
        };

        const data = await runBacktest(payload);
        const newJobId = data && (data.job_id || data.jobId);

        if (!newJobId) {
          throw new Error('回测任务返回缺少 job_id');
        }

        this.jobId = newJobId;
        this.jobStatus = 'QUEUED';
        this.showMessage(`回测任务已提交（${newJobId}）`);
        mergeLocalStrategyId(strategyId);
        this.startPolling();
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '回测启动失败'), 'error');
      } finally {
        this.isStarting = false;
      }
    },
    startPolling() {
      if (!this.jobId || this.pollTimer) {
        return;
      }

      this.isPolling = true;
      this.pollJobStatus();
      this.pollTimer = setInterval(() => {
        this.pollJobStatus();
      }, 2000);
    },
    stopPolling(showTip = false) {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }

      this.isPolling = false;
      this.pollingRequesting = false;

      if (showTip) {
        this.showMessage('已停止自动刷新');
      }
    },
    async pollJobStatus() {
      if (this.pollingRequesting || !this.jobId) {
        return;
      }

      this.pollingRequesting = true;
      try {
        const data = await getJob(this.jobId);
        const status = ((data && data.status) || this.jobStatus || 'QUEUED').toUpperCase();
        this.jobStatus = status;
        this.jobError = (data && (data.error || data.message)) || '';

        if (status === 'FAILED') {
          this.stopPolling();
          this.showMessage(this.jobError ? `回测失败：${this.jobError}` : '回测失败', 'error');
          return;
        }

        if (status === 'FINISHED') {
          this.stopPolling();
          await this.fetchResult();
        }
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '任务状态查询失败'), 'error');
      } finally {
        this.pollingRequesting = false;
      }
    },
    async fetchResult() {
      if (!this.jobId) {
        return;
      }

      try {
        const data = await getResult(this.jobId);
        this.resultData = data || null;
        this.showMessage('回测结果已更新');
      } catch (error) {
        if (error && error.response && error.response.status === 409) {
          this.jobStatus = 'RUNNING';
          if (!this.isPolling) {
            this.startPolling();
          }
          return;
        }

        this.showMessage(this.getErrorMessage(error, '获取回测结果失败'), 'error');
      }
    },
    async handleToggleLog() {
      this.showLog = !this.showLog;
      if (!this.showLog || this.jobLog || !this.jobId) {
        return;
      }

      this.loadingLog = true;
      try {
        const data = await getLog(this.jobId);
        this.jobLog = normalizeLogPayload(data) || '暂无日志';
      } catch (error) {
        this.showMessage(this.getErrorMessage(error, '获取日志失败'), 'error');
      } finally {
        this.loadingLog = false;
      }
    },
    toggleEquityDetails() {
      this.showEquityDetails = !this.showEquityDetails;
      if (this.showEquityDetails) {
        this.currentEquityPage = 1;
      }
    },
    goPrevEquityPage() {
      if (this.currentEquityPage > 1) {
        this.currentEquityPage -= 1;
      }
    },
    goNextEquityPage() {
      if (this.currentEquityPage < this.totalEquityPages) {
        this.currentEquityPage += 1;
      }
    },
    toggleTradeFieldMode() {
      this.showAllTradeFields = !this.showAllTradeFields;
      this.currentTradePage = 1;
    },
    normalizeBenchmarkSeries(sourceDates, sourceValues, baseDates) {
      if (!Array.isArray(sourceValues) || !sourceValues.length) {
        return null;
      }

      const values = sourceValues.map((item) => toNumberOrNull(item));
      const preferredDates = Array.isArray(baseDates) ? baseDates : [];

      if (Array.isArray(sourceDates) && sourceDates.length === values.length) {
        const pointMap = new Map();
        for (let i = 0; i < sourceDates.length; i += 1) {
          const key = normalizeDateKey(sourceDates[i]);
          if (!key || pointMap.has(key)) {
            continue;
          }
          pointMap.set(key, values[i]);
        }

        if (preferredDates.length) {
          const aligned = preferredDates.map((date) => {
            const key = normalizeDateKey(date);
            return pointMap.has(key) ? pointMap.get(key) : null;
          });
          return { dates: preferredDates, nav: aligned };
        }

        const dates = Array.from(pointMap.keys());
        return {
          dates,
          nav: dates.map((date) => pointMap.get(date))
        };
      }

      if (preferredDates.length) {
        if (values.length === preferredDates.length) {
          return {
            dates: preferredDates,
            nav: values
          };
        }
        return {
          dates: preferredDates,
          nav: preferredDates.map((_, index) => (index < values.length ? values[index] : null))
        };
      }

      return {
        dates: values.map((_, index) => String(index + 1)),
        nav: values
      };
    },
    parseBenchmarkRows(rows, baseDates) {
      const preferredDates = Array.isArray(baseDates) ? baseDates : [];
      const buildFromPointMap = (pointMap) => {
        if (!pointMap.size) {
          return null;
        }

        if (preferredDates.length) {
          return {
            dates: preferredDates,
            nav: preferredDates.map((date) => {
              const key = normalizeDateKey(date);
              return pointMap.has(key) ? pointMap.get(key) : null;
            })
          };
        }

        const dates = Array.from(pointMap.keys()).sort();
        return {
          dates,
          nav: dates.map((date) => pointMap.get(date))
        };
      };

      if (rows && typeof rows === 'object' && !Array.isArray(rows)) {
        if (Array.isArray(rows.records)) {
          rows = rows.records;
        } else if (Array.isArray(rows.items)) {
          rows = rows.items;
        } else {
          const mapFromObject = new Map();
          Object.keys(rows).forEach((rawKey) => {
            const date = normalizeDateKey(rawKey);
            if (!date || mapFromObject.has(date)) {
              return;
            }
            const rawValue = rows[rawKey];
            let nav = toNumberOrNull(rawValue);
            if (nav === null && rawValue && typeof rawValue === 'object') {
              nav = toNumberOrNull(pickFirstAvailable([rawValue], ['unit_net_value', 'nav', 'benchmark_nav', 'net_value', 'value']));
            }
            if (nav !== null) {
              mapFromObject.set(date, nav);
            }
          });

          const objectResult = buildFromPointMap(mapFromObject);
          if (objectResult) {
            return objectResult;
          }
          rows = Object.values(rows);
        }
      }

      if (!Array.isArray(rows) || !rows.length) {
        return null;
      }

      const dateKeyCandidates = ['date', 'datetime', 'trading_datetime', 'time', 'dt'];
      const valueKeyCandidates = ['unit_net_value', 'nav', 'benchmark_nav', 'net_value', 'value', 'portfolio_value', 'total_value'];
      const pointMap = new Map();

      rows.forEach((row) => {
        if (!row || typeof row !== 'object') {
          return;
        }

        const rawDate = pickFirstAvailable([row], dateKeyCandidates);
        const date = normalizeDateKey(rawDate);
        const nav = toNumberOrNull(pickFirstAvailable([row], valueKeyCandidates));
        if (!date || nav === null || pointMap.has(date)) {
          return;
        }
        pointMap.set(date, nav);
      });

      return buildFromPointMap(pointMap);
    },
    formatTradeColumnLabel(key) {
      return TRADE_LABEL_MAP[key] || key;
    },
    formatMetricValue(value, isPercent = false) {
      if (value === Infinity) {
        return '∞';
      }
      if (value === -Infinity) {
        return '-∞';
      }

      const num = toNumberOrNull(value);
      if (num !== null) {
        if (isPercent) {
          const absNum = Math.abs(num);
          const percentVal = absNum <= 2 ? num * 100 : num;
          return `${percentVal.toFixed(2)}%`;
        }
        return num.toFixed(4).replace(/\.?0+$/, '');
      }

      if (value === null || value === undefined || value === '') {
        return 'N/A';
      }

      return String(value);
    },
    formatCellValue(value) {
      const num = toNumberOrNull(value);
      if (num !== null) {
        return num.toLocaleString('zh-CN', {
          maximumFractionDigits: 6
        });
      }

      if (value === null || value === undefined || value === '') {
        return 'N/A';
      }

      if (typeof value === 'object') {
        return JSON.stringify(value);
      }

      return String(value);
    },
    async copyJobId() {
      if (!this.jobId) {
        return;
      }

      const text = String(this.jobId);
      try {
        if (window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
        } else {
          const input = document.createElement('textarea');
          input.value = text;
          input.setAttribute('readonly', '');
          input.style.position = 'fixed';
          input.style.opacity = '0';
          document.body.appendChild(input);
          input.select();
          document.execCommand('copy');
          document.body.removeChild(input);
        }
        this.showMessage('任务 ID 已复制');
      } catch (error) {
        this.showMessage('复制失败，请手动复制任务 ID', 'error');
      }
    },
    goPrevPage() {
      if (this.currentTradePage > 1) {
        this.currentTradePage -= 1;
      }
    },
    goNextPage() {
      if (this.currentTradePage < this.totalTradePages) {
        this.currentTradePage += 1;
      }
    },
    renderEquityChart() {
      if (!this.hasEquityData || !this.$refs.equityChart) {
        if (this.chart) {
          this.chart.destroy();
          this.chart = null;
        }
        return;
      }

      const canvasEl = this.$refs.equityChart;
      const ctx = canvasEl.getContext('2d');
      if (!ctx) {
        return;
      }

      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }

      const textColor = this.isDarkMode ? '#d1d5db' : '#303133';
      const splitLineColor = this.isDarkMode ? '#4b5563' : '#e5e7eb';
      const showBenchmark = this.hasBenchmarkSeries;

      const datasets = [
        {
          label: '策略净值',
          data: this.equityNavSeries,
          yAxisID: 'yNav',
          borderColor: '#409EFF',
          backgroundColor: 'rgba(64, 158, 255, 0.08)',
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 3,
          tension: 0.25,
          spanGaps: true
        }
      ];

      if (showBenchmark) {
        datasets.push({
          label: '基准净值',
          data: this.benchmarkNavSeries,
          yAxisID: 'yNav',
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 3,
          borderDash: [6, 4],
          tension: 0.25,
          spanGaps: true
        });
      }

      const scales = {
        x: {
          type: 'category',
          ticks: {
            color: textColor,
            autoSkip: true,
            maxTicksLimit: 8,
            padding: 6
          },
          grid: {
            color: splitLineColor
          }
        },
        yNav: {
          type: 'linear',
          position: 'left',
          ticks: {
            color: textColor,
            padding: 8
          },
          grid: {
            color: splitLineColor
          }
        }
      };

      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.equityDateSeries,
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              left: 8,
              right: 8,
              top: 4,
              bottom: 0
            }
          },
          interaction: {
            mode: 'index',
            intersect: false
          },
          animation: false,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: textColor
              }
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const val = context.parsed.y;
                  if (context.dataset && context.dataset.label === '基准净值') {
                    return `基准净值: ${Number(val).toFixed(4).replace(/\.?0+$/, '')}`;
                  }
                  return `策略净值: ${Number(val).toFixed(4).replace(/\.?0+$/, '')}`;
                }
              }
            }
          },
          scales
        }
      });
    },
    handleWindowResize() {
      if (this.chart) {
        this.chart.resize();
      }
    }
  },
  async mounted() {
    if (this.$route.query && this.$route.query.strategy_id) {
      this.strategyId = String(this.$route.query.strategy_id);
    }

    window.addEventListener('resize', this.handleWindowResize);
    await this.fetchStrategyList(true);
  },
  beforeUnmount() {
    this.stopPolling();

    if (this.toastTimer) {
      clearTimeout(this.toastTimer);
      this.toastTimer = null;
    }

    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }

    window.removeEventListener('resize', this.handleWindowResize);
  }
};
</script>

<style scoped>
.local-backtest-page {
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

.editor-config-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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

.date-input-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input-wrap .text-input {
  flex: 1;
  min-width: 0;
}

.date-action-btn {
  flex-shrink: 0;
}

.date-shortcuts {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin: 0 0 6px;
  padding: 8px 10px;
  border: 1px solid #e9eef5;
  background: #f8fbff;
  border-radius: 8px;
}

.shortcut-label {
  font-size: 12px;
  color: #606266;
  font-weight: 600;
  margin-right: 2px;
}

.actions-row {
  display: flex;
  gap: 10px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.btn {
  border: 1px solid transparent;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-mini {
  padding: 4px 10px;
  font-size: 12px;
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

.meta-text {
  margin: 10px 0 0;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
}

.meta-sub-text {
  margin: 6px 0 0;
  color: #909399;
  font-size: 12px;
}

.loaded-code-wrap {
  margin-top: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px;
  background: #fafafa;
}

.loaded-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #303133;
  font-size: 13px;
}

.loaded-code {
  margin: 8px 0 0;
  max-height: 220px;
  overflow: auto;
  background: #1f2937;
  color: #f9fafb;
  border-radius: 6px;
  padding: 10px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.job-info {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed #dcdfe6;
}

.job-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.job-row .label {
  color: #606266;
  font-size: 13px;
}

.job-row .value {
  color: #303133;
  font-size: 14px;
}

.monospace {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #303133;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-size: 12px;
  padding: 4px 10px;
  font-weight: 600;
}

.status-queued {
  color: #909399;
  background: #f4f4f5;
}

.status-running {
  color: #e6a23c;
  background: #fdf6ec;
}

.status-finished {
  color: #67c23a;
  background: #f0f9eb;
}

.status-failed {
  color: #f56c6c;
  background: #fef0f0;
}

.status-cancelled {
  color: #909399;
  background: #f4f4f5;
}

.job-progress {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: #f1f3f6;
  overflow: hidden;
  margin-top: 2px;
}

.job-progress-inner {
  height: 100%;
  border-radius: inherit;
  transition: width 0.35s ease;
  background: #909399;
}

.job-progress-inner.status-running {
  background: #e6a23c;
}

.job-progress-inner.status-finished {
  background: #67c23a;
}

.job-progress-inner.status-failed {
  background: #f56c6c;
}

.job-progress-inner.status-cancelled {
  background: #909399;
}

.error-text {
  color: #f56c6c !important;
}

.result-card .card-body {
  min-height: 180px;
}

.result-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.failed-box {
  border: 1px solid #fbc4c4;
  background: #fff5f5;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.failed-box p {
  margin: 0 0 10px;
  color: #f56c6c;
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 12px;
  background: #f8fbff;
}

.summary-card:nth-child(2n) {
  background: #f7faf8;
}

.summary-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 6px;
}

.summary-value {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.result-section {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 12px;
  background: #fcfdff;
}

.section-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
  margin-bottom: 0;
}

.equity-chart {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

.equity-chart-wrap {
  position: relative;
  width: 100%;
  height: clamp(280px, 42vh, 380px);
  border: 1px solid #edf1f7;
  border-radius: 10px;
  padding: 6px 8px 2px;
  background: #fff;
}

.preview-table-wrap {
  margin-top: 12px;
}

.detail-panel {
  margin-top: 12px;
}

.table-hint {
  color: #909399;
  font-size: 12px;
  margin-bottom: 8px;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 860px;
}

.data-table th,
.data-table td {
  border-bottom: 1px solid #ebeef5;
  padding: 10px 8px;
  font-size: 13px;
  color: #606266;
  text-align: left;
  white-space: nowrap;
}

.data-table th {
  color: #303133;
  font-weight: 600;
  background: #f4f8ff;
}

.data-table .sticky-col {
  position: sticky;
  left: 0;
  z-index: 2;
  background: #fff;
}

.data-table th.sticky-col {
  z-index: 3;
  background: #f4f8ff;
}

.data-table tbody tr:nth-child(even) td {
  background: #fafcff;
}

.data-table tbody tr:hover td {
  background: #eef6ff;
}

.pagination {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  color: #606266;
  font-size: 13px;
}

.log-panel {
  background: #1f2937;
  color: #f3f4f6;
  border-radius: 8px;
  padding: 10px;
  margin: 10px 0 14px;
  max-height: 320px;
  overflow: auto;
}

.log-panel pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.5;
}

.empty-block {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 16px;
  color: #909399;
  background: #f8fbff;
  font-size: 14px;
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

@media (max-width: 1024px) {
  .editor-config-grid {
    grid-template-columns: 1fr;
  }

  .summary-grid {
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

  .form-grid {
    grid-template-columns: 1fr;
  }

  .date-input-wrap {
    flex-direction: column;
    align-items: stretch;
  }

  .date-action-btn {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .equity-chart {
    height: 100% !important;
  }

  .equity-chart-wrap {
    height: 280px;
  }

  .success-toast {
    right: 12px;
    left: 12px;
  }
}

body.dark-mode .page-header,
body.dark-mode .content-card,
body.dark-mode .result-section,
body.dark-mode .summary-card,
body.dark-mode .loaded-code-wrap {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.28);
  border-color: #4c4d4f;
}

body.dark-mode .card-header,
body.dark-mode .data-table th,
body.dark-mode .empty-block {
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
body.dark-mode .section-title,
body.dark-mode .summary-value,
body.dark-mode .status-row,
body.dark-mode .job-row .value,
body.dark-mode .data-table th,
body.dark-mode .data-table td,
body.dark-mode .loaded-title-row {
  color: #f5f7fa;
}

body.dark-mode .page-header p,
body.dark-mode .form-row label,
body.dark-mode .summary-label,
body.dark-mode .job-row .label,
body.dark-mode .pagination,
body.dark-mode .meta-text,
body.dark-mode .meta-sub-text,
body.dark-mode .table-hint {
  color: #b0b3b8;
}

body.dark-mode .date-shortcuts {
  background: #343434;
  border-color: #4c4d4f;
}

body.dark-mode .shortcut-label {
  color: #d1d5db;
}

body.dark-mode .text-input {
  background: #1f1f1f;
  color: #f5f7fa;
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

body.dark-mode .data-table th,
body.dark-mode .data-table td,
body.dark-mode .job-info,
body.dark-mode .result-section {
  border-color: #4c4d4f;
}

body.dark-mode .equity-chart-wrap {
  border-color: #4c4d4f;
  background: #2d2d2d;
}

body.dark-mode .data-table .sticky-col {
  background: #2d2d2d;
}

body.dark-mode .data-table th.sticky-col {
  background: #3a3a3a;
}

body.dark-mode .data-table tbody tr:nth-child(even) td {
  background: #313131;
}

body.dark-mode .data-table tbody tr:hover td {
  background: #3a3a3a;
}

body.dark-mode .failed-box {
  background: rgba(245, 108, 108, 0.15);
  border-color: rgba(245, 108, 108, 0.35);
}
</style>
