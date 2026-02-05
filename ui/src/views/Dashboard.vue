<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="clay-header">
      <div class="header-left">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <div class="logo-text">
            <h1>{{ t('dashboard.title') }}</h1>
            <p>{{ t('dashboard.subtitle') }}</p>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="time-display">
          <span class="time-icon">🕐</span>
          <span class="time-value">{{ currentTime }}</span>
        </div>
      </div>

      <div class="header-right">
        <!-- Connection Status -->
        <div class="status-pill" :class="{ connected: wsConnected }">
          <span class="status-dot"></span>
          <span class="status-text">{{ wsConnected ? t('dashboard.linkOk') : t('dashboard.offline') }}</span>
        </div>

        <!-- Action Buttons -->
        <button class="clay-btn-icon" @click="toggleLocale" :title="locale === 'zh' ? 'English' : '中文'">
          {{ locale === 'zh' ? '中' : 'EN' }}
        </button>

        <button class="clay-btn-icon" @click="showConfig = true" :title="t('common.config')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>

        <button class="clay-btn-icon" @click="refresh" :class="{ spinning: isRefreshing }" :title="t('common.refresh')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Stats Overview -->
      <section class="stats-section">
        <StatsCard @showFailed="showFailedTasks = true" @showInstanceStatus="showInstanceStatus = true" />
      </section>

      <!-- Two Column Layout -->
      <div class="content-grid">
        <section class="instances-section">
          <InstancePanel />
        </section>

        <section class="queue-section">
          <QueuePanel />
        </section>
      </div>
    </main>

    <!-- Footer -->
    <footer class="clay-footer">
      <div class="footer-left">
        <span class="footer-item">
          <span class="status-dot success"></span>
          {{ t('dashboard.sysReady') }}
        </span>
      </div>
      <div class="footer-right">
        <span class="footer-item">{{ t('dashboard.mem') }}: 64%</span>
        <span class="footer-item">{{ t('dashboard.cpu') }}: 23%</span>
        <span class="footer-item">{{ t('dashboard.net') }}: OK</span>
      </div>
    </footer>

    <!-- Config Dialog -->
    <ConfigPanel v-model:visible="showConfig" />

    <!-- Failed Tasks Dialog -->
    <FailedTasksDialog v-model:visible="showFailedTasks" />

    <!-- Instance Status Dialog -->
    <InstanceStatusDialog v-model:visible="showInstanceStatus" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'
import StatsCard from '../components/StatsCard.vue'
import InstancePanel from '../components/InstancePanel.vue'
import QueuePanel from '../components/QueuePanel.vue'
import ConfigPanel from '../components/ConfigPanel.vue'
import FailedTasksDialog from '../components/FailedTasksDialog.vue'
import InstanceStatusDialog from '../components/InstanceStatusDialog.vue'

const store = useMainStore()
const { wsConnected } = storeToRefs(store)
const { t, locale, toggleLocale } = useI18n()

const showConfig = ref(false)
const showFailedTasks = ref(false)
const showInstanceStatus = ref(false)
const isRefreshing = ref(false)
const currentTime = ref('')

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
}

function refresh() {
  isRefreshing.value = true
  store.fetchStats()
  store.fetchInstances()
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}

let timeInterval

onMounted(() => {
  store.init()
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  store.disconnectWebSocket()
  clearInterval(timeInterval)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
}

/* ============================================
   HEADER - Claymorphism Style
   ============================================ */
.clay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: var(--clay-surface);
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 8px 20px rgba(163, 177, 198, 0.4),
    inset 0 -2px 5px rgba(163, 177, 198, 0.2),
    inset 0 2px 5px rgba(255, 255, 255, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Logo */
.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-convex-sm);
}

.logo-icon svg {
  width: 28px;
  height: 28px;
}

.logo-text h1 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
  letter-spacing: -0.02em;
}

.logo-text p {
  font-size: 0.85rem;
  color: var(--text-light);
  margin: 0;
}

/* Time Display */
.time-display {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: var(--clay-surface);
  border-radius: 25px;
  box-shadow: var(--shadow-concave);
}

.time-icon {
  font-size: 1.1rem;
}

.time-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 1px;
}

/* Header Right */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Status Pill */
.status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: var(--accent-coral);
  border-radius: 25px;
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.3s ease;
}

.status-pill.connected {
  background: var(--accent-green);
}

.status-pill .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  animation: pulseSoft 2s ease-in-out infinite;
}

.status-pill .status-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.6);
}

/* Icon Buttons */
.clay-btn-icon {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex-sm);
  color: var(--text-main);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.2s var(--transition-smooth);
}

.clay-btn-icon svg {
  width: 20px;
  height: 20px;
}

.clay-btn-icon:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.clay-btn-icon:active {
  transform: translateY(0);
  box-shadow: var(--shadow-active);
}

.clay-btn-icon.spinning svg {
  animation: spin 1s linear infinite;
}

/* ============================================
   MAIN CONTENT
   ============================================ */
.main-content {
  flex: 1;
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.stats-section {
  margin-bottom: 32px;
}

.content-grid {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 32px;
}

/* ============================================
   FOOTER
   ============================================ */
.clay-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 32px;
  background: var(--clay-surface);
  border-top: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 -4px 15px rgba(163, 177, 198, 0.3),
    inset 0 2px 5px rgba(255, 255, 255, 0.4);
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-light);
}

.footer-item .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.footer-item .status-dot.success {
  background: var(--accent-green);
  box-shadow: 0 0 6px var(--accent-green);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .clay-header {
    flex-wrap: wrap;
    gap: 16px;
    padding: 16px;
  }

  .header-center {
    order: 3;
    width: 100%;
    display: flex;
    justify-content: center;
  }

  .main-content {
    padding: 20px;
  }

  .logo-text h1 {
    font-size: 1.25rem;
  }
}
</style>
