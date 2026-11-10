import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('104: tipos e API com capítulo e bandeja', () => {
  const types = read('types.ts')
  assert.match(types, /chapter_id\?: number \| null\n\s+chapter_name\?: string \| null/)
  assert.match(types, /export interface InboxBookTrayResponse \{\n\s+by_chapter: Record<string, number>\n\s+without_chapter: number/)
  const api = read('services/api.ts')
  assert.match(api, /if \(params\?\.chapter_id != null\) searchParams\.set\('chapter_id'/)
  assert.match(api, /getInboxBookTray: \(bookId: number, signal\?: AbortSignal\) =>/)
})

test('104: captura rápida com capítulo e padrão vindo da página do livro', () => {
  const qc = read('composables/useQuickCapture.ts')
  assert.match(qc, /function setPageContext\(bookId: number \| null, chapterId: number \| null\)/)
  assert.match(qc, /const fromPage = options\?\.bookId === undefined && options\?\.chapterId === undefined/)
  assert.match(qc, /chapter_id: payload\.chapter_id \?\? null/)
  const modal = read('components/inbox/QuickCaptureModal.vue')
  assert.match(modal, /id="capture-chapter"/)
  assert.match(modal, /@change="onBookChange"/)
  assert.match(modal, /void loadChapters\(selectedBookId\.value, defaultChapterId\.value\)/)
  assert.match(modal, /chapter_id: selectedChapterId\.value \|\| null/)
})

test('104: bandeja do capítulo com virar estudo, arquivar e abrir na Mesa', () => {
  const tray = read('components/books/ChapterTray.vue')
  assert.match(tray, /api\.getInboxCaptures\(\{ status: 'inbox', chapter_id: props\.chapterId, limit: 100 \}/)
  assert.match(tray, /promote_inbox_id: String\(capture\.id\), book: String\(props\.bookId\), chapter: String\(props\.chapterId\)/)
  assert.match(tray, /api\.updateInboxCapture\(capture\.id, \{ status: 'archived' \}\)/)
  assert.match(tray, /emit\('changed'\)/)
  assert.match(tray, /query: \{ livro: String\(bookId\) \}/)
  assert.match(tray, /quickCapture\.open\(\{ bookId: props\.bookId, chapterId: props\.chapterId \}\)/)
  assert.match(tray, /aria-live="polite"/)
  assert.match(tray, /class="quiet chapter-tray-action"/)
})

test('104: página do livro mostra contagens, bandeja e linha sem capítulo só para o dono', () => {
  const view = read('views/BookView.vue')
  assert.match(view, /api\.getInboxBookTray\(id, controller\.signal\)/)
  assert.match(view, /class="chapter-tray-badge"/)
  assert.match(view, /<ChapterTray\n\s+v-if="isOwnBook"/)
  assert.match(view, /trayCounts\.without_chapter > 0/)
  assert.match(view, /quickCapture\.setPageContext\(own \? currentBookId : null, own \? chapterId : null\)/)
  assert.match(view, /quickCapture\.setPageContext\(null, null\)/)
})

test('104: Importar, cartão e Mesa conhecem o capítulo', () => {
  assert.match(read('views/ImportView.vue'), /if \(capture\.chapter_id\) preferredChapter = capture\.chapter_id/)
  const card = read('components/inbox/CaptureItemCard.vue')
  assert.match(card, /capture\.chapter_name/)
  assert.match(card, /\.\.\.\(props\.capture\.book_id \? \{ chapter_id: editChapterId\.value \} : \{\}\)/)
  const inbox = read('views/InboxView.vue')
  assert.match(inbox, /const value = Number\(route\.query\.livro\)/)
  assert.match(inbox, /book_id: bookFilterId\.value \?\? undefined/)
  assert.match(inbox, /query\.chapter = String\(capture\.chapter_id\)/)
})
