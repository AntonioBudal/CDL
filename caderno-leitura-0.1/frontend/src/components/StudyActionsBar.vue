<script setup lang="ts">
/**
 * F0.12.10 (spec 123): barra de ações do estudo, fixa logo acima das abas das seções (estilo Word / Google Docs).
 * Substitui a barra que flutuava junto do trecho selecionado. Sempre visível e presa no alto ao rolar; sem trecho
 * selecionado, os botões ficam desativados. Os eventos são os mesmos da barra antiga, então o StudyView não muda de
 * comportamento. Clicar na barra não tira a seleção (mousedown.prevent), e a última seleção válida fica guardada.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { HighlightColor, TextSelectionContext } from '../types.ts'
import { HIGHLIGHT_COLOR_HEX, HIGHLIGHT_COLOR_OPTIONS } from '../types/toolbar.ts'
import { useHighlightColorPreference } from '../composables/useHighlightColorPreference.ts'

const props = withDefaults(
  defineProps<{
    /** Há um trecho que pode receber ações (seleção feita e nenhum popover aberto). */
    active: boolean
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
  (e: 'copy-quote', payload: { selection: TextSelectionContext }): void
  (e: 'occlude', payload: { selection: TextSelectionContext }): void
  (e: 'open-note', payload: { selection: TextSelectionContext }): void
  (e: 'open-question', payload: { selection: TextSelectionContext }): void
  (e: 'tool-selected', payload: { tool: string; label: string; colorDot?: string }): void
  (e: 'close'): void
}>()

const splitButtonRef = ref<HTMLElement | null>(null)
const currentSelection = ref<TextSelectionContext | null>(null)
const isPaletteOpen = ref(false)
const isMobile = ref(false)

const { activeColor, colorHex, colorLabel, setColor } = useHighlightColorPreference()

watch(
  () => props.selection,
  (sel) => {
    currentSelection.value = sel
    if (!sel) isPaletteOpen.value = false
  },
  { immediate: true },
)

const hasSelection = computed(() => props.active && Boolean(props.selection || currentSelection.value))

function checkMobile() {
  if (typeof window !== 'undefined') isMobile.value = window.innerWidth < 768
}

/** Clicar na barra não pode desfazer a seleção do texto (como no Docs); campos de texto seguem normais. */
function keepSelection(event: MouseEvent) {
  const target = event.target as HTMLElement | null
  if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) return
  event.preventDefault()
}

function activeSel(): TextSelectionContext | null {
  return hasSelection.value ? currentSelection.value || props.selection : null
}

function togglePalette() {
  if (!hasSelection.value) return
  isPaletteOpen.value = !isPaletteOpen.value
}

function selectColorAndApply(color: HighlightColor) {
  setColor(color)
  isPaletteOpen.value = false
  applyHighlight(color)
}

function applyHighlight(color: HighlightColor) {
  const sel = activeSel()
  if (!sel) return
  emit('tool-selected', { tool: 'highlight', label: 'Destaque aplicado', colorDot: HIGHLIGHT_COLOR_HEX[color] || '#fef08a' })
  emit('highlight', { color, selection: sel })
  reset()
}

function triggerOpenNote() {
  const sel = activeSel()
  if (!sel) return
  emit('tool-selected', { tool: 'note', label: 'Adicionar anotação' })
  emit('open-note', { selection: sel })
}

function triggerOpenQuestion() {
  const sel = activeSel()
  if (!sel) return
  emit('tool-selected', { tool: 'question', label: 'Criar pergunta' })
  emit('open-question', { selection: sel })
}

function triggerOcclude() {
  const sel = activeSel()
  if (!sel) return
  emit('tool-selected', { tool: 'occlude', label: 'Trecho ocultado para revisão' })
  emit('occlude', { selection: sel })
  reset()
}

function triggerQuote() {
  const sel = activeSel()
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
  if (event.key === 'Escape') {
    if (isPaletteOpen.value) {
      isPaletteOpen.value = false
    } else if (hasSelection.value) {
      reset()
    }
  }
}

function handleClickOutside(event: MouseEvent | TouchEvent) {
  if (isPaletteOpen.value && splitButtonRef.value && !splitButtonRef.value.contains(event.target as Node)) {
    isPaletteOpen.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  window.addEventListener('keydown', handleKeydown)
  document.addEventListener('mousedown', handleClickOutside)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div
    class="study-actions-bar"
    :class="{ 'is-mobile': isMobile, 'has-selection': hasSelection }"
    role="toolbar"
    aria-label="Ações para o trecho selecionado"
    @mousedown="keepSelection"
  >
    <!-- Destacar (com a cor escolhida) e escolher a cor -->
    <div v-if="canEdit" ref="splitButtonRef" class="split-button">
      <button
        type="button"
        class="toolbar-btn split-trigger"
        :disabled="!hasSelection"
        :title="`Destacar com marca-texto (${colorLabel})`"
        :aria-label="`Destacar com marca-texto (${colorLabel})`"
        @click="applyHighlight(activeColor)"
      >
        <span class="color-dot" :style="{ backgroundColor: colorHex }"></span>
        <span class="btn-text">Destacar</span>
      </button>
      <button
        type="button"
        class="toolbar-btn split-expand"
        :disabled="!hasSelection"
        title="Escolher cor do marca-texto"
        aria-label="Escolher cor do marca-texto"
        :aria-expanded="isPaletteOpen"
        aria-haspopup="true"
        @click.stop="togglePalette"
      >
        <svg class="chevron-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      <Transition name="palette-fade">
        <div
          v-if="isPaletteOpen"
          class="split-palette-popover"
          role="region"
          aria-label="Cores do marca-texto"
          @mousedown.stop.prevent
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

    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      :disabled="!hasSelection"
      title="Adicionar anotação vinculada"
      aria-label="Adicionar anotação vinculada"
      @click="triggerOpenNote"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
      <span class="btn-text">Anotar</span>
    </button>

    <button
      type="button"
      class="toolbar-btn"
      :disabled="!hasSelection"
      title="Copiar citação formatada"
      aria-label="Copiar como citação"
      @click="triggerQuote"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
        <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
      </svg>
      <span class="btn-text">Citação</span>
    </button>

    <div v-if="canEdit" class="toolbar-divider" aria-hidden="true"></div>

    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      :disabled="!hasSelection"
      title="Ocultar trecho (para lembrar sem olhar)"
      aria-label="Ocultar trecho para estudo ativo"
      @click="triggerOcclude"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
        <line x1="1" y1="1" x2="23" y2="23" />
      </svg>
      <span class="btn-text">Ocultar</span>
    </button>

    <button
      v-if="canEdit"
      type="button"
      class="toolbar-btn"
      :disabled="!hasSelection"
      title="Transformar em pergunta"
      aria-label="Transformar trecho em pergunta"
      @click="triggerOpenQuestion"
    >
      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <span class="btn-text">Pergunta</span>
    </button>

    <span class="bar-hint" aria-live="polite">
      {{ hasSelection ? '' : 'Selecione um trecho do texto para destacar, anotar ou citar.' }}
    </span>
  </div>
</template>

<style scoped>
/* Presa no alto ao rolar, logo acima das abas das seções (o cabeçalho global não é fixo, então top: 0). */
.study-actions-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 4px;
  min-height: 48px;
  padding: 4px 8px;
  background: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-panel, 8px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
  font-size: 0.8125rem;
  user-select: none;
}

.bar-hint {
  margin-left: auto;
  padding: 0 6px;
  color: var(--color-text-secondary);
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 10px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text);
  border-radius: var(--radius-button, 6px);
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--color-surface-soft);
}

.toolbar-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.toolbar-btn:disabled {
  cursor: default;
  color: var(--color-text-secondary);
  opacity: 0.6;
}

.split-button {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.split-trigger {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  padding-right: 6px;
}

.split-expand {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  padding: 6px;
  margin-left: -2px;
}

.chevron-svg {
  width: 14px;
  height: 14px;
  transition: transform 0.15s ease;
}

.split-expand[aria-expanded='true'] .chevron-svg {
  transform: rotate(180deg);
}

.split-palette-popover {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  z-index: 40;
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

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.15);
  display: inline-block;
  flex-shrink: 0;
}

.toolbar-btn:disabled .color-dot {
  opacity: 0.5;
}

.color-choice-btn {
  width: 26px;
  height: 26px;
  min-height: 0;
  min-width: 0;
  padding: 0;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.color-choice-btn:hover {
  transform: scale(1.18);
}

.color-choice-btn.is-active {
  box-shadow: 0 0 0 2px var(--color-accent);
}

.icon-svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.toolbar-divider {
  width: 1px;
  height: 22px;
  background: var(--color-border);
  margin: 0 4px;
  flex-shrink: 0;
}

/* A regra global dos botões (":root :is(button, .button):not(...)", 46 px) tem especificidade maior; estas a vencem. */
:root .study-actions-bar button.toolbar-btn {
  min-height: 36px;
}

:root .study-actions-bar button.color-choice-btn {
  min-height: 0;
  min-width: 0;
}

:root .study-actions-bar.is-mobile button.toolbar-btn {
  min-height: 44px;
}

/* Celular: presa no alto da tela, só ícones de 44 px (cabem em 320 px; sem rolagem, que cortaria a paleta). */
.study-actions-bar.is-mobile {
  gap: 2px;
  padding-inline: 4px;
}

.is-mobile .toolbar-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem;
}

.is-mobile .toolbar-btn .btn-text {
  display: none;
}

.is-mobile .split-trigger {
  padding: 0.5rem 0.35rem 0.5rem 0.5rem;
}

.is-mobile .split-expand {
  min-width: 28px;
  padding: 0.5rem 0.35rem;
}

.is-mobile .icon-svg {
  width: 22px;
  height: 22px;
}

.is-mobile .color-dot {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.is-mobile .color-choice-btn {
  width: 36px;
  height: 36px;
}

/* No celular a dica não cabe ao lado dos ícones: fica só para o leitor de tela. */
.is-mobile .bar-hint {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.is-mobile .toolbar-divider {
  margin: 0 1px;
}

/* Coluna do texto estreita (ex.: 768 px com o painel lateral): só ícones, a dica fica para o leitor de tela. */
.study-actions-bar {
  container-type: inline-size;
}

@container (max-width: 600px) {
  .toolbar-btn .btn-text {
    display: none;
  }

  .bar-hint {
    position: absolute;
    width: 1px;
    height: 1px;
    margin: -1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .toolbar-btn,
  .color-choice-btn,
  .palette-fade-enter-active,
  .palette-fade-leave-active {
    transition: none;
  }
}
</style>
