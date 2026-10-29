<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    summary: { easy: number; medium: number; hard: number; total: number }
    hasMoreItems?: boolean
    elapsedSeconds?: number
  }>(),
  {
    hasMoreItems: true,
    elapsedSeconds: 0,
  },
)

const emit = defineEmits<{
  (e: 'review-more'): void
  (e: 'finish'): void
}>()

const easyPercent = computed(() =>
  props.summary.total > 0 ? Math.round((props.summary.easy / props.summary.total) * 100) : 0,
)
const mediumPercent = computed(() =>
  props.summary.total > 0 ? Math.round((props.summary.medium / props.summary.total) * 100) : 0,
)
const hardPercent = computed(() =>
  props.summary.total > 0 ? Math.round((props.summary.hard / props.summary.total) * 100) : 0,
)

const formattedTime = computed(() => {
  if (!props.elapsedSeconds || props.elapsedSeconds <= 0) return ''
  const mins = Math.floor(props.elapsedSeconds / 60)
  const secs = props.elapsedSeconds % 60
  if (mins === 0) return `${secs}s de foco`
  return `${mins}m ${secs}s de foco`
})
</script>

<template>
  <div
    v-if="isOpen"
    class="modal-backdrop"
    role="dialog"
    aria-modal="true"
    aria-labelledby="summary-title"
  >
    <div class="summary-modal-card">
      <header class="modal-header">
        <div class="celebration-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 id="summary-title" class="modal-title">Rodada Concluída!</h2>
        <p class="modal-subtitle">
          Você praticou {{ summary.total }} itens nesta sessão<template v-if="formattedTime"> em {{ formattedTime }}</template>.
        </p>
      </header>

      <!-- Balanço de Retenção -->
      <div class="retention-grid">
        <div class="retention-card card-easy">
          <span class="retention-label">Fácil</span>
          <span class="retention-value">{{ summary.easy }}</span>
          <span class="retention-percent">{{ easyPercent }}%</span>
        </div>

        <div class="retention-card card-medium">
          <span class="retention-label">Médio</span>
          <span class="retention-value">{{ summary.medium }}</span>
          <span class="retention-percent">{{ mediumPercent }}%</span>
        </div>

        <div class="retention-card card-hard">
          <span class="retention-label">Difícil</span>
          <span class="retention-value">{{ summary.hard }}</span>
          <span class="retention-percent">{{ hardPercent }}%</span>
        </div>
      </div>

      <!-- Barra proporcional de retenção -->
      <div class="retention-bar" aria-hidden="true">
        <div class="bar-segment bar-easy" :style="{ width: `${easyPercent}%` }" />
        <div class="bar-segment bar-medium" :style="{ width: `${mediumPercent}%` }" />
        <div class="bar-segment bar-hard" :style="{ width: `${hardPercent}%` }" />
      </div>

      <footer class="modal-actions">
        <button
          v-if="hasMoreItems"
          type="button"
          class="btn-action btn-primary"
          @click="emit('review-more')"
        >
          Revisar mais 10
        </button>
        <button
          type="button"
          class="btn-action btn-secondary"
          @click="emit('finish')"
        >
          Concluir e voltar ao acervo
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.summary-modal-card {
  width: 100%;
  max-width: 480px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: var(--radius-card, 1.25rem);
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: center;
}

.celebration-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.1));
  color: var(--color-link, var(--color-primary, #3b82f6));
  margin: 0 auto 0.5rem;
}

.modal-title {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  margin: 0 0 0.5rem;
  letter-spacing: -0.015em;
}

.modal-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

.retention-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.retention-card {
  display: flex;
  flex-direction: column;
  padding: 0.85rem 0.5rem;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
}

.card-easy {
  color: var(--color-success);
}

.card-medium {
  color: var(--color-warning);
}

.card-hard {
  color: var(--color-error);
}

.retention-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.retention-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
}

.retention-percent {
  font-size: 0.75rem;
  opacity: 0.85;
}

.retention-bar {
  display: flex;
  height: 8px;
  border-radius: 9999px;
  overflow: hidden;
  background-color: var(--color-border-subtle, #e2e8f0);
}

.bar-easy {
  background-color: var(--color-success);
}

.bar-medium {
  background-color: var(--color-warning);
}

.bar-hard {
  background-color: var(--color-error);
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-action {
  min-height: 44px;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-button, 0.5rem);
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  text-align: center;
  justify-content: center;
}

.btn-primary {
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  border: 1px solid transparent;
}

.btn-primary:hover {
  opacity: 0.92;
}

@media (hover: hover) and (pointer: fine) {
  .btn-primary:hover {
    transform: translateY(-1px);
  }
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-text-secondary, #64748b);
  border: 1px solid var(--color-border-strong, #cbd5e1);
}

.btn-secondary:hover {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text, #0f172a);
}
</style>
