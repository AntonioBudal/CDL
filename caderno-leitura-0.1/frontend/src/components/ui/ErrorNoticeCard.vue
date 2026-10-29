<script setup lang="ts">
import Icon from './Icon.vue'

withDefaults(
  defineProps<{
    title?: string
    message?: string
    retryLabel?: string
    showRetry?: boolean
  }>(),
  {
    title: 'Não foi possível carregar o conteúdo',
    message: 'Ocorreu uma falha temporária na requisição. Verifique sua conexão local ou tente novamente.',
    retryLabel: 'Tentar novamente',
    showRetry: true,
  }
)

const emit = defineEmits<{
  (e: 'retry'): void
}>()

function onRetry() {
  emit('retry')
}
</script>

<template>
  <div class="error-notice-card" role="alert" aria-live="polite">
    <div class="error-notice-icon-box" aria-hidden="true">
      <Icon name="alert-triangle" :size="24" class="error-notice-icon" />
    </div>

    <div class="error-notice-content">
      <h3 v-if="title" class="error-notice-title">{{ title }}</h3>
      <p class="error-notice-message">{{ message }}</p>

      <div v-if="showRetry" class="error-notice-actions">
        <button
          type="button"
          class="btn-error-retry"
          @click="onRetry"
        >
          <Icon name="rotate-ccw" :size="16" aria-hidden="true" />
          <span>{{ retryLabel }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-notice-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, var(--color-border, #e2e8f0));
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  color: var(--color-text-primary, #0f172a);
  margin: 1.25rem 0;
  transition: border-color 0.15s ease;
}

.error-notice-icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: var(--color-surface-soft, var(--color-surface-subtle, #f1f5f9));
  color: var(--color-link, var(--color-primary, #64748b));
}

.error-notice-content {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.error-notice-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary, #0f172a);
  letter-spacing: -0.01em;
}

.error-notice-message {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-secondary, #475569);
  margin: 0;
}

.error-notice-actions {
  margin-top: 0.5rem;
}

.btn-error-retry {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  min-height: 44px;
  min-width: 44px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-error-retry:hover {
  background-color: var(--color-surface-hover, var(--color-surface-subtle, #e2e8f0));
  border-color: var(--color-border-hover, #94a3b8);
}

.btn-error-retry:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--ring-focus, rgba(37, 99, 235, 0.35));
}

@media (max-width: 640px) {
  .error-notice-card {
    flex-direction: column;
    padding: 1rem;
    gap: 0.75rem;
  }

  .btn-error-retry {
    width: 100%;
    justify-content: center;
  }
}
</style>
