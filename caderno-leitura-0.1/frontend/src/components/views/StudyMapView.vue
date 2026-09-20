<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary } from '../../types'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import CanvasAcceleratedLayer from './canvas/CanvasAcceleratedLayer.vue'
import { useCanvasConnections, type ComputedConnection } from '../../composables/useCanvasConnections'
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
  loading: false
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
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

function handleNodeClick(e: MouseEvent, studyId: number): void {
  physics.triggerHapticPulse(e.currentTarget as HTMLElement, 'connect')
  emit('select-study', studyId)
}

// Cálculo da distribuição radial dos nós no mapa conceitual (Q1 - Projeção Fluida)
const svgDimensions = { width: 700, height: 500, cx: 350, cy: 250 }

interface MapNode {
  study: StudySummary
  x: number
  y: number
  angle: number
}

const mappedNodes = computed<MapNode[]>(() => {
  const count = props.studies.length
  if (count === 0) return []

  const radius = count <= 3 ? 140 : count <= 6 ? 175 : 190

  return props.studies.map((study, idx) => {
    // Espalha os nós uniformemente em círculo ao redor do centro
    const angle = (2 * Math.PI * idx) / count - Math.PI / 2
    const x = svgDimensions.cx + radius * Math.cos(angle)
    const y = svgDimensions.cy + radius * Math.sin(angle)
    return { study, x, y, angle }
  })
})

const nodesById = computed(() => {
  const map = new Map<number, { x: number; y: number }>()
  for (const n of mappedNodes.value) {
    map.set(n.study.id, { x: n.x, y: n.y })
  }
  return map
})

const mapSemanticEdges = computed(() => {
  const edges: Array<{ id: number; path: string; label: string; type: string }> = []
  for (const rel of canvasConnections.relations.value) {
    const src = nodesById.value.get(rel.source_study_id)
    const tgt = nodesById.value.get(rel.target_study_id)
    if (src && tgt) {
      const mx = (src.x + tgt.x) / 2
      const my = (src.y + tgt.y) / 2
      const dx = tgt.x - src.x
      const dy = tgt.y - src.y
      const cx = Math.round(mx - dy * 0.2)
      const cy = Math.round(my + dx * 0.2)
      edges.push({
        id: rel.id,
        path: `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`,
        label: rel.relation_type,
        type: rel.relation_type,
      })
    }
  }
  return edges
})

const isAcceleratedMode = computed(() => physics.shouldAccelerate(props.studies.length, 60))

const mapComputedConnections = computed<ComputedConnection[]>(() => {
  const list: ComputedConnection[] = []
  for (const rel of canvasConnections.relations.value) {
    const src = nodesById.value.get(rel.source_study_id)
    const tgt = nodesById.value.get(rel.target_study_id)
    if (src && tgt) {
      const mx = (src.x + tgt.x) / 2
      const my = (src.y + tgt.y) / 2
      const dx = tgt.x - src.x
      const dy = tgt.y - src.y
      const cx = Math.round(mx - dy * 0.2)
      const cy = Math.round(my + dx * 0.2)
      list.push({
        relation: rel,
        sourcePoint: { x: src.x, y: src.y },
        targetPoint: { x: tgt.x, y: tgt.y },
        startX: src.x,
        startY: src.y,
        endX: tgt.x,
        endY: tgt.y,
        controlPoint1X: cx,
        controlPoint1Y: cy,
        controlPoint2X: cx,
        controlPoint2Y: cy,
        badgeX: mx,
        badgeY: my,
        path: `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`,
      })
    }
  }
  return list
})
</script>

<template>
  <div class="study-map-view" role="region" aria-label="Visualização em Mapa Conceitual dos Estudos">
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

    <div v-else class="map-stage-container">
      <div class="map-controls-header">
        <span class="map-hint">
          <Icon name="network" :size="14" class="hint-icon" />
          <span>Distribuição conceitual dos estudos em rede radial</span>
        </span>
        <span class="map-badge">{{ studies.length }} nós</span>
      </div>

        <CanvasAcceleratedLayer
          v-if="isAcceleratedMode"
          :connections="mapComputedConnections"
          :active-study-id="activeStudyId"
          @select-relation="emit('select-study', $event.relation.target_study_id)"
        />

        <svg
          class="map-svg-surface"
          :viewBox="`0 0 ${svgDimensions.width} ${svgDimensions.height}`"
          preserveAspectRatio="xMidYMid meet"
          aria-hidden="true"
        >
          <defs>
            <radialGradient id="hubGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.25" />
              <stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0.04" />
            </radialGradient>
          </defs>

          <!-- Círculos de órbita concêntricos de fundo -->
          <circle
            :cx="svgDimensions.cx"
            :cy="svgDimensions.cy"
            r="175"
            class="orbit-ring"
          />
          <circle
            :cx="svgDimensions.cx"
            :cy="svgDimensions.cy"
            r="120"
            class="orbit-ring inner"
          />

          <!-- Linhas conectoras do centro aos estudos -->
          <g class="connection-lines">
            <line
              v-for="node in mappedNodes"
              :key="`line-${node.study.id}`"
              :x1="svgDimensions.cx"
              :y1="svgDimensions.cy"
              :x2="node.x"
              :y2="node.y"
              class="map-connector-line"
              :class="{ 'is-active-line': activeStudyId === node.study.id }"
            />
          </g>

          <!-- Arestas Semânticas Direcionadas entre Estudos (F04 / F10) -->
          <g v-if="!isAcceleratedMode && mapSemanticEdges.length > 0" class="semantic-edges-group">
            <path
              v-for="edge in mapSemanticEdges"
              :key="`edge-${edge.id}`"
              :d="edge.path"
              class="map-semantic-edge"
              :class="{ 'edge-contradict': edge.type === 'contradiz' }"
            />
          </g>

          <!-- Hub Central (Capítulo / Núcleo de Leitura) -->
          <circle
            :cx="svgDimensions.cx"
            :cy="svgDimensions.cy"
            r="44"
            class="central-hub-circle"
            fill="url(#hubGradient)"
          />
          <circle
            :cx="svgDimensions.cx"
            :cy="svgDimensions.cy"
            r="28"
            class="central-hub-core"
          />
          <text
            :x="svgDimensions.cx"
            :y="svgDimensions.cy + 4"
            text-anchor="middle"
            class="central-hub-text"
          >
            Núcleo
          </text>
        </svg>

        <!-- Nós HTML sobrepostos para acessibilidade e interação rica -->
        <div class="map-nodes-overlay">
          <div
            v-for="node in mappedNodes"
            :key="`node-${node.study.id}`"
            class="map-node-card"
            :class="{ 'is-focused': activeStudyId === node.study.id }"
            :style="{
              left: `${(node.x / svgDimensions.width) * 100}%`,
              top: `${(node.y / svgDimensions.height) * 100}%`
            }"
            @click="handleNodeClick($event, node.study.id)"
          >
            <div class="node-badge-row">
              <span class="node-index">#{{ node.study.id }}</span>
              <time :datetime="node.study.created_at" class="node-date">{{ formatDate(node.study.created_at) }}</time>
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

            <p class="node-location" v-if="node.study.location">
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
                class="node-trash-button"
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
}

.map-hint {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.hint-icon {
  color: var(--color-accent);
}

.map-badge {
  font-weight: 600;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background-color: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  color: var(--color-accent);
}

.map-canvas-viewport {
  position: relative;
  width: 100%;
  min-height: 480px;
  background: radial-gradient(circle at center, var(--color-surface) 0%, color-mix(in srgb, var(--color-surface-elevated) 80%, transparent) 100%);
  border-radius: 6px;
  overflow: hidden;
}

.map-svg-surface {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.orbit-ring {
  fill: none;
  stroke: var(--color-border, #e2e8f0);
  stroke-width: 1;
  stroke-dasharray: 4 4;
}

.orbit-ring.inner {
  stroke-opacity: 0.6;
}

.map-connector-line {
  stroke: var(--color-border-hover, #cbd5e1);
  stroke-width: 1.5;
  stroke-dasharray: 5 3;
  transition: stroke 0.2s ease, stroke-width 0.2s ease;
}

.map-connector-line.is-active-line {
  stroke: var(--color-accent);
  stroke-width: 2.5;
  stroke-dasharray: none;
}

.central-hub-circle {
  stroke: var(--color-accent);
  stroke-width: 1.5;
  stroke-dasharray: 2 2;
}

.central-hub-core {
  fill: var(--color-surface);
  stroke: var(--color-accent);
  stroke-width: 2;
}

.central-hub-text {
  font-size: 11px;
  font-weight: 700;
  fill: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.map-nodes-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.map-node-card {
  position: absolute;
  transform: translate(-50%, -50%);
  pointer-events: auto;
  width: 190px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  padding: 0.65rem 0.8rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.map-node-card:hover {
  transform: translate(-50%, -54%);
  border-color: var(--color-border-hover, #94a3b8);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.map-node-card.is-focused {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent), 0 6px 16px rgba(0, 0, 0, 0.12);
  z-index: 15;
}

.node-badge-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.node-index {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-accent);
}

.node-date {
  font-size: 0.72rem;
  color: var(--color-muted);
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
  color: var(--color-inverse-bg, #0f172a);
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
  width: 26px;
  height: 26px;
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

.map-semantic-edge {
  fill: none;
  stroke: var(--color-accent, #3b82f6);
  stroke-width: 2px;
  stroke-dasharray: 4 3;
  opacity: 0.7;
}

.map-semantic-edge.edge-contradict {
  stroke: #ef4444;
}

@media (max-width: 640px) {
  .map-canvas-viewport {
    min-height: 420px;
  }
  .map-node-card {
    width: 140px;
    padding: 0.5rem;
  }
  .node-location {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .map-node-card,
  .map-connector-line {
    transition: none !important;
  }
}
</style>
