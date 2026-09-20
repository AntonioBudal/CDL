<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, CanvasPositionedCard } from '../../types'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import CanvasToolbar from './canvas/CanvasToolbar.vue'
import CanvasNode from './canvas/CanvasNode.vue'
import CanvasFrameNode from './canvas/CanvasFrameNode.vue'
import CanvasMinimap from './canvas/CanvasMinimap.vue'
import CanvasConnectionsLayer from './canvas/CanvasConnectionsLayer.vue'
import CanvasAcceleratedLayer from './canvas/CanvasAcceleratedLayer.vue'
import { useCanvasViewport } from '../../composables/useCanvasViewport'
import { useCanvasNodes, CARD_WIDTH, CARD_HEIGHT } from '../../composables/useCanvasNodes'
import { useCanvasSelection } from '../../composables/useCanvasSelection'
import { useCanvasConnections } from '../../composables/useCanvasConnections'
import { useCanvasFrames } from '../../composables/useCanvasFrames'
import { useSuperclassPhysics } from '../../composables/useSuperclassPhysics'

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

// 1. Motor de Viewport 2D (Pan & Zoom)
const viewport = useCanvasViewport({
  bookId: () => props.bookId,
})

// 2. Gestão de Nós, Auto-grid e Sincronização em Lote
const canvasNodes = useCanvasNodes({
  bookId: () => props.bookId,
  studies: () => props.studies,
})

// 3. Seleção Simples e Marquee Selection
const canvasSelection = useCanvasSelection()

// 4. Conexões Semânticas e Arestas Vetoriais (F04)
const canvasConnections = useCanvasConnections()

// 5. Molduras Espaciais e Projeção Reversível (F05)
const canvasFrames = useCanvasFrames(computed(() => props.bookId))

// 6. Cinemática e Física das Superclasses (F10)
const physics = useSuperclassPhysics()
const isAcceleratedMode = computed(() => physics.shouldAccelerate(props.studies.length, 60))

const draggingFrameId = ref<number | null>(null)
const frameDragStart = ref({ clientX: 0, clientY: 0, frameX: 0, frameY: 0 })

const resizingFrameId = ref<number | null>(null)
const frameResizeStart = ref({ clientX: 0, clientY: 0, width: 0, height: 0 })

onMounted(() => {
  canvasNodes.loadNodes()
  canvasConnections.loadBookRelations(props.bookId)
  canvasFrames.loadFrames(props.bookId)
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

// Manipulação de Ponteiro no Viewport
function handlePointerDown(e: PointerEvent): void {
  if (e.button !== 0 && e.pointerType === 'mouse') return
  const target = e.target as HTMLElement
  if (target.closest('.canvas-node') || target.closest('button') || target.closest('a')) {
    return
  }

  const rect = viewportContainerRef.value?.getBoundingClientRect()
  const screenX = rect ? e.clientX - rect.left : e.clientX
  const screenY = rect ? e.clientY - rect.top : e.clientY

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
    return
  }

  viewport.handlePointerMove(e.pointerId, e.clientX, e.clientY)

  if (canvasSelection.isMarqueeSelecting.value) {
    const rect = viewportContainerRef.value?.getBoundingClientRect()
    const screenX = rect ? e.clientX - rect.left : e.clientX
    const screenY = rect ? e.clientY - rect.top : e.clientY

    canvasSelection.updateMarquee(
      screenX,
      screenY,
      canvasNodes.positionedNodes.value,
      viewport.screenToWorld,
    )
  }
}

function handlePointerUp(e: PointerEvent): void {
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

function handleNodeSelect(studyId: number, isMulti: boolean): void {
  canvasSelection.selectNode(studyId, isMulti)
  emit('select-study', studyId)
}

function handleNodeDragStart(studyId: number, clientX: number, clientY: number): void {
  canvasNodes.startDragNode(studyId, clientX, clientY, canvasSelection.selectedIds.value)
}

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
  updateViewportSize()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateViewportSize)
  }
})

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
    resizingFrameId.value !== null
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
          @zoom-in="() => viewport.zoomIn()"
          @zoom-out="() => viewport.zoomOut()"
          @reset-zoom="() => viewport.resetView()"
          @fit-to-view="handleFitToView"
          @clear-selection="() => canvasSelection.clearSelection()"
          @add-frame="handleAddFrame"
        />

        <div class="canvas-navigation-hint">
          <Icon name="canvas" :size="14" />
          <span>Arraste cards para organizar • Shift+Arrastar para selecionar área</span>
        </div>
      </div>

      <!-- Palco Interativo 2D com Grade Espacial -->
      <div
        ref="viewportContainerRef"
        class="canvas-viewport"
        :class="{
          'is-panning': viewport.isPanning.value,
          'is-interacting': isInteracting,
        }"
        role="application"
        aria-label="Área bidimensional de estudos"
        tabindex="0"
        @wheel.passive="false"
        @wheel="handleWheel"
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
  cursor: grab;
  touch-action: none;
  background-color: var(--color-surface-ground, #fafafa);
  background-image: radial-gradient(var(--color-border, #cbd5e1) 1px, transparent 1px);
  background-size: 24px 24px;
}

.canvas-viewport.is-panning {
  cursor: grabbing;
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
