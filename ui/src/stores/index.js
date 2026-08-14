import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi, instancesApi, configApi, tasksApi } from '../api'

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
  const failedTasks = ref([])
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

  const dataFresh = ref(false)
  let pollTimer = null
  let pollInFlight = false
  let polling = false
  let failureCount = 0
  const failureDelays = [2000, 5000, 10000, 30000]

  // Task list dialog state
  const taskListDialog = ref({
    visible: false,
    status: null,  // null | 'pending' | 'running' | 'completed'
    tasks: [],
    total: 0,
    page: 1,
    pageSize: 50,
    loading: false
  })

  // Getters
  const totalPending = computed(() => stats.value.queue.pending)
  const totalRunning = computed(() => stats.value.queue.running)
  const totalCompleted = computed(() => stats.value.tasks.completed)
  const totalFailed = computed(() => stats.value.tasks.failed)

  // Actions
  async function fetchStats() {
    if (pollInFlight) return false
    pollInFlight = true
    try {
      const response = await statsApi.get()
      const data = response.data
      stats.value = {
        queue: data.queue,
        tasks: data.tasks,
        instances: {
          total: data.instances.length,
          idle: data.instances.filter(i => i.status === 'idle' && i.enabled).length,
          busy: data.instances.filter(i => i.status === 'busy').length,
          offline: data.instances.filter(i => i.status === 'offline' || i.status === 'error').length
        }
      }
      instances.value = data.instances
      queuedTasks.value = data.queued_tasks || []
      runningTasks.value = data.running_tasks || []
      dataFresh.value = true
      failureCount = 0
      return true
    } catch (error) {
      dataFresh.value = false
      failureCount += 1
      console.error('Failed to fetch stats:', error)
      return false
    } finally {
      pollInFlight = false
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

  async function addInstance(name, url, backend = 'pipeline') {
    try {
      await instancesApi.add(name, url, backend)
      await fetchInstances()
      return true
    } catch (error) {
      console.error('Failed to add instance:', error)
      return false
    }
  }

  async function updateInstance(instanceId, data) {
    try {
      await instancesApi.update(instanceId, data)
      await fetchInstances()
      return true
    } catch (error) {
      console.error('Failed to update instance:', error)
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

  function nextPollDelay() {
    if (failureCount > 0) {
      return failureDelays[Math.min(failureCount - 1, failureDelays.length - 1)]
    }
    if (document.hidden) return 15000
    return stats.value.queue.pending + stats.value.queue.running > 0 ? 2000 : 5000
  }

  function schedulePoll() {
    if (!polling) return
    clearTimeout(pollTimer)
    pollTimer = setTimeout(pollDashboard, nextPollDelay())
  }

  async function pollDashboard() {
    await fetchStats()
    schedulePoll()
  }

  async function refreshDashboard() {
    return fetchStats()
  }

  function handleVisibilityChange() {
    if (!document.hidden && polling) {
      clearTimeout(pollTimer)
      pollDashboard()
    }
  }

  function startPolling() {
    if (polling) return
    polling = true
    document.addEventListener('visibilitychange', handleVisibilityChange)
    pollDashboard()
  }

  function stopPolling() {
    polling = false
    clearTimeout(pollTimer)
    pollTimer = null
    document.removeEventListener('visibilitychange', handleVisibilityChange)
  }

  function init() {
    fetchConfig()
    startPolling()
  }

  async function retryTask(taskId) {
    try {
      await tasksApi.retry(taskId)
      return true
    } catch (error) {
      console.error('Failed to retry task:', error)
      return false
    }
  }

  async function fetchFailedTasks() {
    try {
      const response = await tasksApi.listFailed()
      failedTasks.value = response.data.tasks || []
      return true
    } catch (error) {
      console.error('Failed to fetch failed tasks:', error)
      failedTasks.value = []
      return false
    }
  }

  async function retryAllTasks() {
    try {
      const response = await tasksApi.retryAll()
      return response.data.count
    } catch (error) {
      console.error('Failed to retry all tasks:', error)
      return 0
    }
  }

  // Task list dialog methods
  async function fetchTasksByStatus(status = null, page = 1, pageSize = 50) {
    taskListDialog.value.loading = true
    try {
      const response = await tasksApi.listByStatus(status, page, pageSize)
      taskListDialog.value.tasks = response.data.tasks || []
      taskListDialog.value.total = response.data.total || 0
      taskListDialog.value.page = page
      taskListDialog.value.pageSize = pageSize
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
      taskListDialog.value.tasks = []
      taskListDialog.value.total = 0
    } finally {
      taskListDialog.value.loading = false
    }
  }

  function openTaskListDialog(status = null) {
    taskListDialog.value.status = status
    taskListDialog.value.visible = true
    taskListDialog.value.page = 1
    fetchTasksByStatus(status, 1, taskListDialog.value.pageSize)
  }

  function closeTaskListDialog() {
    taskListDialog.value.visible = false
    taskListDialog.value.tasks = []
    taskListDialog.value.total = 0
    taskListDialog.value.page = 1
  }

  return {
    // State
    stats,
    instances,
    queuedTasks,
    runningTasks,
    failedTasks,
    config,
    dataFresh,
    taskListDialog,

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
    updateInstance,
    removeInstance,
    toggleInstance,
    refreshDashboard,
    startPolling,
    stopPolling,
    init,
    fetchFailedTasks,
    retryTask,
    retryAllTasks,
    fetchTasksByStatus,
    openTaskListDialog,
    closeTaskListDialog
  }
})
