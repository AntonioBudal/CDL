<script setup lang="ts">
import Icon from '../../ui/Icon.vue'
import type { CanvasToolMode } from '../../../types.ts'

interface Props {
  zoomLevel: number
  hasSelection?: boolean
  selectedCount?: number
  hasNodes?: boolean
  activeTool?: CanvasToolMode
}

withDefaults(defineProps<Props>(), {
  hasSelection: false,
  selectedCount: 0,
  hasNodes: true,
  activeTool: 'select',
})

const emit = defineEmits<{
  (e: 'zoom-in'): void
  (e: 'zoom-out'): void
  (e: 'reset-zoom'): void
  (e: 'fit-to-view'): void
  (e: 'clear-selection'): void
  (e: 'add-frame'): void
  (e: 'quick-create'): void
  (e: 'set-tool', tool: CanvasToolMode): void
}>()
</script>

<template>
  <div class="canvas-toolbar" role="toolbar" aria-label="Ferramentas e navegação do Canvas">
    <!-- Grupo de Ferramentas Modais -->
    <div class="tool-mode-group" role="radiogroup" aria-label="Modo de interação">
      <button
        type="button"
        class="canvas-tool-btn tool-mode-btn"
        :class="{ 'is-active': activeTool === 'select' }"
        title="Ferramenta de Seleção e Mover (V)"
        aria-label="Selecionar"
        role="radio"
        :aria-checked="activeTool === 'select'"
        @click="emit('set-tool', 'select')"
      >
        <Icon name="grid" :size="16" />
      </button>

      <button
        type="button"
        class="canvas-tool-btn tool-mode-btn"
        :class="{ 'is-active': activeTool === 'pan' }"
        title="Ferramenta Mão / Navegação Livre (H ou Espaço)"
        aria-label="Mão"
        role="radio"
        :aria-checked="activeTool === 'pan'"
        @click="emit('set-tool', 'pan')"
      >
        <Icon name="grip-vertical" :size="16" />
      </button>

      <button
        type="button"
        class="canvas-tool-btn tool-mode-btn"
        :class="{ 'is-active': activeTool === 'frame' }"
        title="Desenhar Moldura Espacial (F)"
        aria-label="Moldura"
        role="radio"
        :aria-checked="activeTool === 'frame'"
        @click="emit('set-tool', 'frame')"
      >
        <Icon name="folder" :size="16" />
      </button>

      <button
        type="button"
        class="canvas-tool-btn tool-mode-btn"
        :class="{ 'is-active': activeTool === 'connect' }"
        title="Ferramenta de Conexão Semântica (C)"
        aria-label="Conectar"
        role="radio"
        :aria-checked="activeTool === 'connect'"
        @click="emit('set-tool', 'connect')"
      >
        <Icon name="link" :size="16" />
      </button>
    </div>

    <div class="toolbar-divider" aria-hidden="true" />

    <!-- Ação de Criação Rápida de Estudo -->
    <div class="quick-action-group">
      <button
        type="button"
        class="canvas-tool-btn primary-action-btn quick-create-btn"
        title="Criar novo estudo no Canvas (Duplo clique ou botão)"
        aria-label="Novo Estudo"
        @click="emit('quick-create')"
      >
        <Icon name="plus" :size="16" />
      </button>
    </div>

    <div class="toolbar-divider" aria-hidden="true" />

    <!-- Controles de Zoom e Enquadramento -->
    <div class="zoom-controls">
      <button
        type="button"
        class="canvas-tool-btn zoom-btn"
        title="Aproximar visualização (+)"
        aria-label="Aumentar zoom"
        @click="emit('zoom-in')"
      >
        <Icon name="plus" :size="15" />
      </button>

      <span class="zoom-indicator" aria-live="polite" aria-atomic="true">
        {{ Math.round(zoomLevel * 100) }}%
      </span>

      <button
        type="button"
        class="canvas-tool-btn zoom-btn"
        title="Afastar visualização (-)"
        aria-label="Diminuir zoom"
        @click="emit('zoom-out')"
      >
        <Icon name="minus" :size="15" />
      </button>

      <button
        type="button"
        class="canvas-tool-btn reset-btn"
        title="Resetar escala para 100%"
        aria-label="Resetar zoom para 100%"
        @click="emit('reset-zoom')"
      >
        <Icon name="rotate-ccw" :size="14" />
      </button>

      <button
        v-if="hasNodes"
        type="button"
        class="canvas-tool-btn fit-btn"
        title="Ajustar e centralizar todos os estudos na tela"
        aria-label="Ajustar estudos à tela"
        @click="emit('fit-to-view')"
      >
        <Icon name="maximize-2" :size="15" />
      </button>

      <button
        type="button"
        class="canvas-tool-btn add-frame-btn"
        title="Criar moldura delimitadora"
        aria-label="Adicionar moldura manual"
        @click="emit('add-frame')"
      >
        <Icon name="folder-plus" :size="15" />
      </button>
    </div>

    <!-- Indicador de Seleção Múltipla -->
    <div v-if="hasSelection && selectedCount > 0" class="selection-badge" role="status">
      <span class="badge-text">{{ selectedCount }} sel.</span>
      <button
        type="button"
        class="clear-sel-btn"
        title="Limpar seleção"
        aria-label="Limpar seleção"
        @click="emit('clear-selection')"
      >
        <Icon name="x" :size="13" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.canvas-toolbar {
  display: inline-flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: 0.35rem;
  padding: 0.3rem 0.5rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 9999px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  user-select: none;
  z-index: 40;
  max-width: 100%;
  overflow-x: auto;
  white-space: nowrap !important;
  box-sizing: border-box;
}

.tool-mode-group,
.quick-action-group,
.zoom-controls {
  display: inline-flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  gap: 0.25rem;
  flex-shrink: 0 !important;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background-color: var(--color-border, #e2e8f0);
  margin: 0 0.15rem;
  flex-shrink: 0;
}

/* Blindagem total contra seletores globais como :root :is(button, .button) */
:root .canvas-toolbar :is(button, .button).canvas-tool-btn,
.canvas-toolbar .canvas-tool-btn {
  display: inline-flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  flex: 0 0 36px !important;
  width: 36px !important;
  height: 36px !important;
  min-width: 36px !important;
  min-height: 36px !important;
  max-width: 36px !important;
  max-height: 36px !important;
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 50% !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  color: var(--color-text-primary, #1e293b) !important;
  cursor: pointer !important;
  line-height: 1 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  box-shadow: none !important;
  text-decoration: none !important;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

:root .canvas-toolbar :is(button, .button).canvas-tool-btn:hover,
.canvas-toolbar .canvas-tool-btn:hover {
  background: var(--color-surface-hover, #f1f5f9) !important;
  color: var(--color-primary, #2563eb) !important;
}

:root .canvas-toolbar :is(button, .button).canvas-tool-btn:focus-visible,
.canvas-toolbar .canvas-tool-btn:focus-visible {
  outline: 2px solid var(--color-primary, #2563eb) !important;
  outline-offset: 2px !important;
}

:root .canvas-toolbar :is(button, .button).canvas-tool-btn.tool-mode-btn.is-active,
.canvas-toolbar .canvas-tool-btn.tool-mode-btn.is-active {
  background: color-mix(in srgb, var(--color-primary, #2563eb) 14%, var(--color-surface, #ffffff)) !important;
  color: var(--color-primary, #2563eb) !important;
  border-color: color-mix(in srgb, var(--color-primary, #2563eb) 30%, transparent) !important;
}

:root .canvas-toolbar :is(button, .button).canvas-tool-btn.primary-action-btn,
.canvas-toolbar .canvas-tool-btn.primary-action-btn {
  background: var(--color-primary, #2563eb) !important;
  color: #ffffff !important;
  border-color: var(--color-primary, #2563eb) !important;
}

:root .canvas-toolbar :is(button, .button).canvas-tool-btn.primary-action-btn:hover,
.canvas-toolbar .canvas-tool-btn.primary-action-btn:hover {
  filter: brightness(1.08);
  background: var(--color-primary, #2563eb) !important;
  color: #ffffff !important;
}

.canvas-toolbar .zoom-indicator {
  min-width: 42px;
  text-align: center;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted, #64748b);
  font-variant-numeric: tabular-nums;
  user-select: none;
  flex-shrink: 0;
  white-space: nowrap;
}

.canvas-toolbar .selection-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.55rem;
  background: var(--color-primary-light, #eff6ff);
  border: 1px solid var(--color-primary-border, #bfdbfe);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary, #2563eb);
  flex-shrink: 0;
  white-space: nowrap;
}

.canvas-toolbar .clear-sel-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--color-primary, #2563eb);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  min-width: 18px;
  min-height: 18px;
  flex-shrink: 0;
}

.canvas-toolbar .clear-sel-btn:hover {
  background: rgba(37, 99, 235, 0.15);
}

@media (max-width: 768px) {
  :root .canvas-toolbar :is(button, .button).canvas-tool-btn,
  .canvas-toolbar .canvas-tool-btn {
    flex: 0 0 44px !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    max-width: 44px !important;
    max-height: 44px !important;
  }
}
</style>
