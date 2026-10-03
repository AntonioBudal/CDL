<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HighlightColor, TextSelectionContext } from '../types.ts'
import {
  HIGHLIGHT_COLOR_HEX,
  HIGHLIGHT_COLOR_OPTIONS,
} from '../types/toolbar.ts'
import { computeToolbarPosition } from '../utils/toolbarPosition.ts'
import { useHighlightColorPreference } from '../composables/useHighlightColorPreference.ts'

const props = withDefaults(
  defineProps<{
    visible: boolean
    selection: TextSelectionContext | null
    studyTitle: string
    bookTitle?: string
    chapterName?: string
    canEdit?: boolean
  }>(),
  {
    canEdit: true,
    bookTitle: '',
    chapterName: '',
  },
)

const emit = defineEmits<{
  (e: 'highlight', payload: { color: HighlightColor; selection: TextSelectionContext }): void
  (e: 'annotate', payload: { note: string; color: HighlightColor; selection: TextSelectionContext }): void
  (e: 'copy-quote', payload: { selection: TextSelectionContext }): void
  (e: 'occlude', payload: { selection: TextSelectionContext }): void
  (e: 'ask-question', payload: { question: string; selection: TextSelectionContext }): void
  (e: 'open-note', payload: { selection: TextSelectionContext }): void
  (e: 'open-question', payload: { selection: TextSelectionContext }): void
  (e: 'tool-selected', payload: { tool: string; label: string; colorDot?: string }): void
  (e: 'close'): void
}>()

const toolbarRef = ref<HTMLElement | null>(null)
const splitButtonRef = ref<HTMLElement | null>(null)
const currentSelection = ref<TextSelectionContext | null>(null)
const isPaletteOpen = ref(false)
const isMobile = ref(false)

const { activeColor, colorHex, colorLabel, setColor } = useHighlightColorPreference()

watch(
  () => props.selection,
  (sel) => {
    if (sel) {
      currentSelection.value = sel
    }
  },
  { immediate: true },
)

function checkMobile() {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth <= 768
  }
}

const positionStyle = computed(() => {
  const activeSel = props.selection || currentSelection.value
  if (!props.visible || !activeSel) return { display: 'none' }

  const rect = activeSel.boundingRect
  const vpWidth = typeof window !== 'undefined' ? window.innerWidth : 1280
  const vpHeight = typeof window !== 'undefined' ? window.innerHeight : 800

  const toolbarWidth = isMobile.value ? vpWidth : (toolbarRef.value?.offsetWidth || 340)
  const toolbarHeight = toolbarRef.value?.offsetHeight || 48

  const pos = computeToolbarPosition({
    selectionRect: {
      top: rect.top,
      bottom: rect.bottom,
      left: rect.left,
      right: rect.right,
      width: rect.width,
      height: rect.height,
    },
    toolbarWidth,
    toolbarHeight,
    viewportWidth: vpWidth,
    viewportHeight: vpHeight,
    isMobile: isMobile.value,
  })

  if (pos.isBottomDocked) {
    return {
      position: 'fixed' as const,
      bottom: pos.bottom,
      left: pos.left,
      right: '0px',
      zIndex: 9999,
    }
  }

  return {
    position: 'fixed' as const,
    top: pos.top,
    left: pos.left,
    zIndex: 9999,
  }
})

function handleToolbarMouseDown(event: MouseEvent) {
  const target = event.target as HTMLElement | null
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
    return
  }
  event.preventDefault()
}

function togglePalette() {
  isPaletteOpen.value = !isPaletteOpen.value
}

function selectColorAndApply(color: HighlightColor) {
  setColor(color)
  isPaletteOpen.value = false
  applyHighlight(color)
}

function applyHighlight(color: HighlightColor) {
  const sel = currentSelection.value || props.selection
  if (!sel) return
  const dotColor = HIGHLIGHT_COLOR_HEX[color] || '#fef08a'
  emit('tool-selected', { tool: 'highlight', label: 'Destaque aplicado', colorDot: dotColor })
  emit('highlight', { color, selection: sel })
  reset()
}

function triggerOpenNote() {
  const sel = currentSelection.value || props.selection
  if (!sel) return
  emit('tool-selected', { tool: 'note', label: 'Adicionar anotação' })
  emit('open-note', { selection: sel })
}

function triggerOpenQuestion() {
  const sel = currentSelection.value || props.selection
  if (!sel) return
  emit('tool-selected', { tool: 'question', label: 'Criar pergunta' })
  emit('open-question', { selection: sel })
}

function triggerOcclude() {
  const sel = currentSelection.value || props.selection
  if (!sel) return
  emit('tool-selected', { tool: 'occlude', label: 'Trecho ocultado para revisão' })
  emit('occlude', { selection: sel })
  reset()
}

function triggerQuote() {
  const sel = currentSelection.value || props.selection
  if (!sel) return
  emit('tool-selected', { tool: 'copy-quote', label: 'Citação copiada' })
  emit('copy-quote', { selection: sel })
  reset()
}

function reset() {
  isPaletteOpen.value = false
  currentSelection.value = null
  emit('close')
}

function handleKeydown(event: KeyboardEvent) {
  if (!props.visible) return
  if (event.key === 'Escape') {
    if (isPaletteOpen.value) {
      isPaletteOpen.value = false
      return
    }
    reset()
  }
}

function handleClickOutside(event: MouseEvent | TouchEvent) {
  if (!props.visible || !toolbarRef.value) return
  const target = event.target as Node
  if (!toolbarRef.value.contains(target)) {
    reset()
  } else if (isPaletteOpen.value && splitButtonRef.value && !splitButtonRef.value.contains(target)) {
    isPaletteOpen.value = false
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      isPaletteOpen.value = false
      checkMobile()
    }
  },
)

onMounted(() => {
  checkMobile()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', checkMobile)
    window.addEventListener('keydown', handleKeydown)
    document.addEventListener('mousedown', handleClickOutside)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', checkMobile)
    window.removeEventListener('keydown', handleKeydown)
    document.removeEventListener('mousedown', handleClickOutside)
  }
})
</script>

<template>
  <div
    v-if="visible && (selection || currentSelection)"
    ref="toolbarRef"
    class="floating-actions-toolbar"
    :class="{ 'is-mobile': isMobile }"
    :style="positionStyle"
    role="toolbar"
    aria-label="Ações para o trecho selecionado"
    @mousedown="handleToolbarMouseDown"
  >
    <!-- Ação 1: Split Button de Marca-Texto -->
    <div v-if="canEdit" ref="splitButtonRef" class="split-button">
      <button
        type="button"
        class="toolbar-btn split-trigger"
        :title="`Destacar com marca-texto (${colorLabel})`"
        :aria-label="`Destacar com marca-texto (${colorLabel})`"
        @click="applyHighlight(activeColor)"
      >
        <span
          class="color-dot"
          :style="{ backgroundColor: colorHex }"
        ></span>
        <span class="btn-text">Destacar</span>
      </button>

      <button
        type="button"
        class="toolbar-btn split-expand"
        title="Escolher cor do marca-texto"
        aria-label="Escolher cor do marca-texto"
        :aria-expanded="isPaletteOpen"
        aria-haspopup="true"
        @click.stop="togglePalette"
      >
        <svg class="chevron-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      <!-- Paleta suspensa de 5 cores -->
      <Transition name="palette-fade">
        <div
          v-if="isPaletteOpen"
          class="split-palette-popover"
          role="region"
          aria-label="Cores do marca-texto"
          @mousedown.stop
        >
          <button
            v-for="color in HIGHLIGHT_COLOR_OPTIONS"
            :key="color.id"
            type="button"
            class="color-choice-btn"
            :class="{ 'is-active': color.id === activeColor }"
            :style="{ backgroundColor: color.bg, borderColor: color.border }"
            :title="color.label"
            :aria-label="color.label"
            @click="selectColorAndApply(color.id)"
          ></button>
        </div>
      </Transition>
    </div>

    <div v-if="canEdit" class="toolbar-divider" aria-hidden="true"></div>

    <!-- Ação 2: Anotar -->
    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      title="Adicionar anotação vinculada"
      aria-label="Adicionar anotação vinculada"
      @click="triggerOpenNote"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
      <span class="btn-text">Anotar</span>
    </button>

    <!-- Ação 3: Copiar Citação -->
    <button
      type="button"
      class="toolbar-btn"
      title="Copiar citação formatada"
      aria-label="Copiar como citação"
      @click="triggerQuote"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
        <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
      </svg>
      <span class="btn-text">Citação</span>
    </button>

    <div v-if="canEdit" class="toolbar-divider" aria-hidden="true"></div>

    <!-- Ação 4: Ocultar Trecho (Oclusão) -->
    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      title="Ocultar trecho (Active Recall)"
      aria-label="Ocultar trecho para estudo ativo"
      @click="triggerOcclude"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </svg>
      <span class="btn-text">Ocultar</span>
    </button>

    <!-- Ação 5: Pergunta -->
    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      title="Transformar em pergunta"
      aria-label="Transformar trecho em pergunta"
      @click="triggerOpenQuestion"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <span class="btn-text">Pergunta</span>
    </button>

    <!-- Botão Fechar -->
    <button
      type="button"
      class="toolbar-btn icon-only close-btn"
      title="Fechar barra"
      aria-label="Fechar barra de ações"
      @click="reset"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.floating-actions-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(12px);
  user-select: none;
  font-family: inherit;
  font-size: 0.8125rem;
  transition: opacity 0.15s ease, transform 0.15s ease;
}

/* Modo Mobile: Barra ancorada na base com ícones puros de 44x44px */
.floating-actions-toolbar.is-mobile {
  border-radius: 16px 16px 0 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
  padding: 8px 12px calc(8px + env(safe-area-inset-bottom, 0px)) 12px;
  justify-content: space-around;
  width: 100%;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-primary, #18181b);
  border-radius: 9999px;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: background-color 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

/* No mobile, oculta textos e assegura botões de no mínimo 44x44px */
.is-mobile .toolbar-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}

.is-mobile .toolbar-btn .btn-text {
  display: none;
}

.is-mobile .toolbar-btn.icon-only {
  border-radius: 9999px;
}

.toolbar-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.06));
}

.toolbar-btn:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 1px;
}

.toolbar-btn.icon-only {
  padding: 6px 8px;
  border-radius: 50%;
}

/* Split Button de Marca-Texto */
.split-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  background: transparent;
  transition: background-color 0.15s ease;
}

.split-button:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.04));
}

.split-trigger {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  padding-right: 6px;
}

.split-expand {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  padding: 6px 6px;
  margin-left: -2px;
}

.is-mobile .split-button {
  display: flex;
  align-items: center;
}

.is-mobile .split-trigger {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 0.35rem 0.5rem 0.5rem;
}

.is-mobile .split-expand {
  min-height: 44px;
  min-width: 28px;
  padding: 0.5rem 0.35rem;
}

.chevron-svg {
  width: 14px;
  height: 14px;
  transition: transform 0.15s ease;
}

.split-expand[aria-expanded="true"] .chevron-svg {
  transform: rotate(180deg);
}

/* Paleta rápida suspensa */
.split-palette-popover {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(12px);
  z-index: 10000;
}

.is-mobile .split-palette-popover {
  top: auto;
  bottom: calc(100% + 12px);
  left: 12px;
  gap: 12px;
  padding: 8px 14px;
}

.palette-fade-enter-active,
.palette-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.palette-fade-enter-from,
.palette-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.is-mobile .palette-fade-enter-from,
.is-mobile .palette-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.15);
  display: inline-block;
  flex-shrink: 0;
}

.is-mobile .color-dot {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.color-choice-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.is-mobile .color-choice-btn {
  width: 36px;
  height: 36px;
}

.color-choice-btn:hover {
  transform: scale(1.18);
}

.color-choice-btn.is-active {
  box-shadow: 0 0 0 2px var(--color-primary, #3b82f6);
}

.icon-svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.is-mobile .icon-svg {
  width: 22px;
  height: 22px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border, #e4e4e7);
  margin: 0 2px;
}

.is-mobile .toolbar-divider {
  display: none;
}

/* Compatibilidade de layout para elementos de prompt no mobile */
.is-mobile .prompt-container {
  min-width: 0;
  width: 100%;
  padding: 4px;
}

.is-mobile .prompt-textarea {
  font-size: 0.875rem;
  padding: 8px;
  max-height: 80px;
}

.is-mobile .prompt-input {
  font-size: 0.875rem;
  padding: 8px;
  height: 40px;
}

.is-mobile .prompt-actions {
  gap: 6px;
  width: 100%;
}
</style>
