import { ref, type Ref } from 'vue'
import type {
  CanvasFrameItem,
  CreateCanvasFramePayload,
  UpdateCanvasFramePayload,
  StudySummary,
  StudyGroupByCriteria,
} from '../types.ts'
import {
  getCanvasFrames,
  createCanvasFrame as apiCreateFrame,
  updateCanvasFrame as apiUpdateFrame,
  deleteCanvasFrame as apiDeleteFrame,
  errorMessage,
} from '../services/api.ts'
import { getDateBucket } from './useStudyGrouping.ts'

export const DEFAULT_CARD_WIDTH = 220
export const DEFAULT_CARD_HEIGHT = 140

export function isNodeInsideFrame(
  node: { pos_x?: number; pos_y?: number; x?: number; y?: number; width?: number | null; height?: number | null },
  frame: { pos_x: number; pos_y: number; width: number; height: number },
): boolean {
  const nx = node.x ?? node.pos_x ?? 0
  const ny = node.y ?? node.pos_y ?? 0
  const nw = node.width ?? DEFAULT_CARD_WIDTH
  const nh = node.height ?? DEFAULT_CARD_HEIGHT
  const centerX = nx + nw / 2
  const centerY = ny + nh / 2

  return (
    centerX >= frame.pos_x &&
    centerX <= frame.pos_x + frame.width &&
    centerY >= frame.pos_y &&
    centerY <= frame.pos_y + frame.height
  )
}

export function getContainedNodes<T extends { pos_x?: number; pos_y?: number; x?: number; y?: number; width?: number | null; height?: number | null }>(
  frame: { pos_x: number; pos_y: number; width: number; height: number },
  nodes: T[],
): T[] {
  return nodes.filter(node => isNodeInsideFrame(node, frame))
}

export function computeTemporaryLanesProjection(
  nodes: { study_id: number; pos_x?: number; pos_y?: number; x?: number; y?: number }[],
  studies: StudySummary[],
  criteria: StudyGroupByCriteria,
): Map<number, { pos_x: number; pos_y: number; x: number; y: number }> {
  const result = new Map<number, { pos_x: number; pos_y: number; x: number; y: number }>()
  if (criteria === 'manual') {
    return result
  }

  const studyMap = new Map<number, StudySummary>()
  for (const s of studies) {
    studyMap.set(s.id, s)
  }

  // Agrupar IDs por raias
  const laneBuckets = new Map<string, number[]>()

  for (const node of nodes) {
    const study = studyMap.get(node.study_id)
    let laneKey = 'Geral'

    if (criteria === 'status') {
      laneKey = study?.reading_status || 'rascunho'
    } else if (criteria === 'date') {
      laneKey = getDateBucket(study?.created_at).title
    } else if (criteria === 'chapter') {
      laneKey = study?.chapter_id ? `Capítulo ${study.chapter_id}` : 'Sem Capítulo'
    }

    if (!laneBuckets.has(laneKey)) {
      laneBuckets.set(laneKey, [])
    }
    laneBuckets.get(laneKey)!.push(node.study_id)
  }

  // Posicionar em raias/colunas ordenadas
  const LANE_WIDTH = 320
  const CARD_HEIGHT_GAP = 180
  const START_X = 100
  const START_Y = 100

  let laneIndex = 0
  for (const [_, studyIds] of laneBuckets.entries()) {
    const colX = START_X + laneIndex * (LANE_WIDTH + 60)
    studyIds.forEach((studyId, rowIdx) => {
      const y = START_Y + rowIdx * CARD_HEIGHT_GAP
      result.set(studyId, {
        pos_x: colX,
        pos_y: y,
        x: colX,
        y: y,
      })
    })
    laneIndex++
  }

  return result
}

export function useCanvasFrames(bookId?: Ref<number | null | undefined> | number) {
  const frames = ref<CanvasFrameItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activeFrameId = ref<number | null>(null)

  // Snapshot em memória de coordenadas manuais para projeção reversível
  const manualCoordinatesSnapshot = ref<Map<number, { pos_x: number; pos_y: number; x: number; y: number }>>(new Map())
  const isTemporaryProjectionActive = ref(false)

  async function loadFrames(bId?: number) {
    const targetBookId = bId ?? (typeof bookId === 'object' && bookId?.value != null ? bookId.value : typeof bookId === 'number' ? bookId : null)
    if (!targetBookId) return

    loading.value = true
    error.value = null
    try {
      const result = await getCanvasFrames(targetBookId)
      frames.value = result
    } catch (err) {
      error.value = errorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function addFrame(bId: number, payload: CreateCanvasFramePayload): Promise<CanvasFrameItem | null> {
    error.value = null
    try {
      const created = await apiCreateFrame(bId, payload)
      frames.value.push(created)
      return created
    } catch (err) {
      error.value = errorMessage(err)
      return null
    }
  }

  async function updateFrame(frameId: number, payload: UpdateCanvasFramePayload): Promise<CanvasFrameItem | null> {
    try {
      const updated = await apiUpdateFrame(frameId, payload)
      const idx = frames.value.findIndex(f => f.id === frameId)
      if (idx !== -1) {
        frames.value[idx] = updated
      }
      return updated
    } catch (err) {
      error.value = errorMessage(err)
      return null
    }
  }

  async function removeFrame(frameId: number): Promise<boolean> {
    try {
      await apiDeleteFrame(frameId)
      frames.value = frames.value.filter(f => f.id !== frameId)
      if (activeFrameId.value === frameId) {
        activeFrameId.value = null
      }
      return true
    } catch (err) {
      error.value = errorMessage(err)
      return false
    }
  }

  function moveFrameSolidary<T extends { study_id: number; pos_x?: number; pos_y?: number; x?: number; y?: number; width?: number | null; height?: number | null }>(
    frameId: number,
    deltaX: number,
    deltaY: number,
    nodes: T[],
  ): { movedNodes: { study_id: number; x: number; y: number; pos_x: number; pos_y: number }[] } {
    const frame = frames.value.find(f => f.id === frameId)
    if (!frame) return { movedNodes: [] }

    // Atualiza posição do frame localmente
    frame.pos_x = Math.round((frame.pos_x + deltaX) * 10) / 10
    frame.pos_y = Math.round((frame.pos_y + deltaY) * 10) / 10

    // Identifica nós contidos
    const contained = getContainedNodes(frame, nodes)
    const movedNodes = contained.map(node => {
      if (node.x !== undefined) node.x = Math.round((node.x + deltaX) * 10) / 10
      if (node.pos_x !== undefined) node.pos_x = Math.round((node.pos_x + deltaX) * 10) / 10
      if (node.y !== undefined) node.y = Math.round((node.y + deltaY) * 10) / 10
      if (node.pos_y !== undefined) node.pos_y = Math.round((node.pos_y + deltaY) * 10) / 10

      const finalX = node.x ?? node.pos_x ?? 0
      const finalY = node.y ?? node.pos_y ?? 0
      return {
        study_id: node.study_id,
        x: finalX,
        y: finalY,
        pos_x: finalX,
        pos_y: finalY,
      }
    })

    return { movedNodes }
  }

  function applyReversibleProjection<T extends { study_id: number; pos_x?: number; pos_y?: number; x?: number; y?: number; width?: number | null; height?: number | null }>(
    nodes: T[],
    studies: StudySummary[],
    criteria: StudyGroupByCriteria,
  ) {
    if (criteria === 'manual') {
      // Reverter se havia projeção ativa
      if (isTemporaryProjectionActive.value && manualCoordinatesSnapshot.value.size > 0) {
        for (const node of nodes) {
          const original = manualCoordinatesSnapshot.value.get(node.study_id)
          if (original) {
            if (node.x !== undefined) node.x = original.x
            if (node.pos_x !== undefined) node.pos_x = original.pos_x
            if (node.y !== undefined) node.y = original.y
            if (node.pos_y !== undefined) node.pos_y = original.pos_y
          }
        }
        manualCoordinatesSnapshot.value.clear()
        isTemporaryProjectionActive.value = false
      }
      return
    }

    // Se ainda não salvou o snapshot manual, salva agora
    if (!isTemporaryProjectionActive.value) {
      const snap = new Map<number, { pos_x: number; pos_y: number; x: number; y: number }>()
      for (const node of nodes) {
        const nx = node.x ?? node.pos_x ?? 0
        const ny = node.y ?? node.pos_y ?? 0
        snap.set(node.study_id, { pos_x: nx, pos_y: ny, x: nx, y: ny })
      }
      manualCoordinatesSnapshot.value = snap
      isTemporaryProjectionActive.value = true
    }

    // Calcula projeção temporária
    const projected = computeTemporaryLanesProjection(nodes, studies, criteria)
    for (const node of nodes) {
      const coords = projected.get(node.study_id)
      if (coords) {
        if (node.x !== undefined) node.x = coords.x
        if (node.pos_x !== undefined) node.pos_x = coords.pos_x
        if (node.y !== undefined) node.y = coords.y
        if (node.pos_y !== undefined) node.pos_y = coords.pos_y
      }
    }
  }

  return {
    frames,
    loading,
    error,
    activeFrameId,
    isTemporaryProjectionActive,
    loadFrames,
    addFrame,
    updateFrame,
    removeFrame,
    moveFrameSolidary,
    applyReversibleProjection,
  }
}
