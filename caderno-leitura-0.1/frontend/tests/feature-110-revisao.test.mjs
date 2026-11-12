import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { timeAgo } from '../src/utils/timeAgo.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('110: "há quanto tempo" da Memória do dia', () => {
  const now = new Date(2026, 10, 12, 12)
  assert.equal(timeAgo(new Date(2025, 10, 12, 9).toISOString(), now), 'há 1 ano')
  assert.equal(timeAgo(new Date(2023, 10, 1).toISOString(), now), 'há 3 anos')
  assert.equal(timeAgo(new Date(2026, 7, 12).toISOString(), now), 'há 3 meses')
  assert.equal(timeAgo(new Date(2026, 9, 1).toISOString(), now), 'há 1 mês')
  assert.equal(timeAgo(new Date(2026, 9, 20).toISOString(), now), 'há 23 dias')
})

test('110: filtro "Conceitos", verso do cartão e gravação pelo endpoint certo', () => {
  const header = read('components/review/ReviewStatsHeader.vue')
  assert.match(header, /@click="setKind\('concept'\)"/)
  assert.match(header, />\s*Conceitos\s*</)
  const card = read('components/review/ReviewCard.vue')
  assert.match(card, /item\.kind === 'concept' \? 'Conceito'/)
  assert.match(card, /v-for="\(definition, index\) in item\.definitions \?\? \[\]"/)
  const session = read('composables/useReviewSession.ts')
  assert.match(session, /if \(item\.kind === 'concept' && item\.concept_key\) await reviewApi\.recordConceptRating\(item\.concept_key, rating\)/)
  const api = read('services/api.ts')
  assert.match(api, /`\/review\/concepts\/\$\{encodeURIComponent\(key\)\}\/record`/)
  assert.match(api, /if \(params\?\.fragile\) queryParts\.push\('fragile=true'\)/)
  assert.match(api, /`\/review\/fragile-concepts\?limit=\$\{limit\}`/)
  assert.match(api, /`\/dashboard\/memory\?tz_offset=\$\{tzOffset\}`/)
})

test('110: conceitos frágeis na Central, etiqueta no Léxico e Memória no Painel', () => {
  const hub = read('views/ReviewHubView.vue')
  assert.match(hub, /<FragileConceptsPanel ref="fragilePanel"/)
  assert.match(hub, /session\.loadItems\(\{ kind: 'concept', fragile: true, limit \}\)/)
  assert.match(hub, /Os cartões de conceito ficam fora da sessão registrada/)
  const panel = read('components/review/FragileConceptsPanel.vue')
  assert.match(panel, /Praticar conceitos frágeis/)
  assert.match(panel, /class="quiet fragile-practice"/)
  assert.match(read('views/LexiconView.vue'), /<span v-if="item\.fragile" class="fragile-tag">Frágil<\/span>/)
  assert.match(read('views/ConceptView.vue'), /<span class="fragile-tag">Frágil<\/span>/)
  assert.match(read('views/DashboardView.vue'), /<DailyMemoryCard \/>/)
  const memory = read('components/dashboard/DailyMemoryCard.vue')
  assert.match(memory, /api\.getDailyMemory\(-new Date\(\)\.getTimezoneOffset\(\)\)/)
  assert.match(memory, /Memória do dia/)
})
