<script setup lang="ts">
/**
 * F0.11.10 (spec 112): etapa "Ajustar a foto" da digitalização — recorte e giro no navegador, antes da leitura.
 * O recorte é desenhado num canvas na resolução original e enviado como arquivo novo; nada sai daqui sem o leitor
 * pedir.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'
import {
  MIN_CROP_SIDE_PX,
  MAX_OUTPUT_PIXELS,
  describeCrop,
  drawTransform,
  initialCrop,
  isWholeImage,
  keyboardDelta,
  moveHandle,
  outputSize,
  rotate,
  rotateCrop,
  rotatedSize,
  sourceOffset,
  type Crop,
  type CropHandle,
  type Rotation,
} from '../../utils/photoCrop'

const props = defineProps<{ file: File; previewUrl: string }>()
const emit = defineEmits<{
  (e: 'confirm', file: File): void
  (e: 'whole'): void
  (e: 'another'): void
}>()

const MAX_BYTES = 20 * 1024 * 1024
const DISPLAY_MAX_SIDE = 1600

const crop = ref<Crop>(initialCrop())
const rotation = ref<Rotation>(0)
const natural = ref({ width: 0, height: 0 })
const displayCanvas = ref<HTMLCanvasElement | null>(null)
const stage = ref<HTMLDivElement | null>(null)
const exporting = ref(false)
const error = ref('')
let source: ImageBitmap | HTMLImageElement | null = null

const HANDLES: { id: CropHandle; label: string }[] = [
  { id: 'nw', label: 'Canto superior esquerdo do recorte' },
  { id: 'n', label: 'Borda de cima do recorte' },
  { id: 'ne', label: 'Canto superior direito do recorte' },
  { id: 'e', label: 'Borda direita do recorte' },
  { id: 'se', label: 'Canto inferior direito do recorte' },
  { id: 's', label: 'Borda de baixo do recorte' },
  { id: 'sw', label: 'Canto inferior esquerdo do recorte' },
  { id: 'w', label: 'Borda esquerda do recorte' },
]

const description = computed(() => describeCrop(crop.value))
const boxStyle = computed(() => ({
  left: `${crop.value.x * 100}%`,
  top: `${crop.value.y * 100}%`,
  width: `${crop.value.w * 100}%`,
  height: `${crop.value.h * 100}%`,
}))
const stageStyle = computed(() => {
  const size = rotatedSize(natural.value.width || 4, natural.value.height || 3, rotation.value)
  // Largura limitada pela altura máxima (70vh), para a imagem não se deformar.
  return { aspectRatio: `${size.width} / ${size.height}`, width: `min(100%, calc(70vh * ${size.width / size.height}))` }
})

async function loadSource(): Promise<void> {
  try {
    source = await createImageBitmap(props.file, { imageOrientation: 'from-image' })
  } catch {
    source = await new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('imagem'))
      img.src = props.previewUrl
    })
  }
  natural.value = {
    width: 'naturalWidth' in source ? source.naturalWidth : source.width,
    height: 'naturalHeight' in source ? source.naturalHeight : source.height,
  }
}

function drawDisplay() {
  const canvas = displayCanvas.value
  if (!canvas || !source || !natural.value.width) return
  const rotated = rotatedSize(natural.value.width, natural.value.height, rotation.value)
  const scale = Math.min(1, DISPLAY_MAX_SIDE / Math.max(rotated.width, rotated.height))
  canvas.width = Math.max(1, Math.round(rotated.width * scale))
  canvas.height = Math.max(1, Math.round(rotated.height * scale))
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.scale(scale, scale)
  const t = drawTransform(rotation.value, rotated.width, rotated.height)
  ctx.translate(t.tx, t.ty)
  ctx.rotate(t.angle)
  ctx.drawImage(source, 0, 0)
}

onMounted(async () => {
  try {
    await loadSource()
  } catch {
    error.value = 'Não consegui abrir a foto para recortar. Ela será lida inteira.'
    emit('whole')
    return
  }
  if (Math.min(natural.value.width, natural.value.height) < MIN_CROP_SIDE_PX) {
    emit('whole') // foto pequena: lê direto, como antes
    return
  }
  drawDisplay()
})

watch(rotation, drawDisplay)

onBeforeUnmount(() => {
  if (source && 'close' in source) source.close()
  source = null
})

// --- Arraste (mouse, toque e caneta) ---------------------------------------------------------

let drag: { handle: CropHandle; startX: number; startY: number; start: Crop; pointer: number } | null = null

function onPointerDown(handle: CropHandle, event: PointerEvent) {
  const target = event.currentTarget as HTMLElement
  target.setPointerCapture?.(event.pointerId)
  drag = { handle, startX: event.clientX, startY: event.clientY, start: { ...crop.value }, pointer: event.pointerId }
  event.preventDefault()
  event.stopPropagation()
}

function onPointerMove(event: PointerEvent) {
  if (!drag || drag.pointer !== event.pointerId || !stage.value) return
  const rect = stage.value.getBoundingClientRect()
  if (!rect.width || !rect.height) return
  crop.value = moveHandle(drag.start, drag.handle, (event.clientX - drag.startX) / rect.width,
    (event.clientY - drag.startY) / rect.height)
}

function onPointerUp(event: PointerEvent) {
  if (drag && drag.pointer === event.pointerId) drag = null
}

function onKey(handle: CropHandle, event: KeyboardEvent) {
  const delta = keyboardDelta(event.key, event.shiftKey)
  if (!delta) return
  event.preventDefault()
  event.stopPropagation() // a alça não move também o recorte inteiro
  crop.value = moveHandle(crop.value, handle, delta.dx, delta.dy)
}

function turn(direction: 'left' | 'right') {
  crop.value = rotateCrop(crop.value, direction)
  rotation.value = rotate(rotation.value, direction)
}

// --- Exportação ------------------------------------------------------------------------------

function toBlob(canvas: HTMLCanvasElement, type: string): Promise<Blob | null> {
  return new Promise((resolve) => canvas.toBlob(resolve, type, 0.92))
}

async function exportCrop(area: Crop): Promise<File | null> {
  if (!source) return null
  const type = props.file.type === 'image/png' ? 'image/png' : 'image/jpeg'
  let maxPixels = MAX_OUTPUT_PIXELS
  for (let attempt = 0; attempt < 4; attempt += 1) {
    const size = outputSize(natural.value.width, natural.value.height, area, rotation.value, maxPixels)
    const canvas = document.createElement('canvas')
    canvas.width = size.width
    canvas.height = size.height
    const ctx = canvas.getContext('2d')
    if (!ctx) return null
    const rotated = rotatedSize(natural.value.width, natural.value.height, rotation.value)
    const offset = sourceOffset(natural.value.width, natural.value.height, area, rotation.value)
    const t = drawTransform(rotation.value, rotated.width, rotated.height)
    ctx.scale(size.scale, size.scale)
    ctx.translate(-offset.x, -offset.y)
    ctx.translate(t.tx, t.ty)
    ctx.rotate(t.angle)
    ctx.drawImage(source, 0, 0)
    const blob = await toBlob(canvas, type)
    canvas.width = canvas.height = 0
    if (!blob) return null
    if (blob.size <= MAX_BYTES) {
      const base = props.file.name.replace(/\.[^.]+$/, '') || 'pagina'
      return new File([blob], `${base}-recorte.${type === 'image/png' ? 'png' : 'jpg'}`, { type })
    }
    maxPixels = Math.floor(size.width * size.height * 0.6)
  }
  return null
}

async function confirm(area: Crop = crop.value) {
  exporting.value = true
  error.value = ''
  try {
    const file = await exportCrop(area)
    if (file) emit('confirm', file)
    else {
      error.value = 'Não consegui recortar a foto neste navegador. Ela será lida inteira.'
      emit('whole')
    }
  } finally {
    exporting.value = false
  }
}

function useWhole() {
  const whole = { x: 0, y: 0, w: 1, h: 1 }
  if (isWholeImage(whole, rotation.value)) emit('whole')
  else void confirm(whole) // girada: envia a foto inteira já na orientação escolhida
}
</script>

<template>
  <section class="panel cropper-panel" aria-labelledby="cropper-heading">
    <h2 id="cropper-heading" tabindex="-1">Ajustar a foto</h2>
    <p class="cropper-muted">
      Deixe só a página dentro do recorte: arraste os cantos, as bordas ou o próprio recorte. Use as setas do teclado
      nos cantos (Shift para passos maiores).
    </p>

    <div
      ref="stage"
      class="cropper-stage"
      :style="stageStyle"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <canvas ref="displayCanvas" class="cropper-image" role="img" aria-label="Foto escolhida" />
      <div
        class="cropper-box"
        :style="boxStyle"
        role="button"
        tabindex="0"
        aria-label="Área do recorte (arraste ou use as setas para mover)"
        @pointerdown="onPointerDown('move', $event)"
        @keydown="onKey('move', $event)"
      >
        <span
          v-for="handle in HANDLES"
          :key="handle.id"
          class="cropper-handle"
          :class="`handle-${handle.id}`"
          role="button"
          tabindex="0"
          :aria-label="handle.label"
          @pointerdown="onPointerDown(handle.id, $event)"
          @keydown="onKey(handle.id, $event)"
        />
      </div>
    </div>
    <p class="cropper-muted" aria-live="polite">{{ description }}</p>
    <p v-if="error" class="cropper-error" role="alert">{{ error }}</p>

    <div class="cropper-actions">
      <button type="button" class="quiet cropper-button" :disabled="exporting" @click="turn('left')">
        <Icon name="rotate-ccw" :size="18" aria-hidden="true" /> Girar à esquerda
      </button>
      <button type="button" class="quiet cropper-button" :disabled="exporting" @click="turn('right')">
        <Icon name="refresh-cw" :size="18" aria-hidden="true" /> Girar à direita
      </button>
    </div>
    <div class="cropper-actions">
      <button type="button" class="primary cropper-button" :disabled="exporting" @click="confirm()">
        {{ exporting ? 'Recortando…' : 'Ler a página' }}
      </button>
      <button type="button" class="quiet cropper-button" :disabled="exporting" @click="useWhole">Usar a foto inteira</button>
      <button type="button" class="quiet cropper-button" :disabled="exporting" @click="emit('another')">Escolher outra foto</button>
    </div>
  </section>
</template>

<style scoped>
.cropper-panel {
  min-width: 0;
}
.cropper-muted {
  color: var(--color-muted);
  font-size: 0.92rem;
  margin: 6px 0;
}
.cropper-error {
  color: var(--color-danger-text);
}
.cropper-stage {
  position: relative;
  margin: 12px auto;
  overflow: hidden;
  touch-action: none;
  user-select: none;
  border-radius: 6px;
  background: var(--color-surface-soft, var(--color-surface));
}
.cropper-image {
  display: block;
  width: 100%;
  height: 100%;
}
.cropper-box {
  position: absolute;
  box-shadow: 0 0 0 9999px rgb(0 0 0 / 0.55);
  outline: 2px solid #fff;
  cursor: move;
  touch-action: none;
}
.cropper-box:focus-visible,
.cropper-handle:focus-visible {
  outline: 3px solid var(--ring-focus);
  outline-offset: 2px;
}
.cropper-handle {
  position: absolute;
  width: 44px;
  height: 44px;
  margin: -22px 0 0 -22px;
  touch-action: none;
}
.cropper-handle::after {
  content: '';
  position: absolute;
  inset: 14px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid rgb(0 0 0 / 0.6);
}
.handle-nw { left: 0; top: 0; cursor: nwse-resize; }
.handle-n { left: 50%; top: 0; cursor: ns-resize; }
.handle-ne { left: 100%; top: 0; cursor: nesw-resize; }
.handle-e { left: 100%; top: 50%; cursor: ew-resize; }
.handle-se { left: 100%; top: 100%; cursor: nwse-resize; }
.handle-s { left: 50%; top: 100%; cursor: ns-resize; }
.handle-sw { left: 0; top: 100%; cursor: nesw-resize; }
.handle-w { left: 0; top: 50%; cursor: ew-resize; }
.cropper-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.cropper-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  white-space: normal;
}
</style>
