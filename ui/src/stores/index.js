import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi, instancesApi, configApi, createWebSocket } from '../api'

export const useMainStore = defineStore('main', () => {
  // State
  const stats = ref({
    queue: { pending: 0, running: 0 },
    tasks: { total: 0, completed: 0, failed: 0 },
    instances: { total: 0, idle: 0, busy: 0, offline: 0 }
  })

  const instances = ref([])
  const queuedTasks = ref([])
  const runningTasks = ref([])
  const config = ref({
    task_timeout: 300,
    queue_timeout: 600,
    max_queue_size: 100,
    enable_priority: true,
    max_retries: 3,
    retry_delay: 5,
    health_check_interval: 30,
    instance_timeout: 10
  })

  const wsConnected = ref(false)
  let ws = null

  // Getters
  const totalPending = computed(() => stats.value.queue.pending)
  const totalRunning = computed(() => stats.value.queue.running)
  const totalCompleted = computed(() => stats.value.tasks.completed)
  const totalFailed = computed(() => stats.value.tasks.failed)

  // Actions
  async function fetchStats() {
    try {
      const response = await statsApi.get()
      stats.value = response.data
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  async function fetchInstances() {
    try {
      const response = await instancesApi.list()
      instances.value = response.data
    } catch (error) {
      console.error('Failed to fetch instances:', error)
    }
  }

  async function fetchConfig() {
    try {
      const response = await configApi.get()
      config.value = response.data
    } catch (error) {
      console.error('Failed to fetch config:', error)
    }
  }

  async function updateConfig(newConfig) {
    try {
      const response = await configApi.update(newConfig)
      config.value = response.data
      return true
    } catch (error) {
      console.error('Failed to update config:', error)
      return false
    }
  }

  async function addInstance(name, url) {
    try {
      await instancesApi.add(name, url)
      await fetchInstances()
      return true
    } catch (error) {
      console.error('Failed to add instance:', error)
      return false
    }
  }

  async function removeInstance(instanceId) {
    try {
      await instancesApi.remove(instanceId)
      await fetchInstances()
      return true
    } catch (error) {
      console.error('Failed to remove instance:', error)
      return false
    }
  }

  async function toggleInstance(instanceId, enable) {
    try {
      if (enable) {
        await instancesApi.enable(instanceId)
      } else {
        await instancesApi.disable(instanceId)
      }
      await fetchInstances()
      return true
    } catch (error) {
      console.error('Failed to toggle instance:', error)
      return false
    }
  }

  function connectWebSocket() {
    ws = createWebSocket(
      (data) => {
        wsConnected.value = true
        if (data.type === 'stats' && data.data) {
          stats.value = {
            queue: data.data.queue,
            tasks: data.data.tasks,
            instances: {
              total: data.data.instances.length,
              idle: data.data.instances.filter(i => i.status === 'idle' && i.enabled).length,
              busy: data.data.instances.filter(i => i.status === 'busy').length,
              offline: data.data.instances.filter(i => i.status === 'offline' || i.status === 'error').length
            }
          }
          instances.value = data.data.instances
          queuedTasks.value = data.data.queued_tasks || []
          runningTasks.value = data.data.running_tasks || []
        }
      },
      () => {
        wsConnected.value = false
      }
    )
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close()
      ws = null
    }
    wsConnected.value = false
  }

  function init() {
    fetchStats()
    fetchInstances()
    fetchConfig()
    connectWebSocket()
  }

  return {
    // State
    stats,
    instances,
    queuedTasks,
    runningTasks,
    config,
    wsConnected,

    // Getters
    totalPending,
    totalRunning,
    totalCompleted,
    totalFailed,

    // Actions
    fetchStats,
    fetchInstances,
    fetchConfig,
    updateConfig,
    addInstance,
    removeInstance,
    toggleInstance,
    connectWebSocket,
    disconnectWebSocket,
    init
  }
})
