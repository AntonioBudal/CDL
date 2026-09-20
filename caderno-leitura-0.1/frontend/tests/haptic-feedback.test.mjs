import test from 'node:test'
import assert from 'node:assert/strict'
import {
  useSuperclassPhysics,
} from '../src/composables/useSuperclassPhysics.ts'

// Mock simples de elemento DOM para testes no Node
function createMockElement() {
  const attributes = new Map()
  return {
    setAttribute(name, value) {
      attributes.set(name, String(value))
    },
    removeAttribute(name) {
      attributes.delete(name)
    },
    getAttribute(name) {
      return attributes.get(name) ?? null
    },
    hasAttribute(name) {
      return attributes.has(name)
    },
  }
}

test('triggerHapticPulse aplica data-haptic-pulse e programa remoção após 80ms', async () => {
  const el = createMockElement()
  const { triggerHapticPulse } = useSuperclassPhysics({
    activeSuperclass: { value: 'mecanica' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: false },
  })

  triggerHapticPulse(el, 'snap')
  assert.equal(el.getAttribute('data-haptic-pulse'), 'snap')

  // Aguarda passar 85ms para conferir remoção do pulso
  await new Promise(resolve => setTimeout(resolve, 90))
  assert.equal(el.hasAttribute('data-haptic-pulse'), false)
})

test('triggerHapticPulse não injeta atributo se intensidade estiver zerada (0%)', () => {
  const el = createMockElement()
  const { triggerHapticPulse } = useSuperclassPhysics({
    activeSuperclass: { value: 'mecanica' },
    intensity: { value: 0 },
    prefersReducedMotion: { value: false },
  })

  triggerHapticPulse(el, 'snap')
  assert.equal(el.hasAttribute('data-haptic-pulse'), false)
})

test('triggerHapticPulse não injeta atributo sob prefersReducedMotion ativo', () => {
  const el = createMockElement()
  const { triggerHapticPulse } = useSuperclassPhysics({
    activeSuperclass: { value: 'mecanica' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: true },
  })

  triggerHapticPulse(el, 'step')
  assert.equal(el.hasAttribute('data-haptic-pulse'), false)
})

test('Colapso mecânico imediato com intensidade 0% (inércia abortada)', () => {
  const { calculateInertialStep } = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 0 },
    prefersReducedMotion: { value: false },
  })

  const step = calculateInertialStep({ x: 50, y: 50 }, { vx: 20, vy: 15 }, 16.6)
  assert.equal(step.isFinished, true)
  assert.equal(step.nextPosition.x, 50)
  assert.equal(step.nextPosition.y, 50)
  assert.equal(step.nextVelocity.vx, 0)
  assert.equal(step.nextVelocity.vy, 0)
})

test('Escalonamento paramétrico de intensidade modula velocidade e deslocamento', () => {
  const physicsFull = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: false },
  })

  const physicsHalf = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 0.5 },
    prefersReducedMotion: { value: false },
  })

  const stepFull = physicsFull.calculateInertialStep({ x: 0, y: 0 }, { vx: 10, vy: 0 }, 16.6)
  const stepHalf = physicsHalf.calculateInertialStep({ x: 0, y: 0 }, { vx: 10, vy: 0 }, 16.6)

  assert.equal(stepFull.isFinished, false)
  assert.equal(stepHalf.isFinished, false)
  // Com intensidade 0.5, o deslocamento é proporcionalmente atenuado
  assert.ok(stepHalf.nextPosition.x < stepFull.nextPosition.x)
  assert.ok(stepHalf.nextPosition.x > 0)
})
