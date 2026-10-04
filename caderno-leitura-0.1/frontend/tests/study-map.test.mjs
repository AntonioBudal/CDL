import test from 'node:test'
import assert from 'node:assert/strict'

const {
  computeRadialLayout,
  DEFAULT_MAP_LAYOUT_OPTIONS,
} = await import('../src/composables/useMapLayout.ts')

// ==========================================
// Testes de Layout Radial Concêntrico (T003 - Foundational)
// ==========================================

test('computeRadialLayout com lista vazia retorna estrutura vazia', () => {
  const result = computeRadialLayout([], [])
  assert.equal(result.coreNode, null)
  assert.deepEqual(result.nodes, [])
  assert.deepEqual(result.edges, [])
})

test('computeRadialLayout ancora estudo focal como nó núcleo ao centro', () => {
  const mockStudies = [
    { id: 1, chapter_id: 10, title: 'Estudo 1', location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 10, title: 'Estudo 2', location: '', created_at: '', updated_at: '' },
    { id: 3, chapter_id: 10, title: 'Estudo 3', location: '', created_at: '', updated_at: '' },
  ]

  // Define Estudo 2 como ativo
  const result = computeRadialLayout(mockStudies, [], 2)

  assert.ok(result.coreNode)
  assert.equal(result.coreNode.study.id, 2)
  assert.equal(result.coreNode.isCore, true)
  assert.equal(result.coreNode.ring, 'core')
  assert.equal(result.coreNode.x, DEFAULT_MAP_LAYOUT_OPTIONS.cx)
  assert.equal(result.coreNode.y, DEFAULT_MAP_LAYOUT_OPTIONS.cy)
})

test('computeRadialLayout seleciona estudo com maior grau quando activeStudyId é nulo', () => {
  const mockStudies = [
    { id: 10, chapter_id: 1, title: 'Isolado', location: '', created_at: '', updated_at: '' },
    { id: 20, chapter_id: 1, title: 'Mais Conectado', location: '', created_at: '', updated_at: '' },
    { id: 30, chapter_id: 1, title: 'Satélite', location: '', created_at: '', updated_at: '' },
  ]
  const mockRelations = [
    { id: 1, source_study_id: 20, target_study_id: 10, relation_type: 'fundamenta' },
    { id: 2, source_study_id: 20, target_study_id: 30, relation_type: 'desdobra' },
  ]

  const result = computeRadialLayout(mockStudies, mockRelations, null)

  assert.ok(result.coreNode)
  assert.equal(result.coreNode.study.id, 20)
  assert.equal(result.coreNode.degree, 2)
})

test('computeRadialLayout separa nós conectados em anel primário e desconectados em secundário', () => {
  const mockStudies = [
    { id: 1, chapter_id: 1, title: 'Núcleo', location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 1, title: 'Vizinho Direto', location: '', created_at: '', updated_at: '' },
    { id: 3, chapter_id: 1, title: 'Distante', location: '', created_at: '', updated_at: '' },
  ]
  const mockRelations = [
    { id: 101, source_study_id: 1, target_study_id: 2, relation_type: 'complementa' },
  ]

  const result = computeRadialLayout(mockStudies, mockRelations, 1)

  const nodeVizinho = result.nodes.find((n) => n.study.id === 2)
  const nodeDistante = result.nodes.find((n) => n.study.id === 3)

  assert.ok(nodeVizinho)
  assert.ok(nodeDistante)

  assert.equal(nodeVizinho.ring, 'primary')
  assert.equal(nodeDistante.ring, 'secondary')

  // Distância euclidiana ao centro
  const distVizinho = Math.round(
    Math.hypot(nodeVizinho.x - DEFAULT_MAP_LAYOUT_OPTIONS.cx, nodeVizinho.y - DEFAULT_MAP_LAYOUT_OPTIONS.cy)
  )
  const distDistante = Math.round(
    Math.hypot(nodeDistante.x - DEFAULT_MAP_LAYOUT_OPTIONS.cx, nodeDistante.y - DEFAULT_MAP_LAYOUT_OPTIONS.cy)
  )

  assert.equal(distVizinho, DEFAULT_MAP_LAYOUT_OPTIONS.primaryRadius)
  assert.equal(distDistante, DEFAULT_MAP_LAYOUT_OPTIONS.secondaryRadius)
})

test('computeRadialLayout calcula arestas direcionadas curvas com badges e trata contradição', () => {
  const mockStudies = [
    { id: 1, chapter_id: 1, title: 'Premissa', location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 1, title: 'Antítese', location: '', created_at: '', updated_at: '' },
  ]
  const mockRelations = [
    { id: 50, source_study_id: 1, target_study_id: 2, relation_type: 'contradiz', description: 'Conflito de teses' },
  ]

  const result = computeRadialLayout(mockStudies, mockRelations, 1)

  assert.equal(result.edges.length, 1)
  const edge = result.edges[0]

  assert.equal(edge.id, 50)
  assert.equal(edge.sourceStudyId, 1)
  assert.equal(edge.targetStudyId, 2)
  assert.equal(edge.relationType, 'contradiz')
  assert.equal(edge.isContradiction, true)
  assert.match(edge.path, /^M \d+ \d+ Q \d+ \d+ \d+ \d+$/)
  assert.ok(edge.badgeX > 0)
  assert.ok(edge.badgeY > 0)
})

test('computeRadialLayout descarta auto-relações espúrias', () => {
  const mockStudies = [
    { id: 1, chapter_id: 1, title: 'Estudo A', location: '', created_at: '', updated_at: '' },
  ]
  const mockRelations = [
    { id: 99, source_study_id: 1, target_study_id: 1, relation_type: 'complementa' },
  ]

  const result = computeRadialLayout(mockStudies, mockRelations, 1)

  assert.equal(result.edges.length, 0, 'Auto-relação não deve gerar aresta')
})
