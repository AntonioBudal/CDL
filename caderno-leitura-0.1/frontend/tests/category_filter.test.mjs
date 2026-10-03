import test from 'node:test'
import assert from 'node:assert/strict'
import { filterBooks, normalizeText } from '../src/composables/useLibraryFilter.ts'

test('normalizeText trata diacríticos, pontuação e caixa baixa', () => {
  assert.equal(normalizeText('História do Brasil'), 'historia do brasil')
  assert.equal(normalizeText('Ficção Científica!'), 'ficcao cientifica!')
  assert.equal(normalizeText('  Filosofia   Moderna  '), 'filosofia moderna')
  assert.equal(normalizeText(null), '')
})

test('filterBooks filtra acervo por categorias canônicas planas', () => {
  const books = [
    {
      id: 1,
      title: 'Crítica da Razão Pura',
      author: 'Immanuel Kant',
      categories: [{ id: 'filosofia', name: 'Filosofia', is_canonical: true, parent_id: null, path: 'filosofia' }],
    },
    {
      id: 2,
      title: 'Casa-Grande & Senzala',
      author: 'Gilberto Freyre',
      categories: [
        { id: 'historia', name: 'História', is_canonical: true, parent_id: null, path: 'historia' },
        { id: 'sociologia', name: 'Sociologia', is_canonical: true, parent_id: null, path: 'sociologia' },
      ],
    },
    {
      id: 3,
      title: 'O Fim da Eternidade',
      author: 'Isaac Asimov',
      categories: [{ id: 'ficcao', name: 'Ficção', is_canonical: true, parent_id: null, path: 'ficcao' }],
    },
    {
      id: 4,
      title: 'Caderno de Notas Anônimo',
      author: 'Desconhecido',
      categories: [],
    },
  ]

  // 1. Filtrar por categoria canônica Filosofia
  const resFilo = filterBooks(books, '', 'filosofia')
  assert.equal(resFilo.length, 1)
  assert.equal(resFilo[0].id, 1)

  // 2. Filtrar por categoria com múltiplos livros (Sociologia)
  const resSocio = filterBooks(books, '', 'sociologia')
  assert.equal(resSocio.length, 1)
  assert.equal(resSocio[0].id, 2)

  // 3. Filtrar livros sem categoria
  const resUncat = filterBooks(books, '', '__uncategorized__')
  assert.equal(resUncat.length, 1)
  assert.equal(resUncat[0].id, 4)

  // 4. Combinação de filtro de categoria e busca textual
  const resCombined = filterBooks(books, 'Kant', 'filosofia')
  assert.equal(resCombined.length, 1)
  assert.equal(resCombined[0].id, 1)

  const resCombinedMiss = filterBooks(books, 'Freyre', 'filosofia')
  assert.equal(resCombinedMiss.length, 0)
})

test('filterBooks lida com busca de livros associados a múltiplas categorias canônicas', () => {
  const books = [
    {
      id: 10,
      title: 'O Príncipe',
      author: 'Nicolau Maquiavel',
      categories: [
        { id: 'filosofia', name: 'Filosofia', is_canonical: true },
        { id: 'politica', name: 'Política', is_canonical: true },
        { id: 'historia', name: 'História', is_canonical: true },
      ],
    },
  ]

  // Deve ser encontrado por qualquer uma das três categorias
  assert.equal(filterBooks(books, '', 'filosofia').length, 1)
  assert.equal(filterBooks(books, '', 'politica').length, 1)
  assert.equal(filterBooks(books, '', 'historia').length, 1)
  assert.equal(filterBooks(books, '', 'ciencia').length, 0)
})
