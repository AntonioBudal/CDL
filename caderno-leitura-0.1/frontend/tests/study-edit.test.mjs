import test from 'node:test'
import assert from 'node:assert/strict'
import { useStudyEdit } from '../src/composables/useStudyEdit.ts'
import { useImportDraft } from '../src/composables/useImportDraft.ts'
import { api, ApiError } from '../src/services/api.ts'

const original = {
  id: 7, chapter_id: 2, title: 'A leitura atenta', location: 'p. 20–22',
  source_response: '## Resumo\r\nTexto **original**.\r\n',
  summary: 'Texto **original**.\r\n', explanation: 'Explicação.', concepts: '- Atenção',
  references: '', notes: 'Minha interpretação.\nOutra linha.',
  created_at: '2026-09-08T12:00:00Z', updated_at: '2026-09-08T12:00:00Z',
}
function makeEditor(gateway = {}) {
  const editor = useStudyEdit({ updateStudy: async (id, patch) => ({ ...original, ...patch }), ...gateway })
  editor.load(original)
  return editor
}

test('edição de uma seção envia apenas a alteração e preserva origem, outras seções e notas', async () => {
  let sent
  const editor = makeEditor({ updateStudy: async (id, patch) => { sent = { id, patch }; return { ...original, ...patch } } })
  assert.equal(editor.dirty.value, false)
  editor.state.sections.explanation = '**Explicação revisada.**\n\nOutro parágrafo.'
  assert.equal(editor.dirty.value, true)
  const saved = await editor.save()
  assert.deepEqual(sent, { id: 7, patch: { explanation: '**Explicação revisada.**\n\nOutro parágrafo.' } })
  assert.equal(saved.source_response, original.source_response)
  assert.equal(saved.summary, original.summary)
  assert.equal(saved.concepts, original.concepts)
  assert.equal(saved.notes, original.notes)
  assert.equal(editor.dirty.value, false)
})

test('limpar notas e referências é uma alteração explícita; metadados também são editáveis', async () => {
  let sent
  const editor = makeEditor({ updateStudy: async (_, patch) => { sent = patch; return { ...original, ...patch } } })
  editor.state.notes = ''
  editor.state.sections.concepts = ''
  editor.state.title = '  Novo título  '
  editor.state.location = 'Loc. 320'
  await editor.save()
  assert.deepEqual(sent, { title: 'Novo título', location: 'Loc. 320', notes: '', concepts: '' })
})

test('sem alterações ou ao desfazer a edição, nenhum PATCH é enviado', async () => {
  let calls = 0
  const editor = makeEditor({ updateStudy: async () => { calls++; return original } })
  assert.equal(await editor.save(), null)
  editor.state.notes = 'Mudança'
  assert.equal(editor.dirty.value, true)
  editor.state.notes = original.notes
  assert.equal(editor.dirty.value, false)
  assert.equal(await editor.save(), null)
  assert.equal(calls, 0)
})

test('título vazio e quatro seções vazias bloqueiam o salvamento sem apagar o rascunho', async () => {
  let calls = 0
  const editor = makeEditor({ updateStudy: async () => { calls++; return original } })
  editor.state.title = '  '
  assert.equal(await editor.save(), null)
  editor.state.title = original.title
  editor.state.sections = { summary: '', explanation: '  ', concepts: '', references: '' }
  editor.state.notes = 'Anotações não substituem a análise.'
  assert.equal(await editor.save(), null)
  assert.equal(calls, 0)
  assert.equal(editor.dirty.value, true)
  assert.equal(editor.state.notes, 'Anotações não substituem a análise.')
})

test('falha de comunicação conserva todos os campos e permite nova tentativa explícita', async () => {
  let calls = 0
  const editor = makeEditor({ updateStudy: async (_, patch) => {
    if (++calls === 1) throw new ApiError('Sem conexão.', 0)
    return { ...original, ...patch }
  } })
  editor.state.notes = 'Anotação que precisa permanecer.'
  editor.state.sections.references = '[Fonte](https://example.org)'
  assert.equal(await editor.save(), null)
  assert.equal(calls, 1)
  assert.equal(editor.dirty.value, true)
  assert.equal(editor.state.notes, 'Anotação que precisa permanecer.')
  assert.match(editor.state.error, /não foi possível confirmar/i)
  assert.equal((await editor.save()).references, '[Fonte](https://example.org)')
  assert.equal(calls, 2)
  assert.equal(editor.dirty.value, false)
})

test('envios simultâneos fazem um único PATCH e só limpam a pendência após a resposta', async () => {
  let resolve
  const pending = new Promise(done => { resolve = done })
  let calls = 0
  const editor = makeEditor({ updateStudy: async (_, patch) => { calls++; await pending; return { ...original, ...patch } } })
  editor.state.sections.summary = 'Novo resumo'
  const first = editor.save()
  assert.equal(editor.state.saving, true)
  assert.equal(editor.dirty.value, true)
  assert.equal(await editor.save(), null)
  resolve()
  await first
  assert.equal(calls, 1)
  assert.equal(editor.state.saving, false)
  assert.equal(editor.dirty.value, false)
})

test('importação passa a ter pendência com texto e deixa de ter pendência após salvar', async () => {
  const preview = { ...original, unassigned_text: '', warnings: [] }
  const draft = useImportDraft({ preview: async () => preview, createStudy: async () => original })
  draft.state.bookId = '1'; draft.state.chapterId = '2'
  assert.equal(draft.dirty.value, false)
  draft.state.sourceResponse = original.source_response
  assert.equal(draft.dirty.value, true)
  await draft.prepare()
  assert.equal(draft.dirty.value, true)
  await draft.save()
  assert.equal(draft.dirty.value, false)
})

test('cliente usa GET e PATCH no estudo correto, sem substituir campos não enviados', async t => {
  const calls = []
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    calls.push({ url, options })
    return new Response(JSON.stringify(original), { status: 200 })
  })
  const controller = new AbortController()
  await api.getStudy(7, controller.signal)
  await api.updateStudy(7, { notes: '' })
  assert.equal(calls[0].url, '/api/studies/7')
  assert.equal(calls[0].options.signal, controller.signal)
  assert.equal(calls[1].url, '/api/studies/7')
  assert.equal(calls[1].options.method, 'PATCH')
  assert.deepEqual(JSON.parse(calls[1].options.body), { notes: '' })
})
