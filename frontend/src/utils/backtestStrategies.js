const STORAGE_KEY = 'backtest_strategy_ids';

function uniqueIds(ids) {
  return Array.from(new Set((ids || []).filter((id) => typeof id === 'string' && id.trim()).map((id) => id.trim())));
}

export function getLocalStrategyIds() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }
    return uniqueIds(parsed);
  } catch (error) {
    return [];
  }
}

export function saveLocalStrategyIds(ids) {
  const normalized = uniqueIds(ids);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized));
  return normalized;
}

export function mergeLocalStrategyId(id) {
  const merged = uniqueIds([...getLocalStrategyIds(), id]);
  return saveLocalStrategyIds(merged);
}

export function mergeLocalStrategyIds(ids) {
  const merged = uniqueIds([...getLocalStrategyIds(), ...(ids || [])]);
  return saveLocalStrategyIds(merged);
}

export function removeLocalStrategyId(id) {
  const target = typeof id === 'string' ? id.trim() : '';
  if (!target) {
    return getLocalStrategyIds();
  }

  const next = getLocalStrategyIds().filter((item) => item !== target);
  return saveLocalStrategyIds(next);
}

export function renameLocalStrategyId(fromId, toId) {
  const from = typeof fromId === 'string' ? fromId.trim() : '';
  const to = typeof toId === 'string' ? toId.trim() : '';

  if (!to) {
    return getLocalStrategyIds();
  }

  if (!from || from === to) {
    return mergeLocalStrategyId(to);
  }

  const ids = getLocalStrategyIds().filter((item) => item !== from);
  ids.push(to);
  return saveLocalStrategyIds(ids);
}
