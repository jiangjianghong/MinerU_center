<template>
  <Teleport to="body">
    <div v-if="taskListDialog.visible" class="dialog-overlay" @click.self="store.closeTaskListDialog()">
      <div class="dialog-container">
        <!-- Header -->
        <div class="dialog-header" :class="headerClass">
          <div class="header-title">
            <span class="title-icon">
              <svg v-if="taskListDialog.status === null" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <svg v-else-if="taskListDialog.status === 'pending'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <svg v-else-if="taskListDialog.status === 'running'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </span>
            <span>{{ dialogTitle }}</span>
            <span class="task-count">({{ taskListDialog.total }})</span>
          </div>
          <div class="header-actions">
            <button class="close-btn" @click="store.closeTaskListDialog()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="dialog-content">
          <!-- Loading -->
          <div v-if="taskListDialog.loading" class="loading-state">
            <div class="loading-spinner"></div>
            <span>{{ t('taskList.loading') }}</span>
          </div>

          <!-- Empty State -->
          <div v-else-if="taskListDialog.tasks.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <span>{{ t('taskList.empty') }}</span>
          </div>

          <!-- Task List -->
          <div v-else class="task-list">
            <div
              v-for="(task, index) in taskListDialog.tasks"
              :key="task.task_id"
              class="task-item"
            >
              <div class="task-main">
                <!-- Row 1: ID and Status -->
                <div class="task-row">
                  <div class="task-id">
                    <span class="label">ID:</span>
                    <span class="value mono">{{ task.task_id.slice(0, 8) }}...</span>
                  </div>
                  <div class="task-status" :class="getStatusClass(task.status)">
                    {{ t(`status.${task.status}`) }}
                  </div>
                </div>

                <!-- Row 2: File Name -->
                <div class="task-file" v-if="task.file_name">
                  <span class="label">{{ t('taskList.fileName') }}:</span>
                  <span class="value">{{ task.file_name }}</span>
                </div>

                <!-- Row 3: Meta Info based on status -->
                <div class="task-meta">
                  <!-- All/Completed: show priority, created_at, duration -->
                  <template v-if="taskListDialog.status === null || taskListDialog.status === 'completed'">
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.priority') }}:</span>
                      <span class="value priority-badge" :class="getPriorityClass(task.priority)">
                        P{{ task.priority }}
                      </span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.createdAt') }}:</span>
                      <span class="value">{{ formatTime(task.created_at) }}</span>
                    </span>
                    <span class="meta-item" v-if="task.duration">
                      <span class="label">{{ t('taskList.duration') }}:</span>
                      <span class="value">{{ formatDuration(task.duration) }}</span>
                    </span>
                    <span class="meta-item" v-if="task.instance_name">
                      <span class="label">{{ t('taskList.instance') }}:</span>
                      <span class="value">{{ task.instance_name }}</span>
                    </span>
                  </template>

                  <!-- Pending: show position, priority, wait time -->
                  <template v-else-if="taskListDialog.status === 'pending'">
                    <span class="meta-item highlight">
                      <span class="label">{{ t('taskList.position') }}:</span>
                      <span class="value position-badge">
                        {{ t('taskList.positionAhead', { n: task.position }) }}
                      </span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.priority') }}:</span>
                      <span class="value priority-badge" :class="getPriorityClass(task.priority)">
                        P{{ task.priority }}
                      </span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.requestedAt') }}:</span>
                      <span class="value">{{ formatTime(task.created_at) }}</span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.waitTime') }}:</span>
                      <span class="value">{{ getWaitTime(task.created_at) }}</span>
                    </span>
                  </template>

                  <!-- Running: show instance, started_at, processing time, retry -->
                  <template v-else-if="taskListDialog.status === 'running'">
                    <span class="meta-item highlight" v-if="task.instance_name">
                      <span class="label">{{ t('taskList.instance') }}:</span>
                      <span class="value instance-badge">{{ task.instance_name }}</span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.startedAt') }}:</span>
                      <span class="value">{{ formatTime(task.started_at) }}</span>
                    </span>
                    <span class="meta-item">
                      <span class="label">{{ t('taskList.processingTime') }}:</span>
                      <span class="value">{{ getWaitTime(task.started_at) }}</span>
                    </span>
                    <span class="meta-item" v-if="task.retry_count > 0">
                      <span class="label">{{ t('taskList.retryCount') }}:</span>
                      <span class="value">{{ task.retry_count }} {{ t('config.times') }}</span>
                    </span>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="dialog-footer" v-if="taskListDialog.total > taskListDialog.pageSize">
          <div class="pagination">
            <button
              class="page-btn"
              :disabled="taskListDialog.page <= 1"
              @click="changePage(taskListDialog.page - 1)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <span class="page-info">
              {{ taskListDialog.page }} / {{ totalPages }}
            </span>
            <button
              class="page-btn"
              :disabled="taskListDialog.page >= totalPages"
              @click="changePage(taskListDialog.page + 1)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

const store = useMainStore()
const { taskListDialog } = storeToRefs(store)
const { t } = useI18n()

const dialogTitle = computed(() => {
  switch (taskListDialog.value.status) {
    case null:
      return t('taskList.titleAll')
    case 'pending':
      return t('taskList.titlePending')
    case 'running':
      return t('taskList.titleRunning')
    case 'completed':
      return t('taskList.titleCompleted')
    default:
      return t('taskList.titleAll')
  }
})

const headerClass = computed(() => {
  switch (taskListDialog.value.status) {
    case null:
      return 'header-all'
    case 'pending':
      return 'header-pending'
    case 'running':
      return 'header-running'
    case 'completed':
      return 'header-completed'
    default:
      return 'header-all'
  }
})

const totalPages = computed(() => {
  return Math.ceil(taskListDialog.value.total / taskListDialog.value.pageSize)
})

function formatTime(isoString) {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString()
}

function formatDuration(seconds) {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const mins = Math.floor(seconds / 60)
  const secs = (seconds % 60).toFixed(0)
  return `${mins}m ${secs}s`
}

function getWaitTime(isoString) {
  if (!isoString) return '-'
  const created = new Date(isoString)
  const now = new Date()
  const seconds = Math.floor((now - created) / 1000)
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${mins}m`
}

function getStatusClass(status) {
  return {
    'status-pending': status === 'pending',
    'status-running': status === 'running',
    'status-completed': status === 'completed',
    'status-failed': status === 'failed' || status === 'timeout',
    'status-cancelled': status === 'cancelled'
  }
}

function getPriorityClass(priority) {
  if (priority >= 8) return 'priority-high'
  if (priority >= 5) return 'priority-medium'
  return 'priority-low'
}

function changePage(page) {
  store.fetchTasksByStatus(
    taskListDialog.value.status,
    page,
    taskListDialog.value.pageSize
  )
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-container {
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid rgba(163, 177, 198, 0.2);
}

.dialog-header.header-all {
  background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
}

.dialog-header.header-pending {
  background: linear-gradient(135deg, var(--accent-yellow) 0%, var(--accent-coral) 100%);
}

.dialog-header.header-running {
  background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-pink) 100%);
}

.dialog-header.header-completed {
  background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-mint) 100%);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.7);
}

.title-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-icon svg {
  width: 24px;
  height: 24px;
}

.task-count {
  font-size: 0.9rem;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.4);
  color: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.close-btn svg {
  width: 18px;
  height: 18px;
}

/* Content */
.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-light);
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(163, 177, 198, 0.3);
  border-top-color: var(--accent-purple);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--accent-green);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.5);
}

.empty-icon svg {
  width: 32px;
  height: 32px;
}

.empty-state span,
.loading-state span {
  font-size: 1rem;
  font-weight: 600;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 16px 20px;
  background: var(--clay-surface);
  border-radius: 20px;
  border: 2px solid rgba(163, 177, 198, 0.2);
  box-shadow: var(--shadow-concave);
  transition: all 0.2s ease;
}

.task-item:hover {
  border-color: rgba(167, 139, 250, 0.3);
}

.task-main {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-id {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-file {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.task-file .value {
  font-weight: 600;
  color: var(--text-main);
  word-break: break-all;
}

.label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-light);
}

.value {
  font-size: 0.85rem;
  color: var(--text-main);
}

.value.mono {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

/* Status Badge */
.task-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-pending {
  background: var(--accent-yellow);
  color: rgba(0, 0, 0, 0.6);
}

.status-running {
  background: var(--accent-purple);
  color: rgba(0, 0, 0, 0.6);
}

.status-completed {
  background: var(--accent-green);
  color: rgba(0, 0, 0, 0.6);
}

.status-failed {
  background: var(--accent-coral);
  color: rgba(0, 0, 0, 0.6);
}

.status-cancelled {
  background: var(--text-dim);
  color: white;
}

/* Meta Info */
.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(163, 177, 198, 0.2);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item.highlight .value {
  font-weight: 700;
}

/* Priority Badge */
.priority-badge {
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.priority-high {
  background: var(--accent-coral);
  color: rgba(0, 0, 0, 0.6);
}

.priority-medium {
  background: var(--accent-yellow);
  color: rgba(0, 0, 0, 0.6);
}

.priority-low {
  background: var(--accent-blue);
  color: rgba(0, 0, 0, 0.6);
}

/* Position Badge */
.position-badge {
  padding: 2px 10px;
  border-radius: 10px;
  background: var(--accent-purple);
  color: rgba(0, 0, 0, 0.6);
  font-weight: 700;
}

/* Instance Badge */
.instance-badge {
  padding: 2px 10px;
  border-radius: 10px;
  background: var(--accent-blue);
  color: rgba(0, 0, 0, 0.6);
  font-weight: 700;
}

/* Footer / Pagination */
.dialog-footer {
  padding: 16px 24px;
  border-top: 2px solid rgba(163, 177, 198, 0.2);
  display: flex;
  justify-content: center;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--clay-surface);
  border: 2px solid rgba(163, 177, 198, 0.3);
  box-shadow: var(--shadow-convex-sm);
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-info {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  min-width: 80px;
  text-align: center;
}

/* Scrollbar */
.dialog-content::-webkit-scrollbar {
  width: 8px;
}

.dialog-content::-webkit-scrollbar-track {
  background: transparent;
}

.dialog-content::-webkit-scrollbar-thumb {
  background: rgba(163, 177, 198, 0.4);
  border-radius: 4px;
}

.dialog-content::-webkit-scrollbar-thumb:hover {
  background: rgba(163, 177, 198, 0.6);
}

/* Responsive */
@media (max-width: 600px) {
  .task-meta {
    flex-direction: column;
    gap: 8px;
  }

  .task-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
