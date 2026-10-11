<script setup lang="ts">
import { computed } from 'vue'
import type { Chapter, ReviewStatsResponse } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    stats: ReviewStatsResponse
    selectedBookId?: number | null
    selectedChapterId?: number | null
    selectedKind?: string
    chapters?: Chapter[]
    loading?: boolean
  }>(),
  {
    selectedBookId: null,
    selectedChapterId: null,
    selectedKind: 'all',
    chapters: () => [],
    loading: false,
  },
)

const emit = defineEmits<{
  (e: 'update:selectedBookId', value: number | null): void
  (e: 'update:selectedChapterId', value: number | null): void
  (e: 'update:selectedKind', value: string): void
  (e: 'start-practice'): void
}>()

const estimatedMinutes = computed(() => {
  const count = props.stats?.pending_review ?? 0
  if (count <= 0) return 0
  return Math.max(1, Math.ceil(count * 0.6))
})

function setKind(kind: string) {
  emit('update:selectedKind', kind)
}

function onBookChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const val = target.value ? Number(target.value) : null
  emit('update:selectedBookId', val)
  emit('update:selectedChapterId', null)
}

function onChapterChange(event: Event) {
  const target = event.target as HTMLSelectElement
  const val = target.value ? Number(target.value) : null
  emit('update:selectedChapterId', val)
}

function onStartPractice() {
  emit('start-practice')
}
</script>

<template>
  <header class="review-stats-header" role="region" aria-label="Bancada de Prontidão e Filtros de Revisão">
    <!-- Barra Unificada de Prontidão Intelectual (Substitui os 5 cards isolados de estilo SaaS) -->
    <div class="readiness-banner">
      <div class="readiness-summary">
        <div class="readiness-headline">
          <div class="readiness-pill" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2m6-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="readiness-core">
            <span class="readiness-title">
              <strong class="pending-count" data-testid="pending-review">{{ stats.pending_review }}</strong>
              {{ stats.pending_review === 1 ? 'cartão pendente' : 'cartões prontos para hoje' }}
            </span>
            <span v-if="stats.pending_review > 0" class="estimated-time">
              • ~{{ estimatedMinutes }} min sugeridos
            </span>
          </div>
        </div>

        <!-- Metadados de Distribuição Semântica (mantém identificadores para compatibilidade) -->
        <div class="readiness-breakdown">
          <span class="breakdown-item">
            <strong data-testid="total-questions">{{ stats.total_questions }}</strong> perguntas
          </span>
          <span class="breakdown-separator" aria-hidden="true">•</span>
          <span class="breakdown-item">
            <strong data-testid="total-hidden">{{ stats.total_hidden }}</strong> termos ocultos
          </span>
          <span class="breakdown-separator" aria-hidden="true">•</span>
          <span class="breakdown-item">
            <strong data-testid="reviewed-today">{{ stats.reviewed_today }}</strong> revisados hoje
          </span>
          <span class="breakdown-separator" aria-hidden="true">•</span>
          <span class="breakdown-item subtle">
            Total elegível: <span data-testid="total-eligible">{{ stats.total_eligible }}</span>
          </span>
        </div>
      </div>

      <!-- Disparador de Ação Primária Centralizado/Destacado -->
      <div class="readiness-action">
        <button
          type="button"
          class="btn-start-practice"
          data-testid="start-practice-btn"
          :disabled="loading || stats.pending_review === 0"
          @click="onStartPractice"
        >
          <svg class="practice-icon" viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          <span>Praticar Revisão Agora</span>
        </button>
      </div>
    </div>

    <!-- Barra de Filtros e Escopo -->
    <div class="filters-toolbar">
      <!-- Pílulas de Alternância Rápida de Tipo -->
      <div class="kind-filter" role="radiogroup" aria-label="Filtrar por tipo de item">
        <button
          type="button"
          class="filter-pill"
          :class="{ active: selectedKind === 'all' }"
          role="radio"
          :aria-checked="selectedKind === 'all'"
          @click="setKind('all')"
        >
          Todos
        </button>
        <button
          type="button"
          class="filter-pill"
          :class="{ active: selectedKind === 'question' }"
          role="radio"
          :aria-checked="selectedKind === 'question'"
          @click="setKind('question')"
        >
          Perguntas
        </button>
        <button
          type="button"
          class="filter-pill"
          :class="{ active: selectedKind === 'hidden' }"
          role="radio"
          :aria-checked="selectedKind === 'hidden'"
          @click="setKind('hidden')"
        >
          Termos Ocultos
        </button>
      </div>

      <!-- Seletores de Livro e Capítulo -->
      <div class="scope-selectors">
        <div class="select-field">
          <label for="review-book-select" class="sr-only">Filtrar por Livro</label>
          <select
            id="review-book-select"
            class="review-select"
            :value="selectedBookId ?? ''"
            :disabled="loading"
            @change="onBookChange"
          >
            <option value="">Todos os livros ({{ stats.total_eligible }} itens)</option>
            <option
              v-for="b in stats.books"
              :key="b.book_id"
              :value="b.book_id"
            >
              {{ b.title }} ({{ b.items_count }})
            </option>
          </select>
        </div>

        <div v-if="selectedBookId && chapters && chapters.length > 0" class="select-field">
          <label for="review-chapter-select" class="sr-only">Filtrar por Capítulo</label>
          <select
            id="review-chapter-select"
            class="review-select"
            :value="selectedChapterId ?? ''"
            :disabled="loading"
            @change="onChapterChange"
          >
            <option value="">Todos os capítulos</option>
            <option
              v-for="c in chapters"
              :key="c.id"
              :value="c.id"
            >
              {{ c.name }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.review-stats-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

/* Barra Unificada de Prontidão Intelectual */
.readiness-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem 1.75rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: var(--radius-card, 14px);
  box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.04);
}

.readiness-summary {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.readiness-headline {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.readiness-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--color-accent-subtle, rgba(59, 130, 246, 0.1));
  color: var(--color-accent, var(--color-primary, #3b82f6));
}

.readiness-core {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.readiness-title {
  font-family: var(--font-serif, "EB Garamond", Garamond, Georgia, serif);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text, #0f172a);
  letter-spacing: -0.01em;
}

.pending-count {
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--color-accent, var(--color-primary, #3b82f6));
}

.estimated-time {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  font-weight: 500;
}

.readiness-breakdown {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary, #64748b);
  flex-wrap: wrap;
}

.breakdown-item strong {
  color: var(--color-text, #0f172a);
  font-weight: 600;
}

.breakdown-item.subtle {
  opacity: 0.8;
}

.breakdown-separator {
  color: var(--color-border-strong, #cbd5e1);
}

/* Disparador de Ação Primária */
.readiness-action {
  flex-shrink: 0;
}

.btn-start-practice {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 46px;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-button, 10px);
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.08);
  transition: transform 180ms ease, opacity 180ms ease, box-shadow 180ms ease;
}

.btn-start-practice:hover:not(:disabled) {
  opacity: 0.93;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.12);
}

.btn-start-practice:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.practice-icon {
  flex-shrink: 0;
}

/* Barra de Filtros e Escopo */
.filters-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 0.75rem;
}

.kind-filter {
  display: flex;
  gap: 0.375rem;
  background-color: var(--color-surface, #ffffff);
  padding: 0.25rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
}

.filter-pill {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.filter-pill:hover {
  color: var(--color-text, #0f172a);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
}

.filter-pill.active {
  background-color: var(--color-accent, var(--color-primary, #3b82f6));
  color: var(--color-on-accent, #ffffff);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.scope-selectors {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.select-field {
  position: relative;
}

.review-select {
  min-height: 44px;
  padding: 0.5rem 2rem 0.5rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border-strong, #cbd5e1);
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text, #0f172a);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
}

.review-select:focus {
  outline: 2px solid var(--color-accent, #3b82f6);
  outline-offset: 1px;
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
  border-width: 0;
}

@media (max-width: 768px) {
  .readiness-banner {
    flex-direction: column;
    align-items: stretch;
    gap: 1.25rem;
  }

  .btn-start-practice {
    width: 100%;
    justify-content: center;
  }

  .filters-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .kind-filter {
    width: 100%;
    justify-content: space-between;
  }

  .filter-pill {
    flex: 1;
  }

  .scope-selectors {
    width: 100%;
    flex-direction: column;
  }

  .review-select {
    width: 100%;
  }
}
</style>
