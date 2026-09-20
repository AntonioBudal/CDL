import test from 'node:test'
import assert from 'node:assert/strict'
import { api } from '../src/services/api.ts'

test('cliente HTTP envia getDashboard com parâmetros de consulta corretos', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedMethod = ''

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedMethod = options?.method || 'GET'
    return {
      ok: true,
      status: 200,
      json: async () => ({
        summary: {
          total_books: 5,
          total_studies: 15,
          total_reading_days: 10,
          current_streak: 3,
          avg_studies_per_book: 3.0,
        },
        heatmap: [
          { date: '2026-09-19', count: 4, level: 3 },
        ],
        timeline: [
          {
            id: 'study-1-created',
            entity_type: 'study',
            action: 'study_created',
            timestamp: '2026-09-19T10:00:00Z',
            title: 'Estudo 1',
            book_id: 1,
            book_title: 'Livro 1',
            chapter_id: 1,
            chapter_title: 'Capítulo 1',
            study_id: 1,
          },
        ],
      }),
    }
  }

  try {
    const result = await api.getDashboard({
      tz_offset: -180,
      days: 365,
      date: '2026-09-19',
      limit: 20,
    })

    assert.equal(requestedMethod, 'GET')
    assert.ok(requestedUrl.startsWith('/api/dashboard?'))
    assert.ok(requestedUrl.includes('tz_offset=-180'))
    assert.ok(requestedUrl.includes('days=365'))
    assert.ok(requestedUrl.includes('date=2026-09-19'))
    assert.ok(requestedUrl.includes('limit=20'))

    assert.equal(result.summary.total_books, 5)
    assert.equal(result.summary.total_studies, 15)
    assert.equal(result.summary.current_streak, 3)
    assert.equal(result.heatmap.length, 1)
    assert.equal(result.heatmap[0].level, 3)
    assert.equal(result.timeline.length, 1)
    assert.equal(result.timeline[0].action, 'study_created')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('cliente HTTP executa getDashboard sem parâmetros opcionais', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''

  globalThis.fetch = async (url) => {
    requestedUrl = String(url)
    return {
      ok: true,
      status: 200,
      json: async () => ({
        summary: {
          total_books: 0,
          total_studies: 0,
          total_reading_days: 0,
          current_streak: 0,
          avg_studies_per_book: 0.0,
        },
        heatmap: [],
        timeline: [],
      }),
    }
  }

  try {
    const result = await api.getDashboard()
    assert.equal(requestedUrl, '/api/dashboard')
    assert.equal(result.summary.total_books, 0)
    assert.equal(result.heatmap.length, 0)
    assert.equal(result.timeline.length, 0)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('cálculo dos níveis de intensidade do heatmap', () => {
  function getLevel(count) {
    if (count === 0) return 0
    if (count === 1) return 1
    if (count <= 3) return 2
    return 3
  }

  assert.equal(getLevel(0), 0)
  assert.equal(getLevel(1), 1)
  assert.equal(getLevel(2), 2)
  assert.equal(getLevel(3), 2)
  assert.equal(getLevel(4), 3)
  assert.equal(getLevel(10), 3)
})

test('cálculo da média de estudos por livro', () => {
  function calcAvg(totalStudies, totalBooks) {
    if (totalBooks === 0) return 0.0
    return Math.round((totalStudies / totalBooks) * 10) / 10
  }

  assert.equal(calcAvg(0, 0), 0.0)
  assert.equal(calcAvg(5, 2), 2.5)
  assert.equal(calcAvg(10, 3), 3.3)
})
