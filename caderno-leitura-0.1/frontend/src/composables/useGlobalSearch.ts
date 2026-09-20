import { ref } from 'vue'
import type { Router } from 'vue-router'
import {
  clearSearchHistory,
  deleteSearchHistoryItem,
  getSearchHistory,
  searchStudies,
} from '../services/api.ts'
import type { SearchHistoryItem, SearchMatchItem } from '../types.ts'

// Estado compartilhado (singleton) para permitir controle a partir de qualquer componente
const isOpen = ref(false)
const query = ref('')
const mode = ref<'and' | 'or'>('and')
const bookId = ref<number | null>(null)
const categoryId = ref<string | null>(null)
const results = ref<SearchMatchItem[]>([])
const total = ref(0)
const suggestOr = ref(false)
const isLoading = ref(false)
const error = ref<string | null>(null)
const history = ref<SearchHistoryItem[]>([])
const isLoadingHistory = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null
let currentAbortController: AbortController | null = null

export function useGlobalSearch() {
  function openSearch() {
    isOpen.value = true
    if (!query.value.trim()) {
      loadHistory()
    }
  }

  function closeSearch() {
    isOpen.value = false
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
    if (currentAbortController) {
      currentAbortController.abort()
      currentAbortController = null
    }
  }

  function toggleSearch() {
    if (isOpen.value) {
      closeSearch()
    } else {
      openSearch()
    }
  }

  async function loadHistory() {
    try {
      isLoadingHistory.value = true
      const res = await getSearchHistory()
      history.value = res.items || []
    } catch {
      history.value = []
    } finally {
      isLoadingHistory.value = false
    }
  }

  async function removeHistoryItem(id: number) {
    try {
      await deleteSearchHistoryItem(id)
      history.value = history.value.filter((item) => item.id !== id)
    } catch {
      // Ignora erro visual
    }
  }

  async function clearHistory() {
    try {
      await clearSearchHistory()
      history.value = []
    } catch {
      // Ignora erro visual
    }
  }

  async function executeSearch(customMode?: 'and' | 'or') {
    const activeQuery = query.value.trim()
    if (activeQuery.length < 2) {
      results.value = []
      total.value = 0
      suggestOr.value = false
      error.value = null
      isLoading.value = false
      loadHistory()
      return
    }

    if (currentAbortController) {
      currentAbortController.abort()
    }
    currentAbortController = new AbortController()

    if (customMode) {
      mode.value = customMode
    }

    isLoading.value = true
    error.value = null

    try {
      const res = await searchStudies(
        {
          q: activeQuery,
          mode: mode.value,
          book_id: bookId.value ?? undefined,
          category_id: categoryId.value ?? undefined,
          limit: 30,
        },
        currentAbortController.signal,
      )
      results.value = res.results
      total.value = res.total
      suggestOr.value = res.suggest_or
    } catch (err: any) {
      if (err?.name === 'AbortError') return
      error.value = err?.message || 'Falha ao realizar busca.'
      results.value = []
      total.value = 0
      suggestOr.value = false
    } finally {
      isLoading.value = false
    }
  }

  function onQueryChange(newQuery: string) {
    query.value = newQuery
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    if (newQuery.trim().length < 2) {
      results.value = []
      total.value = 0
      suggestOr.value = false
      error.value = null
      isLoading.value = false
      loadHistory()
      return
    }
    debounceTimer = setTimeout(() => {
      executeSearch()
    }, 250)
  }

  function setMode(newMode: 'and' | 'or') {
    if (mode.value !== newMode) {
      mode.value = newMode
      executeSearch()
    }
  }

  function setBookFilter(id: number | null) {
    bookId.value = id
    executeSearch()
  }

  function setCategoryFilter(id: string | null) {
    categoryId.value = id
    executeSearch()
  }

  function clearFilters() {
    bookId.value = null
    categoryId.value = null
    mode.value = 'and'
    executeSearch()
  }

  function selectHistoryTerm(term: string) {
    query.value = term
    executeSearch()
  }

  function selectResult(result: SearchMatchItem, router: Router) {
    closeSearch()
    router.push({
      path: `/books/${result.book_id}`,
      query: { study: String(result.study_id) },
    })
  }

  return {
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
    openSearch,
    closeSearch,
    toggleSearch,
    onQueryChange,
    executeSearch,
    setMode,
    setBookFilter,
    setCategoryFilter,
    clearFilters,
    loadHistory,
    removeHistoryItem,
    clearHistory,
    selectHistoryTerm,
    selectResult,
  }
}
