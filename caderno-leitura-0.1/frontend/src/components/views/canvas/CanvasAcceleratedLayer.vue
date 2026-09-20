<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { ComputedConnection } from '../../../composables/useCanvasConnections'
import { RELATION_TYPE_LABELS } from '../../../composables/useStudyRelations'

interface Props {
  connections: ComputedConnection[]
  activeStudyId?: number | null
  zoomLevel?: number
  panX?: number
  panY?: number
}

const props = withDefaults(defineProps<Props>(), {
  activeStudyId: null,
  zoomLevel: 1.0,
  panX: 0,
  panY: 0,
})

const emit = defineEmits<{
  (e: 'select-relation', connection: ComputedConnection): void
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationFrameId: number | null = null

function isHighlighted(conn: ComputedConnection): boolean {
  if (!props.activeStudyId) return false
  return (
    conn.relation.source_study_id === props.activeStudyId ||
    conn.relation.target_study_id === props.activeStudyId
  )
}

function renderCanvas(): void {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const dpr = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1
  const rect = canvas.getBoundingClientRect()
  const displayWidth = rect.width || canvas.clientWidth || 800
  const displayHeight = rect.height || canvas.clientHeight || 600

  if (canvas.width !== displayWidth * dpr || canvas.height !== displayHeight * dpr) {
    canvas.width = displayWidth * dpr
    canvas.height = displayHeight * dpr
  }

  ctx.save()
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, displayWidth, displayHeight)

  // Aplicar transformação de pan e zoom do canvas
  ctx.translate(props.panX, props.panY)
  ctx.scale(props.zoomLevel, props.zoomLevel)

  for (const conn of props.connections) {
    const highlighted = isHighlighted(conn)
    const isContradict = conn.relation.relation_type === 'contradiz'

    ctx.beginPath()

    // Estilo da linha
    if (highlighted) {
      ctx.strokeStyle = '#2563eb'
      ctx.lineWidth = 3
      ctx.setLineDash([])
    } else if (isContradict) {
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      ctx.setLineDash([4, 2])
    } else {
      ctx.strokeStyle = '#94a3b8'
      ctx.lineWidth = 2
      ctx.setLineDash([4, 2])
    }

    const startX = conn.startX ?? conn.sourcePoint?.x ?? 0
    const startY = conn.startY ?? conn.sourcePoint?.y ?? 0
    const endX = conn.endX ?? conn.targetPoint?.x ?? 0
    const endY = conn.endY ?? conn.targetPoint?.y ?? 0
    const cp1X = conn.controlPoint1X ?? (startX + (endX - startX) * 0.3)
    const cp1Y = conn.controlPoint1Y ?? (startY + (endY - startY) * 0.3)
    const cp2X = conn.controlPoint2X ?? (startX + (endX - startX) * 0.7)
    const cp2Y = conn.controlPoint2Y ?? (startY + (endY - startY) * 0.7)

    // Desenha a curva cúbica ou quadrática
    ctx.moveTo(startX, startY)
    ctx.bezierCurveTo(
      cp1X,
      cp1Y,
      cp2X,
      cp2Y,
      endX,
      endY
    )
    ctx.stroke()

    // Desenhar seta na extremidade final
    const angle = Math.atan2(endY - cp2Y, endX - cp2X)
    const arrowSize = highlighted ? 9 : 7
    ctx.save()
    ctx.translate(endX, endY)
    ctx.rotate(angle)
    ctx.beginPath()
    ctx.moveTo(0, 0)
    ctx.lineTo(-arrowSize, -arrowSize * 0.5)
    ctx.lineTo(-arrowSize * 0.8, 0)
    ctx.lineTo(-arrowSize, arrowSize * 0.5)
    ctx.closePath()
    ctx.fillStyle = ctx.strokeStyle
    ctx.fill()
    ctx.restore()

    // Desenhar badge semântico no ponto médio
    ctx.save()
    ctx.translate(conn.badgeX, conn.badgeY)

    const label =
      RELATION_TYPE_LABELS[conn.relation.relation_type]?.outbound ||
      conn.relation.relation_type ||
      ''
    const badgeWidth = Math.max(80, label.length * 7 + 16)
    const badgeHeight = 20

    ctx.beginPath()
    ctx.roundRect(-badgeWidth / 2, -badgeHeight / 2, badgeWidth, badgeHeight, 10)

    if (highlighted) {
      ctx.fillStyle = '#ffffff'
      ctx.strokeStyle = '#2563eb'
      ctx.lineWidth = 2
    } else if (isContradict) {
      ctx.fillStyle = '#fef2f2'
      ctx.strokeStyle = '#fca5a5'
      ctx.lineWidth = 1
    } else {
      ctx.fillStyle = '#ffffff'
      ctx.strokeStyle = '#cbd5e1'
      ctx.lineWidth = 1
    }

    ctx.fill()
    ctx.stroke()

    // Texto do badge
    ctx.font = '600 10px system-ui, -apple-system, sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillStyle = isContradict ? '#991b1b' : highlighted ? '#1e40af' : '#475569'
    ctx.fillText(label, 0, 1)

    ctx.restore()
  }

  ctx.restore()
}

function requestRender(): void {
  if (animationFrameId !== null) return
  animationFrameId = requestAnimationFrame(() => {
    animationFrameId = null
    renderCanvas()
  })
}

function handleCanvasClick(e: MouseEvent): void {
  const canvas = canvasRef.value
  if (!canvas) return

  const rect = canvas.getBoundingClientRect()
  // Converter coordenadas de clique na tela para coordenadas do mundo
  const screenX = e.clientX - rect.left
  const screenY = e.clientY - rect.top
  const worldX = (screenX - props.panX) / props.zoomLevel
  const worldY = (screenY - props.panY) / props.zoomLevel

  // Verificar clique sobre algum badge ou aresta
  for (const conn of props.connections) {
    const distToBadge = Math.hypot(worldX - conn.badgeX, worldY - conn.badgeY)
    if (distToBadge <= 45) {
      emit('select-relation', conn)
      return
    }
  }
}

watch(
  () => [props.connections, props.activeStudyId, props.zoomLevel, props.panX, props.panY],
  () => {
    requestRender()
  },
  { deep: true }
)

onMounted(() => {
  nextTick(() => {
    renderCanvas()
  })
})

onUnmounted(() => {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="canvas-accelerated-layer"
    aria-hidden="true"
    @click="handleCanvasClick"
  />
</template>

<style scoped>
.canvas-accelerated-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: all;
  z-index: 1;
}
</style>
