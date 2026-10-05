<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type {
  HighlightColor,
  HighlightKind,
  HighlightLibraryFilterOption,
  HighlightLibrarySummary,
  HighlightViewMode,
} from '../../types'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    searchQuery?: string
    selectedBookId?: number | null
    selectedKind?: string | null
    selectedColor?: string | null
    viewMode?: HighlightViewMode
    availableBooks?: HighlightLibraryFilterOption[]
    summary?: HighlightLibrarySummary | null
    totalCount?: number
  }>(),
  {
    searchQuery: '',
    selectedBookId: null,
    selectedKind: null,
    selectedColor: null,
    viewMode: 'recent',
    availableBooks: () => [],
    summary: null,
    totalCount: 0,
  }
)

const emit = defineEmits<{
  (e: 'update:searchQuery', val: string): void
  (e: 'update:selectedBookId', val: number | null): void
  (e: 'update:selectedKind', val: string | null): void
  (e: 'update:selectedColor', val: string | null): void
  (e: 'update:viewMode', val: HighlightViewMode): void
  (e: 'reset-filters'): void
}>()

// Debounce de busca de 250ms
const localSearch = ref(props.searchQuery)
let debounceTimeout: ReturnType<typeof setTimeout> | null = null

watch(
  () => props.searchQuery,
  (newVal) => {
    if (newVal !== localSearch.value) {
      localSearch.value = newVal
    }
  }
)

function onSearchInput(e: Event) {
  const target = e.target as HTMLInputElement
  localSearch.value = target.value
  if (debounceTimeout) clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    emit('update:searchQuery', localSearch.value.trim())
  }, 250)
}

function clearSearch() {
  localSearch.value = ''
  if (debounceTimeout) clearTimeout(debounceTimeout)
  emit('update:searchQuery', '')
}

// Filtros
function onBookChange(e: Event) {
  const target = e.target as HTMLSelectElement
  const val = target.value ? Number(target.value) : null
  emit('update:selectedBookId', val)
}

function onKindChange(e: Event) {
  const target = e.target as HTMLSelectElement
  const val = target.value ? target.value : null
  emit('update:selectedKind', val)
}

function onColorChange(color: HighlightColor | null) {
  emit('update:selectedColor', color)
}

const colorsList: { key: HighlightColor; label: string; hex: string }[] = [
  { key: 'yellow', label: 'Amarelo', hex: '#eab308' },
  { key: 'green', label: 'Verde', hex: '#22c55e' },
  { key: 'blue', label: 'Azul', hex: '#3b82f6' },
  { key: 'pink', label: 'Rosa', hex: '#ec4899' },
  { key: 'purple', label: 'Roxo', hex: '#a855f7' },
]

const kindsList: { key: HighlightKind; label: string }[] = [
  { key: 'highlight', label: 'Destaques' },
  { key: 'note', label: 'Anotações' },
  { key: 'quote', label: 'Citações' },
  { key: 'question', label: 'Perguntas' },
  { key: 'hidden', label: 'Termos Ocultos' },
]

function getKindCount(kind: HighlightKind): number | null {
  if (!props.summary) return null
  switch (kind) {
    case 'highlight': return props.summary.total_highlights
    case 'note': return props.summary.total_notes
    case 'quote': return props.summary.total_quotes
    case 'question': return props.summary.total_questions
    case 'hidden': return props.summary.total_hidden
    default: return null
  }
}

const hasActiveFilters = computed(() => {
  return Boolean(
    props.searchQuery ||
    props.selectedBookId !== null ||
    props.selectedKind !== null ||
    props.selectedColor !== null
  )
})

const activeFilterCount = computed(() => {
  let count = 0
  if (props.selectedBookId !== null) count++
  if (props.selectedKind !== null) count++
  if (props.selectedColor !== null) count++
  if (props.searchQuery.trim().length > 0) count++
  return count
})

// Gaveta móvel de filtros
const mobileDrawerOpen = ref(false)
</script>

<template>
  <div class="highlight-filter-toolbar">
    <!-- Linha Principal: Busca, Alternador de Modo e Botão de Gaveta Mobile -->
    <div class="toolbar-primary-row">
      <!-- Campo de Busca Instantânea com Debounce -->
      <div class="search-input-wrapper">
        <Icon name="search" :size="16" class="search-icon" aria-hidden="true" />
        <input
          :value="localSearch"
          type="search"
          class="search-input"
          placeholder="Buscar no texto ou anotações..."
          aria-label="Buscar destaques e anotações"
          @input="onSearchInput"
        />
        <button
          v-if="localSearch"
          type="button"
          class="btn-clear-search"
          aria-label="Limpar busca"
          title="Limpar busca"
          @click="clearSearch"
        >
          <Icon name="x" :size="14" />
        </button>
      </div>

      <!-- Alternador de Modo: "Recentes" vs "Por Obra" -->
      <div class="view-mode-toggle" role="group" aria-label="Modo de visualização">
        <button
          type="button"
          class="btn-mode"
          :class="{ 'is-active': viewMode === 'recent' }"
          :aria-pressed="viewMode === 'recent'"
          title="Exibir em ordem cronológica de criação"
          @click="emit('update:viewMode', 'recent')"
        >
          <Icon name="list" :size="16" />
          <span class="mode-label">Recentes</span>
        </button>
        <button
          type="button"
          class="btn-mode"
          :class="{ 'is-active': viewMode === 'by_book' }"
          :aria-pressed="viewMode === 'by_book'"
          title="Exibir agrupado por livro e obra"
          @click="emit('update:viewMode', 'by_book')"
        >
          <Icon name="book-open" :size="16" />
          <span class="mode-label">Por Obra</span>
        </button>
      </div>

      <!-- Botão para Abrir Gaveta de Filtros no Mobile -->
      <button
        type="button"
        class="btn-mobile-filter-toggle"
        :class="{ 'has-filters': activeFilterCount > 0 }"
        :aria-expanded="mobileDrawerOpen"
        aria-label="Abrir opções de filtro"
        @click="mobileDrawerOpen = !mobileDrawerOpen"
      >
        <Icon name="sliders" :size="18" />
        <span>Filtros</span>
        <span v-if="activeFilterCount > 0" class="filter-count-badge">
          {{ activeFilterCount }}
        </span>
      </button>
    </div>

    <!-- Linha Secundária: Filtros por Livro, Tipo, Cores e Botão Limpar (Desktop e gaveta móvel) -->
    <div
      class="toolbar-filters-row"
      :class="{ 'mobile-open': mobileDrawerOpen }"
    >
      <!-- Seletor de Livro / Obra -->
      <div class="filter-control filter-book">
        <label for="filter-book-select" class="filter-label">Obra:</label>
        <select
          id="filter-book-select"
          class="filter-select"
          :value="selectedBookId ?? ''"
          aria-label="Filtrar por livro"
          @change="onBookChange"
        >
          <option value="">Todas as Obras ({{ totalCount }})</option>
          <option
            v-for="b in availableBooks"
            :key="b.id"
            :value="b.id"
          >
            {{ b.title }} ({{ b.count }})
          </option>
        </select>
      </div>

      <!-- Seletor de Tipo de Marcação -->
      <div class="filter-control filter-kind">
        <label for="filter-kind-select" class="filter-label">Tipo:</label>
        <select
          id="filter-kind-select"
          class="filter-select"
          :value="selectedKind ?? ''"
          aria-label="Filtrar por tipo"
          @change="onKindChange"
        >
          <option value="">Todos os Tipos</option>
          <option
            v-for="k in kindsList"
            :key="k.key"
            :value="k.key"
          >
            {{ k.label }}
            <template v-if="getKindCount(k.key) !== null">
              ({{ getKindCount(k.key) }})
            </template>
          </option>
        </select>
      </div>

      <!-- Paleta Cromática de Cores -->
      <div class="filter-control filter-colors" role="radiogroup" aria-label="Filtrar por cor">
        <span class="filter-label">Cor:</span>
        <div class="color-swatches">
          <button
            type="button"
            class="swatch-btn swatch-all"
            :class="{ 'is-selected': selectedColor === null }"
            title="Todas as cores"
            aria-label="Todas as cores"
            @click="onColorChange(null)"
          >
            Todas
          </button>
          <button
            v-for="c in colorsList"
            :key="c.key"
            type="button"
            class="swatch-btn swatch-color"
            :class="[`swatch-${c.key}`, { 'is-selected': selectedColor === c.key }]"
            :title="`Filtrar por ${c.label}`"
            :aria-label="`Filtrar por cor ${c.label}`"
            @click="onColorChange(selectedColor === c.key ? null : c.key)"
          >
            <span class="swatch-circle" :style="{ backgroundColor: c.hex }" />
          </button>
        </div>
      </div>

      <!-- Botão de Limpar Filtros -->
      <div v-if="hasActiveFilters" class="filter-control filter-reset">
        <button
          type="button"
          class="btn-reset-filters"
          title="Limpar todos os filtros ativos"
          aria-label="Limpar filtros"
          @click="emit('reset-filters')"
        >
          <Icon name="rotate-ccw" :size="14" />
          <span>Limpar</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.highlight-filter-toolbar {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

/* Linha Principal */
.toolbar-primary-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 240px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--color-text-muted, #a1a1aa);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 2rem 0 2.25rem;
  border: 1px solid var(--color-border, #d4d4d8);
  border-radius: 6px;
  background-color: var(--color-surface-subtle, #f8fafc);
  color: var(--color-text-primary, #0f172a);
  font-size: 0.875rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-surface, #ffffff);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.btn-clear-search {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: none;
  border: none;
  border-radius: 50%;
  color: var(--color-text-muted, #a1a1aa);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.btn-clear-search:hover {
  background-color: var(--color-surface-hover, #e2e8f0);
  color: var(--color-text-primary, #0f172a);
}

/* Alternador de Modo */
.view-mode-toggle {
  display: inline-flex;
  background-color: var(--color-surface-subtle, #f1f5f9);
  padding: 3px;
  border-radius: 6px;
  border: 1px solid var(--color-border, #e2e8f0);
}

.btn-mode {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  border: none;
  border-radius: 4px;
  background: none;
  color: var(--color-text-secondary, #64748b);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 32px;
}

.btn-mode.is-active {
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #0f172a);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  font-weight: 600;
}

.btn-mode:hover:not(.is-active) {
  color: var(--color-text-primary, #0f172a);
}

/* Botão Mobile de Toggle */
.btn-mobile-filter-toggle {
  display: none;
  align-items: center;
  gap: 0.4rem;
  background-color: var(--color-surface-subtle, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary, #475569);
  cursor: pointer;
  min-height: 44px;
}

.filter-count-badge {
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 9999px;
  padding: 0.1rem 0.4rem;
  line-height: 1;
}

/* Linha de Filtros */
.toolbar-filters-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding-top: 0.65rem;
  border-top: 1px solid var(--color-border-subtle, #f1f5f9);
}

.filter-control {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  white-space: nowrap;
}

.filter-select {
  height: 34px;
  padding: 0 0.65rem;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #0f172a);
  font-size: 0.8125rem;
  cursor: pointer;
  max-width: 220px;
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

/* Cores */
.color-swatches {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.swatch-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.swatch-all {
  height: 28px;
  padding: 0 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  background-color: var(--color-surface-subtle, #f8fafc);
}

.swatch-all.is-selected {
  background-color: var(--color-text-primary, #0f172a);
  color: #ffffff;
  border-color: var(--color-text-primary, #0f172a);
}

.swatch-color {
  width: 28px;
  height: 28px;
  padding: 0;
  border-radius: 50%;
}

.swatch-circle {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: block;
}

.swatch-color.is-selected {
  border-color: var(--color-text-primary, #0f172a);
  box-shadow: 0 0 0 2px var(--color-primary, #2563eb);
}

/* Botão Limpar Filtros */
.filter-reset {
  margin-left: auto;
}

.btn-reset-filters {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: none;
  border: 1px dashed var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.3rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  height: 32px;
  transition: all 0.15s ease;
}

.btn-reset-filters:hover {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #ef4444;
}

/* Responsividade Móvel */
@media (max-width: 768px) {
  .btn-mobile-filter-toggle {
    display: inline-flex;
  }

  .view-mode-toggle {
    flex-grow: 1;
    justify-content: center;
  }

  .btn-mode {
    flex: 1;
    justify-content: center;
    min-height: 44px;
  }

  .search-input {
    min-height: 44px;
    font-size: 1rem;
  }

  .toolbar-filters-row {
    display: none;
    flex-direction: column;
    align-items: stretch;
    gap: 0.85rem;
    padding-top: 0.85rem;
  }

  .toolbar-filters-row.mobile-open {
    display: flex;
  }

  .filter-control {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .filter-select {
    width: 100%;
    max-width: none;
    min-height: 44px;
    font-size: 0.9375rem;
  }

  .color-swatches {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .swatch-all,
  .swatch-color {
    min-height: 44px;
    min-width: 44px;
  }

  .btn-reset-filters {
    width: 100%;
    justify-content: center;
    min-height: 44px;
    font-size: 0.875rem;
  }
}
</style>
