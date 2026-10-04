<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    summary: { easy: number; medium: number; hard: number; total: number }
    hasMoreItems?: boolean
  }>(),
  {
    hasMoreItems: true,
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
          Você praticou {{ summary.total }} itens nesta sessão. Confira o balanço de retenção:
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
  background-color: rgba(15, 23, 42, 0.6);
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
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: center;
}

.celebration-badge {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #0f172a);
  margin: 0 0 0.5rem;
}

.modal-subtitle {
  font-size: 0.875rem;
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
  padding: 1rem 0.5rem;
  border-radius: 0.75rem;
  border: 1px solid transparent;
}

.card-easy {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
}

.card-medium {
  background-color: #fefce8;
  border-color: #fef08a;
  color: #854d0e;
}

.card-hard {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
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
  background-color: #e2e8f0;
}

.bar-easy {
  background-color: #22c55e;
}

.bar-medium {
  background-color: #eab308;
}

.bar-hard {
  background-color: #ef4444;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-action {
  min-height: 44px;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
}

.btn-primary {
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
}

.btn-primary:hover {
  background-color: var(--color-primary-hover, #1d4ed8);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-text-secondary, #64748b);
  border: 1px solid var(--color-border-subtle, #cbd5e1);
}

.btn-secondary:hover {
  background-color: var(--color-bg-surface-secondary, #f8fafc);
  color: var(--color-text-primary, #0f172a);
}
</style>
