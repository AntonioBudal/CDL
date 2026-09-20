<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../../services/api.ts'
import { useGlobalSearch } from '../../composables/useGlobalSearch.ts'
import Icon from '../ui/Icon.vue'
import SearchResultItem from './SearchResultItem.vue'
import SearchHistoryList from './SearchHistoryList.vue'
import type { Book, Category, SearchMatchItem } from '../../types.ts'

const router = useRouter()
const {
  isOpen,
  query,
  mode,
  bookId,
  categoryId,
  results,
  total,
  suggestOr,
  isLoading,
  error,
  history,
  isLoadingHistory,
  closeSearch,
  onQueryChange,
  setMode,
  setBookFilter,
  setCategoryFilter,
  clearFilters,
  removeHistoryItem,
  clearHistory,
  selectHistoryTerm,
  selectResult,
} = useGlobalSearch()

const inputRef = ref<HTMLInputElement | null>(null)
const selectedIndex = ref<number>(-1)
const booksList = ref<Book[]>([])
const categoriesList = ref<Category[]>([])
const showFilters = ref(false)

const hasActiveFilters = computed(() => {
  return bookId.value !== null || categoryId.value !== null || mode.value !== 'and'
})

async function loadFilterOptions() {
  try {
    const [books, cats] = await Promise.all([
      api.listBooks(),
      api.listCategories(),
    ])
    booksList.value = books || []
    categoriesList.value = cats || []
  } catch {
    // Falha silenciosa nos filtros
  }
}

watch(isOpen, async (open) => {
  if (open) {
    selectedIndex.value = -1
    await nextTick()
    inputRef.value?.focus()
    loadFilterOptions()
  }
})

watch(results, () => {
  selectedIndex.value = results.value.length > 0 ? 0 : -1
})

function handleGlobalKeydown(e: KeyboardEvent) {
  // Atalho global Ctrl+K ou / para abrir a busca
  if (!isOpen.value) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault()
      isOpen.value = true
    } else if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
      e.preventDefault()
      isOpen.value = true
    }
    return
  }

  // Comandos com modal aberto
  if (e.key === 'Escape') {
    e.preventDefault()
    closeSearch()
  } else if (e.key === 'ArrowDown') {
    if (results.value.length > 0) {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value + 1) % results.value.length
      scrollToSelected()
    }
  } else if (e.key === 'ArrowUp') {
    if (results.value.length > 0) {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value - 1 + results.value.length) % results.value.length
      scrollToSelected()
    }
  } else if (e.key === 'Enter') {
    if (selectedIndex.value >= 0 && selectedIndex.value < results.value.length) {
      e.preventDefault()
      onSelect(results.value[selectedIndex.value])
    }
  }
}

function scrollToSelected() {
  nextTick(() => {
    const el = document.querySelector('.search-result-item.is-selected')
    if (el) {
      el.scrollIntoView({ block: 'nearest' })
    }
  })
}

function onSelect(item: SearchMatchItem) {
  selectResult(item, router)
}

function clearQuery() {
  onQueryChange('')
  inputRef.value?.focus()
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="search-modal-root overflow-x-hidden"
      role="dialog"
      aria-modal="true"
      aria-label="Busca global de estudos"
    >
      <!-- Backdrop escuro translúcido com desfoque -->
      <div
        class="search-modal-backdrop"
        @click="closeSearch"
      />

      <!-- Container / Diálogo do Modal -->
      <div
        class="search-modal-dialog overflow-x-hidden"
      >
        <!-- Cabeçalho com Campo de Busca -->
        <div class="search-header">
          <div class="search-input-wrapper">
            <Icon
              name="search"
              :size="18"
              class="search-input-icon"
            />
            <input
              ref="inputRef"
              :value="query"
              type="text"
              placeholder="Buscar em estudos, notas, conceitos, títulos..."
              class="search-input min-h-[44px]"
              aria-autocomplete="list"
              aria-controls="search-results-list"
              @input="onQueryChange(($event.target as HTMLInputElement).value)"
            />
            <button
              v-if="query"
              type="button"
              class="search-clear-btn"
              aria-label="Limpar termo de busca"
              @click="clearQuery"
            >
              <Icon name="x" :size="14" />
            </button>
          </div>

          <!-- Botão de Filtros -->
          <button
            type="button"
            class="filter-toggle-btn min-h-[44px]"
            :class="{ 'is-active': showFilters || hasActiveFilters }"
            :aria-expanded="showFilters"
            aria-label="Alternar filtros de busca"
            @click="showFilters = !showFilters"
          >
            <Icon name="sliders" :size="14" />
            <span class="filter-label">Filtros</span>
            <span
              v-if="hasActiveFilters"
              class="filter-dot"
            />
          </button>

          <!-- Botão Fechar Modal -->
          <button
            type="button"
            class="modal-close-btn min-h-[44px] min-w-[44px]"
            aria-label="Fechar busca"
            @click="closeSearch"
          >
            <Icon name="x" :size="16" />
          </button>
        </div>

        <!-- Painel de Filtros Expansível -->
        <div
          v-if="showFilters"
          class="filters-panel"
        >
          <div class="filters-grid">
            <!-- Filtro de Livro -->
            <div class="filter-group">
              <label class="filter-label-heading">
                Livro Específico
              </label>
              <select
                :value="bookId ?? ''"
                class="filter-select min-h-[44px]"
                @change="setBookFilter(($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
              >
                <option value="">Todas as obras</option>
                <option v-for="b in booksList" :key="b.id" :value="b.id">
                  {{ b.title }}
                </option>
              </select>
            </div>

            <!-- Filtro de Categoria Taxonômica -->
            <div class="filter-group">
              <label class="filter-label-heading">
                Categoria Taxonômica
              </label>
              <select
                :value="categoryId ?? ''"
                class="filter-select min-h-[44px]"
                @change="setCategoryFilter(($event.target as HTMLSelectElement).value || null)"
              >
                <option value="">Todas as categorias</option>
                <option v-for="cat in categoriesList" :key="cat.id" :value="cat.id">
                  {{ cat.path }}
                </option>
              </select>
            </div>
          </div>

          <!-- Modo de Combinação e Limpeza -->
          <div class="filter-modes-row">
            <div class="mode-buttons-group">
              <span class="mode-label">Modo de termos:</span>
              <button
                type="button"
                class="mode-btn min-h-[36px]"
                :class="{ 'is-active': mode === 'and' }"
                @click="setMode('and')"
              >
                AND (Estrito)
              </button>
              <button
                type="button"
                class="mode-btn min-h-[36px]"
                :class="{ 'is-active': mode === 'or' }"
                @click="setMode('or')"
              >
                OR (Abrangente)
              </button>
            </div>

            <button
              v-if="hasActiveFilters"
              type="button"
              class="clear-filters-btn min-h-[36px]"
              @click="clearFilters"
            >
              Limpar filtros
            </button>
          </div>
        </div>

        <!-- Área de Conteúdo / Resultados -->
        <div class="search-body">
          <!-- Alerta de Erro -->
          <div
            v-if="error"
            class="search-error-alert"
          >
            {{ error }}
          </div>

          <!-- Estado de Carregamento -->
          <div
            v-if="isLoading"
            class="search-loading-state"
          >
            <div class="search-spinner" />
            <span>Buscando no acervo de estudos...</span>
          </div>

          <!-- Histórico Recente quando input vazio -->
          <div v-else-if="!query.trim()">
            <SearchHistoryList
              :items="history"
              :is-loading="isLoadingHistory"
              @select="selectHistoryTerm"
              @remove="removeHistoryItem"
              @clear="clearHistory"
            />
          </div>

          <!-- Menos de 2 caracteres -->
          <div
            v-else-if="query.trim().length === 1"
            class="search-hint-state"
          >
            Digite no mínimo 2 caracteres para pesquisar.
          </div>

          <!-- Sugestão assistida de modo OR (quando AND não encontra resultados) -->
          <div
            v-else-if="results.length === 0 && suggestOr"
            class="search-suggest-or"
          >
            <p class="suggest-or-text">
              Nenhum estudo contém todos os termos juntos no modo estrito.
            </p>
            <button
              type="button"
              class="suggest-or-btn min-h-[38px]"
              @click="setMode('or')"
            >
              Buscar estudos com qualquer um dos termos (Modo OR)
            </button>
          </div>

          <!-- Nenhum resultado encontrado -->
          <div
            v-else-if="results.length === 0"
            class="search-empty-state"
          >
            <Icon name="search" :size="28" class="empty-icon" />
            <p class="empty-title">Nenhum resultado encontrado</p>
            <p class="empty-desc">
              Verifique a ortografia do termo ou experimente palavras-chave mais gerais.
            </p>
          </div>

          <!-- Lista de Resultados Encontrados -->
          <div v-else id="search-results-list" class="search-results-list">
            <div
              class="search-results-header"
              aria-live="polite"
            >
              <span>{{ total }} {{ total === 1 ? 'estudo encontrado' : 'estudos encontrados' }}</span>
              <span class="results-shortcut-hint">Use ↑ ↓ para navegar e Enter para abrir</span>
            </div>

            <SearchResultItem
              v-for="(item, idx) in results"
              :key="item.study_id"
              :item="item"
              :is-selected="idx === selectedIndex"
              @select="onSelect"
            />
          </div>
        </div>

        <!-- Rodapé do Modal -->
        <div class="search-footer">
          <div class="footer-shortcuts">
            <span><kbd class="kbd-badge">↑</kbd> <kbd class="kbd-badge">↓</kbd> Navegar</span>
            <span><kbd class="kbd-badge">Enter</kbd> Selecionar</span>
            <span><kbd class="kbd-badge">Esc</kbd> Fechar</span>
          </div>
          <span class="footer-brand">Busca local integrada</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.search-modal-root {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 15vh;
  box-sizing: border-box;
}

.search-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  transition: opacity 0.2s ease;
}

.search-modal-dialog {
  position: relative;
  z-index: 10;
  width: min(640px, 92vw);
  max-height: 75vh;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--sc-border-radius, var(--radius-card, 10px));
  box-shadow: var(--sc-box-shadow, 0 20px 35px -5px rgba(0, 0, 0, 0.35));
  overflow: hidden;
  box-sizing: border-box;
}

.search-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.search-input-icon {
  position: absolute;
  left: 0.75rem;
  color: var(--color-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.6rem 2.25rem 0.6rem 2.5rem;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  font-size: 0.9375rem;
  color: var(--color-text);
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.search-input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 20%, transparent);
}

.search-clear-btn {
  position: absolute;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  border-radius: 50%;
}

.search-clear-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.filter-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-toggle-btn:hover {
  color: var(--color-text);
  border-color: var(--color-border-hover, var(--color-accent));
}

.filter-toggle-btn.is-active {
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.filter-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
}

.modal-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-close-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.filters-panel {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  font-size: 0.8125rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  flex-shrink: 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-label-heading {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-muted);
  letter-spacing: 0.03em;
}

.filter-select {
  width: 100%;
  padding: 0.4rem 0.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  color: var(--color-text);
  font-size: 0.8125rem;
}

.filter-modes-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 0.25rem;
}

.mode-buttons-group {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.mode-label {
  font-size: 0.75rem;
  color: var(--color-muted);
  margin-right: 0.25rem;
}

.mode-btn {
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-control, 4px);
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-btn:hover {
  color: var(--color-text);
}

.mode-btn.is-active {
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  border-color: var(--color-accent);
  color: var(--color-accent);
  font-weight: 600;
}

.clear-filters-btn {
  font-size: 0.75rem;
  color: var(--color-muted);
  text-decoration: underline;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
}

.clear-filters-btn:hover {
  color: var(--color-text);
}

.search-body {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 0.85rem 1rem;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-error-alert {
  padding: 0.75rem;
  border-radius: var(--radius-control, 6px);
  background: var(--color-error-bg, rgba(220, 38, 38, 0.08));
  color: var(--color-error-text, #dc2626);
  font-size: 0.8125rem;
  border: 1px solid var(--color-error-border, rgba(220, 38, 38, 0.2));
}

.search-loading-state {
  padding: 2.5rem 0;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.search-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-accent);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-hint-state {
  padding: 2rem 0;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.search-suggest-or {
  padding: 1rem;
  border-radius: var(--radius-control, 6px);
  background: var(--color-warning-bg, rgba(245, 158, 11, 0.08));
  border: 1px solid var(--color-warning-border, rgba(245, 158, 11, 0.3));
  color: var(--color-warning-text, #b45309);
  font-size: 0.8125rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.suggest-or-text {
  margin: 0;
  font-weight: 500;
}

.suggest-or-btn {
  align-self: flex-start;
  padding: 0.4rem 0.75rem;
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
  border-radius: var(--radius-control, 4px);
  font-weight: 600;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.suggest-or-btn:hover {
  background: color-mix(in srgb, var(--color-accent) 25%, var(--color-surface));
}

.search-empty-state {
  padding: 2.5rem 0;
  text-align: center;
  color: var(--color-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  margin-bottom: 0.5rem;
  opacity: 0.4;
}

.empty-title {
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
  font-size: 0.9375rem;
}

.empty-desc {
  font-size: 0.8125rem;
  color: var(--color-muted);
  max-width: 320px;
  margin: 0;
}

.search-results-list {
  display: flex;
  flex-direction: column;
}

.search-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-muted);
  padding: 0 0.25rem 0.4rem;
}

.results-shortcut-hint {
  font-size: 0.6875rem;
}

.search-footer {
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  font-size: 0.75rem;
  color: var(--color-muted);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.footer-shortcuts {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.kbd-badge {
  display: inline-block;
  padding: 0.1rem 0.35rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text);
  font-family: monospace;
  font-size: 0.6875rem;
}

.footer-brand {
  opacity: 0.7;
}

@media (max-width: 640px) {
  .search-modal-root {
    padding-top: 1rem;
  }
  .filter-label {
    display: none;
  }
  .results-shortcut-hint {
    display: none;
  }
  .search-footer {
    display: none;
  }
}
</style>
