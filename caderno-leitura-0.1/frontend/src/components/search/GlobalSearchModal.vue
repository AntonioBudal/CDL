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
    const el = document.querySelector('.search-result-item.bg-accent\\/15')
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
      class="fixed inset-0 z-50 flex items-start justify-center p-0 sm:p-4 md:p-6 overflow-x-hidden"
      role="dialog"
      aria-modal="true"
      aria-label="Busca global de estudos"
    >
      <!-- Backdrop escuro -->
      <div
        class="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        @click="closeSearch"
      />

      <!-- Container do Modal -->
      <div
        class="relative w-full max-w-2xl bg-card border border-border shadow-2xl rounded-none sm:rounded-xl overflow-hidden flex flex-col h-full sm:h-auto sm:max-h-[85vh] z-10 transition-all overflow-x-hidden"
      >
        <!-- Cabeçalho com Campo de Busca -->
        <div class="p-3.5 border-b border-border bg-card/95 sticky top-0 z-20 flex items-center gap-2">
          <div class="relative flex-1 flex items-center">
            <Icon
              name="search"
              :size="18"
              class="absolute left-3 text-muted-foreground/70 pointer-events-none"
            />
            <input
              ref="inputRef"
              :value="query"
              type="text"
              placeholder="Buscar em estudos, notas, conceitos, títulos..."
              class="w-full pl-10 pr-9 py-2.5 bg-background border border-border/80 rounded-lg text-sm text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-accent min-h-[44px]"
              aria-autocomplete="list"
              aria-controls="search-results-list"
              @input="onQueryChange(($event.target as HTMLInputElement).value)"
            />
            <button
              v-if="query"
              type="button"
              class="absolute right-2 p-1.5 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors min-w-[32px] min-h-[32px] flex items-center justify-center cursor-pointer"
              aria-label="Limpar termo de busca"
              @click="clearQuery"
            >
              <Icon name="x" :size="14" />
            </button>
          </div>

          <!-- Botão de Filtros -->
          <button
            type="button"
            class="px-2.5 py-2 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition-colors min-h-[44px] cursor-pointer"
            :class="[
              showFilters || hasActiveFilters
                ? 'bg-accent/15 border-accent text-accent'
                : 'bg-muted/50 border-border/60 text-muted-foreground hover:text-foreground'
            ]"
            :aria-expanded="showFilters"
            aria-label="Alternar filtros de busca"
            @click="showFilters = !showFilters"
          >
            <Icon name="sliders" :size="14" />
            <span class="hidden sm:inline">Filtros</span>
            <span
              v-if="hasActiveFilters"
              class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"
            />
          </button>

          <!-- Botão Fechar Modal -->
          <button
            type="button"
            class="p-2 rounded-lg border border-border/60 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center cursor-pointer"
            aria-label="Fechar busca"
            @click="closeSearch"
          >
            <Icon name="x" :size="16" />
          </button>
        </div>

        <!-- Painel de Filtros Expansível (US2) -->
        <div
          v-if="showFilters"
          class="p-3 bg-muted/30 border-b border-border text-xs space-y-2.5 transition-all"
        >
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <!-- Filtro de Livro -->
            <div>
              <label class="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">
                Livro Específico
              </label>
              <select
                :value="bookId ?? ''"
                class="w-full p-2 bg-background border border-border rounded text-xs min-h-[44px] focus:outline-none focus:ring-1 focus:ring-accent"
                @change="setBookFilter(($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
              >
                <option value="">Todas as obras</option>
                <option v-for="b in booksList" :key="b.id" :value="b.id">
                  {{ b.title }}
                </option>
              </select>
            </div>

            <!-- Filtro de Categoria Taxonômica -->
            <div>
              <label class="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">
                Categoria Taxonômica
              </label>
              <select
                :value="categoryId ?? ''"
                class="w-full p-2 bg-background border border-border rounded text-xs min-h-[44px] focus:outline-none focus:ring-1 focus:ring-accent"
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
          <div class="flex items-center justify-between pt-1 flex-wrap gap-2">
            <div class="flex items-center gap-1.5">
              <span class="text-muted-foreground text-[11px]">Modo de termos:</span>
              <button
                type="button"
                class="px-2 py-1 rounded text-xs font-medium border transition-colors min-h-[36px]"
                :class="mode === 'and' ? 'bg-accent/20 border-accent text-accent' : 'bg-background border-border text-muted-foreground'"
                @click="setMode('and')"
              >
                AND (Estrito)
              </button>
              <button
                type="button"
                class="px-2 py-1 rounded text-xs font-medium border transition-colors min-h-[36px]"
                :class="mode === 'or' ? 'bg-accent/20 border-accent text-accent' : 'bg-background border-border text-muted-foreground'"
                @click="setMode('or')"
              >
                OR (Abrangente)
              </button>
            </div>

            <button
              v-if="hasActiveFilters"
              type="button"
              class="text-xs text-muted-foreground hover:text-foreground underline p-1 min-h-[36px] flex items-center cursor-pointer"
              @click="clearFilters"
            >
              Limpar filtros
            </button>
          </div>
        </div>

        <!-- Área de Conteúdo / Resultados -->
        <div class="flex-1 overflow-y-auto p-3.5 space-y-2.5 min-h-[220px]">
          <!-- Alerta de Erro -->
          <div
            v-if="error"
            class="p-3 rounded-lg bg-destructive/10 text-destructive text-xs border border-destructive/20"
          >
            {{ error }}
          </div>

          <!-- Estado de Carregamento -->
          <div
            v-if="isLoading"
            class="py-10 text-center text-sm text-muted-foreground flex flex-col items-center gap-2"
          >
            <div class="w-5 h-5 border-2 border-accent border-t-transparent rounded-full animate-spin" />
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
            class="py-8 text-center text-xs text-muted-foreground"
          >
            Digite no mínimo 2 caracteres para pesquisar.
          </div>

          <!-- Sugestão assistida de modo OR (quando AND não encontra resultados) -->
          <div
            v-else-if="results.length === 0 && suggestOr"
            class="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-700 dark:text-amber-300 text-xs space-y-2"
          >
            <p class="font-medium">
              Nenhum estudo contém todos os termos juntos no modo estrito.
            </p>
            <button
              type="button"
              class="px-3 py-1.5 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 rounded-md font-semibold text-xs transition-colors min-h-[38px] flex items-center cursor-pointer"
              @click="setMode('or')"
            >
              Buscar estudos com qualquer um dos termos (Modo OR)
            </button>
          </div>

          <!-- Nenhum resultado encontrado -->
          <div
            v-else-if="results.length === 0"
            class="py-12 text-center text-sm text-muted-foreground space-y-1.5"
          >
            <Icon name="search" :size="28" class="mx-auto text-muted-foreground/40 mb-2" />
            <p class="font-medium text-foreground">Nenhum resultado encontrado</p>
            <p class="text-xs text-muted-foreground/80 max-w-sm mx-auto">
              Verifique a ortografia do termo ou experimente palavras-chave mais gerais.
            </p>
          </div>

          <!-- Lista de Resultados Encontrados -->
          <div v-else id="search-results-list" class="space-y-2">
            <div
              class="flex items-center justify-between text-xs text-muted-foreground px-1 pb-1"
              aria-live="polite"
            >
              <span>{{ total }} {{ total === 1 ? 'estudo encontrado' : 'estudos encontrados' }}</span>
              <span class="text-[11px] hidden sm:inline">Use ↑ ↓ para navegar e Enter para abrir</span>
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
        <div class="px-3.5 py-2 border-t border-border bg-muted/20 text-[11px] text-muted-foreground flex items-center justify-between hidden sm:flex">
          <div class="flex items-center gap-3">
            <span><kbd class="px-1.5 py-0.5 border rounded bg-card text-foreground font-mono">↑</kbd> <kbd class="px-1.5 py-0.5 border rounded bg-card text-foreground font-mono">↓</kbd> Navegar</span>
            <span><kbd class="px-1.5 py-0.5 border rounded bg-card text-foreground font-mono">Enter</kbd> Selecionar</span>
            <span><kbd class="px-1.5 py-0.5 border rounded bg-card text-foreground font-mono">Esc</kbd> Fechar</span>
          </div>
          <span class="text-muted-foreground/70">Busca local integrada</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>
