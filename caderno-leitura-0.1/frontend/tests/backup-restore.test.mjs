import test from 'node:test'
import assert from 'node:assert/strict'
import { downloadBackupBundle, restoreBackupPackage } from '../src/services/api.ts'

test('downloadBackupBundle solicita /api/backup/bundle com headers corretos e retorna blob', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedHeaders = {}

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedHeaders = options?.headers ?? {}
    return {
      ok: true,
      headers: new Headers({
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename="caderno-backup-20260919-120000.zip"',
      }),
      blob: async () => new Blob(['fake zip content'], { type: 'application/zip' }),
    }
  }

  try {
    const result = await downloadBackupBundle()
    assert.equal(requestedUrl, '/api/backup/bundle')
    assert.equal(requestedHeaders['Accept'], 'application/zip')
    assert.equal(result.filename, 'caderno-backup-20260919-120000.zip')
    assert.ok(result.blob)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('downloadBackupBundle propaga mensagem de erro da API em caso de falha HTTP', async () => {
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () => ({
    ok: false,
    status: 503,
    json: async () => ({ detail: 'O banco está ocupado. Tente novamente em alguns segundos.' }),
  })

  try {
    await assert.rejects(
      async () => downloadBackupBundle(),
      /O banco está ocupado/
    )
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('restoreBackupPackage envia arquivo via POST /api/backup/restore e retorna resultado', async () => {
  const originalFetch = globalThis.fetch
  let requestedUrl = ''
  let requestedMethod = ''
  let sentBody = null

  const mockResponse = {
    success: true,
    message: 'Acervo restaurado com sucesso!',
    pre_restore_snapshot: 'caderno-pre-restauracao-20260919-120000.db',
    schema_revision: '0005_trash_and_covers',
    counts: { books: 5, chapters: 10, studies: 25 },
    covers_restored: 1,
  }

  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url)
    requestedMethod = options?.method ?? 'GET'
    sentBody = options?.body
    return {
      ok: true,
      json: async () => mockResponse,
    }
  }

  try {
    const fakeFile = new File(['dummy backup'], 'backup.zip', { type: 'application/zip' })
    const result = await restoreBackupPackage(fakeFile)

    assert.equal(requestedUrl, '/api/backup/restore')
    assert.equal(requestedMethod, 'POST')
    assert.ok(sentBody instanceof FormData)
    assert.equal(result.success, true)
    assert.equal(result.counts.books, 5)
    assert.equal(result.covers_restored, 1)
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('restoreBackupPackage rejeita com mensagem clara se arquivo for inválido (400)', async () => {
  const originalFetch = globalThis.fetch

  globalThis.fetch = async () => ({
    ok: false,
    status: 400,
    json: async () => ({ detail: 'Tentativa de escape de diretório (Zip Slip) detectada.' }),
  })

  try {
    const fakeFile = new File(['malicious'], 'hack.zip')
    await assert.rejects(
      async () => restoreBackupPackage(fakeFile),
      /Zip Slip/
    )
  } finally {
    globalThis.fetch = originalFetch
  }
})
