<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="$emit('update:visible', false)">
        <div class="modal-content">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-title">
              <span class="title-icon">📊</span>
              <span>{{ t('stats.instanceStatus') }}</span>
            </div>
            <button class="close-btn" @click="$emit('update:visible', false)">×</button>
          </div>

          <!-- Modal Body -->
          <div class="modal-body">
            <!-- Arrow Visualization -->
            <div class="arrow-container">
              <!-- Instance Arrows (Left Side) -->
              <div class="instances-side">
                <div
                  v-for="(instance, index) in instances"
                  :key="instance.id"
                  class="instance-row"
                  :class="instance.status"
                >
                  <!-- Instance Info -->
                  <div class="instance-info">
                    <div class="instance-name">
                      <span class="node-label">节点</span>
                      <span class="node-number">{{ String(index + 1).padStart(2, '0') }}</span>
                    </div>
                    <div class="instance-details">
                      <span class="instance-url">{{ instance.name }}</span>
                      <span class="status-tag" :class="instance.status">
                        {{ instance.status.toUpperCase() }}
                      </span>
                    </div>
                    <!-- Current Task File -->
                    <div v-if="instance.current_task_id" class="current-task">
                      <span class="task-icon">📄</span>
                      <span class="task-file">{{ getTaskFileName(instance) }}</span>
                    </div>
                  </div>

                  <!-- Arrow -->
                  <div class="arrow-line" :class="{ active: instance.status === 'busy' }">
                    <svg class="arrow-svg" viewBox="0 0 120 40" preserveAspectRatio="none">
                      <defs>
                        <linearGradient :id="'arrowGrad-' + index" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" :stop-color="getStatusColor(instance.status)" />
                          <stop offset="100%" stop-color="#a78bfa" />
                        </linearGradient>
                      </defs>
                      <path
                        :d="getArrowPath(index)"
                        :stroke="'url(#arrowGrad-' + index + ')'"
                        stroke-width="6"
                        fill="none"
                        stroke-linecap="round"
                        :class="{ flowing: instance.status === 'busy' }"
                      />
                      <!-- Arrow head -->
                      <polygon
                        :points="getArrowHead(index)"
                        :fill="'#a78bfa'"
                        :class="{ flowing: instance.status === 'busy' }"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              <!-- Center Hub -->
              <div class="center-hub">
                <div class="hub-circle">
                  <div class="hub-inner">
                    <span class="hub-icon">⚡</span>
                    <span class="hub-text">调度中心</span>
                  </div>
                </div>
                <div class="hub-stats">
                  <div class="hub-stat">
                    <span class="stat-value">{{ busyCount }}</span>
                    <span class="stat-label">运行中</span>
                  </div>
                  <div class="hub-stat">
                    <span class="stat-value">{{ idleCount }}</span>
                    <span class="stat-label">空闲</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="instances.length === 0" class="empty-state">
              <div class="empty-icon">🖥️</div>
              <p class="empty-text">暂无实例</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:visible'])

const store = useMainStore()
const { instances, runningTasks } = storeToRefs(store)
const { t } = useI18n()

const busyCount = computed(() => instances.value.filter(i => i.status === 'busy').length)
const idleCount = computed(() => instances.value.filter(i => i.status === 'idle' && i.enabled).length)

function getStatusColor(status) {
  const colors = {
    idle: '#86efac',
    busy: '#c4b5fd',
    error: '#fca5a5',
    offline: '#9ca3af'
  }
  return colors[status] || '#9ca3af'
}

function getTaskFileName(instance) {
  if (!instance.current_task_id) return ''

  // Try to find the running task and extract filename
  const task = runningTasks.value.find(t => t.task_id === instance.current_task_id)
  if (task && task.payload) {
    // Try to extract filename from payload
    if (task.payload.file) {
      const parts = task.payload.file.split(/[/\\]/)
      return parts[parts.length - 1]
    }
    if (task.payload.filename) {
      return task.payload.filename
    }
    if (task.payload.path) {
      const parts = task.payload.path.split(/[/\\]/)
      return parts[parts.length - 1]
    }
  }
  // Fallback to showing task ID
  return instance.current_task_id.substring(0, 12) + '...'
}

function getArrowPath(index) {
  const total = instances.value.length
  if (total === 0) return 'M 0,20 L 120,20'

  // Calculate curve based on position
  const normalizedIndex = total === 1 ? 0.5 : index / (total - 1)
  const curveOffset = (normalizedIndex - 0.5) * 30

  return `M 0,20 Q 60,${20 + curveOffset} 110,20`
}

function getArrowHead(index) {
  return '105,14 120,20 105,26'
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(224, 229, 236, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Modal Content */
.modal-content {
  position: relative;
  width: 95%;
  max-width: 900px;
  max-height: 85vh;
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-main);
}

.title-icon {
  font-size: 1.4rem;
}

.close-btn {
  width: 40px;
  height: 40px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  box-shadow: var(--shadow-convex-sm);
  color: var(--text-light);
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s var(--transition-smooth);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--accent-coral);
  color: #7a4238;
}

/* Modal Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Arrow Container */
.arrow-container {
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 300px;
}

/* Instances Side */
.instances-side {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Instance Row */
.instance-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--clay-surface);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.3s ease;
}

.instance-row:hover {
  transform: translateX(5px);
  box-shadow: var(--shadow-hover);
}

.instance-row.busy {
  border-color: rgba(167, 139, 250, 0.4);
  background: linear-gradient(135deg, var(--clay-surface), rgba(167, 139, 250, 0.1));
}

.instance-row.idle {
  border-color: rgba(134, 239, 172, 0.4);
}

.instance-row.error {
  border-color: rgba(252, 165, 165, 0.4);
}

.instance-row.offline {
  border-color: rgba(156, 163, 175, 0.4);
  opacity: 0.7;
}

/* Instance Info */
.instance-info {
  flex: 1;
  min-width: 0;
}

.instance-name {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 6px;
}

.node-label {
  font-size: 0.75rem;
  color: var(--text-light);
  font-weight: 600;
}

.node-number {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-main);
}

.instance-details {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.instance-url {
  font-size: 0.85rem;
  color: var(--text-light);
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.status-tag.idle {
  background: var(--accent-green);
  color: #3d6b4f;
}

.status-tag.busy {
  background: var(--accent-purple);
  color: #5a4669;
}

.status-tag.error {
  background: var(--accent-coral);
  color: #7a4238;
}

.status-tag.offline {
  background: var(--bg-dark);
  color: var(--text-dim);
}

/* Current Task */
.current-task {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.15);
  border-radius: 12px;
  margin-top: 8px;
}

.task-icon {
  font-size: 0.9rem;
}

.task-file {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent-purple-dark);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Arrow Line */
.arrow-line {
  width: 120px;
  height: 40px;
  flex-shrink: 0;
}

.arrow-svg {
  width: 100%;
  height: 100%;
}

.arrow-svg path {
  transition: stroke-width 0.3s ease;
}

.arrow-svg path.flowing {
  animation: flowPulse 1.5s ease-in-out infinite;
}

.arrow-svg polygon.flowing {
  animation: arrowPulse 1.5s ease-in-out infinite;
}

@keyframes flowPulse {
  0%, 100% {
    stroke-width: 6;
    opacity: 1;
  }
  50% {
    stroke-width: 8;
    opacity: 0.8;
  }
}

@keyframes arrowPulse {
  0%, 100% {
    transform: translateX(0);
    opacity: 1;
  }
  50% {
    transform: translateX(3px);
    opacity: 0.8;
  }
}

/* Center Hub */
.center-hub {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  flex-shrink: 0;
}

.hub-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 10px 30px rgba(167, 139, 250, 0.4),
    inset 0 2px 10px rgba(255, 255, 255, 0.3);
  animation: hubPulse 3s ease-in-out infinite;
}

@keyframes hubPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow:
      0 10px 30px rgba(167, 139, 250, 0.4),
      inset 0 2px 10px rgba(255, 255, 255, 0.3);
  }
  50% {
    transform: scale(1.03);
    box-shadow:
      0 15px 40px rgba(167, 139, 250, 0.5),
      inset 0 2px 10px rgba(255, 255, 255, 0.4);
  }
}

.hub-inner {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  background: var(--clay-surface);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-shadow: var(--shadow-concave);
}

.hub-icon {
  font-size: 2rem;
}

.hub-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-main);
}

.hub-stats {
  display: flex;
  gap: 24px;
}

.hub-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.hub-stat .stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
}

.hub-stat .stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-light);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  gap: 16px;
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.1rem;
  color: var(--text-light);
  font-weight: 600;
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s var(--transition-smooth);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9) translateY(20px);
}

/* Responsive */
@media (max-width: 768px) {
  .arrow-container {
    flex-direction: column;
  }

  .instances-side {
    width: 100%;
  }

  .arrow-line {
    width: 60px;
    transform: rotate(90deg);
  }

  .center-hub {
    margin-top: 20px;
  }
}
</style>
