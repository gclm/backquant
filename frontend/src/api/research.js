import axiosInstance from '@/utils/axios';

const RESEARCH_PREFIX = '/api/research';

function unwrapData(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return payload;
  }
  if (payload.data !== undefined && payload.data !== null) {
    return payload.data;
  }
  return payload;
}

export function listResearches(params = {}) {
  return axiosInstance
    .get(`${RESEARCH_PREFIX}/items`, { params })
    .then((res) => unwrapData(res.data));
}

export function createResearch(payload = {}) {
  return axiosInstance
    .post(`${RESEARCH_PREFIX}/items`, payload)
    .then((res) => unwrapData(res.data));
}

export function getResearch(id) {
  return axiosInstance
    .get(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}`)
    .then((res) => unwrapData(res.data));
}

export function updateResearch(id, payload = {}) {
  return axiosInstance
    .put(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}`, payload)
    .then((res) => unwrapData(res.data));
}

export function deleteResearch(id) {
  return axiosInstance
    .delete(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}`)
    .then((res) => unwrapData(res.data));
}

export function getNotebookSession(id, params = {}) {
  return axiosInstance
    .get(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}/notebook/session`, { params })
    .then((res) => unwrapData(res.data));
}

export function createNotebookSession(id, payload = {}) {
  return axiosInstance
    .post(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}/notebook/session`, payload)
    .then((res) => unwrapData(res.data));
}

export function refreshNotebookSession(id, payload = {}) {
  return axiosInstance
    .post(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}/notebook/session/refresh`, payload)
    .then((res) => unwrapData(res.data));
}

export function stopNotebookSession(id, payload = {}) {
  const config = {};
  if (payload && typeof payload === 'object' && Object.keys(payload).length) {
    config.data = payload;
  }
  return axiosInstance
    .delete(`${RESEARCH_PREFIX}/items/${encodeURIComponent(id)}/notebook/session`, config)
    .then((res) => unwrapData(res.data));
}
