import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyMapViewPath = path.resolve('src/components/views/StudyMapView.vue')
const mapRelationPopoverPath = path.resolve('src/components/views/map/MapRelationPopover.vue')
const mapQuickCreateCardPath = path.resolve('src/components/views/map/MapQuickCreateCard.vue')

// ============================================================================
// User Story 1: Visualização Radial Semântica e Destaque do Estudo Núcleo (P1 - MVP)
// ============================================================================

test('US1: StudyMapView.vue renderiza Estudo Núcleo destacado e anéis concêntricos', () => {
  const mapContent = fs.readFileSync(studyMapViewPath, 'utf-8')

  // Núcleo central destacado e anéis
  assert.match(mapContent, /central-core-node|is-core|core-node/)
  assert.match(mapContent, /orbit-ring/)
  assert.match(mapContent, /computeRadialLayout|useMapLayout/)
})

test('US1: StudyMapView.vue traça arestas direcionadas com setas e rótulos semânticos', () => {
  const mapContent = fs.readFileSync(studyMapViewPath, 'utf-8')

  // Arestas direcionadas e badges
  assert.match(mapContent, /map-semantic-edge|map-arrow/)
  assert.match(mapContent, /map-edge-badge|edge\.label/)
})

test('US1: StudyMapView.vue implementa controles de zoom e navegação de pan', () => {
  const mapContent = fs.readFileSync(studyMapViewPath, 'utf-8')

  // Pan e Zoom
  assert.match(mapContent, /zoom-controls|zoom-btn|handleZoom/)
  assert.match(mapContent, /panX|panY|zoomLevel/)
})

// ============================================================================
// User Story 2: Traçado Interativo de Conexões e Mini-Popover de Relações (P2)
// ============================================================================

test('US2: StudyMapView.vue suporta traçado com linha elástica SVG e alça conectora', () => {
  const mapContent = fs.readFileSync(studyMapViewPath, 'utf-8')

  // Alça conectora e linha elástica
  assert.match(mapContent, /node-connect-handle/)
  assert.match(mapContent, /elastic-draft-line|draftLinePath/)
  assert.match(mapContent, /isConnecting/)
})

test('US2: MapRelationPopover.vue implementa oração semântica ativa e inversão rápida', () => {
  assert.ok(fs.existsSync(mapRelationPopoverPath), 'MapRelationPopover.vue deve existir')
  const popoverContent = fs.readFileSync(mapRelationPopoverPath, 'utf-8')

  // Oração semântica e inversão
  assert.match(popoverContent, /isReversed|reverseDirection|⇄/)
  assert.match(popoverContent, /relation_type|selectedType/)
  assert.match(popoverContent, /fundamenta|desdobra|contradiz/)
})

// ============================================================================
// User Story 3: Criação Direta de Estudos no Mapa e Ergonomia Mobile (P3)
// ============================================================================

test('US3: MapQuickCreateCard.vue implementa criação rápida in-place no mapa', () => {
  assert.ok(fs.existsSync(mapQuickCreateCardPath), 'MapQuickCreateCard.vue deve existir')
  const cardContent = fs.readFileSync(mapQuickCreateCardPath, 'utf-8')

  // Mini-card inline
  assert.match(cardContent, /quick-create-card/)
  assert.match(cardContent, /title/)
  assert.match(cardContent, /summary|concepts|explanation/)
})

test('US3: StudyMapView.vue define alvos táteis mínimos de 44x44px no mobile', () => {
  const mapContent = fs.readFileSync(studyMapViewPath, 'utf-8')

  // Ergonomia mobile
  assert.match(mapContent, /min-width:\s*44px/)
  assert.match(mapContent, /min-height:\s*44px/)
  assert.match(mapContent, /mobile-map-toolbar|touch-target|action-btn/)
})
