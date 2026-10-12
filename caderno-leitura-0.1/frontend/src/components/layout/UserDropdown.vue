<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import Icon from '../ui/Icon.vue'
import { useAuthStore } from '../../stores/auth'
import { useProfile } from '../../composables/useProfile'

const router = useRouter()
const auth = useAuthStore()
const profileService = useProfile()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const currentUser = computed(() => auth.user.value)
const isAdmin = computed(() => auth.isAdmin.value)
const displayName = computed(() => profileService.profile.value?.display_name || currentUser.value?.display_name || currentUser.value?.username || 'Leitor')
const username = computed(() => profileService.profile.value?.username || currentUser.value?.username || '')
const avatarUrl = computed(() => profileService.profile.value?.avatar_url)
const initials = computed(() => profileService.initials.value || 'AN')

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function closeDropdown() {
  isOpen.value = false
}

function handleKeydown(e: KeyboardEvent) {
  if (!isOpen.value) return
  if (e.key === 'Escape') {
    e.preventDefault()
    closeDropdown()
  }
}

function handleClickOutside(e: MouseEvent) {
  if (!isOpen.value) return
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    closeDropdown()
  }
}

async function handleLogout() {
  closeDropdown()
  if (confirm('Deseja realmente sair da aplicação?')) {
    await auth.logout()
    router.replace('/login')
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
  <div ref="containerRef" class="user-dropdown-container">
    <button
      type="button"
      class="user-trigger-btn"
      :class="{ active: isOpen }"
      aria-haspopup="menu"
      :aria-expanded="isOpen"
      :aria-label="`Menu do usuário: ${displayName}`"
      title="Conta e opções de perfil"
      @click="toggleDropdown"
    >
      <img
        v-if="avatarUrl"
        :src="avatarUrl"
        alt=""
        class="header-avatar-img"
        aria-hidden="true"
      />
      <span
        v-else
        class="header-avatar-initials"
        aria-hidden="true"
      >
        {{ initials }}
      </span>
    </button>

    <Transition name="user-menu-fade">
      <div
        v-if="isOpen"
        class="user-dropdown-menu"
        role="menu"
        aria-label="Opções da conta"
      >
        <div class="user-menu-header">
          <div class="user-menu-header-avatar">
            <img v-if="avatarUrl" :src="avatarUrl" alt="" class="menu-avatar-img" aria-hidden="true" />
            <span v-else class="menu-avatar-initials" aria-hidden="true">{{ initials }}</span>
          </div>
          <div class="user-menu-info">
            <span class="user-menu-name">{{ displayName }}</span>
            <span v-if="username" class="user-menu-handle">@{{ username }}</span>
            <span v-if="isAdmin" class="user-menu-badge">Administrador</span>
          </div>
        </div>

        <div class="user-menu-divider" role="separator" />

        <div class="user-menu-links">
          <RouterLink
            :to="username ? `/@${username}` : '/ajustes'"
            class="user-menu-item"
            role="menuitem"
            @click="closeDropdown"
          >
            <Icon name="user" :size="16" />
            <span>Perfil Público</span>
          </RouterLink>

          <RouterLink
            to="/ajustes"
            class="user-menu-item"
            role="menuitem"
            @click="closeDropdown"
          >
            <Icon name="sliders" :size="16" />
            <span>Ajustes &amp; Preferências</span>
          </RouterLink>

          <RouterLink
            v-if="isAdmin"
            to="/admin"
            class="user-menu-item"
            role="menuitem"
            @click="closeDropdown"
          >
            <Icon name="shield" :size="16" />
            <span>Painel de Administração</span>
          </RouterLink>
        </div>

        <div class="user-menu-divider" role="separator" />

        <div class="user-menu-actions">
          <button
            type="button"
            class="user-menu-item user-logout-item"
            role="menuitem"
            @click="handleLogout"
          >
            <Icon name="log-out" :size="16" />
            <span>Encerrar Sessão (Sair)</span>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.user-dropdown-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.user-trigger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: 50%;
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 150ms ease, border-color 150ms ease;
}

.user-trigger-btn:hover,
.user-trigger-btn.active {
  background-color: var(--color-surface-hover);
  border-color: var(--color-border);
}

.user-trigger-btn:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

.header-avatar-img,
.header-avatar-initials {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-avatar-img {
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.header-avatar-initials {
  background-color: var(--color-selected-bg, var(--color-surface-soft));
  color: var(--color-selected-text, var(--color-accent));
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid var(--color-border);
}

.user-trigger-name {
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trigger-chevron {
  color: var(--color-muted);
  transition: transform 150ms ease;
}

.user-trigger-btn.active .trigger-chevron {
  transform: rotate(180deg);
}

.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 240px;
  background-color: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-panel, 0.5rem);
  box-shadow: 0 10px 25px -5px color-mix(in srgb, var(--color-inverse-bg, #000) 15%, transparent);
  padding: 0.5rem 0;
  z-index: 1050;
  display: flex;
  flex-direction: column;
}

.user-menu-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem 0.5rem;
}

.menu-avatar-img,
.menu-avatar-initials {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-avatar-img {
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.menu-avatar-initials {
  background-color: var(--color-selected-bg, var(--color-surface-soft));
  color: var(--color-selected-text, var(--color-accent));
  font-size: 0.875rem;
  font-weight: 700;
  border: 1px solid var(--color-border);
}

.user-menu-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-menu-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu-handle {
  font-size: 0.8125rem;
  color: var(--color-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu-badge {
  display: inline-block;
  align-self: flex-start;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.1rem 0.35rem;
  border-radius: var(--radius-badge, 0.25rem);
  background-color: var(--color-info-bg, var(--color-surface-soft));
  color: var(--color-accent);
  margin-top: 0.25rem;
}

.user-menu-divider {
  height: 1px;
  background-color: var(--color-border-divider, var(--color-border));
  margin: 0.4rem 0;
  border: none;
}

.user-menu-links,
.user-menu-actions {
  display: flex;
  flex-direction: column;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 1rem;
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

.user-menu-item:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-hover-text, var(--color-text));
}

.user-menu-item:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: -2px;
}

.user-logout-item {
  color: var(--color-error-text, #9f1239);
}

.user-logout-item:hover {
  background-color: var(--color-error-bg, #ffe4e6);
  color: var(--color-error-text, #9f1239);
}

.user-menu-fade-enter-active,
.user-menu-leave-active {
  transition: opacity 150ms ease, transform 150ms ease;
}

.user-menu-fade-enter-from,
.user-menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .user-menu-fade-enter-active,
  .user-menu-leave-active,
  .user-dropdown-menu,
  .trigger-chevron {
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 640px) {
  .user-trigger-name {
    display: none;
  }
}
</style>
