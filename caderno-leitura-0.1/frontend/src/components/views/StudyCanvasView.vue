<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import type {
  StudySummary,
  CanvasPositionedCard,
  CanvasToolMode,
  SnappingTarget,
  CanvasQuickCreateState,
  StudyRelationType,
  StudyRelationItem,
  BookCanvasRelationItem,
} from '../../types.ts'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import CanvasToolbar from './canvas/CanvasToolbar.vue'
import CanvasNode from './canvas/CanvasNode.vue'
import CanvasFrameNode from './canvas/CanvasFrameNode.vue'
import CanvasMinimap from './canvas/CanvasMinimap.vue'
import CanvasConnectionsLayer from './canvas/CanvasConnectionsLayer.vue'
import CanvasAcceleratedLayer from './canvas/CanvasAcceleratedLayer.vue'
import MapQuickCreateCard from './map/MapQuickCreateCard.vue'
import MapRelationPopover from './map/MapRelationPopover.vue'
import { useCanvasViewport } from '../../composables/useCanvasViewport.ts'
import { useCanvasNodes, CARD_WIDTH, CARD_HEIGHT } from '../../composables/useCanvasNodes.ts'
import { useCanvasSelection } from '../../composables/useCanvasSelection.ts'
import { useCanvasConnections } from '../../composables/useCanvasConnections.ts'
import { useCanvasFrames } from '../../composables/useCanvasFrames.ts'
import { useSuperclassPhysics } from '../../composables/useSuperclassPhysics.ts'
import { useSmartSnapping } from '../../composables/useSmartSnapping.ts'
import {
  createStudyRelation,
  updateStudyRelation,
  deleteStudyRelation,
} from '../../services/api.ts'

interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  activeStudyId?: number | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  chapterId: null,
  activeStudyId: null,
  loading: false,
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}>()

const viewportContainerRef = ref<HTMLElement | null>(null)

// 1. Ferramenta Ativa e Estado Modal
const activeTool = ref<CanvasToolMode>('select')
const isSpacePressed = ref(false)

// 2. Motor de Viewport 2D (Pan & Zoom)
const viewport = useCanvasViewport({
  bookId: () => props.bookId,
})

// 3. Gestão de Nós, Auto-grid e Sincronização em Lote
const canvasNodes = useCanvasNodes({
  bookId: () => props.bookId,
  studies: () => props.studies,
})

// 4. Seleção Simples e Marquee Selection
const canvasSelection = useCanvasSelection()

// 5. Conexões Semânticas e Arestas Vetoriais (F04 + F 0.7.8)
const canvasConnections = useCanvasConnections()

// 6. Molduras Espaciais e Movimento Solidário (F05 + F 0.7.8)
const canvasFrames = useCanvasFrames(computed(() => props.bookId))

// 7. Cinemática e Física das Superclasses (F10)
const physics = useSuperclassPhysics()
const isAcceleratedMode = computed(() => physics.shouldAccelerate(props.studies.length, 60))

// 8. Guias Magnéticas Inteligentes (Smart Guides - F 0.7.8)
const smartSnapping = useSmartSnapping()

// Estados de Interação
const draggingFrameId = ref<number | null>(null)
const frameDragStart = ref({ clientX: 0, clientY: 0, frameX: 0, frameY: 0 })

const resizingFrameId = ref<number | null>(null)
const frameResizeStart = ref({ clientX: 0, clientY: 0, width: 0, height: 0 })

// Desenho de nova Moldura
const isDrawingFrame = ref(false)
const frameDrawStart = ref({ x: 0, y: 0 })
const frameDrawCurrent = ref({ x: 0, y: 0 })

// Criação Rápida In-Place (US1)
const quickCreateState = ref<CanvasQuickCreateState>({
  isOpen: false,
  worldX: 0,
  worldY: 0,
  clientX: 0,
  clientY: 0,
  connectedSourceId: null,
})

const targetChapterId = computed(() => {
  return props.chapterId || props.studies[0]?.chapter_id || null
})

// Conexão Semântica Interativa (US3)
const isConnecting = ref(false)
const connectingSourceId = ref<number | null>(null)
const connectingSourcePt = ref<{ x: number; y: number } | null>(null)
const cursorWorldPt = ref<{ x: number; y: number }>({ x: 0, y: 0 })

const relationPopoverState = ref<{
  isOpen: boolean
  sourceStudy: StudySummary | null
  targetStudy: StudySummary | null
  existingRelation: StudyRelationItem | BookCanvasRelationItem | null
  position: { x: number; y: number }
}>({
  isOpen: false,
  sourceStudy: null,
  targetStudy: null,
  existingRelation: null,
  position: { x: 300, y: 200 },
})

const viewportWidth = ref(800)
const viewportHeight = ref(600)

function updateViewportSize(): void {
  if (viewportContainerRef.value) {
    viewportWidth.value = viewportContainerRef.value.clientWidth || 800
    viewportHeight.value = viewportContainerRef.value.clientHeight || 600
  }
}

onMounted(() => {
  canvasNodes.loadNodes()
  canvasConnections.loadBookRelations(props.bookId)
  canvasFrames.loadFrames(props.bookId)
  updateViewportSize()

  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateViewportSize)
    window.addEventListener('keydown', handleGlobalKeyDown)
    window.addEventListener('keyup', handleGlobalKeyUp)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateViewportSize)
    window.removeEventListener('keydown', handleGlobalKeyDown)
    window.removeEventListener('keyup', handleGlobalKeyUp)
  }
})

watch(
  () => props.bookId,
  (newId) => {
    canvasNodes.loadNodes()
    canvasSelection.clearSelection()
    canvasConnections.loadBookRelations(newId)
    canvasFrames.loadFrames(newId)
  },
)

watch(
  () => props.studies,
  () => {
    canvasNodes.loadNodes()
  },
  { deep: true },
)

const computedConnections = computed(() => {
  return canvasConnections.computeConnections(canvasNodes.positionedNodes.value)
})

function getNodeForStudy(study: StudySummary, idx: number): CanvasPositionedCard {
  const existing = canvasNodes.positionedNodes.value.get(study.id)
  if (existing) return existing

  return {
    study_id: study.id,
    x: 40 + (idx % 3) * (CARD_WIDTH + 24),
    y: 40 + Math.floor(idx / 3) * (CARD_HEIGHT + 24),
    width: CARD_WIDTH,
    height: CARD_HEIGHT,
    z_index: 0,
    color_tag: null,
    is_persisted: false,
  }
}

// Atalhos Globais de Teclado (V, H, F, C, Espaço, Esc)
function handleGlobalKeyDown(e: KeyboardEvent): void {
  const target = e.target as HTMLElement
  if (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    quickCreateState.value.isOpen ||
    relationPopoverState.value.isOpen
  ) {
    return
  }

  if (e.code === 'Space' && !e.repeat) {
    e.preventDefault()
    isSpacePressed.value = true
    return
  }

  if (e.key === 'Escape') {
    if (isConnecting.value) {
      cancelConnecting()
    } else if (activeTool.value !== 'select') {
      activeTool.value = 'select'
    }
    return
  }

  const key = e.key.toLowerCase()
  if (key === 'v') {
    activeTool.value = 'select'
  } else if (key === 'h') {
    activeTool.value = 'pan'
  } else if (key === 'f') {
    activeTool.value = 'frame'
  } else if (key === 'c') {
    activeTool.value = 'connect'
  }
}

function handleGlobalKeyUp(e: KeyboardEvent): void {
  if (e.code === 'Space') {
    isSpacePressed.value = false
  }
}

// Interação com a roda do mouse (zoom focal)
function handleWheel(e: WheelEvent): void {
  e.preventDefault()
  if (!viewportContainerRef.value) return

  const rect = viewportContainerRef.value.getBoundingClientRect()
  const screenPoint = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
  }

  const delta = e.deltaY < 0 ? 0.12 : -0.12
  viewport.zoomAt(screenPoint, viewport.zoomLevel.value + delta)
}

// Duplo clique na área livre do Canvas (US1 - MVP)
function handleCanvasDblClick(e: MouseEvent): void {
  const target = e.target as HTMLElement
  if (
    target.closest('.canvas-node') ||
    target.closest('.canvas-frame-node') ||
    target.closest('button') ||
    target.closest('a') ||
    target.closest('.quick-create-card') ||
    target.closest('.map-relation-popover')
  ) {
    return
  }

  const rect = viewportContainerRef.value?.getBoundingClientRect()
  if (!rect) return
  const screenX = e.clientX - rect.left
  const screenY = e.clientY - rect.top
  const worldPoint = viewport.screenToWorld(screenX, screenY)

  quickCreateState.value = {
    isOpen: true,
    worldX: Math.round(worldPoint.x),
    worldY: Math.round(worldPoint.y),
    clientX: e.clientX,
    clientY: e.clientY,
    connectedSourceId: null,
  }
}

function handleToolbarQuickCreate(): void {
  updateViewportSize()
  const worldCenter = viewport.screenToWorld(viewportWidth.value / 2, viewportHeight.value / 2)
  const rect = viewportContainerRef.value?.getBoundingClientRect()
  quickCreateState.value = {
    isOpen: true,
    worldX: Math.round(worldCenter.x),
    worldY: Math.round(worldCenter.y),
    clientX: (rect?.left ?? 100) + viewportWidth.value / 2,
    clientY: (rect?.top ?? 100) + viewportHeight.value / 2,
    connectedSourceId: null,
  }
}

function handleQuickStudyCreated(payload: {
  study: StudySummary
  initialRelation?: {
    sourceId: number
    targetId: number
    relationType: StudyRelationType
  }
}): void {
  canvasNodes.setNodePosition(payload.study.id, quickCreateState.value.worldX, quickCreateState.value.worldY, true)
  canvasNodes.scheduleBatchSave()
  emit('select-study', payload.study.id)

  if (payload.initialRelation) {
    canvasConnections.loadBookRelations(props.bookId)
  }
  quickCreateState.value.isOpen = false
}

// Manipulação de Ponteiro no Viewport
function handlePointerDown(e: PointerEvent): void {
  if (e.button !== 0 && e.pointerType === 'mouse') return
  const target = e.target as HTMLElement
  if (
    target.closest('.canvas-node') ||
    target.closest('.canvas-frame-node') ||
    target.closest('button') ||
    target.closest('a') ||
    target.closest('.quick-create-card') ||
    target.closest('.map-relation-popover')
  ) {
    return
  }

  const rect = viewportContainerRef.value?.getBoundingClientRect()
  const screenX = rect ? e.clientX - rect.left : e.clientX
  const screenY = rect ? e.clientY - rect.top : e.clientY

  if (activeTool.value === 'frame') {
    const worldPt = viewport.screenToWorld(screenX, screenY)
    isDrawingFrame.value = true
    frameDrawStart.value = { ...worldPt }
    frameDrawCurrent.value = { ...worldPt }
    ;(e.currentTarget as HTMLElement)?.setPointerCapture?.(e.pointerId)
    return
  }

  if (isSpacePressed.value || activeTool.value === 'pan') {
    canvasSelection.clearSelection()
    viewport.handlePointerDown(e.pointerId, e.clientX, e.clientY)
    ;(e.currentTarget as HTMLElement)?.setPointerCapture?.(e.pointerId)
    return
  }

  if (e.shiftKey) {
    // Iniciar Marquee Selection
    canvasSelection.startMarquee(screenX, screenY, e.ctrlKey || e.metaKey)
  } else {
    // Iniciar Pan livre / Gestos táteis
    canvasSelection.clearSelection()
    viewport.handlePointerDown(e.pointerId, e.clientX, e.clientY)
  }

  ;(e.currentTarget as HTMLElement)?.setPointerCapture?.(e.pointerId)
}

function handleAddFrame() {
  updateViewportSize()
  const worldCenter = viewport.screenToWorld(
    viewportWidth.value / 2,
    viewportHeight.value / 2,
  )
  canvasFrames.addFrame(props.bookId, {
    title: 'Nova Moldura',
    color: 'amber',
    pos_x: Math.round(worldCenter.x - 200),
    pos_y: Math.round(worldCenter.y - 150),
    width: 400,
    height: 300,
  })
}

function handleFrameDragStart(frameId: number, screenX: number, screenY: number) {
  const frame = canvasFrames.frames.value.find(f => f.id === frameId)
  if (!frame) return
  draggingFrameId.value = frameId
  frameDragStart.value = {
    clientX: screenX,
    clientY: screenY,
    frameX: frame.pos_x,
    frameY: frame.pos_y,
  }
}

function handleFrameResizeStart(frameId: number, screenX: number, screenY: number) {
  const frame = canvasFrames.frames.value.find(f => f.id === frameId)
  if (!frame) return
  resizingFrameId.value = frameId
  frameResizeStart.value = {
    clientX: screenX,
    clientY: screenY,
    width: frame.width,
    height: frame.height,
  }
}

function handleFrameUpdateTitle(frameId: number, title: string) {
  canvasFrames.updateFrame(frameId, { title })
}

function handleFrameUpdateColor(frameId: number, color: string) {
  canvasFrames.updateFrame(frameId, { color })
}

function handleFrameDelete(frameId: number) {
  canvasFrames.removeFrame(frameId)
}

function handlePointerMove(e: PointerEvent): void {
  const rect = viewportContainerRef.value?.getBoundingClientRect()
  const screenX = rect ? e.clientX - rect.left : e.clientX
  const screenY = rect ? e.clientY - rect.top : e.clientY

  if (isConnecting.value) {
    cursorWorldPt.value = viewport.screenToWorld(screenX, screenY)
  }

  if (isDrawingFrame.value) {
    frameDrawCurrent.value = viewport.screenToWorld(screenX, screenY)
    return
  }

  if (draggingFrameId.value !== null) {
    const deltaX = (e.clientX - frameDragStart.value.clientX) / viewport.zoomLevel.value
    const deltaY = (e.clientY - frameDragStart.value.clientY) / viewport.zoomLevel.value
    frameDragStart.value.clientX = e.clientX
    frameDragStart.value.clientY = e.clientY

    canvasFrames.moveFrameSolidary(
      draggingFrameId.value,
      deltaX,
      deltaY,
      Array.from(canvasNodes.positionedNodes.value.values()),
    )
    return
  }

  if (resizingFrameId.value !== null) {
    const deltaX = (e.clientX - frameResizeStart.value.clientX) / viewport.zoomLevel.value
    const deltaY = (e.clientY - frameResizeStart.value.clientY) / viewport.zoomLevel.value
    frameResizeStart.value.clientX = e.clientX
    frameResizeStart.value.clientY = e.clientY

    const frame = canvasFrames.frames.value.find(f => f.id === resizingFrameId.value)
    if (frame) {
      frame.width = Math.max(100, Math.round((frame.width + deltaX) * 10) / 10)
      frame.height = Math.max(80, Math.round((frame.height + deltaY) * 10) / 10)
    }
    return
  }

  if (canvasNodes.isDraggingNodes.value) {
    canvasNodes.updateDragNode(e.clientX, e.clientY, viewport.zoomLevel.value)

    // Cálculo em tempo real de Smart Snapping com guias magnéticas (US3)
    const dragId = canvasNodes.dragStudyId.value
    if (dragId !== null) {
      const draggedNode = canvasNodes.positionedNodes.value.get(dragId)
      if (draggedNode) {
        const draggingRect: SnappingTarget = {
          x: draggedNode.x,
          y: draggedNode.y,
          width: draggedNode.width ?? CARD_WIDTH,
          height: draggedNode.height ?? CARD_HEIGHT,
          id: dragId,
        }

        const others: SnappingTarget[] = []
        for (const [id, node] of canvasNodes.positionedNodes.value.entries()) {
          if (id !== dragId && !canvasSelection.selectedIds.value.has(id)) {
            others.push({
              x: node.x,
              y: node.y,
              width: node.width ?? CARD_WIDTH,
              height: node.height ?? CARD_HEIGHT,
              id,
            })
          }
        }
        for (const frame of canvasFrames.frames.value) {
          others.push({
            x: frame.pos_x,
            y: frame.pos_y,
            width: frame.width,
            height: frame.height,
            id: `frame-${frame.id}`,
          })
        }

        const snapped = smartSnapping.snapPosition(draggingRect, others)
        const diffX = snapped.x - draggedNode.x
        const diffY = snapped.y - draggedNode.y
        if (diffX !== 0 || diffY !== 0) {
          draggedNode.x = snapped.x
          draggedNode.y = snapped.y
          if (canvasSelection.selectedIds.value.has(dragId)) {
            for (const id of canvasSelection.selectedIds.value) {
              if (id !== dragId) {
                const otherSel = canvasNodes.positionedNodes.value.get(id)
                if (otherSel) {
                  otherSel.x = Math.round((otherSel.x + diffX) * 10) / 10
                  otherSel.y = Math.round((otherSel.y + diffY) * 10) / 10
                }
              }
            }
          }
        }
      }
    }
    return
  }

  viewport.handlePointerMove(e.pointerId, e.clientX, e.clientY)

  if (canvasSelection.isMarqueeSelecting.value) {
    canvasSelection.updateMarquee(
      screenX,
      screenY,
      canvasNodes.positionedNodes.value,
      viewport.screenToWorld,
    )
  }
}

function handlePointerUp(e: PointerEvent): void {
  if (isDrawingFrame.value) {
    isDrawingFrame.value = false
    const fx = Math.min(frameDrawStart.value.x, frameDrawCurrent.value.x)
    const fy = Math.min(frameDrawStart.value.y, frameDrawCurrent.value.y)
    const fw = Math.abs(frameDrawCurrent.value.x - frameDrawStart.value.x)
    const fh = Math.abs(frameDrawCurrent.value.y - frameDrawStart.value.y)

    const finalWidth = fw >= 60 ? fw : 400
    const finalHeight = fh >= 60 ? fh : 300
    const finalX = fw >= 60 ? fx : Math.round(frameDrawStart.value.x - finalWidth / 2)
    const finalY = fh >= 60 ? fy : Math.round(frameDrawStart.value.y - finalHeight / 2)

    canvasFrames.addFrame(props.bookId, {
      title: 'Nova Moldura',
      color: 'amber',
      pos_x: Math.round(finalX),
      pos_y: Math.round(finalY),
      width: Math.round(finalWidth),
      height: Math.round(finalHeight),
    })
    activeTool.value = 'select'
  }

  if (draggingFrameId.value !== null) {
    const frame = canvasFrames.frames.value.find(f => f.id === draggingFrameId.value)
    if (frame) {
      let posX = Math.round(frame.pos_x * 10) / 10
      let posY = Math.round(frame.pos_y * 10) / 10
      if (physics.activeProfile.value.snapGridSize > 0) {
        const { snappedX, snappedY, didSnap } = physics.calculateSnapPosition(posX, posY)
        if (didSnap) {
          posX = snappedX
          posY = snappedY
          physics.triggerHapticPulse(viewportContainerRef.value, 'snap')
        }
      }
      canvasFrames.updateFrame(frame.id, {
        pos_x: posX,
        pos_y: posY,
      })
      canvasNodes.scheduleBatchSave()
    }
    draggingFrameId.value = null
  }

  if (resizingFrameId.value !== null) {
    const frame = canvasFrames.frames.value.find(f => f.id === resizingFrameId.value)
    if (frame) {
      canvasFrames.updateFrame(frame.id, {
        width: Math.round(frame.width * 10) / 10,
        height: Math.round(frame.height * 10) / 10,
      })
    }
    resizingFrameId.value = null
  }

  if (canvasNodes.isDraggingNodes.value) {
    smartSnapping.clearGuides()
    if (physics.activeProfile.value.snapGridSize > 0) {
      let didAnySnap = false
      for (const id of canvasSelection.selectedIds.value) {
        const node = canvasNodes.positionedNodes.value.get(id)
        if (node) {
          const { snappedX, snappedY, didSnap } = physics.calculateSnapPosition(node.x, node.y)
          if (didSnap) {
            node.x = snappedX
            node.y = snappedY
            didAnySnap = true
          }
        }
      }
      if (didAnySnap) {
        physics.triggerHapticPulse(viewportContainerRef.value, 'snap')
        canvasNodes.scheduleBatchSave()
      }
    }
    canvasNodes.endDragNode()
  }

  viewport.handlePointerUp(e.pointerId)
  if (canvasSelection.isMarqueeSelecting.value) {
    canvasSelection.endMarquee()
  }
}

function handleNodeKeyboardMove(studyId: number, deltaX: number, deltaY: number): void {
  const node = canvasNodes.positionedNodes.value.get(studyId)
  if (node) {
    node.x = Math.round((node.x + deltaX) * 10) / 10
    node.y = Math.round((node.y + deltaY) * 10) / 10
    canvasNodes.scheduleBatchSave()
  }
}

function handleNodeSelect(studyId: number, isMulti: boolean, event?: MouseEvent): void {
  if (isConnecting.value && connectingSourceId.value) {
    if (connectingSourceId.value === studyId) {
      cancelConnecting()
    } else {
      finishConnecting(studyId, event?.clientX ?? 300, event?.clientY ?? 300)
    }
    return
  }

  if (activeTool.value === 'connect') {
    startConnecting(studyId, event?.clientX ?? 300, event?.clientY ?? 300)
    return
  }

  canvasSelection.selectNode(studyId, isMulti)
  emit('select-study', studyId)
}

function handleNodeDragStart(studyId: number, clientX: number, clientY: number): void {
  if (activeTool.value === 'pan' || isSpacePressed.value) return
  canvasNodes.startDragNode(studyId, clientX, clientY, canvasSelection.selectedIds.value)
}

function handleStartConnect(studyId: number, e: MouseEvent): void {
  if (isConnecting.value) {
    if (connectingSourceId.value === studyId) {
      cancelConnecting()
    } else {
      finishConnecting(studyId, e.clientX, e.clientY)
    }
  } else {
    startConnecting(studyId, e.clientX, e.clientY)
  }
}

function startConnecting(studyId: number, clientX: number, clientY: number): void {
  isConnecting.value = true
  connectingSourceId.value = studyId
  const node = canvasNodes.positionedNodes.value.get(studyId)
  if (node) {
    connectingSourcePt.value = {
      x: node.x + (node.width ?? CARD_WIDTH) / 2,
      y: node.y + (node.height ?? CARD_HEIGHT) / 2,
    }
  }
  const rect = viewportContainerRef.value?.getBoundingClientRect()
  if (rect) {
    const screenX = clientX - rect.left
    const screenY = clientY - rect.top
    cursorWorldPt.value = viewport.screenToWorld(screenX, screenY)
  }
}

function cancelConnecting(): void {
  isConnecting.value = false
  connectingSourceId.value = null
  connectingSourcePt.value = null
}

function finishConnecting(targetStudyId: number, clientX: number, clientY: number): void {
  if (!connectingSourceId.value || connectingSourceId.value === targetStudyId) {
    cancelConnecting()
    return
  }

  const srcStudy = props.studies.find(s => s.id === connectingSourceId.value) || null
  const tgtStudy = props.studies.find(s => s.id === targetStudyId) || null

  const existing = canvasConnections.relations.value.find(
    r => (r.source_study_id === connectingSourceId.value && r.target_study_id === targetStudyId) ||
         (r.source_study_id === targetStudyId && r.target_study_id === connectingSourceId.value)
  ) || null

  relationPopoverState.value = {
    isOpen: true,
    sourceStudy: srcStudy,
    targetStudy: tgtStudy,
    existingRelation: existing,
    position: {
      x: typeof window !== 'undefined' ? Math.min(window.innerWidth - 320, Math.max(20, clientX)) : clientX,
      y: typeof window !== 'undefined' ? Math.min(window.innerHeight - 380, Math.max(20, clientY)) : clientY,
    },
  }
  cancelConnecting()
}

async function handleSaveRelation(payload: {
  sourceId: number
  targetId: number
  relationType: StudyRelationType
  description?: string
}) {
  try {
    if (relationPopoverState.value.existingRelation) {
      await updateStudyRelation(relationPopoverState.value.existingRelation.id, {
        relation_type: payload.relationType,
        description: payload.description,
      })
    } else {
      await createStudyRelation(payload.sourceId, {
        target_study_id: payload.targetId,
        relation_type: payload.relationType,
        description: payload.description,
      })
    }
    await canvasConnections.loadBookRelations(props.bookId)
  } catch (err) {
    console.error('Erro ao salvar relação no canvas:', err)
  } finally {
    relationPopoverState.value.isOpen = false
  }
}

async function handleDeleteRelation(relationId: number) {
  try {
    await deleteStudyRelation(relationId)
    await canvasConnections.loadBookRelations(props.bookId)
  } catch (err) {
    console.error('Erro ao excluir relação:', err)
  } finally {
    relationPopoverState.value.isOpen = false
  }
}

function handleMinimapNavigate(worldPt: { x: number; y: number }): void {
  updateViewportSize()
  const w = viewportWidth.value
  const h = viewportHeight.value
  viewport.panX.value = Math.round((w / 2 - worldPt.x * viewport.zoomLevel.value) * 10) / 10
  viewport.panY.value = Math.round((h / 2 - worldPt.y * viewport.zoomLevel.value) * 10) / 10
  viewport.saveViewport(props.bookId)
}

function handleFitToView(): void {
  updateViewportSize()
  viewport.fitToView(canvasNodes.boundingBox.value, viewportWidth.value, viewportHeight.value)
}

const isInteracting = computed(() => {
  return (
    viewport.isPanning.value ||
    canvasNodes.isDraggingNodes.value ||
    canvasSelection.isMarqueeSelecting.value ||
    draggingFrameId.value !== null ||
    resizingFrameId.value !== null ||
    isDrawingFrame.value ||
    isConnecting.value
  )
})
</script>

<template>
  <div class="study-canvas-view" role="region" aria-label="Visualização em Canvas Espacial dos Estudos">
    <EmptyState
      v-if="studies.length === 0 && !loading"
      icon="book-open"
      title="Nenhum estudo neste capítulo"
      description="Importe o texto-base de um fichamento para registrar reflexões e análises sobre este trecho da leitura."
      heading-level="h3"
    >
      <RouterLink
        v-if="chapterId"
        class="button primary"
        :to="{ name: 'import', query: { book: bookId, chapter: chapterId } }"
      >
        Importar estudo
      </RouterLink>
    </EmptyState>

    <div v-else class="canvas-outer-wrapper">
      <!-- Barra de Ferramentas Superior -->
      <div class="canvas-header-bar">
        <CanvasToolbar
          :zoom-level="viewport.zoomLevel.value"
          :has-nodes="studies.length > 0"
          :has-selection="canvasSelection.selectedIds.value.size > 0"
          :selected-count="canvasSelection.selectedIds.value.size"
          :active-tool="activeTool"
          @set-tool="activeTool = $event"
          @quick-create="handleToolbarQuickCreate"
          @zoom-in="() => viewport.zoomIn()"
          @zoom-out="() => viewport.zoomOut()"
          @reset-zoom="() => viewport.resetView()"
          @fit-to-view="handleFitToView"
          @clear-selection="() => canvasSelection.clearSelection()"
          @add-frame="handleAddFrame"
        />

        <div class="canvas-navigation-hint">
          <Icon name="canvas" :size="14" />
          <span>Duplo clique: Criar estudo • Shift+Arrastar: Seleção em bloco</span>
        </div>
      </div>

      <!-- Palco Interativo 2D com Grade Espacial -->
      <div
        ref="viewportContainerRef"
        class="canvas-viewport"
        :class="{
          'is-panning': viewport.isPanning.value || isSpacePressed || activeTool === 'pan',
          'is-interacting': isInteracting,
          'mode-frame': activeTool === 'frame',
          'mode-connect': activeTool === 'connect' || isConnecting,
        }"
        role="application"
        aria-label="Área bidimensional de estudos"
        tabindex="0"
        @wheel.passive="false"
        @wheel="handleWheel"
        @dblclick="handleCanvasDblClick"
        @pointerdown="handlePointerDown"
        @pointermove="handlePointerMove"
        @pointerup="handlePointerUp"
        @pointercancel="handlePointerUp"
      >
        <!-- Camada de Transformação Matricial Afim -->
        <div
          class="canvas-transform-layer"
          :style="viewport.transformStyle.value"
        >
          <!-- Molduras Espaciais Manuais (Canvas Frames) -->
          <CanvasFrameNode
            v-for="frame in canvasFrames.frames.value"
            :key="frame.id"
            :frame="frame"
            @drag-start="handleFrameDragStart"
            @resize-start="handleFrameResizeStart"
            @update-title="handleFrameUpdateTitle"
            @update-color="handleFrameUpdateColor"
            @delete="handleFrameDelete"
          />

          <!-- Rascunho visual de moldura sendo desenhada -->
          <div
            v-if="isDrawingFrame"
            class="canvas-frame-draft"
            :style="{
              left: `${Math.min(frameDrawStart.x, frameDrawCurrent.x)}px`,
              top: `${Math.min(frameDrawStart.y, frameDrawCurrent.y)}px`,
              width: `${Math.abs(frameDrawCurrent.x - frameDrawStart.x)}px`,
              height: `${Math.abs(frameDrawCurrent.y - frameDrawStart.y)}px`,
            }"
          />

          <!-- Arestas e Conexões: Camada Acelerada Canvas 2D (≥ 60 nós) OU SVG (< 60 nós) -->
          <CanvasAcceleratedLayer
            v-if="isAcceleratedMode"
            :connections="computedConnections"
            :active-study-id="activeStudyId"
            @select-relation="emit('select-study', $event.relation.target_study_id)"
          />
          <CanvasConnectionsLayer
            v-else
            :connections="computedConnections"
            :active-study-id="activeStudyId"
            @select-relation="emit('select-study', $event.relation.target_study_id)"
          />

          <!-- Linha elástica temporária de rascunho de conexão (US3) -->
          <svg
            v-if="isConnecting && connectingSourcePt"
            class="canvas-draft-connection-layer"
            aria-hidden="true"
          >
            <line
              :x1="connectingSourcePt.x"
              :y1="connectingSourcePt.y"
              :x2="cursorWorldPt.x"
              :y2="cursorWorldPt.y"
              stroke="var(--color-primary, #2563eb)"
              stroke-width="2"
              stroke-dasharray="6 4"
            />
          </svg>

          <!-- Camada de Guias Magnéticas Inteligentes (Smart Guides - US3) -->
          <svg
            v-if="smartSnapping.activeGuides.value.length > 0"
            class="canvas-smart-guides-layer"
            aria-hidden="true"
          >
            <line
              v-for="(guide, idx) in smartSnapping.activeGuides.value"
              :key="idx"
              :x1="guide.type === 'vertical' ? guide.coordinate : guide.start"
              :y1="guide.type === 'vertical' ? guide.start : guide.coordinate"
              :x2="guide.type === 'vertical' ? guide.coordinate : guide.end"
              :y2="guide.type === 'vertical' ? guide.end : guide.coordinate"
              stroke="var(--color-primary, #2563eb)"
              stroke-width="1.5"
              stroke-dasharray="4 3"
              opacity="0.9"
            />
          </svg>

          <!-- Cards de Estudos Posicionados no Mundo -->
          <CanvasNode
            v-for="(study, idx) in studies"
            :key="study.id"
            :study="study"
            :node="getNodeForStudy(study, idx)"
            :book-id="bookId"
            :is-selected="canvasSelection.selectedIds.value.has(study.id)"
            :is-focused="activeStudyId === study.id"
            @select="handleNodeSelect"
            @drag-start="handleNodeDragStart"
            @move-keyboard="handleNodeKeyboardMove"
            @start-connect="handleStartConnect"
            @trash="emit('trash-study', $event)"
          />
        </div>

        <!-- Retângulo de Marquee Selection -->
        <div
          v-if="canvasSelection.isMarqueeSelecting.value"
          class="canvas-marquee-box"
          :style="canvasSelection.marqueeStyle.value"
        />
      </div>

      <!-- Mini-mapa Radar de Orientação Espacial -->
      <CanvasMinimap
        v-if="studies.length > 0"
        :nodes="canvasNodes.positionedNodes.value"
        :bounding-box="canvasNodes.boundingBox.value"
        :pan-x="viewport.panX.value"
        :pan-y="viewport.panY.value"
        :zoom-level="viewport.zoomLevel.value"
        :viewport-width="viewportWidth"
        :viewport-height="viewportHeight"
        @navigate="handleMinimapNavigate"
      />

      <!-- Mini-card inline in-place de criação rápida (US1) -->
      <MapQuickCreateCard
        v-if="quickCreateState.isOpen && targetChapterId"
        :is-open="quickCreateState.isOpen"
        :position="{ x: quickCreateState.clientX, y: quickCreateState.clientY }"
        :chapter-id="targetChapterId"
        :book-id="bookId"
        :connected-source-id="quickCreateState.connectedSourceId"
        @close="quickCreateState.isOpen = false"
        @created="handleQuickStudyCreated"
      />

      <!-- Popover de Relações Semânticas (US3) -->
      <MapRelationPopover
        v-if="relationPopoverState.isOpen"
        :is-open="relationPopoverState.isOpen"
        :source-study="relationPopoverState.sourceStudy"
        :target-study="relationPopoverState.targetStudy"
        :existing-relation="relationPopoverState.existingRelation"
        :position="relationPopoverState.position"
        @close="relationPopoverState.isOpen = false"
        @save="handleSaveRelation"
        @delete="handleDeleteRelation"
      />
    </div>
  </div>
</template>

<style scoped>
.study-canvas-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.canvas-outer-wrapper {
  position: relative;
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  height: 680px;
  display: flex;
  flex-direction: column;
}

.canvas-header-bar {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 30;
  pointer-events: none;
}

.canvas-header-bar > * {
  pointer-events: auto;
}

.canvas-navigation-hint {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.canvas-viewport {
  position: relative;
  flex: 1;
  width: 100%;
  height: 100%;
  overflow: hidden;
  cursor: default;
  touch-action: none;
  background-color: var(--color-surface-ground, #fafafa);
  background-image: radial-gradient(var(--color-border, #cbd5e1) 1px, transparent 1px);
  background-size: 24px 24px;
}

.canvas-viewport.is-panning {
  cursor: grab;
}

.canvas-viewport.is-panning:active {
  cursor: grabbing;
}

.canvas-viewport.mode-frame {
  cursor: crosshair;
}

.canvas-viewport.mode-connect {
  cursor: crosshair;
}

.canvas-viewport:focus-visible {
  outline: 2px solid var(--color-primary, #2563eb);
  outline-offset: -2px;
}

.canvas-transform-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  will-change: transform;
}

.canvas-transform-layer > * {
  pointer-events: auto;
}

.canvas-frame-draft {
  position: absolute;
  border: 2px dashed var(--color-primary, #2563eb);
  background: color-mix(in srgb, var(--color-primary, #2563eb) 8%, transparent);
  border-radius: 12px;
  pointer-events: none;
  z-index: 2;
}

.canvas-draft-connection-layer {
  position: absolute;
  inset: -10000px;
  width: 20000px;
  height: 20000px;
  pointer-events: none;
  z-index: 15;
}

.canvas-smart-guides-layer {
  position: absolute;
  inset: -10000px;
  width: 20000px;
  height: 20000px;
  pointer-events: none;
  z-index: 25;
}

.canvas-marquee-box {
  position: absolute;
  border: 1.5px dashed var(--color-primary, #2563eb);
  background-color: rgba(37, 99, 235, 0.08);
  pointer-events: none;
  z-index: 50;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .canvas-navigation-hint {
    display: none;
  }
}
</style>
