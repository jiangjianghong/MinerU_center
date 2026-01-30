<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="close">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-title">
              <span class="title-icon">⚙️</span>
              <span class="title-text">系统配置</span>
            </div>
            <button class="close-btn" @click="close">×</button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- Timeout Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">⏱️</span>
                <span class="section-title">超时设置</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">任务超时</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.task_timeout"
                      class="clay-input"
                      :min="10"
                      :max="3600"
                    />
                    <span class="input-suffix">秒</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">队列超时</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.queue_timeout"
                      class="clay-input"
                      :min="60"
                      :max="7200"
                    />
                    <span class="input-suffix">秒</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Queue Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">📋</span>
                <span class="section-title">队列设置</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">最大队列长度</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.max_queue_size"
                      class="clay-input"
                      :min="1"
                      :max="1000"
                    />
                    <span class="input-suffix">任务</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">启用优先级</label>
                  <div class="toggle-container">
                    <button
                      class="clay-toggle"
                      :class="{ active: formData.enable_priority }"
                      @click="formData.enable_priority = !formData.enable_priority"
                    >
                      <span class="toggle-dot"></span>
                      <span class="toggle-text">{{ formData.enable_priority ? '开启' : '关闭' }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Retry Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">🔄</span>
                <span class="section-title">重试设置</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">最大重试次数</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.max_retries"
                      class="clay-input"
                      :min="0"
                      :max="10"
                    />
                    <span class="input-suffix">次</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">重试延迟</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.retry_delay"
                      class="clay-input"
                      :min="1"
                      :max="60"
                    />
                    <span class="input-suffix">秒</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Instance Settings -->
            <div class="config-section">
              <div class="section-header">
                <span class="section-icon">🖥️</span>
                <span class="section-title">实例设置</span>
              </div>
              <div class="config-grid">
                <div class="config-item">
                  <label class="config-label">健康检查间隔</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.health_check_interval"
                      class="clay-input"
                      :min="5"
                      :max="300"
                    />
                    <span class="input-suffix">秒</span>
                  </div>
                </div>
                <div class="config-item">
                  <label class="config-label">实例超时</label>
                  <div class="input-group">
                    <input
                      type="number"
                      v-model.number="formData.instance_timeout"
                      class="clay-input"
                      :min="1"
                      :max="60"
                    />
                    <span class="input-suffix">秒</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="clay-btn neutral" @click="close">
              取消
            </button>
            <button class="clay-btn primary" @click="saveConfig" :disabled="saving">
              <span v-if="saving" class="btn-loading">⏳</span>
              <span v-else>保存配置</span>
            </button>
          </div>
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
  background: rgba(224, 229, 236, 0.8);
  backdrop-filter: blur(8px);
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
  max-width: 540px;
  max-height: 90vh;
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 1.3rem;
}

.title-text {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-main);
}

.close-btn {
  width: 36px;
  height: 36px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  box-shadow: var(--shadow-convex-sm);
  color: var(--text-light);
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s var(--transition-smooth);
}

.close-btn:hover {
  background: var(--accent-coral);
  color: #7a4238;
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Config Section */
.config-section {
  margin-bottom: 28px;
}

.config-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px dashed rgba(255, 255, 255, 0.2);
}

.section-icon {
  font-size: 1.1rem;
}

.section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-light);
  padding-left: 6px;
}

/* Input Group */
.input-group {
  display: flex;
  align-items: stretch;
  background: var(--clay-surface);
  border-radius: 16px;
  box-shadow: var(--shadow-concave);
  overflow: hidden;
}

.clay-input {
  flex: 1;
  min-width: 0;
  padding: 12px 14px;
  background: transparent;
  border: none;
  color: var(--text-main);
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  outline: none;
}

.clay-input::-webkit-inner-spin-button,
.clay-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.input-suffix {
  padding: 0 14px;
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-light);
  background: rgba(255, 255, 255, 0.3);
}

/* Toggle */
.toggle-container {
  display: flex;
  align-items: center;
}

.clay-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: var(--shadow-convex-sm);
  cursor: pointer;
  transition: all 0.2s var(--transition-smooth);
  width: 100%;
}

.clay-toggle:hover {
  transform: translateY(-2px);
}

.clay-toggle.active {
  background: var(--accent-green);
  border-color: rgba(255, 255, 255, 0.3);
}

.toggle-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--text-dim);
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s ease;
}

.clay-toggle.active .toggle-dot {
  background: #4a9b6f;
  box-shadow: 0 0 8px #4a9b6f;
}

.toggle-text {
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-light);
}

.clay-toggle.active .toggle-text {
  color: #3d6b4f;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.clay-btn {
  padding: 12px 26px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s var(--transition-smooth);
  display: flex;
  align-items: center;
  gap: 8px;
}

.clay-btn.neutral {
  background: var(--clay-surface);
  color: var(--text-light);
}

.clay-btn.neutral:hover {
  transform: translateY(-2px);
}

.clay-btn.primary {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  color: white;
}

.clay-btn.primary:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.clay-btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-active);
}

.clay-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  transform: scale(0.9);
}

/* Responsive */
@media (max-width: 560px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}
</style>
