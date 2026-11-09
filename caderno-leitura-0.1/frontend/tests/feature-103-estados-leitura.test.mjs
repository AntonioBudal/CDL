import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { filterBooks } from '../src/composables/useLibraryFilter.ts'
import { BOOK_READING_STATE_OPTIONS, bookReadingStateLabel } from '../src/types.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const books = [
  { id: 1, title: 'Livro A', author: 'Autora Fictícia', reading_state: 'lendo', categories: [] },
  { id: 2, title: 'Livro B', author: 'Autor Teste', reading_state: 'lido', categories: [] },
  { id: 3, title: 'Livro C', author: null, reading_state: null, categories: [] },
  { id: 4, title: 'Livro D', author: null, categories: [] },
]

test('103: estados e rótulos', () => {
  assert.deepEqual(BOOK_READING_STATE_OPTIONS.map((o) => o.value), ['quero_ler', 'lendo', 'lido', 'abandonado'])
  assert.equal(bookReadingStateLabel('quero_ler'), 'Quero ler')
  assert.equal(bookReadingStateLabel(null), '')
})

test('103: filtro por estado de leitura combinado com a busca', () => {
  assert.deepEqual(filterBooks(books, '', null, null, 'all').map((b) => b.id), [1, 2, 3, 4])
  assert.deepEqual(filterBooks(books, '', null, null, 'lendo').map((b) => b.id), [1])
  assert.deepEqual(filterBooks(books, '', null, null, 'none').map((b) => b.id), [3, 4])
  assert.deepEqual(filterBooks(books, 'teste', null, null, 'lido').map((b) => b.id), [2])
  assert.deepEqual(filterBooks(books, '').map((b) => b.id), [1, 2, 3, 4], 'sem o parâmetro nada muda')
})

test('103: filtro lembrado no navegador com try/catch e limpo junto com os outros', () => {
  const src = read('composables/useLibraryFilter.ts')
  assert.match(src, /STORAGE_KEY_READING_STATE = 'caderno_library_reading_state'/)
  assert.match(src, /try \{\n\s+const saved = typeof localStorage/)
  assert.match(src, /setReadingStateFilter\('all'\)/)
  assert.match(src, /hasActiveSearch\.value \|\| hasActiveCategory\.value \|\| hasActiveReadingState\.value/)
  const toolbar = read('components/LibraryToolbar.vue')
  assert.match(toolbar, /id="library-reading-state-select"/)
  assert.ok(toolbar.includes('<option value="none">Sem estado</option>'))
})

test('103: seletor como radiogroup com setas, datas e gravação com versão', () => {
  const comp = read('components/books/BookReadingState.vue')
  assert.match(comp, /role="radiogroup"/)
  assert.match(comp, /role="radio"/)
  assert.match(comp, /:aria-checked="option\.value === current"/)
  assert.match(comp, /'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp'/)
  assert.match(comp, /\{ quiet: option\.value !== current/)
  assert.match(comp, /type="date"/)
  assert.match(comp, /:min="started \|\| undefined"/)
  assert.match(comp, /body\.expected_version = props\.book\.version/)
  assert.match(comp, /api\.updateBook\(props\.book\.id, body\)/)
  assert.ok(comp.includes("label: 'Sem estado'"))
})

test('103: página do livro mostra o seletor só ao dono; biblioteca mostra o selo', () => {
  const view = read('views/BookView.vue')
  assert.match(view, /<BookReadingState v-if="book\.can_edit !== false" :book="book" @saved="onBookSaved" \/>/)
  const books = read('views/BooksView.vue')
  assert.equal((books.match(/class="reading-state-badge"/g) || []).length, 2)
  assert.match(books, /@update:reading-state-filter="setReadingStateFilter"/)
})
