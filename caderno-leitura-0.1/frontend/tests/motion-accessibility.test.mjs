import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  useSuperclassPhysics,
} from '../src/composables/useSuperclassPhysics.ts'

test('prefers-reduced-motion: cancela inércia e colapsa movimento imediatamente', () => {
  const { calculateInertialStep } = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: true },
  })

  // Mesmo sob Zero-G (fricção 0.96) e alta velocidade inicial, deve parar imediatamente
  const step = calculateInertialStep({ x: 100, y: 100 }, { vx: 50, vy: 50 }, 16.6)
  assert.equal(step.isFinished, true)
  assert.equal(step.nextPosition.x, 100)
  assert.equal(step.nextPosition.y, 100)
  assert.equal(step.nextVelocity.vx, 0)
  assert.equal(step.nextVelocity.vy, 0)
})

test('prefers-reduced-motion: desativa efeito de proximidade de Invisível (opacidade fixa 1.0)', () => {
  const { calculateProximityOpacity } = useSuperclassPhysics({
    activeSuperclass: { value: 'invisivel' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: true },
  })

  // Longe do cursor (distância 500px), a opacidade deve permanecer 1.0
  const opacity = calculateProximityOpacity(0, 0, 500, 500)
  assert.equal(opacity, 1.0)
})

test('prefers-reduced-motion: desativa deslocamento de paralaxe 2.5D de Dimensional', () => {
  const { calculateParallaxOffset } = useSuperclassPhysics({
    activeSuperclass: { value: 'dimensional' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: true },
  })

  const offset = calculateParallaxOffset(100, 200, 1.5)
  assert.equal(offset.x, 100)
  assert.equal(offset.y, 200)
})

test('isTouchDevice: anula loops de física inercial após soltura em telas táteis móveis', () => {
  const { calculateInertialStep } = useSuperclassPhysics({
    activeSuperclass: { value: 'zero-g' },
    intensity: { value: 1.0 },
    prefersReducedMotion: { value: false },
    isTouchDevice: { value: true },
  })

  const step = calculateInertialStep({ x: 40, y: 40 }, { vx: 15, vy: 15 }, 16.6)
  assert.equal(step.isFinished, true)
  assert.equal(step.nextPosition.x, 40)
  assert.equal(step.nextPosition.y, 40)
})

test('StudyView.vue mantém blindagem estática de leitura e ausência de camadas aceleradas', () => {
  const studyViewPath = path.resolve(process.cwd(), 'src/views/StudyView.vue')
  const content = fs.readFileSync(studyViewPath, 'utf8')

  // Verifica marcação de superfície estática de leitura
  assert.ok(content.includes('reader-static-surface'), 'StudyView deve possuir a classe reader-static-surface')

  // Garante ausência de CanvasAcceleratedLayer em telas de leitura para evitar ruído cognitivo
  assert.ok(!content.includes('CanvasAcceleratedLayer'), 'StudyView não deve instanciar camada de aceleração gráfica')
  assert.ok(!content.includes('CanvasConnectionsLayer'), 'StudyView não deve instanciar conexões móveis')
})

test('physics.css define anuladores globais sob @media (prefers-reduced-motion)', () => {
  const cssPath = path.resolve(process.cwd(), 'src/styles/superclasses/physics.css')
  const content = fs.readFileSync(cssPath, 'utf8')

  assert.ok(content.includes('@media (prefers-reduced-motion: reduce)'))
  assert.ok(content.includes('--sc-physics-friction: 0.0 !important'))
  assert.ok(content.includes('--sc-spring-stiffness: 1.0 !important'))
  assert.ok(content.includes('animation: none !important'))
})
