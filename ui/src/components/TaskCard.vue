<template>
  <div class="task-card" :class="[type, { 'high-priority': task.priority >= 8 }]">
    <!-- Priority Badge -->
    <div class="priority-badge" :class="priorityClass">
      <span class="priority-icon">⚡</span>
      <span class="priority-value">{{ task.priority }}</span>
    </div>

    <!-- Task Info -->
    <div class="task-info">
      <div class="task-header">
        <span class="task-id">{{ task.id.substring(0, 12) }}</span>
        <div class="status-badge" :class="statusClass">
          <span class="status-dot"></span>
          <span class="status-text">{{ task.status.toUpperCase() }}</span>
        </div>
      </div>

      <div class="task-meta">
        <div v-if="position" class="meta-item">
          <span class="meta-icon">📍</span>
          <span class="meta-value highlight-yellow">#{{ position }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-icon">⏱️</span>
          <span class="meta-value">{{ formatTime }}</span>
        </div>
        <div v-if="task.instance_id" class="meta-item">
          <span class="meta-icon">🖥️</span>
          <span class="meta-value highlight-blue">{{ task.instance_id.substring(0, 8) }}</span>
        </div>
      </div>
    </div>

    <!-- Progress Indicator for Running Tasks -->
    <div v-if="type === 'running'" class="task-progress">
      <div class="progress-bar"></div>
    </div>

    <!-- Actions -->
    <div class="task-actions">
      <button
        v-if="type === 'pending'"
        class="cancel-btn"
        @click="cancelTask"
        title="CANCEL"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { tasksApi } from '../api'
import { useI18n } from '../i18n'

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'pending'
  },
  position: {
    type: Number,
    default: null
  }
})

const { t } = useI18n()

const priorityClass = computed(() => {
  if (props.task.priority >= 8) return 'high'
  if (props.task.priority >= 5) return 'medium'
  return 'low'
})

const statusClass = computed(() => {
  switch (props.task.status) {
    case 'running': return 'running'
    case 'completed': return 'success'
    case 'failed':
    case 'timeout': return 'danger'
    case 'cancelled': return 'cancelled'
    default: return 'pending'
  }
})

const formatTime = computed(() => {
  const time = props.task.started_at || props.task.created_at
  if (!time) return '--:--'

  const date = new Date(time)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)

  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  return `${Math.floor(diff / 3600)}h`
})

async function cancelTask() {
  try {
    await tasksApi.cancel(props.task.id)
    ElMessage.success(t('queue.cancelSuccess'))
  } catch (error) {
    ElMessage.error(t('queue.cancelFailed'))
  }
}
</script>

<style scoped>
.task-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--clay-surface);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s var(--transition-smooth);
  overflow: hidden;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.task-card.high-priority {
  background: linear-gradient(90deg, rgba(255, 167, 167, 0.3) 0%, var(--clay-surface) 30%);
  border-color: rgba(255, 167, 167, 0.5);
}

.task-card.pending {
  border-left: 4px solid var(--accent-yellow);
}

.task-card.running {
  border-left: 4px solid var(--accent-blue);
}

/* Priority Badge */
.priority-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: var(--clay-surface);
  border-radius: 12px;
  box-shadow: var(--shadow-convex-sm);
  font-size: 0.8rem;
  font-weight: 700;
  min-width: 50px;
  justify-content: center;
}

.priority-icon {
  font-size: 0.7rem;
}

.priority-badge.low {
  color: var(--text-light);
}

.priority-badge.medium {
  color: var(--accent-yellow-dark);
  background: var(--accent-yellow);
}

.priority-badge.high {
  color: #7a4238;
  background: var(--accent-coral);
  animation: pulseSoft 2s ease-in-out infinite;
}

/* Task Info */
.task-info {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.task-id {
  font-family: monospace;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 0.5px;
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  margin-left: auto;
  border-radius: 12px;
  background: var(--clay-surface);
  box-shadow: var(--shadow-convex-sm);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.pending {
  background: var(--accent-yellow);
}
.status-badge.pending .status-dot {
  background: #a88c30;
  box-shadow: 0 0 6px #a88c30;
}
.status-badge.pending .status-text {
  color: #776530;
}

.status-badge.running {
  background: var(--accent-blue);
}
.status-badge.running .status-dot {
  background: #4a7ab5;
  box-shadow: 0 0 6px #4a7ab5;
  animation: pulseSoft 1.5s ease-in-out infinite;
}
.status-badge.running .status-text {
  color: #3d5a82;
}

.status-badge.success {
  background: var(--accent-green);
}
.status-badge.success .status-dot {
  background: #4a9b6f;
  box-shadow: 0 0 6px #4a9b6f;
}
.status-badge.success .status-text {
  color: #3d6b4f;
}

.status-badge.danger {
  background: var(--accent-coral);
}
.status-badge.danger .status-dot {
  background: #c45a4a;
  box-shadow: 0 0 6px #c45a4a;
}
.status-badge.danger .status-text {
  color: #7a4238;
}

.status-badge.cancelled {
  background: var(--bg-dark);
}
.status-badge.cancelled .status-dot {
  background: var(--text-dim);
}
.status-badge.cancelled .status-text {
  color: var(--text-dim);
}

.status-text {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* Task Meta */
.task-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
}

.meta-icon {
  font-size: 0.7rem;
}

.meta-value {
  color: var(--text-light);
  font-weight: 600;
}

.meta-value.highlight-yellow { 
  color: var(--accent-yellow-dark);
  font-weight: 700;
}
.meta-value.highlight-blue { 
  color: var(--accent-blue-dark);
  font-weight: 700;
}

/* Progress Indicator */
.task-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(168, 198, 233, 0.3);
  border-radius: 0 0 20px 20px;
  overflow: hidden;
}

.progress-bar {
  width: 30%;
  height: 100%;
  background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
  border-radius: 4px;
  animation: progressScan 1.5s ease-in-out infinite;
}

@keyframes progressScan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

/* Actions */
.task-actions {
  flex-shrink: 0;
}

.cancel-btn {
  width: 32px;
  height: 32px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  box-shadow: var(--shadow-convex-sm);
  color: var(--text-light);
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s var(--transition-smooth);
}

.cancel-btn:hover {
  background: var(--accent-coral);
  color: #7a4238;
  transform: scale(1.05);
}

.cancel-btn:active {
  transform: scale(0.95);
  box-shadow: var(--shadow-active);
}
</style>
