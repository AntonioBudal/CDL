import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { useSectionOrganizer } from '../src/composables/useSectionOrganizer.ts'
import { useDigitizeDraft } from '../src/composables/useDigitizeDraft.ts'
import { useImportDraft } from '../src/composables/useImportDraft.ts'
import { ApiError } from '../src/services/api.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = relative => fs.readFileSync(path.resolve(srcDir, relative), 'utf-8')
const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

// Textos fictícios: a "resposta" imita o contrato de /api/imports/organize.
const TEXT = 'O capítulo trata de um tema de teste.\nTermo de teste: definição fictícia.\nIsso importa porque é um teste.\nSOBRENOME, Nome. Livro de Teste. 2020.'
const PIECES = TEXT.split('\n')
const result = (sections = ['summary', 'concepts', 'explanation', 'references'], review = [false, true, true, false]) => {
  let start = 0
  const segments = PIECES.map((text, index) => {
    const seg = { index, start, end: start + text.length, text, section: sections[index], confidence: 0.8, review: review[index] }
    start += text.length + 1
    return seg
  })
  const by = key => segments.filter(s => s.section === key).map(s => s.text).join('\n')
  return {
    sections: { summary: by('summary'), explanation: by('explanation'), concepts: by('concepts'), references: by('references') },
    segments, explicit_headings: false, review_count: review.filter(Boolean).length,
    engine: { name: 'leitorum-organizer', version: '1', sha256: 'x' }, elapsed_ms: 1,
    warnings: [{ code: 'suggestion', message: 'Distribuição automática: confira as seções antes de salvar.' }],
  }
}
function deferred() {
  let resolve
  const promise = new Promise(done => { resolve = done })
  return { promise, resolve }
}

// --- useSectionOrganizer -------------------------------------------------------------------

test('organizar monta as 4 seções iguais às da resposta e guarda o texto de antes', async () => {
  let sent
  const org = useSectionOrganizer({ organize: async payload => { sent = payload; return result() } })
  const lines = [{ text: PIECES[0], bbox: [1, 2, 3, 4], confidence: 0.9 }]
  assert.equal(await org.organize(TEXT, lines), true)
  assert.deepEqual(sent, { text: TEXT, lines })
  assert.equal(org.state.active, true)
  assert.deepEqual({ ...org.state.sections }, result().sections)
  assert.equal(org.state.snapshot, TEXT)
  assert.equal(org.edited.value, false)
  assert.deepEqual(org.reviewItems.value.map(i => [i.index, i.section, i.movable]), [[1, 'concepts', true], [2, 'explanation', true]])
  assert.deepEqual({ ...org.reviewCounts.value }, { summary: 0, explanation: 1, concepts: 1, references: 0 })
})

test('sem linhas, o pedido leva só o texto; texto vazio não chama a API', async () => {
  let calls = 0
  let sent
  const org = useSectionOrganizer({ organize: async payload => { calls++; sent = payload; return result() } })
  assert.equal(await org.organize('  \n '), false)
  assert.equal(org.state.error.code, 'empty_text')
  await org.organize(TEXT, [])
  assert.deepEqual(sent, { text: TEXT })
  assert.equal(calls, 1)
})

test('mover com editores intactos remonta origem e destino na ordem original', async () => {
  const org = useSectionOrganizer({ organize: async () => result() })
  await org.organize(TEXT)
  assert.equal(org.move(2, 'summary'), true)
  assert.equal(org.state.sections.summary, `${PIECES[0]}\n${PIECES[2]}`)
  assert.equal(org.state.sections.explanation, '')
  assert.equal(org.edited.value, false)
  assert.equal(org.move(1, 'summary'), true)
  assert.equal(org.state.sections.summary, PIECES.slice(0, 3).join('\n'), 'mantém a ordem original do texto')
})

test('mover com a origem editada tira o trecho como substring; destino editado recebe no fim', async () => {
  const org = useSectionOrganizer({ organize: async () => result() })
  await org.organize(TEXT)
  org.state.sections.concepts = `Nota do leitor.\n${PIECES[1]}`
  org.state.sections.summary = `${PIECES[0]} (revisado)`
  assert.equal(org.move(1, 'summary'), true)
  assert.equal(org.state.sections.concepts, 'Nota do leitor.')
  assert.equal(org.state.sections.summary, `${PIECES[0]} (revisado)\n${PIECES[1]}`)
  assert.equal(org.edited.value, true)
})

test('trecho editado aparece como "já editado" e não se move', async () => {
  const org = useSectionOrganizer({ organize: async () => result() })
  await org.organize(TEXT)
  org.state.sections.explanation = 'Explicação reescrita pelo leitor.'
  const item = org.reviewItems.value.find(i => i.index === 2)
  assert.equal(item.movable, false)
  assert.equal(org.move(2, 'concepts'), false)
  assert.equal(org.state.sections.explanation, 'Explicação reescrita pelo leitor.')
})

test('voltar devolve o texto exato de antes e sai do modo organizado', async () => {
  const org = useSectionOrganizer({ organize: async () => result() })
  await org.organize(TEXT)
  org.state.sections.summary = 'alterado'
  assert.equal(org.revert(), TEXT)
  assert.equal(org.state.active, false)
  assert.deepEqual({ ...org.state.sections }, { summary: '', explanation: '', concepts: '', references: '' })
})

test('erro da API vira mensagem e não liga o modo organizado', async () => {
  const org = useSectionOrganizer({
    organize: async () => { throw new ApiError('A organização automática não está disponível nesta instalação.', 503, { code: 'unavailable', detail: 'x' }) },
  })
  assert.equal(await org.organize(TEXT), false)
  assert.equal(org.state.active, false)
  assert.deepEqual(org.state.error, { code: 'unavailable', message: 'A organização automática não está disponível nesta instalação.' })
})

test('segundo pedido durante o primeiro é ignorado; cancelar descarta a resposta tardia', async () => {
  const pending = deferred()
  let calls = 0
  let signal
  const org = useSectionOrganizer({ organize: async (_p, s) => { calls++; signal = s; return pending.promise } })
  const first = org.organize(TEXT)
  assert.equal(await org.organize(TEXT), false)
  assert.equal(calls, 1)
  org.cancel()
  assert.equal(signal.aborted, true)
  pending.resolve(result())
  assert.equal(await first, false)
  assert.equal(org.state.active, false)
  assert.equal(org.state.loading, false)
})

// --- Digitalização ---------------------------------------------------------------------------

const preview = () => ({
  text: TEXT,
  lines: PIECES.map((text, index) => ({ index, text, confidence: 0.9, low_confidence: false, bbox: [0, index * 80, 900, index * 80 + 60] })),
  low_confidence_count: 0, warnings: [], engine: { name: 'leitorum-motor', version: '0', reader: 'Leitor de Teste', license_status: 'VERIFIED' }, elapsed_ms: 1,
})
const saved = payload => ({ ...payload, id: 9, reading_status: 'rascunho' })
async function digitizeDraft(overrides = {}) {
  const calls = { organize: [], create: [] }
  const draft = useDigitizeDraft(
    {
      status: async () => ({ available: true, reason: null }),
      preview: async () => preview(),
      createStudy: async payload => { calls.create.push(payload); return saved(payload) },
      organize: async payload => { calls.organize.push(payload); return result() },
      ...overrides,
    },
    { createObjectURL: () => 'blob:teste', revokeObjectURL: () => {}, today: () => new Date(2026, 9, 27) },
  )
  await draft.checkStatus()
  await draft.choose(new File([new Uint8Array(4)], 'pagina.jpg', { type: 'image/jpeg' }))
  Object.assign(draft.state, { bookId: '2', chapterId: '7' })
  return { draft, calls }
}

test('digitalização: organizar manda as linhas com caixa e salvar envia as 4 seções', async () => {
  const { draft, calls } = await digitizeDraft()
  assert.equal(await draft.organize(), true)
  assert.equal(calls.organize[0].lines.length, 4)
  assert.deepEqual(calls.organize[0].lines[1], { text: PIECES[1], bbox: [0, 80, 900, 140], confidence: 0.9 })
  assert.equal(draft.dirty.value, true)
  await draft.save()
  const payload = calls.create[0]
  assert.equal(payload.source_response, TEXT, 'registro de origem é a leitura bruta')
  assert.deepEqual([payload.summary, payload.explanation, payload.concepts, payload.references], [PIECES[0], PIECES[2], PIECES[1], PIECES[3]])
})

test('digitalização: 4 seções vazias bloqueiam o salvamento; voltar restaura o texto único', async () => {
  const { draft } = await digitizeDraft()
  draft.state.text = `${TEXT}\nlinha editada antes de organizar`
  const before = draft.state.text
  await draft.organize()
  for (const key of ['summary', 'explanation', 'concepts', 'references']) draft.organizer.state.sections[key] = ' '
  assert.equal(draft.canSave.value, false)
  draft.unorganize()
  assert.equal(draft.state.text, before)
  assert.equal(draft.canSave.value, true)
})

test('digitalização: nova página desliga o modo organizado', async () => {
  const { draft } = await digitizeDraft()
  await draft.organize()
  draft.reset()
  assert.equal(draft.organizer.state.active, false)
})

// --- Importação ------------------------------------------------------------------------------

function importDraft(organizeText) {
  const draft = useImportDraft({
    preview: async text => ({ source_response: text, summary: 'Resumo já existente.', explanation: '', concepts: '', references: '', unassigned_text: TEXT, warnings: [] }),
    createStudy: async payload => saved(payload),
    organizeText,
  })
  Object.assign(draft.state, { bookId: '2', chapterId: '7', sourceResponse: 'fichamento de teste' })
  return draft
}

test('importação: organizar acrescenta às seções, esvazia o não classificado e desfazer restaura', async () => {
  let sent
  const draft = importDraft(async payload => { sent = payload; return result() })
  await draft.prepare()
  const before = { ...draft.state.sections }
  assert.equal(await draft.organizeUnassigned(), true)
  assert.deepEqual(sent, { text: TEXT })
  assert.equal(draft.state.sections.summary, `Resumo já existente.\n\n${PIECES[0]}`)
  assert.equal(draft.state.sections.concepts, PIECES[1])
  assert.equal(draft.state.preview.unassigned_text, '')
  assert.ok(draft.state.organizeSnapshot)
  assert.equal(draft.undoOrganize(), true)
  assert.deepEqual({ ...draft.state.sections }, before)
  assert.equal(draft.state.preview.unassigned_text, TEXT)
  assert.equal(draft.state.organizeSnapshot, null)
})

test('importação: nova prévia descarta o desfazer; sem gateway ou sem texto não organiza', async () => {
  const draft = importDraft(async () => result())
  await draft.prepare()
  await draft.organizeUnassigned()
  await draft.prepare()
  assert.equal(draft.state.organizeSnapshot, null)
  const noGateway = importDraft(undefined)
  await noGateway.prepare()
  assert.equal(await noGateway.organizeUnassigned(), false)
})

test('importação: erro vira mensagem e nada muda', async () => {
  const draft = importDraft(async () => { throw new ApiError('Organização indisponível.', 503, { code: 'unavailable' }) })
  await draft.prepare()
  const before = { ...draft.state.sections }
  assert.equal(await draft.organizeUnassigned(), false)
  assert.equal(draft.state.organizeError, 'Organização indisponível.')
  assert.deepEqual({ ...draft.state.sections }, before)
  assert.equal(draft.state.preview.unassigned_text, TEXT)
})

// --- Telas e componente ----------------------------------------------------------------------

test('tela de digitalização: botão, aviso, conferência, mover e voltar', () => {
  const view = read('views/DigitizeNotebookView.vue')
  for (const piece of ['Organizar nas 4 seções', 'Distribuição automática.', 'Seções para conferir', 'Mover para…',
    'Voltar para texto único', 'já editado', 'organize: api.organizeText', 'getOrganizeStatus', 'OrganizedSectionsEditor',
    'Organização automática indisponível nesta instalação.', 'corrija o texto antes de organizar']) {
    assert.ok(view.includes(piece), piece)
  }
  assert.ok(view.includes('v-if="!organizer.state.active" class="section-choice"'), 'escolha de seção some no modo organizado')
  assert.ok(view.includes('v-else class="editor-column"'), 'linhas para conferir só no texto único')
  assert.ok(!emojiRegex.test(view))
})

test('importação: botão só com o organizador disponível e desfazer visível', () => {
  const view = read('views/ImportView.vue')
  assert.ok(view.includes('v-if="organizeAvailable" class="unassigned-organize"'))
  assert.ok(view.includes('Organizar automaticamente'))
  assert.ok(view.includes('Desfazer organização'))
  assert.ok(!emojiRegex.test(view))
})

test('editor das 4 seções: abas acessíveis no celular, tokens, foco e alvos de 44px', () => {
  const component = read('components/OrganizedSectionsEditor.vue')
  for (const piece of ['role="tablist"', 'role="tab"', ':aria-selected', 'tabpanel', "'(max-width: 767px)'", 'ArrowRight']) {
    assert.ok(component.includes(piece), piece)
  }
  const style = component.slice(component.indexOf('<style'))
  assert.ok(style.includes('min-height: 44px'))
  assert.ok(style.includes(':focus-visible'))
  assert.ok(style.includes('prefers-reduced-motion'))
  assert.ok(!/#[0-9a-fA-F]{3,8}\b/.test(style) && !/rgba?\(/.test(style), 'sem cores fixas')
  assert.ok(!emojiRegex.test(component))
  const view = read('views/DigitizeNotebookView.vue')
  const viewStyle = view.slice(view.indexOf('<style'))
  assert.ok(!/#[0-9a-fA-F]{3,8}\b/.test(viewStyle) && !/rgba?\(/.test(viewStyle))
})
