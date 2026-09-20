import { ref, computed, toValue } from 'vue'
import type { MaybeRefOrGetter } from 'vue'
import type {
  StudySummary,
  StudyCanvasNode,
  CanvasPositionedCard,
  CanvasBoundingBox,
  CanvasBatchUpdateItem,
} from '../types'
import { getCanvasNodes, saveCanvasBatch } from '../services/api.ts'

export interface UseCanvasNodesOptions {
  bookId: MaybeRefOrGetter<number>
  studies: MaybeRefOrGetter<StudySummary[]>
}

export const CARD_WIDTH = 280
export const CARD_HEIGHT = 200
export const GRID_GAP = 24
export const COLS_PER_CHAPTER = 3

export function computeAutoGridPositions(
  studies: StudySummary[],
  existingNodesMap: Map<number, StudyCanvasNode>,
): Map<number, CanvasPositionedCard> {
  const result = new Map<number, CanvasPositionedCard>()

  // 1. Estudos com coordenadas já salvas no banco
  let maxPersistedZ = 0
  for (const study of studies) {
    const saved = existingNodesMap.get(study.id)
    if (saved) {
      result.set(study.id, {
        study_id: study.id,
        x: saved.pos_x,
        y: saved.pos_y,
        width: saved.width ?? CARD_WIDTH,
        height: saved.height ?? CARD_HEIGHT,
        z_index: saved.z_index ?? 0,
        color_tag: saved.color_tag,
        is_persisted: true,
      })
      if (saved.z_index > maxPersistedZ) {
        maxPersistedZ = saved.z_index
      }
    }
  }

  // 2. Estudos sem coordenadas: agrupar por chapter_id e dispor em auto-grid
  const unpositionedByChapter = new Map<number, StudySummary[]>()
  for (const study of studies) {
    if (!existingNodesMap.has(study.id)) {
      const list = unpositionedByChapter.get(study.chapter_id) || []
      list.push(study)
      unpositionedByChapter.set(study.chapter_id, list)
    }
  }

  let chapterBlockOffsetX = 40
  for (const [, chapterStudies] of unpositionedByChapter.entries()) {
    chapterStudies.forEach((study, idx) => {
      const col = idx % COLS_PER_CHAPTER
      const row = Math.floor(idx / COLS_PER_CHAPTER)

      const x = chapterBlockOffsetX + col * (CARD_WIDTH + GRID_GAP)
      const y = 40 + row * (CARD_HEIGHT + GRID_GAP)

      result.set(study.id, {
        study_id: study.id,
        x,
        y,
        width: CARD_WIDTH,
        height: CARD_HEIGHT,
        z_index: 0,
        color_tag: null,
        is_persisted: false,
      })
    })

    // Desloca o próximo capítulo para a direita para separar visualmente
    const chapterCols = Math.min(chapterStudies.length, COLS_PER_CHAPTER)
    chapterBlockOffsetX += Math.max(1, chapterCols) * (CARD_WIDTH + GRID_GAP) + 60
  }

  return result
}

export function useCanvasNodes(options: UseCanvasNodesOptions) {
  const positionedNodes = ref<Map<number, CanvasPositionedCard>>(new Map())
  const loading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)

  // Estado de arrasto
  const isDraggingNodes = ref(false)
  const dragStudyId = ref<number | null>(null)
  const dragStartScreen = ref({ x: 0, y: 0 })
  const initialDragPositions = ref<Map<number, { x: number; y: number }>>(new Map())

  let saveDebounceTimer: ReturnType<typeof setTimeout> | null = null

  async function loadNodes(): Promise<void> {
    const currentBookId = toValue(options.bookId)
    if (!currentBookId) return

    loading.value = true
    error.value = null
    try {
      const res = await getCanvasNodes(currentBookId)
      const existingMap = new Map<number, StudyCanvasNode>()
      for (const node of res.nodes) {
        existingMap.set(node.study_id, node)
      }

      const allStudies = toValue(options.studies)
      positionedNodes.value = computeAutoGridPositions(allStudies, existingMap)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Erro ao carregar nós do canvas'
    } finally {
      loading.value = false
    }
  }

  function scheduleBatchSave(): void {
    if (saveDebounceTimer) {
      clearTimeout(saveDebounceTimer)
    }

    saveDebounceTimer = setTimeout(async () => {
      const currentBookId = toValue(options.bookId)
      if (!currentBookId) return

      const payloadItems: CanvasBatchUpdateItem[] = []
      for (const node of positionedNodes.value.values()) {
        payloadItems.push({
          study_id: node.study_id,
          pos_x: Math.round(node.x * 10) / 10,
          pos_y: Math.round(node.y * 10) / 10,
          width: node.width,
          height: node.height,
          z_index: node.z_index,
          color_tag: node.color_tag,
        })
      }

      if (payloadItems.length === 0) return

      isSaving.value = true
      try {
        await saveCanvasBatch(currentBookId, { nodes: payloadItems })
        // Marca como persistidos
        for (const item of payloadItems) {
          const current = positionedNodes.value.get(item.study_id)
          if (current) {
            current.is_persisted = true
          }
        }
      } catch (err) {
        console.error('Falha ao salvar coordenadas do canvas:', err)
      } finally {
        isSaving.value = false
      }
    }, 300)
  }

  function startDragNode(
    studyId: number,
    screenX: number,
    screenY: number,
    selectedIds: Set<number> = new Set(),
  ): void {
    isDraggingNodes.value = true
    dragStudyId.value = studyId
    dragStartScreen.value = { x: screenX, y: screenY }

    // Determinar se move apenas o clicado ou o grupo selecionado
    const targets = selectedIds.has(studyId) ? Array.from(selectedIds) : [studyId]

    initialDragPositions.value = new Map()
    let maxZ = 0
    for (const node of positionedNodes.value.values()) {
      if (node.z_index > maxZ) maxZ = node.z_index
    }

    // Eleva o z-index dos nós arrastados
    for (const id of targets) {
      const node = positionedNodes.value.get(id)
      if (node) {
        initialDragPositions.value.set(id, { x: node.x, y: node.y })
        node.z_index = maxZ + 1
      }
    }
  }

  function updateDragNode(screenX: number, screenY: number, zoomLevel: number): void {
    if (!isDraggingNodes.value || initialDragPositions.value.size === 0) return

    const deltaX = (screenX - dragStartScreen.value.x) / zoomLevel
    const deltaY = (screenY - dragStartScreen.value.y) / zoomLevel

    for (const [id, initialPos] of initialDragPositions.value.entries()) {
      const node = positionedNodes.value.get(id)
      if (node) {
        node.x = Math.round((initialPos.x + deltaX) * 10) / 10
        node.y = Math.round((initialPos.y + deltaY) * 10) / 10
      }
    }
  }

  function endDragNode(): void {
    if (isDraggingNodes.value) {
      isDraggingNodes.value = false
      dragStudyId.value = null
      initialDragPositions.value.clear()
      scheduleBatchSave()
    }
  }

  // Bounding box calculado de todos os cards existentes
  const boundingBox = computed<CanvasBoundingBox | null>(() => {
    if (positionedNodes.value.size === 0) return null

    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    for (const node of positionedNodes.value.values()) {
      const w = node.width ?? CARD_WIDTH
      const h = node.height ?? CARD_HEIGHT

      if (node.x < minX) minX = node.x
      if (node.y < minY) minY = node.y
      if (node.x + w > maxX) maxX = node.x + w
      if (node.y + h > maxY) maxY = node.y + h
    }

    if (!Number.isFinite(minX) || !Number.isFinite(maxX)) return null

    return {
      min_x: minX,
      min_y: minY,
      max_x: maxX,
      max_y: maxY,
      width: Math.max(10, maxX - minX),
      height: Math.max(10, maxY - minY),
    }
  })

  return {
    positionedNodes,
    loading,
    isSaving,
    error,
    isDraggingNodes,
    dragStudyId,
    boundingBox,
    loadNodes,
    startDragNode,
    updateDragNode,
    endDragNode,
    scheduleBatchSave,
  }
}
