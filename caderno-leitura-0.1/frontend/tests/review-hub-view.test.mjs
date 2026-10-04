import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { reviewApi } from '../src/api/review.ts'

const reviewHubViewPath = path.resolve('src/views/ReviewHubView.vue')
const reviewStatsHeaderPath = path.resolve('src/components/review/ReviewStatsHeader.vue')
const reviewSummaryModalPath = path.resolve('src/components/review/ReviewSummaryModal.vue')

// ============================================================================
// User Story 1: Hub Central de Revisão e Seleção por Escopo (P1 - MVP)
// ============================================================================

test('US1: reviewApi.getStats executa GET para /api/review/stats', async () => {
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
        total_eligible: 10,
        total_questions: 6,
        total_hidden: 4,
        reviewed_today: 2,
        pending_review: 8,
        books: [{ book_id: 1, title: 'Livro Teste', items_count: 10 }],
      }),
    }
  }

  try {
    const stats = await reviewApi.getStats()
    assert.equal(calledMethod, 'GET')
    assert.equal(calledUrl, '/api/review/stats')
    assert.equal(stats.total_eligible, 10)
    assert.equal(stats.total_questions, 6)
    assert.equal(stats.total_hidden, 4)
    assert.equal(stats.books.length, 1)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('US1: reviewApi.getItems envia filtros por livro, capitulo e tipo', async () => {
  const originalFetch = globalThis.fetch
  let calledUrl = ''

  globalThis.fetch = async (url) => {
    calledUrl = String(url)
    return {
      ok: true,
      status: 200,
      json: async () => [
        {
          id: 1,
          study_id: 10,
          study_title: 'Estudo 1',
          book_id: 2,
          book_title: 'Livro 2',
          chapter_id: 3,
          chapter_name: 'Capítulo 3',
          kind: 'question',
          section: 'explanation',
          question_text: 'O que é virtude?',
          expected_answer: 'Um hábito bom.',
          context_prefix: '',
          context_suffix: '',
          last_reviewed_at: null,
          review_count: 0,
          last_rating: null,
        },
      ],
    }
  }

  try {
    const items = await reviewApi.getItems({ book_id: 2, chapter_id: 3, kind: 'question', limit: 10 })
    assert.ok(calledUrl.startsWith('/api/review/items?'))
    assert.ok(calledUrl.includes('book_id=2'))
    assert.ok(calledUrl.includes('chapter_id=3'))
    assert.ok(calledUrl.includes('kind=question'))
    assert.ok(calledUrl.includes('limit=10'))
    assert.equal(items.length, 1)
    assert.equal(items[0].kind, 'question')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('US1: ReviewStatsHeader.vue renderiza cards de métricas e pílulas de filtro', () => {
  assert.ok(fs.existsSync(reviewStatsHeaderPath), 'ReviewStatsHeader.vue deve existir')
  const content = fs.readFileSync(reviewStatsHeaderPath, 'utf-8')

  // Cards de métricas
  assert.match(content, /total_eligible|totalEligible/)
  assert.match(content, /total_questions|totalQuestions/)
  assert.match(content, /total_hidden|totalHidden/)
  assert.match(content, /reviewed_today|reviewedToday/)

  // Pílulas de filtro rápido
  assert.match(content, /filter-pill|kind-filter/)
  assert.match(content, /question/)
  assert.match(content, /hidden/)
})

test('US1: ReviewHubView.vue exibe estado vazio acolhedor e botão Iniciar Revisão', () => {
  assert.ok(fs.existsSync(reviewHubViewPath), 'ReviewHubView.vue deve existir')
  const content = fs.readFileSync(reviewHubViewPath, 'utf-8')

  // Estado vazio e botão de início
  assert.match(content, /empty-state|empty-review/)
  assert.match(content, /Iniciar Revisão|start-review-btn/)
  assert.match(content, /ReviewStatsHeader/)
})

// ============================================================================
// User Story 3: Conclusão de Sessão e Resumo de Assimilação (P3)
// ============================================================================

test('US3: ReviewSummaryModal.vue renderiza balanço de retenção e opções de continuidade', () => {
  assert.ok(fs.existsSync(reviewSummaryModalPath), 'ReviewSummaryModal.vue deve existir')
  const content = fs.readFileSync(reviewSummaryModalPath, 'utf-8')

  // Balanço de retenção por dificuldade
  assert.match(content, /easy|fácil|facil/i)
  assert.match(content, /medium|médio|medio/i)
  assert.match(content, /hard|difícil|dificil/i)

  // Botões de continuidade
  assert.match(content, /Revisar mais|review-more/i)
  assert.match(content, /Voltar|acervo|concluir/i)
})
