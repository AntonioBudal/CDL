<script setup lang="ts">
import type { LoadingSkeletonProps } from '../../types'

withDefaults(defineProps<LoadingSkeletonProps>(), {
  shape: 'rect',
  width: '100%',
  height: '1.25rem',
  lines: 1,
  gap: '0.5rem',
})
</script>

<template>
  <div
    class="loading-skeleton-container"
    aria-busy="true"
    aria-live="polite"
    :style="{ gap: gap }"
  >
    <span class="sr-only">Carregando conteúdo…</span>
    <div
      v-for="index in lines"
      :key="index"
      :class="['skeleton-block', `skeleton-${shape}`]"
      :style="{
        width: shape === 'text' && lines > 1 && index === lines ? '60%' : width,
        height: height,
      }"
    />
  </div>
</template>

<style scoped>
.loading-skeleton-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.skeleton-block {
  background: var(--skeleton-base, color-mix(in srgb, var(--color-border, #cbd5e1) 50%, transparent));
  position: relative;
  overflow: hidden;
}

.skeleton-rect {
  border-radius: var(--radius-card, 6px);
}

.skeleton-circle {
  border-radius: 50%;
}

.skeleton-text {
  border-radius: var(--radius-badge, 4px);
}

/* Shimmer animado suave */
.skeleton-block::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transform: translateX(-100%);
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--skeleton-shimmer, color-mix(in srgb, var(--color-surface, #ffffff) 40%, transparent)) 50%,
    transparent 100%
  );
  animation: shimmer 1.8s infinite;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

/* Acessibilidade: respeitar prefers-reduced-motion e alto contraste */
@media (prefers-reduced-motion: reduce) {
  .skeleton-block::after {
    animation: none;
    display: none;
  }
  .skeleton-block {
    opacity: 0.6;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
