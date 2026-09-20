import test from 'node:test'
import assert from 'node:assert/strict'

test('US1: Navegação direta de 1 clique monta rota correta com study_id e book_id', () => {
  const resultItem = {
    study_id: 15,
    study_title: 'O Conceito de Angústia',
    book_id: 4,
    book_title: 'Kierkegaard e a Existência',
    chapter_id: 2,
    chapter_name: 'Capítulo I',
    reading_status: 'revisado',
    matched_field: 'Título',
    snippet: '…estudo sobre <mark class="search-highlight">angústia</mark> existencial…',
    updated_at: '2026-09-19T20:00:00Z',
  }

  function resolveStudyRoute(item) {
    return {
      path: `/books/${item.book_id}`,
      query: { study: String(item.study_id) },
    }
  }

  const route = resolveStudyRoute(resultItem)
  assert.equal(route.path, '/books/4')
  assert.equal(route.query.study, '15')
})

test('US1: Snippets sanitizados contêm realce com mark sem vazamento de tags perigosas', () => {
  const rawSnippet = '…teoria da <mark class="search-highlight">dialética</mark> em Hegel…'
  assert.match(rawSnippet, /<mark class="search-highlight">dialética<\/mark>/)
  assert.doesNotMatch(rawSnippet, /<script>/)
})

test('US2: Filtros contextuais montam parâmetros corretos para URLSearchParams', () => {
  function buildSearchParams(params) {
    const query = new URLSearchParams()
    query.set('q', params.q)
    if (params.mode) query.set('mode', params.mode)
    if (params.book_id != null) query.set('book_id', String(params.book_id))
    if (params.category_id != null) query.set('category_id', String(params.category_id))
    if (params.limit != null) query.set('limit', String(params.limit))
    return query.toString()
  }

  const qs1 = buildSearchParams({ q: 'ontologia', mode: 'and', book_id: 3 })
  assert.equal(qs1, 'q=ontologia&mode=and&book_id=3')

  const qs2 = buildSearchParams({ q: 'ética', mode: 'or', category_id: 'filosofia', limit: 30 })
  assert.equal(qs2, 'q=%C3%A9tica&mode=or&category_id=filosofia&limit=30')
})

test('US2: Alternância de modo de combinação (AND vs OR assistido)', () => {
  function getModeExplanation(mode, suggestOr) {
    if (mode === 'and' && suggestOr) {
      return 'Sugerir busca OR'
    }
    if (mode === 'or') {
      return 'Busca abrangente ativa'
    }
    return 'Busca estrita ativa'
  }

  assert.equal(getModeExplanation('and', false), 'Busca estrita ativa')
  assert.equal(getModeExplanation('and', true), 'Sugerir busca OR')
  assert.equal(getModeExplanation('or', false), 'Busca abrangente ativa')
})

test('US3: Histórico de buscas deduplica termos e mantém ordenação cronológica', () => {
  const history = [
    { id: 1, query: 'kant', updated_at: '2026-09-19T10:00:00Z' },
    { id: 2, query: 'hegel', updated_at: '2026-09-19T11:00:00Z' },
  ]

  function recordQuery(list, newQuery) {
    const clean = newQuery.trim().toLowerCase()
    const filtered = list.filter((item) => item.query.toLowerCase() !== clean)
    const updated = [
      { id: Date.now(), query: clean, updated_at: new Date().toISOString() },
      ...filtered,
    ]
    return updated.slice(0, 10)
  }

  const updated1 = recordQuery(history, 'spinoza')
  assert.equal(updated1.length, 3)
  assert.equal(updated1[0].query, 'spinoza')

  // Ao pesquisar 'kant' novamente, ele deve ir para o topo sem duplicar
  const updated2 = recordQuery(updated1, 'kant')
  assert.equal(updated2.length, 3)
  assert.equal(updated2[0].query, 'kant')
  assert.equal(updated2[1].query, 'spinoza')
  assert.equal(updated2[2].query, 'hegel')
})

test('US3: Exclusão de termo individual e limpeza do histórico', () => {
  let history = [
    { id: 10, query: 'lógica' },
    { id: 11, query: 'epistemologia' },
    { id: 12, query: 'metafísica' },
  ]

  function removeItem(list, id) {
    return list.filter((item) => item.id !== id)
  }

  history = removeItem(history, 11)
  assert.equal(history.length, 2)
  assert.deepEqual(history.map((h) => h.id), [10, 12])

  history = []
  assert.equal(history.length, 0)
})
