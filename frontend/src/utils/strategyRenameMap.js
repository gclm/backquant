import { fetchStrategyRenameMap } from '@/api/backtest';

const STORAGE_KEY = 'backtest_strategy_rename_map_v1';

function normalizeId(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function normalizeMap(map) {
  const normalized = {};
  Object.entries(map || {}).forEach(([fromId, toId]) => {
    const from = normalizeId(fromId);
    const to = normalizeId(toId);
    if (from && to && from !== to) {
      normalized[from] = to;
    }
  });
  return normalized;
}

function unwrapPayload(payload) {
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

function normalizeMapPayload(payload) {
  const root = unwrapPayload(payload);
  if (!root || typeof root !== 'object') {
    return {};
  }
  if (root.map && typeof root.map === 'object') {
    return normalizeMap(root.map);
  }
  return normalizeMap(root);
}

function readRawMap() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return {};
    }
    return normalizeMap(parsed);
  } catch (error) {
    return {};
  }
}

function saveRawMap(map) {
  const normalized = normalizeMap(map);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(normalized));
  return normalized;
}

export function getStrategyRenameMap() {
  return readRawMap();
}

export function resolveCurrentStrategyId(id, mapInput = null) {
  const start = normalizeId(id);
  if (!start) {
    return '';
  }

  const map = mapInput && typeof mapInput === 'object' ? normalizeMap(mapInput) : readRawMap();
  let current = start;
  const visited = new Set([start]);

  while (map[current]) {
    const next = normalizeId(map[current]);
    if (!next || visited.has(next)) {
      break;
    }
    visited.add(next);
    current = next;
  }

  return current;
}

export function getStrategyAliasIds(id, mapInput = null) {
  const current = resolveCurrentStrategyId(id, mapInput);
  if (!current) {
    return [];
  }

  const map = mapInput && typeof mapInput === 'object' ? normalizeMap(mapInput) : readRawMap();
  const aliases = new Set([current]);
  Object.keys(map).forEach((fromId) => {
    if (resolveCurrentStrategyId(fromId, map) === current) {
      aliases.add(normalizeId(fromId));
    }
  });
  return Array.from(aliases).filter(Boolean);
}

export async function syncStrategyRenameMap() {
  if (process.env.NODE_ENV === 'test') {
    return getStrategyRenameMap();
  }

  try {
    const remotePayload = await fetchStrategyRenameMap();
    const remoteMap = normalizeMapPayload(remotePayload);
    return saveRawMap(remoteMap);
  } catch (error) {
    return readRawMap();
  }
}
