import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))

const dashboardViewSource = readFileSync(
  resolve(__dirname, '../src/views/DashboardView.vue'),
  'utf-8'
)
const resumeWidgetSource = readFileSync(
  resolve(__dirname, '../src/components/dashboard/ResumeStudiesWidget.vue'),
  'utf-8'
)
const orphanWidgetSource = readFileSync(
  resolve(__dirname, '../src/components/dashboard/OrphanStudiesWidget.vue'),
  'utf-8'
)
const recentWidgetSource = readFileSync(
  resolve(__dirname, '../src/components/dashboard/RecentConnectionsWidget.vue'),
  'utf-8'
)
const quickNavSource = readFileSync(
  resolve(__dirname, '../src/components/dashboard/QuickNavChips.vue'),
  'utf-8'
)

test('FR-014 e FR-015: DashboardView possui contenção estrita de largura e overflow-x hidden', () => {
  assert.ok(
    dashboardViewSource.includes('overflow-x: hidden;'),
    'DashboardView deve ter overflow-x: hidden para blindagem contra rolagem lateral'
  )
  assert.ok(
    dashboardViewSource.includes('max-width: 100vw;'),
    'DashboardView deve respeitar largura máxima de 100vw no mobile'
  )
})

test('FR-014: Em resoluções móveis (<=768px), grade métrica adota layout 2x2', () => {
  assert.ok(
    dashboardViewSource.includes('@media (max-width: 768px)') &&
    dashboardViewSource.includes('grid-template-columns: repeat(2, 1fr);'),
    'Métricas devem se organizar em grade 2x2 no mobile para visualização compacta'
  )
})

test('FR-014: Em telas <1024px, widgets secundários comutam para abas acessíveis', () => {
  assert.ok(
    dashboardViewSource.includes('class="mobile-secondary-tabs mobile-only-tabs"'),
    'Deve incluir container de abas móveis para widgets secundários'
  )
  assert.ok(
    dashboardViewSource.includes('role="tablist"'),
    'Barra de abas secundárias deve possuir role="tablist"'
  )
  assert.ok(
    dashboardViewSource.includes('class="secondary-tab-btn"'),
    'Botões de aba devem ter classe secondary-tab-btn'
  )
})

test('FR-015 e SC-004: Todos os gatilhos e botões interativos cumprem alvos táteis mínimos de 44px', () => {
  // ResumeStudiesWidget
  assert.ok(
    resumeWidgetSource.includes('min-height: 44px;'),
    'ResumeStudiesWidget deve assegurar alvos táteis de no mínimo 44px'
  )

  // OrphanStudiesWidget
  assert.ok(
    orphanWidgetSource.includes('min-height: 44px;'),
    'OrphanStudiesWidget deve assegurar alvos táteis de no mínimo 44px'
  )

  // QuickNavChips
  assert.ok(
    quickNavSource.includes('min-height: 44px;') && quickNavSource.includes('min-width: 44px;'),
    'QuickNavChips deve ter dimensões mínimas táteis de 44x44px'
  )

  // Secondary tab buttons in DashboardView
  assert.ok(
    dashboardViewSource.includes('.secondary-tab-btn') &&
    dashboardViewSource.includes('min-height: 44px;'),
    'Abas secundárias devem ter no mínimo 44px de altura'
  )
})
