<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import Icon from '../ui/Icon.vue'
import NavigationTabs from './NavigationTabs.vue'
import UserDropdown from './UserDropdown.vue'
import SyncStatusBadge from '../sync/SyncStatusBadge.vue'
import NotificationsDropdown from '../notifications/NotificationsDropdown.vue'
import { useAuthStore } from '../../stores/auth'
import { useGlobalSearch } from '../../composables/useGlobalSearch'
import { useQuickCapture } from '../../composables/useQuickCapture'
import { useNotifications } from '../../composables/useNotifications'

const props = defineProps<{
  homeViewPreference?: string
}>()

const emit = defineEmits<{
  (e: 'open-mobile-more'): void
}>()

const route = useRoute()
const auth = useAuthStore()
const { openSearch } = useGlobalSearch()
const quickCapture = useQuickCapture()
const notificationsService = useNotifications()

const isAuthenticated = computed(() => auth.isAuthenticated.value)
const isAuthPage = computed(() => ['login', 'register', 'setup-owner'].includes(String(route.name)))
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Bloco 1: Esquerdo (Marca) -->
      <div class="header-block header-left">
        <RouterLink
          class="brand"
          :to="isAuthenticated ? (props.homeViewPreference === 'dashboard' ? '/dashboard' : '/livros') : '/'"
        >
          Leitorum
        </RouterLink>
      </div>

      <!-- Bloco 2: Central (Navegação Primária + Menu Mais) -->
      <div class="header-block header-center">
        <NavigationTabs
          v-if="!isAuthPage && isAuthenticated"
          :home-view-preference="props.homeViewPreference"
        />

        <nav
          v-else-if="!isAuthPage && !isAuthenticated"
          class="public-nav"
          aria-label="Navegação institucional"
        >
          <RouterLink
            to="/sobre"
            :class="{ selected: route.name === 'about' }"
            :aria-current="route.name === 'about' ? 'page' : undefined"
          >
            <Icon name="book-open" :size="18" :stroke-width="1.8" class="nav-icon" />
            <span>Sobre</span>
          </RouterLink>
          <RouterLink
            to="/apoie"
            :class="{ selected: route.name === 'support' }"
            :aria-current="route.name === 'support' ? 'page' : undefined"
          >
            <Icon name="sliders" :size="18" :stroke-width="1.8" class="nav-icon" />
            <span>Apoie</span>
          </RouterLink>
        </nav>
      </div>

      <!-- Bloco 3: Direito (Centro de Ferramentas e Identidade) -->
      <div class="header-block header-right">
        <template v-if="!isAuthPage && isAuthenticated">
          <!-- Sincronização (Apenas Ícone Discreto com Tooltip) -->
          <SyncStatusBadge />

          <!-- Busca Global (Apenas Ícone de Busca) -->
          <button
            type="button"
            class="header-tool-btn search-trigger-btn"
            aria-label="Abrir busca global de estudos (Ctrl+K)"
            title="Buscar (Ctrl+K)"
            @click="openSearch"
          >
            <Icon name="search" :size="16" />
          </button>

          <!-- Captura Rápida (Apenas o + com destaque primário) -->
          <button
            type="button"
            class="header-tool-btn quick-capture-trigger-btn"
            aria-label="Captura rápida no Inbox (Ctrl+Shift+C)"
            title="Captura rápida (Ctrl+Shift+C)"
            @click="quickCapture.open()"
          >
            <Icon name="plus" :size="18" :stroke-width="2.5" />
          </button>

          <!-- Notificações -->
          <div class="notifications-nav-container">
            <button
              type="button"
              class="btn-notifications-trigger"
              :class="{
                'has-unread': notificationsService.unread.value > 0,
                active: notificationsService.open.value,
              }"
              :title="
                notificationsService.unread.value > 0
                  ? `${notificationsService.unread.value} notificação(ões) pendente(s)`
                  : 'Notificações'
              "
              :aria-label="
                notificationsService.unread.value > 0
                  ? `Notificações: ${notificationsService.unread.value} pendentes`
                  : 'Notificações'
              "
              :aria-expanded="notificationsService.open.value"
              aria-haspopup="dialog"
              @click="notificationsService.toggleDropdown"
            >
              <Icon
                :name="notificationsService.unread.value > 0 ? 'bell-ring' : 'bell'"
                :size="18"
              />
              <span
                v-if="notificationsService.unread.value > 0"
                class="notifications-badge"
                aria-hidden="true"
              >
                {{ notificationsService.unread.value > 99 ? '99+' : notificationsService.unread.value }}
              </span>
            </button>
            <NotificationsDropdown />
          </div>

          <!-- Menu do Usuário com Logout Encapsulado -->
          <UserDropdown />
        </template>

        <!-- Ações para Visitantes (Público) -->
        <div v-else-if="!isAuthenticated && !isAuthPage" class="public-auth-actions">
          <RouterLink to="/login" class="public-login-link">Entrar</RouterLink>
          <RouterLink to="/registro" class="public-register-btn">Criar Conta</RouterLink>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: var(--color-surface);
  border-top: var(--edge-strong, 0.3rem) solid var(--color-text);
  border-bottom: var(--border-width, 1px) solid var(--color-border);
  position: relative;
  z-index: 990;
}

.header-inner {
  width: min(100% - var(--page-gutter, 2rem), var(--workspace-max-width, 74rem));
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: calc(var(--space-unit, 1rem) * 0.75);
  min-height: 3.75rem;
}

/* 3 Zonas Operacionais */
.header-block {
  display: flex;
  align-items: center;
  min-width: 0;
}

.header-left {
  justify-self: start;
  justify-content: flex-start;
}

.header-center {
  justify-self: center;
  justify-content: center;
}

.header-right {
  justify-self: end;
  justify-content: flex-end;
  gap: calc(var(--space-unit, 1rem) * 0.45);
}

.brand {
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 750;
  letter-spacing: -0.025em;
  color: var(--color-text);
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}

.brand:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.public-nav {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit, 1rem) * 0.35);
}

.public-nav a {
  text-decoration: none;
  padding: calc(var(--space-unit, 1rem) * 0.5) calc(var(--space-unit, 1rem) * 0.75);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: var(--radius-control, 0.35rem);
  font-size: 0.9375rem;
  color: var(--color-muted);
  font-weight: 600;
  transition: background-color 150ms ease, color 150ms ease;
}

.public-nav a.selected {
  color: var(--color-selected-text);
  background-color: var(--color-selected-bg);
}

.public-nav a:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.header-tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  min-height: 36px;
  height: 36px;
  background-color: var(--color-surface-soft, var(--color-surface));
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: 9999px;
  color: var(--color-muted);
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
}

.header-tool-btn:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
  border-color: var(--color-border-hover, var(--color-border));
}

.header-tool-btn:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.search-trigger-btn {
  width: 36px;
  height: 36px;
  min-width: 36px;
  padding: 0;
  justify-content: center;
  border-radius: 9999px;
}

.quick-capture-trigger-btn {
  width: 36px;
  height: 36px;
  min-width: 36px;
  padding: 0;
  justify-content: center;
  border-radius: 9999px;
  background-color: var(--color-accent);
  border: 1px solid var(--color-accent);
  color: var(--color-on-accent, #ffffff);
  box-shadow: 0 1px 3px color-mix(in srgb, var(--color-accent) 25%, transparent);
}

.quick-capture-trigger-btn:hover {
  background-color: var(--color-accent-hover, var(--color-accent));
  border-color: var(--color-accent-hover, var(--color-accent));
  color: var(--color-on-accent, #ffffff);
  transform: translateY(-1px);
}

.quick-capture-trigger-btn:active {
  transform: translateY(0);
}

.quick-capture-trigger-btn:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.notifications-nav-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.btn-notifications-trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  min-width: 36px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 9999px;
  color: var(--color-muted);
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
}

.btn-notifications-trigger:hover,
.btn-notifications-trigger.active {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
  border-color: var(--color-border);
}

.btn-notifications-trigger:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.notifications-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.15rem;
  height: 1.15rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background-color: var(--color-error-marker, #b42318);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  line-height: 1;
}

.mobile-more-trigger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-button, 0.4rem);
  color: var(--color-muted);
  cursor: pointer;
}

.mobile-more-trigger:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.public-auth-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.public-login-link {
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-muted);
  padding: 0.5rem 0.75rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.public-login-link:hover {
  color: var(--color-text);
}

.public-register-btn {
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-on-accent, #fff);
  background-color: var(--color-accent);
  padding: 0.5rem 1rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-button, 0.4rem);
  transition: background-color 150ms ease;
}

.public-register-btn:hover {
  background-color: var(--color-accent-hover);
}

@media (max-width: 900px) {
  .header-inner {
    display: flex;
    justify-content: space-between;
  }
}

@media (max-width: 767px) {
  .header-center {
    display: none !important;
  }

  .tool-label {
    display: none;
  }

  .search-trigger-btn {
    width: 36px;
    height: 36px;
    min-width: 36px;
    padding: 0;
    justify-content: center;
  }
}

@media (pointer: coarse) {
  .quick-capture-trigger-btn,
  .search-trigger-btn,
  .btn-notifications-trigger {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
