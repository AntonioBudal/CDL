import test from 'node:test'
import assert from 'node:assert/strict'

import {
  getRectIntersection,
  computeConnectionGeometry,
} from '../src/composables/useCanvasConnections.ts'

test('getRectIntersection calcula ancoragem nas bordas de cards retangulares', () => {
  const rect = { x: 100, y: 100, width: 200, height: 100 }

  // Alvo diretamente à direita: borda direita x=300, y=150
  const ptRight = getRectIntersection(rect, { x: 500, y: 150 })
  assert.equal(ptRight.x, 300)
  assert.equal(ptRight.y, 150)

  // Alvo diretamente à esquerda: borda esquerda x=100, y=150
  const ptLeft = getRectIntersection(rect, { x: 0, y: 150 })
  assert.equal(ptLeft.x, 100)
  assert.equal(ptLeft.y, 150)

  // Alvo diretamente abaixo: borda inferior x=200, y=200
  const ptBottom = getRectIntersection(rect, { x: 200, y: 500 })
  assert.equal(ptBottom.x, 200)
  assert.equal(ptBottom.y, 200)
})

test('computeConnectionGeometry gera curva Bézier cúbica válida e coordenadas de badge', () => {
  const source = { x: 50, y: 50, width: 280, height: 200 }
  const target = { x: 500, y: 400, width: 280, height: 200 }

  const geom = computeConnectionGeometry(source, target)

  // O path deve ser uma curva Bézier com M e C
  assert.ok(geom.path.startsWith('M '), 'O path deve iniciar com comando de movimento M')
  assert.ok(geom.path.includes(' C '), 'O path deve conter comando de curva Bézier C')

  // O badge deve estar localizado entre o nó de origem e o nó de destino
  assert.ok(
    geom.badgeX > source.x && geom.badgeX < target.x + target.width,
    `badgeX (${geom.badgeX}) deve estar entre source e target`
  )
  assert.ok(
    geom.badgeY > source.y && geom.badgeY < target.y + target.height,
    `badgeY (${geom.badgeY}) deve estar entre source e target`
  )

  // Pontos de ancoragem
  assert.ok(Number.isFinite(geom.sourcePoint.x))
  assert.ok(Number.isFinite(geom.sourcePoint.y))
  assert.ok(Number.isFinite(geom.targetPoint.x))
  assert.ok(Number.isFinite(geom.targetPoint.y))
})
