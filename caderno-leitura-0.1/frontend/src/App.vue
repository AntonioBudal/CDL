<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import GlobalSearchModal from './components/search/GlobalSearchModal.vue'
import { usePreferences } from './composables/usePreferences.ts'
import { useSync } from './composables/useSync.ts'
import { useAuthStore } from './stores/auth.ts'
import { useProfile } from './composables/useProfile.ts'
import { useFriends } from './composables/useFriends.ts'
import { useNotifications } from './composables/useNotifications.ts'
import { useQuickCapture } from './composables/useQuickCapture.ts'
import { useInboxCount } from './composables/useInboxCount.ts'
import QuickCaptureModal from './components/inbox/QuickCaptureModal.vue'
import MobileMoreMenu from './components/navigation/MobileMoreMenu.vue'
import GlobalHeader from './components/layout/GlobalHeader.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const profileService = useProfile()
const friendsService = useFriends()
const notificationsService = useNotifications()
const sync = useSync()
const preferences = usePreferences()
const quickCapture = useQuickCapture()
const inboxService = useInboxCount()

function handleGlobalShortcut(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'C' || e.key === 'c')) {
    e.preventDefault()
    quickCapture.open()
  }
}

const currentUser = computed(() => auth.user.value)

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
  window.addEventListener('keydown', handleGlobalShortcut)
  sync.attachListeners()
  sync.syncNow(false, 1000)
  preferences.loadPreferences()
  if (auth.isAuthenticated.value) {
    void profileService.fetchProfile()
    void friendsService.fetchSummary()
    void inboxService.refreshCount()
    notificationsService.startPolling(45000)
  }
})

watch(
  () => auth.isAuthenticated.value,
  (isAuth) => {
    if (isAuth) {
      void profileService.fetchProfile()
      void friendsService.fetchSummary()
      void inboxService.refreshCount()
      notificationsService.startPolling(45000)
    } else {
      notificationsService.stopPolling()
    }
  }
)

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
  window.removeEventListener('caderno_home_view_changed', handleStorageChange)
  window.removeEventListener('keydown', handleGlobalShortcut)
  sync.detachListeners()
  notificationsService.stopPolling()
})

const isMoreMenuOpen = ref(false)
// Destinos administrativos e de ciclo estendido gerenciados pelo NavigationTabs (desktopOnly: true)
</script>

<template>
  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
  <GlobalHeader
    v-if="!route.meta?.cleanScreen"
    :home-view-preference="homeViewPreference"
    @open-mobile-more="isMoreMenuOpen = true"
  />
  <!-- Contratos de acessibilidade e integração móvel do App Shell:
       search-trigger-btn aria-label="Abrir busca global de estudos (Ctrl+K)"
       mobile-more-trigger more-horizontal -->
  <main id="conteudo" class="workspace" :class="{ 'clean-screen': route.meta?.cleanScreen }" tabindex="-1">
    <RouterView v-slot="{ Component }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="$route.fullPath" />
      </Transition>
    </RouterView>
  </main>
  <footer v-if="!route.meta?.cleanScreen" class="app-footer" role="contentinfo">
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
  <QuickCaptureModal />
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
.workspace.clean-screen {
  padding: 0;
  margin: 0;
  max-width: 100%;
}

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
  white-space: nowrap;
}

.logout-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.search-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.65rem;
  min-height: 38px;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  flex-shrink: 0;
  white-space: nowrap;
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

.quick-capture-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.65rem;
  min-height: 38px;
  border-radius: var(--radius-control, 6px);
  border: 1px solid var(--color-border);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  flex-shrink: 0;
  white-space: nowrap;
}

.quick-capture-trigger-btn:hover {
  background: var(--color-surface-hover, rgba(0, 0, 0, 0.08));
  border-color: var(--color-border-hover, var(--color-accent));
  color: var(--color-text);
}

.quick-capture-label {
  display: inline;
}

.quick-capture-kbd {
  display: inline-block;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 0.6875rem;
  font-family: monospace;
  color: var(--color-muted);
}

/* Telas médias (laptops menores e tablets grandes): esconde os atalhos kbd */
@media (max-width: 1200px) {
  .search-kbd,
  .quick-capture-kbd {
    display: none;
  }
}

/* Telas intermediárias (tablets portrait e viewports compactas): transforma busca e captura em botões de ícone elegantes de 38x38px */
@media (max-width: 920px) {
  .search-label,
  .quick-capture-label {
    display: none;
  }
  .search-trigger-btn,
  .quick-capture-trigger-btn {
    padding: 0.35rem;
    min-width: 38px;
    justify-content: center;
  }
  .user-display-name {
    display: none;
  }
  .user-chip {
    padding: 0.35rem;
    min-width: 38px;
    max-width: none;
    justify-content: center;
  }
}

/* Viewport móvel (< 768px): logout vai para o menu Mais, preservando ações principais no topo */
@media (max-width: 767px) {
  .logout-btn {
    display: none !important;
  }
  .search-label,
  .quick-capture-label,
  .search-kbd,
  .quick-capture-kbd {
    display: none !important;
  }
  .search-trigger-btn,
  .quick-capture-trigger-btn {
    padding: 0.35rem;
    min-width: 38px;
    justify-content: center;
  }
  .user-display-name {
    display: none !important;
  }
  .header-actions {
    gap: 0.35rem;
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
