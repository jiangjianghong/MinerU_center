<template>
  <div class="dashboard">
    <!-- Header Terminal Bar -->
    <header class="cyber-header">
      <div class="header-left">
        <div class="logo-container">
          <div class="logo-icon">
            <div class="logo-hex"></div>
            <span class="logo-text">M</span>
          </div>
          <div class="logo-info">
            <h1 class="logo-title">{{ t('dashboard.title') }}<span class="blink">_</span></h1>
            <div class="logo-subtitle">
              <span class="terminal-prompt">&gt;</span>
              <span class="typing-text">{{ t('dashboard.subtitle') }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="system-time">
          <span class="time-label">{{ t('dashboard.sysTime') }}</span>
          <span class="time-value">{{ currentTime }}</span>
        </div>
      </div>

      <div class="header-right">
        <!-- Connection Status -->
        <div class="status-indicator" :class="{ connected: wsConnected }">
          <div class="led" :class="wsConnected ? 'green' : 'red'"></div>
          <span class="status-text">{{ wsConnected ? t('dashboard.linkOk') : t('dashboard.offline') }}</span>
        </div>

        <!-- Divider -->
        <div class="header-divider"></div>

        <!-- Control Buttons -->
        <button class="cyber-btn-icon" @click="toggleLocale" :title="locale === 'zh' ? 'EN' : '中'">
          <span class="btn-label">{{ locale === 'zh' ? '中' : 'EN' }}</span>
        </button>

        <button class="cyber-btn-icon" @click="showConfig = true" :title="t('common.config')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>

        <button class="cyber-btn-icon" @click="refresh" :class="{ active: isRefreshing }" :title="t('common.refresh')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" :class="{ spin: isRefreshing }">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Stats Overview - Terminal Style -->
      <section class="stats-section">
        <StatsCard />
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

    <!-- Footer Status Bar -->
    <footer class="cyber-footer">
      <div class="footer-left">
        <span class="footer-item">
          <span class="led green"></span>
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

const store = useMainStore()
const { wsConnected } = storeToRefs(store)
const { t, locale, toggleLocale } = useI18n()

const showConfig = ref(false)
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
}

/* ============================================
   HEADER
   ============================================ */
.cyber-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(180deg, rgba(15, 15, 24, 0.95) 0%, rgba(10, 10, 15, 0.9) 100%);
  border-bottom: 1px solid var(--neon-green-dark);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.cyber-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon-green), transparent);
  opacity: 0.5;
}

/* Logo */
.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-hex {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--neon-green-dark) 0%, transparent 50%);
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
  border: 1px solid var(--neon-green);
  animation: breathe 3s ease-in-out infinite;
}

.logo-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 24px;
  font-weight: 900;
  color: var(--neon-green);
  text-shadow: 0 0 10px var(--neon-green), 0 0 20px var(--neon-green);
  z-index: 1;
}

.logo-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--neon-green);
  letter-spacing: 4px;
  text-shadow: 0 0 10px var(--neon-green);
  margin: 0;
}

.logo-title .blink {
  animation: blink 1s step-end infinite;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.terminal-prompt {
  color: var(--neon-cyan);
}

.typing-text {
  overflow: hidden;
  white-space: nowrap;
}

/* Header Center */
.header-center {
  display: flex;
  align-items: center;
}

.system-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 20px;
  background: rgba(0, 255, 159, 0.05);
  border: 1px solid var(--neon-green-dark);
}

.time-label {
  font-size: 9px;
  color: var(--text-dim);
  letter-spacing: 2px;
}

.time-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  color: var(--neon-cyan);
  text-shadow: 0 0 10px var(--neon-cyan);
  letter-spacing: 2px;
}

/* Header Right */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 0, 64, 0.1);
  border: 1px solid var(--neon-red);
}

.status-indicator.connected {
  background: rgba(0, 255, 159, 0.1);
  border-color: var(--neon-green);
}

.led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.led.green {
  background: var(--neon-green);
  box-shadow: 0 0 10px var(--neon-green);
  animation: breathe 2s ease-in-out infinite;
}

.led.red {
  background: var(--neon-red);
  box-shadow: 0 0 10px var(--neon-red);
  animation: breathe 1s ease-in-out infinite;
}

.status-text {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--neon-red);
}

.status-indicator.connected .status-text {
  color: var(--neon-green);
}

.header-divider {
  width: 1px;
  height: 30px;
  background: var(--border-dim);
}

/* Control Buttons */
.cyber-btn-icon {
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid var(--border-dim);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.cyber-btn-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 159, 0.1), transparent);
  transition: left 0.3s ease;
}

.cyber-btn-icon:hover {
  border-color: var(--neon-green);
  color: var(--neon-green);
  box-shadow: 0 0 15px rgba(0, 255, 159, 0.3), inset 0 0 15px rgba(0, 255, 159, 0.1);
}

.cyber-btn-icon:hover::before {
  left: 100%;
}

.cyber-btn-icon:active {
  transform: translateY(2px);
  box-shadow: none;
}

.cyber-btn-icon.active {
  border-color: var(--neon-cyan);
  color: var(--neon-cyan);
}

.cyber-btn-icon svg {
  width: 18px;
  height: 18px;
}

.cyber-btn-icon svg.spin {
  animation: spin 1s linear infinite;
}

.btn-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
}

/* ============================================
   MAIN CONTENT
   ============================================ */
.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.stats-section {
  margin-bottom: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
}

/* ============================================
   FOOTER
   ============================================ */
.cyber-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 24px;
  background: rgba(15, 15, 24, 0.95);
  border-top: 1px solid var(--border-dim);
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.cyber-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon-green-dark), transparent);
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
  gap: 6px;
}

.footer-item .led {
  width: 6px;
  height: 6px;
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
  .cyber-header {
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px 16px;
  }

  .header-center {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .main-content {
    padding: 16px;
  }
}
</style>
