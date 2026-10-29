import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { useDigitizeDraft } from '../src/composables/useDigitizeDraft.ts'
import { useImportDraft } from '../src/composables/useImportDraft.ts'

// Feature 091-B: registro silencioso do feedback do organizador. Textos fictícios; a "resposta" imita o contrato.
const srcDir = path.resolve(process.cwd(), 'src')
const read = relative => fs.readFileSync(path.resolve(srcDir, relative), 'utf-8')

const TEXT = 'O capítulo trata de um tema de teste.\nTermo de teste: definição fictícia.\nIsso importa porque é um teste.\n- Livro de Teste — Autora Fictícia'
const PIECES = TEXT.split('\n')
const ENGINE = { name: 'leitorum-organizer', version: '2', sha256: '9f6530a3' }
const result = (sections = ['summary', 'concepts', 'explanation', 'references']) => {
  let start = 0
  const segments = PIECES.map((text, index) => {
    const seg = { index, start, end: start + text.length, text, section: sections[index], confidence: 0.8, review: false }
    start += text.length + 1
    return seg
  })
  const by = key => segments.filter(s => s.section === key).map(s => s.text).join('\n')
  return {
    sections: { summary: by('summary'), explanation: by('explanation'), concepts: by('concepts'), references: by('references') },
    segments, explicit_headings: false, review_count: 0, engine: ENGINE, elapsed_ms: 1, warnings: [],
  }
}
const expectedSegments = () => result().segments.map(({ index, start, end, section, confidence, review }) => ({ index, start, end, section, confidence, review }))
const preview = () => ({
  text: TEXT,
  lines: PIECES.map((text, index) => ({ index, text, confidence: 0.9, low_confidence: false, bbox: [0, index * 80, 900, index * 80 + 60] })),
  low_confidence_count: 0, warnings: [], engine: { name: 'leitorum-motor', version: '0', reader: 'Leitor de Teste', license_status: 'VERIFIED' }, elapsed_ms: 1,
})
const flush = () => new Promise(done => setTimeout(done, 0))
const sentLines = () => PIECES.map((text, index) => ({ text, bbox: [0, index * 80, 900, index * 80 + 60], confidence: 0.9 }))

async function digitizeDraft(overrides = {}) {
  const sent = []
  const order = []
  const draft = useDigitizeDraft(
    {
      status: async () => ({ available: true, reason: null }),
      preview: async () => preview(),
      createStudy: async payload => { order.push('study'); return { ...payload, id: 41, reading_status: 'rascunho' } },
      organize: async () => result(),
      sendFeedback: async (studyId, payload) => { order.push('feedback'); sent.push([studyId, payload]) },
      ...overrides,
    },
    { createObjectURL: () => 'blob:teste', revokeObjectURL: () => {}, today: () => new Date(2026, 9, 28) },
  )
  await draft.checkStatus()
  await draft.choose(new File([new Uint8Array(4)], 'pagina.jpg', { type: 'image/jpeg' }))
  Object.assign(draft.state, { bookId: '2', chapterId: '7' })
  return { draft, sent, order }
}

test('digitalização organizada: depois do estudo, manda a sugestão como salva, com as linhas (091-C)', async () => {
  const { draft, sent, order } = await digitizeDraft()
  await draft.organize()
  draft.organizer.move(2, 'summary')
  await draft.save()
  await flush()
  assert.deepEqual(order, ['study', 'feedback'])
  assert.deepEqual(sent, [[41, {
    origin: 'digitize',
    organizer: {
      engine: { version: '2', sha256: '9f6530a3', adapter: null }, outcome: 'saved', text: TEXT, segments: expectedSegments(), lines: sentLines(),
    },
  }]])
})

test('o adaptador da resposta vai no registro (091-C); nada muda na tela', async () => {
  const { draft, sent } = await digitizeDraft({ organize: async () => ({ ...result(), engine: { ...ENGINE, adapter: 31 } }) })
  await draft.organize()
  const before = JSON.stringify(draft.organizer.state.sections)
  await draft.save()
  await flush()
  assert.equal(sent[0][1].organizer.engine.adapter, 31)
  assert.equal(JSON.stringify(draft.organizer.state.sections), before)
})

test('digitalização sem organizar: manda só a origem, para o diff da leitura', async () => {
  const { draft, sent } = await digitizeDraft()
  await draft.save()
  await flush()
  assert.deepEqual(sent, [[41, { origin: 'digitize', organizer: null }]])
})

test('voltar para o texto único: a sugestão vai como revertida', async () => {
  const { draft, sent } = await digitizeDraft()
  await draft.organize()
  draft.unorganize()
  await draft.save()
  await flush()
  assert.equal(sent[0][1].organizer.outcome, 'reverted')
  assert.deepEqual(sent[0][1].organizer.segments, expectedSegments())
})

test('nova organização depois de voltar substitui a revertida', async () => {
  const { draft, sent } = await digitizeDraft()
  await draft.organize()
  draft.unorganize()
  await draft.organize()
  await draft.save()
  await flush()
  assert.equal(sent[0][1].organizer.outcome, 'saved')
})

test('falha no envio do feedback não aparece e o estudo continua salvo', async () => {
  for (const sendFeedback of [async () => { throw new Error('rede fora') }, () => { throw new Error('síncrona') }]) {
    const { draft } = await digitizeDraft({ sendFeedback })
    await draft.organize()
    const saved = await draft.save()
    await flush()
    assert.equal(saved.id, 41)
    assert.equal(draft.state.phase, 'saved')
    assert.equal(draft.state.error, null)
  }
})

test('nada é enviado se o estudo não foi salvo', async () => {
  const { draft, sent } = await digitizeDraft({ createStudy: async () => { throw new Error('falha ao salvar') } })
  await draft.save()
  await flush()
  assert.deepEqual(sent, [])
  assert.equal(draft.state.phase, 'review')
})

function importDraft(organizeText) {
  const sent = []
  const draft = useImportDraft({
    preview: async text => ({ source_response: text, summary: 'Resumo já existente.', explanation: '', concepts: '', references: '', unassigned_text: TEXT, warnings: [] }),
    createStudy: async payload => ({ ...payload, id: 52, reading_status: 'rascunho' }),
    organizeText,
    sendOrganizerFeedback: async (studyId, payload) => { sent.push([studyId, payload]) },
  })
  Object.assign(draft.state, { bookId: '2', chapterId: '7', sourceResponse: 'fichamento de teste' })
  return { draft, sent }
}

test('importação organizada manda a sugestão; sem organizar, nada', async () => {
  const organized = importDraft(async () => result())
  await organized.draft.prepare()
  await organized.draft.organizeUnassigned()
  await organized.draft.save()
  await flush()
  assert.deepEqual(organized.sent, [[52, {
    origin: 'import',
    organizer: { engine: { version: '2', sha256: '9f6530a3', adapter: null }, outcome: 'saved', text: TEXT, segments: expectedSegments() },
  }]])

  const plain = importDraft(async () => result())
  await plain.draft.prepare()
  plain.draft.state.sections.summary = 'Resumo editado à mão.'
  await plain.draft.save()
  await flush()
  assert.deepEqual(plain.sent, [])
})

test('importação: desfazer a organização manda a sugestão como revertida', async () => {
  const { draft, sent } = importDraft(async () => result())
  await draft.prepare()
  await draft.organizeUnassigned()
  draft.undoOrganize()
  draft.assignUnassignedToSection('explanation')
  await draft.save()
  await flush()
  assert.equal(sent[0][1].organizer.outcome, 'reverted')
})

test('as telas passam o envio do feedback e a página Sobre explica o registro local', () => {
  assert.ok(read('views/DigitizeNotebookView.vue').includes('sendFeedback: api.sendOrganizerFeedback'))
  assert.ok(read('services/api.ts').includes('/organizer-feedback'))
  const about = read('views/AboutView.vue')
  assert.ok(about.includes('o Leitorum guarda localmente, junto do estudo, o que foi sugerido e o que você corrigiu'))
  assert.ok(about.includes('Esses dados não saem do seu computador e são apagados junto com o estudo.'))
})
