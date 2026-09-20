import { ref, computed } from 'vue'
import type { CanvasPositionedCard } from '../types'

export function isRectIntersecting(
  r1: { x: number; y: number; width: number; height: number },
  r2: { x: number; y: number; width: number; height: number },
): boolean {
  return !(
    r2.x > r1.x + r1.width ||
    r2.x + r2.width < r1.x ||
    r2.y > r1.y + r1.height ||
    r2.y + r2.height < r1.y
  )
}

export function useCanvasSelection() {
  const selectedIds = ref<Set<number>>(new Set())
  const isMarqueeSelecting = ref(false)
  const marqueeStartScreen = ref({ x: 0, y: 0 })
  const marqueeCurrentScreen = ref({ x: 0, y: 0 })

  function selectNode(studyId: number, isMulti = false): void {
    if (isMulti) {
      const next = new Set(selectedIds.value)
      if (next.has(studyId)) {
        next.delete(studyId)
      } else {
        next.add(studyId)
      }
      selectedIds.value = next
    } else {
      selectedIds.value = new Set([studyId])
    }
  }

  function clearSelection(): void {
    selectedIds.value = new Set()
  }

  function selectAll(ids: number[]): void {
    selectedIds.value = new Set(ids)
  }

  function startMarquee(screenX: number, screenY: number, append = false): void {
    isMarqueeSelecting.value = true
    marqueeStartScreen.value = { x: screenX, y: screenY }
    marqueeCurrentScreen.value = { x: screenX, y: screenY }
    if (!append) {
      selectedIds.value = new Set()
    }
  }

  function updateMarquee(
    screenX: number,
    screenY: number,
    nodes: Map<number, CanvasPositionedCard>,
    screenToWorld: (x: number, y: number) => { x: number; y: number },
  ): void {
    if (!isMarqueeSelecting.value) return
    marqueeCurrentScreen.value = { x: screenX, y: screenY }

    const screenMinX = Math.min(marqueeStartScreen.value.x, screenX)
    const screenMinY = Math.min(marqueeStartScreen.value.y, screenY)
    const screenMaxX = Math.max(marqueeStartScreen.value.x, screenX)
    const screenMaxY = Math.max(marqueeStartScreen.value.y, screenY)

    const worldTopLeft = screenToWorld(screenMinX, screenMinY)
    const worldBottomRight = screenToWorld(screenMaxX, screenMaxY)

    const marqueeWorldRect = {
      x: worldTopLeft.x,
      y: worldTopLeft.y,
      width: Math.max(1, worldBottomRight.x - worldTopLeft.x),
      height: Math.max(1, worldBottomRight.y - worldTopLeft.y),
    }

    const nextSelected = new Set<number>()
    for (const node of nodes.values()) {
      const nodeRect = {
        x: node.x,
        y: node.y,
        width: node.width ?? 280,
        height: node.height ?? 200,
      }
      if (isRectIntersecting(marqueeWorldRect, nodeRect)) {
        nextSelected.add(node.study_id)
      }
    }

    selectedIds.value = nextSelected
  }

  function endMarquee(): void {
    isMarqueeSelecting.value = false
  }

  const marqueeStyle = computed(() => {
    if (!isMarqueeSelecting.value) return { display: 'none' }

    const minX = Math.min(marqueeStartScreen.value.x, marqueeCurrentScreen.value.x)
    const minY = Math.min(marqueeStartScreen.value.y, marqueeCurrentScreen.value.y)
    const width = Math.abs(marqueeCurrentScreen.value.x - marqueeStartScreen.value.x)
    const height = Math.abs(marqueeCurrentScreen.value.y - marqueeStartScreen.value.y)

    return {
      left: `${minX}px`,
      top: `${minY}px`,
      width: `${width}px`,
      height: `${height}px`,
    }
  })

  return {
    selectedIds,
    isMarqueeSelecting,
    marqueeStyle,
    selectNode,
    clearSelection,
    selectAll,
    startMarquee,
    updateMarquee,
    endMarquee,
  }
}
