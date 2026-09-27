<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { applyFormatToTextarea, type MarkdownFormatAction } from '../utils/markdownFormatter'

const props = defineProps<{
  targetId: string
}>()

function handleFormat(action: MarkdownFormatAction) {
  if (typeof document === 'undefined') return
  const textarea = document.getElementById(props.targetId) as HTMLTextAreaElement | null
  if (textarea) {
    applyFormatToTextarea(textarea, action)
  }
}

onMounted(() => {
  if (typeof document === 'undefined') return
  const textarea = document.getElementById(props.targetId) as HTMLTextAreaElement | null
  if (!textarea) return

  function onTextareaKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey) {
      if (e.key === 'b' || e.key === 'B') {
        e.preventDefault()
        handleFormat('bold')
      } else if (e.key === 'i' || e.key === 'I') {
        e.preventDefault()
        handleFormat('italic')
      } else if (e.key === 'k' || e.key === 'K') {
        e.preventDefault()
        handleFormat('link')
      }
    }
  }

  textarea.addEventListener('keydown', onTextareaKeydown)
  onBeforeUnmount(() => {
    textarea.removeEventListener('keydown', onTextareaKeydown)
  })
})
</script>

<template>
  <div
    class="markdown-toolbar"
    role="toolbar"
    aria-label="Ferramentas de formatação Markdown"
  >
    <!-- Negrito -->
    <button
      type="button"
      class="toolbar-btn"
      title="Negrito (**texto**)"
      aria-label="Negrito"
      @mousedown.prevent="handleFormat('bold')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
        <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
      </svg>
    </button>

    <!-- Itálico -->
    <button
      type="button"
      class="toolbar-btn"
      title="Itálico (*texto*)"
      aria-label="Itálico"
      @mousedown.prevent="handleFormat('italic')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="19" y1="4" x2="10" y2="4" />
        <line x1="14" y1="20" x2="5" y2="20" />
        <line x1="15" y1="4" x2="9" y2="20" />
      </svg>
    </button>

    <div class="toolbar-separator" aria-hidden="true"></div>

    <!-- Título -->
    <button
      type="button"
      class="toolbar-btn"
      title="Título (### Título)"
      aria-label="Título nível 3"
      @mousedown.prevent="handleFormat('heading')"
    >
      <span class="btn-text-badge">H3</span>
    </button>

    <!-- Lista com marcadores -->
    <button
      type="button"
      class="toolbar-btn"
      title="Lista com marcadores (- item)"
      aria-label="Lista com marcadores"
      @mousedown.prevent="handleFormat('bullet_list')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="8" y1="6" x2="21" y2="6" />
        <line x1="8" y1="12" x2="21" y2="12" />
        <line x1="8" y1="18" x2="21" y2="18" />
        <circle cx="4" cy="6" r="1.5" fill="currentColor" />
        <circle cx="4" cy="12" r="1.5" fill="currentColor" />
        <circle cx="4" cy="18" r="1.5" fill="currentColor" />
      </svg>
    </button>

    <!-- Citação -->
    <button
      type="button"
      class="toolbar-btn"
      title="Citação em bloco (> citação)"
      aria-label="Citação em bloco"
      @mousedown.prevent="handleFormat('quote')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
        <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
      </svg>
    </button>

    <div class="toolbar-separator" aria-hidden="true"></div>

    <!-- Código inline -->
    <button
      type="button"
      class="toolbar-btn"
      title="Código inline (`código`)"
      aria-label="Código inline"
      @mousedown.prevent="handleFormat('code')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="16 18 22 12 16 6" />
        <polyline points="8 6 2 12 8 18" />
      </svg>
    </button>

    <!-- Link -->
    <button
      type="button"
      class="toolbar-btn"
      title="Inserir link ([texto](url))"
      aria-label="Inserir link"
      @mousedown.prevent="handleFormat('link')"
    >
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.markdown-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
  padding: 4px 6px;
  background: var(--color-surface-subtle, var(--color-surface, #ffffff));
  border: var(--border-width, 1px) solid var(--color-border-strong, #e4e4e7);
  border-bottom: 1px solid var(--color-border, #e4e4e7);
  border-top-left-radius: var(--radius-control, 6px);
  border-top-right-radius: var(--radius-control, 6px);
  user-select: none;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
  padding: 4px 6px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-control, 4px);
  color: var(--color-text, #18181b);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  font-family: inherit;
  font-size: 0.8125rem;
}

.toolbar-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.06));
  border-color: var(--color-border, #e4e4e7);
}

.toolbar-btn:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 1px;
}

.toolbar-icon {
  width: 15px;
  height: 15px;
  display: block;
}

.btn-text-badge {
  font-weight: 700;
  font-size: 0.75rem;
  letter-spacing: -0.02em;
}

.toolbar-separator {
  width: 1px;
  height: 18px;
  background: var(--color-border, #e4e4e7);
  margin: 0 4px;
}
</style>
