<script setup lang="ts">
import type { EmptyStateProps } from '../../types'
import Icon from './Icon.vue'

withDefaults(defineProps<EmptyStateProps>(), {
  description: '',
  headingLevel: 'h2',
})
</script>

<template>
  <div class="empty-state-wrapper">
    <div class="empty-state-icon-box" aria-hidden="true">
      <Icon :name="icon" :size="32" :stroke-width="1.75" />
    </div>

    <component :is="headingLevel" class="empty-state-title">
      {{ title }}
    </component>

    <p v-if="description" class="empty-state-description">
      {{ description }}
    </p>

    <div v-if="$slots.default" class="empty-state-actions">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.empty-state-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  border-radius: var(--radius-md, 8px);
  background: var(--bg-surface-elevated, var(--bg-surface, #ffffff));
  border: 1px dashed var(--border-subtle, #e0e0e0);
  margin: 1.5rem 0;
  max-width: 540px;
  margin-inline: auto;
}

.empty-state-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent-subtle, var(--border-subtle, #e0e0e0)) 40%, transparent);
  color: var(--text-muted, #71717a);
  margin-bottom: 1.25rem;
}

.empty-state-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-main, #18181b);
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.empty-state-description {
  font-size: 0.9375rem;
  color: var(--text-muted, #71717a);
  margin: 0 0 1.25rem 0;
  line-height: 1.5;
  max-width: 420px;
}

.empty-state-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}
</style>
