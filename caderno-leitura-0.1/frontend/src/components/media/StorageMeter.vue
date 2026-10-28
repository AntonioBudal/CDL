<script setup lang="ts">
import { computed } from 'vue'
import Icon from '../ui/Icon.vue'
import type { UsageLevel } from '../../types/media'
import { LEVEL_LABELS } from '../../utils/mediaFormat'

// Medidor de espaço (feature 090-C): o nível aparece em texto e ícone, nunca só na cor.
const props = defineProps<{
  label: string
  text: string
  level: UsageLevel
  percent?: number | null
}>()

const shown = computed(() => Math.min(100, Math.max(0, props.percent ?? 0)))
const levelText = computed(() => LEVEL_LABELS[props.level])
const icon = computed(() => (props.level === 'normal' ? 'check-circle' : 'alert-triangle'))
const valueText = computed(() => `${props.text}. Estado: ${levelText.value}`)
</script>

<template>
  <div class="storage-meter" :class="`level-${level}`">
    <div class="meter-heading">
      <span class="meter-label">{{ label }}</span>
      <span class="meter-level">
        <Icon :name="icon" :size="16" aria-hidden="true" />
        Estado: {{ levelText }}
      </span>
    </div>
    <div
      v-if="percent !== undefined && percent !== null"
      class="meter-track"
      role="meter"
      :aria-label="label"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-valuenow="shown"
      :aria-valuetext="valueText"
    >
      <div class="meter-fill" :style="{ width: `${shown}%` }" />
    </div>
    <p class="meter-text">{{ text }}</p>
  </div>
</template>

<style scoped>
.storage-meter {
  display: grid;
  gap: 0.5rem;
}

.meter-heading {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
  font-weight: 600;
}

.meter-level {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.level-high .meter-level {
  color: var(--color-warning-text);
}

.level-full .meter-level {
  color: var(--color-error-text);
}

.meter-track {
  height: 0.75rem;
  border-radius: 999px;
  background: var(--color-surface-inset);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  min-width: 2px;
  background: var(--color-accent);
}

.level-high .meter-fill {
  background: var(--color-warning-marker);
}

.level-full .meter-fill {
  background: var(--color-error-marker);
}

.meter-text {
  margin: 0;
  color: var(--color-text-secondary);
}

/* E-Ink: o preenchimento usa hachura, não só cor. */
:root[data-theme='e-ink'] .meter-fill {
  background: repeating-linear-gradient(45deg, var(--color-text) 0 3px, transparent 3px 6px);
}
</style>
