import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

const {
  isNodeInsideFrame,
  getContainedNodes,
  computeTemporaryLanesProjection,
  useCanvasFrames,
  DEFAULT_CARD_WIDTH,
  DEFAULT_CARD_HEIGHT,
} = await import('../src/composables/useCanvasFrames.ts')

// ==========================================
// 1. Testes de Contenção Espacial Retangular
// ==========================================

test('isNodeInsideFrame identifica corretamente quando centro do nó está dentro da moldura', () => {
  const frame = { pos_x: 100, pos_y: 100, width: 400, height: 300 }

  // Nó com centro em (100 + 220/2, 100 + 140/2) = (210, 170) -> Dentro
  const insideNode = { pos_x: 100, pos_y: 100, width: DEFAULT_CARD_WIDTH, height: DEFAULT_CARD_HEIGHT }
  assert.equal(isNodeInsideFrame(insideNode, frame), true)

  // Nó no canto superior esquerdo (fora da moldura)
  const outsideLeft = { pos_x: -200, pos_y: 100, width: 200, height: 100 }
  assert.equal(isNodeInsideFrame(outsideLeft, frame), false)

  // Nó abaixo da moldura
  const outsideBottom = { pos_x: 150, pos_y: 500, width: 200, height: 100 }
  assert.equal(isNodeInsideFrame(outsideBottom, frame), false)

  // Nó à direita da moldura
  const outsideRight = { pos_x: 600, pos_y: 150, width: 200, height: 100 }
  assert.equal(isNodeInsideFrame(outsideRight, frame), false)
})

test('isNodeInsideFrame suporta tanto pos_x/pos_y quanto x/y', () => {
  const frame = { pos_x: 50, pos_y: 50, width: 300, height: 200 }

  const nodeWithXY = { x: 100, y: 100, width: 100, height: 80 }
  assert.equal(isNodeInsideFrame(nodeWithXY, frame), true)

  const nodeOutsideWithXY = { x: 500, y: 100, width: 100, height: 80 }
  assert.equal(isNodeInsideFrame(nodeOutsideWithXY, frame), false)
})

test('getContainedNodes filtra apenas os nós cujos centros estão dentro da moldura', () => {
  const frame = { pos_x: 0, pos_y: 0, width: 500, height: 400 }

  const nodes = [
    { study_id: 1, x: 50, y: 50, width: 200, height: 100 }, // centro (150, 100) -> dentro
    { study_id: 2, x: 200, y: 200, width: 200, height: 100 }, // centro (300, 250) -> dentro
    { study_id: 3, x: 600, y: 100, width: 200, height: 100 }, // centro (700, 150) -> fora
    { study_id: 4, x: 100, y: 500, width: 200, height: 100 }, // centro (200, 550) -> fora
  ]

  const contained = getContainedNodes(frame, nodes)
  assert.equal(contained.length, 2)
  assert.deepEqual(contained.map(n => n.study_id), [1, 2])
})

// ==========================================
// 2. Testes de Movimentação Solidária em Bloco
// ==========================================

test('moveFrameSolidary desloca moldura e nós contidos simultaneamente sem afetar nós externos', () => {
  const composable = useCanvasFrames()
  composable.frames.value = [
    {
      id: 1,
      book_id: 10,
      title: 'Moldura Alfa',
      color: 'amber',
      pos_x: 100,
      pos_y: 100,
      width: 400,
      height: 300,
      created_at: '2026-09-19T00:00:00Z',
      updated_at: '2026-09-19T00:00:00Z',
    },
  ]

  const nodes = [
    { study_id: 1, x: 120, y: 120, width: 100, height: 80 }, // Contido (centro 170, 160)
    { study_id: 2, x: 200, y: 150, width: 100, height: 80 }, // Contido (centro 250, 190)
    { study_id: 3, x: 700, y: 700, width: 100, height: 80 }, // Externo
  ]

  const result = composable.moveFrameSolidary(1, 50, -30, nodes)

  // Moldura deslocada
  const frame = composable.frames.value[0]
  assert.equal(frame.pos_x, 150)
  assert.equal(frame.pos_y, 70)

  // Nós contidos deslocados
  assert.equal(nodes[0].x, 170)
  assert.equal(nodes[0].y, 90)
  assert.equal(nodes[1].x, 250)
  assert.equal(nodes[1].y, 120)

  // Nó externo intocado
  assert.equal(nodes[2].x, 700)
  assert.equal(nodes[2].y, 700)

  // Retorno da função
  assert.equal(result.movedNodes.length, 2)
  assert.equal(result.movedNodes[0].study_id, 1)
  assert.equal(result.movedNodes[0].x, 170)
})

// ==========================================
// 3. Testes de Projeção Reversível no Canvas
// ==========================================

test('computeTemporaryLanesProjection agrupa nós em colunas distintas por status de leitura', () => {
  const nodes = [
    { study_id: 1, x: 0, y: 0 },
    { study_id: 2, x: 50, y: 50 },
    { study_id: 3, x: 100, y: 100 },
  ]

  const studies = [
    { id: 1, title: 'S1', reading_status: 'rascunho', chapter_id: 1, created_at: '2026-09-01T00:00:00Z' },
    { id: 2, title: 'S2', reading_status: 'em_estudo', chapter_id: 1, created_at: '2026-09-01T00:00:00Z' },
    { id: 3, title: 'S3', reading_status: 'rascunho', chapter_id: 1, created_at: '2026-09-01T00:00:00Z' },
  ]

  const projected = computeTemporaryLanesProjection(nodes, studies, 'status')
  assert.equal(projected.size, 3)

  // Estudos com mesmo status compartilham mesma coluna (pos_x)
  const p1 = projected.get(1)
  const p2 = projected.get(2)
  const p3 = projected.get(3)

  assert.equal(p1.pos_x, p3.pos_x)
  assert.notEqual(p1.pos_x, p2.pos_x)

  // P3 fica abaixo de P1 na mesma coluna
  assert.ok(p3.pos_y > p1.pos_y)
})

test('applyReversibleProjection salva coordenadas manuais e restaura fielmente ao voltar para manual', () => {
  const composable = useCanvasFrames()

  const nodes = [
    { study_id: 1, x: 45, y: 80, width: 220, height: 140 },
    { study_id: 2, x: 310, y: 150, width: 220, height: 140 },
  ]

  const studies = [
    { id: 1, title: 'S1', reading_status: 'rascunho', chapter_id: 1, created_at: '2026-09-01T00:00:00Z' },
    { id: 2, title: 'S2', reading_status: 'concluido', chapter_id: 1, created_at: '2026-09-01T00:00:00Z' },
  ]

  // Aplicar projeção por status
  composable.applyReversibleProjection(nodes, studies, 'status')
  assert.equal(composable.isTemporaryProjectionActive.value, true)

  // Posições mudaram
  assert.notEqual(nodes[0].x, 45)
  assert.notEqual(nodes[1].x, 310)

  // Reverter para agrupamento manual
  composable.applyReversibleProjection(nodes, studies, 'manual')
  assert.equal(composable.isTemporaryProjectionActive.value, false)

  // Coordenadas originais 100% restauradas
  assert.equal(nodes[0].x, 45)
  assert.equal(nodes[0].y, 80)
  assert.equal(nodes[1].x, 310)
  assert.equal(nodes[1].y, 150)
})
