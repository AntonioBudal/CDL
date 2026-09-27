<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useNotifications } from '../../composables/useNotifications.ts'
import NotificationItem from './NotificationItem.vue'
import Icon from '../ui/Icon.vue'

const {
  notifications,
  unread,
  loading,
  open,
  filterUnread,
  closeDropdown,
  markAllAsRead,
  setUnreadFilter,
} = useNotifications()

const dropdownRef = ref<HTMLElement | null>(null)
const isMarkingAll = ref(false)

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && open.value) {
    closeDropdown()
  }
}

function handleClickOutside(event: MouseEvent) {
  if (!open.value) return
  const target = event.target as Node | null
  const triggerEl = document.querySelector('.btn-notifications-trigger')
  if (
    dropdownRef.value &&
    !dropdownRef.value.contains(target) &&
    triggerEl &&
    !triggerEl.contains(target)
  ) {
    closeDropdown()
  }
}

async function handleMarkAll() {
  if (isMarkingAll.value || unread.value === 0) return
  isMarkingAll.value = true
  await markAllAsRead()
  isMarkingAll.value = false
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div
    v-if="open"
    ref="dropdownRef"
    class="notifications-dropdown"
    role="region"
    aria-label="Central de notificações e avisos"
    tabindex="-1"
  >
    <!-- Cabeçalho do Dropdown -->
    <header class="notifications-header">
      <div class="notifications-header-left">
        <h3 class="notifications-title">Notificações</h3>
        <span v-if="unread > 0" class="unread-pill">{{ unread }} pendente(s)</span>
      </div>

      <div class="notifications-header-right">
        <button
          v-if="unread > 0"
          type="button"
          class="btn-mark-all"
          :disabled="isMarkingAll"
          title="Marcar todas como lidas"
          aria-label="Marcar todas as notificações como lidas"
          @click="handleMarkAll"
        >
          <Icon name="check" :size="14" />
          <span>Marcar lidas</span>
        </button>
      </div>
    </header>

    <!-- Filtros Rápidos (Todas / Não lidas) -->
    <div class="notifications-filters" role="tablist" aria-label="Filtros de notificações">
      <button
        type="button"
        class="filter-tab"
        role="tab"
        :aria-selected="!filterUnread"
        :class="{ active: !filterUnread }"
        @click="setUnreadFilter(false)"
      >
        Todas
      </button>
      <button
        type="button"
        class="filter-tab"
        role="tab"
        :aria-selected="filterUnread"
        :class="{ active: filterUnread }"
        @click="setUnreadFilter(true)"
      >
        Não lidas
      </button>
    </div>

    <!-- Lista de Notificações -->
    <div class="notifications-body" role="feed" :aria-busy="loading">
      <div v-if="loading && notifications.length === 0" class="notifications-loading">
        <Icon name="refresh-cw" :size="20" class="spinning" />
        <span>Carregando notificações...</span>
      </div>

      <div v-else-if="notifications.length === 0" class="notifications-empty">
        <Icon name="bell" :size="32" class="empty-icon" />
        <p class="empty-title">Tudo tranquilo por aqui</p>
        <p class="empty-subtitle">
          {{ filterUnread ? 'Nenhuma notificação não lida.' : 'Você não possui notificações no momento.' }}
        </p>
      </div>

      <div v-else class="notifications-list">
        <NotificationItem
          v-for="item in notifications"
          :key="item.id"
          :item="item"
          @close-dropdown="closeDropdown"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-width: 90vw;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: dropdown-fade-in 0.15s ease-out;
}

@keyframes dropdown-fade-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notifications-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #ffffff);
}

.notifications-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.notifications-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text, #111827);
}

.unread-pill {
  font-size: 0.72rem;
  font-weight: 600;
  background-color: var(--color-primary-light, #e0e7ff);
  color: var(--color-primary, #4338ca);
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
}

.btn-mark-all {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  color: var(--color-text-muted, #6b7280);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.btn-mark-all:hover:not(:disabled) {
  color: var(--color-text, #111827);
  background-color: var(--color-surface-hover, #f3f4f6);
}

.btn-mark-all:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notifications-filters {
  display: flex;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface-muted, #f9fafb);
  padding: 0.25rem 0.5rem;
  gap: 0.25rem;
}

.filter-tab {
  flex: 1;
  padding: 0.3rem 0.5rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--color-text-muted, #6b7280);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-tab:hover {
  color: var(--color-text, #111827);
}

.filter-tab.active {
  background-color: var(--color-surface, #ffffff);
  color: var(--color-primary, #2563eb);
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.notifications-body {
  max-height: 400px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.notifications-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2.5rem 1rem;
  color: var(--color-text-muted, #6b7280);
  font-size: 0.85rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.notifications-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  text-align: center;
}

.empty-icon {
  color: var(--color-text-muted, #9ca3af);
  margin-bottom: 0.5rem;
  opacity: 0.6;
}

.empty-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text, #374151);
}

.empty-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.78rem;
  color: var(--color-text-muted, #6b7280);
}

.notifications-list {
  display: flex;
  flex-direction: column;
}
</style>
