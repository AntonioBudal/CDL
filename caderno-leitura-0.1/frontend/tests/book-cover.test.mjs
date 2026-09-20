import test from 'node:test'
import assert from 'node:assert/strict'
import { api } from '../src/services/api.ts'

test('cliente HTTP envia uploadBookCover com FormData para a rota do livro', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedMethod = ''
  let requestedBody = null

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedMethod = options.method
    requestedBody = options.body
    return {
      ok: true,
      status: 200,
      json: async () => ({
        book_id: 1,
        cover_image: 'abc12345.webp',
        cover_url: '/api/covers/abc12345.webp',
        message: 'Capa atualizada com sucesso.',
      }),
    }
  }

  try {
    const fakeFile = new Blob(['synthetic image content'], { type: 'image/jpeg' })
    const result = await api.uploadBookCover(1, fakeFile)

    assert.equal(requestedUrl, '/api/books/1/cover')
    assert.equal(requestedMethod, 'POST')
    assert.ok(requestedBody instanceof FormData)
    assert.equal(result.book_id, 1)
    assert.equal(result.cover_image, 'abc12345.webp')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('cliente HTTP envia importBookCoverFromUrl com JSON contendo a URL informada', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedMethod = ''
  let requestedBody = ''

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedMethod = options.method
    requestedBody = String(options.body)
    return {
      ok: true,
      status: 200,
      json: async () => ({
        book_id: 2,
        cover_image: 'urlcover.webp',
        cover_url: '/api/covers/urlcover.webp',
        message: 'Capa importada com sucesso.',
      }),
    }
  }

  try {
    const result = await api.importBookCoverFromUrl(2, 'https://example.com/cover.jpg')

    assert.equal(requestedUrl, '/api/books/2/cover/url')
    assert.equal(requestedMethod, 'POST')
    assert.deepEqual(JSON.parse(requestedBody), { url: 'https://example.com/cover.jpg' })
    assert.equal(result.cover_image, 'urlcover.webp')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('cliente HTTP envia removeBookCover via DELETE e desassocia a capa', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedMethod = ''

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedMethod = options.method
    return {
      ok: true,
      status: 200,
      json: async () => ({
        book_id: 3,
        cover_image: null,
        cover_url: null,
        message: 'Capa removida com sucesso.',
      }),
    }
  }

  try {
    const result = await api.removeBookCover(3)

    assert.equal(requestedUrl, '/api/books/3/cover')
    assert.equal(requestedMethod, 'DELETE')
    assert.equal(result.cover_image, null)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('geração de tom determinístico de cor e iniciais a partir do título', () => {
  function getTitleHue(text) {
    let hash = 0
    for (let i = 0; i < text.length; i++) {
      hash = (hash << 5) - hash + text.charCodeAt(i)
      hash |= 0
    }
    return Math.abs(hash) % 360
  }

  function getInitials(title) {
    if (!title) return '📖'
    const words = title.trim().split(/\s+/).filter(Boolean)
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase()
    return (words[0][0] + words[1][0]).toUpperCase()
  }

  // Mesmo título sempre produz o mesmo tom
  assert.equal(getTitleHue('Guerra e Paz'), getTitleHue('Guerra e Paz'))
  assert.ok(getTitleHue('Guerra e Paz') >= 0 && getTitleHue('Guerra e Paz') < 360)

  // Iniciais corretas
  assert.equal(getInitials('Guerra e Paz'), 'GE')
  assert.equal(getInitials('Odisseia'), 'OD')
  assert.equal(getInitials(''), '📖')
})
