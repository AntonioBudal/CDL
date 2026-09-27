<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HighlightColor, TextSelectionContext } from '../types.ts'
import { computeToolbarPosition } from '../utils/toolbarPosition.ts'

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
  (e: 'highlight', payload: { color: HighlightColor }): void
  (e: 'annotate', payload: { note: string; color: HighlightColor }): void
  (e: 'copy-quote'): void
  (e: 'occlude'): void
  (e: 'ask-question', payload: { question: string }): void
  (e: 'close'): void
}>()

const toolbarRef = ref<HTMLElement | null>(null)
const noteInputRef = ref<HTMLTextAreaElement | null>(null)
const questionInputRef = ref<HTMLInputElement | null>(null)

type Mode = 'actions' | 'color_picker' | 'note' | 'question'
const mode = ref<Mode>('actions')
const selectedColor = ref<HighlightColor>('yellow')
const noteText = ref('')
const questionText = ref('')
const isMobile = ref(false)

const colors: { id: HighlightColor; label: string; bg: string; border: string }[] = [
  { id: 'yellow', label: 'Amarelo', bg: '#fef08a', border: '#facc15' },
  { id: 'green', label: 'Verde', bg: '#bbf7d0', border: '#4ade80' },
  { id: 'blue', label: 'Azul', bg: '#bae6fd', border: '#38bdf8' },
  { id: 'pink', label: 'Rosa', bg: '#fbcfe8', border: '#f472b6' },
  { id: 'purple', label: 'Lilás', bg: '#e9d5ff', border: '#c084fc' },
]

function checkMobile() {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth <= 768
  }
}

const positionStyle = computed(() => {
  if (!props.visible || !props.selection) return { display: 'none' }

  const rect = props.selection.boundingRect
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

function applyHighlight(color: HighlightColor) {
  selectedColor.value = color
  emit('highlight', { color })
  reset()
}

function openNotePrompt() {
  mode.value = 'note'
  noteText.value = ''
  nextTick(() => {
    noteInputRef.value?.focus()
  })
}

function submitNote() {
  const clean = noteText.value.trim()
  if (!clean) return
  emit('annotate', { note: clean, color: selectedColor.value })
  reset()
}

function openQuestionPrompt() {
  mode.value = 'question'
  questionText.value = ''
  nextTick(() => {
    questionInputRef.value?.focus()
  })
}

function submitQuestion() {
  const clean = questionText.value.trim()
  if (!clean) return
  emit('ask-question', { question: clean })
  reset()
}

function triggerOcclude() {
  emit('occlude')
  reset()
}

function triggerQuote() {
  emit('copy-quote')
  reset()
}

function reset() {
  mode.value = 'actions'
  noteText.value = ''
  questionText.value = ''
  emit('close')
}

function handleKeydown(event: KeyboardEvent) {
  if (!props.visible) return
  if (event.key === 'Escape') {
    reset()
  }
}

function handleClickOutside(event: MouseEvent | TouchEvent) {
  if (!props.visible || !toolbarRef.value) return
  const target = event.target as Node
  if (!toolbarRef.value.contains(target)) {
    // Se o clique for fora da barra flutuante, fecha
    reset()
  }
}

watch(
  () => props.visible,
  (val) => {
    if (val) {
      mode.value = 'actions'
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
    v-if="visible && selection"
    ref="toolbarRef"
    class="floating-actions-toolbar"
    :class="{ 'is-mobile': isMobile }"
    :style="positionStyle"
    role="toolbar"
    aria-label="Ações para o trecho selecionado"
  >
    <!-- MODO 1: Barra de Ações Principais -->
    <template v-if="mode === 'actions'">
      <!-- Ação 1: Destacar -->
      <button
        v-if="canEdit"
        type="button"
        class="toolbar-btn"
        title="Destacar com marca-texto"
        aria-label="Destacar com marca-texto"
        @click="applyHighlight(selectedColor)"
      >
        <span
          class="color-dot"
          :style="{ backgroundColor: colors.find((c) => c.id === selectedColor)?.bg || '#fef08a' }"
        ></span>
        <span>Destacar</span>
      </button>

      <!-- Botão para escolher outra cor -->
      <button
        v-if="canEdit"
        type="button"
        class="toolbar-btn icon-only"
        title="Outras cores"
        aria-label="Escolher cor do marca-texto"
        @click="mode = 'color_picker'"
      >
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="1" />
          <circle cx="12" cy="5" r="1" />
          <circle cx="12" cy="19" r="1" />
        </svg>
      </button>

      <div v-if="canEdit" class="toolbar-divider" aria-hidden="true"></div>

      <!-- Ação 2: Anotar -->
      <button
        v-if="canEdit"
        type="button"
        class="toolbar-btn"
        title="Adicionar anotação vinculada"
        aria-label="Adicionar anotação vinculada"
        @click="openNotePrompt"
      >
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
        <span>Anotar</span>
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
        <span>Citação</span>
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
        <span>Ocultar</span>
      </button>

      <!-- Ação 5: Pergunta -->
      <button
        v-if="canEdit"
        type="button"
        class="toolbar-btn"
        title="Transformar em pergunta"
        aria-label="Transformar trecho em pergunta"
        @click="openQuestionPrompt"
      >
        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span>Pergunta</span>
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
    </template>

    <!-- MODO 2: Seletor de Cores -->
    <template v-else-if="mode === 'color_picker'">
      <div class="color-picker-row">
        <span class="mode-label">Escolher cor:</span>
        <button
          v-for="color in colors"
          :key="color.id"
          type="button"
          class="color-choice-btn"
          :style="{ backgroundColor: color.bg, borderColor: color.border }"
          :title="color.label"
          :aria-label="color.label"
          @click="applyHighlight(color.id)"
        ></button>
        <button type="button" class="toolbar-btn back-btn" @click="mode = 'actions'">
          Voltar
        </button>
      </div>
    </template>

    <!-- MODO 3: Prompt de Anotação -->
    <template v-else-if="mode === 'note'">
      <div class="prompt-container">
        <label for="floating-note-input" class="sr-only">Sua anotação para o trecho</label>
        <textarea
          id="floating-note-input"
          ref="noteInputRef"
          v-model="noteText"
          class="prompt-textarea"
          rows="2"
          placeholder="Escreva sua reflexão sobre este trecho…"
          @keydown.enter.prevent="submitNote"
        ></textarea>
        <div class="prompt-actions">
          <button type="button" class="toolbar-btn submit-btn" :disabled="!noteText.trim()" @click="submitNote">
            Salvar nota
          </button>
          <button type="button" class="toolbar-btn back-btn" @click="mode = 'actions'">
            Cancelar
          </button>
        </div>
      </div>
    </template>

    <!-- MODO 4: Prompt de Pergunta -->
    <template v-else-if="mode === 'question'">
      <div class="prompt-container">
        <label for="floating-question-input" class="sr-only">Pergunta para estudo ativo</label>
        <input
          id="floating-question-input"
          ref="questionInputRef"
          v-model="questionText"
          type="text"
          class="prompt-input"
          placeholder="Ex: O que causou essa transformação?"
          @keydown.enter.prevent="submitQuestion"
        />
        <div class="prompt-actions">
          <button type="button" class="toolbar-btn submit-btn" :disabled="!questionText.trim()" @click="submitQuestion">
            Criar pergunta
          </button>
          <button type="button" class="toolbar-btn back-btn" @click="mode = 'actions'">
            Cancelar
          </button>
        </div>
      </div>
    </template>
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

/* Modo Mobile: Barra ancorada na base */
.floating-actions-toolbar.is-mobile {
  border-radius: 16px 16px 0 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 0px)) 12px;
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

.is-mobile .toolbar-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 8px 10px;
  flex-direction: column;
  gap: 4px;
  font-size: 0.75rem;
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

.is-mobile .toolbar-btn.icon-only {
  border-radius: 8px;
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.15);
  display: inline-block;
  flex-shrink: 0;
}

.icon-svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.is-mobile .icon-svg {
  width: 20px;
  height: 20px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border, #e4e4e7);
  margin: 0 2px;
}

.color-picker-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 6px;
}

.mode-label {
  font-size: 0.75rem;
  color: var(--color-text-muted, #71717a);
}

.color-choice-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.color-choice-btn:hover {
  transform: scale(1.2);
}

.prompt-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 280px;
  padding: 6px;
}

.prompt-textarea,
.prompt-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: 8px;
  background: var(--color-background, #fbfbfb);
  color: var(--color-text-primary, #18181b);
  font-family: inherit;
  font-size: 0.8125rem;
  resize: none;
  box-sizing: border-box;
}

.prompt-textarea:focus,
.prompt-input:focus {
  outline: 2px solid var(--color-primary, #3b82f6);
  border-color: transparent;
}

.prompt-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.submit-btn {
  background: var(--color-primary, #18181b);
  color: var(--color-surface, #ffffff);
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-hover, #27272a);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-btn {
  color: var(--color-text-muted, #71717a);
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
