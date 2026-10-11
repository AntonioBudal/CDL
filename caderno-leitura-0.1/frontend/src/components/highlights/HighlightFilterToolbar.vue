<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type {
  HighlightColor,
  HighlightKind,
  HighlightLibraryFilterOption,
  HighlightLibrarySummary,
  HighlightViewMode,
} from '../../types'
import { HIGHLIGHT_SEMANTIC_CATEGORIES } from '../../types'
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

const semanticCategoriesList = computed(() => {
  return (Object.keys(HIGHLIGHT_SEMANTIC_CATEGORIES) as HighlightColor[]).map((key) => {
    return HIGHLIGHT_SEMANTIC_CATEGORIES[key]
  })
})
const colorsList = semanticCategoriesList

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
          <Icon name="x" :size="14" aria-hidden="true" />
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
          <Icon name="list" :size="16" aria-hidden="true" />
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
          <Icon name="book-open" :size="16" aria-hidden="true" />
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
        <Icon name="sliders" :size="18" aria-hidden="true" />
        <span>Filtros</span>
        <span v-if="activeFilterCount > 0" class="filter-count-badge">
          {{ activeFilterCount }}
        </span>
      </button>
    </div>

    <!-- Linha Secundária: Filtros por Livro, Tipo, Categorias Semânticas e Botão Limpar -->
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

      <!-- Categorias Intelectuais de Grifo -->
      <div class="filter-control filter-categories" role="group" aria-label="Filtrar por intenção de estudo">
        <span class="filter-label">Intenção:</span>
        <div class="category-pills color-swatches">
          <button
            type="button"
            class="pill-btn swatch-btn pill-all"
            :class="{ 'is-selected': selectedColor === null }"
            title="Todas as categorias de grifo"
            aria-label="Todas as categorias de grifo"
            @click="onColorChange(null)"
          >
            Todas
          </button>
          <button
            v-for="cat in colorsList"
            :key="cat.key"
            type="button"
            class="pill-btn swatch-btn pill-category"
            :class="[`pill-${cat.key}`, { 'is-selected': selectedColor === cat.key }]"
            :title="`${cat.semanticName} (${cat.label}): ${cat.description}`"
            :aria-label="`Filtrar por ${cat.semanticName} (destaques em ${cat.label})`"
            @click="onColorChange(selectedColor === cat.key ? null : cat.key)"
          >
            <span class="pill-dot" aria-hidden="true" />
            <span class="pill-name">{{ cat.semanticName }}</span>
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
          <Icon name="rotate-ccw" :size="14" aria-hidden="true" />
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
  padding: 1rem 1.25rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, var(--color-border, #e2e8f0));
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  margin-bottom: 1.5rem;
}

/* Linha Principal */
.toolbar-primary-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex-grow: 1;
  min-width: 220px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--color-text-secondary, #64748b);
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 2rem 0 2.25rem;
  font-size: 0.875rem;
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  outline: none;
  transition: all 0.15s ease;
}

.search-input:focus {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-accent, var(--color-primary, #2563eb));
  box-shadow: 0 0 0 2px var(--ring-focus, rgba(37, 99, 235, 0.2));
}

.btn-clear-search {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  padding: 0.25rem;
  color: var(--color-text-secondary, #94a3b8);
  cursor: pointer;
  border-radius: 4px;
}

.btn-clear-search:hover {
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface-hover, #e2e8f0);
}

/* Alternador de Modo de Visualização */
.view-mode-toggle {
  display: inline-flex;
  align-items: center;
  background-color: var(--color-surface-soft, #f1f5f9);
  padding: 0.2rem;
  border-radius: 6px;
  border: 1px solid var(--color-border-subtle, #e2e8f0);
  flex-shrink: 0;
}

.btn-mode {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 32px;
}

.btn-mode:hover {
  color: var(--color-text-primary, #0f172a);
}

.btn-mode.is-active {
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #0f172a);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  font-weight: 600;
}

/* Botão Mobile */
.btn-mobile-filter-toggle {
  display: none;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface-soft, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  cursor: pointer;
}

.filter-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  font-size: 0.7rem;
  font-weight: 600;
  background-color: var(--color-accent, var(--color-primary, #2563eb));
  color: var(--color-on-accent, #ffffff);
  border-radius: 9999px;
}

/* Linha Secundária de Filtros */
.toolbar-filters-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.25rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border-subtle, #f1f5f9);
}

.filter-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  white-space: nowrap;
}

.filter-select {
  height: 32px;
  padding: 0 1.75rem 0 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-text-primary, #0f172a);
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  cursor: pointer;
  outline: none;
  max-width: 200px;
}

.filter-select:focus {
  border-color: var(--color-accent, var(--color-primary, #2563eb));
  box-shadow: 0 0 0 2px var(--ring-focus, rgba(37, 99, 235, 0.2));
}

/* Pílulas de Categorias Intelectuais de Grifo */
.category-pills {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  height: 30px;
  padding: 0 0.6rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
  border: 1px solid var(--color-border, #cbd5e1);
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.pill-btn:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft, #f1f5f9));
  color: var(--color-text-primary, #0f172a);
}

.pill-btn.is-selected {
  background-color: var(--color-surface-soft, #f1f5f9);
  color: var(--color-text-primary, #0f172a);
  border-color: var(--color-accent, var(--color-primary, #0f172a));
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  background-color: currentColor;
}

.pill-yellow .pill-dot { color: #eab308; }
.pill-green .pill-dot { color: #22c55e; }
.pill-blue .pill-dot { color: #3b82f6; }
.pill-pink .pill-dot { color: #ec4899; }
.pill-purple .pill-dot { color: #a855f7; }

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
  padding: 0 0.65rem;
  height: 30px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-reset-filters:hover {
  background-color: var(--color-surface-hover, var(--color-surface-soft, #f1f5f9));
  border-color: var(--color-border-hover, #94a3b8);
  color: var(--color-text-primary, #0f172a);
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

  .category-pills {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .pill-all,
  .pill-category {
    min-height: 44px;
    padding: 0 0.75rem;
  }

  .btn-reset-filters {
    width: 100%;
    justify-content: center;
    min-height: 44px;
    font-size: 0.875rem;
  }
}
</style>
