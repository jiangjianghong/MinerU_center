<template>
  <div class="panel-container">
    <!-- Panel Header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="header-icon">[</span>
        <span class="header-title">{{ t('queue.title') }}</span>
        <span class="header-icon">]</span>
      </div>
      <div class="header-badges">
        <div class="badge yellow">
          <span class="badge-led"></span>
          <span class="badge-count">{{ queuedTasks.length }}</span>
          <span class="badge-label">{{ t('queue.pending') }}</span>
        </div>
        <div class="badge cyan">
          <span class="badge-led"></span>
          <span class="badge-count">{{ runningTasks.length }}</span>
          <span class="badge-label">{{ t('queue.running') }}</span>
        </div>
      </div>
    </div>

    <!-- Queue Progress -->
    <div class="queue-progress">
      <div class="progress-header">
        <span class="progress-label">&gt; {{ t('queue.queueStatus') }}</span>
        <span class="progress-value">{{ queuedTasks.length + runningTasks.length }} {{ t('queue.active') }}</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill pending" :style="{ width: pendingWidth }">
          <div class="progress-glow"></div>
        </div>
        <div class="progress-fill running" :style="{ width: runningWidth }">
          <div class="progress-glow"></div>
        </div>
        <div class="progress-scan"></div>
      </div>
      <div class="progress-legend">
        <span class="legend-item yellow">{{ t('queue.pending') }}</span>
        <span class="legend-item cyan">{{ t('queue.running') }}</span>
        <span class="legend-item green">{{ t('stats.completed') }}</span>
      </div>
    </div>

    <!-- Tasks Container -->
    <div class="tasks-container">
      <!-- Running Tasks -->
      <div v-if="runningTasks.length > 0" class="task-group">
        <div class="group-header">
          <span class="group-icon">&gt;</span>
          <span class="group-title">{{ t('queue.procActive') }}</span>
          <div class="group-led cyan pulse"></div>
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
          <span class="group-icon">&gt;</span>
          <span class="group-title">{{ t('queue.queueWaiting') }}</span>
          <div class="group-led yellow"></div>
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
        <div class="empty-terminal">
          <div class="terminal-line">
            <span class="prompt">&gt;</span>
            <span class="cmd">queue.status()</span>
          </div>
          <div class="terminal-line output">
            <span class="result">{{ t('queue.empty') }}</span>
          </div>
          <div class="terminal-line">
            <span class="prompt">&gt;</span>
            <span class="cmd">{{ t('queue.waitingForTasks') }}</span>
            <span class="cursor"></span>
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
  background: var(--cyber-panel);
  border: 1px solid var(--border-dim);
  height: calc(100vh - 280px);
  display: flex;
  flex-direction: column;
  position: relative;
}

.panel-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
}

/* Panel Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-dim);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-icon {
  color: var(--neon-cyan);
  font-weight: 700;
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.header-badges {
  display: flex;
  gap: 12px;
}

.badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-dim);
}

.badge.yellow {
  border-color: rgba(255, 255, 0, 0.3);
}

.badge.cyan {
  border-color: rgba(0, 240, 255, 0.3);
}

.badge-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.badge.yellow .badge-led {
  background: var(--neon-yellow);
  box-shadow: 0 0 8px var(--neon-yellow);
}

.badge.cyan .badge-led {
  background: var(--neon-cyan);
  box-shadow: 0 0 8px var(--neon-cyan);
  animation: breathe 1.5s ease-in-out infinite;
}

.badge-count {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  font-weight: 700;
}

.badge.yellow .badge-count { color: var(--neon-yellow); }
.badge.cyan .badge-count { color: var(--neon-cyan); }

.badge-label {
  font-size: 9px;
  letter-spacing: 1px;
  color: var(--text-dim);
}

/* Queue Progress */
.queue-progress {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-dim);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-label {
  font-size: 10px;
  color: var(--neon-green);
  letter-spacing: 1px;
}

.progress-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 12px;
  color: var(--text-secondary);
}

.progress-track {
  height: 6px;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  display: flex;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  position: relative;
  transition: width 0.5s ease;
}

.progress-fill.pending {
  background: var(--neon-yellow);
}

.progress-fill.running {
  background: var(--neon-cyan);
}

.progress-glow {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5));
}

.progress-scan {
  position: absolute;
  top: 0;
  left: 0;
  width: 30%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  animation: h-scan 2s ease-in-out infinite;
}

.progress-legend {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.legend-item {
  font-size: 9px;
  letter-spacing: 1px;
  color: var(--text-dim);
}

.legend-item.yellow { color: var(--neon-yellow); }
.legend-item.cyan { color: var(--neon-cyan); }
.legend-item.green { color: var(--neon-green); }

.legend-item::before {
  content: '■';
  margin-right: 4px;
}

/* Tasks Container */
.tasks-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.task-group {
  margin-bottom: 20px;
}

.task-group:last-child {
  margin-bottom: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--border-dim);
}

.group-icon {
  color: var(--neon-green);
  font-weight: 700;
}

.group-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.group-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-left: auto;
}

.group-led.cyan {
  background: var(--neon-cyan);
  box-shadow: 0 0 8px var(--neon-cyan);
}

.group-led.yellow {
  background: var(--neon-yellow);
  box-shadow: 0 0 8px var(--neon-yellow);
}

.group-led.pulse {
  animation: breathe 1.5s ease-in-out infinite;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-terminal {
  padding: 20px;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  min-width: 300px;
}

.terminal-line {
  font-size: 12px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.terminal-line:last-child {
  margin-bottom: 0;
}

.terminal-line .prompt {
  color: var(--neon-green);
}

.terminal-line .cmd {
  color: var(--text-secondary);
}

.terminal-line.output {
  padding-left: 16px;
}

.terminal-line .result {
  color: var(--neon-yellow);
}

.cursor {
  width: 8px;
  height: 14px;
  background: var(--neon-green);
  animation: blink 1s step-end infinite;
}

/* Transitions */
.task-enter-active,
.task-leave-active {
  transition: all 0.3s ease;
}

.task-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.task-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.task-move {
  transition: transform 0.3s ease;
}
</style>
