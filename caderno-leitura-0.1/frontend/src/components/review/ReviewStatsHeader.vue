<script setup lang="ts">
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
}>()

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
</script>

<template>
  <header class="review-stats-header" role="region" aria-label="Painel de Métricas e Filtros de Revisão">
    <!-- Grade de Métricas Resumidas -->
    <div class="metrics-grid">
      <div class="metric-card metric-total">
        <span class="metric-label">Total Elegível</span>
        <span class="metric-value" data-testid="total-eligible">{{ stats.total_eligible }}</span>
        <span class="metric-caption">Destaques interativos</span>
      </div>

      <div class="metric-card metric-questions">
        <span class="metric-label">Perguntas</span>
        <span class="metric-value" data-testid="total-questions">{{ stats.total_questions }}</span>
        <span class="metric-caption">Fixação ativa</span>
      </div>

      <div class="metric-card metric-hidden">
        <span class="metric-label">Termos Ocultos</span>
        <span class="metric-value" data-testid="total-hidden">{{ stats.total_hidden }}</span>
        <span class="metric-caption">Clozes na leitura</span>
      </div>

      <div class="metric-card metric-reviewed">
        <span class="metric-label">Revisados Hoje</span>
        <span class="metric-value" data-testid="reviewed-today">{{ stats.reviewed_today }}</span>
        <span class="metric-caption">Itens praticados</span>
      </div>

      <div class="metric-card metric-pending">
        <span class="metric-label">Pendentes</span>
        <span class="metric-value" data-testid="pending-review">{{ stats.pending_review }}</span>
        <span class="metric-caption">Aguardando rodada</span>
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
}

.metric-card {
  display: flex;
  flex-direction: column;
  padding: 1rem 1.125rem;
  border-radius: 0.75rem;
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted, #64748b);
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-text-primary, #0f172a);
}

.metric-caption {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #94a3b8);
  margin-top: 0.25rem;
}

.metric-total .metric-value {
  color: var(--color-primary, #2563eb);
}

.metric-reviewed .metric-value {
  color: #16a34a;
}

.filters-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background-color: var(--color-bg-surface-secondary, #f8fafc);
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  border-radius: 0.75rem;
}

.kind-filter {
  display: flex;
  gap: 0.375rem;
  background-color: var(--color-bg-surface, #ffffff);
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
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-bg-hover, #f1f5f9);
}

.filter-pill.active {
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
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
  border: 1px solid var(--color-border-subtle, #cbd5e1);
  background-color: var(--color-bg-surface, #ffffff);
  color: var(--color-text-primary, #0f172a);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 1rem;
}

.review-select:focus {
  outline: 2px solid var(--color-primary, #2563eb);
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

@media (max-width: 640px) {
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
