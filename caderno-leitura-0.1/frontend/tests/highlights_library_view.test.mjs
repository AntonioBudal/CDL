import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { getHighlightLibrary, updateStudyHighlight, deleteStudyHighlight } from '../src/services/api.ts'

const highlightsLibraryViewPath = path.resolve('src/views/HighlightsLibraryView.vue')
const highlightCardPath = path.resolve('src/components/highlights/HighlightCard.vue')
const highlightFilterToolbarPath = path.resolve('src/components/highlights/HighlightFilterToolbar.vue')

// ============================================================================
// User Story 1: Exploração Transversal e Busca Textual Instantânea (P1 - MVP)
// ============================================================================

test('US1: getHighlightLibrary executa GET para /highlights/library com parâmetros', async () => {
  const originalFetch = globalThis.fetch
  let calledUrl = ''
  let calledMethod = ''

  globalThis.fetch = async (url, options) => {
    calledUrl = String(url)
    calledMethod = options?.method || 'GET'
    return {
      ok: true,
      status: 200,
      json: async () => ({
        items: [
          {
            id: 1,
            study_id: 10,
            study_title: 'Estudo Teste',
            chapter_id: 2,
            chapter_title: 'Capítulo 1',
            book_id: 3,
            book_title: 'Livro Sintético',
            book_author: 'Autor Teste',
            section: 'summary',
            start_offset: 0,
            end_offset: 10,
            selected_text: 'Trecho teste',
            prefix: '',
            suffix: '',
            color: 'yellow',
            kind: 'highlight',
            note: 'Nota de teste',
            created_at: '2026-10-06T12:00:00Z',
            updated_at: '2026-10-06T12:00:00Z',
          },
        ],
        total: 1,
        page: 1,
        per_page: 15,
        pages: 1,
        has_next: false,
        has_prev: false,
        available_books: [{ id: 3, title: 'Livro Sintético', count: 1 }],
        summary: {
          total_highlights: 1,
          total_notes: 0,
          total_quotes: 0,
          total_hidden: 0,
          total_questions: 0,
        },
      }),
    }
  }

  try {
    const res = await getHighlightLibrary({ q: 'teste', page: 1, per_page: 15 })
    assert.equal(calledMethod, 'GET')
    assert.ok(calledUrl.includes('/highlights/library?'))
    assert.ok(calledUrl.includes('q=teste'))
    assert.equal(res.total, 1)
    assert.equal(res.items.length, 1)
    assert.equal(res.items[0].selected_text, 'Trecho teste')
    assert.equal(res.items[0].book_title, 'Livro Sintético')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('US1: HighlightsLibraryView.vue possui esqueleto de loading, modos de visão e estado vazio', () => {
  assert.ok(fs.existsSync(highlightsLibraryViewPath), 'HighlightsLibraryView.vue deve existir')
  const content = fs.readFileSync(highlightsLibraryViewPath, 'utf-8')

  // Estrutura principal
  assert.match(content, /Destaques e Anotações/)
  assert.match(content, /HighlightFilterToolbar/)
  assert.match(content, /HighlightCard/)

  // Modos de visualização: Recentes e Por Obra
  assert.match(content, /viewMode === 'recent'/)
  assert.match(content, /viewMode === 'by_book'/)
  assert.match(content, /groupedByBook/)

  // Skeletons de carregamento e estado vazio
  assert.match(content, /skeletons-list|skeleton-card/)
  assert.match(content, /empty-state/)
})

// ============================================================================
// User Story 2: Filtragem Multidimensional e Sincronização na URL (P2)
// ============================================================================

test('US2: HighlightFilterToolbar.vue possui debounce de busca e seletores de livro, tipo e cor', () => {
  assert.ok(fs.existsSync(highlightFilterToolbarPath), 'HighlightFilterToolbar.vue deve existir')
  const content = fs.readFileSync(highlightFilterToolbarPath, 'utf-8')

  // Debounce de 250ms
  assert.match(content, /250/)
  assert.match(content, /debounceTimeout/)

  // Seletores de filtros
  assert.match(content, /availableBooks/)
  assert.match(content, /kindsList/)
  assert.match(content, /colorsList/)
  assert.match(content, /color-swatches|swatch-btn/)

  // Alternador de modo e botão de limpar filtros
  assert.match(content, /Recentes/)
  assert.match(content, /Por Obra/)
  assert.match(content, /btn-reset-filters/)
})

test('US2: HighlightsLibraryView.vue sincroniza parâmetros na URL e possui paginação', () => {
  const content = fs.readFileSync(highlightsLibraryViewPath, 'utf-8')

  // Sincronização de URL
  assert.match(content, /initFromUrlParams/)
  assert.match(content, /updateUrlParams/)
  assert.match(content, /router\.replace/)

  // Paginação estruturada
  assert.match(content, /pagination-nav/)
  assert.match(content, /pagination-btn/)
  assert.match(content, /totalPages/)
})

// ============================================================================
// User Story 3: Salto Contextual e Gestão Rápida In-Card (P3)
// ============================================================================

test('US3: updateStudyHighlight e deleteStudyHighlight chamam endpoints corretos', async () => {
  const originalFetch = globalThis.fetch
  let patchUrl = ''
  let deleteUrl = ''

  globalThis.fetch = async (url, options) => {
    const method = options?.method || 'GET'
    if (method === 'PATCH') {
      patchUrl = String(url)
      return {
        ok: true,
        status: 200,
        json: async () => ({
          id: 5,
          study_id: 10,
          user_id: 'user-uuid',
          section: 'summary',
          start_offset: 0,
          end_offset: 10,
          selected_text: 'Trecho',
          prefix: '',
          suffix: '',
          color: 'yellow',
          kind: 'note',
          note: 'Nota atualizada',
          created_at: '2026-10-06T12:00:00Z',
          updated_at: '2026-10-06T12:30:00Z',
        }),
      }
    }
    if (method === 'DELETE') {
      deleteUrl = String(url)
      return {
        ok: true,
        status: 204,
        json: async () => ({}),
      }
    }
    return { ok: true, status: 200, json: async () => ({}) }
  }

  try {
    const updated = await updateStudyHighlight(10, 5, { note: 'Nota atualizada' })
    assert.equal(patchUrl, '/api/studies/10/highlights/5')
    assert.equal(updated.note, 'Nota atualizada')

    await deleteStudyHighlight(10, 5)
    assert.equal(deleteUrl, '/api/studies/10/highlights/5')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('US3: HighlightCard.vue renderiza salto contextual com âncora, edição de nota e exclusão in-card', () => {
  assert.ok(fs.existsSync(highlightCardPath), 'HighlightCard.vue deve existir')
  const content = fs.readFileSync(highlightCardPath, 'utf-8')

  // Salto contextual com âncora #highlight-{id}
  assert.match(content, /#highlight-\$\{item\.id\}/)
  assert.match(content, /Abrir no Estudo/)

  // Edição rápida in-card
  assert.match(content, /isEditing/)
  assert.match(content, /note-textarea/)
  assert.match(content, /saveNote/)
  assert.match(content, /cancelEditing/)

  // Confirmação de exclusão in-card
  assert.match(content, /isConfirmingDelete/)
  assert.match(content, /delete-confirmation-banner/)
  assert.match(content, /confirmDelete/)

  // Truncamento harmonioso de textos extensos
  assert.match(content, /isLongText/)
  assert.match(content, /displayText/)
  assert.match(content, /btn-toggle-expand/)
})

// ============================================================================
// Phase 6: Responsividade Móvel e Ergonomia
// ============================================================================

test('Phase 6: Componentes possuem suporte responsivo e alvos táteis mínimos de 44x44px', () => {
  const cardContent = fs.readFileSync(highlightCardPath, 'utf-8')
  const toolbarContent = fs.readFileSync(highlightFilterToolbarPath, 'utf-8')
  const viewContent = fs.readFileSync(highlightsLibraryViewPath, 'utf-8')

  // Alvos mínimos de toque no mobile
  assert.match(cardContent, /min-height:\s*44px/)
  assert.match(toolbarContent, /min-height:\s*44px/)
  assert.match(viewContent, /min-height:\s*44px/)

  // Gaveta móvel de filtros no toolbar
  assert.match(toolbarContent, /mobileDrawerOpen/)
  assert.match(toolbarContent, /btn-mobile-filter-toggle/)
})
