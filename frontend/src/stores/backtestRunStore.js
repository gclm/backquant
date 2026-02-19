const STORAGE_KEY = 'backtest_run_cache_v1';

function safeParseJson(raw) {
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function nowIso() {
  return new Date().toISOString();
}

const state = {
  runs: {}
};

function toSerializableRun(run) {
  if (!run || typeof run !== 'object') {
    return null;
  }

  // 避免把大体积回测结果塞进 sessionStorage（可能超限/影响性能）。
  // 仅持久化：summary + UI 状态 + 轻量 cache 元信息。
  const cache = run.cache || {};
  const logText = typeof cache.logText === 'string' ? cache.logText : '';
  const serializedLog = logText.length > 8000 ? `${logText.slice(0, 8000)}\n...TRUNCATED` : logText;

  return {
    runId: run.runId,
    strategyId: run.strategyId || '',
    params: run.params || null,
    createdAt: run.createdAt,
    updatedAt: run.updatedAt,
    ui: run.ui || { activeTab: 'overview' },
    cache: {
      jobStatus: cache.jobStatus || '',
      jobError: cache.jobError || '',
      // resultData 不持久化，避免过大；保留是否有结果的标记
      hasResult: !!cache.resultData,
      logText: serializedLog
    }
  };
}

function persist() {
  try {
    const serializable = {
      runs: Object.fromEntries(
        Object.entries(state.runs || {}).map(([key, run]) => [key, toSerializableRun(run)]).filter(([, value]) => value)
      )
    };
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(serializable));
  } catch (e) {
    // ignore
  }
}

function hydrateOnce() {
  if (hydrateOnce.done) {
    return;
  }
  hydrateOnce.done = true;

  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return;
    }
    const parsed = safeParseJson(raw);
    if (!parsed || typeof parsed !== 'object' || !parsed.runs || typeof parsed.runs !== 'object') {
      return;
    }
    state.runs = parsed.runs;
  } catch (e) {
    // ignore
  }
}

hydrateOnce.done = false;

export function getBacktestRunState(runId) {
  hydrateOnce();
  const id = String(runId || '').trim();
  if (!id) {
    return null;
  }

  if (!state.runs[id]) {
    state.runs[id] = {
      runId: id,
      strategyId: '',
      params: null,
      createdAt: nowIso(),
      updatedAt: nowIso(),
      ui: {
        activeTab: 'overview'
      },
      cache: {
        jobStatus: '',
        jobError: '',
        resultData: null,
        logText: ''
      }
    };
    persist();
  }

  return state.runs[id];
}

export function upsertBacktestRunSummary(runId, { strategyId = '', params = null } = {}) {
  const run = getBacktestRunState(runId);
  if (!run) {
    return null;
  }

  run.strategyId = strategyId || run.strategyId || '';
  run.params = params || run.params || null;
  run.updatedAt = nowIso();
  persist();
  return run;
}

export function setBacktestRunActiveTab(runId, tab) {
  const run = getBacktestRunState(runId);
  if (!run) {
    return;
  }
  run.ui = run.ui || {};
  run.ui.activeTab = String(tab || 'overview');
  run.updatedAt = nowIso();
  persist();
}

export function upsertBacktestRunCache(runId, { jobStatus, jobError, resultData, logText } = {}) {
  const run = getBacktestRunState(runId);
  if (!run) {
    return null;
  }

  run.cache = run.cache || {};
  if (jobStatus !== undefined) {
    run.cache.jobStatus = String(jobStatus || '');
  }
  if (jobError !== undefined) {
    run.cache.jobError = String(jobError || '');
  }
  if (resultData !== undefined) {
    run.cache.resultData = resultData || null;
  }
  if (logText !== undefined) {
    run.cache.logText = String(logText || '');
  }

  run.updatedAt = nowIso();
  persist();
  return run;
}

export function renameBacktestRunStrategyId(fromId, toId) {
  hydrateOnce();

  const from = String(fromId || '').trim();
  const to = String(toId || '').trim();
  if (!from || !to || from === to) {
    return 0;
  }

  let updated = 0;
  Object.keys(state.runs || {}).forEach((runId) => {
    const run = state.runs[runId];
    if (run && String(run.strategyId || '').trim() === from) {
      run.strategyId = to;
      run.updatedAt = nowIso();
      updated += 1;
    }
  });

  if (updated > 0) {
    persist();
  }

  return updated;
}
