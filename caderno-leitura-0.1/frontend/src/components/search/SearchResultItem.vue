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
      return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
    case 'revisado':
      return 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20'
    case 'em_estudo':
      return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
    case 'rascunho':
    default:
      return 'bg-muted text-muted-foreground border-border/40'
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
    class="search-result-item group w-full text-left p-3.5 rounded-lg border transition-all cursor-pointer select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-accent"
    :class="[
      isSelected
        ? 'bg-accent/15 border-accent/40 shadow-sm'
        : 'bg-card hover:bg-accent/10 border-border/40 hover:border-border'
    ]"
    @click="handleClick"
    @keydown="handleKeyDown"
  >
    <!-- Trilha Contextual -->
    <div class="flex items-center justify-between gap-2 text-xs text-muted-foreground mb-1.5 flex-wrap">
      <div class="flex items-center gap-1.5 min-w-0 truncate">
        <Icon name="book" :size="13" class="shrink-0 text-muted-foreground/80" />
        <span class="font-medium truncate max-w-[180px] sm:max-w-[260px]">{{ item.book_title }}</span>
        <Icon name="chevron-right" :size="11" class="shrink-0 text-muted-foreground/50" />
        <span class="truncate max-w-[140px] sm:max-w-[200px]">{{ item.chapter_name || 'Sem capítulo' }}</span>
      </div>

      <div class="flex items-center gap-1.5 shrink-0">
        <span class="text-[10px] px-1.5 py-0.5 rounded font-mono border bg-muted/60 text-muted-foreground">
          {{ item.matched_field }}
        </span>
        <span
          class="text-[10px] px-1.5 py-0.5 rounded font-medium border"
          :class="statusBadgeClass"
        >
          {{ statusLabel }}
        </span>
      </div>
    </div>

    <!-- Título do Estudo -->
    <h4 class="text-sm font-semibold text-foreground group-hover:text-accent transition-colors flex items-center justify-between gap-2">
      <span class="line-clamp-1">{{ item.study_title }}</span>
      <Icon
        name="arrow-right"
        :size="14"
        class="shrink-0 text-muted-foreground/40 group-hover:text-accent group-hover:translate-x-0.5 transition-all"
      />
    </h4>

    <!-- Snippet com Realce Sanitizado -->
    <div
      v-if="item.snippet"
      class="search-snippet text-xs text-muted-foreground/90 mt-1.5 leading-relaxed line-clamp-2"
      v-html="item.snippet"
    />
  </div>
</template>

<style scoped>
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
