import test from 'node:test'
import assert from 'node:assert/strict'

const {
  computeSmartSnapping,
  useSmartSnapping,
  DEFAULT_SNAP_THRESHOLD,
} = await import('../src/composables/useSmartSnapping.ts')

test('computeSmartSnapping retorna posição original sem guias se não houver outros retângulos', () => {
  const dragging = { x: 50, y: 100, width: 200, height: 120, id: 1 }
  const result = computeSmartSnapping(dragging, [])

  assert.equal(result.x, 50)
  assert.equal(result.y, 100)
  assert.equal(result.guides.length, 0)
})

test('computeSmartSnapping ignora o próprio retângulo pelo id', () => {
  const dragging = { x: 50, y: 100, width: 200, height: 120, id: 1 }
  const others = [{ x: 52, y: 102, width: 200, height: 120, id: 1 }]
  const result = computeSmartSnapping(dragging, others)

  assert.equal(result.x, 50)
  assert.equal(result.y, 100)
  assert.equal(result.guides.length, 0)
})

test('computeSmartSnapping atrai borda esquerda para borda esquerda vizinha dentro de 10px', () => {
  const dragging = { x: 105, y: 300, width: 200, height: 120, id: 1 }
  const others = [{ x: 100, y: 100, width: 200, height: 120, id: 2 }]

  // Distância = 5px <= 10px -> deve atrair para x = 100
  const result = computeSmartSnapping(dragging, others)

  assert.equal(result.x, 100)
  assert.equal(result.guides.length, 1)
  assert.equal(result.guides[0].type, 'vertical')
  assert.equal(result.guides[0].coordinate, 100)
})

test('computeSmartSnapping atrai centros horizontais e verticais simultaneamente', () => {
  // dragging center: (204 + 100 = 304, 303 + 50 = 353)
  // other center: (100 + 200 = 300, 150 + 200 = 350)
  // deltaX = 300 - 304 = -4 -> snap para x = 200
  // deltaY = 350 - 353 = -3 -> snap para y = 300
  const dragging = { x: 204, y: 303, width: 200, height: 100, id: 1 }
  const others = [{ x: 100, y: 150, width: 400, height: 400, id: 2 }]

  const result = computeSmartSnapping(dragging, others)

  assert.equal(result.x, 200)
  assert.equal(result.y, 300)
  assert.equal(result.guides.length, 2)
  const vGuide = result.guides.find(g => g.type === 'vertical')
  const hGuide = result.guides.find(g => g.type === 'horizontal')
  assert.ok(vGuide)
  assert.ok(hGuide)
  assert.equal(vGuide.coordinate, 300)
  assert.equal(hGuide.coordinate, 350)
})

test('computeSmartSnapping não atrai se a distância for maior que o threshold', () => {
  const dragging = { x: 115, y: 300, width: 200, height: 120, id: 1 }
  const others = [{ x: 100, y: 100, width: 200, height: 120, id: 2 }]

  // Distância = 15px > 10px -> não atrai
  const result = computeSmartSnapping(dragging, others)

  assert.equal(result.x, 115)
  assert.equal(result.y, 300)
  assert.equal(result.guides.length, 0)
})

test('useSmartSnapping gerencia estado reativo de guias e limpeza', () => {
  const { activeGuides, snapPosition, clearGuides } = useSmartSnapping()

  assert.equal(activeGuides.value.length, 0)

  const dragging = { x: 104, y: 200, width: 200, height: 100, id: 1 }
  const others = [{ x: 100, y: 50, width: 200, height: 100, id: 2 }]

  const snapped = snapPosition(dragging, others)
  assert.equal(snapped.x, 100)
  assert.equal(activeGuides.value.length, 1)

  clearGuides()
  assert.equal(activeGuides.value.length, 0)
})
