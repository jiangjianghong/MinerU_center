<template>
  <div id="app" class="clay-app">
    <!-- Decorative Background Shapes -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
    </div>

    <!-- Main Content -->
    <Dashboard />
  </div>
</template>

<script setup>
import Dashboard from './views/Dashboard.vue'
</script>

<style>
.clay-app {
  min-height: 100vh;
  background: var(--bg-color);
  position: relative;
  overflow: hidden;
}

/* Decorative Background Shapes - 装饰性背景形状 */
.bg-shapes {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 45% 55% 40% 60% / 50% 60% 40% 50%;
  opacity: 0.4;
  animation: float 12s ease-in-out infinite;
  box-shadow:
    15px 15px 30px rgba(163, 177, 198, 0.3),
    -15px -15px 30px rgba(255, 255, 255, 0.3);
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  top: -150px;
  right: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, var(--accent-pink), var(--accent-coral));
  bottom: -100px;
  left: -80px;
  animation-delay: 2s;
}

.shape-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, var(--accent-green), var(--accent-mint));
  top: 40%;
  right: 5%;
  animation-delay: 4s;
}

.shape-4 {
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, var(--accent-yellow), var(--accent-coral));
  bottom: 30%;
  left: 10%;
  animation-delay: 6s;
}
</style>
