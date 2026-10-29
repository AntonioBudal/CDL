<script setup lang="ts">
import { computed } from 'vue'
import type { StudySessionSummary } from '../../types.ts'

const props = defineProps<{
  summary: StudySessionSummary
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'goToBook', bookId: number): void
}>()

const session = computed(() => props.summary.session)

const formattedDuration = computed(() => {
  const totalSecs = session.value.duration_seconds || 0
  const minutes = Math.floor(totalSecs / 60)
  const seconds = totalSecs % 60
  if (minutes === 0) {
    return `${seconds} segundos`
  }
  return `${minutes} min e ${seconds} s`
})
</script>

<template>
  <div
    class="summary-modal-overlay"
    role="dialog"
    aria-modal="true"
    aria-labelledby="summary-title"
  >
    <div class="summary-modal-card">
      <div class="card-header">
        <span class="laurel-badge" aria-hidden="true">Sessão Concluída</span>
        <h2 id="summary-title" class="summary-heading">
          Auditoria de Aprendizado
        </h2>
        <p class="summary-subheading">
          Você completou seu bloco de estudo com foco e deliberação.
        </p>
      </div>

      <div class="metrics-grid">
        <div class="metric-box primary-box">
          <span class="metric-label">Retenção Estimada</span>
          <span class="metric-value">{{ summary.accuracy_rate }}%</span>
        </div>

        <div class="metric-box">
          <span class="metric-label">Itens Concluídos</span>
          <span class="metric-value">{{ session.completed_items }} de {{ session.total_items }}</span>
        </div>

        <div class="metric-box">
          <span class="metric-label">Tempo Dedicado</span>
          <span class="metric-value">{{ formattedDuration }}</span>
        </div>
      </div>

      <div class="retention-distribution">
        <h3 class="distribution-title">Distribuição de Retenção</h3>
        <div class="distribution-bars">
          <div class="dist-row">
            <span class="dist-tag easy-tag">Fácil</span>
            <div class="dist-track">
              <div
                class="dist-fill easy-fill"
                :style="{
                  width: `${session.completed_items > 0 ? (session.easy_count / session.completed_items) * 100 : 0}%`
                }"
              />
            </div>
            <span class="dist-count">{{ session.easy_count }}</span>
          </div>

          <div class="dist-row">
            <span class="dist-tag medium-tag">Médio</span>
            <div class="dist-track">
              <div
                class="dist-fill medium-fill"
                :style="{
                  width: `${session.completed_items > 0 ? (session.medium_count / session.completed_items) * 100 : 0}%`
                }"
              />
            </div>
            <span class="dist-count">{{ session.medium_count }}</span>
          </div>

          <div class="dist-row">
            <span class="dist-tag hard-tag">Difícil</span>
            <div class="dist-track">
              <div
                class="dist-fill hard-fill"
                :style="{
                  width: `${session.completed_items > 0 ? (session.hard_count / session.completed_items) * 100 : 0}%`
                }"
              />
            </div>
            <span class="dist-count">{{ session.hard_count }}</span>
          </div>
        </div>
      </div>

      <div class="card-actions">
        <button
          v-if="session.book_id"
          type="button"
          class="btn-secondary"
          @click="emit('goToBook', session.book_id)"
        >
          Ir para o Livro
        </button>
        <button
          type="button"
          class="btn-primary"
          @click="emit('close')"
        >
          Retornar à Central de Revisão
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.summary-modal-card {
  width: 100%;
  max-width: 540px;
  background-color: var(--color-bg, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 2rem;
}

.card-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.laurel-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-link, #2563eb);
  background-color: var(--color-accent-subtle, #eff6ff);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  margin-bottom: 0.75rem;
}

.summary-heading {
  font-family: var(--font-serif, "EB Garamond", serif);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0 0 0.5rem 0;
}

.summary-subheading {
  font-size: 0.9375rem;
  color: var(--color-text-muted, #6b7280);
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.metric-box {
  background-color: var(--color-bg-subtle, #f9fafb);
  border: 1px solid var(--color-border-subtle, #f3f4f6);
  border-radius: 8px;
  padding: 0.875rem 0.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.primary-box {
  background-color: var(--color-accent-subtle, #eff6ff);
  border-color: var(--color-border-accent, #bfdbfe);
}

.metric-label {
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  font-weight: 500;
}

.metric-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text, #111827);
  font-variant-numeric: tabular-nums;
}

.retention-distribution {
  background-color: var(--color-bg-subtle, #f9fafb);
  border: 1px solid var(--color-border-subtle, #e5e7eb);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 2rem;
}

.distribution-title {
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary, #4b5563);
  margin: 0 0 0.875rem 0;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.dist-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8125rem;
}

.dist-tag {
  min-width: 52px;
  font-weight: 600;
}

.easy-tag {
  color: var(--color-success, #16a34a);
}

.medium-tag {
  color: var(--color-warning, #d97706);
}

.hard-tag {
  color: var(--color-danger, #dc2626);
}

.dist-track {
  flex: 1;
  height: 8px;
  background-color: var(--color-border-subtle, #e5e7eb);
  border-radius: 9999px;
  overflow: hidden;
}

.dist-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.easy-fill {
  background-color: var(--color-success, #16a34a);
}

.medium-fill {
  background-color: var(--color-warning, #d97706);
}

.hard-fill {
  background-color: var(--color-danger, #dc2626);
}

.dist-count {
  min-width: 20px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--color-text-muted, #6b7280);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.625rem 1.25rem;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-primary {
  background-color: var(--color-accent, #2563eb);
  color: var(--color-on-accent);
  border: 1px solid transparent;
}

.btn-primary:hover {
  background-color: var(--color-accent-hover, #1d4ed8);
  color: var(--color-accent-hover-text);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-text, #374151);
  border: 1px solid var(--color-border, #d1d5db);
}

.btn-secondary:hover {
  background-color: var(--color-bg-subtle, #f3f4f6);
}

@media (max-width: 640px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  .card-actions {
    flex-direction: column-reverse;
  }
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
