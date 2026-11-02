import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// F0.10.02.5 — capa no tamanho certo no celular, ícones do capítulo selecionado legíveis e gerenciamento de
// capítulos (mover, renomear, excluir) no desktop e no celular.
const srcDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../src')
const bookView = fs.readFileSync(path.join(srcDir, 'views/BookView.vue'), 'utf-8')
const css = fs.readFileSync(path.join(srcDir, 'appearance-advanced.css'), 'utf-8')
const api = fs.readFileSync(path.join(srcDir, 'services/api.ts'), 'utf-8')

test('1.1 a regra móvel da capa mira o container real do BookCover', () => {
  assert.match(bookView, /\.book-header-cover :deep\(\.book-cover-container\)/)
  assert.doesNotMatch(bookView, /:deep\(\.book-cover\)/, 'A classe .book-cover não existe mais no BookCover')
})

test('1.2 as ferramentas da pílula selecionada usam a cor de texto da seleção', () => {
  assert.match(css, /--button-fg:\s*var\(--quiet-fg,\s*var\(--color-text\)\)/)
  assert.match(css, /color:\s*var\(--quiet-fg-disabled,\s*var\(--color-muted\)\)/)
  assert.match(bookView, /\.chapter-pill\.selected \.pill-tool-btn\s*\{[^}]*--quiet-fg:\s*var\(--color-selected-text\)/)
})

test('2. desktop: o capítulo selecionado tem botão de excluir com confirmação', () => {
  assert.match(bookView, /class="pill-tool-btn quiet[^"]*"[\s\S]{0,200}aria-label="Excluir capítulo"/)
  assert.match(bookView, /<TrashConfirmModal[\s\S]{0,400}confirmDeleteChapter/)
  assert.match(api, /deleteChapter:\s*\(bookId: number, chapterId: number\)/)
})

test('2. celular: menu "Gerenciar capítulo" com as quatro ações e campo de renomear', () => {
  const start = bookView.indexOf('chapters-mobile-manage')
  assert.ok(start > 0, 'Deve existir o menu de gerenciamento no celular')
  const block = bookView.slice(start, start + 4000)
  for (const label of ['Mover para trás', 'Mover para frente', 'Renomear', 'Excluir']) {
    assert.ok(block.includes(label), `Menu móvel deve oferecer "${label}"`)
  }
  assert.match(bookView, /class="chapters-mobile-edit"/)
})
