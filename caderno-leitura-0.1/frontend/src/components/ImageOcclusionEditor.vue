<script setup lang="ts">
// F0.12.06 (spec 119): editor de oclusão de imagem. Retângulos em SVG sobre a imagem, em coordenadas relativas (0–1);
// cada retângulo vira um cartão de revisão. Mouse, toque e teclado (Delete apaga, setas movem, Ctrl+Z desfaz).
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { api, errorMessage } from '../services/api'
import Icon from './ui/Icon.vue'
import type { OcclusionBoxInput } from '../types.ts'

const props = defineProps<{
  open: boolean
  studyId: number
  mediaId: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', count: number): void
}>()

interface Box extends OcclusionBoxInput {
  key: number
}

const MAX_BOXES = 50
const MIN_SIDE = 0.01
const STEP = 0.01

const state = reactive({
  boxes: [] as Box[],
  selected: -1,
  loading: false,
  saving: false,
  error: '',
  dirty: false,
  undoCount: 0,
})
const history: string[] = []
let nextKey = 1
const stage = ref<HTMLElement | null>(null)
const dialog = ref<HTMLElement | null>(null)
const stageSize = reactive({ width: 1, height: 1 })
let observer: ResizeObserver | null = null
type Gesture =
  | { mode: 'draw'; startX: number; startY: number; index: number }
  | { mode: 'move'; index: number; offsetX: number; offsetY: number }
  | { mode: 'resize'; index: number }
let gesture: Gesture | null = null
// Mover/redimensionar só entra no histórico do "Desfazer" quando algo muda de fato (um clique só seleciona).
let pendingSnapshot = false

const full = computed(() => state.boxes.length >= MAX_BOXES)
const handleW = computed(() => 16 / stageSize.width)
const handleH = computed(() => 16 / stageSize.height)

function clamp(value: number) {
  return Math.min(1, Math.max(0, value))
}

function snapshot() {
  history.push(JSON.stringify(state.boxes))
  if (history.length > 100) history.shift()
  state.undoCount = history.length
  state.dirty = true
}

function undo() {
  const previous = history.pop()
  state.undoCount = history.length
  if (previous === undefined) return
  state.boxes = JSON.parse(previous)
  state.selected = Math.min(state.selected, state.boxes.length - 1)
}

async function load() {
  state.loading = true
  state.error = ''
  state.boxes = []
  state.selected = -1
  state.dirty = false
  history.length = 0
  state.undoCount = 0
  try {
    const view = await api.getOcclusions(props.studyId, props.mediaId)
    state.boxes = view.cards.map((card) => ({
      key: nextKey++, id: card.id, x: card.x, y: card.y, width: card.width, height: card.height, label: card.label,
    }))
  } catch (error) {
    state.error = errorMessage(error)
  } finally {
    state.loading = false
  }
}

watch(() => props.open, async (isOpen) => {
  if (!isOpen) return
  await load()
  await nextTick()
  dialog.value?.focus()
  if (stage.value && typeof ResizeObserver !== 'undefined') {
    observer?.disconnect()
    observer = new ResizeObserver(([entry]) => {
      stageSize.width = Math.max(1, entry.contentRect.width)
      stageSize.height = Math.max(1, entry.contentRect.height)
    })
    observer.observe(stage.value)
  }
}, { immediate: true })

onBeforeUnmount(() => observer?.disconnect())

function point(event: PointerEvent) {
  const rect = stage.value!.getBoundingClientRect()
  return { x: clamp((event.clientX - rect.left) / rect.width), y: clamp((event.clientY - rect.top) / rect.height) }
}

function startDraw(event: PointerEvent) {
  if (!stage.value || state.loading) return
  if (full.value) {
    state.error = `No máximo ${MAX_BOXES} áreas por imagem.`
    return
  }
  const { x, y } = point(event)
  snapshot()
  state.boxes.push({ key: nextKey++, x, y, width: 0, height: 0, label: '' })
  state.selected = state.boxes.length - 1
  gesture = { mode: 'draw', startX: x, startY: y, index: state.selected }
  stage.value.setPointerCapture(event.pointerId)
}

function startMove(event: PointerEvent, index: number) {
  if (!stage.value) return
  event.stopPropagation()
  const { x, y } = point(event)
  const box = state.boxes[index]
  pendingSnapshot = true
  state.selected = index
  gesture = { mode: 'move', index, offsetX: x - box.x, offsetY: y - box.y }
  stage.value.setPointerCapture(event.pointerId)
}

function startResize(event: PointerEvent, index: number) {
  if (!stage.value) return
  event.stopPropagation()
  pendingSnapshot = true
  state.selected = index
  gesture = { mode: 'resize', index }
  stage.value.setPointerCapture(event.pointerId)
}

function onMove(event: PointerEvent) {
  if (!gesture) return
  const { x, y } = point(event)
  const box = state.boxes[gesture.index]
  if (!box) return
  if (pendingSnapshot) {
    pendingSnapshot = false
    snapshot()
  }
  if (gesture.mode === 'draw') {
    box.x = Math.min(gesture.startX, x)
    box.y = Math.min(gesture.startY, y)
    box.width = Math.abs(x - gesture.startX)
    box.height = Math.abs(y - gesture.startY)
  } else if (gesture.mode === 'move') {
    box.x = clamp(Math.min(x - gesture.offsetX, 1 - box.width))
    box.y = clamp(Math.min(y - gesture.offsetY, 1 - box.height))
  } else {
    box.width = Math.max(MIN_SIDE, x - box.x)
    box.height = Math.max(MIN_SIDE, y - box.y)
  }
}

function onUp() {
  if (gesture?.mode === 'draw') {
    const box = state.boxes[gesture.index]
    if (box && (box.width < MIN_SIDE * 2 || box.height < MIN_SIDE * 2)) {
      // Um toque sem arrastar não cria área.
      state.boxes.splice(gesture.index, 1)
      history.pop()
      state.undoCount = history.length
      state.selected = -1
    }
  }
  gesture = null
  pendingSnapshot = false
}

function remove(index: number) {
  snapshot()
  state.boxes.splice(index, 1)
  state.selected = Math.min(index, state.boxes.length - 1)
}

function nudge(index: number, dx: number, dy: number) {
  const box = state.boxes[index]
  snapshot()
  box.x = clamp(Math.min(box.x + dx, 1 - box.width))
  box.y = clamp(Math.min(box.y + dy, 1 - box.height))
}

function onBoxKey(event: KeyboardEvent, index: number) {
  const step = event.shiftKey ? STEP * 5 : STEP
  const moves: Record<string, [number, number]> = {
    ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step],
  }
  if (event.key === 'Delete' || event.key === 'Backspace') {
    event.preventDefault()
    remove(index)
  } else if (moves[event.key]) {
    event.preventDefault()
    nudge(index, ...moves[event.key])
  }
}

function onDialogKey(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    close()
  } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
    const tag = (event.target as HTMLElement)?.tagName
    if (tag === 'INPUT') return
    event.preventDefault()
    undo()
  }
}

function close() {
  if (state.saving) return
  emit('close')
}

async function save() {
  state.saving = true
  state.error = ''
  try {
    const cards = state.boxes.map(({ id, x, y, width, height, label }) => ({
      ...(id ? { id } : {}), x, y, width, height, label: label.trim(),
    }))
    const view = await api.saveOcclusions(props.studyId, props.mediaId, cards)
    state.dirty = false
    emit('saved', view.cards.length)
    emit('close')
  } catch (error) {
    state.error = errorMessage(error)
  } finally {
    state.saving = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop occlusion-backdrop" @keydown="onDialogKey">
      <div
        ref="dialog"
        class="occlusion-dialog panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="occlusion-title"
        tabindex="-1"
      >
        <header class="occlusion-header">
          <h2 id="occlusion-title">Cartões nesta imagem</h2>
          <button type="button" class="secondary icon-only" aria-label="Fechar sem salvar" @click="close">
            <Icon name="x" :size="18" aria-hidden="true" />
          </button>
        </header>
        <p class="occlusion-help">
          Arraste sobre a imagem para cobrir uma parte; cada área vira um cartão de revisão. Arraste uma área para
          movê-la e o canto para mudar o tamanho. Com uma área selecionada: Delete apaga e as setas movem.
        </p>
        <p v-if="state.error" class="notice error" role="alert">{{ state.error }}</p>
        <p v-if="state.loading" class="muted" role="status">Carregando a imagem…</p>

        <div class="occlusion-body">
          <div
            ref="stage"
            class="occlusion-editor-stage"
            @pointerdown="startDraw"
            @pointermove="onMove"
            @pointerup="onUp"
            @pointercancel="onUp"
          >
            <img
              :src="`/api/media/${encodeURIComponent(mediaId)}/content`"
              alt="Imagem do estudo para criar cartões"
              draggable="false"
            >
            <svg class="occlusion-editor-layer" viewBox="0 0 1 1" preserveAspectRatio="none">
              <g
                v-for="(box, index) in state.boxes"
                :key="box.key"
                class="occlusion-box"
                :class="{ selected: index === state.selected }"
                role="button"
                tabindex="0"
                :aria-label="`Área ${index + 1}${box.label ? `: ${box.label}` : ''}`"
                :aria-pressed="index === state.selected"
                @pointerdown="startMove($event, index)"
                @focus="state.selected = index"
                @keydown="onBoxKey($event, index)"
              >
                <rect
                  :x="box.x"
                  :y="box.y"
                  :width="box.width"
                  :height="box.height"
                  class="occlusion-box-rect"
                  vector-effect="non-scaling-stroke"
                />
                <rect
                  v-if="index === state.selected"
                  :x="box.x + box.width - handleW / 2"
                  :y="box.y + box.height - handleH / 2"
                  :width="handleW"
                  :height="handleH"
                  class="occlusion-handle"
                  vector-effect="non-scaling-stroke"
                  @pointerdown="startResize($event, index)"
                />
              </g>
            </svg>
            <span
              v-for="(box, index) in state.boxes"
              :key="`n-${box.key}`"
              class="occlusion-number"
              :style="{ left: `${box.x * 100}%`, top: `${box.y * 100}%` }"
              aria-hidden="true"
            >{{ index + 1 }}</span>
          </div>

          <aside class="occlusion-list" aria-label="Áreas e respostas">
            <p class="occlusion-count">{{ state.boxes.length }} de {{ MAX_BOXES }} áreas</p>
            <p v-if="!state.boxes.length && !state.loading" class="muted">Nenhuma área ainda.</p>
            <ol>
              <li
                v-for="(box, index) in state.boxes"
                :key="box.key"
                :class="{ selected: index === state.selected }"
              >
                <label :for="`occlusion-label-${box.key}`">Área {{ index + 1 }} — resposta (opcional)</label>
                <div class="occlusion-row">
                  <input
                    :id="`occlusion-label-${box.key}`"
                    v-model="box.label"
                    type="text"
                    maxlength="200"
                    placeholder="Ex.: Ventrículo esquerdo"
                    @focus="state.selected = index"
                    @input="state.dirty = true"
                  >
                  <button
                    type="button"
                    class="secondary icon-only"
                    :aria-label="`Apagar a área ${index + 1}`"
                    @click="remove(index)"
                  >
                    <Icon name="trash" :size="16" aria-hidden="true" />
                  </button>
                </div>
              </li>
            </ol>
          </aside>
        </div>

        <footer class="occlusion-footer">
          <p class="muted keep-note">Ao salvar, esta foto passa a ser mantida para sempre (não expira).</p>
          <div class="occlusion-actions">
            <button type="button" class="secondary" :disabled="!state.undoCount || state.saving" @click="undo">
              Desfazer
            </button>
            <button type="button" class="secondary" :disabled="state.saving" @click="close">Cancelar</button>
            <button type="button" class="primary" :disabled="state.saving || state.loading" @click="save">
              {{ state.saving ? 'Salvando…' : 'Salvar cartões' }}
            </button>
          </div>
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.occlusion-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.55);
}

.occlusion-dialog {
  width: min(1100px, 100%);
  max-height: calc(100dvh - 2rem);
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
}

.occlusion-dialog:focus {
  outline: none;
}

.occlusion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.occlusion-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.occlusion-help,
.keep-note {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.92rem;
}

.occlusion-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 1rem;
  align-items: start;
}

.occlusion-editor-stage {
  position: relative;
  touch-action: none;
  user-select: none;
  cursor: crosshair;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  overflow: hidden;
  background: var(--color-surface-soft);
}

.occlusion-editor-stage img {
  display: block;
  width: 100%;
  height: auto;
  pointer-events: none;
}

.occlusion-editor-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.occlusion-box {
  cursor: move;
  outline: none;
}

.occlusion-box-rect {
  fill: var(--color-accent);
  fill-opacity: 0.55;
  stroke: var(--color-text);
  stroke-width: 2;
}

.occlusion-box.selected .occlusion-box-rect,
.occlusion-box:focus-visible .occlusion-box-rect {
  fill-opacity: 0.75;
  stroke-width: 3;
  stroke-dasharray: 6 3;
}

.occlusion-handle {
  fill: var(--color-surface);
  stroke: var(--color-text);
  stroke-width: 2;
  cursor: nwse-resize;
}

.occlusion-number {
  position: absolute;
  transform: translate(2px, 2px);
  min-width: 1.4rem;
  padding: 0 0.3rem;
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  pointer-events: none;
}

.occlusion-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.occlusion-count {
  margin: 0;
  font-weight: 600;
}

.occlusion-list ol {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 55vh;
  overflow: auto;
}

.occlusion-list li {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-button);
}

.occlusion-list li.selected {
  border-color: var(--color-accent);
}

.occlusion-list label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.occlusion-row {
  display: flex;
  gap: 0.4rem;
}

.occlusion-row input {
  flex: 1;
  min-width: 0;
}

.occlusion-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.occlusion-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 760px) {
  .occlusion-backdrop {
    padding: 0;
  }

  .occlusion-dialog {
    max-height: 100dvh;
    height: 100dvh;
    border-radius: 0;
    padding: 0.75rem 1rem;
  }

  .occlusion-body {
    grid-template-columns: 1fr;
  }

  .occlusion-list ol {
    max-height: none;
  }

  .occlusion-actions {
    width: 100%;
  }

  .occlusion-actions button {
    flex: 1;
    min-height: 44px;
  }
}
</style>
