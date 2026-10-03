<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import type { DropdownMenuAlign } from '../../types/dropdown'

const props = withDefaults(
  defineProps<{
    align?: DropdownMenuAlign
    ariaLabel?: string
    disabled?: boolean
  }>(),
  {
    align: 'right',
    ariaLabel: 'Mais opções',
    disabled: false
  }
)

const emit = defineEmits<{
  (e: 'open'): void
  (e: 'close'): void
}>()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)
const menuRef = ref<HTMLElement | null>(null)
const defaultTriggerRef = ref<HTMLButtonElement | null>(null)

const menuAlignClass = computed(() => {
  return props.align === 'left' ? 'align-left' : 'align-right'
})

function getFocusableItems(): HTMLElement[] {
  if (!menuRef.value) return []
  return Array.from(
    menuRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), a:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  )
}

function open() {
  if (props.disabled || isOpen.value) return
  isOpen.value = true
  emit('open')
  nextTick(() => {
    const items = getFocusableItems()
    if (items.length > 0) {
      items[0].focus()
    } else if (menuRef.value) {
      menuRef.value.focus()
    }
  })
}

function close() {
  if (!isOpen.value) return
  isOpen.value = false
  emit('close')
}

function toggle() {
  if (isOpen.value) {
    close()
  } else {
    open()
  }
}

function onTriggerKeydown(event: KeyboardEvent) {
  if (props.disabled) return

  if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    event.stopPropagation()
    if (!isOpen.value) {
      open()
    } else {
      const items = getFocusableItems()
      if (items.length > 0) items[0].focus()
    }
  } else if (event.key === 'Escape' && isOpen.value) {
    event.preventDefault()
    event.stopPropagation()
    close()
  }
}

function onMenuKeydown(event: KeyboardEvent) {
  if (!isOpen.value) return

  // Conter propagação para não conflitar com listeners globais (ex: Active Recall)
  if (['Escape', 'ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
    event.stopPropagation()
  }

  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    if (defaultTriggerRef.value) {
      defaultTriggerRef.value.focus()
    } else if (containerRef.value) {
      const customTrigger = containerRef.value.querySelector<HTMLElement>('[aria-haspopup="menu"]')
      customTrigger?.focus()
    }
    return
  }

  const items = getFocusableItems()
  if (items.length === 0) return

  const activeIndex = items.indexOf(document.activeElement as HTMLElement)

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    const nextIndex = activeIndex >= 0 && activeIndex < items.length - 1 ? activeIndex + 1 : 0
    items[nextIndex].focus()
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    const prevIndex = activeIndex > 0 ? activeIndex - 1 : items.length - 1
    items[prevIndex].focus()
  } else if (event.key === 'Home') {
    event.preventDefault()
    items[0].focus()
  } else if (event.key === 'End') {
    event.preventDefault()
    items[items.length - 1].focus()
  } else if (event.key === 'Tab') {
    // Permite que o Tab feche o dropdown e siga a navegação natural
    close()
  }
}

function handlePointerDownOutside(event: PointerEvent) {
  if (!isOpen.value) return
  const target = event.target as Node | null
  if (containerRef.value && !containerRef.value.contains(target)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', handlePointerDownOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handlePointerDownOutside)
})

defineExpose({
  isOpen,
  open,
  close,
  toggle
})
</script>

<template>
  <div ref="containerRef" class="dropdown-menu-container">
    <slot name="trigger" :is-open="isOpen" :toggle="toggle" :on-keydown="onTriggerKeydown">
      <button
        ref="defaultTriggerRef"
        type="button"
        class="dropdown-trigger-btn secondary"
        :aria-label="ariaLabel"
        aria-haspopup="menu"
        :aria-expanded="isOpen"
        :disabled="disabled"
        @click="toggle"
        @keydown="onTriggerKeydown"
      >
        <svg
          class="w-4 h-4 dots-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"
          />
        </svg>
      </button>
    </slot>

    <Transition name="dropdown-fade">
      <div
        v-if="isOpen"
        ref="menuRef"
        role="menu"
        class="dropdown-menu-popover"
        :class="menuAlignClass"
        aria-orientation="vertical"
        tabindex="-1"
        @keydown="onMenuKeydown"
      >
        <slot :close="close" />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dropdown-menu-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.dropdown-trigger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 38px;
  min-height: 38px;
  padding: 0.375rem;
  border-radius: var(--radius-md, 0.5rem);
  border: 1px solid var(--color-border, #e4e4e7);
  background: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #18181b);
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.dropdown-trigger-btn:hover:not(:disabled) {
  background: var(--color-surface-hover, #f4f4f5);
  border-color: var(--color-border-hover, #d4d4d8);
}

.dropdown-trigger-btn:focus-visible {
  outline: 2px solid var(--color-primary, #4f46e5);
  outline-offset: 2px;
}

.dropdown-trigger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dots-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.dropdown-menu-popover {
  position: absolute;
  top: calc(100% + 6px);
  min-width: 200px;
  max-width: calc(100vw - 2rem);
  padding: 0.375rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e4e4e7);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.align-right {
  right: 0;
}

.align-left {
  left: 0;
}

/* Transições suaves */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}

@media (max-width: 768px) {
  .dropdown-trigger-btn {
    min-width: 44px;
    min-height: 44px;
    padding: 0.5rem;
  }
}
</style>
