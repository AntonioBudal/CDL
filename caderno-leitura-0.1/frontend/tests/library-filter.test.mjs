import test from 'node:test'
import assert from 'node:assert/strict'
import { normalizeText, filterBooks, sortBooks } from '../src/composables/useLibraryFilter.ts'

test('normalizeText remove diacríticos, pontuações excedentes e converte para minúsculas', () => {
  assert.equal(normalizeText('Memórias Póstumas de Brás Cubas'), 'memorias postumas de bras cubas')
  assert.equal(normalizeText('Árvore da Vida — Volume 1!'), 'arvore da vida — volume 1!')
  assert.equal(normalizeText('  Espaços   Extras  '), 'espacos extras')
  assert.equal(normalizeText(''), '')
})

test('filterBooks localiza livros por múltiplos tokens no título, autor e subtítulo', () => {
  const books = [
    { id: 1, title: 'Dom Casmurro', author: 'Machado de Assis', subtitle: null },
    { id: 2, title: 'Memórias Póstumas de Brás Cubas', author: 'Machado de Assis', subtitle: 'Edição Crítica' },
    { id: 3, title: 'A Arte da Guerra', author: 'Sun Tzu', subtitle: null },
    { id: 4, title: 'O Alienista', author: 'Machado de Assis', subtitle: null },
  ]

  // Busca simples sem acento encontrando livro com acento
  const res1 = filterBooks(books, 'memorias')
  assert.equal(res1.length, 1)
  assert.equal(res1[0].id, 2)

  // Busca por autor
  const res2 = filterBooks(books, 'sun tzu')
  assert.equal(res2.length, 1)
  assert.equal(res2[0].id, 3)

  // Busca por múltiplos tokens em campos diferentes (título + autor)
  const res3 = filterBooks(books, 'machado alienista')
  assert.equal(res3.length, 1)
  assert.equal(res3[0].id, 4)

  // Busca por subtítulo
  const res4 = filterBooks(books, 'critica')
  assert.equal(res4.length, 1)
  assert.equal(res4[0].id, 2)

  // Busca vazia retorna todos os livros
  const resEmpty = filterBooks(books, '   ')
  assert.equal(resEmpty.length, 4)

  // Busca sem correspondência
  const resNone = filterBooks(books, 'psicologia')
  assert.equal(resNone.length, 0)
})

test('sortBooks ordena acervo respeitando todas as opções explícitas', () => {
  const books = [
    { id: 1, title: 'Memórias Póstumas', author: 'Machado de Assis', year: 1881, created_at: '2026-01-01T10:00:00Z', updated_at: '2026-02-01T10:00:00Z' },
    { id: 2, title: 'A Arte da Guerra', author: 'Sun Tzu', year: null, created_at: '2026-01-02T10:00:00Z', updated_at: '2026-01-05T10:00:00Z' },
    { id: 3, title: 'Dom Casmurro', author: 'Machado de Assis', year: 1899, created_at: '2026-01-03T10:00:00Z', updated_at: '2026-03-01T10:00:00Z' },
    { id: 4, title: 'Árvore Solitária', author: 'Álvares de Azevedo', year: 1850, created_at: '2026-01-04T10:00:00Z', updated_at: '2026-01-04T10:00:00Z' },
  ]

  // Título A-Z (Árvore deve se ordenar alfabeticamente com A)
  const byTitleAsc = sortBooks(books, 'title-asc')
  assert.equal(byTitleAsc[0].title, 'A Arte da Guerra')
  assert.equal(byTitleAsc[1].title, 'Árvore Solitária')
  assert.equal(byTitleAsc[2].title, 'Dom Casmurro')
  assert.equal(byTitleAsc[3].title, 'Memórias Póstumas')

  // Título Z-A
  const byTitleDesc = sortBooks(books, 'title-desc')
  assert.equal(byTitleDesc[0].title, 'Memórias Póstumas')
  assert.equal(byTitleDesc[3].title, 'A Arte da Guerra')

  // Recentemente adicionados (created_at desc)
  const byRecentCreated = sortBooks(books, 'recent-created')
  assert.equal(byRecentCreated[0].id, 4)
  assert.equal(byRecentCreated[3].id, 1)

  // Recentemente modificados (updated_at desc)
  const byRecentUpdated = sortBooks(books, 'recent-updated')
  assert.equal(byRecentUpdated[0].id, 3) // updated in March
  assert.equal(byRecentUpdated[1].id, 1) // updated in February

  // Mais antigos adicionados (created_at asc)
  const byOldestCreated = sortBooks(books, 'oldest-created')
  assert.equal(byOldestCreated[0].id, 1)

  // Ano de publicação (decrescente, nulos por último)
  const byYearDesc = sortBooks(books, 'year-desc')
  assert.equal(byYearDesc[0].year, 1899)
  assert.equal(byYearDesc[1].year, 1881)
  assert.equal(byYearDesc[2].year, 1850)
  assert.equal(byYearDesc[3].year, null)

  // Autor A-Z com autores nulos posicionados no final
  const withNullAuthors = [
    { id: 1, title: 'Livro Sem Autor', author: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
    { id: 2, title: 'Belo Livro', author: 'Bernardo Guimarães', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
    { id: 3, title: 'Alquimia', author: 'Clarice Lispector', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
  ]
  const byAuthor = sortBooks(withNullAuthors, 'author-asc')
  assert.equal(byAuthor[0].author, 'Bernardo Guimarães')
  assert.equal(byAuthor[1].author, 'Clarice Lispector')
  assert.equal(byAuthor[2].author, null)
})

test('filterBooks lida com valores ausentes sem lançar exceções', () => {
  const books = [
    { id: 1, title: 'Livro Vazio', author: null, subtitle: null },
    { id: 2, title: 'Outro Livro', author: undefined, subtitle: '' },
  ]
  assert.equal(filterBooks(books, 'vazio').length, 1)
  assert.equal(filterBooks(books, 'outro').length, 1)
  assert.equal(filterBooks(books, 'nada').length, 0)
})

test('filterBooks filtra por categoria exata, recursiva com descendentes e livros sem categoria', () => {
  const books = [
    {
      id: 1,
      title: 'Raízes do Brasil Colônia',
      author: 'Sérgio Buarque',
      categories: [{ id: 'historia-brasil-colonia', name: 'Brasil Colônia', parent_id: 'historia-brasil', path: 'História / Brasil Colônia' }],
    },
    {
      id: 2,
      title: 'O Império das Américas',
      author: 'Laurentino Gomes',
      categories: [{ id: 'historia-brasil-imperio', name: 'Brasil Império', parent_id: 'historia-brasil', path: 'História / Brasil Império' }],
    },
    {
      id: 3,
      title: 'Ética a Nicômaco',
      author: 'Aristóteles',
      categories: [{ id: 'filosofia-etica', name: 'Ética', parent_id: 'filosofia', path: 'Filosofia / Ética' }],
    },
    {
      id: 4,
      title: 'Livro Sem Categoria',
      author: 'Autor Anônimo',
      categories: [],
    },
  ]

  // 1. Categoria folha exata sem descendentes adicionais
  const resLeaf = filterBooks(books, '', 'historia-brasil-colonia')
  assert.equal(resLeaf.length, 1)
  assert.equal(resLeaf[0].id, 1)

  // 2. Categoria pai com conjunto de descendentes recursivos
  const historiaBrasilDescendants = new Set([
    'historia-brasil',
    'historia-brasil-colonia',
    'historia-brasil-imperio',
  ])
  const resParent = filterBooks(books, '', 'historia-brasil', historiaBrasilDescendants)
  assert.equal(resParent.length, 2)
  const parentIds = resParent.map((b) => b.id).sort()
  assert.deepEqual(parentIds, [1, 2])

  // 3. Categoria especial sem categoria (__uncategorized__)
  const resUncategorized = filterBooks(books, '', '__uncategorized__')
  assert.equal(resUncategorized.length, 1)
  assert.equal(resUncategorized[0].id, 4)

  // 4. Combinação de categoria pai + busca textual por token
  const resCombo = filterBooks(books, 'laurentino', 'historia-brasil', historiaBrasilDescendants)
  assert.equal(resCombo.length, 1)
  assert.equal(resCombo[0].id, 2)

  // 5. Categoria inexistente sem descendentes
  const resNone = filterBooks(books, '', 'categoria-inexistente')
  assert.equal(resNone.length, 0)
})

