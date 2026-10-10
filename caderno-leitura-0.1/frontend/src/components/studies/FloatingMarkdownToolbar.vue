<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { applyFormatToTextarea, type MarkdownFormatAction } from '../../utils/markdownFormatter'

const props = defineProps<{
  targetId: string
  visible: boolean
  coords?: { x: number; y: number } | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'action', action: MarkdownFormatAction): void
}>()


function handleFormat(action: MarkdownFormatAction) {
  if (typeof document === 'undefined') return
  const textarea = document.getElementById(props.targetId) as HTMLTextAreaElement | null
  if (textarea) {
    applyFormatToTextarea(textarea, action)
    emit('action', action)
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.visible) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Transition name="floating-popover">
    <div
      v-if="visible"
      class="floating-markdown-toolbar"
      role="toolbar"
      aria-label="Ferramentas flutuantes de formatação"
      :style="coords ? { top: `${coords.y}px`, left: `${coords.x}px` } : undefined"
    >
      <!-- Negrito -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Negrito (Ctrl+B)"
        aria-label="Negrito"
        @mousedown.prevent="handleFormat('bold')"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
          <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
        </svg>
      </button>

      <!-- Itálico -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Itálico (Ctrl+I)"
        aria-label="Itálico"
        @mousedown.prevent="handleFormat('italic')"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="19" y1="4" x2="10" y2="4" />
          <line x1="14" y1="20" x2="5" y2="20" />
          <line x1="15" y1="4" x2="9" y2="20" />
        </svg>
      </button>

      <!-- Título H3 -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Título H3 (### Título)"
        aria-label="Título nível 3"
        @mousedown.prevent="handleFormat('heading')"
      >
        <span class="tool-text-badge">H3</span>
      </button>

      <div class="tool-divider" aria-hidden="true"></div>

      <!-- Tabela -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Inserir Tabela"
        aria-label="Inserir Tabela"
        @mousedown.prevent="handleFormat('table')"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <line x1="3" y1="9" x2="21" y2="9" />
          <line x1="3" y1="15" x2="21" y2="15" />
          <line x1="12" y1="3" x2="12" y2="21" />
        </svg>
      </button>

      <!-- Código -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Código (`código`)"
        aria-label="Código em linha"
        @mousedown.prevent="handleFormat('code')"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="16 18 22 12 16 6" />
          <polyline points="8 6 2 12 8 18" />
        </svg>
      </button>

      <!-- Link -->
      <button
        type="button"
        class="floating-tool-btn"
        title="Link (Ctrl+K)"
        aria-label="Link"
        @mousedown.prevent="handleFormat('link')"
      >
        <svg class="tool-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.floating-markdown-toolbar {
  position: absolute;
  z-index: 40;
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 6px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm, 6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(8px);
}

.floating-tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 140ms ease, color 140ms ease;
}

.floating-tool-btn:hover {
  color: var(--color-accent);
  background-color: var(--color-page);
}

.floating-tool-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.tool-icon {
  width: 15px;
  height: 15px;
}

.tool-text-badge {
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
}

.tool-divider {
  width: 1px;
  height: 16px;
  margin: 0 2px;
  background-color: var(--color-border);
}

/* Transições suaves */
.floating-popover-enter-active,
.floating-popover-leave-active {
  transition: opacity 160ms cubic-bezier(0.16, 1, 0.3, 1), transform 160ms cubic-bezier(0.16, 1, 0.3, 1);
}

.floating-popover-enter-from,
.floating-popover-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.97);
}

@media (prefers-reduced-motion: reduce) {
  .floating-popover-enter-active,
  .floating-popover-leave-active {
    transition-duration: 0.01ms !important;
  }
}
</style>
