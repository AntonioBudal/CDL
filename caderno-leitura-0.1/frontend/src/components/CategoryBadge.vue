<script setup lang="ts">
import type { Category } from '../types'
import Icon from './ui/Icon.vue'

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
      class="category-remove-btn text-muted hover:text-danger focus:outline-none p-0.5 -mr-0.5 rounded inline-flex items-center justify-center transition-colors"
      :aria-label="`Remover categoria ${category.name}`"
      @click="onRemove"
    >
      <Icon name="x" :size="size === 'sm' ? 12 : 14" />
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
