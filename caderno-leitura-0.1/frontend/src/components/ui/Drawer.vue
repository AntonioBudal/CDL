<script setup lang="ts">
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import Icon from './Icon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    description?: string
    width?: string
  }>(),
  {
    open: false,
    description: '',
    width: '420px',
  }
)

const emit = defineEmits<{
  (e: 'close'): void
}>()

const drawerRef = ref<HTMLElement | null>(null)
let previousActiveElement: HTMLElement | null = null

function getFocusableElements(): HTMLElement[] {
  if (!drawerRef.value) return []
  return Array.from(
    drawerRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  )
}

function handleKeydown(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
    return
  }
  if (e.key === 'Tab') {
    const focusable = getFocusableElements()
    if (focusable.length === 0) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      previousActiveElement = document.activeElement as HTMLElement | null
      document.addEventListener('keydown', handleKeydown)
      document.body.style.overflow = 'hidden'
      nextTick(() => {
        const focusable = getFocusableElements()
        const firstInput = focusable.find((el) => ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName))
        if (firstInput) {
          firstInput.focus()
        } else if (focusable.length > 0) {
          focusable[0].focus()
        } else if (drawerRef.value) {
          drawerRef.value.focus()
        }
      })
    } else {
      document.removeEventListener('keydown', handleKeydown)
      document.body.style.overflow = ''
      if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
        previousActiveElement.focus()
      }
      previousActiveElement = null
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div
        v-if="open"
        class="drawer-backdrop"
        aria-hidden="true"
        @click="emit('close')"
      />
    </Transition>

    <Transition name="drawer-slide">
      <div
        v-if="open"
        ref="drawerRef"
        class="drawer-panel"
        :style="{ '--drawer-width': width }"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="title ? 'drawer-heading' : undefined"
        :aria-describedby="description ? 'drawer-desc' : undefined"
        tabindex="-1"
      >
        <header class="drawer-header">
          <div class="drawer-title-group">
            <h2 id="drawer-heading" class="drawer-title">{{ title }}</h2>
            <p v-if="description" id="drawer-desc" class="drawer-description">
              {{ description }}
            </p>
          </div>
          <button
            type="button"
            class="drawer-close-btn"
            aria-label="Fechar gaveta (Esc)"
            title="Fechar (Esc)"
            @click="emit('close')"
          >
            <Icon name="x" :size="20" :stroke-width="2" />
          </button>
        </header>

        <div class="drawer-body">
          <slot />
        </div>

        <footer v-if="$slots.footer" class="drawer-footer">
          <slot name="footer" />
        </footer>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background-color: color-mix(in srgb, var(--color-inverse-bg, #000) 45%, transparent);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  z-index: 1000;
  transition: opacity 200ms ease;
}

.drawer-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: min(var(--drawer-width, 420px), 100vw);
  background-color: var(--color-surface);
  border-left: var(--border-width, 1px) solid var(--color-border);
  box-shadow: -8px 0 24px -4px color-mix(in srgb, var(--color-inverse-bg, #000) 18%, transparent);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  outline: none;
  transform: translateX(0);
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: var(--border-width, 1px) solid var(--color-border-divider, var(--color-border));
  background-color: var(--color-surface);
}

.drawer-title-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.drawer-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.3;
}

.drawer-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
  line-height: 1.4;
}

.drawer-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--radius-button, 0.4rem);
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
}

.drawer-close-btn:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
  border-color: var(--color-border);
}

.drawer-close-btn:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

.drawer-body {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 1.5rem;
  overscroll-behavior: contain;
}

.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: var(--border-width, 1px) solid var(--color-border-divider, var(--color-border));
  background-color: var(--color-surface-soft, var(--color-surface));
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Animações aceleradas por GPU */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 200ms ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-slide-enter-active {
  transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-slide-leave-active {
  transition: transform 180ms ease-in;
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
}

/* Fallback obrigatório para preferência de movimento reduzido */
@media (prefers-reduced-motion: reduce) {
  .drawer-fade-enter-active,
  .drawer-fade-leave-active,
  .drawer-slide-enter-active,
  .drawer-slide-leave-active,
  .drawer-backdrop,
  .drawer-panel {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (max-width: 640px) {
  .drawer-panel {
    width: 100vw;
    border-left: none;
  }
}
</style>
