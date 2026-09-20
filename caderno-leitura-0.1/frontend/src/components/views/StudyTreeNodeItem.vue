<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, StudyTreeNode } from '../../types.ts'
import Icon from '../ui/Icon.vue'

interface Props {
  node: StudyTreeNode
  bookId: number
  activeStudyId?: number | null
  isExpanded: boolean
  isNodeExpanded?: (id: number) => boolean
  // Flags para drag-and-drop
  isDragging?: boolean
  isDropForbidden?: boolean
  dropPosition?: 'before' | 'inside' | 'after' | null
  activeDraggingId?: number | null
  dropTargetId?: number | null
  isDropForbiddenNode?: (targetId: number) => boolean
}

const props = withDefaults(defineProps<Props>(), {
  activeStudyId: null,
  isDragging: false,
  isDropForbidden: false,
  dropPosition: null,
  activeDraggingId: null,
  dropTargetId: null,
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'toggle-expand', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
  (e: 'move-action', payload: { studyId: number; action: 'promote' | 'demote' | 'up' | 'down' }): void
  (e: 'drag-start', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-over', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-leave', event: DragEvent, node: StudyTreeNode): void
  (e: 'drop', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-end', event: DragEvent): void
}>()

const isMobileMenuOpen = ref(false)

const hasChildren = computed(() => props.node.children && props.node.children.length > 0)
const childCount = computed(() => props.node.children?.length ?? 0)

function formatDate(isoStr: string): string {
  try {
    return new Date(isoStr).toLocaleDateString('pt-BR')
  } catch {
    return isoStr
  }
}

function handleChevronClick(e: MouseEvent) {
  e.stopPropagation()
  emit('toggle-expand', props.node.id)
}

function toggleMobileMenu(e: MouseEvent) {
  e.stopPropagation()
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function triggerMove(action: 'promote' | 'demote' | 'up' | 'down', e: MouseEvent) {
  e.stopPropagation()
  isMobileMenuOpen.value = false
  emit('move-action', { studyId: props.node.id, action })
}
</script>

<template>
  <li
    class="tree-node-item"
    :class="{
      'is-focused': activeStudyId === node.id,
      'is-dragging': isDragging,
      'is-drop-forbidden': isDropForbidden,
      'drop-before': dropPosition === 'before',
      'drop-inside': dropPosition === 'inside',
      'drop-after': dropPosition === 'after',
      'has-children': hasChildren
    }"
    role="treeitem"
    :aria-expanded="hasChildren ? isExpanded : undefined"
    :aria-selected="activeStudyId === node.id"
    :data-study-id="node.id"
    :data-depth="node.depth"
    @dragover.prevent="emit('drag-over', $event, node)"
    @dragleave="emit('drag-leave', $event, node)"
    @drop.prevent="emit('drop', $event, node)"
  >
    <!-- Conector de ramo SVG/CSS -->
    <div class="tree-node-connector" aria-hidden="true"></div>

    <!-- Drop indicator visual superior (irmão antes) -->
    <div v-if="dropPosition === 'before'" class="drop-line drop-line-before" aria-hidden="true"></div>

    <!-- Card principal do nó -->
    <div
      class="tree-node-card"
      :draggable="true"
      @dragstart="emit('drag-start', $event, node)"
      @dragend="emit('drag-end', $event)"
      @click="emit('select-study', node.id)"
    >
      <!-- Indicador de Expansão / Colapso (Chevron) -->
      <button
        v-if="hasChildren"
        type="button"
        class="tree-chevron-btn"
        :title="isExpanded ? 'Recolher sub-estudos' : 'Expandir sub-estudos'"
        :aria-label="isExpanded ? 'Recolher sub-estudos' : 'Expandir sub-estudos'"
        @click="handleChevronClick"
      >
        <Icon :name="isExpanded ? 'chevron-down' : 'chevron-right'" :size="14" />
      </button>
      <div v-else class="tree-chevron-placeholder" aria-hidden="true"></div>

      <!-- Handle de arrasto -->
      <div
        class="tree-drag-handle"
        title="Arrastar para reorganizar ou aninhar"
        aria-hidden="true"
      >
        <Icon name="grip-vertical" :size="14" />
      </div>

      <!-- Informações principais do nó -->
      <div class="node-main-info">
        <div class="node-icon-wrapper">
          <Icon name="book" :size="14" />
        </div>
        <div class="node-text-group">
          <div class="node-title-row">
            <h4 class="node-title">
              <RouterLink
                :to="{ name: 'study', params: { bookId, studyId: node.id } }"
                class="node-title-link"
                @click.stop="emit('select-study', node.id)"
              >
                {{ node.title }}
              </RouterLink>
            </h4>
            <!-- Badge de contagem de filhos (quando recolhido ou como resumo) -->
            <span
              v-if="hasChildren"
              class="child-count-badge"
              :class="{ 'is-collapsed-badge': !isExpanded }"
              :title="`${childCount} sub-estudo(s) subordinado(s)`"
            >
              {{ childCount }}
            </span>
          </div>

          <div class="node-meta-row">
            <span v-if="node.location" class="node-location">
              <Icon name="book-open" :size="11" />
              {{ node.location }}
            </span>
            <span class="node-separator" v-if="node.location">•</span>
            <time :datetime="node.created_at" class="node-date">
              {{ formatDate(node.created_at) }}
            </time>
          </div>
        </div>
      </div>

      <!-- Ações do nó -->
      <div class="node-actions-group">
        <!-- Menu de ações rápidas táteis (mobile e desktop acessível) -->
        <div class="mobile-action-container">
          <button
            type="button"
            class="tree-action-btn mobile-menu-toggle-btn"
            title="Ações de hierarquia e posição"
            aria-label="Ações de hierarquia e posição"
            :aria-expanded="isMobileMenuOpen"
            @click="toggleMobileMenu"
          >
            <Icon name="more-horizontal" :size="16" />
          </button>

          <!-- Dropdown com alvos mínimos de 44x44px -->
          <div v-if="isMobileMenuOpen" class="quick-actions-dropdown" role="menu">
            <button
              type="button"
              class="quick-action-item touch-target"
              role="menuitem"
              title="Mover nó para cima na ordenação"
              @click="triggerMove('up', $event)"
            >
              <Icon name="arrow-up" :size="16" />
              <span>Mover para cima</span>
            </button>
            <button
              type="button"
              class="quick-action-item touch-target"
              role="menuitem"
              title="Mover nó para baixo na ordenação"
              @click="triggerMove('down', $event)"
            >
              <Icon name="arrow-down" :size="16" />
              <span>Mover para baixo</span>
            </button>
            <button
              type="button"
              class="quick-action-item touch-target"
              role="menuitem"
              title="Recuar nó (tornar filho do irmão anterior)"
              @click="triggerMove('demote', $event)"
            >
              <Icon name="corner-down-right" :size="16" />
              <span>Recuar nó (aninhar)</span>
            </button>
            <button
              type="button"
              class="quick-action-item touch-target"
              role="menuitem"
              title="Promover nó (subir um nível hierárquico)"
              @click="triggerMove('promote', $event)"
            >
              <Icon name="corner-up-left" :size="16" />
              <span>Promover nó</span>
            </button>
          </div>
        </div>

        <RouterLink
          :to="{ name: 'study', params: { bookId, studyId: node.id } }"
          class="node-open-link touch-target"
          title="Abrir estudo completo"
        >
          Ler
        </RouterLink>

        <button
          type="button"
          class="tree-action-btn node-trash-btn touch-target"
          title="Mover estudo para a lixeira"
          aria-label="Mover estudo para a lixeira"
          @click.stop="emit('trash-study', node)"
        >
          <Icon name="trash" :size="15" />
        </button>
      </div>
    </div>

    <!-- Drop indicator visual inferior (irmão depois) -->
    <div v-if="dropPosition === 'after'" class="drop-line drop-line-after" aria-hidden="true"></div>

    <!-- Sub-ramos aninhados recursivos -->
    <ul
      v-if="hasChildren"
      v-show="isExpanded"
      class="tree-subbranch"
      role="group"
      :aria-label="`Sub-estudos de ${node.title}`"
    >
      <StudyTreeNodeItem
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :book-id="bookId"
        :active-study-id="activeStudyId"
        :is-expanded="isNodeExpanded ? isNodeExpanded(child.id) : true"
        :is-node-expanded="isNodeExpanded"
        :is-dragging="activeDraggingId === child.id"
        :drop-position="dropTargetId === child.id ? dropPosition : null"
        :is-drop-forbidden="isDropForbiddenNode ? isDropForbiddenNode(child.id) : false"
        :active-dragging-id="activeDraggingId"
        :drop-target-id="dropTargetId"
        :is-drop-forbidden-node="isDropForbiddenNode"
        @select-study="emit('select-study', $event)"
        @toggle-expand="emit('toggle-expand', $event)"
        @trash-study="emit('trash-study', $event)"
        @move-action="emit('move-action', $event)"
        @drag-start="(ev, n) => emit('drag-start', ev, n)"
        @drag-over="(ev, n) => emit('drag-over', ev, n)"
        @drag-leave="(ev, n) => emit('drag-leave', ev, n)"
        @drop="(ev, n) => emit('drop', ev, n)"
        @drag-end="ev => emit('drag-end', ev)"
      />
    </ul>
  </li>
</template>

<style scoped>
.tree-node-item {
  position: relative;
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
  transition: transform 0.15s ease;
}

.tree-node-connector {
  position: absolute;
  left: -1rem;
  top: 1.4rem;
  width: 0.9rem;
  height: 2px;
  background-color: var(--color-border, #e2e8f0);
}

.tree-node-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.85rem;
  background-color: var(--color-surface-elevated, #fafafa);
  border: 1px solid var(--color-border-divider, #f1f5f9);
  border-radius: var(--radius-control, 6px);
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}

.tree-node-card:hover {
  border-color: var(--color-border-hover, #cbd5e1);
  background-color: var(--color-surface-hover, #f8fafc);
}

.tree-node-item.is-focused > .tree-node-card {
  border-color: var(--color-accent);
  background-color: color-mix(in srgb, var(--color-accent) 6%, var(--color-surface));
  box-shadow: 0 0 0 1px var(--color-accent);
}

/* Indicadores de Drag and Drop */
.tree-node-item.is-dragging > .tree-node-card {
  opacity: 0.4;
  border-style: dashed;
}

.tree-node-item.is-drop-forbidden > .tree-node-card {
  cursor: not-allowed;
  border-color: var(--color-danger, #ef4444);
  background-color: color-mix(in srgb, var(--color-danger) 5%, var(--color-surface));
}

.tree-node-item.drop-inside > .tree-node-card {
  border-color: var(--color-accent, #3b82f6);
  border-style: dashed;
  background-color: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  box-shadow: 0 0 0 2px var(--color-accent, #3b82f6);
}

.drop-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--color-accent, #3b82f6);
  border-radius: 999px;
  z-index: 10;
}

.drop-line-before {
  top: -4px;
}

.drop-line-after {
  bottom: -4px;
}

.tree-chevron-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: var(--color-muted, #64748b);
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.tree-chevron-btn:hover {
  background-color: var(--color-surface-hover, #e2e8f0);
  color: var(--color-inverse-bg, #0f172a);
}

.tree-chevron-placeholder {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.tree-drag-handle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 24px;
  cursor: grab;
  color: var(--color-border-hover, #94a3b8);
  flex-shrink: 0;
}

.tree-drag-handle:active {
  cursor: grabbing;
}

.node-main-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
  flex: 1;
}

.node-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 5px;
  background-color: color-mix(in srgb, var(--color-accent) 10%, var(--color-surface));
  color: var(--color-accent);
  flex-shrink: 0;
}

.node-text-group {
  min-width: 0;
  flex: 1;
}

.node-title-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.node-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-title-link {
  color: var(--color-inverse-bg, #0f172a);
  text-decoration: none;
}

.node-title-link:hover {
  color: var(--color-accent);
}

.child-count-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.05rem 0.4rem;
  border-radius: 999px;
  background-color: var(--color-surface-hover, #e2e8f0);
  color: var(--color-muted, #475569);
  flex-shrink: 0;
}

.child-count-badge.is-collapsed-badge {
  background-color: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  color: var(--color-accent);
}

.node-meta-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.15rem;
  font-size: 0.75rem;
  color: var(--color-muted, #64748b);
}

.node-location {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.node-separator {
  color: var(--color-border);
}

.node-date {
  font-variant-numeric: tabular-nums;
}

.node-actions-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}

.mobile-action-container {
  position: relative;
}

.tree-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-control, 4px);
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.tree-action-btn:hover {
  background-color: var(--color-surface-hover);
  border-color: var(--color-border);
  color: var(--color-inverse-bg);
}

.quick-actions-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 4px;
  min-width: 200px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  z-index: 50;
  display: flex;
  flex-direction: column;
  padding: 0.35rem 0;
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.5rem 0.85rem;
  background: transparent;
  border: none;
  font-size: 0.82rem;
  text-align: left;
  color: var(--color-inverse-bg);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.quick-action-item:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
  color: var(--color-accent);
}

.node-open-link {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.3rem 0.6rem;
  border-radius: var(--radius-control, 4px);
  background: color-mix(in srgb, var(--color-accent) 10%, var(--color-surface));
  color: var(--color-accent);
  text-decoration: none;
  transition: background-color 0.15s ease;
}

.node-open-link:hover {
  background: color-mix(in srgb, var(--color-accent) 18%, var(--color-surface));
}

.node-trash-btn:hover {
  color: var(--color-danger, #b91c1c);
}

.tree-subbranch {
  list-style: none;
  margin: 0.5rem 0 0 1.25rem;
  padding: 0 0 0 1rem;
  border-left: 2px solid var(--color-border, #e2e8f0);
  display: flex;
  flex-direction: column;
}

/* Ergonomia móvel: alvos mínimos de 44x44px */
@media (max-width: 768px) {
  .touch-target,
  .mobile-menu-toggle-btn {
    min-width: 44px;
    min-height: 44px;
  }
  .quick-action-item {
    min-height: 44px;
  }
  .tree-drag-handle {
    display: none; /* Em telas de toque, a reorganização prioritária é pelo menu de ações rápidas */
  }
  .node-open-link {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tree-node-card,
  .tree-node-item,
  .tree-chevron-btn,
  .tree-action-btn {
    transition: none !important;
  }
}
</style>
