import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

const {
  computeAutoGridPositions,
  useCanvasNodes,
  CARD_WIDTH,
  CARD_HEIGHT,
  GRID_GAP,
  COLS_PER_CHAPTER,
} = await import('../src/composables/useCanvasNodes.ts')

const {
  useCanvasSelection,
  isRectIntersecting,
} = await import('../src/composables/useCanvasSelection.ts')

// ==========================================
// 1. Testes de Auto-Grid
// ==========================================

test('computeAutoGridPositions posiciona estudos não-persistidos em grade ordenada por capítulo', () => {
  const mockStudies = [
    { id: 1, chapter_id: 10, title: 'Estudo 1', location: '', parent_study_id: null, position: 0, created_at: '', updated_at: '' },
    { id: 2, chapter_id: 10, title: 'Estudo 2', location: '', parent_study_id: null, position: 1, created_at: '', updated_at: '' },
    { id: 3, chapter_id: 10, title: 'Estudo 3', location: '', parent_study_id: null, position: 2, created_at: '', updated_at: '' },
    { id: 4, chapter_id: 10, title: 'Estudo 4', location: '', parent_study_id: null, position: 3, created_at: '', updated_at: '' },
  ]

  const existingMap = new Map()
  const result = computeAutoGridPositions(mockStudies, existingMap)

  assert.equal(result.size, 4)

  const n1 = result.get(1)
  const n2 = result.get(2)
  const n3 = result.get(3)
  const n4 = result.get(4)

  // Coluna 0, Linha 0
  assert.equal(n1.x, 40)
  assert.equal(n1.y, 40)
  assert.equal(n1.is_persisted, false)

  // Coluna 1, Linha 0
  assert.equal(n2.x, 40 + 1 * (CARD_WIDTH + GRID_GAP))
  assert.equal(n2.y, 40)

  // Coluna 2, Linha 0
  assert.equal(n3.x, 40 + 2 * (CARD_WIDTH + GRID_GAP))
  assert.equal(n3.y, 40)

  // Coluna 0, Linha 1 (pois COLS_PER_CHAPTER = 3)
  assert.equal(n4.x, 40)
  assert.equal(n4.y, 40 + 1 * (CARD_HEIGHT + GRID_GAP))
})

test('computeAutoGridPositions preserva coordenadas de nós já persistidos', () => {
  const mockStudies = [
    { id: 1, chapter_id: 10, title: 'Estudo Salvo', location: '', parent_study_id: null, position: 0, created_at: '', updated_at: '' },
    { id: 2, chapter_id: 10, title: 'Estudo Novo', location: '', parent_study_id: null, position: 1, created_at: '', updated_at: '' },
  ]

  const existingMap = new Map([
    [1, { id: 100, study_id: 1, book_id: 5, pos_x: 750, pos_y: 320, width: 300, height: 210, z_index: 8, color_tag: 'emerald', updated_at: '' }]
  ])

  const result = computeAutoGridPositions(mockStudies, existingMap)

  const saved = result.get(1)
  assert.equal(saved.x, 750)
  assert.equal(saved.y, 320)
  assert.equal(saved.z_index, 8)
  assert.equal(saved.color_tag, 'emerald')
  assert.equal(saved.is_persisted, true)

  const unpersisted = result.get(2)
  assert.equal(unpersisted.is_persisted, false)
})

// ==========================================
// 2. Testes de Seleção e Marquee
// ==========================================

test('isRectIntersecting detecta sobreposição e descolamento entre retângulos', () => {
  const r1 = { x: 0, y: 0, width: 100, height: 100 }
  const r2 = { x: 50, y: 50, width: 100, height: 100 }
  const r3 = { x: 150, y: 150, width: 50, height: 50 }

  assert.equal(isRectIntersecting(r1, r2), true, 'r1 e r2 se sobrepõem')
  assert.equal(isRectIntersecting(r1, r3), false, 'r1 e r3 não se sobrepõem')
})

test('useCanvasSelection gerencia seleção simples e aditiva', () => {
  const sel = useCanvasSelection()

  sel.selectNode(1, false)
  assert.deepEqual(Array.from(sel.selectedIds.value), [1])

  sel.selectNode(2, true) // Aditiva
  assert.deepEqual(Array.from(sel.selectedIds.value).sort(), [1, 2])

  sel.selectNode(1, true) // Desmarca 1
  assert.deepEqual(Array.from(sel.selectedIds.value), [2])

  sel.selectNode(3, false) // Substitui por 3
  assert.deepEqual(Array.from(sel.selectedIds.value), [3])

  sel.clearSelection()
  assert.equal(sel.selectedIds.value.size, 0)
})

test('updateMarquee seleciona nós intersectados em coordenadas de mundo', () => {
  const sel = useCanvasSelection()

  const nodes = new Map([
    [1, { study_id: 1, x: 50, y: 50, width: 100, height: 100, z_index: 0, is_persisted: true }],
    [2, { study_id: 2, x: 300, y: 300, width: 100, height: 100, z_index: 0, is_persisted: true }],
  ])

  // Identidade de tela para mundo (zoom 1.0, pan 0)
  const screenToWorld = (x, y) => ({ x, y })

  sel.startMarquee(0, 0)
  sel.updateMarquee(120, 120, nodes, screenToWorld)

  assert.ok(sel.selectedIds.value.has(1), 'Estudo 1 deve ser selecionado')
  assert.ok(!sel.selectedIds.value.has(2), 'Estudo 2 não deve ser selecionado')
})

// ==========================================
// 3. Testes de Arrasto em Bloco
// ==========================================

test('startDragNode e updateDragNode movem múltiplos cards selecionados pelo mesmo delta', () => {
  const bookId = ref(1)
  const studies = ref([])
  const canvasNodes = useCanvasNodes({ bookId, studies })

  canvasNodes.positionedNodes.value = new Map([
    [1, { study_id: 1, x: 100, y: 100, width: 280, height: 200, z_index: 1, is_persisted: true }],
    [2, { study_id: 2, x: 450, y: 100, width: 280, height: 200, z_index: 2, is_persisted: true }],
  ])

  const selected = new Set([1, 2])

  // Iniciar arrasto a partir de tela (200, 200) com zoom 1.0
  canvasNodes.startDragNode(1, 200, 200, selected)
  assert.equal(canvasNodes.isDraggingNodes.value, true)

  // Deslocar 50px para direita e 30px para baixo
  canvasNodes.updateDragNode(250, 230, 1.0)

  const n1 = canvasNodes.positionedNodes.value.get(1)
  const n2 = canvasNodes.positionedNodes.value.get(2)

  assert.equal(n1.x, 150) // 100 + 50
  assert.equal(n1.y, 130) // 100 + 30
  assert.equal(n2.x, 500) // 450 + 50
  assert.equal(n2.y, 130) // 100 + 30

  // A distância relativa entre n1 e n2 (350px) permaneceu exatamente invariante!
  assert.equal(n2.x - n1.x, 350)
})
