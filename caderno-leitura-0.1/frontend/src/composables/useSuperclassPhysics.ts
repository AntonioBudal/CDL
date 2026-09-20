/**
 * useSuperclassPhysics.ts
 * Motor de física inercial, amortecimento elástico e aceleração gráfica das Superclasses (F10).
 * Integração com as 5 Superclasses (Zero-G, Mecânica, Invisível, Dimensional, Monolítica),
 * suporte a prefers-reduced-motion, detecção tátil e feedback háptico visual de 80ms.
 */

import { computed, getCurrentInstance, onUnmounted, ref, type ComputedRef, type Ref } from 'vue'
import type { KinematicProfile } from '../types.ts'

export const SUPERCLASS_KINEMATIC_PROFILES: Record<string, KinematicProfile> = {
  'zero-g': {
    name: 'zero-g',
    friction: 0.96,
    springStiffness: 0.05,
    snapGridSize: 0,
    parallaxFactor: 1.0,
    revealDistance: 0,
    hapticStyle: 'smooth',
  },
  'mecanica': {
    name: 'mecanica',
    friction: 0.82,
    springStiffness: 0.28,
    snapGridSize: 20,
    parallaxFactor: 0.0,
    revealDistance: 0,
    hapticStyle: 'snap',
  },
  'invisivel': {
    name: 'invisivel',
    friction: 0.90,
    springStiffness: 0.10,
    snapGridSize: 0,
    parallaxFactor: 0.2,
    revealDistance: 140,
    hapticStyle: 'subtle',
  },
  'dimensional': {
    name: 'dimensional',
    friction: 0.92,
    springStiffness: 0.12,
    snapGridSize: 0,
    parallaxFactor: 1.6,
    revealDistance: 0,
    hapticStyle: 'subtle',
  },
  'monolitica': {
    name: 'monolitica',
    friction: 0.0,
    springStiffness: 1.0,
    snapGridSize: 0,
    parallaxFactor: 0.0,
    revealDistance: 0,
    hapticStyle: 'none',
  },
}

export interface UseSuperclassPhysicsOptions {
  activeSuperclass?: Ref<string> | ComputedRef<string>
  intensity?: Ref<number> | ComputedRef<number>
  prefersReducedMotion?: Ref<boolean> | ComputedRef<boolean>
  isTouchDevice?: Ref<boolean> | ComputedRef<boolean>
}

export function useSuperclassPhysics(options: UseSuperclassPhysicsOptions = {}) {
  // 1. Detecção reativa de Acessibilidade (prefers-reduced-motion)
  const internalReducedMotion = ref(false)
  const internalTouchDevice = ref(false)

  let motionMediaQuery: MediaQueryList | null = null
  let touchMediaQuery: MediaQueryList | null = null

  function handleMotionChange(e: MediaQueryListEvent | MediaQueryList) {
    internalReducedMotion.value = e.matches
  }

  function handleTouchChange(e: MediaQueryListEvent | MediaQueryList) {
    internalTouchDevice.value = e.matches
  }

  if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
    motionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    internalReducedMotion.value = motionMediaQuery.matches
    if (typeof motionMediaQuery.addEventListener === 'function') {
      motionMediaQuery.addEventListener('change', handleMotionChange)
    }

    touchMediaQuery = window.matchMedia('(pointer: coarse)')
    internalTouchDevice.value = touchMediaQuery.matches
    if (typeof touchMediaQuery.addEventListener === 'function') {
      touchMediaQuery.addEventListener('change', handleTouchChange)
    }
  }

  const isReducedMotion = computed(() => {
    if (options.prefersReducedMotion !== undefined) {
      return options.prefersReducedMotion.value
    }
    return internalReducedMotion.value
  })

  const isTouchDevice = computed(() => {
    if (options.isTouchDevice !== undefined) {
      return options.isTouchDevice.value
    }
    return internalTouchDevice.value
  })

  // 2. Leitura da Superclasse ativa
  const superclassKey = computed(() => {
    if (options.activeSuperclass) {
      return options.activeSuperclass.value || 'zero-g'
    }
    if (typeof document !== 'undefined') {
      return document.documentElement.getAttribute('data-superclass') || 'zero-g'
    }
    return 'zero-g'
  })

  // 3. Leitura da Intensidade (0.0 a 1.0)
  const intensityValue = computed(() => {
    if (options.intensity !== undefined) {
      return Math.max(0, Math.min(1.5, options.intensity.value))
    }
    if (typeof document !== 'undefined') {
      const raw = document.documentElement.getAttribute('data-superclass-intensity')
      if (raw === 'off') return 0.0
      if (raw === 'subtle') return 0.5
      if (raw === 'high') return 1.5
      return 1.0
    }
    return 1.0
  })

  // 4. Perfil Cinemático Ativo
  const activeProfile = computed<KinematicProfile>(() => {
    const base = SUPERCLASS_KINEMATIC_PROFILES[superclassKey.value] || SUPERCLASS_KINEMATIC_PROFILES['zero-g']
    return { ...base }
  })

  // 5. Cálculo de Passo Inercial (desaceleração pós-soltar)
  function calculateInertialStep(
    current: { x: number; y: number },
    velocity: { vx: number; vy: number },
    deltaTime = 16.6
  ) {
    // Sob prefers-reduced-motion, intensidade zerada, touch device ou Monolítica (friction = 0), parada imediata
    if (isReducedMotion.value || intensityValue.value === 0 || activeProfile.value.friction === 0 || isTouchDevice.value) {
      return {
        nextPosition: { ...current },
        nextVelocity: { vx: 0, vy: 0 },
        isFinished: true,
      }
    }

    const normalizedDelta = Math.max(0.1, Math.min(3, deltaTime / 16.6))
    // Fricção ponderada pelo multiplicador de intensidade
    const baseFriction = activeProfile.value.friction
    const effectiveFriction = Math.pow(
      1 - (1 - baseFriction) / Math.max(0.2, intensityValue.value),
      normalizedDelta
    )

    const nextVx = velocity.vx * effectiveFriction
    const nextVy = velocity.vy * effectiveFriction

    const speed = Math.hypot(nextVx, nextVy)
    if (speed < 0.1) {
      return {
        nextPosition: { ...current },
        nextVelocity: { vx: 0, vy: 0 },
        isFinished: true,
      }
    }

    return {
      nextPosition: {
        x: current.x + nextVx * normalizedDelta,
        y: current.y + nextVy * normalizedDelta,
      },
      nextVelocity: { vx: nextVx, vy: nextVy },
      isFinished: false,
    }
  }

  // 6. Cálculo de Encaixe em Grade (Snap-to-Grid)
  function calculateSnapPosition(x: number, y: number, customGridSize?: number) {
    const gridSize = customGridSize ?? activeProfile.value.snapGridSize
    if (!gridSize || gridSize <= 1) {
      return { snappedX: x, snappedY: y, didSnap: false }
    }

    const snappedX = Math.round(x / gridSize) * gridSize
    const snappedY = Math.round(y / gridSize) * gridSize
    const didSnap = Math.abs(snappedX - x) > 0.01 || Math.abs(snappedY - y) > 0.01

    return { snappedX, snappedY, didSnap }
  }

  // 7. Micro-resposta Tátil e Feedback Háptico Visual (80ms)
  function triggerHapticPulse(
    element: HTMLElement | null,
    style?: 'snap' | 'connect' | 'step'
  ) {
    if (!element || isReducedMotion.value || intensityValue.value === 0) return
    const pulseStyle = style || activeProfile.value.hapticStyle || 'snap'

    element.setAttribute('data-haptic-pulse', pulseStyle)
    setTimeout(() => {
      if (element) {
        element.removeAttribute('data-haptic-pulse')
      }
    }, 80)
  }

  // 8. Verificação do Limiar de Aceleração Gráfica (≥ 60 nós)
  function shouldAccelerate(nodeCount: number, threshold = 60): boolean {
    return nodeCount >= threshold
  }

  // 9. Cálculo de Proximidade da Superclasse Invisível (raio 140px)
  function calculateProximityOpacity(
    cursorX: number,
    cursorY: number,
    itemX: number,
    itemY: number,
    maxDistance = 140
  ): number {
    if (superclassKey.value !== 'invisivel') return 1.0
    if (isReducedMotion.value || intensityValue.value === 0) return 1.0

    const dist = Math.hypot(cursorX - itemX, cursorY - itemY)
    if (dist >= maxDistance) return 0.15
    const factor = 1 - dist / maxDistance
    return 0.15 + factor * 0.85
  }

  // 10. Cálculo de Deslocamento de Paralaxe 2.5D (Dimensional)
  function calculateParallaxOffset(
    panX: number,
    panY: number,
    layerDepth = 1.0
  ): { x: number; y: number } {
    if (superclassKey.value !== 'dimensional') return { x: panX, y: panY }
    if (isReducedMotion.value || intensityValue.value === 0) return { x: panX, y: panY }

    const multiplier = activeProfile.value.parallaxFactor * intensityValue.value * layerDepth
    return {
      x: panX * multiplier,
      y: panY * multiplier,
    }
  }

  if (getCurrentInstance()) {
    onUnmounted(() => {
      if (motionMediaQuery && typeof motionMediaQuery.removeEventListener === 'function') {
        motionMediaQuery.removeEventListener('change', handleMotionChange)
      }
      if (touchMediaQuery && typeof touchMediaQuery.removeEventListener === 'function') {
        touchMediaQuery.removeEventListener('change', handleTouchChange)
      }
    })
  }

  return {
    activeProfile,
    isReducedMotion,
    isTouchDevice,
    intensityValue,
    superclassKey,
    calculateInertialStep,
    calculateSnapPosition,
    triggerHapticPulse,
    shouldAccelerate,
    calculateProximityOpacity,
    calculateParallaxOffset,
  }
}
