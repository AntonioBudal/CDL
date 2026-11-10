import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { formatReferenceABNT } from '../src/utils/citationFormatter.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const base = {
  selected_text: 'Trecho.',
  book_title: 'Livro de Teste',
  book_subtitle: '',
  book_author: 'Ana Fictícia',
  book_year: 1997,
  chapter_title: '',
}

test('106: referência ABNT com local e editora', () => {
  const full = formatReferenceABNT({ ...base, book_publication_place: 'São Paulo', book_publisher: 'Editora Fictícia' })
  assert.equal(full.text, 'FICTÍCIA, Ana. Livro de Teste. São Paulo: Editora Fictícia, 1997.')
  assert.equal(full.html, 'FICTÍCIA, Ana. <i>Livro de Teste</i>. São Paulo: Editora Fictícia, 1997.')
  assert.equal(formatReferenceABNT({ ...base, book_publisher: 'Editora Fictícia' }).text, 'FICTÍCIA, Ana. Livro de Teste. [S. l.]: Editora Fictícia, 1997.')
  assert.equal(formatReferenceABNT({ ...base, book_publication_place: 'Lisboa' }).text, 'FICTÍCIA, Ana. Livro de Teste. Lisboa: [s. n.], 1997.')
  assert.equal(formatReferenceABNT(base).text, 'FICTÍCIA, Ana. Livro de Teste. 1997.', 'sem os dois, como antes')
})

test('106: componente valida o ISBN antes de buscar e aplica sem sobrescrever', () => {
  const comp = read('components/books/IsbnLookup.vue')
  assert.match(comp, /function isbnLooksValid\(raw: string\): boolean/)
  assert.match(comp, /if \(!isbnLooksValid\(isbn\.value\)\) \{\n\s+error\.value = 'ISBN inválido/)
  assert.match(comp, /if \(overwrite\.value \|\| !props\.current\[key\]\?\.trim\(\)\) chosen\[key\] = value/)
  assert.ok(comp.includes('Substituir o que já está preenchido'))
  assert.ok(comp.includes('Consulta a BrasilAPI e a Open Library pelo servidor do Leitorum, só quando você clica.'))
  assert.match(comp, /suggestion\.existing_book/)
  assert.match(comp, /aria-live="polite"/)
  assert.match(comp, /class="quiet isbn-search"/)
})

test('106: cadastro, edição, página do livro e API', () => {
  const api = read('services/api.ts')
  assert.match(api, /lookupIsbn: \(isbn: string, signal\?: AbortSignal\) =>/)
  assert.match(api, /`\/books\/isbn\/\$\{encodeURIComponent\(isbn\.replace/)
  const edit = read('components/BookEditModal.vue')
  assert.match(edit, /<IsbnLookup v-model:isbn="isbn" id-prefix="edit-book"/)
  assert.match(edit, /publication_place: publicationPlace\.value\.trim\(\) \|\| null/)
  const books = read('views/BooksView.vue')
  assert.match(books, /<IsbnLookup v-model:isbn="newIsbn" id-prefix="new-book"/)
  assert.match(books, /isbn: newIsbn\.value\.trim\(\) \|\| null/)
  assert.match(read('views/BookView.vue'), /class="book-imprint"/)
})

test('106: landing diz que a busca por ISBN é uma conexão externa a pedido', () => {
  const facts = read('components/landing/SovereigntySection.vue')
  assert.ok(facts.includes('ao buscar dados de um livro pelo ISBN — sempre a seu pedido.'))
  const trust = read('components/landing/TrustChallengeSection.vue')
  assert.ok(trust.includes('a busca\n        pelo ISBN são feitas pelo servidor do Leitorum, a seu pedido'))
})
