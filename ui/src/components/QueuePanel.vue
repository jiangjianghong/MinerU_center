<template>
  <div class="panel-container">
    <!-- Panel Header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="header-icon">📋</span>
        <span class="header-title">{{ t('queue.title') }}</span>
      </div>
      <div class="header-badges">
        <div class="badge pending">
          <span class="badge-dot"></span>
          <span class="badge-count">{{ queuedTasks.length }}</span>
          <span class="badge-label">{{ t('queue.pending') }}</span>
        </div>
        <div class="badge running">
          <span class="badge-dot"></span>
          <span class="badge-count">{{ runningTasks.length }}</span>
          <span class="badge-label">{{ t('queue.running') }}</span>
        </div>
      </div>
    </div>

    <!-- Queue Progress -->
    <div class="queue-progress">
      <div class="progress-header">
        <span class="progress-label">{{ t('queue.queueStatus') }}</span>
        <span class="progress-value">{{ queuedTasks.length + runningTasks.length }} {{ t('queue.active') }}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill pending" :style="{ width: pendingWidth }"></div>
        <div class="progress-fill running" :style="{ width: runningWidth }"></div>
      </div>
      <div class="progress-legend">
        <span class="legend-item pending">
          <span class="legend-dot"></span>
          {{ t('queue.pending') }}
        </span>
        <span class="legend-item running">
          <span class="legend-dot"></span>
          {{ t('queue.running') }}
        </span>
        <span class="legend-item completed">
          <span class="legend-dot"></span>
          {{ t('stats.completed') }}
        </span>
      </div>
    </div>

    <!-- Tasks Container -->
    <div class="tasks-container">
      <!-- Running Tasks -->
      <div v-if="runningTasks.length > 0" class="task-group">
        <div class="group-header">
          <span class="group-icon">⚡</span>
          <span class="group-title">{{ t('queue.procActive') }}</span>
          <div class="group-dot running pulse"></div>
        </div>
        <TransitionGroup name="task" tag="div" class="task-list">
          <TaskCard
            v-for="task in runningTasks"
            :key="task.id"
            :task="task"
            type="running"
          />
        </TransitionGroup>
      </div>

      <!-- Pending Tasks -->
      <div v-if="queuedTasks.length > 0" class="task-group">
        <div class="group-header">
          <span class="group-icon">⏳</span>
          <span class="group-title">{{ t('queue.queueWaiting') }}</span>
          <div class="group-dot pending"></div>
        </div>
        <TransitionGroup name="task" tag="div" class="task-list">
          <TaskCard
            v-for="(task, index) in queuedTasks"
            :key="task.id"
            :task="task"
            :position="index + 1"
            type="pending"
          />
        </TransitionGroup>
      </div>

      <!-- Empty State -->
      <div v-if="queuedTasks.length === 0 && runningTasks.length === 0" class="empty-state">
        <div class="empty-card">
          <div class="empty-icon">📋</div>
          <div class="empty-title">{{ t('queue.empty') }}</div>
          <div class="empty-subtitle">{{ t('queue.waitingForTasks') }}</div>
          <div class="empty-dots">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'
import TaskCard from './TaskCard.vue'

const store = useMainStore()
const { queuedTasks, runningTasks } = storeToRefs(store)
const { t } = useI18n()

const total = computed(() => {
  const pending = queuedTasks.value.length
  const running = runningTasks.value.length
  return Math.max(pending + running, 1)
})

const pendingWidth = computed(() => {
  const pending = queuedTasks.value.length
  return `${(pending / total.value) * 100}%`
})

const runningWidth = computed(() => {
  const running = runningTasks.value.length
  return `${(running / total.value) * 100}%`
})
</script>

<style scoped>
.panel-container {
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  height: calc(100vh - 520px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Panel Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 1.3rem;
}

.header-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
}

.header-badges {
  display: flex;
  gap: 12px;
}

.badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--clay-surface);
  border-radius: 20px;
  box-shadow: var(--shadow-convex-sm);
}

.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.badge.pending .badge-dot {
  background: var(--accent-yellow);
  box-shadow: 0 0 8px var(--accent-yellow);
}

.badge.running .badge-dot {
  background: var(--accent-blue);
  box-shadow: 0 0 8px var(--accent-blue);
  animation: pulseSoft 1.5s ease-in-out infinite;
}

.badge-count {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-main);
}

.badge-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-light);
  letter-spacing: 0.5px;
}

/* Queue Progress */
.queue-progress {
  padding: 20px 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
}

.progress-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-light);
}

.progress-track {
  height: 12px;
  background: var(--clay-surface);
  border-radius: 10px;
  box-shadow: var(--shadow-concave);
  display: flex;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.5s var(--transition-bounce);
  border-radius: 10px;
}

.progress-fill.pending {
  background: linear-gradient(135deg, var(--accent-yellow), #f8d66d);
}

.progress-fill.running {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
}

.progress-legend {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-light);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-item.pending .legend-dot { background: var(--accent-yellow); }
.legend-item.running .legend-dot { background: var(--accent-blue); }
.legend-item.completed .legend-dot { background: var(--accent-green); }

/* Tasks Container */
.tasks-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.task-group {
  margin-bottom: 24px;
}

.task-group:last-child {
  margin-bottom: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 2px dashed rgba(255, 255, 255, 0.2);
}

.group-icon {
  font-size: 1rem;
}

.group-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}

.group-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-left: auto;
}

.group-dot.running {
  background: var(--accent-blue);
  box-shadow: 0 0 10px var(--accent-blue);
}

.group-dot.pending {
  background: var(--accent-yellow);
  box-shadow: 0 0 10px var(--accent-yellow);
}

.group-dot.pulse {
  animation: pulseSoft 1.5s ease-in-out infinite;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 50px;
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px dashed rgba(150, 160, 175, 0.3);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 0.9rem;
  color: var(--text-light);
  margin-bottom: 20px;
}

.empty-dots {
  display: flex;
  gap: 8px;
}

.empty-dots .dot {
  width: 8px;
  height: 8px;
  background: var(--accent-blue);
  border-radius: 50%;
  animation: bounceIn 1.4s ease-in-out infinite;
}

.empty-dots .dot:nth-child(1) { animation-delay: 0s; }
.empty-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.empty-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounceIn {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* Transitions */
.task-enter-active,
.task-leave-active {
  transition: all 0.3s var(--transition-bounce);
}

.task-enter-from {
  opacity: 0;
  transform: translateX(-20px) scale(0.95);
}

.task-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95);
}

.task-move {
  transition: transform 0.3s var(--transition-smooth);
}
</style>
