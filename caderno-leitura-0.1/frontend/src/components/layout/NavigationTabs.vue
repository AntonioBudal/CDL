<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import type { IconName } from '../../types'
import Icon from '../ui/Icon.vue'
import { useAuthStore } from '../../stores/auth'
import { useFriends } from '../../composables/useFriends'
import { useInboxCount } from '../../composables/useInboxCount'

const props = defineProps<{
  homeViewPreference?: string
}>()

const route = useRoute()
const auth = useAuthStore()
const friendsService = useFriends()
const inboxService = useInboxCount()

const isMoreOpen = ref(false)
const moreContainerRef = ref<HTMLElement | null>(null)

const pendingFriendsCount = computed(() => friendsService.pendingReceivedCount.value)
const inboxCount = computed(() => inboxService.count.value)
const isAdmin = computed(() => auth.isAdmin.value)

interface PrimaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  badgeCount?: () => number
}

interface SecondaryNavItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  requiresAdmin?: boolean
  badgeCount?: () => number
}

const primaryNavItems = computed<PrimaryNavItem[]>(() => {
  return [
    {
      to: '/dashboard',
      label: 'Dashboard',
      routes: ['dashboard'],
      icon: 'layout-dashboard',
    },
    {
      to: '/livros',
      label: 'Livros',
      routes: ['books', 'book', 'study', 'study-edit'],
      icon: 'book-open',
    },
    {
      to: '/highlights',
      label: 'Destaques',
      routes: ['highlights'],
      icon: 'pencil',
    },
    {
      to: '/review',
      label: 'Revisão',
      routes: ['review', 'study-session'],
      icon: 'rotate-ccw',
    },
    {
      to: '/inbox',
      label: 'Inbox',
      routes: ['inbox'],
      icon: 'inbox',
      badgeCount: () => inboxCount.value,
    },
  ]
})

const secondaryNavItems = computed<SecondaryNavItem[]>(() => {
  const items: SecondaryNavItem[] = [
    {
      to: '/importar',
      label: 'Importar',
      routes: ['import'],
      icon: 'plus',
    },
    {
      to: '/amigos',
      label: 'Amigos',
      routes: ['friends'],
      icon: 'users',
      badgeCount: () => pendingFriendsCount.value,
    },
    {
      to: '/ajustes',
      label: 'Ajustes',
      routes: ['settings', 'connection'],
      icon: 'sliders',
    },
    {
      to: '/lixeira',
      label: 'Lixeira',
      routes: ['trash'],
      icon: 'trash',
    },
  ]

  if (isAdmin.value) {
    items.push({
      to: '/admin',
      label: 'Administração',
      routes: ['admin'],
      icon: 'shield',
      requiresAdmin: true,
    })
  }

  return items
})

const isMoreRouteActive = computed(() => {
  const current = String(route.name)
  return secondaryNavItems.value.some((item) => item.routes.includes(current))
})

const hasMoreBadge = computed(() => {
  return pendingFriendsCount.value > 0
})

function toggleMore() {
  isMoreOpen.value = !isMoreOpen.value
}

function closeMore() {
  isMoreOpen.value = false
}

function handleKeydown(e: KeyboardEvent) {
  if (!isMoreOpen.value) return
  if (e.key === 'Escape') {
    e.preventDefault()
    closeMore()
  }
}

function handleClickOutside(e: MouseEvent) {
  if (!isMoreOpen.value) return
  if (moreContainerRef.value && !moreContainerRef.value.contains(e.target as Node)) {
    closeMore()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <nav class="navigation-tabs" aria-label="Navegação principal">
    <!-- 5 Abas Primárias do Ciclo Ativo de Leitura -->
    <RouterLink
      v-for="item in primaryNavItems"
      :key="item.to"
      :to="item.to"
      class="nav-tab-link"
      :class="{
        selected: item.routes.includes(String(route.name)),
      }"
      :aria-current="
        item.routes.includes(String(route.name))
          ? (route.name === item.routes[0] ? 'page' : 'true')
          : undefined
      "
    >
      <Icon :name="item.icon" :size="18" :stroke-width="1.8" class="tab-icon" />
      <span class="tab-label">{{ item.label }}</span>
      <span
        v-if="item.badgeCount && item.badgeCount() > 0"
        class="tab-badge"
        :aria-label="`${item.label}: ${item.badgeCount()} pendentes`"
      >
        {{ item.badgeCount() > 99 ? '99+' : item.badgeCount() }}
      </span>
    </RouterLink>

    <!-- Menu Retrátil "Mais ▾" para Utilitários e Ciclo Estendido -->
    <div ref="moreContainerRef" class="more-menu-container">
      <button
        type="button"
        class="nav-tab-link more-trigger-btn"
        :class="{
          selected: isMoreRouteActive,
          active: isMoreOpen,
        }"
        aria-haspopup="menu"
        :aria-expanded="isMoreOpen"
        aria-label="Mais opções de navegação"
        @click="toggleMore"
      >
        <Icon name="more-horizontal" :size="18" :stroke-width="1.8" class="tab-icon" />
        <span class="tab-label">Mais</span>
        <Icon name="chevron-down" :size="14" :stroke-width="2" class="more-chevron" />
        <span
          v-if="hasMoreBadge && !isMoreOpen"
          class="tab-badge-dot"
          aria-label="Novas notificações nas abas secundárias"
        />
      </button>

      <Transition name="more-fade">
        <div
          v-if="isMoreOpen"
          class="more-dropdown-menu"
          role="menu"
          aria-label="Navegação secundária"
        >
          <RouterLink
            v-for="item in secondaryNavItems"
            :key="item.to"
            :to="item.to"
            class="more-menu-item"
            :class="{ selected: item.routes.includes(String(route.name)) }"
            role="menuitem"
            @click="closeMore"
          >
            <Icon :name="item.icon" :size="16" class="more-item-icon" />
            <span class="more-item-label">{{ item.label }}</span>
            <span
              v-if="item.badgeCount && item.badgeCount() > 0"
              class="more-item-badge"
            >
              {{ item.badgeCount() }}
            </span>
          </RouterLink>
        </div>
      </Transition>
    </div>
  </nav>
</template>

<style scoped>
.navigation-tabs {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit, 1rem) * 0.35);
  flex-wrap: nowrap;
}

.nav-tab-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  text-decoration: none;
  padding: calc(var(--space-unit, 1rem) * 0.5) calc(var(--space-unit, 1rem) * 0.75);
  min-height: 44px;
  border-radius: var(--radius-control, 0.35rem);
  font-size: 0.9375rem;
  color: var(--color-muted);
  font-weight: 600;
  white-space: nowrap;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  font-family: inherit;
  transition: background-color 150ms ease, color 150ms ease;
  position: relative;
}

.nav-tab-link:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.nav-tab-link.selected {
  color: var(--color-selected-text);
  background-color: var(--color-selected-bg);
  border-color: transparent;
}

.nav-tab-link:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.25rem;
  height: 1.25rem;
  padding: 0 0.35rem;
  border-radius: 9999px;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #fff);
  font-size: 0.7rem;
  font-weight: 700;
  line-height: 1;
}

.tab-badge-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent);
}

.more-menu-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.more-trigger-btn {
  gap: 0.35rem;
}

.more-trigger-btn.active {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.more-chevron {
  color: currentColor;
  opacity: 0.85;
  transition: transform 150ms ease;
}

.more-trigger-btn.active .more-chevron {
  transform: rotate(180deg);
}

.more-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 190px;
  background-color: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-panel, 0.5rem);
  box-shadow: 0 10px 25px -5px color-mix(in srgb, var(--color-inverse-bg, #000) 15%, transparent);
  padding: 0.4rem 0;
  z-index: 1050;
  display: flex;
  flex-direction: column;
}

.more-menu-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 1rem;
  min-height: 44px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-decoration: none;
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  transition: background-color 120ms ease, color 120ms ease;
}

.more-menu-item:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-hover-text, var(--color-text));
}

.more-menu-item.selected {
  color: var(--color-selected-text);
  background-color: var(--color-selected-bg);
}

.more-menu-item:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: -2px;
}

.more-item-badge {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.15rem;
  height: 1.15rem;
  padding: 0 0.3rem;
  border-radius: 9999px;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #fff);
  font-size: 0.6875rem;
  font-weight: 700;
}

.more-fade-enter-active,
.more-fade-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}

.more-fade-enter-from,
.more-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 767px) {
  .navigation-tabs {
    display: none !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .more-fade-enter-active,
  .more-fade-leave-active,
  .more-dropdown-menu,
  .more-chevron {
    transition-duration: 0.01ms !important;
  }
}
</style>
