<script setup lang="ts">
import { computed, ref, toRef } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudySummary, StudyTreeNode } from '../../types.ts'
import Icon from '../ui/Icon.vue'
import EmptyState from '../ui/EmptyState.vue'
import StudyTreeNodeItem from './StudyTreeNodeItem.vue'
import { useStudyHierarchy } from '../../composables/useStudyHierarchy.ts'
import { useSuperclassPhysics } from '../../composables/useSuperclassPhysics.ts'

interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  activeStudyId?: number | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  chapterId: null,
  activeStudyId: null,
  loading: false,
})

const emit = defineEmits<{
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
  (e: 'studies-updated', updatedStudies?: StudySummary[]): void
}>()

const studiesRef = toRef(props, 'studies')
const chapterIdRef = toRef(props, 'chapterId')

const {
  treeRoots,
  treeMap,
  isNodeExpanded,
  toggleNode,
  expandAll,
  collapseAll,
  canNestUnder,
} = useStudyHierarchy(studiesRef, chapterIdRef)

const physics = useSuperclassPhysics()

// Estado local de Drag and Drop
const activeDraggingNode = ref<StudyTreeNode | null>(null)
const dropTargetNode = ref<StudyTreeNode | null>(null)
const dropPosition = ref<'before' | 'inside' | 'after' | null>(null)
const errorMessage = ref<string | null>(null)
const isMoving = ref(false)

// Raiz global colapsável
const isTreeRootExpanded = ref(true)
function toggleRoot(): void {
  isTreeRootExpanded.value = !isTreeRootExpanded.value
}

// Verifica se soltar em determinado nó é proibido (evita loops)
function isDropForbidden(targetId: number): boolean {
  if (!activeDraggingNode.value) return false
  return !canNestUnder(activeDraggingNode.value.id, targetId)
}

// Handlers de Drag and Drop HTML5 nativo
function handleDragStart(event: DragEvent, node: StudyTreeNode) {
  activeDraggingNode.value = node
  errorMessage.value = null
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(node.id))
  }
}

function handleDragOver(event: DragEvent, node: StudyTreeNode) {
  if (!activeDraggingNode.value) return
  if (activeDraggingNode.value.id === node.id) {
    dropTargetNode.value = null
    dropPosition.value = null
    return
  }

  const targetEl = (event.currentTarget as HTMLElement).querySelector('.tree-node-card') as HTMLElement
  if (!targetEl) return

  const rect = targetEl.getBoundingClientRect()
  const offsetY = event.clientY - rect.top
  const height = rect.height

  // Zonas: 25% superior (before), 50% centro (inside), 25% inferior (after)
  if (offsetY < height * 0.25) {
    dropPosition.value = 'before'
    dropTargetNode.value = node
  } else if (offsetY > height * 0.75) {
    dropPosition.value = 'after'
    dropTargetNode.value = node
  } else {
    // Inside: verificar se ciclo impede aninhamento
    if (canNestUnder(activeDraggingNode.value.id, node.id)) {
      dropPosition.value = 'inside'
      dropTargetNode.value = node
    } else {
      dropPosition.value = null
      dropTargetNode.value = null
    }
  }
}

function handleDragLeave(_event: DragEvent, node: StudyTreeNode) {
  if (dropTargetNode.value?.id === node.id) {
    dropTargetNode.value = null
    dropPosition.value = null
  }
}

function handleDragEnd() {
  activeDraggingNode.value = null
  dropTargetNode.value = null
  dropPosition.value = null
}

async function handleDrop(event: DragEvent, targetNode: StudyTreeNode) {
  const source = activeDraggingNode.value
  const position = dropPosition.value

  handleDragEnd()

  if (!source || !position) return
  if (source.id === targetNode.id) return

  let newParentId: number | null = null
  let targetPosition = 0

  if (position === 'inside') {
    newParentId = targetNode.id
    targetPosition = targetNode.children.length
  } else if (position === 'before') {
    newParentId = targetNode.parent_study_id
    targetPosition = Math.max(0, targetNode.position)
  } else if (position === 'after') {
    newParentId = targetNode.parent_study_id
    targetPosition = targetNode.position + 1
  }

  if (event.currentTarget) {
    physics.triggerHapticPulse(event.currentTarget as HTMLElement, 'snap')
  }

  await executeMove(source.id, newParentId, targetPosition)
}

// Handler para o menu tátil móvel (Promover, Recuar, Subir, Descer)
async function handleMoveAction(payload: { studyId: number; action: 'promote' | 'demote' | 'up' | 'down' }) {
  const node = treeMap.value.get(payload.studyId)
  if (!node) return

  errorMessage.value = null
  physics.triggerHapticPulse(document.activeElement as HTMLElement, 'step')

  if (payload.action === 'promote') {
    // Subir um nível hierárquico (tornar-se irmão do pai)
    if (node.parent_study_id === null) {
      errorMessage.value = 'O estudo já está no nível raiz.'
      return
    }
    const parentNode = treeMap.value.get(node.parent_study_id)
    const newParentId = parentNode ? parentNode.parent_study_id : null
    const targetPos = parentNode ? parentNode.position + 1 : 0
    await executeMove(node.id, newParentId, targetPos)
  } else if (payload.action === 'demote') {
    // Tornar-se filho do irmão anterior
    const parentId = node.parent_study_id
    const siblings = Array.from(treeMap.value.values()).filter(
      (s) => s.parent_study_id === parentId && s.id !== node.id
    ).sort((a, b) => a.position - b.position)

    const prevSibling = siblings.filter((s) => s.position < node.position).pop()
    if (!prevSibling) {
      errorMessage.value = 'Não há irmão anterior para aninhar este estudo.'
      return
    }
    if (!canNestUnder(node.id, prevSibling.id)) {
      errorMessage.value = 'Não é possível aninhar: limite de profundidade (5 níveis) atingido.'
      return
    }
    await executeMove(node.id, prevSibling.id, prevSibling.children.length)
  } else if (payload.action === 'up') {
    // Mover para cima entre irmãos
    if (node.position <= 0) {
      errorMessage.value = 'O estudo já está na primeira posição.'
      return
    }
    await executeMove(node.id, node.parent_study_id, node.position - 1)
  } else if (payload.action === 'down') {
    // Mover para baixo entre irmãos
    await executeMove(node.id, node.parent_study_id, node.position + 1)
  }
}

// Chamada à API backend
async function executeMove(studyId: number, newParentId: number | null, targetPosition: number) {
  isMoving.value = true
  errorMessage.value = null

  const node = treeMap.value.get(studyId)
  const expectedUpdatedAt = node?.updated_at ?? null

  try {
    const res = await fetch(`/api/studies/${studyId}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        parent_study_id: newParentId,
        target_position: targetPosition,
        expected_updated_at: expectedUpdatedAt,
      }),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      if (res.status === 409) {
        errorMessage.value = 'Conflito de edição: o estudo foi alterado por outro dispositivo. Recarregando...'
        emit('studies-updated')
        return
      }
      errorMessage.value = data.detail || 'Não foi possível mover o estudo.'
      return
    }

    const updatedList: StudySummary[] = await res.json()
    // Notifica o componente pai para atualizar os dados
    emit('studies-updated', updatedList)
  } catch (err) {
    console.error('[StudyTreeView] Erro ao mover estudo:', err)
    errorMessage.value = 'Erro de conexão ao salvar hierarquia.'
  } finally {
    isMoving.value = false
  }
}

// Lista linear de nós visíveis para navegação por teclado WAI-ARIA
const visibleNodes = computed<StudyTreeNode[]>(() => {
  const list: StudyTreeNode[] = []
  function traverse(nodes: StudyTreeNode[]) {
    for (const n of nodes) {
      list.push(n)
      if (n.children.length > 0 && isNodeExpanded(n.id)) {
        traverse(n.children)
      }
    }
  }
  traverse(treeRoots.value)
  return list
})

function handleTreeKeydown(event: KeyboardEvent) {
  const visible = visibleNodes.value
  if (visible.length === 0) return

  const currentActiveId = props.activeStudyId ?? visible[0]?.id
  const currentIndex = visible.findIndex((n) => n.id === currentActiveId)
  const currentNode = currentIndex >= 0 ? visible[currentIndex] : null

  // Atalhos acessíveis de reordenação estrutural com Alt
  if (event.altKey && currentNode) {
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      handleMoveAction({ studyId: currentNode.id, action: 'up' })
      return
    }
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      handleMoveAction({ studyId: currentNode.id, action: 'down' })
      return
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault()
      handleMoveAction({ studyId: currentNode.id, action: 'demote' })
      return
    }
    if (event.key === 'ArrowLeft') {
      event.preventDefault()
      handleMoveAction({ studyId: currentNode.id, action: 'promote' })
      return
    }
  }

  // Navegação direcional padrão WAI-ARIA Treeview
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    const nextIdx = Math.min(visible.length - 1, (currentIndex >= 0 ? currentIndex : -1) + 1)
    emit('select-study', visible[nextIdx].id)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    const prevIdx = Math.max(0, (currentIndex >= 0 ? currentIndex : 1) - 1)
    emit('select-study', visible[prevIdx].id)
  } else if (event.key === 'ArrowRight') {
    event.preventDefault()
    if (currentNode && currentNode.children.length > 0) {
      if (!isNodeExpanded(currentNode.id)) {
        toggleNode(currentNode.id)
      } else {
        emit('select-study', currentNode.children[0].id)
      }
    }
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault()
    if (currentNode) {
      if (currentNode.children.length > 0 && isNodeExpanded(currentNode.id)) {
        toggleNode(currentNode.id)
      } else if (currentNode.parent_study_id !== null) {
        emit('select-study', currentNode.parent_study_id)
      }
    }
  } else if (event.key === 'Enter' || event.key === ' ') {
    if (currentNode) {
      event.preventDefault()
      emit('select-study', currentNode.id)
    }
  }
}
</script>

<template>
  <div class="study-tree-view" role="region" aria-label="Visualização em Árvore dos Estudos">
    <EmptyState
      v-if="studies.length === 0 && !loading"
      icon="book-open"
      title="Nenhum estudo neste capítulo"
      description="Importe o texto-base de um fichamento para registrar reflexões e análises sobre este trecho da leitura."
      heading-level="h3"
    >
      <RouterLink
        v-if="chapterId"
        class="button primary"
        :to="{ name: 'import', query: { book: bookId, chapter: chapterId } }"
      >
        Importar estudo
      </RouterLink>
    </EmptyState>

    <div v-else class="tree-container">
      <!-- Barra de Ferramentas da Árvore -->
      <div class="tree-toolbar-row">
        <div class="tree-root-node">
          <button
            type="button"
            class="tree-toggle-btn"
            :aria-expanded="isTreeRootExpanded"
            @click="toggleRoot"
            title="Expandir ou recolher árvore inteira"
          >
            <Icon :name="isTreeRootExpanded ? 'chevron-down' : 'chevron-right'" :size="16" />
            <span class="tree-root-label">
              <Icon name="folder" :size="16" class="root-folder-icon" />
              <span>Estrutura de Estudos</span>
              <span class="tree-count-badge">{{ studies.length }}</span>
            </span>
          </button>
        </div>

        <div class="tree-tools-actions">
          <button
            type="button"
            class="tree-action-text-btn"
            title="Expandir todos os ramos"
            @click="expandAll"
          >
            <Icon name="maximize-2" :size="13" />
            <span>Expandir</span>
          </button>
          <button
            type="button"
            class="tree-action-text-btn"
            title="Recolher todos os ramos"
            @click="collapseAll"
          >
            <Icon name="minimize-2" :size="13" />
            <span>Recolher</span>
          </button>
        </div>
      </div>

      <!-- Alerta de erro ou conflito -->
      <div v-if="errorMessage" class="tree-error-banner" role="alert">
        <Icon name="alert-triangle" :size="16" />
        <span>{{ errorMessage }}</span>
        <button type="button" class="close-error-btn" @click="errorMessage = null" title="Fechar">
          ×
        </button>
      </div>

      <!-- Ramos com os Estudos Raízes e Sub-ramos Recursivos (acessível via teclado) -->
      <ul
        v-show="isTreeRootExpanded"
        class="tree-branch"
        role="tree"
        tabindex="0"
        aria-label="Estrutura de estudos em árvore"
        @keydown="handleTreeKeydown"
      >
        <StudyTreeNodeItem
          v-for="rootNode in treeRoots"
          :key="rootNode.id"
          :node="rootNode"
          :book-id="bookId"
          :active-study-id="activeStudyId"
          :is-expanded="isNodeExpanded(rootNode.id)"
          :is-node-expanded="isNodeExpanded"
          :active-dragging-id="activeDraggingNode?.id"
          :drop-target-id="dropTargetNode?.id"
          :drop-position="dropTargetNode?.id === rootNode.id ? dropPosition : null"
          :is-drop-forbidden="isDropForbidden(rootNode.id)"
          :is-drop-forbidden-node="isDropForbidden"
          @select-study="emit('select-study', $event)"
          @toggle-expand="toggleNode($event)"
          @trash-study="emit('trash-study', $event)"
          @move-action="handleMoveAction"
          @drag-start="handleDragStart"
          @drag-over="handleDragOver"
          @drag-leave="handleDragLeave"
          @drop="handleDrop"
          @drag-end="handleDragEnd"
        />
      </ul>
    </div>
  </div>
</template>

<style scoped>
.study-tree-view {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.tree-container {
  background: var(--color-surface, #ffffff);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.tree-toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tree-root-node {
  margin-bottom: 0;
}

.tree-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-inverse-bg, #0f172a);
  cursor: pointer;
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius-control, 6px);
  transition: background-color 0.15s ease, color 0.15s ease;
}

.tree-toggle-btn:hover {
  background-color: var(--color-surface-hover, #f1f5f9);
  color: var(--color-accent);
}

.tree-root-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.root-folder-icon {
  color: var(--color-accent);
}

.tree-count-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background-color: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  color: var(--color-accent);
}

.tree-tools-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.tree-action-text-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.tree-action-text-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background-color: var(--color-surface-hover);
}

.tree-error-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.85rem;
  margin-bottom: 0.75rem;
  background-color: color-mix(in srgb, var(--color-danger, #ef4444) 12%, var(--color-surface));
  border: 1px solid var(--color-danger, #ef4444);
  border-radius: 6px;
  color: var(--color-danger, #b91c1c);
  font-size: 0.85rem;
}

.close-error-btn {
  margin-left: auto;
  background: transparent;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: inherit;
}

.tree-branch {
  list-style: none;
  margin: 0 0 0 1rem;
  padding: 0 0 0 0.75rem;
  border-left: 2px solid var(--color-border, #e2e8f0);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .tree-container {
    padding: 0.85rem;
  }
  .tree-branch {
    margin-left: 0.5rem;
    padding-left: 0.5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tree-toggle-btn,
  .tree-action-text-btn {
    transition: none !important;
  }
}
</style>
