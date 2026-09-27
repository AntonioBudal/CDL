<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import Icon from '../ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    isAdmin?: boolean
    username?: string
    displayName?: string
    avatarUrl?: string | null
    initials?: string
  }>(),
  {
    open: false,
    isAdmin: false,
    username: '',
    displayName: '',
    avatarUrl: null,
    initials: '',
  }
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'logout'): void
}>()

function handleKeydown(event: KeyboardEvent) {
  if (props.open && event.key === 'Escape') {
    emit('close')
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div
        v-if="open"
        class="mobile-drawer-backdrop"
        aria-hidden="true"
        @click="emit('close')"
      />
    </Transition>

    <Transition name="drawer-slide">
      <div
        v-if="open"
        class="mobile-more-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="mobile-more-title"
      >
        <div class="drawer-handle" aria-hidden="true">
          <span class="handle-bar" />
        </div>

        <div class="drawer-header">
          <div class="drawer-user-info" v-if="displayName || username">
            <div class="drawer-avatar">
              <img
                v-if="avatarUrl"
                :src="avatarUrl"
                alt=""
                class="avatar-img"
                aria-hidden="true"
              />
              <span v-else class="avatar-initials" aria-hidden="true">{{ initials }}</span>
            </div>
            <div class="drawer-user-text">
              <span class="drawer-user-name">{{ displayName || username }}</span>
              <span v-if="username" class="drawer-user-handle">@{{ username }}</span>
            </div>
          </div>
          <h2 id="mobile-more-title" v-else class="drawer-title">Mais Opções</h2>

          <button
            type="button"
            class="drawer-close-btn"
            aria-label="Fechar menu"
            @click="emit('close')"
          >
            <Icon name="x" :size="20" />
          </button>
        </div>

        <nav class="drawer-nav" aria-label="Navegação secundária">
          <RouterLink
            v-if="username"
            :to="`/@${username}`"
            class="drawer-item"
            @click="emit('close')"
          >
            <Icon name="user" :size="20" class="drawer-item-icon" />
            <span class="drawer-item-label">Meu Perfil</span>
          </RouterLink>

          <RouterLink
            to="/lixeira"
            class="drawer-item"
            @click="emit('close')"
          >
            <Icon name="trash" :size="20" class="drawer-item-icon" />
            <span class="drawer-item-label">Lixeira</span>
          </RouterLink>

          <RouterLink
            v-if="isAdmin"
            to="/admin"
            class="drawer-item"
            @click="emit('close')"
          >
            <Icon name="shield" :size="20" class="drawer-item-icon" />
            <span class="drawer-item-label">Administração</span>
          </RouterLink>

          <RouterLink
            to="/ajustes"
            class="drawer-item"
            @click="emit('close')"
          >
            <Icon name="sliders" :size="20" class="drawer-item-icon" />
            <span class="drawer-item-label">Ajustes & Conexão</span>
          </RouterLink>

          <div class="drawer-divider" role="separator" />

          <button
            type="button"
            class="drawer-item drawer-item-danger"
            @click="emit('logout'); emit('close')"
          >
            <Icon name="log-out" :size="20" class="drawer-item-icon" />
            <span class="drawer-item-label">Encerrar Sessão</span>
          </button>
        </nav>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.mobile-drawer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 90;
  background-color: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
}

.mobile-more-drawer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--color-surface);
  border-top-left-radius: var(--radius-panel, 1rem);
  border-top-right-radius: var(--radius-panel, 1rem);
  border-top: var(--border-width, 1px) solid var(--color-border);
  box-shadow: var(--shadow-panel, 0 -4px 20px rgba(0, 0, 0, 0.15));
  padding-bottom: max(calc(var(--space-unit) * 1.5), env(safe-area-inset-bottom, 16px));
  max-height: 80vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.drawer-handle {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.5rem 0 0.25rem;
}

.handle-bar {
  width: 2.25rem;
  height: 0.25rem;
  background: var(--color-border-strong, #cbd5e1);
  border-radius: 9999px;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1.25rem 0.75rem;
  border-bottom: var(--border-width, 1px) solid var(--color-border-subtle, var(--color-border));
}

.drawer-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
}

.drawer-user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.drawer-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: var(--color-surface-hover);
  border: var(--border-width, 1px) solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text);
  text-transform: uppercase;
}

.drawer-user-text {
  display: flex;
  flex-direction: column;
}

.drawer-user-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.drawer-user-handle {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.drawer-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: transparent;
  color: var(--color-muted);
  border-radius: var(--radius-control, 0.375rem);
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}

.drawer-close-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.drawer-nav {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0.75rem;
  gap: 0.25rem;
}

.drawer-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-height: 48px;
  padding: 0.625rem 1rem;
  border-radius: var(--radius-control, 0.375rem);
  text-decoration: none;
  color: var(--color-text);
  font-size: 0.9375rem;
  font-weight: 550;
  border: none;
  background: transparent;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background 0.15s ease, color 0.15s ease;
}

.drawer-item:hover,
.drawer-item:focus-visible {
  background: var(--color-surface-hover);
}

.drawer-item-icon {
  flex-shrink: 0;
  color: var(--color-muted);
}

.drawer-item:hover .drawer-item-icon {
  color: var(--color-text);
}

.drawer-item-label {
  flex: 1;
}

.drawer-divider {
  height: var(--border-width, 1px);
  background: var(--color-border);
  margin: 0.375rem 0.75rem;
}

.drawer-item-danger {
  color: var(--color-error-text, #ef4444);
}

.drawer-item-danger .drawer-item-icon {
  color: var(--color-error-marker, #ef4444);
}

.drawer-item-danger:hover {
  background: var(--color-error-bg, rgba(239, 68, 68, 0.1));
  color: var(--color-error-text, #dc2626);
}

/* Transições */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateY(100%);
}

@media (prefers-reduced-motion: reduce) {
  .drawer-fade-enter-active,
  .drawer-fade-leave-active,
  .drawer-slide-enter-active,
  .drawer-slide-leave-active {
    transition: none !important;
  }
}
</style>
