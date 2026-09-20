<script setup lang="ts">
import Icon from '../ui/Icon.vue'
import type { SearchHistoryItem } from '../../types.ts'

defineProps<{
  items: SearchHistoryItem[]
  isLoading?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', query: string): void
  (e: 'remove', id: number): void
  (e: 'clear'): void
}>()
</script>

<template>
  <div class="search-history-list w-full py-2">
    <div class="flex items-center justify-between px-1 mb-2">
      <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
        <Icon name="search" :size="13" class="text-muted-foreground/70" />
        Pesquisas Recentes
      </span>
      <button
        v-if="items.length > 0"
        type="button"
        class="text-xs text-muted-foreground hover:text-destructive transition-colors px-2 py-1 rounded hover:bg-destructive/10 cursor-pointer min-h-[36px] flex items-center"
        @click="emit('clear')"
      >
        Limpar histórico
      </button>
    </div>

    <div v-if="isLoading" class="py-4 text-center text-xs text-muted-foreground">
      Carregando histórico...
    </div>

    <div v-else-if="items.length === 0" class="py-6 text-center text-xs text-muted-foreground">
      Nenhuma pesquisa recente registrada.
    </div>

    <div v-else class="space-y-1">
      <div
        v-for="item in items"
        :key="item.id"
        class="group flex items-center justify-between gap-2 px-3 py-2 rounded-md hover:bg-accent/10 border border-transparent hover:border-border/40 transition-all cursor-pointer"
        @click="emit('select', item.query)"
      >
        <div class="flex items-center gap-2.5 min-w-0">
          <Icon name="search" :size="14" class="text-muted-foreground/60 shrink-0 group-hover:text-accent transition-colors" />
          <span class="text-sm text-foreground truncate font-medium group-hover:text-accent transition-colors">
            {{ item.query }}
          </span>
        </div>

        <button
          type="button"
          class="shrink-0 p-1.5 rounded text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 opacity-70 group-hover:opacity-100 transition-all min-w-[32px] min-h-[32px] flex items-center justify-center cursor-pointer"
          :aria-label="`Remover pesquisa '${item.query}' do histórico`"
          @click.stop="emit('remove', item.id)"
        >
          <Icon name="x" :size="13" />
        </button>
      </div>
    </div>
  </div>
</template>
