<script setup lang="ts">
import type { Category } from '../types'

const props = withDefaults(
  defineProps<{
    category: Category
    removable?: boolean
    clickable?: boolean
    size?: 'sm' | 'md'
  }>(),
  {
    removable: false,
    clickable: false,
    size: 'md',
  }
)

const emit = defineEmits<{
  (e: 'remove', category: Category): void
  (e: 'click', category: Category): void
}>()

function onClick(event: MouseEvent) {
  if (props.clickable) {
    event.stopPropagation()
    emit('click', props.category)
  }
}

function onRemove(event: MouseEvent) {
  event.stopPropagation()
  emit('remove', props.category)
}
</script>

<template>
  <span
    class="category-badge inline-flex items-center gap-1.5 rounded-md font-sans border transition-colors select-none"
    :class="[
      size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs sm:text-sm',
      clickable ? 'cursor-pointer hover:border-accent hover:text-accent' : '',
    ]"
    :title="category.path || category.name"
    @click="onClick"
  >
    <span class="category-name truncate max-w-[180px] sm:max-w-[240px]">{{ category.name }}</span>
    <button
      v-if="removable"
      type="button"
      class="category-remove-btn text-muted hover:text-danger focus:outline-none p-0.5 -mr-1 rounded inline-flex items-center justify-center transition-colors"
      :aria-label="`Remover categoria ${category.name}`"
      @click="onRemove"
    >
      <svg class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
        <path
          fill-rule="evenodd"
          d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
          clip-rule="evenodd"
        />
      </svg>
    </button>
  </span>
</template>

<style scoped>
.category-badge {
  background-color: var(--color-surface-muted, #f1f5f9);
  color: var(--color-text, #1e293b);
  border-color: var(--color-border, #cbd5e1);
}

.category-remove-btn:hover {
  color: var(--color-danger, #ef4444);
}
</style>
