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

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const profileService = useProfile()
const { openSearch } = useGlobalSearch()
const sync = useSync()
const preferences = usePreferences()

const isAuthPage = computed(() => ['login', 'register', 'setup-owner'].includes(String(route.name)))
const currentUser = computed(() => auth.user.value)
const isAuthenticated = computed(() => auth.isAuthenticated.value)

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
  }
})

watch(
  () => auth.isAuthenticated.value,
  (isAuth) => {
    if (isAuth) {
      void profileService.fetchProfile()
    }
  }
)

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
  window.removeEventListener('caderno_home_view_changed', handleStorageChange)
  sync.detachListeners()
})

interface NavLinkItem {
  to: string
  label: string
  routes: string[]
  icon: IconName
}

const mainLinks: NavLinkItem[] = [
  {
    to: '/',
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

const visibleMainLinks = computed(() => {
  return mainLinks.filter(item => {
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
      <RouterLink class="brand" to="/">Caderno de Leitura</RouterLink>
      <nav v-if="!isAuthPage" class="main-nav" aria-label="Navegação principal">
        <RouterLink
          v-for="item in visibleMainLinks"
          :key="item.to"
          :to="item.to"
          :class="{
            selected: item.routes.includes(String(route.name))
          }"
          :aria-current="
            item.routes.includes(String(route.name))
              ? (route.name === item.routes[0] ? 'page' : 'true')
              : undefined
          "
        >
          <Icon :name="item.icon" :size="18" :stroke-width="1.8" class="nav-icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
      <div class="header-actions">
        <SyncStatusBadge v-if="!isAuthPage" />
        <button
          v-if="!isAuthPage"
          type="button"
          class="search-trigger-btn"
          aria-label="Abrir busca global de estudos (Ctrl+K)"
          @click="openSearch"
        >
          <Icon name="search" :size="15" />
          <span class="search-label">Buscar</span>
          <kbd class="search-kbd">Ctrl K</kbd>
        </button>

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
  <footer class="app-footer">Caderno de Leitura · Versão 0.4</footer>
  <GlobalSearchModal />
</template>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
</style>
