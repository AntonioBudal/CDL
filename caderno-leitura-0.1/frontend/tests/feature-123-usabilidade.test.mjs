import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// F0.12.10 (spec 123): pequenas melhorias de usabilidade.
const SRC = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.join(SRC, rel), 'utf-8')

test('123: períodos do calendário e o filtro do ano passado', async () => {
  const { HEATMAP_PERIODS, periodDays, pointsForPeriod, DEFAULT_PERIOD } = await import('../src/utils/heatmapPeriods.ts')
  assert.deepEqual(HEATMAP_PERIODS.map((p) => p.id), ['1m', '3m', '6m', '12m', 'last-year'])
  assert.equal(DEFAULT_PERIOD, '12m')
  assert.equal(periodDays('1m'), 30)
  assert.equal(periodDays('12m'), 365)
  assert.equal(periodDays('last-year'), 730)
  assert.equal(periodDays('desconhecido'), 365)
  const points = [
    { date: '2024-12-31', count: 1, level: 1 },
    { date: '2025-01-01', count: 2, level: 2 },
    { date: '2025-12-31', count: 1, level: 1 },
    { date: '2026-01-02', count: 3, level: 3 },
  ]
  const today = new Date(2026, 10, 15)
  assert.deepEqual(pointsForPeriod(points, 'last-year', today).map((p) => p.date), ['2025-01-01', '2025-12-31'])
  assert.equal(pointsForPeriod(points, '12m', today).length, 4, 'os outros períodos não filtram')
  const heatmap = read('components/HeatmapCalendar.vue')
  assert.match(heatmap, /v-for="period in HEATMAP_PERIODS"/)
  const dashboard = read('views/DashboardView.vue')
  assert.match(dashboard, /days: periodDays\(period\.value\)/)
  assert.match(dashboard, /localStorage\.setItem\(PERIOD_STORAGE_KEY, value\)/)
})

test('123: dias da semana dentro da grade e células sem a altura mínima dos botões', () => {
  const heatmap = read('components/HeatmapCalendar.vue')
  assert.match(heatmap, /class="week-column day-label-column"/)
  assert.doesNotMatch(heatmap, /<div class="day-labels"/, 'a coluna paralela sai')
  assert.match(heatmap, /\.heatmap-cell \{[^}]*min-height: 0;[^}]*min-width: 0;/)
})

test('123: filtro por dia com título, contagem e "Ver todas"', () => {
  const dashboard = read('views/DashboardView.vue')
  assert.match(dashboard, /Atividades em \{\{ formatSelectedDate\(selectedDate\) \}\}/)
  assert.match(dashboard, /Ver todas/)
  assert.match(dashboard, /scrollIntoView/)
})

test('123: barra de ações fixa acima das abas, desativada sem seleção', () => {
  assert.ok(!fs.existsSync(path.join(SRC, 'components/FloatingActionsToolbar.vue')), 'a barra flutuante sai')
  const bar = read('components/StudyActionsBar.vue')
  assert.match(bar, /position: sticky/)
  assert.match(bar, /:disabled="!hasSelection"/)
  assert.match(bar, /Selecione um trecho do texto/)
  assert.match(bar, /@mousedown="keepSelection"/)
  for (const event of ['highlight', 'copy-quote', 'occlude', 'open-note', 'open-question', 'tool-selected']) {
    assert.match(bar, new RegExp(`emit\\('${event}'`), event)
  }
  const study = read('views/StudyView.vue')
  const barAt = study.indexOf('<StudyActionsBar')
  const tabsAt = study.indexOf('<StudyTabs')
  assert.ok(barAt > 0 && barAt < tabsAt, 'a barra vem logo antes das abas')
  assert.doesNotMatch(study, /FloatingActionsToolbar/)
})

test('123: o menu encaixa na tela (função pura)', async () => {
  const { placeMenu } = await import('../src/utils/menuPlacement.ts')
  const viewport = { width: 375, height: 812 }
  // Gatilho à direita no celular, menu largo: encosta dentro da tela com margem.
  const right = placeMenu({ trigger: { left: 320, right: 364, top: 100, bottom: 146 }, menu: { width: 280, height: 300 }, viewport, align: 'right' })
  assert.equal(right.left, 364 - 280)
  const tooWide = placeMenu({ trigger: { left: 10, right: 54, top: 100, bottom: 146 }, menu: { width: 280, height: 300 }, viewport, align: 'right' })
  assert.equal(tooWide.left, 8, 'nunca sai pela esquerda')
  // Perto do fim da tela, com a barra de baixo do celular: abre para cima.
  const low = placeMenu({ trigger: { left: 300, right: 344, top: 600, bottom: 646 }, menu: { width: 200, height: 300 }, viewport, align: 'right', bottomInset: 64 })
  assert.equal(low.openUp, true)
  assert.ok(low.top + 300 <= 600, 'fica acima do gatilho')
  // Sem espaço nem embaixo nem em cima: rola por dentro.
  const huge = placeMenu({ trigger: { left: 300, right: 344, top: 380, bottom: 426 }, menu: { width: 200, height: 900 }, viewport, align: 'right', bottomInset: 64 })
  assert.ok(huge.maxHeight < 900 && huge.top >= 8 && huge.top + huge.maxHeight <= 812 - 64 - 8 + 0.5)
  assert.match(read('components/ui/DropdownMenu.vue'), /placeMenu\(/)
})

test('123: cabeçalho do estudo não cresce em coluna no celular', () => {
  assert.match(read('views/StudyView.vue'), /\.page-header\.reader-heading > div \{\n\s+flex: 0 0 auto;/)
})
