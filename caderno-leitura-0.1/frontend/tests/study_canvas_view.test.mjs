import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { ref } from 'vue'

const { useCanvasViewport } = await import('../src/composables/useCanvasViewport.ts')
const studyCanvasViewPath = path.resolve('src/components/views/StudyCanvasView.vue')
const canvasToolbarPath = path.resolve('src/components/views/canvas/CanvasToolbar.vue')

// ============================================================================
// User Story 1: Mesa de Trabalho Espacial Livre e Criação Rápida In-Place (P1 - MVP)
// ============================================================================

test('US1: Projeção inversa de coordenadas de tela para o mundo no Canvas', () => {
  const viewport = useCanvasViewport({ bookId: ref(1) })
  viewport.panX.value = 100
  viewport.panY.value = 50
  viewport.zoomLevel.value = 1.5

  // Screen: x = 250, y = 200
  // World: x = (250 - 100) / 1.5 = 100
  // World: y = (200 - 50) / 1.5 = 100
  const world = viewport.screenToWorld(250, 200)
  assert.equal(Math.round(world.x), 100)
  assert.equal(Math.round(world.y), 100)
})

test('US1: StudyCanvasView.vue implementa duplo clique (@dblclick) e mini-card de criação in-place', () => {
  const content = fs.readFileSync(studyCanvasViewPath, 'utf-8')

  // Duplo clique e manipulador
  assert.match(content, /@dblclick="handleCanvasDblClick"/)
  assert.match(content, /quickCreateState/)
  assert.match(content, /MapQuickCreateCard/)
  assert.match(content, /handleQuickStudyCreated/)
})

test('US1: CanvasToolbar.vue disponibiliza botão de criação rápida de estudo', () => {
  const content = fs.readFileSync(canvasToolbarPath, 'utf-8')

  // Botão de criação rápida
  assert.match(content, /quick-create|add-study|novo estudo/i)
  assert.match(content, /\$emit\('(quick-create|add-study)'\)|emit\('(quick-create|add-study)'\)/)
})

// ============================================================================
// User Story 2: Molduras Espaciais e Agrupamento Temático Solidário (P2)
// ============================================================================

test('US2: StudyCanvasView.vue suporta ferramenta de desenho de moldura e movimento solidário', () => {
  const content = fs.readFileSync(studyCanvasViewPath, 'utf-8')

  assert.match(content, /isDrawingFrame/)
  assert.match(content, /canvas-frame-draft/)
  assert.match(content, /moveFrameSolidary/)
})

// ============================================================================
// User Story 3: Conexões Direcionadas, Snapping e Ergonomia Mobile (P3)
// ============================================================================

test('US3: StudyCanvasView.vue integra guias magnéticas inteligentes (Smart Guides) e camada SVG', () => {
  const content = fs.readFileSync(studyCanvasViewPath, 'utf-8')

  assert.match(content, /useSmartSnapping/)
  assert.match(content, /canvas-smart-guides-layer/)
  assert.match(content, /smartSnapping\.snapPosition/)
})

test('US3: StudyCanvasView.vue integra conexões direcionadas com linha elástica e popover semântico', () => {
  const content = fs.readFileSync(studyCanvasViewPath, 'utf-8')

  assert.match(content, /canvas-draft-connection-layer/)
  assert.match(content, /MapRelationPopover/)
  assert.match(content, /createStudyRelation/)
})

test('US3: CanvasToolbar.vue implementa ergonomia mobile com alvos táteis mínimos de 44px', () => {
  const toolbarContent = fs.readFileSync(canvasToolbarPath, 'utf-8')

  assert.match(toolbarContent, /min-width:\s*44px/)
  assert.match(toolbarContent, /min-height:\s*44px/)
})

