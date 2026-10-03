<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { renderMarkdown } from '../services/markdown'
import { sanitizeHtml } from '../services/sanitizer'
import type { StudyHighlight } from '../types.ts'
import { applyHighlightsToDom, type HighlightClickEvent } from '../utils/highlightRenderer.ts'

const props = withDefaults(
  defineProps<{
    content: string
    highlights?: StudyHighlight[]
  }>(),
  {
    highlights: () => [],
  },
)

const emit = defineEmits<{
  (e: 'highlight-click', payload: HighlightClickEvent): void
}>()

const containerRef = ref<HTMLElement | null>(null)
let cleanupHighlights: (() => void) | null = null

const rendered = computed(() => sanitizeHtml(renderMarkdown(props.content)))

function updateHighlights() {
  if (cleanupHighlights) {
    cleanupHighlights()
    cleanupHighlights = null
  }
  if (!containerRef.value) return

  cleanupHighlights = applyHighlightsToDom(
    containerRef.value,
    props.highlights,
    (event) => {
      emit('highlight-click', event)
    },
  )
}

watch([rendered, () => props.highlights], () => {
  nextTick(updateHighlights)
})

onMounted(() => {
  nextTick(updateHighlights)
})

onBeforeUnmount(() => {
  if (cleanupHighlights) {
    cleanupHighlights()
    cleanupHighlights = null
  }
})
</script>

<template>
  <div
    ref="containerRef"
    class="markdown-content"
    tabindex="-1"
    role="region"
    aria-label="Conteúdo da seção"
    v-html="rendered"
  ></div>
</template>

<style scoped>
.markdown-content:focus {
  outline: none;
}

:deep(.study-highlight) {
  padding: 0.1em 0.25em;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.15s ease, box-shadow 0.15s ease;
  text-decoration: none;
}

:deep(.study-highlight:hover) {
  opacity: 0.88;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.12);
}

:deep(.hl-yellow) { background-color: var(--hl-yellow, #fef08a); color: var(--hl-text, #18181b); }
:deep(.hl-green) { background-color: var(--hl-green, #bbf7d0); color: var(--hl-text, #18181b); }
:deep(.hl-blue) { background-color: var(--hl-blue, #bae6fd); color: var(--hl-text, #18181b); }
:deep(.hl-pink) { background-color: var(--hl-pink, #fbcfe8); color: var(--hl-text, #18181b); }
:deep(.hl-purple) { background-color: var(--hl-purple, #e9d5ff); color: var(--hl-text, #18181b); }

:deep(.study-note) {
  border-bottom: 2px dashed rgba(0, 0, 0, 0.4);
}

:deep(.study-note-badge) {
  margin-left: 4px;
  font-size: 0.85em;
  display: inline-block;
  vertical-align: middle;
}

:deep(.study-occlusion) {
  position: relative;
  display: inline-block;
  background-color: var(--color-surface-hover, #e4e4e7);
  color: transparent !important;
  border-radius: 4px;
  padding: 0.1em 0.35em;
  user-select: none;
  cursor: pointer;
  filter: blur(4px);
  transition: filter 0.2s ease, color 0.2s ease;
}

:deep(.study-occlusion.is-revealed) {
  color: inherit !important;
  filter: none;
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.05));
  user-select: auto;
}

:deep(.study-occlusion-btn) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d4d4d8);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary, #18181b);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  white-space: nowrap;
}

:deep(.study-occlusion.is-revealed .study-occlusion-btn) {
  position: relative;
  top: auto;
  left: auto;
  transform: none;
  margin-left: 6px;
  opacity: 0.6;
}

:deep(.study-question-target) {
  display: inline;
}

:deep(.study-question-badge) {
  display: block;
  margin: 6px 0;
  padding: 6px 10px;
  background: var(--color-surface-subtle, #f4f4f5);
  border-left: 3px solid var(--color-primary, #3b82f6);
  border-radius: 4px;
  font-size: 0.875rem;
}

:deep(.study-question-reveal-btn) {
  margin-left: 10px;
  padding: 2px 8px;
  font-size: 0.75rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d4d4d8);
  border-radius: 4px;
  cursor: pointer;
}
</style>
