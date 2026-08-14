import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Tasks API
export const tasksApi = {
  create: (payload, asyncMode = false, priority = 5) =>
    api.post('/tasks', { payload, async: asyncMode, priority }),

  get: (taskId) => api.get(`/tasks/${taskId}`),

  list: (status = null) => api.get('/tasks', { params: { status } }),

  listByStatus: (status = null, page = 1, pageSize = 50) =>
    api.get('/tasks', { params: { status, page, page_size: pageSize } }),

  cancel: (taskId) => api.delete(`/tasks/${taskId}`),

  listFailed: () => api.get('/tasks/failed/list'),

  retry: (taskId) => api.post(`/tasks/${taskId}/retry`),

  retryAll: () => api.post('/tasks/retry-all')
}

// Instances API
export const instancesApi = {
  list: () => api.get('/instances'),

  add: (name, url, backend = 'pipeline') => api.post('/instances', { name, url, backend }),

  update: (instanceId, data) => api.patch(`/instances/${instanceId}`, data),

  remove: (instanceId) => api.delete(`/instances/${instanceId}`),

  enable: (instanceId) => api.post(`/instances/${instanceId}/enable`),

  disable: (instanceId) => api.post(`/instances/${instanceId}/disable`)
}

// Config API
export const configApi = {
  get: () => api.get('/config'),

  update: (config) => api.patch('/config', config)
}

// Stats API
export const statsApi = {
  get: () => api.get('/stats')
}

export default api
