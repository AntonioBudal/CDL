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
  <div class="search-history-list">
    <div class="history-header">
      <span class="history-header-title">
        <Icon name="search" :size="13" class="history-icon" />
        Pesquisas Recentes
      </span>
      <button
        v-if="items.length > 0"
        type="button"
        class="clear-history-btn"
        @click="emit('clear')"
      >
        Limpar histórico
      </button>
    </div>

    <div v-if="isLoading" class="history-loading">
      Carregando histórico...
    </div>

    <div v-else-if="items.length === 0" class="history-empty">
      Nenhuma pesquisa recente registrada.
    </div>

    <div v-else class="history-items-container">
      <div
        v-for="item in items"
        :key="item.id"
        class="history-item"
        @click="emit('select', item.query)"
      >
        <div class="history-item-left">
          <Icon name="search" :size="14" class="history-item-icon" />
          <span class="history-query-text">
            {{ item.query }}
          </span>
        </div>

        <button
          type="button"
          class="remove-history-btn"
          :aria-label="`Remover pesquisa '${item.query}' do histórico`"
          @click.stop="emit('remove', item.id)"
        >
          <Icon name="x" :size="13" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-history-list {
  width: 100%;
  padding: 0.5rem 0;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.25rem;
  margin-bottom: 0.5rem;
}

.history-header-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.history-icon {
  color: var(--color-muted);
}

.clear-history-btn {
  font-size: 0.75rem;
  color: var(--color-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-control, 4px);
  min-height: 36px;
  display: flex;
  align-items: center;
  transition: all 0.15s ease;
}

.clear-history-btn:hover {
  color: var(--color-error-text, #dc2626);
  background: var(--color-error-bg, rgba(220, 38, 38, 0.08));
}

.history-empty,
.history-loading {
  padding: 1.5rem 0;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.history-items-container {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-control, 6px);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border);
}

.history-item-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.history-item-icon {
  color: var(--color-muted);
  flex-shrink: 0;
  transition: color 0.15s ease;
}

.history-query-text {
  font-size: 0.875rem;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.15s ease;
}

.history-item:hover .history-query-text,
.history-item:hover .history-item-icon {
  color: var(--color-accent);
}

.remove-history-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  border-radius: 4px;
  opacity: 0.7;
  transition: all 0.15s ease;
}

.remove-history-btn:hover {
  color: var(--color-error-text, #dc2626);
  background: var(--color-error-bg, rgba(220, 38, 38, 0.08));
  opacity: 1;
}
</style>
