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
          <!-- Sincronização -->
          <SyncStatusBadge />

          <!-- Busca Global (Ctrl+K) -->
          <button
            type="button"
            class="header-tool-btn search-trigger-btn"
            aria-label="Abrir busca global de estudos (Ctrl+K)"
            title="Buscar (Ctrl+K)"
            @click="openSearch"
          >
            <Icon name="search" :size="15" />
            <span class="tool-label search-label">Buscar</span>
            <kbd class="tool-kbd search-kbd">Ctrl K</kbd>
          </button>

          <!-- Captura Rápida (Ctrl+Shift+C) -->
          <button
            type="button"
            class="header-tool-btn quick-capture-trigger-btn"
            aria-label="Captura rápida no Inbox (Ctrl+Shift+C)"
            title="Captura rápida (Ctrl+Shift+C)"
            @click="quickCapture.open()"
          >
            <Icon name="pencil" :size="15" />
            <span class="tool-label quick-capture-label">Capturar</span>
            <kbd class="tool-kbd quick-capture-kbd">Ctrl+Shift+C</kbd>
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

          <!-- Botão Mais para Telas Móveis (< 768px) -->
          <button
            type="button"
            class="mobile-more-trigger mobile-only"
            aria-label="Mais opções de navegação móvel"
            aria-haspopup="dialog"
            @click="emit('open-mobile-more')"
          >
            <Icon name="more-horizontal" :size="20" :stroke-width="1.8" />
          </button>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: calc(var(--space-unit, 1rem) * 1);
  min-height: 3.75rem;
  flex-wrap: nowrap;
}

/* 3 Zonas Operacionais */
.header-block {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.header-left {
  justify-content: flex-start;
}

.header-center {
  justify-content: center;
  flex: 1 1 auto;
}

.header-right {
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
  gap: 0.4rem;
  padding: 0.35rem 0.6rem;
  min-height: 44px;
  background-color: var(--color-surface-soft, var(--color-surface));
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-button, 0.4rem);
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

.tool-kbd {
  font-size: 0.6875rem;
  font-family: var(--font-mono, monospace);
  padding: 0.15rem 0.3rem;
  border-radius: var(--radius-small, 0.25rem);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-subtle);
  line-height: 1;
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
  width: 44px;
  height: 44px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-button, 0.4rem);
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
  top: 6px;
  right: 6px;
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

@media (max-width: 1024px) {
  .tool-kbd {
    display: none;
  }
}

@media (max-width: 768px) {
  .tool-label {
    display: none;
  }

  .header-tool-btn {
    width: 44px;
    height: 44px;
    padding: 0;
    justify-content: center;
  }

  .mobile-more-trigger {
    display: inline-flex;
  }
}
</style>
