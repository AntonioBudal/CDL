import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// F0.10.04 — revisão com baldes por dificuldade, sessões de 5/10/15 itens e gaveta de contexto após revelar.
const srcDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../src')
const read = (rel) => fs.readFileSync(path.join(srcDir, rel), 'utf-8')

test('baldes como radiogroup, com os quatro níveis e balde vazio desabilitado', () => {
  const header = read('components/review/ReviewStatsHeader.vue')
  assert.match(header, /role="radiogroup"\s+aria-label="Filtrar por dificuldade"/)
  for (const label of ['Novos', 'Difícil', 'Médio', 'Fácil']) {
    assert.ok(header.includes(label), `Balde "${label}"`)
  }
  assert.match(header, /:disabled="[^"]*bucketCount\(/)
  assert.match(header, /update:bucket/)
})

test('seletor de tamanho 5/10/15 aplicado às três entradas de sessão', () => {
  const header = read('components/review/ReviewStatsHeader.vue')
  assert.match(header, /\[5, 10, 15\]/)
  const hub = read('views/ReviewHubView.vue')
  assert.doesNotMatch(hub, /limit: 10,/, 'Nenhuma entrada de sessão com tamanho fixo')
  assert.equal((hub.match(/limit: sessionSize\.value/g) || []).length, 3)
  assert.match(hub, /caderno_review_session_size/)
  assert.match(hub, /bucket: selectedBucket\.value/)
})

test('gaveta "Ver o estudo" só depois de revelar, no hub e na sessão estruturada', () => {
  const card = read('components/review/ReviewCard.vue')
  assert.match(card, /v-if="isRevealed"[^>]*>[\s\S]{0,300}Ver o estudo/)
  const session = read('views/StudySessionView.vue')
  assert.match(session, /v-if="studySession\.isRevealed\.value"[\s\S]{0,600}Ver o estudo/)
  const drawer = read('components/review/StudyContextDrawer.vue')
  assert.match(drawer, /<Drawer/)
  assert.match(drawer, /MarkdownContent/)
  for (const label of ['Resumo', 'Explicação', 'Conceitos', 'Referências']) {
    assert.ok(drawer.includes(label), `Gaveta mostra "${label}"`)
  }
  assert.match(drawer, /não está mais disponível/)
})
