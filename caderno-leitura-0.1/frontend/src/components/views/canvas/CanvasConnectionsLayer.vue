<script setup lang="ts">
import type { ComputedConnection } from '../../../composables/useCanvasConnections'
import { RELATION_TYPE_LABELS } from '../../../composables/useStudyRelations'

interface Props {
  connections: ComputedConnection[]
  activeStudyId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  activeStudyId: null,
})

const emit = defineEmits<{
  (e: 'select-relation', connection: ComputedConnection): void
}>()

function isHighlighted(conn: ComputedConnection): boolean {
  if (!props.activeStudyId) return false
  return (
    conn.relation.source_study_id === props.activeStudyId ||
    conn.relation.target_study_id === props.activeStudyId
  )
}
</script>

<template>
  <svg class="canvas-connections-layer" aria-hidden="true">
    <defs>
      <!-- Marcador de seta padrão -->
      <marker
        id="arrow-default"
        viewBox="0 0 10 10"
        refX="9"
        refY="5"
        markerWidth="6"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-text-muted, #9ca3af)" />
      </marker>

      <!-- Marcador de seta destacado -->
      <marker
        id="arrow-highlighted"
        viewBox="0 0 10 10"
        refX="9"
        refY="5"
        markerWidth="7"
        markerHeight="7"
        orient="auto-start-reverse"
      >
        <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-accent, #2563eb)" />
      </marker>

      <!-- Marcador de seta contradição -->
      <marker
        id="arrow-contradiz"
        viewBox="0 0 10 10"
        refX="9"
        refY="5"
        markerWidth="6"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
      </marker>
    </defs>

    <!-- Curvas de Conexão -->
    <g class="connections-group">
      <path
        v-for="conn in connections"
        :key="'path-' + conn.relation.id"
        :d="conn.path"
        class="connection-path"
        :class="{
          'path-highlighted': isHighlighted(conn),
          'path-contradict': conn.relation.relation_type === 'contradiz',
        }"
        :marker-end="
          isHighlighted(conn)
            ? 'url(#arrow-highlighted)'
            : conn.relation.relation_type === 'contradiz'
            ? 'url(#arrow-contradiz)'
            : 'url(#arrow-default)'
        "
        @click="emit('select-relation', conn)"
      />
    </g>

    <!-- Badges de Tipo Semântico Flutuantes -->
    <g class="badges-group">
      <g
        v-for="conn in connections"
        :key="'badge-' + conn.relation.id"
        :transform="`translate(${conn.badgeX}, ${conn.badgeY})`"
        class="relation-badge-node"
        :class="{ 'badge-highlighted': isHighlighted(conn) }"
        @click="emit('select-relation', conn)"
      >
        <rect
          x="-46"
          y="-11"
          width="92"
          height="22"
          rx="11"
          class="badge-rect"
          :class="{
            'rect-contradict': conn.relation.relation_type === 'contradiz',
            'rect-complement': conn.relation.relation_type === 'complementa',
            'rect-dependency': conn.relation.relation_type === 'depende_de',
          }"
        />
        <text
          x="0"
          y="4"
          text-anchor="middle"
          class="badge-text"
        >
          {{ RELATION_TYPE_LABELS[conn.relation.relation_type]?.outbound || conn.relation.relation_type }}
        </text>
      </g>
    </g>
  </svg>
</template>

<style scoped>
.canvas-connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: visible;
  pointer-events: none;
  z-index: 1;
}

.connection-path {
  fill: none;
  stroke: var(--color-border, #cbd5e1);
  stroke-width: 2px;
  stroke-dasharray: 4 2;
  pointer-events: stroke;
  cursor: pointer;
  transition: stroke 0.15s ease, stroke-width 0.15s ease;
}

.connection-path:hover {
  stroke: var(--color-accent, #2563eb);
  stroke-width: 3px;
  stroke-dasharray: none;
}

.path-highlighted {
  stroke: var(--color-accent, #2563eb);
  stroke-width: 3px;
  stroke-dasharray: none;
}

.path-contradict {
  stroke: #fca5a5;
}

.path-contradict:hover {
  stroke: #ef4444;
}

.relation-badge-node {
  pointer-events: all;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.relation-badge-node:hover {
  transform: scale(1.08);
}

.badge-rect {
  fill: var(--color-surface, #ffffff);
  stroke: var(--color-border, #cbd5e1);
  stroke-width: 1px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.08));
}

.badge-highlighted .badge-rect {
  stroke: var(--color-accent, #2563eb);
  stroke-width: 2px;
}

.rect-contradict {
  fill: #fef2f2;
  stroke: #fecaca;
}

.rect-complement {
  fill: #ecfdf5;
  stroke: #a7f3d0;
}

.rect-dependency {
  fill: #eff6ff;
  stroke: #bfdbfe;
}

.badge-text {
  font-size: 10px;
  font-weight: 600;
  fill: var(--color-text-muted, #475569);
  user-select: none;
}

.rect-contradict + .badge-text {
  fill: #991b1b;
}

.rect-complement + .badge-text {
  fill: #065f46;
}

.rect-dependency + .badge-text {
  fill: #1e40af;
}

/* ==========================================================================
   Comportamento Cinemático e Visual por Superclasse (F10)
   ========================================================================== */

/* Invisível: Quiescência latente em repouso e revelação fluida */
:global(:root[data-superclass="invisivel"]) .connection-path,
:global(.superclass-invisivel) .connection-path {
  opacity: 0.25;
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.15s ease;
}

:global(:root[data-superclass="invisivel"]) .connection-path:hover,
:global(:root[data-superclass="invisivel"]) .path-highlighted,
:global(.superclass-invisivel) .connection-path:hover,
:global(.superclass-invisivel) .path-highlighted {
  opacity: 1;
}

:global(:root[data-superclass="invisivel"]) .relation-badge-node,
:global(.superclass-invisivel) .relation-badge-node {
  opacity: 0.3;
  transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.15s ease;
}

:global(:root[data-superclass="invisivel"]) .relation-badge-node:hover,
:global(:root[data-superclass="invisivel"]) .badge-highlighted,
:global(.superclass-invisivel) .relation-badge-node:hover,
:global(.superclass-invisivel) .badge-highlighted {
  opacity: 1;
}

/* Dimensional: Elevação sombreada 2.5D e profundidade espacial */
:global(:root[data-superclass="dimensional"]) .connection-path,
:global(.superclass-dimensional) .connection-path {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.12));
}

:global(:root[data-superclass="dimensional"]) .relation-badge-node,
:global(.superclass-dimensional) .relation-badge-node {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.16));
}

/* Mecânica: Traçado técnico preciso em grade */
:global(:root[data-superclass="mecanica"]) .connection-path,
:global(.superclass-mecanica) .connection-path {
  stroke-dasharray: 6 3;
  stroke-width: 2px;
}

/* Monolítica: Solidez brutalista sem traçado tracejado */
:global(:root[data-superclass="monolitica"]) .connection-path,
:global(.superclass-monolitica) .connection-path {
  stroke-dasharray: none;
  stroke-width: 2.5px;
  opacity: 0.9;
}
</style>
