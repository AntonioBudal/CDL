<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { routeTitle } from './i18n/index.ts'
import GlobalSearchModal from './components/search/GlobalSearchModal.vue'
import { usePreferences } from './composables/usePreferences.ts'
import { useSync } from './composables/useSync.ts'
import { useAuthStore } from './stores/auth.ts'
import { useProfile } from './composables/useProfile.ts'
import { useFriends } from './composables/useFriends.ts'
import { useNotifications } from './composables/useNotifications.ts'
import { useQuickCapture } from './composables/useQuickCapture.ts'
import { useInboxCount } from './composables/useInboxCount.ts'
import { useCircleInvites } from './composables/useCircleInvites.ts'
import QuickCaptureModal from './components/inbox/QuickCaptureModal.vue'
import MobileMoreMenu from './components/navigation/MobileMoreMenu.vue'
import GlobalHeader from './components/layout/GlobalHeader.vue'
import MobileTabBar from './components/layout/MobileTabBar.vue'
import { appVersion, buildCommit, fullVersion } from './utils/appVersion.ts'

const appVersionText = appVersion()
const appVersionDetail = fullVersion(appVersionText, buildCommit())
const route = useRoute()
const { t, locale } = useI18n() // F0.12.09
// Trocar o idioma sem trocar de tela também atualiza o título da aba.
watch(locale, () => {
  if (route.meta.title || route.name) {
    document.title = `${routeTitle(route.name, String(route.meta.title || 'Caderno de Leitura'))} — Leitorum`
  }
})
const router = useRouter()
const auth = useAuthStore()
const profileService = useProfile()
const friendsService = useFriends()
const notificationsService = useNotifications()
const sync = useSync()
const preferences = usePreferences()
const quickCapture = useQuickCapture()
const inboxService = useInboxCount()
const circleInvites = useCircleInvites() // F0.12.07

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
    void circleInvites.refresh()
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
      void circleInvites.refresh()
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
       mobile-more-trigger more-horizontal
       to: '/admin' requiresAdmin: true !auth.isAdmin.value
       to: '/amigos' nav-badge
       btn-notifications-trigger notifications-badge NotificationsDropdown notificationsService.startPolling(45000) -->
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
      <RouterLink to="/sobre" class="footer-link">{{ t('footer.about') }}</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <RouterLink to="/apoie" class="footer-support-link">{{ t('footer.support') }}</RouterLink>
      <span class="footer-sep" aria-hidden="true">·</span>
      <a class="footer-license" href="https://github.com/AntonioBudal/CDL" target="_blank" rel="noopener noreferrer">{{ t('footer.source') }}</a>
      <span class="footer-sep" aria-hidden="true">·</span>
      <!-- F0.12.01: versão SemVer; o commit só na dica. Não é link: a tela de versões fica escondida no Sobre. -->
      <span class="footer-version" :title="t('footer.version', { version: appVersionDetail })" :aria-label="t('footer.version', { version: appVersionText })" tabindex="0">v{{ appVersionText }}</span>
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
  <MobileTabBar
    v-if="!route.meta?.cleanScreen && auth.isAuthenticated.value"
    @open-more="isMoreMenuOpen = true"
  />
</template>

<style scoped>
.workspace.clean-screen {
  padding: 0;
  margin: 0;
  max-width: 100%;
}

/* Rodapé Global da Aplicação (Espaçoso e Proporcional) */
.app-footer {
  width: min(100% - var(--page-gutter, 2rem), var(--workspace-max-width, 74rem));
  margin: calc(var(--space-unit, 1rem) * 4) auto calc(var(--space-unit, 1rem) * 3);
  padding-top: calc(var(--space-unit, 1rem) * 1.5);
  padding-bottom: calc(var(--space-unit, 1rem) * 1.5);
  padding-inline: clamp(1rem, 3vw, 2rem);
  border-top: var(--border-width, 1px) solid var(--color-border);
  color: var(--color-muted);
  font-size: 0.875rem;
  box-sizing: border-box;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  width: 100%;
}

.footer-brand {
  font-weight: 600;
  color: var(--color-text);
}

.footer-version {
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}

.footer-version:focus-visible {
  outline: 2px solid var(--ring-focus);
  outline-offset: 2px;
}

.footer-sep {
  color: var(--color-border);
  user-select: none;
}

.footer-link,
.footer-support-link {
  color: var(--color-muted);
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover,
.footer-support-link:hover {
  color: var(--color-link);
  text-decoration: underline;
}

.footer-license {
  font-size: 0.8125rem;
  color: inherit;
  text-decoration: none;
}

.footer-license:hover {
  color: var(--color-link);
  text-decoration: underline;
}

@media (max-width: 767px) {
  .app-footer {
    margin-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem);
  }
}
</style>
