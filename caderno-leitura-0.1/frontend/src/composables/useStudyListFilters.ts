import { ref, computed, watch, isRef, type Ref, type ComputedRef } from 'vue'
import type {
  StudySummary,
  ReadingStatus,
  SortColumn,
  SortDirection,
} from '../types.ts'

export interface UseStudyListFiltersOptions {
  studies: Ref<StudySummary[]> | ComputedRef<StudySummary[]> | StudySummary[]
  bookId: number | Ref<number>
  chapterId?: number | null | Ref<number | null | undefined>
}

export interface UseStudyListFiltersReturn {
  searchQuery: Ref<string>
  statusFilter: Ref<ReadingStatus | 'all'>
  sortColumn: Ref<SortColumn>
  sortDirection: Ref<SortDirection>
  filteredAndSortedStudies: ComputedRef<StudySummary[]>
  totalCount: ComputedRef<number>
  filteredCount: ComputedRef<number>
  isFilterActive: ComputedRef<boolean>
  toggleSort: (column: SortColumn) => void
  resetFilters: () => void
}

export const STATUS_ORDINAL: Record<string, number> = {
  rascunho: 1,
  em_andamento: 2,
  em_estudo: 2,
  revisado: 3,
  concluido: 4,
}

export function normalizeSearchTerm(text: string): string {
  if (!text) return ''
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

function getStorage(): Storage | null {
  if (typeof window !== 'undefined' && window.localStorage) {
    return window.localStorage
  }
  if (typeof localStorage !== 'undefined') {
    return localStorage
  }
  return null
}

export function useStudyListFilters(
  options: UseStudyListFiltersOptions
): UseStudyListFiltersReturn {
  const actualBookId = computed(() =>
    isRef(options.bookId) ? options.bookId.value : options.bookId
  )
  const storageKey = computed(() => `caderno_list_sort_${actualBookId.value}`)

  function loadPersistedSort(): { column: SortColumn; direction: SortDirection } {
    try {
      const storage = getStorage()
      if (!storage) return { column: 'natural', direction: 'default' }
      const raw = storage.getItem(storageKey.value)
      if (!raw) return { column: 'natural', direction: 'default' }
      const parsed = JSON.parse(raw)
      const validCols: SortColumn[] = ['natural', 'title', 'status', 'date']
      const validDirs: SortDirection[] = ['asc', 'desc', 'default']
      if (
        parsed &&
        validCols.includes(parsed.sortColumn) &&
        validDirs.includes(parsed.sortDirection)
      ) {
        return { column: parsed.sortColumn, direction: parsed.sortDirection }
      }
    } catch {
      // Ignora erro de JSON ou acesso ao storage
    }
    return { column: 'natural', direction: 'default' }
  }

  const initialSort = loadPersistedSort()
  const searchQuery = ref<string>('')
  const statusFilter = ref<ReadingStatus | 'all'>('all')
  const sortColumn = ref<SortColumn>(initialSort.column)
  const sortDirection = ref<SortDirection>(initialSort.direction)

  // Ao mudar de livro, recarrega a ordenação correspondente
  watch(actualBookId, () => {
    const loaded = loadPersistedSort()
    sortColumn.value = loaded.column
    sortDirection.value = loaded.direction
  })

  function persistSort() {
    try {
      const storage = getStorage()
      if (!storage) return
      if (sortColumn.value === 'natural' && sortDirection.value === 'default') {
        storage.removeItem(storageKey.value)
      } else {
        storage.setItem(
          storageKey.value,
          JSON.stringify({
            sortColumn: sortColumn.value,
            sortDirection: sortDirection.value,
          })
        )
      }
    } catch {
      // Quota ou restrição de armazenamento
    }
  }

  function toggleSort(column: SortColumn) {
    if (sortColumn.value !== column) {
      sortColumn.value = column
      sortDirection.value = 'asc'
    } else {
      if (sortDirection.value === 'asc') {
        sortDirection.value = 'desc'
      } else if (sortDirection.value === 'desc') {
        sortDirection.value = 'default'
        sortColumn.value = 'natural'
      } else {
        sortDirection.value = 'asc'
      }
    }
    persistSort()
  }

  function resetFilters() {
    searchQuery.value = ''
    statusFilter.value = 'all'
    sortColumn.value = 'natural'
    sortDirection.value = 'default'
    persistSort()
  }

  const baseStudies = computed<StudySummary[]>(() => {
    return isRef(options.studies) ? options.studies.value : options.studies
  })

  const totalCount = computed(() => baseStudies.value.length)

  const isFilterActive = computed(() => {
    return Boolean(
      searchQuery.value.trim() !== '' ||
        statusFilter.value !== 'all' ||
        sortDirection.value !== 'default' ||
        sortColumn.value !== 'natural'
    )
  })

  const filteredAndSortedStudies = computed<StudySummary[]>(() => {
    let result = [...baseStudies.value]

    // 1. Filtrar por status
    if (statusFilter.value !== 'all') {
      const targetStatus = statusFilter.value
      result = result.filter(
        (s) => (s.reading_status || 'rascunho') === targetStatus
      )
    }

    // 2. Filtrar por busca textual insensível a maiúsculas e acentos
    const query = normalizeSearchTerm(searchQuery.value)
    if (query) {
      result = result.filter((s) => {
        const titleNorm = normalizeSearchTerm(s.title || '')
        const locNorm = normalizeSearchTerm(s.location || '')
        const prevNorm = normalizeSearchTerm(s.summary_preview || '')
        return (
          titleNorm.includes(query) ||
          locNorm.includes(query) ||
          prevNorm.includes(query)
        )
      })
    }

    // 3. Ordenação
    if (sortColumn.value === 'natural' || sortDirection.value === 'default') {
      result.sort((a, b) => {
        const posA = a.position ?? 0
        const posB = b.position ?? 0
        if (posA !== posB) return posA - posB
        return a.id - b.id
      })
    } else if (sortColumn.value === 'title') {
      result.sort((a, b) => {
        const titleA = a.title || ''
        const titleB = b.title || ''
        const cmp = titleA.localeCompare(titleB, 'pt-BR', { sensitivity: 'base' })
        return sortDirection.value === 'asc' ? cmp : -cmp
      })
    } else if (sortColumn.value === 'status') {
      result.sort((a, b) => {
        const wA = STATUS_ORDINAL[a.reading_status || 'rascunho'] ?? 1
        const wB = STATUS_ORDINAL[b.reading_status || 'rascunho'] ?? 1
        const cmp = wA - wB
        if (cmp !== 0) {
          return sortDirection.value === 'asc' ? cmp : -cmp
        }
        return (a.position ?? 0) - (b.position ?? 0) || a.id - b.id
      })
    } else if (sortColumn.value === 'date') {
      result.sort((a, b) => {
        const dateA = new Date(a.updated_at || a.created_at || 0).getTime()
        const dateB = new Date(b.updated_at || b.created_at || 0).getTime()
        const cmp = dateA - dateB
        if (cmp !== 0) {
          return sortDirection.value === 'asc' ? cmp : -cmp
        }
        return (a.position ?? 0) - (b.position ?? 0) || a.id - b.id
      })
    }

    return result
  })

  const filteredCount = computed(() => filteredAndSortedStudies.value.length)

  return {
    searchQuery,
    statusFilter,
    sortColumn,
    sortDirection,
    filteredAndSortedStudies,
    totalCount,
    filteredCount,
    isFilterActive,
    toggleSort,
    resetFilters,
  }
}
