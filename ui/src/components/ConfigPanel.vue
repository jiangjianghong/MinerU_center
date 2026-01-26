<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="close">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <span class="title-bracket">[</span>
              <span class="title-text">SYS.CONFIG</span>
              <span class="title-bracket">]</span>
            </div>
            <button class="close-btn" @click="close">×</button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- Timeout Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">&gt;</span>
                <span class="section-title">TIMEOUT.CONFIG</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">TASK_TIMEOUT</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.task_timeout"
                      class="cyber-input"
                      :min="10"
                      :max="3600"
                    />
                    <span class="input-suffix">SEC</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">QUEUE_TIMEOUT</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.queue_timeout"
                      class="cyber-input"
                      :min="60"
                      :max="7200"
                    />
                    <span class="input-suffix">SEC</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Queue Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">&gt;</span>
                <span class="section-title">QUEUE.CONFIG</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">MAX_QUEUE_SIZE</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.max_queue_size"
                      class="cyber-input"
                      :min="1"
                      :max="1000"
                    />
                    <span class="input-suffix">TASKS</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">ENABLE_PRIORITY</label>
                  <div class="toggle-container">
                    <button
                      class="cyber-toggle"
                      :class="{ active: formData.enable_priority }"
                      @click="formData.enable_priority = !formData.enable_priority"
                    >
                      <span class="toggle-led"></span>
                      <span class="toggle-text">{{ formData.enable_priority ? 'ON' : 'OFF' }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Retry Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">&gt;</span>
                <span class="section-title">RETRY.CONFIG</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">MAX_RETRIES</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.max_retries"
                      class="cyber-input"
                      :min="0"
                      :max="10"
                    />
                    <span class="input-suffix">×</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">RETRY_DELAY</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.retry_delay"
                      class="cyber-input"
                      :min="1"
                      :max="60"
                    />
                    <span class="input-suffix">SEC</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Instance Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">&gt;</span>
                <span class="section-title">INSTANCE.CONFIG</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">HEALTH_CHECK_INT</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.health_check_interval"
                      class="cyber-input"
                      :min="5"
                      :max="300"
                    />
                    <span class="input-suffix">SEC</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">INSTANCE_TIMEOUT</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.instance_timeout"
                      class="cyber-input"
                      :min="1"
                      :max="60"
                    />
                    <span class="input-suffix">SEC</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="cyber-btn secondary" @click="close">
              CANCEL
            </button>
            <button class="cyber-btn primary" @click="saveConfig" :disabled="saving">
              <span v-if="saving" class="btn-loading">◐</span>
              <span v-else>SAVE.CONFIG</span>
            </button>
          </div>

          <!-- Corner Decorations -->
          <div class="corner tl"></div>
          <div class="corner tr"></div>
          <div class="corner bl"></div>
          <div class="corner br"></div>

          <!-- Scan Line Effect -->
          <div class="scan-line"></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useMainStore } from '../stores'
import { useI18n } from '../i18n'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible'])
const { t } = useI18n()

const store = useMainStore()
const { config } = storeToRefs(store)

const saving = ref(false)
const formData = reactive({
  task_timeout: 300,
  queue_timeout: 600,
  max_queue_size: 100,
  enable_priority: true,
  max_retries: 3,
  retry_delay: 5,
  health_check_interval: 30,
  instance_timeout: 10
})

function close() {
  emit('update:visible', false)
}

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      Object.assign(formData, config.value)
    }
  }
)

async function saveConfig() {
  saving.value = true
  try {
    const success = await store.updateConfig(formData)
    if (success) {
      ElMessage.success(t('config.saveSuccess'))
      close()
    } else {
      ElMessage.error(t('config.saveFailed'))
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

/* Modal Content */
.modal-content {
  position: relative;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  background: var(--cyber-panel);
  border: 1px solid var(--neon-green-dark);
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

/* Scan Line */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
  animation: scan 3s linear infinite;
  opacity: 0.5;
  pointer-events: none;
}

/* Corners */
.corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border-style: solid;
  border-color: var(--neon-green);
  border-width: 0;
}

.corner.tl { top: -1px; left: -1px; border-top-width: 2px; border-left-width: 2px; }
.corner.tr { top: -1px; right: -1px; border-top-width: 2px; border-right-width: 2px; }
.corner.bl { bottom: -1px; left: -1px; border-bottom-width: 2px; border-left-width: 2px; }
.corner.br { bottom: -1px; right: -1px; border-bottom-width: 2px; border-right-width: 2px; }

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-dim);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 4px;
}

.title-bracket {
  color: var(--neon-green);
  font-weight: 700;
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 2px;
}

.close-btn {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-dim);
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  border-color: var(--neon-red);
  color: var(--neon-red);
  box-shadow: 0 0 10px rgba(255, 0, 64, 0.3);
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* Config Section */
.config-section {
  margin-bottom: 24px;
}

.config-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--border-dim);
}

.section-icon {
  color: var(--neon-green);
  font-weight: 700;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--neon-cyan);
  letter-spacing: 1px;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 1px;
}

/* Input Group */
.input-group {
  display: flex;
  align-items: stretch;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  transition: all 0.2s ease;
}

.input-group:focus-within {
  border-color: var(--neon-green);
  box-shadow:
    inset 0 0 10px rgba(0, 255, 159, 0.1),
    0 0 10px rgba(0, 255, 159, 0.2);
}

.cyber-input {
  flex: 1;
  min-width: 0;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: var(--neon-green);
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  outline: none;
}

.cyber-input::-webkit-inner-spin-button,
.cyber-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-suffix {
  padding: 0 12px;
  display: flex;
  align-items: center;
  font-size: 10px;
  color: var(--text-dim);
  letter-spacing: 1px;
  background: rgba(0, 0, 0, 0.2);
  border-left: 1px solid var(--border-dim);
}

/* Toggle */
.toggle-container {
  display: flex;
  align-items: center;
}

.cyber-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: var(--cyber-darker);
  border: 1px solid var(--border-dim);
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.cyber-toggle:hover {
  border-color: var(--neon-green-dark);
}

.cyber-toggle.active {
  border-color: var(--neon-green);
  box-shadow: 0 0 10px rgba(0, 255, 159, 0.2);
}

.toggle-led {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text-dim);
  transition: all 0.2s ease;
}

.cyber-toggle.active .toggle-led {
  background: var(--neon-green);
  box-shadow: 0 0 10px var(--neon-green);
}

.toggle-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.cyber-toggle.active .toggle-text {
  color: var(--neon-green);
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-dim);
  background: rgba(0, 0, 0, 0.2);
}

.cyber-btn {
  padding: 10px 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
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

.cyber-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cyber-btn:active {
  transform: translateY(2px);
}

.btn-loading {
  animation: spin 1s linear infinite;
}

/* Modal Transitions */
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
  transform: scale(0.95) translateY(20px);
}

/* Responsive */
@media (max-width: 560px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}
</style>
