import test from 'node:test'
import assert from 'node:assert/strict'
import { useReviewSession } from '../src/composables/useReviewSession.ts'

function createSampleItems(count = 3) {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    study_id: 10,
    study_title: 'Estudo Teste',
    book_id: 1,
    book_title: 'Livro Teste',
    chapter_id: 1,
    chapter_name: 'Capítulo 1',
    kind: i % 2 === 0 ? 'question' : 'hidden',
    section: 'summary',
    question_text: `Pergunta ${i + 1}`,
    expected_answer: `Resposta ${i + 1}`,
    context_prefix: 'Prefixo',
    context_suffix: 'Sufixo',
    last_reviewed_at: null,
    review_count: 0,
    last_rating: null,
  }))
}

test('useReviewSession: inicializa com estado limpo', () => {
  const session = useReviewSession()
  assert.equal(session.state.items.length, 0)
  assert.equal(session.state.currentIndex, 0)
  assert.equal(session.state.isRevealed, false)
  assert.equal(session.state.isCompleted, false)
  assert.equal(session.currentItem.value, null)
})

test('useReviewSession: carrega itens e atualiza item atual e progresso', async () => {
  const originalFetch = globalThis.fetch
  const mockItems = createSampleItems(2)

  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => mockItems,
  })

  try {
    const session = useReviewSession()
    await session.loadItems({ limit: 10 })

    assert.equal(session.state.items.length, 2)
    assert.equal(session.state.currentIndex, 0)
    assert.equal(session.currentItem.value?.id, 1)
    assert.equal(session.progress.value.current, 1)
    assert.equal(session.progress.value.total, 2)
    assert.equal(session.progress.value.percent, 50)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('useReviewSession: revela resposta e submete avaliações com avanço de índice', async () => {
  const originalFetch = globalThis.fetch
  const mockItems = createSampleItems(2)
  const recordedRatings = []

  globalThis.fetch = async (url, options) => {
    if (String(url).includes('/record')) {
      const body = JSON.parse(options.body)
      recordedRatings.push(body.rating)
      return {
        ok: true,
        status: 200,
        json: async () => ({
          id: 1,
          last_reviewed_at: new Date().toISOString(),
          review_count: 1,
          last_rating: body.rating,
        }),
      }
    }
    return {
      ok: true,
      status: 200,
      json: async () => mockItems,
    }
  }

  try {
    const session = useReviewSession()
    await session.loadItems()

    // 1. Revelar resposta
    assert.equal(session.state.isRevealed, false)
    session.revealAnswer()
    assert.equal(session.state.isRevealed, true)

    // 2. Submeter Fácil
    await session.submitRating('easy')
    assert.equal(recordedRatings[0], 'easy')
    assert.equal(session.state.currentIndex, 1)
    assert.equal(session.state.isRevealed, false)
    assert.equal(session.state.isCompleted, false)
    assert.equal(session.currentItem.value?.id, 2)

    // 3. Revelar e submeter Difícil no segundo e último item
    session.revealAnswer()
    await session.submitRating('hard')
    assert.equal(recordedRatings[1], 'hard')
    assert.equal(session.state.isCompleted, true)

    // 4. Checar sumário de retenção da sessão
    assert.equal(session.summary.value.easy, 1)
    assert.equal(session.summary.value.hard, 1)
    assert.equal(session.summary.value.medium, 0)
    assert.equal(session.summary.value.total, 2)
  } finally {
    globalThis.fetch = originalFetch
  }
})
