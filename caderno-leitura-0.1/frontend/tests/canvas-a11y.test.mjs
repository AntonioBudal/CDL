import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

const { useCanvasViewport } = await import('../src/composables/useCanvasViewport.ts')

test('handlePointerDown, handlePointerMove e handlePointerUp operam pan com 1 ponteiro', () => {
  const bookId = ref(20)
  const viewport = useCanvasViewport({ bookId })

  // Pressionar 1 ponteiro na tela
  viewport.handlePointerDown(1, 100, 100)
  assert.equal(viewport.isPanning.value, true)

  // Mover ponteiro
  viewport.handlePointerMove(1, 160, 140)
  assert.equal(viewport.panX.value, 40 + (160 - 100))
  assert.equal(viewport.panY.value, 40 + (140 - 100))

  // Soltar ponteiro
  viewport.handlePointerUp(1)
  assert.equal(viewport.isPanning.value, false)
})

test('gesto de pinça com 2 ponteiros executa zoom contínuo proporcional à distância', () => {
  const bookId = ref(21)
  const viewport = useCanvasViewport({ bookId })

  viewport.zoomLevel.value = 1.0

  // Dois dedos tocam a tela separados por 100px: (200, 300) e (300, 300)
  viewport.handlePointerDown(1, 200, 300)
  viewport.handlePointerDown(2, 300, 300)

  assert.equal(viewport.isPanning.value, false, 'Pan deve ser desativado durante pinça com 2 dedos')

  // Afasta os dedos para 200px (duplica a distância): (150, 300) e (350, 300)
  viewport.handlePointerMove(1, 150, 300)
  viewport.handlePointerMove(2, 350, 300)

  // O zoom deve ter aumentado (fator ~2.0)
  assert.ok(viewport.zoomLevel.value > 1.5, `Zoom deve aumentar após afastar os dedos, atual: ${viewport.zoomLevel.value}`)

  // Soltar os dois dedos
  viewport.handlePointerUp(1)
  viewport.handlePointerUp(2)
})

test('atalho de teclado com Shift desloca coordenadas do card em passos exatos', () => {
  const node = {
    x: 100,
    y: 100,
  }

  function simulateShiftMove(key, isCtrl) {
    const step = isCtrl ? 50 : 20
    if (key === 'ArrowUp') node.y -= step
    if (key === 'ArrowDown') node.y += step
    if (key === 'ArrowLeft') node.x -= step
    if (key === 'ArrowRight') node.x += step
  }

  simulateShiftMove('ArrowRight', false)
  assert.equal(node.x, 120)

  simulateShiftMove('ArrowDown', false)
  assert.equal(node.y, 120)

  simulateShiftMove('ArrowLeft', true) // Com Ctrl: 50px
  assert.equal(node.x, 70)

  simulateShiftMove('ArrowUp', true) // Com Ctrl: 50px
  assert.equal(node.y, 70)
})
