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
        <span class="task-label">TASK_ID:</span>
        <span class="task-id">{{ task.id.substring(0, 12) }}</span>
        <div class="status-badge" :class="statusClass">
          <span class="status-led"></span>
          <span class="status-text">{{ task.status.toUpperCase() }}</span>
        </div>
      </div>

      <div class="task-meta">
        <div v-if="position" class="meta-item">
          <span class="meta-label">POS:</span>
          <span class="meta-value yellow">#{{ position }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">TIME:</span>
          <span class="meta-value">{{ formatTime }}</span>
        </div>
        <div v-if="task.instance_id" class="meta-item">
          <span class="meta-label">NODE:</span>
          <span class="meta-value cyan">{{ task.instance_id.substring(0, 8) }}</span>
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

    <!-- Status Line -->
    <div class="status-line" :class="type"></div>
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
  gap: 12px;
  padding: 12px 14px;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  transition: all 0.2s ease;
}

.task-card:hover {
  border-color: var(--neon-green-dark);
  box-shadow:
    inset 0 0 20px rgba(0, 255, 159, 0.03),
    0 0 10px rgba(0, 255, 159, 0.1);
}

.task-card.high-priority {
  background: linear-gradient(90deg, rgba(255, 0, 64, 0.1) 0%, var(--cyber-darker) 30%);
}

/* Status Line */
.status-line {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}

.status-line.pending {
  background: var(--neon-yellow);
  box-shadow: 0 0 10px var(--neon-yellow);
}

.status-line.running {
  background: var(--neon-cyan);
  box-shadow: 0 0 10px var(--neon-cyan);
  animation: pulse-glow 1.5s ease-in-out infinite;
}

/* Priority Badge */
.priority-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(128, 128, 144, 0.1);
  border: 1px solid var(--border-dim);
  font-size: 11px;
  font-weight: 600;
  min-width: 50px;
  justify-content: center;
}

.priority-icon {
  font-size: 10px;
}

.priority-badge.low {
  color: var(--text-dim);
  border-color: var(--text-dim);
}

.priority-badge.medium {
  color: var(--neon-yellow);
  border-color: rgba(255, 255, 0, 0.3);
  background: rgba(255, 255, 0, 0.05);
}

.priority-badge.high {
  color: var(--neon-red);
  border-color: rgba(255, 0, 64, 0.3);
  background: rgba(255, 0, 64, 0.1);
  animation: flicker 3s infinite;
}

/* Task Info */
.task-info {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.task-label {
  font-size: 9px;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.task-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  margin-left: auto;
  border: 1px solid var(--border-dim);
}

.status-led {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--text-dim);
}

.status-badge.pending {
  border-color: rgba(255, 255, 0, 0.3);
}
.status-badge.pending .status-led {
  background: var(--neon-yellow);
  box-shadow: 0 0 6px var(--neon-yellow);
}
.status-badge.pending .status-text {
  color: var(--neon-yellow);
}

.status-badge.running {
  border-color: rgba(0, 240, 255, 0.3);
}
.status-badge.running .status-led {
  background: var(--neon-cyan);
  box-shadow: 0 0 6px var(--neon-cyan);
  animation: breathe 1.5s ease-in-out infinite;
}
.status-badge.running .status-text {
  color: var(--neon-cyan);
}

.status-badge.success {
  border-color: rgba(0, 255, 159, 0.3);
}
.status-badge.success .status-led {
  background: var(--neon-green);
  box-shadow: 0 0 6px var(--neon-green);
}
.status-badge.success .status-text {
  color: var(--neon-green);
}

.status-badge.danger {
  border-color: rgba(255, 0, 64, 0.3);
}
.status-badge.danger .status-led {
  background: var(--neon-red);
  box-shadow: 0 0 6px var(--neon-red);
}
.status-badge.danger .status-text {
  color: var(--neon-red);
}

.status-text {
  font-size: 8px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-dim);
}

/* Task Meta */
.task-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
}

.meta-label {
  color: var(--text-dim);
  letter-spacing: 0.5px;
}

.meta-value {
  color: var(--text-secondary);
  font-family: 'JetBrains Mono', monospace;
}

.meta-value.yellow { color: var(--neon-yellow); }
.meta-value.cyan { color: var(--neon-cyan); }

/* Progress Indicator */
.task-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(0, 240, 255, 0.1);
  overflow: hidden;
}

.progress-bar {
  width: 30%;
  height: 100%;
  background: var(--neon-cyan);
  box-shadow: 0 0 10px var(--neon-cyan);
  animation: h-scan 1.5s ease-in-out infinite;
}

/* Actions */
.task-actions {
  flex-shrink: 0;
}

.cancel-btn {
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid var(--border-dim);
  color: var(--text-dim);
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  border-color: var(--neon-red);
  color: var(--neon-red);
  box-shadow: 0 0 10px rgba(255, 0, 64, 0.3);
}

.cancel-btn:active {
  transform: translateY(1px);
}
</style>
