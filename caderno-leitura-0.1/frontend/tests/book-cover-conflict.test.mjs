import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import { bookAfterCoverChange } from '../src/utils/bookCover.ts'

const book = { id: 1, title: 'Livro de Teste', author: null, cover_image: null, updated_at: '2026-01-01T10:00:00Z', version: 3 }

test('depois de trocar a capa, o livro leva a data nova devolvida pelo servidor', () => {
  const res = { book_id: 1, cover_image: 'capa-nova', cover_url: '/api/covers/capa-nova', updated_at: '2026-01-01T11:00:00Z', message: '' }
  const updated = bookAfterCoverChange(book, res)
  assert.equal(updated.cover_image, 'capa-nova')
  assert.equal(updated.updated_at, '2026-01-01T11:00:00Z')
  assert.equal(updated.title, 'Livro de Teste')
  assert.equal(book.updated_at, '2026-01-01T10:00:00Z', 'o objeto original não é alterado')
})

test('remover a capa também atualiza a data; resposta sem data mantém a anterior', () => {
  const withCover = { ...book, cover_image: 'capa' }
  const removed = bookAfterCoverChange(withCover, { book_id: 1, cover_image: null, cover_url: null, updated_at: '2026-01-01T12:00:00Z', message: '' })
  assert.equal(removed.cover_image, null)
  assert.equal(removed.updated_at, '2026-01-01T12:00:00Z')
  const legacy = bookAfterCoverChange(withCover, { book_id: 1, cover_image: 'x', cover_url: null, message: '' })
  assert.equal(legacy.updated_at, book.updated_at)
})

test('o formulário de edição usa a data nova nos três caminhos da capa', () => {
  const source = fs.readFileSync(new URL('../src/components/BookEditModal.vue', import.meta.url), 'utf8')
  assert.equal(source.match(/emit\('saved', bookAfterCoverChange\(props\.book, res\)\)/g)?.length, 3)
  assert.doesNotMatch(source, /emit\('saved', \{ \.\.\.props\.book, cover_image/)
})
