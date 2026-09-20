<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, CanvasPositionedCard } from '../../../types'
import Icon from '../../ui/Icon.vue'
import { useSuperclassPhysics } from '../../../composables/useSuperclassPhysics'

interface Props {
  study: StudySummary
  node: CanvasPositionedCard
  bookId: number
  isSelected?: boolean
  isFocused?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isFocused: false,
})

const emit = defineEmits<{
  (e: 'select', studyId: number, isMulti: boolean): void
  (e: 'drag-start', studyId: number, screenX: number, screenY: number): void
  (e: 'move-keyboard', studyId: number, deltaX: number, deltaY: number): void
  (e: 'trash', study: StudySummary): void
}>()

const nodeElementRef = ref<HTMLElement | null>(null)
const physics = useSuperclassPhysics()

function formatDate(isoStr: string): string {
  try {
    return new Date(isoStr).toLocaleDateString('pt-BR')
  } catch {
    return isoStr
  }
}

function handleKeyDown(e: KeyboardEvent): void {
  if (e.key === 'Enter') {
    physics.triggerHapticPulse(nodeElementRef.value, 'step')
    emit('select', props.study.id, false)
    return
  }

  if (e.shiftKey) {
    const step = e.ctrlKey || e.metaKey ? 50 : 20
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      physics.triggerHapticPulse(nodeElementRef.value, 'step')
      emit('move-keyboard', props.study.id, 0, -step)
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      physics.triggerHapticPulse(nodeElementRef.value, 'step')
      emit('move-keyboard', props.study.id, 0, step)
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      physics.triggerHapticPulse(nodeElementRef.value, 'step')
      emit('move-keyboard', props.study.id, -step, 0)
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      physics.triggerHapticPulse(nodeElementRef.value, 'step')
      emit('move-keyboard', props.study.id, step, 0)
    }
  }
}

function handlePointerDown(e: PointerEvent): void {
  // Apenas botão principal (esquerdo) para arrasto
  if (e.button !== 0) return

  const target = e.target as HTMLElement
  // Não inicia arrasto se clicar em links ou botões de ação
  if (target.closest('a') || target.closest('button')) return

  physics.triggerHapticPulse(nodeElementRef.value, 'step')
  const isMulti = e.ctrlKey || e.metaKey || e.shiftKey
  emit('select', props.study.id, isMulti)
  emit('drag-start', props.study.id, e.clientX, e.clientY)
}

const cardStyle = computed(() => {
  return {
    transform: `translate3d(${props.node.x}px, ${props.node.y}px, 0)`,
    width: `${props.node.width ?? 280}px`,
    zIndex: props.node.z_index,
  }
})
</script>

<template>
  <article
    ref="nodeElementRef"
    class="canvas-node"
    :class="{
      'is-selected': isSelected,
      'is-focused': isFocused,
      [`tag-${node.color_tag}`]: !!node.color_tag,
    }"
    :style="cardStyle"
    role="button"
    :aria-selected="isSelected"
    tabindex="0"
    @pointerdown="handlePointerDown"
    @click.stop="emit('select', study.id, $event.ctrlKey || $event.metaKey)"
    @keydown="handleKeyDown"
  >
    <!-- Cabeçalho do Card com Drag Handle -->
    <div class="node-header">
      <div class="drag-handle" title="Arrastar card" aria-hidden="true">
        <Icon name="grip-vertical" :size="14" />
      </div>

      <span class="node-badge" v-if="node.color_tag">
        {{ node.color_tag }}
      </span>
      <span class="node-badge default" v-else>
        Estudo
      </span>

      <time :datetime="study.created_at" class="node-date">
        {{ formatDate(study.created_at) }}
      </time>
    </div>

    <!-- Título do Estudo -->
    <h4 class="node-title">
      <RouterLink
        :to="{ name: 'study', params: { bookId, studyId: study.id } }"
        class="node-title-link"
        @click.stop="emit('select', study.id, false)"
      >
        {{ study.title }}
      </RouterLink>
    </h4>

    <!-- Localização no Texto -->
    <p v-if="study.location" class="node-location">
      <Icon name="book-open" :size="12" />
      <span>{{ study.location }}</span>
    </p>

    <!-- Barra Inferior de Ações -->
    <div class="node-footer">
      <RouterLink
        :to="{ name: 'study', params: { bookId, studyId: study.id } }"
        class="node-action-read"
        @click.stop
      >
        Abrir estudo →
      </RouterLink>

      <button
        type="button"
        class="node-action-trash"
        title="Mover estudo para a lixeira"
        aria-label="Mover estudo para a lixeira"
        @click.stop="emit('trash', study)"
      >
        <Icon name="trash" :size="13" />
      </button>
    </div>
  </article>
</template>

<style scoped>
.canvas-node {
  position: absolute;
  top: 0;
  left: 0;
  min-height: 160px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-card, 8px);
  padding: 0.85rem 1rem 0.65rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
  user-select: none;
  cursor: grab;
  touch-action: none;
}

.canvas-node:active {
  cursor: grabbing;
}

.canvas-node:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.09);
  border-color: var(--color-primary-border, #93c5fd);
}

.canvas-node.is-selected {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25), 0 8px 24px rgba(37, 99, 235, 0.12);
}

.canvas-node.is-focused {
  outline: 2px solid var(--color-primary, #2563eb);
  outline-offset: 2px;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.45rem;
}

.drag-handle {
  display: flex;
  align-items: center;
  color: var(--color-text-muted, #94a3b8);
  cursor: grab;
}

.node-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: var(--color-primary-light, #eff6ff);
  color: var(--color-primary, #2563eb);
}

.node-badge.default {
  background: var(--color-surface-hover, #f1f5f9);
  color: var(--color-text-muted, #64748b);
}

.node-date {
  margin-left: auto;
  font-size: 0.6875rem;
  color: var(--color-text-muted, #94a3b8);
}

.node-title {
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.35;
  margin: 0 0 0.35rem 0;
}

.node-title-link {
  color: var(--color-text-primary, #0f172a);
  text-decoration: none;
}

.node-title-link:hover {
  color: var(--color-primary, #2563eb);
}

.node-location {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--color-text-muted, #64748b);
  margin: 0 0 0.6rem 0;
}

.node-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 0.45rem;
  border-top: 1px dashed var(--color-border-divider, #f1f5f9);
}

.node-action-read {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-primary, #2563eb);
  text-decoration: none;
}

.node-action-read:hover {
  text-decoration: underline;
}

.node-action-trash {
  background: transparent;
  border: none;
  color: var(--color-text-muted, #94a3b8);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.node-action-trash:hover {
  color: var(--color-danger, #ef4444);
  background: rgba(239, 68, 68, 0.1);
}

@media (max-width: 768px) {
  .node-action-trash {
    min-width: 44px;
    min-height: 44px;
    justify-content: center;
  }
}
</style>
