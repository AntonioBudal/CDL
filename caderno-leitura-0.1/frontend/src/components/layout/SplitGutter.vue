<script setup lang="ts">
import { computed } from 'vue'
import type { PaneId } from '../../types'
import Icon from '../ui/Icon.vue'

interface Props {
  pane: PaneId
  currentWidth: number
  minWidth?: number
  maxWidth?: number
  collapsed: boolean
  ariaLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  minWidth: 240,
  maxWidth: 600,
  ariaLabel: undefined
})

const emit = defineEmits<{
  (e: 'start-drag', event: PointerEvent): void
  (e: 'toggle'): void
  (e: 'reset'): void
  (e: 'step', delta: number): void
}>()

const computedAriaLabel = computed(() => {
  if (props.ariaLabel) return props.ariaLabel
  return props.pane === 'left'
    ? 'Separador redimensionável da navegação'
    : 'Separador redimensionável do painel de contexto'
})

function onPointerDown(event: PointerEvent) {
  emit('start-drag', event)
}

function onDoubleClick() {
  emit('reset')
}

function onKeyDown(event: KeyboardEvent) {
  const stepAmount = 10

  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      // Para o painel esquerdo, seta esquerda diminui largura. Para o direito, expande.
      emit('step', props.pane === 'left' ? -stepAmount : stepAmount)
      break

    case 'ArrowRight':
      event.preventDefault()
      // Para o painel esquerdo, seta direita aumenta largura. Para o direito, diminui.
      emit('step', props.pane === 'left' ? stepAmount : -stepAmount)
      break

    case 'Home':
      event.preventDefault()
      emit('step', props.minWidth - props.currentWidth)
      break

    case 'End':
      event.preventDefault()
      emit('step', props.maxWidth - props.currentWidth)
      break

    case 'Enter':
    case ' ':
      event.preventDefault()
      emit('toggle')
      break
  }
}
</script>

<template>
  <div
    class="split-gutter"
    :class="[`split-gutter-${pane}`, { 'is-collapsed': collapsed }]"
    role="separator"
    tabindex="0"
    aria-orientation="vertical"
    :aria-valuenow="collapsed ? 0 : Math.round(currentWidth)"
    :aria-valuemin="minWidth"
    :aria-valuemax="maxWidth"
    :aria-label="computedAriaLabel"
    @pointerdown="onPointerDown"
    @dblclick="onDoubleClick"
    @keydown="onKeyDown"
  >
    <div class="gutter-handle" aria-hidden="true">
      <div class="gutter-line" />
    </div>

    <!-- Botão de alternância rápida de colapso -->
    <button
      type="button"
      class="gutter-toggle-btn"
      tabindex="-1"
      :aria-label="collapsed ? `Expandir painel ${pane === 'left' ? 'esquerdo' : 'direito'}` : `Recolher painel ${pane === 'left' ? 'esquerdo' : 'direito'}`"
      @click.stop="emit('toggle')"
      @pointerdown.stop
    >
      <Icon
        :name="pane === 'left' ? (collapsed ? 'chevron-right' : 'chevron-down') : (collapsed ? 'chevron-down' : 'chevron-right')"
        size="12"
        :class="(pane === 'left' ? !collapsed : collapsed) ? 'toggle-icon icon-rotated' : 'toggle-icon'"
      />
    </button>
  </div>
</template>

<style scoped>
.split-gutter {
  position: relative;
  width: var(--gutter-width, 8px);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: col-resize;
  touch-action: none;
  background-color: transparent;
  user-select: none;
  transition: background-color 0.15s ease;
  z-index: 10;
}

.split-gutter:hover {
  background-color: color-mix(in srgb, var(--color-accent) 15%, transparent);
}

.split-gutter:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: -1px;
  background-color: color-mix(in srgb, var(--color-accent) 20%, transparent);
}

.gutter-handle {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gutter-line {
  width: 1px;
  height: 100%;
  background-color: var(--color-border-divider);
  transition: background-color 0.15s ease, width 0.15s ease;
}

.split-gutter:hover .gutter-line,
.split-gutter:focus-visible .gutter-line {
  background-color: var(--color-accent);
  width: 2px;
}

.gutter-toggle-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-small, 4px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-muted);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  opacity: 0;
  transition: opacity 0.15s ease, background-color 0.15s ease, color 0.15s ease;
  z-index: 15;
}

.split-gutter:hover .gutter-toggle-btn,
.split-gutter:focus-visible .gutter-toggle-btn,
.gutter-toggle-btn:focus-visible {
  opacity: 1;
}

.gutter-toggle-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.toggle-icon {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.icon-rotated {
  transform: rotate(180deg);
}

@media (prefers-reduced-motion: reduce) {
  .split-gutter,
  .gutter-line,
  .gutter-toggle-btn,
  .toggle-icon {
    transition: none !important;
  }
}
</style>
