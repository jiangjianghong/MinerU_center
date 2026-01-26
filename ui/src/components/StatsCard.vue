<template>
  <div class="stats-container">
    <!-- Stats Grid -->
    <div class="stats-grid">
      <!-- Total Tasks -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-label">{{ t('stats.totalTasks') }}</span>
          <div class="led cyan"></div>
        </div>
        <div class="stat-body">
          <div class="stat-value cyan">{{ animatedTotal }}</div>
          <div class="stat-bar">
            <div class="bar-track">
              <div class="bar-fill cyan" style="width: 100%"></div>
            </div>
          </div>
        </div>
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </div>

      <!-- Pending -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-label">{{ t('stats.pending') }}</span>
          <div class="led yellow"></div>
        </div>
        <div class="stat-body">
          <div class="stat-value yellow">{{ animatedPending }}</div>
          <div class="stat-bar">
            <div class="bar-track">
              <div class="bar-fill yellow" :style="{ width: pendingPercent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </div>

      <!-- Running -->
      <div class="stat-card active">
        <div class="stat-header">
          <span class="stat-label">{{ t('stats.running') }}</span>
          <div class="led green pulse"></div>
        </div>
        <div class="stat-body">
          <div class="stat-value green">{{ animatedRunning }}</div>
          <div class="stat-bar">
            <div class="bar-track">
              <div class="bar-fill green animated" :style="{ width: runningPercent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="scan-line"></div>
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </div>

      <!-- Completed -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-label">{{ t('stats.completed') }}</span>
          <div class="led green"></div>
        </div>
        <div class="stat-body">
          <div class="stat-value green">{{ animatedCompleted }}</div>
          <div class="stat-bar">
            <div class="bar-track">
              <div class="bar-fill green" :style="{ width: completedPercent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </div>

      <!-- Failed -->
      <div class="stat-card" :class="{ alert: animatedFailed > 0 }">
        <div class="stat-header">
          <span class="stat-label">{{ t('stats.failed') }}</span>
          <div class="led" :class="animatedFailed > 0 ? 'red pulse' : 'off'"></div>
        </div>
        <div class="stat-body">
          <div class="stat-value" :class="animatedFailed > 0 ? 'red' : 'dim'">{{ animatedFailed }}</div>
          <div class="stat-bar">
            <div class="bar-track">
              <div class="bar-fill red" :style="{ width: failedPercent + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="corner tl"></div>
        <div class="corner tr"></div>
        <div class="corner bl"></div>
        <div class="corner br"></div>
      </div>
    </div>

    <!-- Instance Status Bar -->
    <div class="instance-bar">
      <div class="bar-title">
        <span class="title-icon">&gt;</span>
        {{ t('stats.instanceStatus') }}
      </div>
      <div class="instance-stats">
        <div class="instance-stat">
          <div class="led green"></div>
          <span class="stat-count">{{ stats.instances.idle }}</span>
          <span class="stat-name">{{ t('stats.idle') }}</span>
        </div>
        <div class="instance-stat">
          <div class="led cyan pulse"></div>
          <span class="stat-count">{{ stats.instances.busy }}</span>
          <span class="stat-name">{{ t('stats.busy') }}</span>
        </div>
        <div class="instance-stat">
          <div class="led off"></div>
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
  gap: 16px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

/* Stat Card */
.stat-card {
  position: relative;
  padding: 16px;
  background: var(--cyber-panel);
  border: 1px solid var(--border-dim);
  transition: all 0.3s ease;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--neon-green-dark), transparent);
}

.stat-card:hover {
  border-color: var(--neon-green-dark);
  box-shadow:
    inset 0 0 30px rgba(0, 255, 159, 0.05),
    0 0 20px rgba(0, 255, 159, 0.1);
}

.stat-card.active {
  border-color: var(--neon-green);
  animation: border-pulse 2s ease-in-out infinite;
}

.stat-card.alert {
  border-color: var(--neon-red);
}

.stat-card.alert::before {
  background: linear-gradient(90deg, var(--neon-red), transparent);
}

/* Corners */
.corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border-style: solid;
  border-color: var(--neon-green-dark);
  border-width: 0;
}

.corner.tl { top: -1px; left: -1px; border-top-width: 2px; border-left-width: 2px; }
.corner.tr { top: -1px; right: -1px; border-top-width: 2px; border-right-width: 2px; }
.corner.bl { bottom: -1px; left: -1px; border-bottom-width: 2px; border-left-width: 2px; }
.corner.br { bottom: -1px; right: -1px; border-bottom-width: 2px; border-right-width: 2px; }

.stat-card:hover .corner {
  border-color: var(--neon-green);
}

/* Scan Line Effect */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-green), transparent);
  animation: scan 2s linear infinite;
  opacity: 0.5;
}

/* Stat Header */
.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-dim);
  letter-spacing: 1px;
}

/* LED */
.led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.led.green {
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green);
}

.led.cyan {
  background: var(--neon-cyan);
  box-shadow: 0 0 8px var(--neon-cyan);
}

.led.yellow {
  background: var(--neon-yellow);
  box-shadow: 0 0 8px var(--neon-yellow);
}

.led.red {
  background: var(--neon-red);
  box-shadow: 0 0 8px var(--neon-red);
}

.led.off {
  background: var(--text-dim);
  box-shadow: none;
}

.led.pulse {
  animation: breathe 1.5s ease-in-out infinite;
}

/* Stat Body */
.stat-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.stat-value.green {
  color: var(--neon-green);
  text-shadow: 0 0 20px var(--neon-green);
}

.stat-value.cyan {
  color: var(--neon-cyan);
  text-shadow: 0 0 20px var(--neon-cyan);
}

.stat-value.yellow {
  color: var(--neon-yellow);
  text-shadow: 0 0 20px var(--neon-yellow);
}

.stat-value.red {
  color: var(--neon-red);
  text-shadow: 0 0 20px var(--neon-red);
}

.stat-value.dim {
  color: var(--text-dim);
  text-shadow: none;
}

/* Progress Bar */
.stat-bar {
  margin-top: 4px;
}

.bar-track {
  height: 4px;
  background: var(--cyber-darker);
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.5s ease;
  position: relative;
}

.bar-fill.green { background: var(--neon-green); box-shadow: 0 0 10px var(--neon-green); }
.bar-fill.cyan { background: var(--neon-cyan); box-shadow: 0 0 10px var(--neon-cyan); }
.bar-fill.yellow { background: var(--neon-yellow); box-shadow: 0 0 10px var(--neon-yellow); }
.bar-fill.red { background: var(--neon-red); box-shadow: 0 0 10px var(--neon-red); }

.bar-fill.animated::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: h-scan 1.5s ease-in-out infinite;
}

/* Instance Bar */
.instance-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: var(--cyber-panel);
  border: 1px solid var(--border-dim);
}

.bar-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: var(--neon-green);
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

.stat-count {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-name {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 1px;
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
    gap: 12px;
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
