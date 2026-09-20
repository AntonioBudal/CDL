import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

// Mock simples de localStorage
class LocalStorageMock {
  constructor() {
    this.store = new Map()
  }
  getItem(key) {
    return this.store.get(key) || null
  }
  setItem(key, value) {
    this.store.set(key, String(value))
  }
  removeItem(key) {
    this.store.delete(key)
  }
  clear() {
    this.store.clear()
  }
}

globalThis.localStorage = new LocalStorageMock()
globalThis.window = {
  localStorage: globalThis.localStorage,
  innerWidth: 1200,
  innerHeight: 800,
}

const { useCanvasViewport } = await import('../src/composables/useCanvasViewport.ts')

test('useCanvasViewport inicializa com pan padrão e zoom 1.0', () => {
  const bookId = ref(10)
  const viewport = useCanvasViewport({ bookId })

  assert.equal(viewport.panX.value, 40)
  assert.equal(viewport.panY.value, 40)
  assert.equal(viewport.zoomLevel.value, 1.0)
})

test('screenToWorld e worldToScreen são funções inversas exatas', () => {
  const bookId = ref(11)
  const viewport = useCanvasViewport({ bookId })

  viewport.panX.value = 100
  viewport.panY.value = 50
  viewport.zoomLevel.value = 1.5

  const originalWorld = { x: 250, y: 180 }
  const screen = viewport.worldToScreen(originalWorld.x, originalWorld.y)

  assert.equal(screen.x, 250 * 1.5 + 100)
  assert.equal(screen.y, 180 * 1.5 + 50)

  const backWorld = viewport.screenToWorld(screen.x, screen.y)
  assert.ok(Math.abs(backWorld.x - originalWorld.x) < 0.001)
  assert.ok(Math.abs(backWorld.y - originalWorld.y) < 0.001)
})

test('zoomAt aplica clamping entre minZoom (0.25) e maxZoom (2.0)', () => {
  const bookId = ref(12)
  const viewport = useCanvasViewport({ bookId, minZoom: 0.25, maxZoom: 2.0 })

  viewport.zoomAt({ x: 400, y: 300 }, 3.5)
  assert.equal(viewport.zoomLevel.value, 2.0, 'Não deve exceder maxZoom de 2.0')

  viewport.zoomAt({ x: 400, y: 300 }, 0.1)
  assert.equal(viewport.zoomLevel.value, 0.25, 'Não deve ficar abaixo de minZoom de 0.25')
})

test('zoomAt mantém invariante o ponto do mundo correspondente ao cursor', () => {
  const bookId = ref(13)
  const viewport = useCanvasViewport({ bookId })

  const cursorScreen = { x: 500, y: 300 }
  const worldBefore = viewport.screenToWorld(cursorScreen.x, cursorScreen.y)

  viewport.zoomAt(cursorScreen, 1.5)

  const worldAfter = viewport.screenToWorld(cursorScreen.x, cursorScreen.y)
  assert.ok(Math.abs(worldAfter.x - worldBefore.x) < 0.001, 'Ponto X sob cursor deve ser invariante')
  assert.ok(Math.abs(worldAfter.y - worldBefore.y) < 0.001, 'Ponto Y sob cursor deve ser invariante')
})

test('fitToView centraliza e ajusta escala para conter bounding box', () => {
  const bookId = ref(14)
  const viewport = useCanvasViewport({ bookId })

  const boundingBox = {
    min_x: 0,
    min_y: 0,
    max_x: 1000,
    max_y: 600,
    width: 1000,
    height: 600,
  }

  viewport.fitToView(boundingBox, 1200, 800)

  assert.ok(viewport.zoomLevel.value <= 1.0, 'Escala não deve ser maior que 100% em fit to view')
  assert.ok(viewport.zoomLevel.value >= 0.25, 'Escala deve respeitar mínimo de 25%')

  // O centro do bounding box (500, 300) deve estar no centro da tela (600, 400)
  const centerScreen = viewport.worldToScreen(500, 300)
  assert.ok(Math.abs(centerScreen.x - 600) < 5, 'Centro X do conteúdo deve alinhar com centro da tela')
  assert.ok(Math.abs(centerScreen.y - 400) < 5, 'Centro Y do conteúdo deve alinhar com centro da tela')
})

test('startPan, updatePan e endPan deslocam o viewport corretamente', () => {
  const bookId = ref(15)
  const viewport = useCanvasViewport({ bookId })

  viewport.startPan(100, 100)
  assert.equal(viewport.isPanning.value, true)

  viewport.updatePan(150, 180)
  assert.equal(viewport.panX.value, 90) // 40 + (150 - 100)
  assert.equal(viewport.panY.value, 120) // 40 + (180 - 100)

  viewport.endPan()
  assert.equal(viewport.isPanning.value, false)

  // Persistência em localStorage
  const saved = JSON.parse(globalThis.localStorage.getItem('caderno_canvas_viewport_15'))
  assert.equal(saved.pan_x, 90)
  assert.equal(saved.pan_y, 120)
})
