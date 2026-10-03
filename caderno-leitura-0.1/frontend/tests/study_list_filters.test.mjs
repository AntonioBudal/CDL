import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

import {
  useStudyListFilters,
  normalizeSearchTerm,
  STATUS_ORDINAL,
} from '../src/composables/useStudyListFilters.ts'

// Mock simples para ambiente de teste em Node
class MockStorage {
  constructor() {
    this.store = new Map()
  }
  getItem(key) {
    return this.store.get(key) || null
  }
  setItem(key, value) {
    this.store.set(key, String(value))
  }
  removeItem(key) {
    this.store.delete(key)
  }
  clear() {
    this.store.clear()
  }
}

test('normalizeSearchTerm remove acentos e normaliza para minúsculas', () => {
  assert.equal(normalizeSearchTerm('Dialética'), 'dialetica')
  assert.equal(normalizeSearchTerm('  FENÔMENO  '), 'fenomeno')
  assert.equal(normalizeSearchTerm('Crítica da Razão'), 'critica da razao')
  assert.equal(normalizeSearchTerm(''), '')
})

test('STATUS_ORDINAL define pesos numéricos crescentes para os 4 status canônicos', () => {
  assert.equal(STATUS_ORDINAL.rascunho, 1)
  assert.equal(STATUS_ORDINAL.em_andamento, 2)
  assert.equal(STATUS_ORDINAL.revisado, 3)
  assert.equal(STATUS_ORDINAL.concluido, 4)
  assert.ok(STATUS_ORDINAL.rascunho < STATUS_ORDINAL.em_andamento)
  assert.ok(STATUS_ORDINAL.em_andamento < STATUS_ORDINAL.revisado)
  assert.ok(STATUS_ORDINAL.revisado < STATUS_ORDINAL.concluido)
})

test('US1: toggleSort implementa ciclo tripartite (asc -> desc -> default) e transição entre colunas', () => {
  const studies = ref([
    { id: 1, title: 'B', reading_status: 'rascunho', position: 1 },
    { id: 2, title: 'A', reading_status: 'concluido', position: 2 },
  ])

  const { sortColumn, sortDirection, toggleSort } = useStudyListFilters({
    studies,
    bookId: 101,
  })

  // Estado inicial padrão
  assert.equal(sortColumn.value, 'natural')
  assert.equal(sortDirection.value, 'default')

  // 1º clique em 'title' -> asc
  toggleSort('title')
  assert.equal(sortColumn.value, 'title')
  assert.equal(sortDirection.value, 'asc')

  // 2º clique em 'title' -> desc
  toggleSort('title')
  assert.equal(sortColumn.value, 'title')
  assert.equal(sortDirection.value, 'desc')

  // 3º clique em 'title' -> default (reseta para natural)
  toggleSort('title')
  assert.equal(sortColumn.value, 'natural')
  assert.equal(sortDirection.value, 'default')

  // Alternar diretamente para outra coluna define imediatamente asc
  toggleSort('status')
  assert.equal(sortColumn.value, 'status')
  assert.equal(sortDirection.value, 'asc')

  // Clique em coluna diferente ('date') migra direto para asc da nova coluna
  toggleSort('date')
  assert.equal(sortColumn.value, 'date')
  assert.equal(sortDirection.value, 'asc')
})

test('US1: ordenação alfabética por título (asc/desc) e ordenação natural por position/id', () => {
  const sampleStudies = [
    { id: 1, title: 'Zoologia', position: 3 },
    { id: 2, title: 'Álgebra', position: 1 },
    { id: 3, title: 'Botânica', position: 2 },
  ]
  const studies = ref([...sampleStudies])

  const { filteredAndSortedStudies, toggleSort } = useStudyListFilters({
    studies,
    bookId: 102,
  })

  // Default: ordem natural por position (1 -> 2 -> 3)
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.id),
    [2, 3, 1]
  )

  // Ascendente por título: Álgebra -> Botânica -> Zoologia
  toggleSort('title')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.title),
    ['Álgebra', 'Botânica', 'Zoologia']
  )

  // Descendente por título: Zoologia -> Botânica -> Álgebra
  toggleSort('title')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.title),
    ['Zoologia', 'Botânica', 'Álgebra']
  )
})

test('US1: ordenação por status respeita peso ordinal', () => {
  const studies = ref([
    { id: 1, title: 'Estudo 1', reading_status: 'concluido', position: 1 },
    { id: 2, title: 'Estudo 2', reading_status: 'rascunho', position: 2 },
    { id: 3, title: 'Estudo 3', reading_status: 'em_andamento', position: 3 },
    { id: 4, title: 'Estudo 4', reading_status: 'revisado', position: 4 },
  ])

  const { filteredAndSortedStudies, toggleSort } = useStudyListFilters({
    studies,
    bookId: 103,
  })

  // Ordenar por status asc: rascunho -> em_andamento -> revisado -> concluido
  toggleSort('status')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.reading_status),
    ['rascunho', 'em_andamento', 'revisado', 'concluido']
  )

  // Ordenar por status desc: concluido -> revisado -> em_andamento -> rascunho
  toggleSort('status')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.reading_status),
    ['concluido', 'revisado', 'em_andamento', 'rascunho']
  )
})

test('US1: ordenação por data utiliza updated_at com fallback para created_at', () => {
  const studies = ref([
    { id: 1, title: 'Estudo Antigo', created_at: '2026-01-01T10:00:00Z', updated_at: '2026-01-01T10:00:00Z' },
    { id: 2, title: 'Estudo Recente', created_at: '2026-02-01T10:00:00Z', updated_at: '2026-05-01T10:00:00Z' },
    { id: 3, title: 'Estudo Intermediário', created_at: '2026-03-01T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' },
  ])

  const { filteredAndSortedStudies, toggleSort } = useStudyListFilters({
    studies,
    bookId: 104,
  })

  // Ascendente (mais antigo para mais recente)
  toggleSort('date')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.id),
    [1, 3, 2]
  )

  // Descendente (mais recente para mais antigo)
  toggleSort('date')
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.id),
    [2, 3, 1]
  )
})

test('US1: persistência no localStorage recupera preferências por bookId', () => {
  const originalStorage = globalThis.localStorage
  const mock = new MockStorage()
  mock.setItem(
    'caderno_list_sort_999',
    JSON.stringify({ sortColumn: 'title', sortDirection: 'desc' })
  )
  globalThis.localStorage = mock

  try {
    const studies = ref([
      { id: 1, title: 'Alfa', position: 1 },
      { id: 2, title: 'Beta', position: 2 },
    ])

    const { sortColumn, sortDirection, filteredAndSortedStudies } = useStudyListFilters({
      studies,
      bookId: 999,
    })

    // Deve inicializar com o que estava salvo
    assert.equal(sortColumn.value, 'title')
    assert.equal(sortDirection.value, 'desc')
    assert.deepEqual(
      filteredAndSortedStudies.value.map((s) => s.title),
      ['Beta', 'Alfa']
    )
  } finally {
    globalThis.localStorage = originalStorage
  }
})

test('US2: busca textual em tempo real é insensível a maiúsculas e diacríticos', () => {
  const studies = ref([
    { id: 1, title: 'Crítica da Razão Pura', location: 'Prefácio B', summary_preview: 'Discussão a priori' },
    { id: 2, title: 'Fenomenologia do Espírito', location: 'Introdução', summary_preview: 'Consciência e saber' },
    { id: 3, title: 'Investigações Lógicas', location: 'Seção II', summary_preview: 'Semiótica e intenção' },
  ])

  const { searchQuery, filteredAndSortedStudies, filteredCount, isFilterActive } =
    useStudyListFilters({
      studies,
      bookId: 105,
    })

  assert.equal(filteredCount.value, 3)
  assert.equal(isFilterActive.value, false)

  // Busca sem acento "critica" deve achar "Crítica da Razão Pura"
  searchQuery.value = 'critica'
  assert.equal(filteredCount.value, 1)
  assert.equal(filteredAndSortedStudies.value[0].id, 1)
  assert.equal(isFilterActive.value, true)

  // Busca por localização "prefacio" sem acento
  searchQuery.value = 'prefacio'
  assert.equal(filteredCount.value, 1)
  assert.equal(filteredAndSortedStudies.value[0].id, 1)

  // Busca por conteúdo no resumo preview "consciencia"
  searchQuery.value = 'consciencia'
  assert.equal(filteredCount.value, 1)
  assert.equal(filteredAndSortedStudies.value[0].id, 2)

  // Termo inexistente
  searchQuery.value = 'metafísica quantitativa'
  assert.equal(filteredCount.value, 0)
})

test('US2: filtro por status e resetFilters limpa busca e status simultaneamente', () => {
  const studies = ref([
    { id: 1, title: 'Estudo 1', reading_status: 'rascunho', position: 1 },
    { id: 2, title: 'Estudo 2', reading_status: 'concluido', position: 2 },
    { id: 3, title: 'Estudo 3', reading_status: 'concluido', position: 3 },
  ])

  const {
    searchQuery,
    statusFilter,
    sortColumn,
    sortDirection,
    filteredAndSortedStudies,
    filteredCount,
    resetFilters,
    toggleSort,
  } = useStudyListFilters({
    studies,
    bookId: 106,
  })

  statusFilter.value = 'concluido'
  assert.equal(filteredCount.value, 2)
  assert.deepEqual(
    filteredAndSortedStudies.value.map((s) => s.id),
    [2, 3]
  )

  // Aplicar busca adicional
  searchQuery.value = 'Estudo 3'
  assert.equal(filteredCount.value, 1)
  assert.equal(filteredAndSortedStudies.value[0].id, 3)

  // Aplicar ordenação
  toggleSort('title')
  assert.equal(sortColumn.value, 'title')

  // Resetar tudo
  resetFilters()
  assert.equal(searchQuery.value, '')
  assert.equal(statusFilter.value, 'all')
  assert.equal(sortColumn.value, 'natural')
  assert.equal(sortDirection.value, 'default')
  assert.equal(filteredCount.value, 3)
})
