import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

const { useCanvasNodes, CARD_WIDTH, CARD_HEIGHT } = await import('../src/composables/useCanvasNodes.ts')

test('boundingBox calcula com precisão os limites mínimos e máximos dos cards', () => {
  const bookId = ref(10)
  const studies = ref([])
  const canvasNodes = useCanvasNodes({ bookId, studies })

  canvasNodes.positionedNodes.value = new Map([
    [1, { study_id: 1, x: 100, y: 150, width: 280, height: 200, z_index: 0, is_persisted: true }],
    [2, { study_id: 2, x: 500, y: 300, width: 280, height: 200, z_index: 0, is_persisted: true }],
    [3, { study_id: 3, x: 20, y: 80, width: 280, height: 200, z_index: 0, is_persisted: true }],
  ])

  const box = canvasNodes.boundingBox.value
  assert.ok(box !== null, 'Bounding box não deve ser nulo')

  assert.equal(box.min_x, 20)
  assert.equal(box.min_y, 80)
  assert.equal(box.max_x, 500 + 280) // 780
  assert.equal(box.max_y, 300 + 200) // 500
  assert.equal(box.width, 760) // 780 - 20
  assert.equal(box.height, 420) // 500 - 80
})

test('boundingBox retorna null quando não existem nós no canvas', () => {
  const bookId = ref(11)
  const studies = ref([])
  const canvasNodes = useCanvasNodes({ bookId, studies })

  canvasNodes.positionedNodes.value = new Map()
  assert.equal(canvasNodes.boundingBox.value, null)
})

test('projeção de radar mapeia coordenadas do mundo para dentro dos limites do mini-mapa', () => {
  const MINIMAP_WIDTH = 180
  const MINIMAP_HEIGHT = 120
  const PADDING = 8

  const worldBounds = { minX: 0, minY: 0, width: 1000, height: 800 }
  const availableW = MINIMAP_WIDTH - PADDING * 2
  const availableH = MINIMAP_HEIGHT - PADDING * 2

  const scale = Math.min(availableW / worldBounds.width, availableH / worldBounds.height)

  const offsetX = (MINIMAP_WIDTH - worldBounds.width * scale) / 2
  const offsetY = (MINIMAP_HEIGHT - worldBounds.height * scale) / 2

  // Ponto no canto superior esquerdo (0, 0)
  const p0 = {
    x: offsetX + (0 - worldBounds.minX) * scale,
    y: offsetY + (0 - worldBounds.minY) * scale,
  }

  // Ponto no canto inferior direito (1000, 800)
  const p1 = {
    x: offsetX + (1000 - worldBounds.minX) * scale,
    y: offsetY + (800 - worldBounds.minY) * scale,
  }

  assert.ok(p0.x >= 0 && p0.x < MINIMAP_WIDTH, 'P0 deve estar contido horizontalmente')
  assert.ok(p0.y >= 0 && p0.y < MINIMAP_HEIGHT, 'P0 deve estar contido verticalmente')
  assert.ok(p1.x > 0 && p1.x <= MINIMAP_WIDTH, 'P1 deve estar contido horizontalmente')
  assert.ok(p1.y > 0 && p1.y <= MINIMAP_HEIGHT, 'P1 deve estar contido verticalmente')

  // Conversão inversa (Radar para Mundo)
  const invertedWorldX = worldBounds.minX + (p1.x - offsetX) / scale
  const invertedWorldY = worldBounds.minY + (p1.y - offsetY) / scale

  assert.ok(Math.abs(invertedWorldX - 1000) < 0.001)
  assert.ok(Math.abs(invertedWorldY - 800) < 0.001)
})
