<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { PaneId, SplitLayoutDimensions } from '../../types'
import { useSplitPanes } from '../../composables/useSplitPanes'
import SplitPane from './SplitPane.vue'
import SplitGutter from './SplitGutter.vue'
import Icon from '../ui/Icon.vue'

interface Props {
  bookId?: string | number | null
  leftCollapsible?: boolean
  rightCollapsible?: boolean
  minPaneWidth?: number
  maxPaneWidth?: number
  defaultPaneWidth?: number
  minMainWidth?: number
  hasRightPane?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  bookId: undefined,
  leftCollapsible: true,
  rightCollapsible: true,
  minPaneWidth: 240,
  maxPaneWidth: 600,
  defaultPaneWidth: 300,
  minMainWidth: 360,
  hasRightPane: false
})

const emit = defineEmits<{
  (e: 'resize', dimensions: SplitLayoutDimensions): void
  (e: 'toggle', pane: PaneId, collapsed: boolean): void
}>()

const containerRef = ref<HTMLElement | null>(null)

const {
  leftWidth,
  rightWidth,
  leftCollapsed,
  rightCollapsed,
  isDragging,
  activePane,
  layoutMode,
  containerWidth,
  startDrag,
  toggleCollapse: baseToggleCollapse,
  resetToDefault,
  stepResize,
  getDimensions
} = useSplitPanes({
  bookId: props.bookId,
  initialLeftWidth: props.defaultPaneWidth,
  initialRightWidth: props.defaultPaneWidth,
  minWidth: props.minPaneWidth,
  maxWidth: props.maxPaneWidth,
  minMainWidth: props.minMainWidth,
  onResizeEnd: (dims) => {
    emit('resize', dims)
  }
})

// Atualiza a largura do contêiner com ResizeObserver
let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  if (containerRef.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        containerWidth.value = entry.contentRect.width
      }
    })
    resizeObserver.observe(containerRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

function toggleCollapse(pane: PaneId) {
  baseToggleCollapse(pane)
  const isNowCollapsed = pane === 'left' ? leftCollapsed.value : rightCollapsed.value
  emit('toggle', pane, isNowCollapsed)
}

function handleGutterDrag(pane: PaneId, event: PointerEvent) {
  startDrag(pane, event)
}

function handleGutterStep(pane: PaneId, delta: number) {
  stepResize(pane, delta)
}

function handleGutterReset(pane: PaneId) {
  resetToDefault(pane)
}

// Fechamento de gaveta mobile ao clicar no backdrop
function closeMobileDrawer(pane: PaneId) {
  if (pane === 'left' && !leftCollapsed.value) {
    toggleCollapse('left')
  } else if (pane === 'right' && !rightCollapsed.value) {
    toggleCollapse('right')
  }
}

// Fechamento com Esc em modo gaveta
function onKeyDownGlobal(event: KeyboardEvent) {
  if (event.key === 'Escape' && (layoutMode.value === 'mobile' || layoutMode.value === 'drawer')) {
    if (!leftCollapsed.value) {
      toggleCollapse('left')
    } else if (!rightCollapsed.value) {
      toggleCollapse('right')
    }
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('keydown', onKeyDownGlobal)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', onKeyDownGlobal)
  }
})

defineExpose({
  leftWidth,
  rightWidth,
  leftCollapsed,
  rightCollapsed,
  isDragging,
  layoutMode,
  toggleCollapse,
  resetToDefault,
  stepResize,
  getDimensions
})
</script>

<template>
  <div
    ref="containerRef"
    class="split-layout"
    :class="[
      `layout-${layoutMode}`,
      {
        'split-resizing': isDragging,
        'has-right-pane': hasRightPane
      }
    ]"
    :style="{
      '--pane-left-width': `${leftWidth}px`,
      '--pane-right-width': `${rightWidth}px`
    }"
  >
    <!-- Modo Desktop / Split Padrão -->
    <template v-if="layoutMode === 'split'">
      <!-- Painel Esquerdo (Navegação) -->
      <SplitPane
        id="left"
        :width="leftWidth"
        :collapsed="leftCollapsed"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :is-resizing="isDragging && activePane === 'left'"
      >
        <slot name="left" />
      </SplitPane>

      <!-- Divisor Esquerdo -->
      <SplitGutter
        pane="left"
        :current-width="leftWidth"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :collapsed="leftCollapsed"
        @start-drag="(e) => handleGutterDrag('left', e)"
        @toggle="() => toggleCollapse('left')"
        @reset="() => handleGutterReset('left')"
        @step="(delta) => handleGutterStep('left', delta)"
      />

      <!-- Palco Central Principal -->
      <SplitPane id="main">
        <slot />
      </SplitPane>

      <!-- Divisor Direito (se houver painel de contexto) -->
      <SplitGutter
        v-if="hasRightPane"
        pane="right"
        :current-width="rightWidth"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :collapsed="rightCollapsed"
        @start-drag="(e) => handleGutterDrag('right', e)"
        @toggle="() => toggleCollapse('right')"
        @reset="() => handleGutterReset('right')"
        @step="(delta) => handleGutterStep('right', delta)"
      />

      <!-- Painel Direito (Contexto / Inspetor) -->
      <SplitPane
        v-if="hasRightPane"
        id="right"
        :width="rightWidth"
        :collapsed="rightCollapsed"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :is-resizing="isDragging && activePane === 'right'"
      >
        <slot name="right" />
      </SplitPane>
    </template>

    <!-- Modo Tablet (Drawer para Contexto, Split para Navegação se couber) -->
    <template v-else-if="layoutMode === 'drawer'">
      <!-- Painel Esquerdo -->
      <SplitPane
        id="left"
        :width="leftWidth"
        :collapsed="leftCollapsed"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :is-resizing="isDragging && activePane === 'left'"
      >
        <slot name="left" />
      </SplitPane>

      <SplitGutter
        pane="left"
        :current-width="leftWidth"
        :min-width="minPaneWidth"
        :max-width="maxPaneWidth"
        :collapsed="leftCollapsed"
        @start-drag="(e) => handleGutterDrag('left', e)"
        @toggle="() => toggleCollapse('left')"
        @reset="() => handleGutterReset('left')"
        @step="(delta) => handleGutterStep('left', delta)"
      />

      <!-- Palco Principal -->
      <SplitPane id="main">
        <slot />
      </SplitPane>

      <!-- Gaveta Lateral Sobreposta para Painel Direito no Tablet -->
      <Teleport to="body" v-if="hasRightPane && !rightCollapsed">
        <div class="drawer-backdrop" @click="closeMobileDrawer('right')" />
        <aside class="drawer-sheet drawer-right" role="dialog" aria-modal="true" aria-label="Painel de contexto">
          <div class="drawer-header">
            <h2 class="drawer-title">Contexto & Notas</h2>
            <button
              type="button"
              class="drawer-close-btn"
              aria-label="Fechar painel de contexto"
              @click="closeMobileDrawer('right')"
            >
              <Icon name="x" size="20" />
            </button>
          </div>
          <div class="drawer-content">
            <slot name="right" />
          </div>
        </aside>
      </Teleport>
    </template>

    <!-- Modo Mobile (< 768px: Gavetas Deslizantes completas) -->
    <template v-else>
      <!-- Palco Principal Ocupa 100% -->
      <SplitPane id="main">
        <slot />
      </SplitPane>

      <!-- Gaveta Mobile de Navegação (Esquerda) -->
      <Teleport to="body" v-if="!leftCollapsed">
        <div class="drawer-backdrop" @click="closeMobileDrawer('left')" />
        <aside class="drawer-sheet drawer-left" role="dialog" aria-modal="true" aria-label="Navegador de leitura">
          <div class="drawer-header">
            <h2 class="drawer-title">Navegação & Capítulos</h2>
            <button
              type="button"
              class="drawer-close-btn"
              aria-label="Fechar navegação"
              @click="closeMobileDrawer('left')"
            >
              <Icon name="x" size="20" />
            </button>
          </div>
          <div class="drawer-content">
            <slot name="left" />
          </div>
        </aside>
      </Teleport>

      <!-- Gaveta Mobile de Contexto (Direita) -->
      <Teleport to="body" v-if="hasRightPane && !rightCollapsed">
        <div class="drawer-backdrop" @click="closeMobileDrawer('right')" />
        <aside class="drawer-sheet drawer-right" role="dialog" aria-modal="true" aria-label="Painel de contexto">
          <div class="drawer-header">
            <h2 class="drawer-title">Contexto & Notas</h2>
            <button
              type="button"
              class="drawer-close-btn"
              aria-label="Fechar painel de contexto"
              @click="closeMobileDrawer('right')"
            >
              <Icon name="x" size="20" />
            </button>
          </div>
          <div class="drawer-content">
            <slot name="right" />
          </div>
        </aside>
      </Teleport>
    </template>
  </div>
</template>

<style scoped>
.split-layout {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  box-sizing: border-box;
}

/* Neutralização de seleção de texto e cursor unificado durante o arrasto */
.split-layout.split-resizing,
:global(body.split-resizing) {
  user-select: none !important;
  -webkit-user-select: none !important;
  cursor: col-resize !important;
}

/* Gavetas / Drawers para Mobile e Tablet */
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

.drawer-sheet {
  position: fixed;
  top: 0;
  bottom: 0;
  width: min(85vw, 360px);
  background-color: var(--color-surface, #ffffff);
  border-left: 1px solid var(--color-border);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 101;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-left {
  left: 0;
  right: auto;
  border-left: none;
  border-right: 1px solid var(--color-border);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
  animation: slideInLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-right {
  right: 0;
  left: auto;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--color-border-divider);
  background-color: var(--color-surface-soft, #f8fafc);
  flex-shrink: 0;
}

.drawer-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-inverse-bg, #0f172a);
  margin: 0;
}

.drawer-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-small, 4px);
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.drawer-close-btn:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-inverse-bg);
}

.drawer-close-btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.drawer-content {
  flex: 1 1 auto;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

@keyframes slideInLeft {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@media (max-width: 767px) {
  .split-layout :deep(.split-gutter) {
    display: none !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .drawer-backdrop,
  .drawer-sheet {
    animation: none !important;
  }
}
</style>
