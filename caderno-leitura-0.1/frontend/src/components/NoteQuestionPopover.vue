<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HighlightColor, TextSelectionContext } from '../types.ts'
import { HIGHLIGHT_COLOR_HEX, HIGHLIGHT_COLOR_LABELS } from '../types/toolbar.ts'
import { computePopoverPosition } from '../utils/toolbarPosition.ts'

const props = withDefaults(
  defineProps<{
    visible: boolean
    kind: 'note' | 'question'
    selection: TextSelectionContext | null
    activeColor?: HighlightColor
    anchorRect?: DOMRect | null
  }>(),
  {
    activeColor: 'yellow',
    anchorRect: null,
  },
)

const emit = defineEmits<{
  (e: 'save', payload: {
    text: string
    color: HighlightColor
    kind: 'note' | 'question'
    selection: TextSelectionContext
  }): void
  (e: 'cancel'): void
}>()

const popoverRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const text = ref('')
const isMobile = ref(false)
const viewportOffsetBottom = ref(0)

function checkMobile() {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth <= 768
  }
}

function updateVisualViewport() {
  if (!isMobile.value || typeof window === 'undefined') {
    viewportOffsetBottom.value = 0
    return
  }
  const vv = window.visualViewport
  if (!vv) {
    viewportOffsetBottom.value = 0
    return
  }
  // No mobile, o teclado virtual diminui o visualViewport em relação ao window.innerHeight
  const offset = Math.max(0, window.innerHeight - (vv.offsetTop + vv.height))
  viewportOffsetBottom.value = Math.round(offset)
}

const colorDotBg = computed(() => {
  return HIGHLIGHT_COLOR_HEX[props.activeColor] || '#fef08a'
})

const colorLabel = computed(() => {
  return HIGHLIGHT_COLOR_LABELS[props.activeColor] || 'Amarelo'
})

const positionStyle = computed(() => {
  if (!props.visible) return { display: 'none' }

  if (isMobile.value) {
    return {
      position: 'fixed' as const,
      bottom: `${viewportOffsetBottom.value}px`,
      left: '0px',
      right: '0px',
      zIndex: 10001,
    }
  }

  const rect = props.anchorRect || props.selection?.boundingRect
  if (!rect) return { display: 'none' }

  const vpWidth = typeof window !== 'undefined' ? window.innerWidth : 1280
  const vpHeight = typeof window !== 'undefined' ? window.innerHeight : 800

  const popoverWidth = popoverRef.value?.offsetWidth || 340
  const popoverHeight = popoverRef.value?.offsetHeight || 160

  const pos = computePopoverPosition({
    selectionRect: {
      top: rect.top,
      bottom: rect.bottom,
      left: rect.left,
      right: rect.right,
      width: rect.width,
      height: rect.height,
    },
    popoverWidth,
    popoverHeight,
    viewportWidth: vpWidth,
    viewportHeight: vpHeight,
    isMobile: false,
  })

  return {
    position: 'fixed' as const,
    top: `${pos.top}px`,
    left: `${pos.left}px`,
    zIndex: 10001,
  }
})

function handleSave() {
  const clean = text.value.trim()
  if (!clean || !props.selection) return
  emit('save', {
    text: clean,
    color: props.activeColor,
    kind: props.kind,
    selection: props.selection,
  })
  text.value = ''
}

function handleCancel() {
  text.value = ''
  emit('cancel')
}

function handleTextareaKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSave()
  } else if (event.key === 'Escape') {
    event.preventDefault()
    handleCancel()
  }
}

function handleGlobalKeydown(event: KeyboardEvent) {
  if (!props.visible) return
  if (event.key === 'Escape') {
    handleCancel()
  }
}

function handleClickOutside(event: MouseEvent | TouchEvent) {
  if (!props.visible || !popoverRef.value) return
  const target = event.target as Node
  if (!popoverRef.value.contains(target)) {
    handleCancel()
  }
}

function focusInput() {
  nextTick(() => {
    textareaRef.value?.focus()
  })
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      text.value = ''
      checkMobile()
      updateVisualViewport()
      focusInput()
    }
  },
)

onMounted(() => {
  checkMobile()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', checkMobile)
    window.addEventListener('keydown', handleGlobalKeydown)
    document.addEventListener('mousedown', handleClickOutside)

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', updateVisualViewport)
      window.visualViewport.addEventListener('scroll', updateVisualViewport)
    }
  }
  if (props.visible) {
    focusInput()
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', checkMobile)
    window.removeEventListener('keydown', handleGlobalKeydown)
    document.removeEventListener('mousedown', handleClickOutside)

    if (window.visualViewport) {
      window.visualViewport.removeEventListener('resize', updateVisualViewport)
      window.visualViewport.removeEventListener('scroll', updateVisualViewport)
    }
  }
})
</script>

<template>
  <div
    v-if="visible"
    ref="popoverRef"
    class="note-question-popover"
    :class="{ 'is-mobile': isMobile, 'bottom-sheet': isMobile }"
    :style="positionStyle"
    role="dialog"
    aria-modal="true"
    :aria-label="kind === 'note' ? 'Adicionar anotação vinculada' : 'Criar pergunta para estudo ativo'"
    @mousedown.stop
  >
    <div class="popover-header">
      <div class="popover-title-row">
        <span
          v-if="kind === 'note'"
          class="color-dot"
          :style="{ backgroundColor: colorDotBg }"
          :title="`Cor: ${colorLabel}`"
        ></span>
        <svg
          v-else
          class="question-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span class="popover-title">
          {{ kind === 'note' ? 'Adicionar Anotação' : 'Criar Pergunta Reflexiva' }}
        </span>
      </div>
      <button
        type="button"
        class="icon-btn-close"
        title="Cancelar e fechar"
        aria-label="Cancelar e fechar"
        @click="handleCancel"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>

    <div class="popover-body">
      <label :for="`popover-input-${kind}`" class="sr-only">
        {{ kind === 'note' ? 'Texto da anotação' : 'Texto da pergunta' }}
      </label>
      <textarea
        :id="`popover-input-${kind}`"
        ref="textareaRef"
        v-model="text"
        class="popover-textarea"
        rows="3"
        :placeholder="
          kind === 'note'
            ? 'Escreva sua reflexão sobre este trecho…'
            : 'Ex: Qual a tese central defendida aqui?'
        "
        @keydown="handleTextareaKeydown"
      ></textarea>
      <span class="shortcut-hint">
        Pressione <kbd>Enter</kbd> para salvar ou <kbd>Shift + Enter</kbd> para quebrar linha
      </span>
    </div>

    <div class="popover-actions">
      <button
        type="button"
        class="action-btn cancel-btn"
        @click="handleCancel"
      >
        Cancelar
      </button>
      <button
        type="button"
        class="action-btn submit-btn"
        :disabled="!text.trim()"
        @click="handleSave"
      >
        {{ kind === 'note' ? 'Salvar anotação' : 'Criar pergunta' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.note-question-popover {
  display: flex;
  flex-direction: column;
  width: 360px;
  max-width: calc(100vw - 24px);
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 14px;
  box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.15), 0 4px 12px -2px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(12px);
  padding: 12px 14px;
  gap: 10px;
  font-family: inherit;
  font-size: 0.875rem;
  box-sizing: border-box;
}

/* Modo Mobile: Bottom Sheet */
.note-question-popover.bottom-sheet {
  width: 100%;
  max-width: 100vw;
  border-radius: 20px 20px 0 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
  padding: 14px 16px calc(14px + env(safe-area-inset-bottom, 0px)) 16px;
  box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.16);
  transition: bottom 0.15s ease-out;
}

.popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.popover-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--color-text-primary, #18181b);
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.15);
  display: inline-block;
  flex-shrink: 0;
}

.question-icon {
  width: 16px;
  height: 16px;
  color: var(--color-primary, #3b82f6);
  flex-shrink: 0;
}

.popover-title {
  font-size: 0.875rem;
  font-weight: 600;
}

.icon-btn-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #71717a);
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.is-mobile .icon-btn-close {
  width: 44px;
  height: 44px;
}

.icon-btn-close svg {
  width: 16px;
  height: 16px;
}

.icon-btn-close:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.06));
}

.popover-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.popover-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 8px;
  background: var(--color-background, #fafafa);
  color: var(--color-text-primary, #18181b);
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.45;
  resize: vertical;
  min-height: 72px;
  box-sizing: border-box;
}

.is-mobile .popover-textarea {
  font-size: 0.9375rem;
  min-height: 84px;
}

.popover-textarea:focus {
  outline: 2px solid var(--color-primary, #3b82f6);
  border-color: transparent;
  background: var(--color-surface, #ffffff);
}

.shortcut-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted, #71717a);
}

.is-mobile .shortcut-hint {
  display: none;
}

.shortcut-hint kbd {
  font-size: 0.7rem;
  padding: 1px 4px;
  border: 1px solid var(--color-border, #d4d4d8);
  border-radius: 4px;
  background: var(--color-surface-hover, #f4f4f5);
}

.popover-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 2px;
}

.is-mobile .popover-actions {
  gap: 10px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, opacity 0.15s ease;
  border: none;
}

.is-mobile .action-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 8px 18px;
  font-size: 0.875rem;
  flex: 1;
}

.cancel-btn {
  background: transparent;
  color: var(--color-text-muted, #71717a);
}

.cancel-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-text-primary, #18181b);
}

.submit-btn {
  background: var(--color-primary, #18181b);
  color: #ffffff;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-hover, #27272a);
}

.submit-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
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
</style>
