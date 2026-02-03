<template>
  <div class="panel-container">
    <!-- Panel Header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="header-icon">🖥️</span>
        <span class="header-title">{{ t('instances.title') }}</span>
      </div>
      <button class="add-btn" @click="showAddDialog = true">
        <span class="btn-icon">+</span>
        <span class="btn-text">{{ t('instances.add') }}</span>
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
          <!-- Status Indicator -->
          <div class="status-indicator" :class="instance.status">
            <span class="status-dot"></span>
          </div>

          <!-- Server Info -->
          <div class="server-main">
            <div class="server-header">
              <div class="server-name">
                <span class="name-label">节点</span>
                <span class="name-value">{{ String(index + 1).padStart(2, '0') }}</span>
              </div>
              <div class="status-badge" :class="instance.status">
                {{ instance.status.toUpperCase() }}
              </div>
            </div>

            <div class="server-details">
              <div class="detail-row">
                <span class="detail-icon">📛</span>
                <span class="detail-value">{{ instance.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-icon">🔗</span>
                <span class="detail-value url">{{ instance.url }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-icon">⚙️</span>
                <span class="detail-value">{{ instance.backend || 'pipeline' }}</span>
              </div>
              <div v-if="instance.current_task_id" class="detail-row active">
                <span class="detail-icon">⚡</span>
                <span class="detail-value">{{ instance.current_task_id.substring(0, 12) }}...</span>
              </div>
            </div>
          </div>

          <!-- Server Controls -->
          <div class="server-controls">
            <button
              class="ctrl-btn"
              :class="instance.enabled ? 'active' : ''"
              @click="toggleInstance(instance.id, !instance.enabled)"
              :title="instance.enabled ? t('common.disable') : t('common.enable')"
            >
              {{ instance.enabled ? '⏸' : '▶' }}
            </button>
            <button
              class="ctrl-btn danger"
              @click="removeInstance(instance.id)"
              :disabled="!!instance.current_task_id"
              :title="t('common.remove')"
            >
              🗑️
            </button>
          </div>
        </div>
      </TransitionGroup>

      <!-- Empty State -->
      <div v-if="instances.length === 0" class="empty-state">
        <div class="empty-icon">🖥️</div>
        <p class="empty-text">{{ t('instances.noInstances') }}</p>
        <button class="add-btn-empty" @click="showAddDialog = true">
          + {{ t('instances.initNode') }}
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
                <span class="title-icon">🖥️</span>
                <span>{{ t('instances.newNode') }}</span>
              </div>
              <button class="close-btn" @click="showAddDialog = false">×</button>
            </div>

            <!-- Modal Body -->
            <div class="modal-body">
              <div class="form-group">
                <label class="form-label">{{ t('instances.nodeName') }}</label>
                <input
                  v-model="newInstance.name"
                  type="text"
                  class="clay-input"
                  placeholder="MinerU-Server-01"
                />
              </div>
              <div class="form-group">
                <label class="form-label">{{ t('instances.nodeAddr') }}</label>
                <input
                  v-model="newInstance.url"
                  type="text"
                  class="clay-input"
                  placeholder="http://192.168.1.100:8080"
                />
              </div>
              <div class="form-group">
                <label class="form-label">{{ t('instances.backend') }}</label>
                <div class="backend-selector">
                  <button
                    type="button"
                    class="backend-option"
                    :class="{ active: newInstance.backend === 'pipeline' }"
                    @click="newInstance.backend = 'pipeline'"
                  >
                    <span class="backend-label">Pipeline</span>
                    <span class="backend-desc">CPU</span>
                  </button>
                  <button
                    type="button"
                    class="backend-option"
                    :class="{ active: newInstance.backend === 'vllm-async-engine' }"
                    @click="newInstance.backend = 'vllm-async-engine'"
                  >
                    <span class="backend-label">vLLM</span>
                    <span class="backend-desc">GPU</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Modal Footer -->
            <div class="modal-footer">
              <button class="clay-btn neutral" @click="showAddDialog = false">
                {{ t('common.cancel') }}
              </button>
              <button class="clay-btn primary" @click="addInstance">
                {{ t('instances.connect') }}
              </button>
            </div>
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
const newInstance = reactive({ name: '', url: '', backend: 'pipeline' })

async function addInstance() {
  if (!newInstance.name || !newInstance.url) {
    ElMessage.warning(t('instances.fillAllFields'))
    return
  }
  const success = await store.addInstance(newInstance.name, newInstance.url, newInstance.backend)
  if (success) {
    ElMessage.success(t('instances.addSuccess'))
    showAddDialog.value = false
    newInstance.name = ''
    newInstance.url = ''
    newInstance.backend = 'pipeline'
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

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  border: none;
  border-radius: 25px;
  color: white;
  font-family: 'Nunito', sans-serif;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s var(--transition-smooth);
}

.add-btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.add-btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-active);
}

.btn-icon {
  font-size: 1rem;
  font-weight: 800;
}

/* Instances List */
.instances-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Server Card - Claymorphism */
.server-card {
  position: relative;
  display: flex;
  align-items: stretch;
  background: var(--clay-surface);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.3s var(--transition-bounce);
  overflow: hidden;
}

.server-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

.server-card.disabled {
  opacity: 0.6;
}

/* Status Indicator */
.status-indicator {
  width: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px 0 0 20px;
}

.status-indicator.idle { background: var(--accent-green); }
.status-indicator.busy { background: var(--accent-purple); }
.status-indicator.error { background: var(--accent-coral); }
.status-indicator.offline { background: var(--text-dim); }
.status-indicator.disabled { background: var(--text-dim); }

.status-dot {
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.status-indicator.busy .status-dot {
  animation: pulseSoft 1.5s ease-in-out infinite;
}

/* Server Main */
.server-main {
  flex: 1;
  padding: 16px 20px;
  min-width: 0;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.server-name {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.name-label {
  font-size: 0.75rem;
  color: var(--text-light);
  font-weight: 600;
}

.name-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-main);
}

/* Status Badge */
.status-badge {
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.status-badge.idle {
  background: var(--accent-green);
  color: #3d6b4f;
}

.status-badge.busy {
  background: var(--accent-purple);
  color: #5a4669;
}

.status-badge.error {
  background: var(--accent-coral);
  color: #7a4238;
}

.status-badge.offline {
  background: var(--bg-dark);
  color: var(--text-dim);
}

.status-badge.disabled {
  background: var(--bg-dark);
  color: var(--text-dim);
}

/* Server Details */
.server-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

.detail-icon {
  font-size: 0.9rem;
}

.detail-value {
  color: var(--text-light);
  font-weight: 600;
}

.detail-value.url {
  font-family: monospace;
  font-size: 0.8rem;
}

.detail-row.active {
  color: var(--accent-purple-dark);
}

.detail-row.active .detail-value {
  color: var(--accent-purple-dark);
}

/* Server Controls */
.server-controls {
  display: flex;
  flex-direction: column;
  padding: 8px;
  gap: 6px;
}

.ctrl-btn {
  width: 36px;
  height: 36px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: var(--shadow-convex-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  transition: all 0.2s var(--transition-smooth);
}

.ctrl-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.ctrl-btn:active {
  transform: translateY(0);
  box-shadow: var(--shadow-active);
}

.ctrl-btn.active {
  background: var(--accent-green);
}

.ctrl-btn.danger:hover {
  background: var(--accent-coral);
}

.ctrl-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
}

.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 1rem;
  color: var(--text-light);
  font-weight: 600;
}

.add-btn-empty {
  padding: 14px 28px;
  background: var(--clay-surface);
  border: 2px dashed var(--accent-blue);
  border-radius: 25px;
  color: var(--accent-blue-dark);
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s var(--transition-smooth);
}

.add-btn-empty:hover {
  border-style: solid;
  background: var(--accent-blue);
  color: #43658b;
  box-shadow: var(--shadow-convex-sm);
}

/* Modal - Claymorphism */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(224, 229, 236, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  width: 90%;
  max-width: 450px;
  background: var(--clay-surface);
  border-radius: 30px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: var(--shadow-convex);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
}

.title-icon {
  font-size: 1.2rem;
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
  transition: all 0.2s var(--transition-smooth);
}

.close-btn:hover {
  background: var(--accent-coral);
  color: #7a4238;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  padding-left: 10px;
}

.clay-input {
  padding: 14px 18px;
  background: var(--clay-surface);
  border: none;
  border-radius: 20px;
  box-shadow: var(--shadow-concave);
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main);
  outline: none;
  transition: box-shadow 0.2s ease;
}

.clay-input::placeholder {
  color: var(--text-dim);
  font-weight: 500;
}

.clay-input:focus {
  box-shadow:
    inset 8px 8px 12px rgba(163, 177, 198, 0.8),
    inset -8px -8px 12px rgba(255, 255, 255, 0.9);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 2px solid rgba(255, 255, 255, 0.2);
}

.clay-btn {
  padding: 12px 24px;
  font-family: 'Nunito', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: var(--shadow-convex-sm);
  transition: all 0.2s var(--transition-smooth);
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

/* Backend Selector */
.backend-selector {
  display: flex;
  gap: 12px;
}

.backend-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 12px;
  background: var(--clay-surface);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: var(--shadow-concave);
  cursor: pointer;
  transition: all 0.2s var(--transition-smooth);
  font-family: 'Nunito', sans-serif;
}

.backend-option.active {
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  border-color: transparent;
  box-shadow: var(--shadow-convex-sm);
}

.backend-option:hover:not(.active) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-convex-sm);
}

.backend-label {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}

.backend-option.active .backend-label {
  color: white;
}

.backend-desc {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-light);
}

.backend-option.active .backend-desc {
  color: rgba(255, 255, 255, 0.8);
}

/* Transitions */
.server-enter-active,
.server-leave-active {
  transition: all 0.3s var(--transition-bounce);
}

.server-enter-from {
  opacity: 0;
  transform: translateX(-20px) scale(0.95);
}

.server-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95);
}

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
</style>
