import { ref } from 'vue'
import type { SnappingTarget, SmartGuide, SnappedPosition } from '../types.ts'

export const DEFAULT_SNAP_THRESHOLD = 10 // pixels de atração magnética

/**
 * Função pura determinística que calcula atração magnética para bordas e centros
 * de retângulos no espaço 2D, gerando as guias visuais correspondentes.
 */
export function computeSmartSnapping(
  draggingRect: SnappingTarget,
  otherRects: SnappingTarget[],
  threshold = DEFAULT_SNAP_THRESHOLD
): SnappedPosition {
  if (!otherRects || otherRects.length === 0) {
    return { x: draggingRect.x, y: draggingRect.y, guides: [] }
  }

  const { x, y, width, height } = draggingRect
  const centerX = x + width / 2
  const centerY = y + height / 2

  let bestDeltaX: number | null = null
  let minDiffX = threshold + 1
  let guideX: SmartGuide | null = null

  let bestDeltaY: number | null = null
  let minDiffY = threshold + 1
  let guideY: SmartGuide | null = null

  for (const other of otherRects) {
    // Ignora o próprio elemento que está sendo arrastado
    if (other.id !== undefined && draggingRect.id !== undefined && other.id === draggingRect.id) {
      continue
    }

    const ox = other.x
    const oy = other.y
    const ow = other.width
    const oh = other.height
    const ocx = ox + ow / 2
    const ocy = oy + oh / 2

    // -------------------------------------------------------------
    // Alinhamentos Verticais (Eixo X)
    // -------------------------------------------------------------
    const candidatesX: Array<{ delta: number; coord: number }> = [
      { delta: ox - x, coord: ox }, // Esquerda com Esquerda
      { delta: (ox + ow) - (x + width), coord: ox + ow }, // Direita com Direita
      { delta: ocx - centerX, coord: ocx }, // Centro com Centro
      { delta: (ox + ow) - x, coord: ox + ow }, // Esquerda com Direita vizinha
      { delta: ox - (x + width), coord: ox }, // Direita com Esquerda vizinha
    ]

    for (const c of candidatesX) {
      const diff = Math.abs(c.delta)
      if (diff <= threshold && diff < minDiffX) {
        minDiffX = diff
        bestDeltaX = c.delta
        guideX = {
          type: 'vertical',
          coordinate: c.coord,
          start: Math.min(y, oy) - 10,
          end: Math.max(y + height, oy + oh) + 10,
        }
      }
    }

    // -------------------------------------------------------------
    // Alinhamentos Horizontais (Eixo Y)
    // -------------------------------------------------------------
    const candidatesY: Array<{ delta: number; coord: number }> = [
      { delta: oy - y, coord: oy }, // Topo com Topo
      { delta: (oy + oh) - (y + height), coord: oy + oh }, // Fundo com Fundo
      { delta: ocy - centerY, coord: ocy }, // Centro com Centro
      { delta: (oy + oh) - y, coord: oy + oh }, // Topo com Fundo vizinho
      { delta: oy - (y + height), coord: oy }, // Fundo com Topo vizinho
    ]

    for (const c of candidatesY) {
      const diff = Math.abs(c.delta)
      if (diff <= threshold && diff < minDiffY) {
        minDiffY = diff
        bestDeltaY = c.delta
        guideY = {
          type: 'horizontal',
          coordinate: c.coord,
          start: Math.min(x, ox) - 10,
          end: Math.max(x + width, ox + ow) + 10,
        }
      }
    }
  }

  const finalX = bestDeltaX !== null ? Math.round(x + bestDeltaX) : x
  const finalY = bestDeltaY !== null ? Math.round(y + bestDeltaY) : y

  const guides: SmartGuide[] = []
  if (guideX) guides.push(guideX)
  if (guideY) guides.push(guideY)

  return {
    x: finalX,
    y: finalY,
    guides,
  }
}

/**
 * Composable reativo para gerenciar guias magnéticas de arrasto no Canvas
 */
export function useSmartSnapping(options?: { threshold?: number }) {
  const activeGuides = ref<SmartGuide[]>([])

  function snapPosition(
    draggingRect: SnappingTarget,
    otherRects: SnappingTarget[]
  ): { x: number; y: number } {
    const res = computeSmartSnapping(draggingRect, otherRects, options?.threshold ?? DEFAULT_SNAP_THRESHOLD)
    activeGuides.value = res.guides
    return { x: res.x, y: res.y }
  }

  function clearGuides() {
    activeGuides.value = []
  }

  return {
    activeGuides,
    snapPosition,
    clearGuides,
  }
}
