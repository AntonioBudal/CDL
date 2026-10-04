<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type {
  StudySummary,
  StudyRelationItem,
  StudyRelationType,
  MapConnectionEdge,
} from '../../types.ts'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import CanvasAcceleratedLayer from './canvas/CanvasAcceleratedLayer.vue'
import { useCanvasConnections, type ComputedConnection } from '../../composables/useCanvasConnections.ts'
import { useSuperclassPhysics } from '../../composables/useSuperclassPhysics.ts'
import { computeRadialLayout } from '../../composables/useMapLayout.ts'
import MapRelationPopover from './map/MapRelationPopover.vue'
import MapQuickCreateCard from './map/MapQuickCreateCard.vue'
import {
  createStudyRelation as apiCreateStudyRelation,
  deleteStudyRelation as apiDeleteStudyRelation,
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
  (e: 'studies-updated'): void
}>()

const canvasConnections = useCanvasConnections()
const physics = useSuperclassPhysics()

onMounted(() => {
  canvasConnections.loadBookRelations(props.bookId)
})

watch(
  () => props.bookId,
  (newId) => {
    canvasConnections.loadBookRelations(newId)
  }
)

function formatDate(isoStr: string): string {
  try {
    return new Date(isoStr).toLocaleDateString('pt-BR')
  } catch {
    return isoStr
  }
}

// ----------------------------------------------------------------------------
// Dimensões do Espaço Vetorial e Distribuição Radial Concêntrica (US1 - MVP)
// ----------------------------------------------------------------------------
const svgDimensions = {
  width: 800,
  height: 560,
  cx: 400,
  cy: 280,
}

const layoutResult = computed(() => {
  return computeRadialLayout(
    props.studies,
    canvasConnections.relations.value as any,
    props.activeStudyId,
    {
      width: svgDimensions.width,
      height: svgDimensions.height,
      cx: svgDimensions.cx,
      cy: svgDimensions.cy,
      primaryRadius: 165,
      secondaryRadius: 265,
    }
  )
})

const isAcceleratedMode = computed(() => physics.shouldAccelerate(props.studies.length, 60))

const mapComputedConnections = computed<ComputedConnection[]>(() => {
  const nodesMap = new Map()
  for (const n of layoutResult.value.nodes) {
    nodesMap.set(n.study.id, {
      x: n.x - 90,
      y: n.y - 45,
      width: 180,
      height: 90,
    })
  }
  return canvasConnections.computeConnections(nodesMap)
})

// ----------------------------------------------------------------------------
// Navegação de Câmera: Pan e Zoom Suave (US1)
// ----------------------------------------------------------------------------
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const stageViewportRef = ref<HTMLElement | null>(null)

function handleZoom(delta: number) {
  const next = Math.min(2.2, Math.max(0.4, Number((zoomLevel.value + delta).toFixed(2))))
  zoomLevel.value = next
}

function zoomIn() {
  handleZoom(0.15)
}

function zoomOut() {
  handleZoom(-0.15)
}

function resetZoom() {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

function onWheel(e: WheelEvent) {
  const delta = e.deltaY < 0 ? 0.1 : -0.1
  handleZoom(delta)
}

function startPan(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.map-node-card, button, .zoom-controls, .mobile-map-toolbar, .map-edge-badge-group')) {
    return
  }
  isPanning.value = true
  panStart.value = { x: e.clientX - panX.value, y: e.clientY - panY.value }
}

function onMouseMove(e: MouseEvent) {
  if (isPanning.value) {
    panX.value = e.clientX - panStart.value.x
    panY.value = e.clientY - panStart.value.y
    return
  }
  if (isConnecting.value) {
    cursorPt.value = getStageCoordinates(e)
  }
}

function endPan() {
  isPanning.value = false
}

// ----------------------------------------------------------------------------
// Traçado Interativo de Conexões e Mini-Popover de Relações (US2)
// ----------------------------------------------------------------------------
const isConnecting = ref(false)
const connectingSourceId = ref<number | null>(null)
const connectingSourcePt = ref<{ x: number; y: number } | null>(null)
const cursorPt = ref<{ x: number; y: number }>({ x: 0, y: 0 })
const mobileAssistedConnecting = ref(false)

const draftLinePath = computed(() => {
  if (!isConnecting.value || !connectingSourcePt.value) return ''
  const src = connectingSourcePt.value
  const tgt = cursorPt.value
  return `M ${src.x} ${src.y} L ${tgt.x} ${tgt.y}`
})

function getStageCoordinates(e: MouseEvent | Touch): { x: number; y: number } {
  if (!stageViewportRef.value) return { x: svgDimensions.cx, y: svgDimensions.cy }
  const rect = stageViewportRef.value.getBoundingClientRect()
  const viewportCenterX = rect.left + rect.width / 2
  const viewportCenterY = rect.top + rect.height / 2
  const mouseDistFromCenterX = (e.clientX - viewportCenterX - panX.value) / zoomLevel.value
  const mouseDistFromCenterY = (e.clientY - viewportCenterY - panY.value) / zoomLevel.value
  return {
    x: Math.round(svgDimensions.cx + mouseDistFromCenterX),
    y: Math.round(svgDimensions.cy + mouseDistFromCenterY),
  }
}

function startConnecting(studyId: number, e: MouseEvent | TouchEvent) {
  const node = layoutResult.value.nodes.find((n) => n.study.id === studyId)
  if (!node) return
  isConnecting.value = true
  connectingSourceId.value = studyId
  connectingSourcePt.value = { x: node.x, y: node.y }
  const clientPt = 'touches' in e && e.touches[0] ? e.touches[0] : (e as MouseEvent)
  cursorPt.value = getStageCoordinates(clientPt)
}

function handleConnectHandleClick(studyId: number, e: MouseEvent) {
  if (isConnecting.value && connectingSourceId.value) {
    if (connectingSourceId.value === studyId) {
      cancelConnecting()
    } else {
      finishConnecting(studyId, e.clientX, e.clientY)
    }
  } else {
    startConnecting(studyId, e)
  }
}

function cancelConnecting() {
  isConnecting.value = false
  connectingSourceId.value = null
  connectingSourcePt.value = null
  mobileAssistedConnecting.value = false
}

const relationPopoverState = ref<{
  isOpen: boolean
  sourceStudy: StudySummary | null
  targetStudy: StudySummary | null
  existingRelation: StudyRelationItem | null
  position: { x: number; y: number }
}>({
  isOpen: false,
  sourceStudy: null,
  targetStudy: null,
  existingRelation: null,
  position: { x: 300, y: 200 },
})

function finishConnecting(targetStudyId: number, clientX: number, clientY: number) {
  if (!connectingSourceId.value || connectingSourceId.value === targetStudyId) {
    // Auto-relação bloqueada (FR-005)
    cancelConnecting()
    return
  }

  const sourceStudy = props.studies.find((s) => s.id === connectingSourceId.value) || null
  const targetStudy = props.studies.find((s) => s.id === targetStudyId) || null
  if (!sourceStudy || !targetStudy) {
    cancelConnecting()
    return
  }

  const existingRel = (canvasConnections.relations.value.find(
    (r) =>
      (r.source_study_id === sourceStudy.id && r.target_study_id === targetStudy.id) ||
      (r.source_study_id === targetStudy.id && r.target_study_id === sourceStudy.id)
  ) as any) || null

  relationPopoverState.value = {
    isOpen: true,
    sourceStudy,
    targetStudy,
    existingRelation: existingRel,
    position: {
      x: typeof window !== 'undefined' ? Math.min(window.innerWidth - 330, Math.max(16, clientX)) : clientX,
      y: typeof window !== 'undefined' ? Math.min(window.innerHeight - 390, Math.max(16, clientY)) : clientY,
    },
  }

  cancelConnecting()
}

function handleNodeMouseUp(studyId: number, e: MouseEvent) {
  if (isConnecting.value && connectingSourceId.value) {
    finishConnecting(studyId, e.clientX, e.clientY)
  }
}

function handleNodeClick(e: MouseEvent, studyId: number): void {
  if (isConnecting.value && connectingSourceId.value) {
    finishConnecting(studyId, e.clientX, e.clientY)
    return
  }
  physics.triggerHapticPulse(e.currentTarget as HTMLElement, 'connect')
  emit('select-study', studyId)
}

function handleEdgeClick(edge: MapConnectionEdge) {
  const sourceStudy = props.studies.find((s) => s.id === edge.sourceStudyId) || null
  const targetStudy = props.studies.find((s) => s.id === edge.targetStudyId) || null
  const existingRel = (canvasConnections.relations.value.find((r) => r.id === edge.id) as any) || null

  if (sourceStudy && targetStudy) {
    relationPopoverState.value = {
      isOpen: true,
      sourceStudy,
      targetStudy,
      existingRelation: existingRel,
      position: {
        x: typeof window !== 'undefined' ? window.innerWidth / 2 - 160 : 300,
        y: typeof window !== 'undefined' ? window.innerHeight / 2 - 180 : 200,
      },
    }
  }
}

async function handleSaveRelation(payload: {
  sourceId: number
  targetId: number
  relationType: StudyRelationType
  description?: string
}) {
  relationPopoverState.value.isOpen = false
  try {
    await apiCreateStudyRelation(payload.sourceId, {
      target_study_id: payload.targetId,
      relation_type: payload.relationType,
      description: payload.description,
    })
    await canvasConnections.loadBookRelations(props.bookId)
  } catch (err) {
    console.error('[StudyMapView] Erro ao persistir relação semântica:', err)
  }
}

async function handleDeleteRelation(relationId: number) {
  relationPopoverState.value.isOpen = false
  try {
    await apiDeleteStudyRelation(relationId)
    await canvasConnections.loadBookRelations(props.bookId)
  } catch (err) {
    console.error('[StudyMapView] Erro ao remover relação semântica:', err)
  }
}

// ----------------------------------------------------------------------------
// Criação Rápida In-Place no Mapa e Ergonomia Mobile (US3)
// ----------------------------------------------------------------------------
const quickCreateState = ref<{
  isOpen: boolean
  position: { x: number; y: number }
  connectedSourceId: number | null
}>({
  isOpen: false,
  position: { x: 300, y: 200 },
  connectedSourceId: null,
})

function handleCanvasDblClick(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.map-node-card, button, .zoom-controls, .mobile-map-toolbar, .map-edge-badge-group')) {
    return
  }
  if (!props.chapterId) return
  quickCreateState.value = {
    isOpen: true,
    position: { x: e.clientX, y: e.clientY },
    connectedSourceId: null,
  }
}

function openQuickCreateCenter() {
  if (!props.chapterId) return
  const x = typeof window !== 'undefined' ? window.innerWidth / 2 - 145 : 300
  const y = typeof window !== 'undefined' ? window.innerHeight / 2 - 170 : 200
  quickCreateState.value = {
    isOpen: true,
    position: { x, y },
    connectedSourceId: null,
  }
}

function openQuickCreateConnected(sourceId: number) {
  if (!props.chapterId) return
  const x = typeof window !== 'undefined' ? window.innerWidth / 2 - 145 : 300
  const y = typeof window !== 'undefined' ? window.innerHeight / 2 - 170 : 200
  quickCreateState.value = {
    isOpen: true,
    position: { x, y },
    connectedSourceId: sourceId,
  }
}

async function handleQuickStudyCreated(payload: {
  study: StudySummary
  initialRelation?: {
    sourceId: number
    targetId: number
    relationType: StudyRelationType
  }
}) {
  quickCreateState.value.isOpen = false
  emit('select-study', payload.study.id)
  emit('studies-updated')
  await canvasConnections.loadBookRelations(props.bookId)
}

const activeStudyNode = computed(() =>
  layoutResult.value.nodes.find((n) => n.study.id === props.activeStudyId)
)

function toggleMobileAssistedConnection() {
  if (!props.activeStudyId) return
  if (mobileAssistedConnecting.value) {
    cancelConnecting()
  } else {
    mobileAssistedConnecting.value = true
    connectingSourceId.value = props.activeStudyId
    const node = layoutResult.value.nodes.find((n) => n.study.id === props.activeStudyId)
    if (node) {
      connectingSourcePt.value = { x: node.x, y: node.y }
    }
  }
}
</script>

<template>
  <div class="study-map-view" role="region" aria-label="Visualização em Mapa Conceitual dos Estudos">
    <!-- Estado Vazio -->
    <EmptyState
      v-if="studies.length === 0 && !loading"
      icon="book-open"
      title="Nenhum estudo neste capítulo"
      description="Importe o texto-base de um fichamento ou crie reflexões diretamente para articular a rede de argumentos."
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

    <div v-else class="map-stage-container">
      <!-- Cabeçalho de Controles e Dicas -->
      <div class="map-controls-header">
        <div class="header-left-hint">
          <Icon name="network" :size="15" class="hint-icon" />
          <span class="map-hint-text">
            Grafo radial semântico • Duplo clique no canvas para criar novo estudo
          </span>
        </div>

        <div class="header-actions-group">
          <span class="map-badge">{{ studies.length }} estudos</span>
          <span class="map-badge connections-badge">{{ layoutResult.edges.length }} conexões</span>

          <button
            v-if="chapterId"
            type="button"
            class="button primary fab-new-study action-btn touch-target"
            title="Criar novo estudo no mapa"
            @click="openQuickCreateCenter"
          >
            <Icon name="plus" :size="13" />
            <span>Novo Estudo</span>
          </button>
        </div>
      </div>

      <!-- Viewport Interativa do Mapa -->
      <div
        ref="stageViewportRef"
        class="map-canvas-viewport"
        @mousedown="startPan"
        @mousemove="onMouseMove"
        @mouseup="endPan"
        @wheel.prevent="onWheel"
        @dblclick="handleCanvasDblClick"
      >
        <!-- Controles Flutuantes de Zoom e Pan -->
        <div class="zoom-controls" role="toolbar" aria-label="Controles de zoom e câmera">
          <button
            type="button"
            class="zoom-btn action-btn touch-target"
            title="Aproximar zoom"
            aria-label="Aproximar zoom"
            @click="zoomIn"
          >
            <Icon name="plus" :size="13" />
          </button>
          <span class="zoom-level-indicator" title="Nível de zoom">
            {{ Math.round(zoomLevel * 100) }}%
          </span>
          <button
            type="button"
            class="zoom-btn action-btn touch-target"
            title="Afastar zoom"
            aria-label="Afastar zoom"
            @click="zoomOut"
          >
            <span class="zoom-symbol">−</span>
          </button>
          <button
            type="button"
            class="zoom-btn action-btn touch-target"
            title="Redefinir visualização"
            aria-label="Redefinir visualização"
            @click="resetZoom"
          >
            <Icon name="rotate-ccw" :size="12" />
          </button>
        </div>

        <!-- Camada Acelerada (Canvas/WebGL para grafos densos) -->
        <CanvasAcceleratedLayer
          v-if="isAcceleratedMode"
          :connections="mapComputedConnections"
          :active-study-id="activeStudyId"
          @select-relation="emit('select-study', $event.relation.target_study_id)"
        />

        <!-- Conteúdo do Mundo (Escalado e Transladado via Transform) -->
        <div
          class="map-world-content"
          :style="{
            transform: `translate(${panX}px, ${panY}px) scale(${zoomLevel})`,
            transformOrigin: `${svgDimensions.cx}px ${svgDimensions.cy}px`,
          }"
        >
          <!-- Superfície SVG para Anéis Orbitais, Arestas Direcionadas e Linha Elástica -->
          <svg
            class="map-svg-surface"
            :viewBox="`0 0 ${svgDimensions.width} ${svgDimensions.height}`"
            preserveAspectRatio="xMidYMid meet"
            aria-hidden="true"
          >
            <defs>
              <radialGradient id="hubGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.28" />
                <stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0.03" />
              </radialGradient>

              <!-- Marcador de Ponta de Seta Direcional -->
              <marker
                id="map-arrow"
                viewBox="0 0 10 10"
                refX="18"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 9 5 L 0 9 z" fill="var(--color-accent, #3b82f6)" />
              </marker>

              <!-- Marcador para Arestas de Contradição -->
              <marker
                id="map-arrow-contradict"
                viewBox="0 0 10 10"
                refX="18"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 9 5 L 0 9 z" fill="#ef4444" />
              </marker>
            </defs>

            <!-- Círculos de Órbita Concêntricos (R1 e R2) -->
            <circle
              :cx="svgDimensions.cx"
              :cy="svgDimensions.cy"
              :r="265"
              class="orbit-ring secondary"
            />
            <circle
              :cx="svgDimensions.cx"
              :cy="svgDimensions.cy"
              :r="165"
              class="orbit-ring primary"
            />

            <!-- Hub Central / Ponto Focal de Fundo -->
            <circle
              :cx="svgDimensions.cx"
              :cy="svgDimensions.cy"
              :r="54"
              class="central-hub-circle"
              fill="url(#hubGradient)"
            />

            <!-- Linhas de Ligação do Centro aos Nós Orbitais -->
            <g class="connection-lines">
              <line
                v-for="node in layoutResult.nodes"
                :key="`line-${node.study.id}`"
                :x1="svgDimensions.cx"
                :y1="svgDimensions.cy"
                :x2="node.x"
                :y2="node.y"
                class="map-connector-line"
                :class="{ 'is-active-line': activeStudyId === node.study.id }"
              />
            </g>

            <!-- Arestas Semânticas Direcionadas (com Badges e Setas) -->
            <g v-if="!isAcceleratedMode" class="semantic-edges-group">
              <g
                v-for="edge in layoutResult.edges"
                :key="`edge-${edge.id}`"
                class="map-edge-group"
              >
                <path
                  :d="edge.path"
                  class="map-semantic-edge"
                  :class="{ 'edge-contradict': edge.isContradiction }"
                  :marker-end="edge.isContradiction ? 'url(#map-arrow-contradict)' : 'url(#map-arrow)'"
                />

                <!-- Badge Semântico da Aresta -->
                <g
                  class="map-edge-badge-group"
                  :transform="`translate(${edge.badgeX}, ${edge.badgeY})`"
                  @click.stop="handleEdgeClick(edge)"
                >
                  <rect
                    x="-36"
                    y="-10"
                    width="72"
                    height="20"
                    rx="4"
                    class="map-edge-badge"
                    :class="{ 'badge-contradict': edge.isContradiction }"
                  />
                  <text
                    x="0"
                    y="4"
                    text-anchor="middle"
                    class="map-edge-badge-text"
                  >
                    {{ edge.label }}
                  </text>
                </g>
              </g>
            </g>

            <!-- Linha Elástica SVG de Conexão em Andamento -->
            <path
              v-if="isConnecting && draftLinePath"
              :d="draftLinePath"
              class="elastic-draft-line"
              marker-end="url(#map-arrow)"
            />
          </svg>

          <!-- Nós HTML Sobrepostos no Espaço Vetorial -->
          <div class="map-nodes-overlay">
            <div
              v-for="node in layoutResult.nodes"
              :key="`node-${node.study.id}`"
              class="map-node-card"
              :class="{
                'is-focused': activeStudyId === node.study.id,
                'central-core-node': node.isCore,
                'is-core': node.isCore,
                'core-node': node.isCore,
                'is-connect-target-candidate': isConnecting && connectingSourceId !== node.study.id,
                'is-drop-forbidden': isConnecting && connectingSourceId === node.study.id,
              }"
              :style="{
                left: `${node.x}px`,
                top: `${node.y}px`,
              }"
              @click="handleNodeClick($event, node.study.id)"
              @mouseup="handleNodeMouseUp(node.study.id, $event)"
            >
              <!-- Alça Conectora para Traçado de Arestas -->
              <button
                type="button"
                class="node-connect-handle action-btn touch-target"
                title="Conectar a outro estudo (arraste até o destino ou clique)"
                aria-label="Conectar a outro estudo"
                @mousedown.stop="startConnecting(node.study.id, $event)"
                @touchstart.stop="startConnecting(node.study.id, $event)"
                @click.stop="handleConnectHandleClick(node.study.id, $event)"
              >
                <Icon name="link" :size="12" />
              </button>

              <div class="node-badge-row">
                <span class="node-index">#{{ node.study.id }}</span>
                <span v-if="node.isCore" class="core-node-pill">Núcleo</span>
                <time :datetime="node.study.created_at" class="node-date">
                  {{ formatDate(node.study.created_at) }}
                </time>
              </div>

              <h4 class="node-card-title">
                <RouterLink
                  :to="{ name: 'study', params: { bookId, studyId: node.study.id } }"
                  class="node-card-link"
                  @click.stop="emit('select-study', node.study.id)"
                >
                  {{ node.study.title }}
                </RouterLink>
              </h4>

              <p v-if="node.study.location" class="node-location">
                <Icon name="book-open" :size="11" />
                <span>{{ node.study.location }}</span>
              </p>

              <div class="node-card-footer">
                <RouterLink
                  :to="{ name: 'study', params: { bookId, studyId: node.study.id } }"
                  class="node-read-link"
                  @click.stop
                >
                  Abrir →
                </RouterLink>
                <button
                  type="button"
                  class="node-trash-button action-btn touch-target"
                  title="Mover estudo para a lixeira"
                  aria-label="Mover estudo para a lixeira"
                  @click.stop="emit('trash-study', node.study)"
                >
                  <Icon name="trash" :size="13" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Barra de Ações Táteis de Rodapé para Mobile (< 768px) -->
        <div
          v-if="activeStudyNode"
          class="mobile-map-toolbar"
          role="toolbar"
          aria-label="Ações táteis do estudo selecionado"
        >
          <div class="mobile-toolbar-header">
            <span class="mobile-selected-title">{{ activeStudyNode.study.title }}</span>
            <button
              type="button"
              class="mobile-dismiss-btn action-btn touch-target"
              title="Desmarcar"
              aria-label="Desmarcar"
              @click="emit('select-study', 0)"
            >
              <Icon name="x" :size="14" />
            </button>
          </div>
          <div class="mobile-toolbar-buttons">
            <button
              type="button"
              class="button secondary action-btn touch-target"
              :class="{ 'is-active': mobileAssistedConnecting }"
              @click="toggleMobileAssistedConnection"
            >
              <Icon name="link" :size="14" />
              <span>{{ mobileAssistedConnecting ? 'Toque no destino...' : 'Conectar a...' }}</span>
            </button>
            <button
              type="button"
              class="button secondary action-btn touch-target"
              @click="openQuickCreateConnected(activeStudyNode.study.id)"
            >
              <Icon name="plus" :size="14" />
              <span>Novo Estudo</span>
            </button>
            <RouterLink
              :to="{ name: 'study', params: { bookId, studyId: activeStudyNode.study.id } }"
              class="button primary action-btn touch-target"
            >
              <span>Ver Estudo</span>
              <Icon name="arrow-right" :size="14" />
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <!-- Mini-Popover Contextual de Relação Semântica (US2) -->
    <MapRelationPopover
      :is-open="relationPopoverState.isOpen"
      :source-study="relationPopoverState.sourceStudy"
      :target-study="relationPopoverState.targetStudy"
      :existing-relation="relationPopoverState.existingRelation"
      :position="relationPopoverState.position"
      @close="relationPopoverState.isOpen = false"
      @save="handleSaveRelation"
      @delete="handleDeleteRelation"
    />

    <!-- Mini-Card Inline de Criação Rápida In-Place (US3) -->
    <MapQuickCreateCard
      v-if="chapterId"
      :is-open="quickCreateState.isOpen"
      :position="quickCreateState.position"
      :chapter-id="chapterId"
      :book-id="bookId"
      :connected-source-id="quickCreateState.connectedSourceId"
      @close="quickCreateState.isOpen = false"
      @created="handleQuickStudyCreated"
    />

    <!-- Resumo Textual Acessível para Leitores de Tela (FR-010 / WCAG) -->
    <div class="sr-only accessible-graph-summary" role="region" aria-label="Resumo textual do grafo de estudos">
      <h3>Grafo Conceitual dos Estudos</h3>
      <p v-if="layoutResult.coreNode">
        Estudo Núcleo: {{ layoutResult.coreNode.study.title }}
      </p>
      <ul>
        <li v-for="node in layoutResult.nodes" :key="`sr-node-${node.study.id}`">
          {{ node.study.title }} ({{ node.isCore ? 'Núcleo Central' : node.ring }})
          <span v-if="node.degree > 0"> — {{ node.degree }} conexão(ões)</span>
        </li>
      </ul>
      <h4>Conexões Semânticas Registradas</h4>
      <ul>
        <li v-for="edge in layoutResult.edges" :key="`sr-edge-${edge.id}`">
          Estudo #{{ edge.sourceStudyId }} {{ edge.relationType }} Estudo #{{ edge.targetStudyId }}
          <span v-if="edge.description">({{ edge.description }})</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.study-map-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.map-stage-container {
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.map-controls-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
  color: var(--color-muted, #64748b);
  gap: 0.5rem;
  flex-wrap: wrap;
}

.header-left-hint {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.hint-icon {
  color: var(--color-accent);
}

.map-hint-text {
  font-size: 0.82rem;
}

.header-actions-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.map-badge {
  font-weight: 600;
  font-size: 0.75rem;
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background-color: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  color: var(--color-accent);
}

.connections-badge {
  background-color: color-mix(in srgb, var(--color-border) 60%, var(--color-surface));
  color: var(--color-muted);
}

.fab-new-study {
  padding: 0.3rem 0.65rem;
  font-size: 0.78rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

/* Viewport do Canvas */
.map-canvas-viewport {
  position: relative;
  width: 100%;
  height: 560px;
  min-height: 520px;
  background: radial-gradient(
    circle at center,
    var(--color-surface) 0%,
    color-mix(in srgb, var(--color-surface-elevated, #f8fafc) 90%, transparent) 100%
  );
  border: 1px solid var(--color-border-divider, #e2e8f0);
  border-radius: 6px;
  overflow: hidden;
  cursor: grab;
  user-select: none;
}

.map-canvas-viewport:active {
  cursor: grabbing;
}

/* Controles de Zoom */
.zoom-controls {
  position: absolute;
  right: 0.85rem;
  top: 0.85rem;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  padding: 0.2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.zoom-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-inverse-bg);
}

.zoom-level-indicator {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-muted);
  min-width: 36px;
  text-align: center;
}

/* Espaço do Mundo */
.map-world-content {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 800px;
  height: 560px;
  margin-left: -400px;
  margin-top: -280px;
  pointer-events: none;
  transition: transform 0.05s linear;
}

.map-svg-surface {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: auto;
}

/* Anéis Orbitais */
.orbit-ring {
  fill: none;
  stroke: var(--color-border, #cbd5e1);
  stroke-width: 1.2;
  stroke-dasharray: 4 4;
}

.orbit-ring.primary {
  stroke-opacity: 0.85;
}

.orbit-ring.secondary {
  stroke-opacity: 0.55;
  stroke-dasharray: 3 5;
}

.central-hub-circle {
  stroke: var(--color-accent);
  stroke-width: 1.5;
  stroke-dasharray: 2 2;
}

.map-connector-line {
  stroke: var(--color-border-hover, #cbd5e1);
  stroke-width: 1;
  stroke-dasharray: 4 4;
  opacity: 0.6;
}

.map-connector-line.is-active-line {
  stroke: var(--color-accent);
  stroke-width: 2;
  stroke-dasharray: none;
  opacity: 1;
}

/* Arestas Semânticas Direcionadas */
.map-semantic-edge {
  fill: none;
  stroke: var(--color-accent, #3b82f6);
  stroke-width: 2px;
  stroke-dasharray: 4 3;
  opacity: 0.85;
  transition: stroke 0.2s, stroke-width 0.2s;
}

.map-semantic-edge.edge-contradict {
  stroke: #ef4444;
}

.map-edge-badge-group {
  cursor: pointer;
}

.map-edge-badge {
  fill: var(--color-surface, #ffffff);
  stroke: var(--color-border, #cbd5e1);
  stroke-width: 1;
  rx: 4;
  transition: all 0.15s ease;
}

.map-edge-badge-group:hover .map-edge-badge {
  stroke: var(--color-accent);
  fill: var(--color-surface-hover);
}

.map-edge-badge.badge-contradict {
  stroke: #ef4444;
}

.map-edge-badge-text {
  font-size: 10px;
  font-weight: 600;
  fill: var(--color-muted, #64748b);
  pointer-events: none;
  user-select: none;
}

/* Linha Elástica de Conexão */
.elastic-draft-line {
  fill: none;
  stroke: var(--color-accent, #3b82f6);
  stroke-width: 2.5px;
  stroke-dasharray: 6 3;
  pointer-events: none;
}

/* Camada de Nós HTML */
.map-nodes-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.map-node-card {
  position: absolute;
  transform: translate(-50%, -50%);
  pointer-events: auto;
  width: 180px;
  max-width: calc(100% - 24px);
  box-sizing: border-box;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  padding: 0.65rem 0.8rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  color: var(--color-text);
  overflow: hidden;
}

.map-node-card:hover {
  transform: translate(-50%, -53%);
  border-color: var(--color-border-hover, #94a3b8);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.map-node-card.is-focused {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent), 0 6px 16px rgba(0, 0, 0, 0.12);
  z-index: 15;
}

/* Destaque Visual Proeminente do Estudo Núcleo (US1 / FR-001) */
.central-core-node,
.is-core,
.core-node {
  border-color: var(--color-accent) !important;
  border-width: 2px !important;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-accent) 20%, transparent), 0 8px 24px rgba(0, 0, 0, 0.12) !important;
  z-index: 20 !important;
}

.core-node-pill {
  font-size: 0.65rem;
  font-weight: 700;
  background-color: var(--color-accent);
  color: #ffffff;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  text-transform: uppercase;
}

/* Alça Conectora Interativa (US2) */
.node-connect-handle {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-elevated, #f8fafc);
  border: 1px solid var(--color-border, #cbd5e1);
  color: var(--color-muted);
  cursor: crosshair;
  padding: 0;
  transition: all 0.15s ease;
}

.node-connect-handle:hover {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #ffffff;
  transform: scale(1.15);
}

.is-connect-target-candidate {
  box-shadow: 0 0 0 2px var(--color-accent);
}

.is-drop-forbidden {
  opacity: 0.6;
  cursor: not-allowed !important;
}

.node-badge-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.35rem;
  padding-right: 22px;
}

.node-index {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-accent);
}

.node-date {
  font-size: 0.7rem;
  color: var(--color-muted);
  margin-left: auto;
}

.node-card-title {
  margin: 0 0 0.3rem 0;
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.25;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-card-link {
  color: var(--color-text);
  text-decoration: none;
}

.node-card-link:hover {
  color: var(--color-accent);
}

.node-location {
  margin: 0 0 0.4rem 0;
  font-size: 0.75rem;
  color: var(--color-muted);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--color-border-divider);
  padding-top: 0.35rem;
  margin-top: 0.3rem;
}

.node-read-link {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
}

.node-read-link:hover {
  text-decoration: underline;
}

.node-trash-button {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  color: var(--color-muted);
  cursor: pointer;
}

.node-trash-button:hover {
  color: var(--color-danger, #b91c1c);
  background: var(--color-surface-hover);
}

/* Botões Globais */
.button {
  padding: 0.35rem 0.7rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.button.primary {
  background: var(--color-accent, #3b82f6);
  color: #ffffff;
}

.button.primary:hover {
  filter: brightness(1.08);
}

.button.secondary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-inverse-bg);
}

.button.secondary:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.button.secondary.is-active {
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  border-color: var(--color-accent);
  color: var(--color-accent);
}

/* Barra de Ações Mobile e Alvos Táteis de 44px (US3 / FR-009) */
@media (max-width: 768px) {
  .touch-target,
  .action-btn {
    min-width: 44px;
    min-height: 44px;
  }

  .mobile-map-toolbar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 40;
    background: var(--color-surface, #ffffff);
    border-top: 1px solid var(--color-border, #cbd5e1);
    padding: 0.75rem 1rem;
    box-shadow: 0 -4px 14px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .mobile-toolbar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .mobile-selected-title {
    font-size: 0.85rem;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 80%;
  }

  .mobile-dismiss-btn {
    background: transparent;
    border: none;
    color: var(--color-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-toolbar-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .mobile-toolbar-buttons .button {
    flex: 1;
    justify-content: center;
    font-size: 0.8rem;
  }

  .map-canvas-viewport {
    height: 460px;
    min-height: 420px;
  }

  .map-node-card {
    width: 150px;
    padding: 0.5rem 0.65rem;
  }

  .node-location {
    display: none;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

@media (prefers-reduced-motion: reduce) {
  .map-node-card,
  .map-connector-line,
  .map-semantic-edge {
    transition: none !important;
  }
}
</style>
