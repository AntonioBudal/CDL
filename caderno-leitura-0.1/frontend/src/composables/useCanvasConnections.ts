import { ref } from 'vue'
import type { BookCanvasRelationItem, CanvasPositionedCard } from '../types.ts'
import { getBookRelations as apiGetBookRelations } from '../services/api.ts'

export interface Point {
  x: number
  y: number
}

export interface RectBox {
  x: number
  y: number
  width: number
  height: number
}

export interface ComputedConnection {
  relation: BookCanvasRelationItem
  path: string
  badgeX: number
  badgeY: number
  sourcePoint: Point
  targetPoint: Point
  startX?: number
  startY?: number
  controlPoint1X?: number
  controlPoint1Y?: number
  controlPoint2X?: number
  controlPoint2Y?: number
  endX?: number
  endY?: number
}

/**
 * Calcula o ponto na borda do retângulo rect onde a linha saindo de seu centro em direção a targetPoint intercepta.
 */
export function getRectIntersection(rect: RectBox, targetPoint: Point): Point {
  const hw = rect.width / 2
  const hh = rect.height / 2
  const cx = rect.x + hw
  const cy = rect.y + hh

  const dx = targetPoint.x - cx
  const dy = targetPoint.y - cy

  if (Math.abs(dx) < 0.0001 && Math.abs(dy) < 0.0001) {
    return { x: Math.round(cx), y: Math.round(cy) }
  }

  const scaleX = dx !== 0 ? hw / Math.abs(dx) : Infinity
  const scaleY = dy !== 0 ? hh / Math.abs(dy) : Infinity
  const scale = Math.min(scaleX, scaleY)

  return {
    x: Math.round(cx + dx * scale),
    y: Math.round(cy + dy * scale),
  }
}

export interface ConnectionGeometry {
  path: string
  badgeX: number
  badgeY: number
  sourcePoint: Point
  targetPoint: Point
  startX: number
  startY: number
  controlPoint1X: number
  controlPoint1Y: number
  controlPoint2X: number
  controlPoint2Y: number
  endX: number
  endY: number
}

/**
 * Calcula a curva Bézier cúbica entre dois nós e o ponto central para o badge.
 */
export function computeConnectionGeometry(
  sourceRect: RectBox,
  targetRect: RectBox
): ConnectionGeometry {
  const sourceCenter: Point = {
    x: sourceRect.x + sourceRect.width / 2,
    y: sourceRect.y + sourceRect.height / 2,
  }
  const targetCenter: Point = {
    x: targetRect.x + targetRect.width / 2,
    y: targetRect.y + targetRect.height / 2,
  }

  // Interseções nas bordas
  const startPt = getRectIntersection(sourceRect, targetCenter)
  const endPt = getRectIntersection(targetRect, sourceCenter)

  const dx = endPt.x - startPt.x
  const dy = endPt.y - startPt.y
  const dist = Math.sqrt(dx * dx + dy * dy)

  // Curvatura suave adaptativa baseada na distância
  const curvature = Math.min(60, dist * 0.25)
  // Vetor perpendicular normalizado
  const nx = dist > 0 ? -dy / dist : 0
  const ny = dist > 0 ? dx / dist : 0

  const c1: Point = {
    x: Math.round(startPt.x + dx * 0.3 + nx * curvature),
    y: Math.round(startPt.y + dy * 0.3 + ny * curvature),
  }
  const c2: Point = {
    x: Math.round(startPt.x + dx * 0.7 + nx * curvature),
    y: Math.round(startPt.y + dy * 0.7 + ny * curvature),
  }

  // Ponto médio da curva Bézier cúbica B(0.5)
  // B(0.5) = 0.125*P0 + 0.375*P1 + 0.375*P2 + 0.125*P3
  const badgeX = Math.round(0.125 * startPt.x + 0.375 * c1.x + 0.375 * c2.x + 0.125 * endPt.x)
  const badgeY = Math.round(0.125 * startPt.y + 0.375 * c1.y + 0.375 * c2.y + 0.125 * endPt.y)

  const path = `M ${startPt.x} ${startPt.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${endPt.x} ${endPt.y}`

  return {
    path,
    badgeX,
    badgeY,
    sourcePoint: startPt,
    targetPoint: endPt,
    startX: startPt.x,
    startY: startPt.y,
    controlPoint1X: c1.x,
    controlPoint1Y: c1.y,
    controlPoint2X: c2.x,
    controlPoint2Y: c2.y,
    endX: endPt.x,
    endY: endPt.y,
  }
}

export function useCanvasConnections() {
  const relations = ref<BookCanvasRelationItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadBookRelations(bookId: number) {
    loading.value = true
    error.value = null
    try {
      relations.value = await apiGetBookRelations(bookId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao carregar conexões do livro.'
    } finally {
      loading.value = false
    }
  }

  /**
   * Constrói a lista de conexões computadas no espaço do mundo
   */
  function computeConnections(nodesMap: Map<number, CanvasPositionedCard>): ComputedConnection[] {
    const list: ComputedConnection[] = []

    for (const rel of relations.value) {
      const sourceNode = nodesMap.get(rel.source_study_id)
      const targetNode = nodesMap.get(rel.target_study_id)

      if (!sourceNode || !targetNode) continue

      const sourceRect: RectBox = {
        x: sourceNode.x,
        y: sourceNode.y,
        width: sourceNode.width ?? 280,
        height: sourceNode.height ?? 200,
      }

      const targetRect: RectBox = {
        x: targetNode.x,
        y: targetNode.y,
        width: targetNode.width ?? 280,
        height: targetNode.height ?? 200,
      }

      const geom = computeConnectionGeometry(sourceRect, targetRect)

      list.push({
        relation: rel,
        path: geom.path,
        badgeX: geom.badgeX,
        badgeY: geom.badgeY,
        sourcePoint: geom.sourcePoint,
        targetPoint: geom.targetPoint,
        startX: geom.startX,
        startY: geom.startY,
        controlPoint1X: geom.controlPoint1X,
        controlPoint1Y: geom.controlPoint1Y,
        controlPoint2X: geom.controlPoint2X,
        controlPoint2Y: geom.controlPoint2Y,
        endX: geom.endX,
        endY: geom.endY,
      })
    }

    return list
  }

  return {
    relations,
    loading,
    error,
    loadBookRelations,
    computeConnections,
  }
}
