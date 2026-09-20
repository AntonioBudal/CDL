import test from 'node:test'
import assert from 'node:assert/strict'
import {
  api,
  buildExportQuery,
  downloadExportFile,
  getExportBookUrl,
  getExportStudyUrl,
} from '../src/services/api.ts'

test('buildExportQuery constrói query params corretos para markdown e opções padrão', () => {
  const config = {
    format: 'markdown',
    includeNotes: true,
    includeSections: true,
    includeSource: false,
    includeMetadata: true,
  }

  const qs = buildExportQuery(config)
  const params = new URLSearchParams(qs)

  assert.equal(params.get('format'), 'markdown')
  assert.equal(params.get('include_notes'), 'true')
  assert.equal(params.get('include_sections'), 'true')
  assert.equal(params.get('include_source'), 'false')
  assert.equal(params.get('include_metadata'), 'true')
})

test('buildExportQuery constrói query params corretos para text e opções personalizadas', () => {
  const config = {
    format: 'text',
    includeNotes: true,
    includeSections: false,
    includeSource: true,
    includeMetadata: false,
  }

  const qs = buildExportQuery(config)
  const params = new URLSearchParams(qs)

  assert.equal(params.get('format'), 'text')
  assert.equal(params.get('include_notes'), 'true')
  assert.equal(params.get('include_sections'), 'false')
  assert.equal(params.get('include_source'), 'true')
  assert.equal(params.get('include_metadata'), 'false')
})

test('getExportBookUrl gera o caminho REST correto com parâmetros', () => {
  const config = {
    format: 'markdown',
    includeNotes: true,
    includeSections: true,
    includeSource: false,
    includeMetadata: true,
  }

  const url = getExportBookUrl(42, config)
  assert.ok(url.startsWith('/api/books/42/export?'))
  assert.ok(url.includes('format=markdown'))
})

test('getExportStudyUrl gera o caminho REST correto com parâmetros', () => {
  const config = {
    format: 'text',
    includeNotes: true,
    includeSections: true,
    includeSource: false,
    includeMetadata: true,
  }

  const url = getExportStudyUrl(99, config)
  assert.ok(url.startsWith('/api/studies/99/export?'))
  assert.ok(url.includes('format=text'))
})

test('downloadExportFile extrai filename do Content-Disposition', async () => {
  const originalFetch = globalThis.fetch
  let fetchedUrl = ''

  globalThis.fetch = async (url) => {
    fetchedUrl = String(url)
    return {
      ok: true,
      status: 200,
      headers: {
        get: (name) => {
          if (name.toLowerCase() === 'content-disposition') {
            return 'attachment; filename="memorias-postumas.md"'
          }
          return null
        },
      },
      blob: async () => new Blob(['# Memórias Póstumas'], { type: 'text/markdown' }),
    }
  }

  try {
    const result = await downloadExportFile('/api/books/1/export', 'fallback.md')
    assert.equal(fetchedUrl, '/api/books/1/export')
    assert.equal(result.filename, 'memorias-postumas.md')
    assert.ok(result.blob)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('downloadExportFile usa defaultFilename se Content-Disposition ausente', async () => {
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    headers: {
      get: () => null,
    },
    blob: async () => new Blob(['texto puro'], { type: 'text/plain' }),
  })

  try {
    const result = await downloadExportFile('/api/studies/5/export', 'default-estudo.txt')
    assert.equal(result.filename, 'default-estudo.txt')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('downloadExportFile lança ApiError com mensagem do servidor em caso de erro HTTP', async () => {
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () => ({
    ok: false,
    status: 404,
    headers: {
      get: () => 'application/json',
    },
    json: async () => ({ detail: 'Livro não encontrado.' }),
  })

  try {
    await assert.rejects(
      async () => {
        await downloadExportFile('/api/books/999/export', 'livro.md')
      },
      (err) => {
        assert.equal(err.name, 'ApiError')
        assert.equal(err.status, 404)
        assert.equal(err.message, 'Livro não encontrado.')
        return true
      },
    )
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('api.exportBook e api.exportStudy chamam downloadExportFile corretamente', async () => {
  const originalFetch = globalThis.fetch
  const calls = []

  globalThis.fetch = async (url) => {
    calls.push(String(url))
    return {
      ok: true,
      status: 200,
      headers: {
        get: () => null,
      },
      blob: async () => new Blob(['content']),
    }
  }

  const config = {
    format: 'markdown',
    includeNotes: true,
    includeSections: true,
    includeSource: false,
    includeMetadata: true,
  }

  try {
    await api.exportBook(10, config)
    await api.exportStudy(25, config)

    assert.equal(calls.length, 2)
    assert.ok(calls[0].startsWith('/api/books/10/export?'))
    assert.ok(calls[1].startsWith('/api/studies/25/export?'))
  } finally {
    globalThis.fetch = originalFetch
  }
})
