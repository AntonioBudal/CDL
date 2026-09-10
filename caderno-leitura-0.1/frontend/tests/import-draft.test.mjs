import test from 'node:test'
import assert from 'node:assert/strict'
import { useImportDraft } from '../src/composables/useImportDraft.ts'
import { ApiError, api } from '../src/services/api.ts'

const source = '## Resumo\r\nResumo original.\r\n## Referências\r\nNenhuma fonte externa.\r\n'
const preview = (text = source) => ({
  source_response: text, summary: 'Resumo original.\r\n', explanation: '', concepts: '',
  references: 'Nenhuma fonte externa.\r\n', unassigned_text: '',
  warnings: [{ code: 'missing_section', message: 'Seção ausente.', section: 'explanation', line: null }],
})
const saved = payload => ({ ...payload, id: 12, title: payload.title || 'Capítulo 1', created_at: '2026-09-08T12:00:00Z', updated_at: '2026-09-08T12:00:00Z' })
function deferred() {
  let resolve
  const promise = new Promise(done => { resolve = done })
  return { promise, resolve }
}
function makeDraft(gateway = {}) {
  const draft = useImportDraft({ preview: async text => preview(text), createStudy: async payload => saved(payload), ...gateway })
  Object.assign(draft.state, { bookId: '2', chapterId: '7', sourceResponse: source, location: 'p. 32–34', notes: 'Minha interpretação.' })
  return draft
}

test('salva as correções, as anotações e a origem literal sem reprocessar a prévia', async () => {
  let parseCalls = 0
  let payload
  const draft = makeDraft({
    preview: async text => { parseCalls++; return preview(text) },
    createStudy: async value => { payload = value; return saved(value) },
  })
  assert.equal(await draft.prepare(), true)
  draft.state.sections.summary = '  Resumo revisado.\nOutra linha.  '
  draft.state.sections.explanation = 'Interpretação corrigida.'
  assert.equal(draft.hasManualChanges.value, true)
  const result = await draft.save()
  assert.equal(parseCalls, 1)
  assert.deepEqual(payload, {
    chapter_id: 7, title: null, location: 'p. 32–34', source_response: source,
    summary: '  Resumo revisado.\nOutra linha.  ', explanation: 'Interpretação corrigida.',
    concepts: '', references: 'Nenhuma fonte externa.\r\n', notes: 'Minha interpretação.',
  })
  assert.equal(result.id, 12)
  assert.equal(draft.state.saved.source_response, source)
})

test('dois envios simultâneos e um novo clique após sucesso criam uma única requisição', async () => {
  const pending = deferred()
  let writes = 0
  const draft = makeDraft({ createStudy: async payload => { writes++; await pending.promise; return saved(payload) } })
  await draft.prepare()
  const first = draft.save()
  assert.equal(draft.state.saving, true)
  assert.equal(draft.state.saved, null)
  assert.equal(await draft.save(), null)
  assert.equal(await draft.prepare(), false)
  draft.reset()
  assert.equal(draft.state.sourceResponse, source)
  pending.resolve()
  await first
  assert.equal(await draft.save(), null)
  assert.equal(writes, 1)
  assert.equal(draft.state.saving, false)
})

test('falha ao salvar preserva o formulário e só tenta novamente por ação explícita', async () => {
  let writes = 0
  const draft = makeDraft({ createStudy: async payload => {
    writes++
    if (writes === 1) throw new ApiError('Banco indisponível.', 503)
    return saved(payload)
  } })
  await draft.prepare()
  draft.state.sections.explanation = 'Correção que não pode sumir.'
  const before = JSON.stringify({ source: draft.state.sourceResponse, sections: draft.state.sections, notes: draft.state.notes, location: draft.state.location })
  assert.equal(await draft.save(), null)
  assert.equal(writes, 1)
  assert.equal(draft.state.saveError, 'Banco indisponível.')
  assert.equal(draft.state.saved, null)
  assert.equal(draft.canSave.value, true)
  assert.equal(JSON.stringify({ source: draft.state.sourceResponse, sections: draft.state.sections, notes: draft.state.notes, location: draft.state.location }), before)
  assert.equal((await draft.save()).explanation, 'Correção que não pode sumir.')
})

test('falha ao refazer a prévia não apaga correções; origem alterada bloqueia o salvamento', async () => {
  let previews = 0
  let writes = 0
  const draft = makeDraft({
    preview: async text => { if (++previews === 2) throw new Error('Sem conexão.'); return preview(text) },
    createStudy: async payload => { writes++; return saved(payload) },
  })
  await draft.prepare()
  draft.state.sections.summary = 'Resumo corrigido.'
  draft.state.sourceResponse = '## Resumo\nNova resposta.'
  assert.equal(await draft.prepare(), false)
  assert.equal(draft.state.previewError, 'Sem conexão.')
  assert.equal(draft.state.sections.summary, 'Resumo corrigido.')
  assert.equal(draft.state.notes, 'Minha interpretação.')
  assert.equal(draft.stale.value, true)
  assert.equal(await draft.save(), null)
  assert.equal(writes, 0)
})

test('resultado atrasado da preparação não substitui um texto modificado', async () => {
  const pending = deferred()
  const draft = makeDraft({ preview: async () => pending.promise })
  const preparing = draft.prepare()
  draft.state.sourceResponse = 'Texto novo.'
  pending.resolve(preview())
  assert.equal(await preparing, false)
  assert.equal(draft.state.preview, null)
  assert.equal(draft.state.sourceResponse, 'Texto novo.')
  assert.equal(draft.state.preparing, false)
})

test('texto sem títulos pode ser distribuído manualmente e uma seção preenchida basta', async () => {
  let sent
  const text = 'Introdução inteira sem títulos.'
  const draft = makeDraft({
    preview: async () => ({ ...preview(text), summary: '', references: '', unassigned_text: text }),
    createStudy: async payload => { sent = payload; return saved(payload) },
  })
  draft.state.sourceResponse = text
  await draft.prepare()
  assert.equal(draft.canSave.value, false)
  assert.equal(await draft.save(), null)
  draft.state.sections.explanation = draft.state.preview.unassigned_text
  assert.equal(draft.canSave.value, true)
  await draft.save()
  assert.equal(sent.explanation, text)
  assert.equal(sent.source_response, text)
  assert.equal(sent.concepts, '')
  assert.equal('unassigned_text' in sent, false)
  assert.equal('warnings' in sent, false)
})

test('começar outro estudo limpa a análise e mantém apenas o livro e o capítulo', async () => {
  const draft = makeDraft()
  await draft.prepare()
  await draft.save()
  draft.reset()
  assert.equal(draft.state.saved, null)
  assert.equal(draft.state.preview, null)
  assert.equal(draft.state.sourceResponse, '')
  assert.equal(draft.state.notes, '')
  assert.equal(draft.state.location, '')
  assert.equal(draft.state.bookId, '2')
  assert.equal(draft.state.chapterId, '7')
})

test('cliente HTTP envia a origem no contrato da prévia e trata erro de validação', async t => {
  let call
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    call = { url, options }
    return new Response(JSON.stringify(preview()), { status: 200, headers: { 'Content-Type': 'application/json' } })
  })
  const result = await api.preview(source)
  assert.equal(result.source_response, source)
  assert.equal(call.url, '/api/imports/preview')
  assert.equal(call.options.method, 'POST')
  assert.deepEqual(JSON.parse(call.options.body), { source_response: source })
  globalThis.fetch.mock.mockImplementation(async () => new Response(JSON.stringify({ detail: [{ loc: ['body'], msg: 'invalid' }] }), { status: 422 }))
  await assert.rejects(api.createBook('', ''), error => error instanceof ApiError && error.status === 422)
})

test('falha de comunicação não é anunciada como sucesso nem causa reenvio automático', async () => {
  let calls = 0
  const draft = makeDraft({ createStudy: async () => { calls++; throw new ApiError('Conexão perdida.', 0) } })
  await draft.prepare()
  assert.equal(await draft.save(), null)
  assert.equal(calls, 1)
  assert.equal(draft.state.saved, null)
  assert.match(draft.state.saveError, /não foi possível confirmar/i)
  assert.equal(draft.state.sourceResponse, source)
})
