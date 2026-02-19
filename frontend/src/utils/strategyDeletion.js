import { deleteJob, deleteStrategy, listStrategyJobs } from '@/api/backtest';
import {
  getStrategyAliasIds,
  getStrategyRenameMap,
  resolveCurrentStrategyId,
  syncStrategyRenameMap
} from '@/utils/strategyRenameMap';

const JOB_PAGE_SIZE = 200;
const DELETE_BATCH_SIZE = 10;
const MAX_PURGE_ROUNDS = 500;

function extractResponseText(error) {
  const data = error?.response?.data;
  if (typeof data === 'string') {
    return data;
  }
  if (data && typeof data === 'object') {
    const msg = data?.error?.message || data?.message || '';
    return String(msg || '');
  }
  return '';
}

function toMethodNotAllowedMessage(error, endpointDesc) {
  const status = error?.response?.status;
  if (!(status === 405 || status === 501)) {
    return '';
  }
  const rawText = extractResponseText(error);
  if (/method not allowed/i.test(rawText)) {
    return `后端未支持 ${endpointDesc}（HTTP ${status}）`;
  }
  return `后端接口不可用：${endpointDesc}（HTTP ${status}）`;
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

function normalizeJobs(payload) {
  const root = unwrapPayload(payload);
  if (!root) {
    return [];
  }

  if (Array.isArray(root)) {
    return root;
  }

  if (Array.isArray(root.jobs)) {
    return root.jobs;
  }

  if (Array.isArray(root.items)) {
    return root.items;
  }

  return [];
}

function chunkList(list, size) {
  const output = [];
  for (let i = 0; i < list.length; i += size) {
    output.push(list.slice(i, i + size));
  }
  return output;
}

async function purgeJobsForStrategy(strategyId) {
  let deleted = 0;
  for (let round = 0; round < MAX_PURGE_ROUNDS; round += 1) {
    let response;
    try {
      response = await listStrategyJobs(strategyId, {
        limit: JOB_PAGE_SIZE,
        offset: 0
      });
    } catch (error) {
      const status = error?.response?.status;
      if (status === 404) {
        return deleted;
      }
      const notAllowedMsg = toMethodNotAllowedMessage(error, 'GET /api/backtest/strategies/{id}/jobs');
      if (notAllowedMsg) {
        throw new Error(notAllowedMsg);
      }
      throw error;
    }
    const jobs = normalizeJobs(response);
    const jobIds = Array.from(new Set(
      jobs
        .map((item) => String(item?.job_id || '').trim())
        .filter(Boolean)
    ));

    if (!jobIds.length) {
      return deleted;
    }

    const batches = chunkList(jobIds, DELETE_BATCH_SIZE);
    for (let i = 0; i < batches.length; i += 1) {
      const batch = batches[i];
      await Promise.all(batch.map(async (jobId) => {
        try {
          await deleteJob(jobId);
        } catch (error) {
          const status = error?.response?.status;
          if (status !== 404) {
            const notAllowedMsg = toMethodNotAllowedMessage(error, 'DELETE /api/backtest/jobs/{id}');
            if (notAllowedMsg) {
              throw new Error(`${notAllowedMsg}，无法执行“删除策略时同步删除历史任务”`);
            }
            throw error;
          }
        }
      }));
      deleted += batch.length;
    }
  }

  throw new Error(`删除策略 ${strategyId} 的历史任务超出上限，请重试`);
}

function parseConflictError(error) {
  const status = error?.response?.status;
  if (status !== 409) {
    return '';
  }
  const data = error?.response?.data;
  if (!data) {
    return '';
  }
  if (typeof data === 'string') {
    return data;
  }
  const msg = data?.error?.message || data?.message || '';
  return String(msg || '').trim();
}

export async function deleteStrategyCascade(strategyId) {
  const rawId = String(strategyId || '').trim();
  if (!rawId) {
    throw new Error('策略 ID 不能为空');
  }

  await syncStrategyRenameMap();
  const renameMap = getStrategyRenameMap();
  const canonicalId = resolveCurrentStrategyId(rawId, renameMap) || rawId;
  const aliasIds = getStrategyAliasIds(canonicalId, renameMap);
  const targetIds = Array.from(new Set([canonicalId, ...aliasIds])).filter(Boolean);

  let deletedJobs = 0;
  for (let i = 0; i < targetIds.length; i += 1) {
    deletedJobs += await purgeJobsForStrategy(targetIds[i]);
  }

  try {
    await deleteStrategy(canonicalId);
  } catch (error) {
    const deleteNotAllowedMsg = toMethodNotAllowedMessage(error, 'DELETE /api/backtest/strategies/{id}');
    if (deleteNotAllowedMsg) {
      throw new Error(`${deleteNotAllowedMsg}，请后端补齐删除策略接口`);
    }

    const conflictMsg = parseConflictError(error);
    if (!conflictMsg) {
      throw error;
    }

    // 后端可能在短时间内仍读取到残留引用，冲突时再做一次清理并重试。
    for (let i = 0; i < targetIds.length; i += 1) {
      deletedJobs += await purgeJobsForStrategy(targetIds[i]);
    }
    await deleteStrategy(canonicalId);
  }

  return {
    strategyId: canonicalId,
    deletedJobs
  };
}
