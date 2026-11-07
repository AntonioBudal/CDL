import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { buildReferenceScopes, formatIndirectCitationWithLocator } from '../src/utils/referenceScopes.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8').replace(/\r\n/g, '\n')

// Item 1 — Revisão
test('102.1: hub com duas entradas, sem o botão duplicado, e N nos rótulos', () => {
  const hub = read('views/ReviewHubView.vue')
  assert.ok(!hub.includes('Prática Rápida neste Hub'))
  assert.ok(!hub.includes('start-review-btn'))
  assert.ok(!hub.includes('Iniciar Sessão Estruturada'))
  assert.match(hub, /class="start-structured-btn quiet"/)
  assert.match(hub, /Sessão registrada<template v-if="selectedBookId"> do livro<\/template> \(até \{\{ sessionSize \}\} itens\)/)
  assert.ok(hub.includes('Fica no histórico e pode ser retomada depois.'))
  assert.match(hub, /:practice-count="Math\.min\(sessionSize, eligibleCountForSelection\)"/)
  assert.match(hub, /:more-count="sessionSize"/)
  const header = read('components/review/ReviewStatsHeader.vue')
  assert.match(header, /practiceCount\?: number \| null/)
  assert.ok(header.includes('Praticar agora'))
  const modal = read('components/review/ReviewSummaryModal.vue')
  assert.ok(!modal.includes('Revisar mais 10'))
  assert.match(modal, /Revisar mais \{\{ moreCount \}\}/)
})

// Item 2 — Licença
test('102.2: nenhum texto público afirma "software livre"', () => {
  for (const rel of ['App.vue', 'components/layout/AppFooter.vue', 'views/SupportView.vue']) {
    const content = read(rel)
    assert.ok(!/software livre/i.test(content), rel)
    assert.ok(!/open source/i.test(content), rel)
  }
  assert.ok(read('App.vue').includes('>Código-fonte público</a>'))
  assert.ok(read('components/layout/AppFooter.vue').includes('>Código-fonte público</a>'))
  assert.ok(read('views/SupportView.vue').includes('com código-fonte público'))
})

// Item 3 — Digitalização
test('102.3: erros passageiros guardam a foto e oferecem "Tentar de novo"', () => {
  const draft = read('composables/useDigitizeDraft.ts')
  assert.match(draft, /DIGITIZE_TRANSIENT_CODES: readonly DigitizeErrorCode\[\] = \['busy', 'low_memory'\]/)
  assert.match(draft, /if \(isTransientDigitizeError\(code\)\) \{\n\s+\/\/[^\n]*\n\s+fail\(code, errorMessage\(error\)\)\n\s+return false\n\s+\}\n\s+releasePhoto\(\)/)
  assert.match(draft, /async function retry\(\): Promise<boolean>/)
  assert.match(draft, /choose, retry, cancel/)
  const view = read('views/DigitizeNotebookView.vue')
  assert.ok(view.includes("transientError ? 'Não deu para ler agora' : 'Não foi possível ler esta foto'"))
  assert.match(view, /v-if="transientError" type="button" class="primary" @click="retrySamePhoto">Tentar de novo/)
  assert.match(view, /:class="transientError \? 'secondary' : 'primary'" @click="startAnother">Tentar outra foto/)
})

// Item 5 — Cópia na tela do estudo
test('102.5: cópia do estudo vira citação indireta ABNT com a página', () => {
  const scopes = buildReferenceScopes({
    book: { title: 'Livro de Teste', author: 'Ana Fictícia', year: 2001 },
    location: 'p. 32-34',
  })
  assert.equal(formatIndirectCitationWithLocator('Trecho do\nleitor.', scopes), 'Trecho do leitor (Fictícia, 2001, p. 32–34).')
  const noMeta = buildReferenceScopes({ book: { title: 'Livro de Teste' } })
  assert.equal(formatIndirectCitationWithLocator('Trecho', noMeta), 'Trecho (Livro..., [s. d.]).')
  const view = read('views/StudyView.vue')
  assert.ok(!view.includes('formatQuoteText('))
  assert.match(view, /formatIndirectCitationWithLocator\(\n\s+sel\.selected_text,\n\s+buildReferenceScopes\(\{/)
  assert.match(view, /location: state\.context\.study\.location/)
})

// Item 6 — Teste indiferente a CRLF
test('102.6: superclasses.test.mjs normaliza CRLF ao ler arquivos', () => {
  const t = fs.readFileSync(path.resolve(process.cwd(), 'tests/superclasses.test.mjs'), 'utf-8')
  assert.match(t, /content\.replace\(\/\\r\\n\/g, '\\n'\)/)
})
