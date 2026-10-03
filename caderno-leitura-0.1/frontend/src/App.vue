<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import type { IconName } from './types'
import Icon from './components/ui/Icon.vue'
import GlobalSearchModal from './components/search/GlobalSearchModal.vue'
import SyncStatusBadge from './components/sync/SyncStatusBadge.vue'
import { useGlobalSearch } from './composables/useGlobalSearch.ts'
import { usePreferences } from './composables/usePreferences.ts'
import { useSync } from './composables/useSync.ts'
import { useAuthStore } from './stores/auth.ts'
import { useProfile } from './composables/useProfile.ts'
import { useFriends } from './composables/useFriends.ts'
import { useNotifications } from './composables/useNotifications.ts'
import NotificationsDropdown from './components/notifications/NotificationsDropdown.vue'
import MobileMoreMenu from './components/navigation/MobileMoreMenu.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const profileService = useProfile()
const friendsService = useFriends()
const notificationsService = useNotifications()
const { openSearch } = useGlobalSearch()
const sync = useSync()
const preferences = usePreferences()

const isAuthPage = computed(() => ['login', 'register', 'setup-owner'].includes(String(route.name)))
const currentUser = computed(() => auth.user.value)
const isAuthenticated = computed(() => auth.isAuthenticated.value)
const pendingReceivedCount = computed(() => friendsService.pendingReceivedCount.value)

async function handleLogout() {
  if (confirm('Deseja realmente sair da aplicação?')) {
    await auth.logout()
    router.replace('/login')
  }
}

const homeViewPreference = ref<string>('dashboard')

function readHomeViewPreference() {
  try {
    const val = window.localStorage?.getItem('caderno_home_view')
    if (val === 'books' || val === 'dashboard') {
      homeViewPreference.value = val
    } else {
      homeViewPreference.value = 'dashboard'
    }
  } catch {
    homeViewPreference.value = 'dashboard'
  }
}

function handleStorageChange() {
  readHomeViewPreference()
}

onMounted(() => {
  readHomeViewPreference()
  window.addEventListener('storage', handleStorageChange)
  window.addEventListener('caderno_home_view_changed', handleStorageChange)
  sync.attachListeners()
  sync.syncNow(false, 1000)
  preferences.loadPreferences()
  if (auth.isAuthenticated.value) {
    void profileService.fetchProfile()
    void friendsService.fetchSummary()
    notificationsService.startPolling(45000)
  }
})

watch(
  () => auth.isAuthenticated.value,
  (isAuth) => {
    if (isAuth) {
      void profileService.fetchProfile()
      void friendsService.fetchSummary()
      notificationsService.startPolling(45000)
    } else {
      notificationsService.stopPolling()
    }
  }
)

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
  window.removeEventListener('caderno_home_view_changed', handleStorageChange)
  sync.detachListeners()
  notificationsService.stopPolling()
})

const isMoreMenuOpen = ref(false)
const isMoreMenuActive = computed(() => {
  const current = String(route.name)
  return ['trash', 'admin', 'profile'].includes(current)
})

interface NavLinkItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
  requiresAdmin?: boolean
  desktopOnly?: boolean
}

const mainLinks: NavLinkItem[] = [
  {
    to: '/livros',
    label: 'Livros',
    routes: ['books', 'book', 'study', 'study-edit'],
    icon: 'book-open',
  },
  {
    to: '/dashboard',
    label: 'Dashboard',
    routes: ['dashboard'],
    icon: 'layout-dashboard',
  },
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
  },
  {
    to: '/ajustes',
    label: 'Ajustes',
    routes: ['settings', 'connection'],
    icon: 'sliders',
  },
  {
    to: '/admin',
    label: 'Administração',
    routes: ['admin'],
    icon: 'shield',
    requiresAdmin: true,
    desktopOnly: true,
  },
  {
    to: '/lixeira',
    label: 'Lixeira',
    routes: ['trash'],
    icon: 'trash',
    desktopOnly: true,
  },
]

const visibleMainLinks = computed(() => {
  return mainLinks.filter(item => {
    // Se a rota requer papel de administrador, oculta para usuários comuns
    if (item.requiresAdmin && !auth.isAdmin.value) {
      return false
    }
    // Se a preferência for 'books', oculta a aba 'Dashboard'
    if (homeViewPreference.value === 'books' && item.label === 'Dashboard') {
      return false
    }
    // Se a preferência for 'dashboard' (padrão), oculta a aba 'Livros'
    if (homeViewPreference.value === 'dashboard' && item.label === 'Livros') {
      return false
    }
    return true
  })
})
</script>

<template>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink class="brand" :to="isAuthenticated ? (homeViewPreference === 'dashboard' ? '/dashboard' : '/livros') : '/'">Leitorum</RouterLink>
      <nav v-if="!isAuthPage && isAuthenticated" class="main-nav" aria-label="Navegação principal">
        <RouterLink
          v-for="item in visibleMainLinks"
          :key="item.to"
          :to="item.to"
          :class="{
            selected: item.routes.includes(String(route.name)),
            'desktop-only': item.desktopOnly,
          }"
          :aria-current="
            item.routes.includes(String(route.name))
              ? (route.name === item.routes[0] ? 'page' : 'true')
              : undefined
          "
        >
          <Icon :name="item.icon" :size="18" :stroke-width="1.8" class="nav-icon" />
          <span>{{ item.label }}</span>
          <span
            v-if="item.routes.includes('friends') && pendingReceivedCount > 0"
            class="nav-badge"
            aria-label="Novas solicitações pendentes"
          >
            {{ pendingReceivedCount }}
          </span>
        </RouterLink>

        <!-- Botão 'Mais' para Mobile (5º destino móvel) -->
        <button
          type="button"
          class="mobile-more-trigger mobile-only"
          :class="{ active: isMoreMenuActive, selected: isMoreMenuActive }"
          aria-label="Mais opções de navegação"
          aria-haspopup="dialog"
          :aria-expanded="isMoreMenuOpen"
          @click="isMoreMenuOpen = true"
        >
          <Icon name="more-horizontal" :size="18" :stroke-width="1.8" class="nav-icon" />
          <span>Mais</span>
        </button>
      </nav>
      <nav v-else-if="!isAuthPage && !isAuthenticated" class="main-nav public-nav" aria-label="Navegação institucional">
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
      <div class="header-actions">
        <SyncStatusBadge v-if="!isAuthPage && isAuthenticated" />
        <button
          v-if="!isAuthPage && isAuthenticated"
          type="button"
          class="search-trigger-btn"
          aria-label="Abrir busca global de estudos (Ctrl+K)"
          @click="openSearch"
        >
          <Icon name="search" :size="15" />
          <span class="search-label">Buscar</span>
          <kbd class="search-kbd">Ctrl K</kbd>
        </button>

        <!-- Ações para Visitantes (Público) -->
        <div v-if="!isAuthenticated && !isAuthPage" class="public-auth-actions">
          <RouterLink to="/login" class="public-login-link">Entrar</RouterLink>
          <RouterLink to="/registro" class="public-register-btn">Criar Conta</RouterLink>
        </div>

        <!-- Centro de Notificações (F09) -->
        <div v-if="isAuthenticated && !isAuthPage" class="notifications-nav-container">
          <button
            type="button"
            class="btn-notifications-trigger"
            :class="{ 'has-unread': notificationsService.unread.value > 0, active: notificationsService.open.value }"
            :title="notificationsService.unread.value > 0 ? `${notificationsService.unread.value} notificação(ões) pendente(s)` : 'Notificações'"
            :aria-label="notificationsService.unread.value > 0 ? `Notificações: ${notificationsService.unread.value} pendentes` : 'Notificações'"
            :aria-expanded="notificationsService.open.value"
            aria-haspopup="dialog"
            @click="notificationsService.toggleDropdown"
          >
            <Icon :name="notificationsService.unread.value > 0 ? 'bell-ring' : 'bell'" :size="18" />
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

        <!-- Informações do Usuário e Botão de Logout (F02/F05) -->
        <div v-if="isAuthenticated && !isAuthPage" class="user-nav-actions">
          <RouterLink
            :to="profileService.profile.value?.username ? `/@${profileService.profile.value.username}` : '/ajustes'"
            class="user-chip"
            :title="`Perfil de ${profileService.profile.value?.display_name || currentUser?.display_name || currentUser?.username}`"
          >
            <img
              v-if="profileService.profile.value?.avatar_url"
              :src="profileService.profile.value.avatar_url"
              alt=""
              class="header-avatar-img"
              aria-hidden="true"
            />
            <span
              v-else
              class="header-avatar-initials"
              aria-hidden="true"
            >
              {{ profileService.initials.value }}
            </span>
            <span class="user-display-name">{{ profileService.profile.value?.display_name || currentUser?.display_name || currentUser?.username }}</span>
          </RouterLink>
          <button
            type="button"
            class="logout-btn"
            title="Encerrar sessão"
            aria-label="Encerrar sessão"
            @click="handleLogout"
          >
            Sair
          </button>
        </div>
      </div>
    </div>
  </header>
  <main id="conteudo" class="workspace" tabindex="-1">
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="$route.fullPath" />
      </Transition>
    </RouterView>
  </main>
  <footer class="app-footer" role="contentinfo">
    <div class="footer-inner">
      <span class="footer-brand">Leitorum</span>
      <span class="footer-sep" aria-hidden="true">·</span>
      <RouterLink to="/sobre" class="footer-link">Sobre o Leitorum</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <RouterLink to="/apoie" class="footer-support-link">Apoie o Leitorum</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <span class="footer-license">Software Livre</span>
    </div>
  </footer>
  <GlobalSearchModal />
  <MobileMoreMenu
    :open="isMoreMenuOpen"
    :is-admin="auth.isAdmin.value"
    :username="profileService.profile.value?.username || currentUser?.username"
    :display-name="profileService.profile.value?.display_name || currentUser?.display_name"
    :avatar-url="profileService.profile.value?.avatar_url"
    :initials="profileService.initials.value"
    @close="isMoreMenuOpen = false"
    @logout="handleLogout"
  />
</template>

<style scoped>
.public-auth-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.public-login-link {
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-control, 6px);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.15s ease;
}

.public-login-link:hover {
  background: var(--color-surface-hover);
}

.public-register-btn {
  padding: 0.4rem 0.9rem;
  background: var(--color-accent);
  color: var(--color-on-accent, #fff);
  border-radius: var(--radius-button, 8px);
  font-size: 0.875rem;
  font-weight: 650;
  text-decoration: none;
  transition: background-color 0.15s ease;
}

.public-register-btn:hover {
  background: var(--color-accent-hover);
}

.mobile-more-trigger {
  display: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  border-radius: 9999px;
  background-color: #dc2626;
  color: #fff;
  line-height: 1;
  margin-left: 0.35rem;
}

.user-nav-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.6rem;
  min-height: 38px;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text);
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.15s ease;
  max-width: 140px;
}

.user-chip:hover {
  border-color: var(--color-accent);
  background: var(--color-surface-hover);
}

.user-avatar-icon {
  font-size: 0.875rem;
}

.header-avatar-img {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.header-avatar-initials {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-accent);
  color: var(--color-surface, #fff);
  font-size: 0.6875rem;
  font-weight: 700;
  flex-shrink: 0;
  line-height: 1;
  user-select: none;
}

.user-display-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  padding: 0.35rem 0.65rem;
  min-height: 38px;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.logout-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

@media (max-width: 640px) {
  .user-display-name {
    display: none;
  }
}

.search-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.75rem;
  min-height: 38px;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.search-trigger-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.08));
  border-color: var(--color-border-hover, var(--color-accent));
  color: var(--color-text);
}

.search-label {
  display: inline;
}

.search-kbd {
  display: inline-block;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 0.6875rem;
  font-family: monospace;
  color: var(--color-muted);
}

@media (max-width: 640px) {
  .search-label {
    display: none;
  }
  .search-kbd {
    display: none;
  }
}

.notifications-nav-container {
  position: relative;
  display: flex;
  align-items: center;
}

.btn-notifications-trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  padding: 0;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.btn-notifications-trigger:hover,
.btn-notifications-trigger.active {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.08));
  border-color: var(--color-border-hover, var(--color-accent));
  color: var(--color-text);
}

.btn-notifications-trigger.has-unread {
  color: var(--color-accent, #2563eb);
}

.notifications-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: var(--color-danger, #ef4444);
  color: #ffffff;
  font-size: 0.65rem;
  font-weight: 700;
  line-height: 1;
  padding: 0.18rem 0.35rem;
  border-radius: 9999px;
  border: 2px solid var(--color-surface, #ffffff);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
</style>
