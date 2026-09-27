import test from 'node:test'
import assert from 'node:assert/strict'
import { findBestMatchOffset, getHighlightClassNames } from '../src/utils/highlightRenderer.ts'

test('findBestMatchOffset localiza deslocamento exato do texto selecionado', () => {
  const fullText = 'A epistemologia contemporânea investiga a validade dos modelos teóricos.'
  const target = 'validade dos modelos'
  const offset = findBestMatchOffset(fullText, target, 40)

  assert.equal(offset, 42)
})

test('findBestMatchOffset desambigua ocorrência mais próxima de approximateOffset', () => {
  const fullText = 'Pois o modelo A explica o caso. Porém, o modelo B contradiz o modelo C.'
  const target = 'o modelo'

  // Primeira ocorrência esperada perto do índice 5
  const firstMatch = findBestMatchOffset(fullText, target, 5)
  assert.equal(firstMatch, 5)

  // Segunda ocorrência esperada perto do índice 39
  const secondMatch = findBestMatchOffset(fullText, target, 40)
  assert.equal(secondMatch, 39)

  // Terceira ocorrência esperada perto do índice 60
  const thirdMatch = findBestMatchOffset(fullText, target, 60)
  assert.equal(thirdMatch, 60)
})

test('getHighlightClassNames gera classes corretas para cada kind e cor', () => {
  const hlHighlight = {
    id: 1,
    study_id: 10,
    user_id: 'u1',
    section: 'summary',
    start_offset: 0,
    end_offset: 10,
    selected_text: 'texto',
    prefix: '',
    suffix: '',
    color: 'green',
    kind: 'highlight',
    note: '',
    created_at: '',
    updated_at: '',
  }
  assert.equal(getHighlightClassNames(hlHighlight), 'study-highlight hl-green')

  const hlNote = { ...hlHighlight, color: 'blue', kind: 'note', note: 'Nota pessoal' }
  assert.equal(getHighlightClassNames(hlNote), 'study-highlight study-note hl-blue')

  const hlHidden = { ...hlHighlight, kind: 'hidden' }
  assert.equal(getHighlightClassNames(hlHidden), 'study-occlusion hl-hidden')

  const hlQuestion = { ...hlHighlight, kind: 'question', note: 'Qual o conceito?' }
  assert.equal(getHighlightClassNames(hlQuestion), 'study-question-target hl-question')
})

test('escapeHtml neutraliza caracteres perigosos e tags injetadas', async () => {
  const { escapeHtml } = await import('../src/utils/highlightRenderer.ts')
  const raw = '<script>alert("xss")</script> & "aspas" e \'apóstrofo\''
  const sanitized = escapeHtml(raw)

  assert.equal(sanitized.includes('<script>'), false)
  assert.ok(sanitized.includes('&lt;script&gt;'))
  assert.ok(sanitized.includes('&quot;aspas&quot;'))
  assert.ok(sanitized.includes('&#039;apóstrofo&#039;'))
  assert.ok(sanitized.includes('&amp;'))
})

test('MarkdownContent.vue define estilos de oclusão e classes para estudo ativo', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const contentPath = path.resolve('src/components/MarkdownContent.vue')
  const content = fs.readFileSync(contentPath, 'utf-8')

  // Classes de oclusão e revelação
  assert.ok(content.includes('.study-occlusion'), 'Deve definir estilo para .study-occlusion')
  assert.ok(content.includes('.study-occlusion.is-revealed'), 'Deve definir estado revelado para .study-occlusion.is-revealed')
  assert.ok(content.includes('.study-occlusion-btn'), 'Deve definir botão de revelação')

  // Classes de pergunta
  assert.ok(content.includes('.study-question-target'), 'Deve definir estilo de destino da pergunta')
  assert.ok(content.includes('.study-question-badge'), 'Deve definir badge de pergunta')
  assert.ok(content.includes('.study-question-reveal-btn'), 'Deve definir botão de ver resposta')
})
