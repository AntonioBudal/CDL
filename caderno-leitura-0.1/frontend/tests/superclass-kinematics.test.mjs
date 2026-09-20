import test from 'node:test'
import assert from 'node:assert/strict'
import {
  SUPERCLASS_KINEMATIC_PROFILES,
  useSuperclassPhysics,
} from '../src/composables/useSuperclassPhysics.ts'

test('SUPERCLASS_KINEMATIC_PROFILES define exatamente as 5 superclasses canônicas', () => {
  const keys = Object.keys(SUPERCLASS_KINEMATIC_PROFILES)
  assert.deepEqual(keys.sort(), ['dimensional', 'invisivel', 'mecanica', 'monolitica', 'zero-g'])
})

test('Zero-G possui baixa desaceleração (fricção 0.96) e deslocamento contínuo sem grade', () => {
  const profile = SUPERCLASS_KINEMATIC_PROFILES['zero-g']
  assert.equal(profile.name, 'zero-g')
  assert.equal(profile.friction, 0.96)
  assert.equal(profile.snapGridSize, 0)
  assert.equal(profile.hapticStyle, 'smooth')

  const { calculateInertialStep } = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 1.0 },
  })

  const step = calculateInertialStep({ x: 100, y: 100 }, { vx: 10, vy: 5 }, 16.6)
  assert.equal(step.isFinished, false)
  assert.ok(step.nextPosition.x > 100)
  assert.ok(step.nextVelocity.vx < 10 && step.nextVelocity.vx > 8)
})

test('Mecânica aplica passo de grade de 20px e amortecimento elástico rápido', () => {
  const profile = SUPERCLASS_KINEMATIC_PROFILES['mecanica']
  assert.equal(profile.name, 'mecanica')
  assert.equal(profile.friction, 0.82)
  assert.equal(profile.snapGridSize, 20)
  assert.equal(profile.hapticStyle, 'snap')

  const { calculateSnapPosition } = useSuperclassPhysics({
    activeSuperclass: { value: 'mecanica' },
    intensity: { value: 1.0 },
  })

  const snap1 = calculateSnapPosition(27, 44)
  assert.equal(snap1.snappedX, 20)
  assert.equal(snap1.snappedY, 40)
  assert.equal(snap1.didSnap, true)

  const snap2 = calculateSnapPosition(40, 60)
  assert.equal(snap2.snappedX, 40)
  assert.equal(snap2.snappedY, 60)
  assert.equal(snap2.didSnap, false)
})

test('Invisível calcula raio de proximidade de 140px e opacidade progressiva', () => {
  const profile = SUPERCLASS_KINEMATIC_PROFILES['invisivel']
  assert.equal(profile.name, 'invisivel')
  assert.equal(profile.revealDistance, 140)
  assert.equal(profile.hapticStyle, 'subtle')

  const { calculateProximityOpacity } = useSuperclassPhysics({
    activeSuperclass: { value: 'invisivel' },
    intensity: { value: 1.0 },
  })

  // Distância zero: opacidade máxima (1.0)
  const opMax = calculateProximityOpacity(100, 100, 100, 100, 140)
  assert.equal(opMax, 1.0)

  // Distância além do raio: opacidade de repouso (0.15)
  const opMin = calculateProximityOpacity(0, 0, 200, 200, 140)
  assert.equal(opMin, 0.15)

  // Distância intermediária
  const opMid = calculateProximityOpacity(0, 0, 70, 0, 140)
  assert.ok(opMid > 0.15 && opMid < 1.0)
})

test('Dimensional calcula fator de paralaxe 2.5D proporcional de 1.6', () => {
  const profile = SUPERCLASS_KINEMATIC_PROFILES['dimensional']
  assert.equal(profile.name, 'dimensional')
  assert.equal(profile.parallaxFactor, 1.6)

  const { calculateParallaxOffset } = useSuperclassPhysics({
    activeSuperclass: { value: 'dimensional' },
    intensity: { value: 1.0 },
  })

  const offset = calculateParallaxOffset(50, 25, 1.0)
  assert.equal(offset.x, 80) // 50 * 1.6
  assert.equal(offset.y, 40) // 25 * 1.6
})

test('Monolítica interrompe movimento instantaneamente sem oscilação elástica', () => {
  const profile = SUPERCLASS_KINEMATIC_PROFILES['monolitica']
  assert.equal(profile.name, 'monolitica')
  assert.equal(profile.friction, 0.0)
  assert.equal(profile.hapticStyle, 'none')

  const { calculateInertialStep } = useSuperclassPhysics({
    activeSuperclass: { value: 'monolitica' },
    intensity: { value: 1.0 },
  })

  const step = calculateInertialStep({ x: 100, y: 100 }, { vx: 20, vy: 15 }, 16.6)
  assert.equal(step.isFinished, true)
  assert.equal(step.nextPosition.x, 100)
  assert.equal(step.nextPosition.y, 100)
  assert.equal(step.nextVelocity.vx, 0)
  assert.equal(step.nextVelocity.vy, 0)
})
