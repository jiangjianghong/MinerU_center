<template>
  <div id="app" class="cyber-app">
    <!-- Matrix Rain Background -->
    <div class="matrix-bg">
      <div v-for="i in 20" :key="i" class="matrix-column" :style="{ left: `${i * 5}%`, animationDelay: `${Math.random() * 5}s`, animationDuration: `${10 + Math.random() * 10}s` }">
        <span v-for="j in 30" :key="j">{{ randomChar() }}</span>
      </div>
    </div>

    <!-- Grid Pattern -->
    <div class="grid-pattern"></div>

    <!-- Scanlines -->
    <div class="scanlines"></div>

    <!-- Main Content -->
    <Dashboard />
  </div>
</template>

<script setup>
import Dashboard from './views/Dashboard.vue'

function randomChar() {
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'
  return chars[Math.floor(Math.random() * chars.length)]
}
</script>

<style>
.cyber-app {
  min-height: 100vh;
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
}

/* Matrix Rain */
.matrix-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  opacity: 0.15;
}

.matrix-column {
  position: absolute;
  top: -100%;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  color: #00ff9f;
  writing-mode: vertical-rl;
  text-orientation: upright;
  animation: matrix-fall 20s linear infinite;
  text-shadow: 0 0 10px #00ff9f;
}

.matrix-column span {
  display: block;
  opacity: 0.8;
}

@keyframes matrix-fall {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(200vh);
  }
}

/* Grid Pattern */
.grid-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(0, 255, 159, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 159, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* Scanlines */
.scanlines {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9998;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.1) 2px,
    rgba(0, 0, 0, 0.1) 4px
  );
}

/* Ensure main content is above effects */
.cyber-app > :not(.matrix-bg):not(.grid-pattern):not(.scanlines) {
  position: relative;
  z-index: 1;
}
</style>
