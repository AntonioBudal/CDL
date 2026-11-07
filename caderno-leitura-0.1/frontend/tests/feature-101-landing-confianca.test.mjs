import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { externalOrigins, groupEntriesByOrigin, summarizeCsp } from '../src/utils/networkAudit.ts'
import {
  COST_ROWS,
  LEITORUM_COST,
  formatCheckedAt,
  formatUsd,
  yearlyTotal,
} from '../src/components/landing/costSources.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')
const PAGE = 'http://127.0.0.1:8010'

// ---------- Desafio F12 ----------

test('101: agrupa entradas por origem, este servidor primeiro, ignorando data: e blob:', () => {
  const groups = groupEntriesByOrigin(
    [
      { name: `${PAGE}/` },
      { name: `${PAGE}/assets/app.js` },
      { name: 'https://exemplo.invalid/x.js' },
      { name: 'data:image/png;base64,AAAA' },
      { name: 'blob:http://127.0.0.1:8010/abc' },
      { name: 'https://a.invalid/y' },
      { name: 'not a url' },
    ],
    PAGE,
  )
  assert.deepEqual(groups, [
    { origin: PAGE, count: 2, sameOrigin: true },
    { origin: 'https://a.invalid', count: 1, sameOrigin: false },
    { origin: 'https://exemplo.invalid', count: 1, sameOrigin: false },
  ])
  assert.equal(externalOrigins(groups).length, 2)
  assert.deepEqual(groupEntriesByOrigin([], PAGE), [])
})

test('101: resumo da CSP com e sem cabeçalho', () => {
  assert.deepEqual(summarizeCsp(null), { present: false, directives: {} })
  assert.deepEqual(summarizeCsp('  '), { present: false, directives: {} })
  const csp = summarizeCsp("default-src 'self'; script-src 'self' https://accounts.google.com; connect-src 'self'; style-src 'self' 'unsafe-inline'")
  assert.equal(csp.present, true)
  assert.equal(csp.directives['default-src'], "'self'")
  assert.equal(csp.directives['script-src'], "'self' https://accounts.google.com")
  assert.equal(csp.directives['connect-src'], "'self'")
  assert.equal(csp.directives['style-src'], undefined)
})

test('101: seção Desafio F12 com passos, painel ao vivo, CSP e honestidade sobre limites', () => {
  const sec = read('components/landing/TrustChallengeSection.vue')
  assert.ok(sec.includes('id="desafio-f12"'))
  assert.match(sec, /getEntriesByType\('navigation'\)/)
  assert.match(sec, /getEntriesByType\('resource'\)/)
  assert.match(sec, /method: 'HEAD'/)
  assert.match(sec, /headers\.get\('Content-Security-Policy'\)/)
  assert.ok(sec.includes('aria-live="polite"'))
  assert.match(sec, /class="quiet trust-recheck"/)
  assert.ok(sec.includes('Extensões instaladas podem fazer pedidos próprios'))
  assert.ok(sec.includes('Seu navegador não expõe esta lista; use o F12.'))
  assert.ok(sec.includes('Não foi possível ler a política agora.'))
})

// ---------- Custo com fontes e datas ----------

test('101: toda linha de preço tem fonte https e data de consulta ISO', () => {
  assert.ok(COST_ROWS.length >= 2)
  for (const row of COST_ROWS) {
    assert.match(row.sourceUrl, /^https:\/\//, row.product)
    assert.match(row.checkedAt, /^\d{4}-\d{2}-\d{2}$/, row.product)
    assert.ok(!Number.isNaN(Date.parse(row.checkedAt)), row.product)
    assert.ok(row.plans.length > 0, row.product)
    for (const plan of row.plans) assert.equal(typeof plan.yearlyMonthly, 'number')
  }
  assert.match(LEITORUM_COST.sourceUrl, /^https:\/\//)
  assert.equal(LEITORUM_COST.license, 0)
  assert.ok(LEITORUM_COST.note.includes('não são estimadas'))
})

test('101: preços conferidos nas fontes oficiais em 07/11/2026', () => {
  const readwise = COST_ROWS.find((r) => r.product === 'Readwise')
  const notion = COST_ROWS.find((r) => r.product === 'Notion')
  assert.equal(readwise.sourceUrl, 'https://readwise.io/pricing')
  assert.deepEqual(readwise.plans.find((p) => p.name === 'Full'), { name: 'Full', yearlyMonthly: 9.99, monthly: 12.99 })
  assert.equal(notion.sourceUrl, 'https://www.notion.com/pricing')
  assert.deepEqual(notion.plans.find((p) => p.name === 'Plus'), { name: 'Plus', yearlyMonthly: 10, monthly: 12 })
})

test('101: formatação de dólar, data e total anual', () => {
  assert.equal(formatUsd(9.99), 'US$ 9,99')
  assert.equal(formatUsd(10), 'US$ 10')
  assert.equal(formatCheckedAt('2026-11-07'), '07/11/2026')
  assert.equal(yearlyTotal({ name: 'Full', yearlyMonthly: 9.99, monthly: 12.99 }), 'US$ 119,88')
  assert.equal(yearlyTotal({ name: 'Plus', yearlyMonthly: 10, monthly: 12 }), 'US$ 120')
})

test('101: tabela mostra fonte e data em cada linha de preço', () => {
  const comp = read('components/landing/CostComparison.vue')
  assert.match(comp, /<a :href="row\.sourceUrl" target="_blank" rel="noopener noreferrer">/)
  assert.match(comp, /<time :datetime="row\.checkedAt">\{\{ formatCheckedAt\(row\.checkedAt\) \}\}<\/time>/)
  assert.ok(comp.includes('Preços de terceiros mudam; confira na fonte.'))
})

// ---------- Landing ----------

test('101: landing inclui as seções depois de Seus dados e não carrega nada de terceiros', () => {
  const view = read('views/LandingView.vue')
  const order = ['<SovereigntySection />', '<TrustChallengeSection />', '<CostComparison />']
  const idx = order.map((tag) => view.indexOf(tag))
  assert.ok(idx.every((i) => i >= 0) && idx[0] < idx[1] && idx[1] < idx[2])
  for (const rel of ['components/landing/TrustChallengeSection.vue', 'components/landing/CostComparison.vue']) {
    const content = read(rel)
    assert.ok(!/<(script|link|img|iframe)[^>]+(src|href)="https?:/.test(content), `${rel} não carrega recurso externo`)
    assert.ok(!/fetch\(\s*['"`]https?:/.test(content), `${rel} não busca terceiros`)
  }
})
