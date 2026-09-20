<script setup lang="ts">
import type { StatusBadgeProps } from '../../types'
import Icon from './Icon.vue'

withDefaults(defineProps<StatusBadgeProps>(), {
  variant: 'neutral',
  icon: undefined,
})
</script>

<template>
  <span :class="['status-badge', `badge-${variant}`]">
    <Icon v-if="icon" :name="icon" :size="14" :stroke-width="2" class="badge-icon" />
    <span class="badge-text">{{ label }}</span>
  </span>
</template>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.2rem 0.55rem;
  border-radius: var(--radius-full, 9999px);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
  vertical-align: middle;
}

.badge-icon {
  flex-shrink: 0;
}

.badge-neutral {
  background: color-mix(in srgb, var(--border-subtle, #e0e0e0) 50%, transparent);
  color: var(--text-muted, #71717a);
  border: 1px solid color-mix(in srgb, var(--border-subtle, #e0e0e0) 80%, transparent);
}

.badge-accent {
  background: color-mix(in srgb, var(--accent, #3b82f6) 12%, transparent);
  color: var(--accent, #3b82f6);
  border: 1px solid color-mix(in srgb, var(--accent, #3b82f6) 25%, transparent);
}

.badge-warning {
  background: color-mix(in srgb, #f59e0b 12%, transparent);
  color: #d97706;
  border: 1px solid color-mix(in srgb, #f59e0b 25%, transparent);
}

.badge-danger {
  background: color-mix(in srgb, #ef4444 12%, transparent);
  color: #dc2626;
  border: 1px solid color-mix(in srgb, #ef4444 25%, transparent);
}

.badge-success {
  background: color-mix(in srgb, #10b981 12%, transparent);
  color: #059669;
  border: 1px solid color-mix(in srgb, #10b981 25%, transparent);
}
</style>
