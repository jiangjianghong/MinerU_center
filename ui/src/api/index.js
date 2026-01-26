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

  cancel: (taskId) => api.delete(`/tasks/${taskId}`)
}

// Instances API
export const instancesApi = {
  list: () => api.get('/instances'),

  add: (name, url) => api.post('/instances', { name, url }),

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

// WebSocket connection
export function createWebSocket(onMessage, onError = null) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const ws = new WebSocket(`${protocol}//${host}/api/stats/ws`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch (e) {
      console.error('WebSocket parse error:', e)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    if (onError) onError(error)
  }

  ws.onclose = () => {
    console.log('WebSocket closed, reconnecting...')
    setTimeout(() => createWebSocket(onMessage, onError), 3000)
  }

  return ws
}

export default api
