<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click.self="$emit('update:visible', false)">
      <div class="dialog-container">
        <!-- Header -->
        <div class="dialog-header">
          <div class="header-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            </span>
            <span>{{ t('failedTasks.title') }}</span>
            <span class="task-count">({{ failedTasks.length }})</span>
          </div>
          <div class="header-actions">
            <button
              v-if="failedTasks.length > 0"
              class="retry-all-btn"
              @click="handleRetryAll"
              :disabled="retrying"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              {{ t('failedTasks.retryAll') }}
            </button>
            <button class="close-btn" @click="$emit('update:visible', false)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="dialog-content">
          <div v-if="failedTasks.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <span>{{ t('failedTasks.empty') }}</span>
          </div>

          <div v-else class="task-list">
            <div
              v-for="task in failedTasks"
              :key="task.id"
              class="task-item"
            >
              <div class="task-main">
                <div class="task-id">
                  <span class="id-label">ID:</span>
                  <span class="id-value">{{ task.id.slice(0, 8) }}...</span>
                </div>
                <div class="task-error">
                  <span class="error-label">{{ t('failedTasks.error') }}:</span>
                  <span class="error-value">{{ task.error || 'Unknown error' }}</span>
                </div>
                <div class="task-meta">
                  <span class="meta-item">
                    <span class="meta-label">{{ t('failedTasks.retryCount') }}:</span>
                    <span class="meta-value">{{ task.retry_count }} {{ t('failedTasks.times') }}</span>
                  </span>
                  <span class="meta-item">
                    <span class="meta-label">{{ t('failedTasks.failedAt') }}:</span>
                    <span class="meta-value">{{ formatTime(task.completed_at) }}</span>
                  </span>
                </div>
                <div v-if="task.payload" class="task-payload">
                  <span class="payload-label">{{ t('failedTasks.payload') }}:</span>
                  <code class="payload-value">{{ formatPayload(task.payload) }}</code>
                </div>
              </div>
              <div class="task-actions">
                <button
                  class="retry-btn"
                  @click="handleRetry(task.id)"
                  :disabled="retrying"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 4v6h-6M1 20v-6h6"/>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                  </svg>
                  {{ t('failedTasks.retry') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['update:visible'])

const store = useMainStore()
const { failedTasks } = storeToRefs(store)
const { t } = useI18n()

const retrying = ref(false)

function formatTime(isoString) {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString()
}

function formatPayload(payload) {
  if (!payload) return '{}'
  try {
    return JSON.stringify(payload, null, 2).slice(0, 200)
  } catch {
    return String(payload).slice(0, 200)
  }
}

async function handleRetry(taskId) {
  retrying.value = true
  const success = await store.retryTask(taskId)
  retrying.value = false
  if (success) {
    // Task will be removed from failed list via WebSocket update
  }
}

async function handleRetryAll() {
  retrying.value = true
  const count = await store.retryAllTasks()
  retrying.value = false
  if (count > 0) {
    // Tasks will be removed from failed list via WebSocket update
  }
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
  max-width: 700px;
  max-height: 80vh;
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
  background: linear-gradient(135deg, var(--accent-coral) 0%, var(--accent-pink) 100%);
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

.retry-all-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-all-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.retry-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.retry-all-btn svg {
  width: 16px;
  height: 16px;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-light);
  gap: 16px;
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

.empty-state span {
  font-size: 1rem;
  font-weight: 600;
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: var(--clay-surface);
  border-radius: 20px;
  border: 2px solid rgba(163, 177, 198, 0.2);
  box-shadow: var(--shadow-concave);
}

.task-main {
  flex: 1;
  min-width: 0;
}

.task-id {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.id-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-light);
}

.id-value {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
}

.task-error {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.error-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--accent-coral);
}

.error-value {
  font-size: 0.85rem;
  color: var(--text-main);
  word-break: break-word;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-light);
}

.meta-value {
  font-size: 0.8rem;
  color: var(--text-main);
}

.task-payload {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.payload-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-light);
}

.payload-value {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  background: rgba(163, 177, 198, 0.15);
  padding: 8px 12px;
  border-radius: 10px;
  color: var(--text-main);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 80px;
  overflow-y: auto;
}

.task-actions {
  flex-shrink: 0;
}

.retry-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--accent-blue);
  border: none;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s ease;
}

.retry-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.retry-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.retry-btn svg {
  width: 14px;
  height: 14px;
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
</style>
