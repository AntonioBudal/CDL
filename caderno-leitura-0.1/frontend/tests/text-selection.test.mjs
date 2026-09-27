import test from 'node:test'
import assert from 'node:assert/strict'
import { calculateOffsetsFromText, formatQuoteText } from '../src/composables/useTextSelection.ts'

test('calculateOffsetsFromText localiza início e término de trecho no texto completo', () => {
  const fullText = 'No século XVIII, a revolução industrial transformou o modo de produção em escala global.'
  const selectedText = 'a revolução industrial transformou o modo de produção'

  const result = calculateOffsetsFromText(fullText, selectedText, 17)
  assert.ok(result)
  assert.equal(result.start_offset, 17)
  assert.equal(result.end_offset, 17 + selectedText.length)
  assert.equal(result.selected_text, selectedText)
  assert.equal(result.prefix, 'No século XVIII, ')
  assert.equal(result.suffix, ' em escala global.')
})

test('calculateOffsetsFromText desambigua ocorrências repetidas usando aproximação de índice', () => {
  const fullText = 'O conceito é vital. Mas o poder nem sempre é visível. Pois o poder institucional prevalece.'
  const selectedText = 'o poder'

  // Primeira ocorrência esperada perto do índice 24
  const match1 = calculateOffsetsFromText(fullText, selectedText, 24)
  assert.ok(match1)
  assert.equal(match1.start_offset, 24)

  // Segunda ocorrência esperada perto do índice 60
  const match2 = calculateOffsetsFromText(fullText, selectedText, 60)
  assert.ok(match2)
  assert.equal(match2.start_offset, 59)
})

test('formatQuoteText formata citação em Markdown com aspas e atribuição da obra', () => {
  const snippet = 'A liberdade é a necessidade compreendida.'
  const formatted = formatQuoteText({
    selected_text: snippet,
    studyTitle: 'Materialismo Histórico',
    bookTitle: 'Anti-Dühring',
    chapterName: 'Capítulo XI',
  })

  assert.ok(formatted.includes(`> "${snippet}"`))
  assert.ok(formatted.includes('*Materialismo Histórico*'))
  assert.ok(formatted.includes('Anti-Dühring'))
  assert.ok(formatted.includes('Capítulo XI'))
})
