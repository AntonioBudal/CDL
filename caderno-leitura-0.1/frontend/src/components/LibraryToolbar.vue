<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { BookSortOption, LibraryViewMode } from '../types'
import { useCategories } from '../composables/useCategories'
import Icon from './ui/Icon.vue'

const props = defineProps<{
  searchQuery: string
  selectedCategory?: string | null
  viewMode: LibraryViewMode
  sortBy: BookSortOption
  totalCount: number
  filteredCount: number
  hasActiveSearch: boolean
  hasActiveCategory?: boolean
  hasActiveFilters?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:searchQuery', value: string): void
  (e: 'update:selectedCategory', value: string | null): void
  (e: 'update:viewMode', value: LibraryViewMode): void
  (e: 'update:sortBy', value: BookSortOption): void
  (e: 'clearSearch'): void
  (e: 'clearCategory'): void
  (e: 'clearAllFilters'): void
}>()

const { categories, loadCategories, getCategoryById } = useCategories()

onMounted(() => {
  loadCategories()
})

const selectedCategoryName = computed(() => {
  if (!props.selectedCategory) return null
  if (props.selectedCategory === '__uncategorized__') return 'Sem categoria'
  const cat = getCategoryById(props.selectedCategory)
  return cat ? (cat.path || cat.name) : props.selectedCategory
})

const searchInput = ref<HTMLInputElement | null>(null)

function onSearchInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:searchQuery', target.value)
}

function onCategoryChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:selectedCategory', target.value || null)
}

function onSortChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit('update:sortBy', target.value as BookSortOption)
}

function handleEscape() {
  emit('clearSearch')
  searchInput.value?.focus()
}

function onClearClick() {
  emit('clearSearch')
  searchInput.value?.focus()
}
</script>

<template>
  <div class="library-toolbar panel" role="region" aria-label="Ferramentas do acervo">
    <div class="search-box-wrapper">
      <div class="search-input-group">
        <span class="search-icon" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </span>
        <input
          ref="searchInput"
          type="search"
          class="search-input"
          :value="searchQuery"
          placeholder="Buscar por título, autor ou subtítulo…"
          aria-label="Filtrar livros do acervo"
          @input="onSearchInput"
          @keydown.esc.prevent="handleEscape"
        />
        <button
          v-if="hasActiveSearch"
          type="button"
          class="search-clear-btn"
          aria-label="Limpar campo de busca"
          title="Limpar busca (Esc)"
          @click="onClearClick"
        >
          <Icon name="x" :size="14" />
        </button>
      </div>

      <p v-if="hasActiveSearch || selectedCategory || hasActiveFilters" class="search-result-count" role="status">
        Exibindo {{ filteredCount }} de {{ totalCount }} {{ totalCount === 1 ? 'livro' : 'livros' }}
        <span v-if="selectedCategoryName" class="active-category-indicator">
          · Categoria: <strong>{{ selectedCategoryName }}</strong>
        </span>
        <button
          type="button"
          class="clear-filters-btn"
          title="Limpar filtros aplicados"
          @click="emit('clearAllFilters')"
        >
          Limpar filtros
        </button>
      </p>
    </div>

    <div class="toolbar-controls">
      <div class="category-control-group">
        <label for="library-category-select" class="control-label">Categoria:</label>
        <div class="category-select-wrapper">
          <select
            id="library-category-select"
            class="category-select"
            :value="selectedCategory || ''"
            aria-label="Filtrar livros por categoria"
            @change="onCategoryChange"
          >
            <option value="">Todas as categorias</option>
            <option value="__uncategorized__">Sem categoria</option>
            <option
              v-for="cat in categories"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.path }}
            </option>
          </select>
          <button
            v-if="selectedCategory"
            type="button"
            class="category-clear-btn"
            aria-label="Limpar filtro de categoria"
            title="Limpar categoria"
            @click="emit('update:selectedCategory', null)"
          >
            <Icon name="x" :size="13" />
          </button>
        </div>
      </div>

      <div class="sort-control-group">
        <label for="library-sort-select" class="control-label">Ordenar:</label>
        <select
          id="library-sort-select"
          class="sort-select"
          :value="sortBy"
          aria-label="Critério de ordenação de livros"
          @change="onSortChange"
        >
          <option value="recent-updated">Recentemente modificados</option>
          <option value="recent-created">Recentemente adicionados</option>
          <option value="title-asc">Título (A–Z)</option>
          <option value="title-desc">Título (Z–A)</option>
          <option value="author-asc">Autor (A–Z)</option>
          <option value="year-desc">Ano de publicação</option>
          <option value="oldest-created">Mais antigos primeiro</option>
        </select>
      </div>

      <div class="view-mode-toggle" role="group" aria-label="Modo de visualização do acervo">
        <button
          type="button"
          class="view-mode-btn"
          :class="{ active: viewMode === 'grid' }"
          :aria-pressed="viewMode === 'grid'"
          title="Exibir em grade de capas"
          @click="emit('update:viewMode', 'grid')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
          <span class="view-mode-label">Grade</span>
        </button>
        <button
          type="button"
          class="view-mode-btn"
          :class="{ active: viewMode === 'list' }"
          :aria-pressed="viewMode === 'list'"
          title="Exibir em lista compacta"
          @click="emit('update:viewMode', 'list')"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="8" y1="6" x2="21" y2="6"></line>
            <line x1="8" y1="12" x2="21" y2="12"></line>
            <line x1="8" y1="18" x2="21" y2="18"></line>
            <line x1="3" y1="6" x2="3.01" y2="6"></line>
            <line x1="3" y1="12" x2="3.01" y2="12"></line>
            <line x1="3" y1="18" x2="3.01" y2="18"></line>
          </svg>
          <span class="view-mode-label">Lista</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.library-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  border-radius: var(--radius, 8px);
}

.search-box-wrapper {
  flex: 1 1 280px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--muted, #666);
  pointer-events: none;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 0.5rem 2.25rem 0.5rem 2.25rem;
  font-size: 0.95rem;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border, #ccc);
  background-color: var(--bg-surface, var(--card, #fff));
  color: var(--text, #222);
}

.search-input:focus {
  outline: 2px solid var(--accent, #3b82f6);
  outline-offset: -1px;
}

.search-clear-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  color: var(--muted, #888);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.search-clear-btn:hover {
  color: var(--text, #111);
  background-color: var(--bg-hover, rgba(0, 0, 0, 0.05));
}

.search-result-count {
  margin: 0;
  font-size: 0.82rem;
  color: var(--muted, #666);
  padding-left: 0.25rem;
}

.toolbar-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.category-control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-select-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.category-select {
  max-width: 230px;
  padding: 0.45rem 1.75rem 0.45rem 0.65rem;
  font-size: 0.9rem;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border, #ccc);
  background-color: var(--bg-surface, var(--card, #fff));
  color: var(--text, #222);
  cursor: pointer;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-select:focus {
  outline: 2px solid var(--accent, #3b82f6);
}

.category-clear-btn {
  position: absolute;
  right: 0.35rem;
  background: none;
  border: none;
  color: var(--muted, #888);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.2rem 0.35rem;
  border-radius: 4px;
}

.category-clear-btn:hover {
  color: var(--text, #111);
}

.active-category-indicator {
  margin-left: 0.25rem;
}

.clear-filters-btn {
  background: none;
  border: none;
  color: var(--accent, #3b82f6);
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.82rem;
  padding: 0 0.25rem;
  margin-left: 0.5rem;
}

.clear-filters-btn:hover {
  color: var(--accent-hover, #2563eb);
}

.sort-control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.88rem;
  color: var(--muted, #666);
  white-space: nowrap;
}

.sort-select {
  padding: 0.45rem 0.65rem;
  font-size: 0.9rem;
  border-radius: var(--radius-sm, 6px);
  border: 1px solid var(--border, #ccc);
  background-color: var(--bg-surface, var(--card, #fff));
  color: var(--text, #222);
  cursor: pointer;
}

.sort-select:focus {
  outline: 2px solid var(--accent, #3b82f6);
}

.view-mode-toggle {
  display: inline-flex;
  border: 1px solid var(--border, #ccc);
  border-radius: var(--radius-sm, 6px);
  overflow: hidden;
  background-color: var(--bg-surface, var(--card, #fff));
}

.view-mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.75rem;
  font-size: 0.85rem;
  background: transparent;
  border: none;
  color: var(--muted, #666);
  cursor: pointer;
  transition: all 0.15s ease;
}

.view-mode-btn:not(:last-child) {
  border-right: 1px solid var(--border, #ccc);
}

.view-mode-btn.active {
  background-color: var(--accent, #3b82f6);
  color: var(--accent-text, #fff);
  font-weight: 600;
}

.view-mode-btn:hover:not(.active) {
  background-color: var(--bg-hover, rgba(0, 0, 0, 0.05));
  color: var(--text, #111);
}

@media (max-width: 640px) {
  .library-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-controls {
    justify-content: space-between;
    width: 100%;
    gap: 0.75rem;
  }

  .category-control-group {
    width: 100%;
  }

  .category-select-wrapper {
    flex: 1;
    width: 100%;
  }

  .category-select {
    width: 100%;
    max-width: 100%;
  }

  .sort-control-group {
    flex: 1;
  }

  .sort-select {
    width: 100%;
  }
}
</style>
