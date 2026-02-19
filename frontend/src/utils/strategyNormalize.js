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

function toNumberOrNull(value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

export function normalizeStrategyMeta(item) {
  if (typeof item === 'string') {
    const id = item.trim();
    return id
      ? {
        id,
        created_at: '',
        updated_at: '',
        size: null,
        read_only: false,
        is_builtin: false,
        can_delete: true
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
    created_at: item.created_at || item.createdAt || item.create_time || item.createTime || item.ctime || '',
    updated_at: item.updated_at || item.updatedAt || item.update_time || item.updateTime || item.mtime || '',
    size: toNumberOrNull(item.size ?? item.code_size ?? item.bytes),
    read_only: Boolean(item.read_only ?? item.readonly),
    is_builtin: Boolean(item.is_builtin ?? item.builtin ?? item.system),
    can_delete: item.can_delete === undefined ? true : Boolean(item.can_delete)
  };
}

export function normalizeStrategyList(data) {
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

export function normalizeCodePayload(data) {
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
