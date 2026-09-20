<script setup lang="ts">
import { ref } from 'vue'
import { STUDY_VIEW_OPTIONS, type StudyViewMode, type StudyViewOption } from '../../types'
import Icon from '../ui/Icon.vue'

interface Props {
  modelValue: StudyViewMode
  options?: StudyViewOption[]
  disabled?: boolean
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  options: () => STUDY_VIEW_OPTIONS,
  disabled: false,
  compact: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', mode: StudyViewMode): void
}>()

const tablistRef = ref<HTMLElement | null>(null)

function selectMode(mode: StudyViewMode) {
  if (props.disabled || props.modelValue === mode) return
  emit('update:modelValue', mode)
}

function focusTab(index: number) {
  if (!tablistRef.value) return
  const buttons = tablistRef.value.querySelectorAll<HTMLButtonElement>('button[role="tab"]')
  if (buttons[index]) {
    buttons[index].focus()
    const nextMode = props.options[index]?.id
    if (nextMode) {
      emit('update:modelValue', nextMode)
    }
  }
}

function onKeyDown(event: KeyboardEvent) {
  const currentIndex = props.options.findIndex((o) => o.id === props.modelValue)
  if (currentIndex === -1) return

  switch (event.key) {
    case 'ArrowRight':
    case 'ArrowDown': {
      event.preventDefault()
      const next = (currentIndex + 1) % props.options.length
      focusTab(next)
      break
    }
    case 'ArrowLeft':
    case 'ArrowUp': {
      event.preventDefault()
      const prev = (currentIndex - 1 + props.options.length) % props.options.length
      focusTab(prev)
      break
    }
    case 'Home': {
      event.preventDefault()
      focusTab(0)
      break
    }
    case 'End': {
      event.preventDefault()
      focusTab(props.options.length - 1)
      break
    }
  }
}
</script>

<template>
  <nav
    ref="tablistRef"
    class="view-switcher"
    :class="{ 'is-compact': compact, 'is-disabled': disabled }"
    role="tablist"
    aria-label="Modo de visualização dos estudos"
    @keydown="onKeyDown"
  >
    <button
      v-for="opt in options"
      :key="opt.id"
      type="button"
      class="view-tab-btn"
      :class="{ 'is-active': modelValue === opt.id }"
      role="tab"
      :aria-selected="modelValue === opt.id"
      :tabindex="modelValue === opt.id ? 0 : -1"
      :title="`${opt.label} — ${opt.description}`"
      :aria-label="`${opt.label}: ${opt.description}`"
      :disabled="disabled"
      @click="selectMode(opt.id)"
    >
      <Icon :name="opt.icon" :size="16" class="tab-icon" />
      <span class="tab-label">{{ opt.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.view-switcher {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  background-color: var(--color-surface-soft, #f1f5f9);
  padding: 3px;
  border-radius: var(--view-switcher-radius, 8px);
  border: var(--border-width, 1px) solid var(--color-border);
  box-sizing: border-box;
}

.view-tab-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-width: 44px;
  min-height: 44px;
  padding: 0 0.75rem;
  border: none;
  background: transparent;
  color: var(--color-muted, #64748b);
  border-radius: calc(var(--view-switcher-radius, 8px) - 2px);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  user-select: none;
  touch-action: manipulation;
  transition: background-color 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
}

.view-tab-btn:hover:not(:disabled):not(.is-active) {
  color: var(--color-inverse-bg, #0f172a);
  background-color: color-mix(in srgb, var(--color-surface) 60%, transparent);
}

.view-tab-btn.is-active {
  background-color: var(--color-surface, #ffffff);
  color: var(--color-accent, #1d4ed8);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.view-tab-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -1px;
  z-index: 2;
}

.tab-icon {
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .view-switcher {
    width: 100%;
    justify-content: space-around;
  }

  .view-tab-btn {
    flex: 1 1 0%;
    padding: 0;
  }

  .tab-label {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .view-tab-btn {
    transition: none !important;
  }
}
</style>
