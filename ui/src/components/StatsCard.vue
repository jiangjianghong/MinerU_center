<template>
  <div class="stats-container">
    <!-- Stats Grid -->
    <div class="stats-grid">
      <!-- Total Tasks -->
      <div class="stat-card blue clickable" @click="$emit('showAllTasks')" :title="t('taskList.titleAll')">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">{{ t('stats.totalTasks') }}</span>
          <span class="stat-value">{{ animatedTotal }}</span>
        </div>
        <div class="stat-bar">
          <div class="bar-fill" style="width: 100%"></div>
        </div>
      </div>

      <!-- Pending -->
      <div class="stat-card yellow clickable" @click="$emit('showPending')" :title="t('taskList.titlePending')">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">{{ t('stats.pending') }}</span>
          <span class="stat-value">{{ animatedPending }}</span>
        </div>
        <div class="stat-bar">
          <div class="bar-fill" :style="{ width: pendingPercent + '%' }"></div>
        </div>
      </div>

      <!-- Running -->
      <div class="stat-card purple active clickable" @click="$emit('showRunning')" :title="t('taskList.titleRunning')">
        <div class="stat-icon pulse">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">{{ t('stats.running') }}</span>
          <span class="stat-value">{{ animatedRunning }}</span>
        </div>
        <div class="stat-bar">
          <div class="bar-fill animated" :style="{ width: runningPercent + '%' }"></div>
        </div>
      </div>

      <!-- Completed -->
      <div class="stat-card green clickable" @click="$emit('showCompleted')" :title="t('taskList.titleCompleted')">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">{{ t('stats.completed') }}</span>
          <span class="stat-value">{{ animatedCompleted }}</span>
        </div>
        <div class="stat-bar">
          <div class="bar-fill" :style="{ width: completedPercent + '%' }"></div>
        </div>
      </div>

      <!-- Failed -->
      <div
        class="stat-card coral clickable"
        :class="{ alert: animatedFailed > 0 }"
        @click="$emit('showFailed')"
        :title="t('failedTasks.title')"
      >
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-label">{{ t('stats.failed') }}</span>
          <span class="stat-value">{{ animatedFailed }}</span>
        </div>
        <div class="stat-bar">
          <div class="bar-fill" :style="{ width: failedPercent + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Instance Status Bar -->
    <div class="instance-bar clickable" @click="$emit('showInstanceStatus')" title="点击查看实例详情">
      <div class="bar-title">
        <span class="title-icon">📊</span>
        {{ t('stats.instanceStatus') }}
        <span class="click-hint">👆</span>
      </div>
      <div class="instance-stats">
        <div class="instance-stat">
          <span class="stat-dot green"></span>
          <span class="stat-count">{{ stats.instances.idle }}</span>
          <span class="stat-name">{{ t('stats.idle') }}</span>
        </div>
        <div class="instance-stat">
          <span class="stat-dot purple pulse"></span>
          <span class="stat-count">{{ stats.instances.busy }}</span>
          <span class="stat-name">{{ t('stats.busy') }}</span>
        </div>
        <div class="instance-stat">
          <span class="stat-dot gray"></span>
          <span class="stat-count">{{ stats.instances.offline }}</span>
          <span class="stat-name">{{ t('stats.offline') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

defineEmits(['showFailed', 'showInstanceStatus', 'showAllTasks', 'showPending', 'showRunning', 'showCompleted'])

const store = useMainStore()
const { stats } = storeToRefs(store)
const { t } = useI18n()

// Animated values
const animatedTotal = ref(0)
const animatedPending = ref(0)
const animatedRunning = ref(0)
const animatedCompleted = ref(0)
const animatedFailed = ref(0)

// Percentages for progress bars
const pendingPercent = computed(() => {
  if (stats.value.tasks.total === 0) return 0
  return (stats.value.queue.pending / stats.value.tasks.total) * 100
})

const runningPercent = computed(() => {
  if (stats.value.tasks.total === 0) return 0
  return (stats.value.queue.running / stats.value.tasks.total) * 100
})

const completedPercent = computed(() => {
  if (stats.value.tasks.total === 0) return 0
  return (stats.value.tasks.completed / stats.value.tasks.total) * 100
})

const failedPercent = computed(() => {
  if (stats.value.tasks.total === 0) return 0
  return (stats.value.tasks.failed / stats.value.tasks.total) * 100
})

function animateValue(ref, target, duration = 500) {
  const start = ref.value
  const change = target - start
  const startTime = performance.now()

  function update(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeOut = 1 - Math.pow(1 - progress, 3)
    ref.value = Math.round(start + change * easeOut)

    if (progress < 1) {
      requestAnimationFrame(update)
    }
  }

  requestAnimationFrame(update)
}

watch(() => stats.value.tasks.total, (val) => animateValue(animatedTotal, val))
watch(() => stats.value.queue.pending, (val) => animateValue(animatedPending, val))
watch(() => stats.value.queue.running, (val) => animateValue(animatedRunning, val))
watch(() => stats.value.tasks.completed, (val) => animateValue(animatedCompleted, val))
watch(() => stats.value.tasks.failed, (val) => animateValue(animatedFailed, val))

onMounted(() => {
  animatedTotal.value = stats.value.tasks.total
  animatedPending.value = stats.value.queue.pending
  animatedRunning.value = stats.value.queue.running
  animatedCompleted.value = stats.value.tasks.completed
  animatedFailed.value = stats.value.tasks.failed
})
</script>

<style scoped>
.stats-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

/* Stat Card - Claymorphism Style */
.stat-card {
  position: relative;
  padding: 20px;
  background: var(--clay-surface);
  border-radius: 25px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  transition: all 0.3s var(--transition-bounce);
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 25px 25px 0 0;
}

.stat-card.blue::before { background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)); }
.stat-card.yellow::before { background: linear-gradient(90deg, var(--accent-yellow), var(--accent-coral)); }
.stat-card.purple::before { background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)); }
.stat-card.green::before { background: linear-gradient(90deg, var(--accent-green), var(--accent-mint)); }
.stat-card.coral::before { background: linear-gradient(90deg, var(--accent-coral), var(--accent-pink)); }

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-hover);
}

.stat-card.active {
  animation: pulseSoft 2s ease-in-out infinite;
}

.stat-card.alert {
  animation: jelly 0.5s ease;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-5px) scale(1.02);
}

/* Stat Icon */
.stat-icon {
  width: 45px;
  height: 45px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  box-shadow: var(--shadow-convex-sm);
}

.stat-card.blue .stat-icon { background: var(--accent-blue); color: #43658b; }
.stat-card.yellow .stat-icon { background: var(--accent-yellow); color: #7a5c2e; }
.stat-card.purple .stat-icon { background: var(--accent-purple); color: #5a4669; }
.stat-card.green .stat-icon { background: var(--accent-green); color: #3d6b4f; }
.stat-card.coral .stat-icon { background: var(--accent-coral); color: #7a4238; }

.stat-icon svg {
  width: 22px;
  height: 22px;
}

.stat-icon.pulse {
  animation: pulseSoft 1.5s ease-in-out infinite;
}

/* Stat Content */
.stat-content {
  margin-bottom: 12px;
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-light);
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}

/* Progress Bar */
.stat-bar {
  height: 8px;
  border-radius: 8px;
  background: var(--clay-surface);
  box-shadow: var(--shadow-concave);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 8px;
  transition: width 0.5s var(--transition-smooth);
  position: relative;
}

.stat-card.blue .bar-fill { background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)); }
.stat-card.yellow .bar-fill { background: linear-gradient(90deg, var(--accent-yellow), var(--accent-coral)); }
.stat-card.purple .bar-fill { background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)); }
.stat-card.green .bar-fill { background: linear-gradient(90deg, var(--accent-green), var(--accent-mint)); }
.stat-card.coral .bar-fill { background: linear-gradient(90deg, var(--accent-coral), var(--accent-pink)); }

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.3), transparent);
  border-radius: 8px 8px 0 0;
}

.bar-fill.animated {
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
}

/* Instance Bar */
.instance-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--clay-surface);
  border-radius: 25px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  transition: all 0.3s var(--transition-bounce);
}

.instance-bar.clickable {
  cursor: pointer;
}

.instance-bar.clickable:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(167, 139, 250, 0.4);
}

.instance-bar.clickable:active {
  transform: translateY(0);
  box-shadow: var(--shadow-active);
}

.click-hint {
  font-size: 0.9rem;
  opacity: 0.6;
  margin-left: 8px;
  transition: opacity 0.2s ease;
}

.instance-bar.clickable:hover .click-hint {
  opacity: 1;
}

.bar-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}

.title-icon {
  font-size: 1.2rem;
}

.instance-stats {
  display: flex;
  gap: 32px;
}

.instance-stat {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-dot.green { background: var(--accent-green); }
.stat-dot.purple { background: var(--accent-purple); }
.stat-dot.gray { background: var(--text-dim); }

.stat-dot.pulse {
  animation: pulseSoft 1.5s ease-in-out infinite;
}

.stat-count {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-main);
}

.stat-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-light);
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .instance-bar {
    flex-direction: column;
    gap: 16px;
  }

  .instance-stats {
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
