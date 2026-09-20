<script setup lang="ts">
import { computed } from 'vue'
import Icon from '../ui/Icon.vue'
import type { SearchMatchItem } from '../../types.ts'

const props = defineProps<{
  item: SearchMatchItem
  isSelected?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', item: SearchMatchItem): void
}>()

const statusLabel = computed(() => {
  switch (props.item.reading_status) {
    case 'concluido':
      return 'Concluído'
    case 'revisado':
      return 'Revisado'
    case 'em_estudo':
      return 'Em Estudo'
    case 'rascunho':
    default:
      return 'Rascunho'
  }
})

const statusBadgeClass = computed(() => {
  switch (props.item.reading_status) {
    case 'concluido':
      return 'status-concluido'
    case 'revisado':
      return 'status-revisado'
    case 'em_estudo':
      return 'status-em_estudo'
    case 'rascunho':
    default:
      return 'status-rascunho'
  }
})

function handleClick() {
  emit('select', props.item)
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    handleClick()
  }
}
</script>

<template>
  <div
    role="button"
    tabindex="0"
    :aria-label="`Abrir estudo ${item.study_title} do livro ${item.book_title}`"
    class="search-result-item"
    :class="{ 'is-selected': isSelected }"
    @click="handleClick"
    @keydown="handleKeyDown"
  >
    <!-- Trilha Contextual -->
    <div class="result-context-row">
      <div class="result-trail">
        <Icon name="book" :size="13" class="trail-icon" />
        <span class="result-book-title">{{ item.book_title }}</span>
        <Icon name="chevron-right" :size="11" class="trail-chevron" />
        <span class="result-chapter-name">{{ item.chapter_name || 'Sem capítulo' }}</span>
      </div>

      <div class="result-meta-badges">
        <span class="matched-field-badge">
          {{ item.matched_field }}
        </span>
        <span
          class="status-badge"
          :class="statusBadgeClass"
        >
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- Título do Estudo -->
    <h4 class="result-title">
      <span class="title-text">{{ item.study_title }}</span>
      <Icon
        name="arrow-right"
        :size="14"
        class="result-arrow-icon"
      />
    </h4>

    <!-- Snippet com Realce Sanitizado -->
    <div
      v-if="item.snippet"
      class="search-snippet"
      v-html="item.snippet"
    />
  </div>
</template>

<style scoped>
.search-result-item {
  display: block;
  width: 100%;
  box-sizing: border-box;
  text-align: left;
  padding: 0.75rem 0.85rem;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  user-select: none;
  margin-bottom: 0.5rem;
}

.search-result-item:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-hover, var(--color-accent));
}

.search-result-item.is-selected {
  background: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.result-context-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-muted);
  margin-bottom: 0.35rem;
  flex-wrap: wrap;
}

.result-trail {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
  overflow: hidden;
}

.trail-icon {
  color: var(--color-muted);
  flex-shrink: 0;
}

.trail-chevron {
  color: var(--color-muted);
  opacity: 0.6;
  flex-shrink: 0;
}

.result-book-title {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.result-chapter-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.result-meta-badges {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.matched-field-badge {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
}

.status-badge {
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
  border: 1px solid currentColor;
}

.status-concluido {
  background: color-mix(in srgb, #10b981 12%, var(--color-surface));
  color: #059669;
  border-color: color-mix(in srgb, #10b981 30%, transparent);
}

.status-revisado {
  background: color-mix(in srgb, #0ea5e9 12%, var(--color-surface));
  color: #0284c7;
  border-color: color-mix(in srgb, #0ea5e9 30%, transparent);
}

.status-em_estudo {
  background: color-mix(in srgb, #f59e0b 12%, var(--color-surface));
  color: #d97706;
  border-color: color-mix(in srgb, #f59e0b 30%, transparent);
}

.status-rascunho {
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  border-color: var(--color-border);
}

.result-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.title-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-result-item:hover .result-title,
.search-result-item.is-selected .result-title {
  color: var(--color-accent);
}

.result-arrow-icon {
  color: var(--color-muted);
  flex-shrink: 0;
  transition: transform 0.15s ease, color 0.15s ease;
}

.search-result-item:hover .result-arrow-icon,
.search-result-item.is-selected .result-arrow-icon {
  color: var(--color-accent);
  transform: translateX(2px);
}

.search-snippet {
  font-size: 0.8125rem;
  color: var(--color-muted);
  margin-top: 0.35rem;
  line-height: 1.45;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

:deep(mark.search-highlight) {
  background-color: rgba(234, 179, 8, 0.25);
  color: inherit;
  font-weight: 600;
  border-radius: 2px;
  padding: 0 2px;
}

:deep(.dark mark.search-highlight) {
  background-color: rgba(234, 179, 8, 0.35);
  color: #fef08a;
}
</style>
