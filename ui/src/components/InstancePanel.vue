<template>
  <div class="panel-container">
    <!-- Panel Header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="header-icon">[</span>
        <span class="header-title">SERVER.POOL</span>
        <span class="header-icon">]</span>
      </div>
      <button class="add-btn" @click="showAddDialog = true">
        <span class="btn-icon">+</span>
        <span class="btn-text">ADD.NODE</span>
      </button>
    </div>

    <!-- Instances List -->
    <div class="instances-list">
      <TransitionGroup name="server">
        <div
          v-for="(instance, index) in instances"
          :key="instance.id"
          class="server-card"
          :class="[instance.status, { disabled: !instance.enabled }]"
        >
          <!-- Server Status LED Bar -->
          <div class="status-bar" :class="instance.status"></div>

          <!-- Server Info -->
          <div class="server-main">
            <div class="server-header">
              <div class="server-id">
                <span class="id-prefix">NODE_</span>
                <span class="id-value">{{ String(index + 1).padStart(2, '0') }}</span>
              </div>
              <div class="status-badge" :class="instance.status">
                <span class="status-led"></span>
                <span class="status-text">{{ instance.status.toUpperCase() }}</span>
              </div>
            </div>

            <div class="server-details">
              <div class="detail-row">
                <span class="detail-label">NAME:</span>
                <span class="detail-value">{{ instance.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">ADDR:</span>
                <span class="detail-value mono">{{ instance.url }}</span>
              </div>
              <div v-if="instance.current_task_id" class="detail-row active">
                <span class="detail-label">TASK:</span>
                <span class="detail-value mono">{{ instance.current_task_id.substring(0, 12) }}...</span>
              </div>
            </div>
          </div>

          <!-- Server Controls -->
          <div class="server-controls">
            <button
              class="ctrl-btn"
              :class="instance.enabled ? 'active' : ''"
              @click="toggleInstance(instance.id, !instance.enabled)"
              :title="instance.enabled ? 'DISABLE' : 'ENABLE'"
            >
              <span class="ctrl-icon">{{ instance.enabled ? '||' : '▶' }}</span>
            </button>
            <button
              class="ctrl-btn danger"
              @click="removeInstance(instance.id)"
              :disabled="!!instance.current_task_id"
              title="REMOVE"
            >
              <span class="ctrl-icon">×</span>
            </button>
          </div>

          <!-- Corner Decorations -->
          <div class="corner tl"></div>
          <div class="corner tr"></div>
          <div class="corner bl"></div>
          <div class="corner br"></div>
        </div>
      </TransitionGroup>

      <!-- Empty State -->
      <div v-if="instances.length === 0" class="empty-state">
        <div class="empty-ascii">
          <pre>
  ┌─────────────────┐
  │  NO SERVERS     │
  │  CONNECTED      │
  │                 │
  │  [+ ADD NODE]   │
  └─────────────────┘
          </pre>
        </div>
        <button class="add-btn-empty" @click="showAddDialog = true">
          <span>+ INITIALIZE NODE</span>
        </button>
      </div>
    </div>

    <!-- Add Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddDialog" class="modal-overlay" @click.self="showAddDialog = false">
          <div class="modal-content">
            <!-- Modal Header -->
            <div class="modal-header">
              <div class="modal-title">
                <span class="title-bracket">[</span>
                <span>NEW.SERVER.NODE</span>
                <span class="title-bracket">]</span>
              </div>
              <button class="close-btn" @click="showAddDialog = false">×</button>
            </div>

            <!-- Modal Body -->
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">&gt; NODE.NAME</label>
                <input
                  v-model="newInstance.name"
                  type="text"
                  class="cyber-input"
                  placeholder="MinerU-Server-01"
                />
              </div>
              <div class="form-group">
                <label class="form-label">&gt; NODE.ADDRESS</label>
                <input
                  v-model="newInstance.url"
                  type="text"
                  class="cyber-input"
                  placeholder="http://192.168.1.100:8080"
                />
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="modal-footer">
              <button class="cyber-btn secondary" @click="showAddDialog = false">
                CANCEL
              </button>
              <button class="cyber-btn primary" @click="addInstance">
                CONNECT
              </button>
            </div>

            <!-- Modal Corners -->
            <div class="corner tl"></div>
            <div class="corner tr"></div>
            <div class="corner bl"></div>
            <div class="corner br"></div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

const store = useMainStore()
const { instances } = storeToRefs(store)
const { t } = useI18n()

const showAddDialog = ref(false)
const newInstance = reactive({ name: '', url: '' })

async function addInstance() {
  if (!newInstance.name || !newInstance.url) {
    ElMessage.warning(t('instances.fillAllFields'))
    return
  }
  const success = await store.addInstance(newInstance.name, newInstance.url)
  if (success) {
    ElMessage.success(t('instances.addSuccess'))
    showAddDialog.value = false
    newInstance.name = ''
    newInstance.url = ''
  } else {
    ElMessage.error(t('instances.addFailed'))
  }
}

async function removeInstance(id) {
  const success = await store.removeInstance(id)
  if (success) {
    ElMessage.success(t('instances.removeSuccess'))
  } else {
    ElMessage.error(t('instances.removeFailed'))
  }
}

async function toggleInstance(id, enable) {
  const success = await store.toggleInstance(id, enable)
  if (success) {
    ElMessage.success(enable ? t('instances.enableSuccess') : t('instances.disableSuccess'))
  } else {
    ElMessage.error(t('instances.updateFailed'))
  }
}
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
  background: linear-gradient(90deg, var(--neon-green), transparent);
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
  color: var(--neon-green);
  font-weight: 700;
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--neon-green-dark);
  color: var(--neon-green);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn:hover {
  background: rgba(0, 255, 159, 0.1);
  border-color: var(--neon-green);
  box-shadow: 0 0 15px rgba(0, 255, 159, 0.3), inset 0 0 15px rgba(0, 255, 159, 0.1);
}

.add-btn:active {
  transform: translateY(2px);
}

.btn-icon {
  font-size: 14px;
}

/* Instances List */
.instances-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Server Card */
.server-card {
  position: relative;
  display: flex;
  align-items: stretch;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  transition: all 0.3s ease;
}

.server-card:hover {
  border-color: var(--neon-green-dark);
  box-shadow:
    inset 0 0 30px rgba(0, 255, 159, 0.03),
    0 0 15px rgba(0, 255, 159, 0.1);
}

.server-card.disabled {
  opacity: 0.5;
}

/* Status Bar */
.status-bar {
  width: 4px;
  background: var(--text-dim);
  flex-shrink: 0;
}

.status-bar.idle {
  background: var(--neon-green);
  box-shadow: 0 0 10px var(--neon-green);
}

.status-bar.busy {
  background: var(--neon-cyan);
  box-shadow: 0 0 10px var(--neon-cyan);
  animation: pulse-glow 1.5s ease-in-out infinite;
}

.status-bar.error {
  background: var(--neon-red);
  box-shadow: 0 0 10px var(--neon-red);
}

.status-bar.offline {
  background: var(--text-dim);
}

/* Server Main */
.server-main {
  flex: 1;
  padding: 14px 16px;
  min-width: 0;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.server-id {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.id-prefix {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.id-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: var(--neon-cyan);
  text-shadow: 0 0 10px var(--neon-cyan);
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(128, 128, 144, 0.1);
  border: 1px solid var(--text-dim);
}

.status-badge.idle {
  background: rgba(0, 255, 159, 0.1);
  border-color: var(--neon-green-dark);
}

.status-badge.busy {
  background: rgba(0, 240, 255, 0.1);
  border-color: var(--neon-cyan-dim);
}

.status-badge.error {
  background: rgba(255, 0, 64, 0.1);
  border-color: var(--neon-red);
}

.status-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-dim);
}

.status-badge.idle .status-led {
  background: var(--neon-green);
  box-shadow: 0 0 8px var(--neon-green);
}

.status-badge.busy .status-led {
  background: var(--neon-cyan);
  box-shadow: 0 0 8px var(--neon-cyan);
  animation: breathe 1.5s ease-in-out infinite;
}

.status-badge.error .status-led {
  background: var(--neon-red);
  box-shadow: 0 0 8px var(--neon-red);
}

.status-text {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.status-badge.idle .status-text { color: var(--neon-green); }
.status-badge.busy .status-text { color: var(--neon-cyan); }
.status-badge.error .status-text { color: var(--neon-red); }

/* Server Details */
.server-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.detail-label {
  color: var(--text-dim);
  letter-spacing: 1px;
  min-width: 50px;
}

.detail-value {
  color: var(--text-secondary);
}

.detail-value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
}

.detail-row.active {
  color: var(--neon-cyan);
}

.detail-row.active .detail-label,
.detail-row.active .detail-value {
  color: var(--neon-cyan);
}

/* Server Controls */
.server-controls {
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--border-dim);
}

.ctrl-btn {
  flex: 1;
  width: 40px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--border-dim);
}

.ctrl-btn:last-child {
  border-bottom: none;
}

.ctrl-btn:hover {
  background: rgba(0, 255, 159, 0.1);
  color: var(--neon-green);
}

.ctrl-btn.active {
  color: var(--neon-green);
}

.ctrl-btn.danger:hover {
  background: rgba(255, 0, 64, 0.1);
  color: var(--neon-red);
}

.ctrl-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ctrl-icon {
  font-size: 16px;
  font-weight: 700;
}

/* Corners */
.corner {
  position: absolute;
  width: 6px;
  height: 6px;
  border-style: solid;
  border-color: var(--neon-green-dark);
  border-width: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.server-card:hover .corner {
  opacity: 1;
}

.corner.tl { top: -1px; left: -1px; border-top-width: 1px; border-left-width: 1px; }
.corner.tr { top: -1px; right: -1px; border-top-width: 1px; border-right-width: 1px; }
.corner.bl { bottom: -1px; left: -1px; border-bottom-width: 1px; border-left-width: 1px; }
.corner.br { bottom: -1px; right: -1px; border-bottom-width: 1px; border-right-width: 1px; }

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.empty-ascii {
  color: var(--text-dim);
  font-size: 12px;
}

.empty-ascii pre {
  margin: 0;
  line-height: 1.4;
}

.add-btn-empty {
  padding: 12px 24px;
  background: transparent;
  border: 1px dashed var(--neon-green-dark);
  color: var(--neon-green-dim);
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn-empty:hover {
  border-style: solid;
  border-color: var(--neon-green);
  color: var(--neon-green);
  box-shadow: 0 0 20px rgba(0, 255, 159, 0.2);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  width: 90%;
  max-width: 450px;
  background: var(--cyber-panel);
  border: 1px solid var(--neon-green-dark);
}

.modal-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-green), transparent);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-dim);
}

.modal-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.title-bracket {
  color: var(--neon-green);
}

.close-btn {
  width: 30px;
  height: 30px;
  background: transparent;
  border: 1px solid var(--border-dim);
  color: var(--text-secondary);
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  border-color: var(--neon-red);
  color: var(--neon-red);
}

.modal-body {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 11px;
  color: var(--neon-green);
  letter-spacing: 1px;
}

.cyber-input {
  padding: 12px 14px;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  outline: none;
  transition: all 0.2s ease;
}

.cyber-input::placeholder {
  color: var(--text-dim);
}

.cyber-input:focus {
  border-color: var(--neon-green);
  box-shadow:
    inset 0 0 10px rgba(0, 255, 159, 0.1),
    0 0 10px rgba(0, 255, 159, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-dim);
}

.cyber-btn {
  padding: 10px 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cyber-btn.secondary {
  background: transparent;
  border: 1px solid var(--border-dim);
  color: var(--text-secondary);
}

.cyber-btn.secondary:hover {
  border-color: var(--text-secondary);
  background: rgba(128, 128, 144, 0.1);
}

.cyber-btn.primary {
  background: transparent;
  border: 1px solid var(--neon-green);
  color: var(--neon-green);
}

.cyber-btn.primary:hover {
  background: rgba(0, 255, 159, 0.1);
  box-shadow: 0 0 15px rgba(0, 255, 159, 0.3);
}

.cyber-btn:active {
  transform: translateY(2px);
}

.modal-content .corner {
  opacity: 1;
  width: 10px;
  height: 10px;
  border-color: var(--neon-green);
}

/* Transitions */
.server-enter-active,
.server-leave-active {
  transition: all 0.3s ease;
}

.server-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.server-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}
</style>
