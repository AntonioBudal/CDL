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
        <Icon name="grid" :size="15" />
        <span class="btn-label">Selecionar</span>
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
        <Icon name="grip-vertical" :size="15" />
        <span class="btn-label">Mão</span>
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
        <Icon name="folder" :size="15" />
        <span class="btn-label">Moldura</span>
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
        <Icon name="link" :size="15" />
        <span class="btn-label">Conectar</span>
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
        <Icon name="plus" :size="15" />
        <span class="btn-label">Novo Estudo</span>
      </button>
    </div>

    <div class="toolbar-divider" aria-hidden="true" />

    <!-- Controles de Zoom e Enquadramento -->
    <div class="zoom-controls">
      <button
        type="button"
        class="canvas-tool-btn"
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
        class="canvas-tool-btn"
        title="Afastar visualização (-)"
        aria-label="Diminuir zoom"
        @click="emit('zoom-out')"
      >
        <span class="zoom-minus" aria-hidden="true">−</span>
      </button>

      <button
        type="button"
        class="canvas-tool-btn reset-btn"
        title="Resetar escala para 100%"
        aria-label="Resetar zoom para 100%"
        @click="emit('reset-zoom')"
      >
        100%
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
        <span class="btn-label">Ajustar</span>
      </button>

      <button
        type="button"
        class="canvas-tool-btn add-frame-btn"
        title="Criar moldura delimitadora"
        aria-label="Adicionar moldura manual"
        @click="emit('add-frame')"
      >
        <Icon name="folder" :size="15" />
        <span class="btn-label">Moldura +</span>
      </button>
    </div>

    <!-- Indicador de Seleção Múltipla -->
    <div v-if="hasSelection && selectedCount > 0" class="selection-badge" role="status">
      <span class="badge-text">{{ selectedCount }} selecionado{{ selectedCount > 1 ? 's' : '' }}</span>
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.5rem;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 9999px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  user-select: none;
  z-index: 40;
  max-width: 100%;
  overflow-x: auto;
}

.tool-mode-group,
.quick-action-group,
.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background-color: var(--color-border, #e2e8f0);
  margin: 0 0.15rem;
}

.canvas-tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-width: 38px;
  min-height: 38px;
  padding: 0.35rem 0.5rem;
  background: transparent;
  border: none;
  border-radius: 9999px;
  color: var(--color-text-primary, #1e293b);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.canvas-tool-btn:hover {
  background: var(--color-surface-hover, #f1f5f9);
  color: var(--color-primary, #2563eb);
}

.canvas-tool-btn:focus-visible {
  outline: 2px solid var(--color-primary, #2563eb);
  outline-offset: 2px;
}

.tool-mode-btn.is-active {
  background: color-mix(in srgb, var(--color-primary, #2563eb) 12%, var(--color-surface, #ffffff));
  color: var(--color-primary, #2563eb);
  font-weight: 600;
}

.primary-action-btn {
  background: var(--color-primary, #2563eb);
  color: #ffffff;
}

.primary-action-btn:hover {
  filter: brightness(1.08);
  color: #ffffff;
}

.zoom-indicator {
  min-width: 44px;
  text-align: center;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted, #64748b);
  font-variant-numeric: tabular-nums;
}

.zoom-minus {
  font-size: 1.15rem;
  line-height: 1;
  font-weight: 600;
}

.reset-btn {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted, #64748b);
}

.fit-btn {
  padding: 0.35rem 0.65rem;
}

.btn-label {
  font-size: 0.75rem;
}

.selection-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  background: var(--color-primary-light, #eff6ff);
  border: 1px solid var(--color-primary-border, #bfdbfe);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-primary, #2563eb);
}

.clear-sel-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  padding: 2px;
  cursor: pointer;
  color: var(--color-primary, #2563eb);
  border-radius: 50%;
}

.clear-sel-btn:hover {
  background: rgba(37, 99, 235, 0.15);
}

@media (max-width: 768px) {
  .canvas-tool-btn {
    min-width: 44px;
    min-height: 44px;
  }
  .btn-label {
    display: none;
  }
}
</style>
