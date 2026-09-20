import { ref, computed, watch, toValue } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import type { CanvasBoundingBox, CanvasViewportState } from '../types'

export interface UseCanvasViewportOptions {
  bookId: MaybeRefOrGetter<number>
  minZoom?: number
  maxZoom?: number
}

const DEFAULT_MIN_ZOOM = 0.25
const DEFAULT_MAX_ZOOM = 2.0

export function useCanvasViewport(options: UseCanvasViewportOptions) {
  const minZoom = options.minZoom ?? DEFAULT_MIN_ZOOM
  const maxZoom = options.maxZoom ?? DEFAULT_MAX_ZOOM

  const panX = ref(40)
  const panY = ref(40)
  const zoomLevel = ref(1.0)
  const isPanning = ref(false)
  const panStart = ref({ x: 0, y: 0 })

  function getStorageKey(id: number): string {
    return `caderno_canvas_viewport_${id}`
  }

  function loadViewport(id: number): void {
    if (typeof window === 'undefined' || !window.localStorage) return
    try {
      const raw = localStorage.getItem(getStorageKey(id))
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<CanvasViewportState>
        if (typeof parsed.pan_x === 'number' && Number.isFinite(parsed.pan_x)) {
          panX.value = parsed.pan_x
        }
        if (typeof parsed.pan_y === 'number' && Number.isFinite(parsed.pan_y)) {
          panY.value = parsed.pan_y
        }
        if (typeof parsed.zoom_level === 'number' && Number.isFinite(parsed.zoom_level)) {
          zoomLevel.value = Math.max(minZoom, Math.min(maxZoom, parsed.zoom_level))
        }
      }
    } catch {
      // Falha silenciosa de leitura de localStorage
    }
  }

  function saveViewport(id: number): void {
    if (typeof window === 'undefined' || !window.localStorage) return
    try {
      const state: CanvasViewportState = {
        pan_x: Math.round(panX.value * 10) / 10,
        pan_y: Math.round(panY.value * 10) / 10,
        zoom_level: Math.round(zoomLevel.value * 100) / 100,
      }
      localStorage.setItem(getStorageKey(id), JSON.stringify(state))
    } catch {
      // Falha silenciosa de escrita
    }
  }

  watch(
    () => toValue(options.bookId),
    (newBookId) => {
      if (newBookId) {
        loadViewport(newBookId)
      }
    },
    { immediate: true },
  )

  function screenToWorld(screenX: number, screenY: number): { x: number; y: number } {
    return {
      x: (screenX - panX.value) / zoomLevel.value,
      y: (screenY - panY.value) / zoomLevel.value,
    }
  }

  function worldToScreen(worldX: number, worldY: number): { x: number; y: number } {
    return {
      x: worldX * zoomLevel.value + panX.value,
      y: worldY * zoomLevel.value + panY.value,
    }
  }

  function zoomAt(screenPoint: { x: number; y: number }, targetZoom: number): void {
    const clampedZoom = Math.max(minZoom, Math.min(maxZoom, targetZoom))
    if (clampedZoom === zoomLevel.value) return

    const currentZoom = zoomLevel.value
    // Mantém invariante o ponto do mundo correspondente a screenPoint
    panX.value = screenPoint.x - (screenPoint.x - panX.value) * (clampedZoom / currentZoom)
    panY.value = screenPoint.y - (screenPoint.y - panY.value) * (clampedZoom / currentZoom)
    zoomLevel.value = clampedZoom

    saveViewport(toValue(options.bookId))
  }

  function zoomIn(centerPoint?: { x: number; y: number }): void {
    const center = centerPoint ?? { x: window?.innerWidth ? window.innerWidth / 2 : 400, y: window?.innerHeight ? window.innerHeight / 2 : 300 }
    const nextZoom = Math.round((zoomLevel.value + 0.15) * 100) / 100
    zoomAt(center, nextZoom)
  }

  function zoomOut(centerPoint?: { x: number; y: number }): void {
    const center = centerPoint ?? { x: window?.innerWidth ? window.innerWidth / 2 : 400, y: window?.innerHeight ? window.innerHeight / 2 : 300 }
    const nextZoom = Math.round((zoomLevel.value - 0.15) * 100) / 100
    zoomAt(center, nextZoom)
  }

  function resetView(): void {
    panX.value = 40
    panY.value = 40
    zoomLevel.value = 1.0
    saveViewport(toValue(options.bookId))
  }

  function fitToView(box: CanvasBoundingBox | null, viewportWidth: number, viewportHeight: number): void {
    if (!box || !Number.isFinite(box.width) || !Number.isFinite(box.height) || box.width <= 0 || box.height <= 0) {
      resetView()
      return
    }

    const margin = 80
    const availableWidth = Math.max(100, viewportWidth - margin * 2)
    const availableHeight = Math.max(100, viewportHeight - margin * 2)

    const scaleX = availableWidth / box.width
    const scaleY = availableHeight / box.height
    const computedZoom = Math.max(minZoom, Math.min(1.0, Math.min(scaleX, scaleY)))

    const boxCenterX = (box.min_x + box.max_x) / 2
    const boxCenterY = (box.min_y + box.max_y) / 2

    zoomLevel.value = Math.round(computedZoom * 100) / 100
    panX.value = Math.round((viewportWidth / 2 - boxCenterX * zoomLevel.value) * 10) / 10
    panY.value = Math.round((viewportHeight / 2 - boxCenterY * zoomLevel.value) * 10) / 10

    saveViewport(toValue(options.bookId))
  }

  function startPan(screenX: number, screenY: number): void {
    isPanning.value = true
    panStart.value = {
      x: screenX - panX.value,
      y: screenY - panY.value,
    }
  }

  function updatePan(screenX: number, screenY: number): void {
    if (!isPanning.value) return
    panX.value = screenX - panStart.value.x
    panY.value = screenY - panStart.value.y
  }

  function endPan(): void {
    if (isPanning.value) {
      isPanning.value = false
      saveViewport(toValue(options.bookId))
    }
  }

  // --- Gestos Multitoque (Pinch-to-Zoom e Pan Tátil com 2 dedos) ---
  const activePointers = new Map<number, { x: number; y: number }>()
  let initialPinchDistance: number | null = null
  let initialPinchZoom = 1.0

  function handlePointerDown(pointerId: number, x: number, y: number): void {
    activePointers.set(pointerId, { x, y })
    if (activePointers.size === 1) {
      startPan(x, y)
    } else if (activePointers.size === 2) {
      isPanning.value = false
      const [p1, p2] = Array.from(activePointers.values())
      initialPinchDistance = Math.hypot(p2.x - p1.x, p2.y - p1.y)
      initialPinchZoom = zoomLevel.value
    }
  }

  function handlePointerMove(pointerId: number, x: number, y: number): void {
    if (!activePointers.has(pointerId)) return
    activePointers.set(pointerId, { x, y })

    if (activePointers.size === 1 && isPanning.value) {
      updatePan(x, y)
    } else if (activePointers.size === 2 && initialPinchDistance && initialPinchDistance > 10) {
      const [p1, p2] = Array.from(activePointers.values())
      const currentDist = Math.hypot(p2.x - p1.x, p2.y - p1.y)
      const factor = currentDist / initialPinchDistance
      const center = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 }
      zoomAt(center, initialPinchZoom * factor)
    }
  }

  function handlePointerUp(pointerId: number): void {
    activePointers.delete(pointerId)
    if (activePointers.size === 0) {
      endPan()
      initialPinchDistance = null
    } else if (activePointers.size === 1) {
      initialPinchDistance = null
      const [remaining] = Array.from(activePointers.values())
      startPan(remaining.x, remaining.y)
    }
  }

  const transformStyle = computed(() => ({
    transform: `translate3d(${panX.value}px, ${panY.value}px, 0) scale(${zoomLevel.value})`,
    transformOrigin: '0 0',
  }))

  return {
    panX,
    panY,
    zoomLevel,
    isPanning,
    transformStyle,
    screenToWorld,
    worldToScreen,
    zoomAt,
    zoomIn,
    zoomOut,
    resetView,
    fitToView,
    startPan,
    updatePan,
    endPan,
    handlePointerDown,
    handlePointerMove,
    handlePointerUp,
    saveViewport,
    loadViewport,
  }
}
