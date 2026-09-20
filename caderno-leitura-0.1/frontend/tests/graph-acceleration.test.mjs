import test from 'node:test'
import assert from 'node:assert/strict'
import { useSuperclassPhysics } from '../src/composables/useSuperclassPhysics.ts'

test('shouldAccelerate retorna false para grafos leves com contagem de nós inferior a 60', () => {
  const { shouldAccelerate } = useSuperclassPhysics()

  assert.equal(shouldAccelerate(0), false)
  assert.equal(shouldAccelerate(15), false)
  assert.equal(shouldAccelerate(45), false)
  assert.equal(shouldAccelerate(59), false)
})

test('shouldAccelerate retorna true exatamente no limiar padrão de 60 nós visíveis', () => {
  const { shouldAccelerate } = useSuperclassPhysics()

  assert.equal(shouldAccelerate(60), true)
})

test('shouldAccelerate retorna true para grafos densos e volumosos', () => {
  const { shouldAccelerate } = useSuperclassPhysics()

  assert.equal(shouldAccelerate(100), true)
  assert.equal(shouldAccelerate(250), true)
  assert.equal(shouldAccelerate(1000), true)
})

test('shouldAccelerate aceita limiar customizado por parâmetro', () => {
  const { shouldAccelerate } = useSuperclassPhysics()

  assert.equal(shouldAccelerate(25, 30), false)
  assert.equal(shouldAccelerate(30, 30), true)
  assert.equal(shouldAccelerate(80, 100), false)
  assert.equal(shouldAccelerate(120, 100), true)
})

test('Projeção geométrica do viewport mapeia coordenadas para contexto 2D acelerado', () => {
  const viewport = { x: 100, y: 50, scale: 1.5 }

  function projectToCanvas(worldX, worldY, vp) {
    return {
      canvasX: (worldX + vp.x) * vp.scale,
      canvasY: (worldY + vp.y) * vp.scale,
    }
  }

  const proj = projectToCanvas(200, 100, viewport)
  assert.equal(proj.canvasX, (200 + 100) * 1.5) // 450
  assert.equal(proj.canvasY, (100 + 50) * 1.5) // 225
})
