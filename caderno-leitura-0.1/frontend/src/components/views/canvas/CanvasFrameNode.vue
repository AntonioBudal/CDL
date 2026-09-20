<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CanvasFrameItem } from '../../../types'
import Icon from '../../ui/Icon.vue'

interface Props {
  frame: CanvasFrameItem
  isSelected?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
})

const emit = defineEmits<{
  (e: 'select', frameId: number): void
  (e: 'drag-start', frameId: number, screenX: number, screenY: number): void
  (e: 'resize-start', frameId: number, screenX: number, screenY: number): void
  (e: 'update-title', frameId: number, newTitle: string): void
  (e: 'update-color', frameId: number, newColor: string): void
  (e: 'delete', frameId: number): void
}>()

const isEditingTitle = ref(false)
const editedTitle = ref(props.frame.title)

const availableColors = [
  { id: 'neutral', label: 'Cinza', bg: 'rgba(100, 116, 139, 0.08)', border: '#cbd5e1' },
  { id: 'amber', label: 'Âmbar', bg: 'rgba(245, 158, 11, 0.08)', border: '#fcd34d' },
  { id: 'indigo', label: 'Índigo', bg: 'rgba(99, 102, 241, 0.08)', border: '#a5b4fc' },
  { id: 'emerald', label: 'Esmeralda', bg: 'rgba(16, 185, 129, 0.08)', border: '#6ee7b7' },
  { id: 'rose', label: 'Rosa', bg: 'rgba(244, 63, 94, 0.08)', border: '#fda4af' },
  { id: 'sky', label: 'Céu', bg: 'rgba(14, 165, 233, 0.08)', border: '#7dd3fc' },
]

const currentColorConfig = computed(() => {
  return availableColors.find(c => c.id === props.frame.color) || availableColors[0]
})

function onHeaderPointerDown(e: PointerEvent) {
  if (e.button !== 0) return
  const target = e.target as HTMLElement
  if (target.closest('input') || target.closest('button')) return

  emit('select', props.frame.id)
  emit('drag-start', props.frame.id, e.clientX, e.clientY)
}

function onResizeHandlePointerDown(e: PointerEvent) {
  if (e.button !== 0) return
  e.stopPropagation()
  emit('select', props.frame.id)
  emit('resize-start', props.frame.id, e.clientX, e.clientY)
}

function startEditTitle() {
  editedTitle.value = props.frame.title
  isEditingTitle.value = true
}

function finishEditTitle() {
  isEditingTitle.value = false
  const trimmed = editedTitle.value.trim()
  if (trimmed && trimmed !== props.frame.title) {
    emit('update-title', props.frame.id, trimmed)
  }
}

function selectColor(colorId: string) {
  if (colorId !== props.frame.color) {
    emit('update-color', props.frame.id, colorId)
  }
}
</script>

<template>
  <div
    :id="`canvas-frame-${frame.id}`"
    class="canvas-frame-node"
    :class="{ 'is-selected': isSelected }"
    :style="{
      transform: `translate3d(${frame.pos_x}px, ${frame.pos_y}px, 0)`,
      width: `${frame.width}px`,
      height: `${frame.height}px`,
      backgroundColor: currentColorConfig.bg,
      borderColor: currentColorConfig.border,
    }"
    role="group"
    :aria-label="`Moldura: ${frame.title}`"
    @pointerdown="emit('select', frame.id)"
  >
    <div
      class="frame-header"
      @pointerdown="onHeaderPointerDown"
    >
      <div class="frame-title-area">
        <Icon name="folder" :size="16" class="frame-icon" aria-hidden="true" />
        <input
          v-if="isEditingTitle"
          v-model="editedTitle"
          type="text"
          class="frame-title-input"
          maxlength="100"
          autofocus
          @blur="finishEditTitle"
          @keydown.enter="finishEditTitle"
          @keydown.esc="isEditingTitle = false"
        />
        <span
          v-else
          class="frame-title-text"
          title="Clique duas vezes para renomear"
          @dblclick="startEditTitle"
        >
          {{ frame.title }}
        </span>
      </div>

      <div class="frame-header-actions">
        <div class="color-palette" role="group" aria-label="Cores da moldura">
          <button
            v-for="c in availableColors"
            :key="c.id"
            type="button"
            class="color-pill"
            :class="{ 'is-active': c.id === frame.color }"
            :style="{ backgroundColor: c.border }"
            :title="`Cor ${c.label}`"
            :aria-label="`Mudar cor para ${c.label}`"
            @click.stop="selectColor(c.id)"
          />
        </div>

        <button
          type="button"
          class="frame-delete-btn"
          title="Excluir moldura"
          aria-label="Excluir moldura"
          @click.stop="emit('delete', frame.id)"
        >
          <Icon name="x" :size="14" />
        </button>
      </div>
    </div>

    <!-- Interior transparente sem bloquear cliques nos cards -->
    <div class="frame-body" />

    <!-- Alça de redimensionamento no canto inferior direito -->
    <div
      class="frame-resize-handle"
      role="button"
      tabindex="0"
      aria-label="Redimensionar moldura"
      title="Arrastar para redimensionar"
      @pointerdown="onResizeHandlePointerDown"
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="resize-dots" aria-hidden="true">
        <circle cx="10" cy="10" r="1.5" fill="currentColor" />
        <circle cx="6" cy="10" r="1.5" fill="currentColor" />
        <circle cx="10" cy="6" r="1.5" fill="currentColor" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.canvas-frame-node {
  position: absolute;
  top: 0;
  left: 0;
  box-sizing: border-box;
  border: 2px dashed #94a3b8;
  border-radius: 12px;
  z-index: 1; /* Abaixo dos cartões (z-index >= 2) e acima do grid */
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
  pointer-events: all;
}

.canvas-frame-node.is-selected {
  border-style: solid;
  border-color: var(--accent-color, #3b82f6) !important;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

.frame-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 38px;
  padding: 0 10px;
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 10px 10px 0 0;
  cursor: grab;
  user-select: none;
}

.frame-header:active {
  cursor: grabbing;
}

.frame-title-area {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.frame-icon {
  color: var(--text-secondary, #64748b);
  flex-shrink: 0;
}

.frame-title-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
}

.frame-title-input {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 2px 6px;
  border: 1px solid var(--accent-color, #3b82f6);
  border-radius: 4px;
  outline: none;
  background: #ffffff;
  color: #0f172a;
  max-width: 180px;
}

.frame-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-palette {
  display: flex;
  align-items: center;
  gap: 4px;
}

.color-pill {
  width: 16px;
  height: 16px;
  min-width: 16px;
  min-height: 16px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.15);
  cursor: pointer;
  padding: 0;
  transition: transform 0.1s ease;
}

.color-pill:hover {
  transform: scale(1.2);
}

.color-pill.is-active {
  box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px var(--accent-color, #3b82f6);
}

.frame-delete-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  transition: color 0.15s, background-color 0.15s;
}

.frame-delete-btn:hover {
  color: #ef4444;
  background-color: #fee2e2;
}

.frame-body {
  width: 100%;
  height: calc(100% - 38px);
  pointer-events: none; /* Não captura cliques para permitir interação com os nós dentro */
}

.frame-resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: nwse-resize;
  color: var(--text-muted, #94a3b8);
  user-select: none;
}

.frame-resize-handle:hover {
  color: var(--accent-color, #3b82f6);
}

.resize-dots {
  position: absolute;
  bottom: 4px;
  right: 4px;
}
</style>
