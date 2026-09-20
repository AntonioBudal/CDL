<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CanvasPositionedCard, CanvasBoundingBox } from '../../../types'
import Icon from '../../ui/Icon.vue'

interface Props {
  nodes: Map<number, CanvasPositionedCard>
  boundingBox: CanvasBoundingBox | null
  panX: number
  panY: number
  zoomLevel: number
  viewportWidth: number
  viewportHeight: number
}

const props = withDefaults(defineProps<Props>(), {
  viewportWidth: 800,
  viewportHeight: 600,
})

const emit = defineEmits<{
  (e: 'navigate', worldPoint: { x: number; y: number }): void
}>()

const isCollapsed = ref(false)
const MINIMAP_WIDTH = 180
const MINIMAP_HEIGHT = 120
const PADDING = 8

// Janela do mundo atualmente visível
const visibleWorldRect = computed(() => {
  const z = props.zoomLevel || 1.0
  return {
    x: -props.panX / z,
    y: -props.panY / z,
    width: props.viewportWidth / z,
    height: props.viewportHeight / z,
  }
})

// União do Bounding Box dos cartões com a janela visível
const combinedBounds = computed(() => {
  const v = visibleWorldRect.value
  let minX = v.x
  let minY = v.y
  let maxX = v.x + v.width
  let maxY = v.y + v.height

  if (props.boundingBox) {
    minX = Math.min(minX, props.boundingBox.min_x)
    minY = Math.min(minY, props.boundingBox.min_y)
    maxX = Math.max(maxX, props.boundingBox.max_x)
    maxY = Math.max(maxY, props.boundingBox.max_y)
  }

  const w = Math.max(100, maxX - minX)
  const h = Math.max(100, maxY - minY)

  return { minX, minY, maxX, maxY, width: w, height: h }
})

// Escala de projeção do mundo para o mini-mapa
const projectionScale = computed(() => {
  const bounds = combinedBounds.value
  const availableW = MINIMAP_WIDTH - PADDING * 2
  const availableH = MINIMAP_HEIGHT - PADDING * 2

  const sx = availableW / bounds.width
  const sy = availableH / bounds.height
  return Math.min(sx, sy)
})

function worldToMinimap(wx: number, wy: number): { x: number; y: number } {
  const b = combinedBounds.value
  const s = projectionScale.value

  // Centraliza o conteúdo dentro da moldura do mini-mapa
  const offsetX = (MINIMAP_WIDTH - b.width * s) / 2
  const offsetY = (MINIMAP_HEIGHT - b.height * s) / 2

  return {
    x: offsetX + (wx - b.minX) * s,
    y: offsetY + (wy - b.minY) * s,
  }
}

function minimapToWorld(mx: number, my: number): { x: number; y: number } {
  const b = combinedBounds.value
  const s = projectionScale.value

  const offsetX = (MINIMAP_WIDTH - b.width * s) / 2
  const offsetY = (MINIMAP_HEIGHT - b.height * s) / 2

  return {
    x: b.minX + (mx - offsetX) / s,
    y: b.minY + (my - offsetY) / s,
  }
}

// Projeção visual dos nós
const projectedNodes = computed(() => {
  const s = projectionScale.value
  const list: Array<{ id: number; x: number; y: number; w: number; h: number; color: string | null }> = []

  for (const node of props.nodes.values()) {
    const pt = worldToMinimap(node.x, node.y)
    list.push({
      id: node.study_id,
      x: pt.x,
      y: pt.y,
      w: Math.max(4, (node.width ?? 280) * s),
      h: Math.max(3, (node.height ?? 200) * s),
      color: node.color_tag ?? null,
    })
  }

  return list
})

// Projeção da janela visível
const projectedViewportRect = computed(() => {
  const v = visibleWorldRect.value
  const s = projectionScale.value
  const pt = worldToMinimap(v.x, v.y)

  return {
    left: `${Math.round(pt.x)}px`,
    top: `${Math.round(pt.y)}px`,
    width: `${Math.max(6, Math.round(v.width * s))}px`,
    height: `${Math.max(6, Math.round(v.height * s))}px`,
  }
})

function handleRadarClick(e: MouseEvent): void {
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const clickX = e.clientX - rect.left
  const clickY = e.clientY - rect.top

  const worldPt = minimapToWorld(clickX, clickY)
  emit('navigate', worldPt)
}
</script>

<template>
  <aside
    class="canvas-minimap-container"
    :class="{ 'is-collapsed': isCollapsed }"
    role="complementary"
    aria-label="Mini-mapa de orientação espacial"
  >
    <div class="minimap-header">
      <span class="minimap-title">Radar</span>
      <button
        type="button"
        class="minimap-toggle-btn"
        :title="isCollapsed ? 'Expandir mini-mapa' : 'Recolher mini-mapa'"
        :aria-label="isCollapsed ? 'Expandir mini-mapa' : 'Recolher mini-mapa'"
        @click="isCollapsed = !isCollapsed"
      >
        <Icon :name="isCollapsed ? 'maximize-2' : 'minimize-2'" :size="12" />
      </button>
    </div>

    <div
      v-show="!isCollapsed"
      class="minimap-stage"
      @click="handleRadarClick"
    >
      <!-- Silhuetas dos Cartões de Estudo -->
      <div
        v-for="item in projectedNodes"
        :key="item.id"
        class="minimap-node-dot"
        :style="{
          left: `${item.x}px`,
          top: `${item.y}px`,
          width: `${item.w}px`,
          height: `${item.h}px`,
        }"
      />

      <!-- Retângulo Indicador do Viewport Visível -->
      <div
        class="minimap-viewport-indicator"
        :style="projectedViewportRect"
      />
    </div>
  </aside>
</template>

<style scoped>
.canvas-minimap-container {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-card, 8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  z-index: 35;
  user-select: none;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.minimap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.35rem 0.6rem;
  background: var(--color-surface-hover, #f8fafc);
  border-bottom: 1px solid var(--color-border-divider, #e2e8f0);
}

.minimap-title {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted, #64748b);
}

.minimap-toggle-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted, #94a3b8);
  padding: 2px;
  cursor: pointer;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
}

.minimap-toggle-btn:hover {
  color: var(--color-text-primary, #0f172a);
  background: rgba(0, 0, 0, 0.05);
}

.minimap-stage {
  position: relative;
  width: 180px;
  height: 120px;
  background: var(--color-surface-ground, #fafafa);
  cursor: crosshair;
}

.minimap-node-dot {
  position: absolute;
  background: var(--color-text-muted, #94a3b8);
  border-radius: 1px;
  opacity: 0.8;
  pointer-events: none;
}

.minimap-viewport-indicator {
  position: absolute;
  border: 1.5px solid var(--color-primary, #2563eb);
  background: rgba(37, 99, 235, 0.12);
  border-radius: 2px;
  pointer-events: none;
  box-shadow: 0 0 4px rgba(37, 99, 235, 0.3);
}

@media (max-width: 768px) {
  .canvas-minimap-container {
    bottom: 0.5rem;
    right: 0.5rem;
    transform: scale(0.9);
    transform-origin: bottom right;
  }
}
</style>
