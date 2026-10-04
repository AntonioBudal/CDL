import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyTreeViewPath = path.resolve('src/components/views/StudyTreeView.vue')
const studyTreeNodeItemPath = path.resolve('src/components/views/StudyTreeNodeItem.vue')

// ============================================================================
// User Story 1: Linhas Guias e Controles Globais de Expansão (P1 - MVP)
// ============================================================================

test('US1: StudyTreeView.vue e StudyTreeNodeItem.vue implementam linhas guias conectoras em CSS contínuo', () => {
  const nodeContent = fs.readFileSync(studyTreeNodeItemPath, 'utf-8')

  // Conectores de ramo usando pseudo-elementos ou classes conectoras
  assert.match(nodeContent, /tree-node-connector|tree-branch::before/)
  assert.match(nodeContent, /border-(left|bottom)/)
})

test('US1: StudyTreeView.vue possui botões globais para Expandir Todos e Recolher Todos com contagem', () => {
  const treeContent = fs.readFileSync(studyTreeViewPath, 'utf-8')

  // Ações de expandir e recolher todos
  assert.match(treeContent, /@click="expandAll"/)
  assert.match(treeContent, /@click="collapseAll"/)
  assert.match(treeContent, /tree-count-badge/)
  assert.match(treeContent, /Expandir/)
  assert.match(treeContent, /Recolher/)
})

// ============================================================================
// User Story 2: Percepção e Indicadores de Progresso Agregado por Ramo (P2)
// ============================================================================

test('US2: StudyTreeNodeItem.vue renderiza micro-badge de progresso de ramo com fração e mini-barra', () => {
  const nodeContent = fs.readFileSync(studyTreeNodeItemPath, 'utf-8')

  // Micro-badge de progresso do ramo em nós pais
  assert.match(nodeContent, /branch-progress-badge/)
  assert.match(nodeContent, /node\.progress/)
  assert.match(nodeContent, /progress-fraction/)
  assert.match(nodeContent, /progress-bar-track/)
  assert.match(nodeContent, /progress-bar-fill/)
})

test('US2: StudyTreeNodeItem.vue exibe tooltip informativo com status do ramo', () => {
  const nodeContent = fs.readFileSync(studyTreeNodeItemPath, 'utf-8')

  // Tooltip detalhado
  assert.match(nodeContent, /concluídos/)
  assert.match(nodeContent, /role="status"|aria-label="Progresso do ramo"/)
})

// ============================================================================
// User Story 3: Reorganização Magnética, Bloqueio de Ciclos e Ergonomia Mobile (P3)
// ============================================================================

test('US3: StudyTreeNodeItem.vue e StudyTreeView.vue suportam moldura magnética de absorção no aninhamento', () => {
  const nodeContent = fs.readFileSync(studyTreeNodeItemPath, 'utf-8')
  const treeContent = fs.readFileSync(studyTreeViewPath, 'utf-8')

  // Estilos visuais e zonas de drop
  assert.match(nodeContent, /drop-inside/)
  assert.match(nodeContent, /drop-before/)
  assert.match(nodeContent, /drop-after/)

  // Bloqueio de ciclo
  assert.match(treeContent, /canNestUnder/)
  assert.match(nodeContent, /is-drop-forbidden/)
})

test('US3: StudyTreeNodeItem.vue define alvos táteis mínimos de 44x44px nos chevrons e menu de ações', () => {
  const nodeContent = fs.readFileSync(studyTreeNodeItemPath, 'utf-8')

  // Chevrons e botões táteis
  assert.match(nodeContent, /tree-chevron-btn/)
  assert.match(nodeContent, /min-width:\s*44px/)
  assert.match(nodeContent, /min-height:\s*44px/)
  assert.match(nodeContent, /touch-target|quick-action-item/)
})
