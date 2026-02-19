import axiosInstance from '@/utils/axios';

const BACKTEST_PREFIX = '/api/backtest';

export function listStrategies(params = {}) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/strategies`, { params })
    .then((res) => res.data);
}

export function saveStrategy(id, code) {
  return axiosInstance
    .post(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(id)}`, { code })
    .then((res) => res.data);
}

export function getStrategy(id) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(id)}`)
    .then((res) => res.data);
}

export function deleteStrategy(id) {
  return axiosInstance
    .delete(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(id)}`)
    .then((res) => res.data);
}

export function renameStrategy(fromId, toId, payload = {}) {
  return axiosInstance
    .post(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(fromId)}/rename`, {
      to_id: toId,
      ...payload
    })
    .then((res) => res.data);
}

export function compileStrategy(id, payload = {}) {
  return axiosInstance
    .post(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(id)}/compile`, payload)
    .then((res) => res.data);
}

export function runBacktest(params) {
  return axiosInstance
    .post(`${BACKTEST_PREFIX}/run`, params)
    .then((res) => res.data);
}

export function getJob(jobId) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/jobs/${encodeURIComponent(jobId)}`)
    .then((res) => res.data);
}

export function listStrategyJobs(strategyId, params = {}) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/strategies/${encodeURIComponent(strategyId)}/jobs`, { params })
    .then((res) => res.data);
}

export function getResult(jobId, params = {}) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/jobs/${encodeURIComponent(jobId)}/result`, { params })
    .then((res) => res.data);
}

export function getLog(jobId) {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/jobs/${encodeURIComponent(jobId)}/log`)
    .then((res) => res.data);
}

export function deleteJob(jobId) {
  return axiosInstance
    .delete(`${BACKTEST_PREFIX}/jobs/${encodeURIComponent(jobId)}`)
    .then((res) => res.data);
}

export function fetchStrategyRenameMap() {
  return axiosInstance
    .get(`${BACKTEST_PREFIX}/strategy-renames`)
    .then((res) => res.data);
}
