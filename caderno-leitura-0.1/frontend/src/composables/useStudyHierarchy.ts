import { computed, ref, watch, type Ref } from 'vue'
import type { StudySummary, StudyTreeNode } from '../types.ts'

export const MAX_TREE_DEPTH = 5 // Níveis de 0 a 4

function getStorage(): Storage | null {
  if (typeof window !== 'undefined' && window.localStorage) {
    return window.localStorage
  }
  if (typeof localStorage !== 'undefined') {
    return localStorage
  }
  return null
}

export function buildStudyTree(studies: StudySummary[]): StudyTreeNode[] {
  if (!studies || studies.length === 0) return []

  const nodeMap = new Map<number, StudyTreeNode>()
  
  // 1. Cria objetos TreeNode para todos os estudos
  for (const s of studies) {
    nodeMap.set(s.id, {
      ...s,
      parent_study_id: s.parent_study_id ?? null,
      position: s.position ?? 0,
      depth: 0,
      children: [],
    })
  }

  const roots: StudyTreeNode[] = []

  // 2. Conecta filhos aos pais
  for (const s of studies) {
    const node = nodeMap.get(s.id)!
    const parentId = node.parent_study_id

    if (parentId !== null && nodeMap.has(parentId) && parentId !== node.id) {
      const parentNode = nodeMap.get(parentId)!
      parentNode.children.push(node)
    } else {
      roots.push(node)
    }
  }

  // 3. Ordena irmãos por position e id, e calcula depth recursivamente
  function sortAndSetDepth(nodes: StudyTreeNode[], depth: number) {
    nodes.sort((a, b) => {
      if (a.position !== b.position) {
        return a.position - b.position
      }
      return a.id - b.id
    })

    for (const n of nodes) {
      n.depth = depth
      if (n.children.length > 0) {
        sortAndSetDepth(n.children, depth + 1)
      }
    }
  }

  sortAndSetDepth(roots, 0)
  return roots
}

export function collectDescendantIds(nodeId: number, nodeMap: Map<number, StudyTreeNode>): number[] {
  const node = nodeMap.get(nodeId)
  if (!node || node.children.length === 0) return []

  const result: number[] = []
  const queue = [...node.children]

  while (queue.length > 0) {
    const curr = queue.shift()!
    result.push(curr.id)
    if (curr.children.length > 0) {
      queue.push(...curr.children)
    }
  }

  return result
}

export function getSubtreeHeight(node: StudyTreeNode): number {
  if (!node.children || node.children.length === 0) return 0
  return 1 + Math.max(...node.children.map(getSubtreeHeight))
}

export function getNodeDepth(nodeId: number, nodeMap: Map<number, StudyTreeNode>): number {
  let depth = 0
  let curr = nodeMap.get(nodeId)
  const visited = new Set<number>()

  while (curr && curr.parent_study_id !== null && nodeMap.has(curr.parent_study_id)) {
    if (visited.has(curr.id)) break
    visited.add(curr.id)
    depth++
    curr = nodeMap.get(curr.parent_study_id)
  }

  return depth
}

export function useStudyHierarchy(
  studiesRef: Ref<StudySummary[]>,
  chapterIdRef?: Ref<number | null | undefined>
) {
  const expandedNodeIds = ref<Set<number>>(new Set())
  const storageKey = computed(() => {
    const chId = chapterIdRef?.value
    return chId ? `caderno_tree_expanded_ch_${chId}` : null
  })

  // Carrega nós expandidos do localStorage
  function loadExpandedState() {
    const key = storageKey.value
    if (!key) return
    const storage = getStorage()
    if (!storage) return
    try {
      const raw = storage.getItem(key)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) {
          expandedNodeIds.value = new Set(parsed.map(Number))
          return
        }
      }
    } catch (e) {
      console.warn('[useStudyHierarchy] Falha ao ler nós expandidos:', e)
    }
    // Default: nós com filhos começam expandidos
    const defaults = new Set<number>()
    for (const s of studiesRef.value) {
      if (s.parent_study_id !== null && s.parent_study_id !== undefined) {
        defaults.add(s.parent_study_id)
      }
    }
    expandedNodeIds.value = defaults
  }

  function saveExpandedState() {
    const key = storageKey.value
    if (!key) return
    const storage = getStorage()
    if (!storage) return
    try {
      storage.setItem(key, JSON.stringify(Array.from(expandedNodeIds.value)))
    } catch (e) {
      console.warn('[useStudyHierarchy] Falha ao salvar nós expandidos:', e)
    }
  }

  // Árvore computada
  const treeRoots = computed<StudyTreeNode[]>(() => {
    return buildStudyTree(studiesRef.value)
  })

  // Mapa plano id -> TreeNode para lookups O(1)
  const treeMap = computed<Map<number, StudyTreeNode>>(() => {
    const map = new Map<number, StudyTreeNode>()
    function fill(nodes: StudyTreeNode[]) {
      for (const n of nodes) {
        map.set(n.id, n)
        if (n.children.length > 0) {
          fill(n.children)
        }
      }
    }
    fill(treeRoots.value)
    return map
  })

  // Inicializa e observa mudanças de capítulo
  watch(
    () => storageKey.value,
    () => {
      loadExpandedState()
    },
    { immediate: true }
  )

  function toggleNode(nodeId: number) {
    if (expandedNodeIds.value.has(nodeId)) {
      expandedNodeIds.value.delete(nodeId)
    } else {
      expandedNodeIds.value.add(nodeId)
    }
    // Cria nova referência para reatividade do Set
    expandedNodeIds.value = new Set(expandedNodeIds.value)
    saveExpandedState()
  }

  function expandAll() {
    const allParentIds = new Set<number>()
    for (const [id, node] of treeMap.value.entries()) {
      if (node.children.length > 0) {
        allParentIds.add(id)
      }
    }
    expandedNodeIds.value = allParentIds
    saveExpandedState()
  }

  function collapseAll() {
    expandedNodeIds.value = new Set()
    saveExpandedState()
  }

  function isNodeExpanded(nodeId: number): boolean {
    return expandedNodeIds.value.has(nodeId)
  }

  function canNestUnder(sourceId: number, targetId: number | null): boolean {
    if (targetId === null) {
      // Mover para raiz: altura da subárvore não pode estourar o limite
      const sourceNode = treeMap.value.get(sourceId)
      if (!sourceNode) return false
      return getSubtreeHeight(sourceNode) < MAX_TREE_DEPTH
    }

    if (sourceId === targetId) return false

    const sourceNode = treeMap.value.get(sourceId)
    const targetNode = treeMap.value.get(targetId)
    if (!sourceNode || !targetNode) return false

    // Prevenção de ciclo DAG: target não pode ser descendente de source
    const descendants = collectDescendantIds(sourceId, treeMap.value)
    if (descendants.includes(targetId)) return false

    // Limite de 5 níveis (0 a 4): parentDepth + 1 + subtreeHeight < MAX_TREE_DEPTH
    const targetDepth = getNodeDepth(targetId, treeMap.value)
    const sourceSubtreeHeight = getSubtreeHeight(sourceNode)
    return targetDepth + 1 + sourceSubtreeHeight < MAX_TREE_DEPTH
  }

  return {
    treeRoots,
    treeMap,
    expandedNodeIds,
    isNodeExpanded,
    toggleNode,
    expandAll,
    collapseAll,
    canNestUnder,
  }
}

export type DropZoneIntent = 'before' | 'inside' | 'after'

export function calculateDropIntent(
  offsetY: number,
  height: number,
  sourceId: number,
  targetId: number,
  canNestFn?: (s: number, t: number) => boolean
): { position: DropZoneIntent | null; allowed: boolean } {
  if (sourceId === targetId || height <= 0) {
    return { position: null, allowed: false }
  }

  const ratio = offsetY / height

  if (ratio < 0.25) {
    return { position: 'before', allowed: true }
  } else if (ratio > 0.75) {
    return { position: 'after', allowed: true }
  } else {
    const allowed = canNestFn ? canNestFn(sourceId, targetId) : true
    return { position: allowed ? 'inside' : null, allowed }
  }
}

