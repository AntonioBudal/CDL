# Contracts: Contratos de Hierarquia e Componentes da Tree View

**Feature**: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos  
**Status**: Completed  
**Artifact**: `contracts/study-tree-hierarchy.md`  

---

## 1. Contrato do Composable `useStudyHierarchy`

### 1.1 Assinatura e Retorno

```typescript
export interface UseStudyHierarchyReturn {
  treeRoots: ComputedRef<StudyTreeNode[]>
  treeMap: ComputedRef<Map<number, StudyTreeNode>>
  isNodeExpanded: (id: number) => boolean
  toggleNode: (id: number) => void
  expandAll: () => void
  collapseAll: () => void
  canNestUnder: (sourceId: number, targetId: number) => boolean
  collapsedNodeIds: Ref<Set<number>>
}
```

### 1.2 Regras de Persistência e Abertura

- Se não houver dados em `localStorage.getItem('caderno_tree_collapsed_${bookId}')`:
  - `collapsedNodeIds` é inicializado como `new Set<number>()` (todos os nós com filhos iniciam expandidos).
- `expandAll()`:
  - `collapsedNodeIds.value.clear()`
  - Persiste lista vazia `[]`.
- `collapseAll()`:
  - Adiciona todos os IDs de nós que possuem filhos ao conjunto `collapsedNodeIds`.
  - Persiste a lista completa de IDs colapsados.

---

## 2. Contrato do Componente `StudyTreeNodeItem.vue`

### 2.1 Props

```typescript
interface Props {
  node: StudyTreeNode
  bookId: number
  activeStudyId?: number | null
  isExpanded: boolean
  isNodeExpanded?: (id: number) => boolean
  isDragging?: boolean
  isDropForbidden?: boolean
  dropPosition?: 'before' | 'inside' | 'after' | null
  activeDraggingId?: number | null
  dropTargetId?: number | null
  isDropForbiddenNode?: (targetId: number) => boolean
}
```

### 2.2 Emits

```typescript
interface Emits {
  (e: 'select-study', studyId: number): void
  (e: 'toggle-expand', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
  (e: 'move-action', payload: { studyId: number; action: 'promote' | 'demote' | 'up' | 'down' }): void
  (e: 'drag-start', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-over', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-leave', event: DragEvent, node: StudyTreeNode): void
  (e: 'drop', event: DragEvent, node: StudyTreeNode): void
  (e: 'drag-end', event: DragEvent): void
}
```

### 2.3 Estrutura Visual do Micro-Badge de Progresso do Ramo

Quando `node.progress` existir (`node.children.length > 0`):
```html
<span
  class="branch-progress-badge"
  :title="`Ramo: ${node.progress.completed} de ${node.progress.total} estudos concluídos (${node.progress.percent}%)`"
  role="status"
  aria-label="Progresso do ramo"
>
  <span class="progress-fraction">{{ node.progress.label }}</span>
  <span class="progress-bar-track">
    <span class="progress-bar-fill" :style="{ width: `${node.progress.percent}%` }"></span>
  </span>
</span>
```

---

## 3. Contrato do Componente `StudyTreeView.vue`

### 3.1 Props e Emits

```typescript
interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  activeStudyId?: number | null
  loading?: boolean
}

interface Emits {
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
  (e: 'studies-updated', updatedStudies?: StudySummary[]): void
}
```

### 3.2 Acessibilidade WAI-ARIA Treeview

- Árvore: `<ul class="tree-branch" role="tree" tabindex="0" aria-label="Estrutura de Estudos">`
- Itens: `<li class="tree-node-item" role="treeitem" :aria-expanded="hasChildren ? isExpanded : undefined" :aria-selected="activeStudyId === node.id" :aria-level="node.depth + 1">`
- Alvos táteis: botões de chevron e ações táteis com dimensões mínimas de 44×44px.
