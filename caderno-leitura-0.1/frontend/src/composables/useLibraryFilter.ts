import { computed, ref, watch, type Ref } from 'vue'
import type { Book, BookSortOption, LibraryViewMode } from '../types.ts'
import { useCategories } from './useCategories.ts'

const STORAGE_KEY_VIEW_MODE = 'caderno_library_view_mode'
const STORAGE_KEY_SORT = 'caderno_library_sort'

const collator = new Intl.Collator('pt-BR', { sensitivity: 'base', numeric: true })

/**
 * Remove acentos (diacríticos), pontuação excessiva e converte para caixa baixa.
 */
export function normalizeText(value: string | null | undefined): string {
  if (!value) return ''
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
}

/**
 * Filtra lista de livros por categoria (recursiva/inclusiva) e múltiplos tokens de texto.
 */
export function filterBooks(
  books: readonly Book[],
  query: string,
  selectedCategory: string | null = null,
  descendantIds?: Set<string> | null,
): Book[] {
  let list = books
  if (selectedCategory) {
    if (selectedCategory === '__uncategorized__') {
      list = list.filter((b) => !b.categories || b.categories.length === 0)
    } else if (descendantIds && descendantIds.size > 0) {
      list = list.filter((b) => b.categories && b.categories.some((c) => descendantIds.has(c.id)))
    } else {
      list = list.filter((b) => b.categories && b.categories.some((c) => c.id === selectedCategory))
    }
  }

  const normalizedQuery = normalizeText(query)
  if (!normalizedQuery) return [...list]

  const tokens = normalizedQuery.split(/\s+/).filter(Boolean)
  if (tokens.length === 0) return [...list]

  return list.filter((book) => {
    const titleNorm = normalizeText(book.title)
    const authorNorm = normalizeText(book.author)
    const subtitleNorm = normalizeText(book.subtitle)
    const combined = `${titleNorm} ${authorNorm} ${subtitleNorm}`

    return tokens.every((token) => combined.includes(token))
  })
}

/**
 * Ordena lista de livros conforme a opção selecionada.
 */
export function sortBooks(books: readonly Book[], sortBy: BookSortOption): Book[] {
  const list = [...books]

  return list.sort((a, b) => {
    switch (sortBy) {
      case 'title-asc': {
        const cmp = collator.compare(a.title, b.title)
        return cmp !== 0 ? cmp : (a.id - b.id)
      }

      case 'title-desc': {
        const cmp = collator.compare(b.title, a.title)
        return cmp !== 0 ? cmp : (a.id - b.id)
      }

      case 'author-asc': {
        if (!a.author && !b.author) return a.id - b.id
        if (!a.author) return 1
        if (!b.author) return -1
        const cmp = collator.compare(a.author, b.author)
        return cmp !== 0 ? cmp : collator.compare(a.title, b.title)
      }

      case 'recent-created': {
        const timeA = a.created_at ? new Date(a.created_at).getTime() : 0
        const timeB = b.created_at ? new Date(b.created_at).getTime() : 0
        const diff = timeB - timeA
        return diff !== 0 ? diff : (b.id - a.id)
      }

      case 'recent-updated': {
        const timeA = a.updated_at ? new Date(a.updated_at).getTime() : 0
        const timeB = b.updated_at ? new Date(b.updated_at).getTime() : 0
        const diff = timeB - timeA
        return diff !== 0 ? diff : (b.id - a.id)
      }

      case 'oldest-created': {
        const timeA = a.created_at ? new Date(a.created_at).getTime() : 0
        const timeB = b.created_at ? new Date(b.created_at).getTime() : 0
        const diff = timeA - timeB
        return diff !== 0 ? diff : (a.id - b.id)
      }

      case 'year-desc': {
        if (a.year == null && b.year == null) return collator.compare(a.title, b.title)
        if (a.year == null) return 1
        if (b.year == null) return -1
        const diff = b.year - a.year
        return diff !== 0 ? diff : collator.compare(a.title, b.title)
      }

      default:
        return a.id - b.id
    }
  })
}

/**
 * Composable que gerencia estado reativo de busca, ordenação e modo de exibição com persistência.
 */
export function useLibraryFilter(booksSource: Ref<Book[]>) {
  // Inicialização com recuperação do localStorage
  const savedViewMode = (typeof localStorage !== 'undefined'
    ? localStorage.getItem(STORAGE_KEY_VIEW_MODE)
    : null) as LibraryViewMode | null

  const savedSort = (typeof localStorage !== 'undefined'
    ? localStorage.getItem(STORAGE_KEY_SORT)
    : null) as BookSortOption | null

  const viewMode = ref<LibraryViewMode>(savedViewMode === 'list' ? 'list' : 'grid')
  const sortBy = ref<BookSortOption>(
    savedSort && [
      'title-asc', 'title-desc', 'author-asc',
      'recent-created', 'recent-updated', 'oldest-created', 'year-desc'
    ].includes(savedSort)
      ? savedSort
      : 'recent-updated'
  )

  const searchQuery = ref('')
  const selectedCategory = ref<string | null>(null)
  const { getDescendantIds } = useCategories()

  const activeDescendants = computed(() => {
    if (!selectedCategory.value || selectedCategory.value === '__uncategorized__') {
      return null
    }
    return getDescendantIds(selectedCategory.value)
  })

  // Sincronização e persistência
  watch(viewMode, (newMode) => {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY_VIEW_MODE, newMode)
      }
      // Sincroniza também com cadernoAppearance se disponível
      if (typeof window !== 'undefined' && window.cadernoAppearance?.set) {
        window.cadernoAppearance.set({ library: newMode })
      }
    } catch {
      // Ignora falhas de gravação no localStorage (ex.: modo anônimo restrito)
    }
  })

  watch(sortBy, (newSort) => {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY_SORT, newSort)
      }
    } catch {
      // Ignora falha de gravação
    }
  })

  function setViewMode(mode: LibraryViewMode) {
    viewMode.value = mode
  }

  function setSortBy(sort: BookSortOption) {
    sortBy.value = sort
  }

  function setSelectedCategory(catId: string | null) {
    selectedCategory.value = catId
  }

  function clearSearch() {
    searchQuery.value = ''
  }

  function clearCategory() {
    selectedCategory.value = null
  }

  function clearAllFilters() {
    searchQuery.value = ''
    selectedCategory.value = null
  }

  // Filtragem e ordenação computadas
  const filteredBooks = computed(() => {
    const filtered = filterBooks(
      booksSource.value,
      searchQuery.value,
      selectedCategory.value,
      activeDescendants.value,
    )
    return sortBooks(filtered, sortBy.value)
  })

  const totalCount = computed(() => booksSource.value.length)
  const filteredCount = computed(() => filteredBooks.value.length)
  const hasActiveSearch = computed(() => !!searchQuery.value.trim())
  const hasActiveCategory = computed(() => !!selectedCategory.value)
  const hasActiveFilters = computed(() => hasActiveSearch.value || hasActiveCategory.value)

  return {
    searchQuery,
    selectedCategory,
    viewMode,
    sortBy,
    filteredBooks,
    totalCount,
    filteredCount,
    hasActiveSearch,
    hasActiveCategory,
    hasActiveFilters,
    setViewMode,
    setSortBy,
    setSelectedCategory,
    clearSearch,
    clearCategory,
    clearAllFilters,
  }
}
