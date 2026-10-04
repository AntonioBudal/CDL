import test from 'node:test'
import assert from 'node:assert/strict'
import { ref } from 'vue'

// Mock simples de localStorage
class LocalStorageMock {
  constructor() {
    this.store = new Map()
  }
  getItem(key) {
    return this.store.get(key) || null
  }
  setItem(key, value) {
    this.store.set(key, String(value))
  }
  removeItem(key) {
    this.store.delete(key)
  }
  clear() {
    this.store.clear()
  }
}

globalThis.localStorage = new LocalStorageMock()
globalThis.window = {
  localStorage: globalThis.localStorage,
}

const {
  buildStudyTree,
  useStudyHierarchy,
  calculateBranchProgress,
  MAX_TREE_DEPTH,
  getSubtreeHeight,
  getNodeDepth,
} = await import('../src/composables/useStudyHierarchy.ts')

// ==========================================
// User Story 1: Estruturação e Visualização Hierárquica em Árvore
// ==========================================

test('buildStudyTree com lista vazia retorna array vazio', () => {
  const tree = buildStudyTree([])
  assert.deepEqual(tree, [])
})

test('buildStudyTree constrói raízes e calcula depth e children corretamente', () => {
  const mockStudies = [
    { id: 1, chapter_id: 10, title: 'Raiz A', location: '', parent_study_id: null, position: 0, created_at: '', updated_at: '' },
    { id: 2, chapter_id: 10, title: 'Filho A1', location: '', parent_study_id: 1, position: 0, created_at: '', updated_at: '' },
    { id: 3, chapter_id: 10, title: 'Filho A2', location: '', parent_study_id: 1, position: 1, created_at: '', updated_at: '' },
    { id: 4, chapter_id: 10, title: 'Neto A1.1', location: '', parent_study_id: 2, position: 0, created_at: '', updated_at: '' },
    { id: 5, chapter_id: 10, title: 'Raiz B', location: '', parent_study_id: null, position: 1, created_at: '', updated_at: '' },
  ]

  const tree = buildStudyTree(mockStudies)

  assert.equal(tree.length, 2, 'Devem existir 2 raízes')
  assert.equal(tree[0].id, 1)
  assert.equal(tree[0].depth, 0)
  assert.equal(tree[0].children.length, 2, 'Raiz A deve ter 2 filhos')

  // Verifica Filho A1
  const filhoA1 = tree[0].children[0]
  assert.equal(filhoA1.id, 2)
  assert.equal(filhoA1.depth, 1)
  assert.equal(filhoA1.children.length, 1, 'Filho A1 deve ter 1 neto')

  // Verifica Neto A1.1
  const neto = filhoA1.children[0]
  assert.equal(neto.id, 4)
  assert.equal(neto.depth, 2)
  assert.equal(neto.children.length, 0)

  // Verifica Raiz B
  assert.equal(tree[1].id, 5)
  assert.equal(tree[1].depth, 0)
  assert.equal(tree[1].children.length, 0)
})

test('buildStudyTree ordena irmãos por position', () => {
  const mockStudies = [
    { id: 10, chapter_id: 1, title: 'Segundo', parent_study_id: null, position: 1, location: '', created_at: '', updated_at: '' },
    { id: 11, chapter_id: 1, title: 'Primeiro', parent_study_id: null, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 12, chapter_id: 1, title: 'Terceiro', parent_study_id: null, position: 2, location: '', created_at: '', updated_at: '' },
  ]

  const tree = buildStudyTree(mockStudies)
  assert.equal(tree[0].id, 11)
  assert.equal(tree[1].id, 10)
  assert.equal(tree[2].id, 12)
})

test('useStudyHierarchy gerencia expansão/colapso e persiste no localStorage', () => {
  globalThis.localStorage.clear()

  const studies = ref([
    { id: 1, chapter_id: 99, title: 'Pai', parent_study_id: null, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 99, title: 'Filho', parent_study_id: 1, position: 0, location: '', created_at: '', updated_at: '' },
  ])
  const chapterId = ref(99)

  const hierarchy = useStudyHierarchy(studies, chapterId)

  // Inicialmente o pai deve estar expandido por padrão
  assert.equal(hierarchy.isNodeExpanded(1), true)

  // Alterna expansão
  hierarchy.toggleNode(1)
  assert.equal(hierarchy.isNodeExpanded(1), false)

  // Verifica persistência no localStorage
  const rawSaved = globalThis.localStorage.getItem('caderno_tree_expanded_ch_99')
  assert.ok(rawSaved)
  assert.deepEqual(JSON.parse(rawSaved), [])

  // Expande tudo
  hierarchy.expandAll()
  assert.equal(hierarchy.isNodeExpanded(1), true)

  // Recolhe tudo
  hierarchy.collapseAll()
  assert.equal(hierarchy.isNodeExpanded(1), false)
})

test('canNestUnder previne ciclos e auto-referência', () => {
  const studies = ref([
    { id: 1, chapter_id: 1, title: 'Pai', parent_study_id: null, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 1, title: 'Filho', parent_study_id: 1, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 3, chapter_id: 1, title: 'Neto', parent_study_id: 2, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 4, chapter_id: 1, title: 'Outro Raiz', parent_study_id: null, position: 1, location: '', created_at: '', updated_at: '' },
  ])

  const hierarchy = useStudyHierarchy(studies)

  // 1. Auto-referência bloqueada
  assert.equal(hierarchy.canNestUnder(1, 1), false)

  // 2. Mover pai para dentro de seu próprio filho é bloqueado (ciclo)
  assert.equal(hierarchy.canNestUnder(1, 2), false)

  // 3. Mover pai para dentro de seu próprio neto é bloqueado (ciclo indireto)
  assert.equal(hierarchy.canNestUnder(1, 3), false)

  // 4. Mover filho para a raiz é permitido
  assert.equal(hierarchy.canNestUnder(2, null), true)

  // 5. Mover Outro Raiz para dentro de Pai é permitido
  assert.equal(hierarchy.canNestUnder(4, 1), true)
})

test('canNestUnder respeita o limite de profundidade de 5 níveis', () => {
  // Cadeia de 5 níveis (depth 0 a 4)
  const studies = ref([
    { id: 1, chapter_id: 1, title: 'N0', parent_study_id: null, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 2, chapter_id: 1, title: 'N1', parent_study_id: 1, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 3, chapter_id: 1, title: 'N2', parent_study_id: 2, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 4, chapter_id: 1, title: 'N3', parent_study_id: 3, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 5, chapter_id: 1, title: 'N4', parent_study_id: 4, position: 0, location: '', created_at: '', updated_at: '' },
    { id: 6, chapter_id: 1, title: 'Solto', parent_study_id: null, position: 1, location: '', created_at: '', updated_at: '' },
  ])

  const hierarchy = useStudyHierarchy(studies)

  // N4 já está na profundidade 4. Tentar aninhar o nó 6 sob N4 ultrapassaria o limite (0,1,2,3,4 -> 5)
  assert.equal(hierarchy.canNestUnder(6, 5), false)

  // Aninhar sob N3 cria nó em profundidade 4 (5 níveis no total: 0,1,2,3,4) -> Permitido
  assert.equal(hierarchy.canNestUnder(6, 4), true)
})

// ==========================================
// User Story 2: Percepção e Progresso Agregado por Ramo
// ==========================================

test('calculateBranchProgress e buildStudyTree calculam progresso agregado recursivo em tempo linear', () => {
  const studies = [
    { id: 1, title: 'Tópico 1', parent_study_id: null, position: 0, reading_status: 'rascunho' },
    { id: 2, title: 'Subtópico 1.1', parent_study_id: 1, position: 0, reading_status: 'concluido' },
    { id: 3, title: 'Subtópico 1.2', parent_study_id: 1, position: 1, reading_status: 'revisado' },
    { id: 4, title: 'Detalhe 1.2.1', parent_study_id: 3, position: 0, reading_status: 'rascunho' },
    { id: 5, title: 'Tópico 2 (Folha)', parent_study_id: null, position: 1, reading_status: 'concluido' },
  ]

  const tree = buildStudyTree(studies)

  // Tópico 2 é folha (sem filhos): progress deve ser null
  assert.equal(tree[1].progress, null)

  // Subtópico 1.2 tem 1 filho (Detalhe 1.2.1 - rascunho)
  assert.ok(tree[0].children[1].progress)
  assert.equal(tree[0].children[1].progress.total, 1)
  assert.equal(tree[0].children[1].progress.completed, 0)
  assert.equal(tree[0].children[1].progress.percent, 0)
  assert.equal(tree[0].children[1].progress.label, '0/1 concluídos')

  // Tópico 1 tem 3 descendentes no total (2, 3 e 4).
  // Status: 2 é concluido, 3 é revisado, 4 é rascunho.
  // Concluidos consolidado: 2 (concluido + revisado).
  assert.ok(tree[0].progress)
  assert.equal(tree[0].progress.total, 3)
  assert.equal(tree[0].progress.completed, 2)
  assert.equal(tree[0].progress.percent, 67)
  assert.equal(tree[0].progress.label, '2/3 concluídos')
  assert.equal(tree[0].progress.details.concluido, 1)
  assert.equal(tree[0].progress.details.revisado, 1)
  assert.equal(tree[0].progress.details.rascunho, 1)
})

test('useStudyHierarchy suporta bookId como chave de persistência de nós expandidos', () => {
  globalThis.localStorage.clear()

  const studies = ref([
    { id: 10, title: 'Pai', parent_study_id: null, position: 0 },
    { id: 11, title: 'Filho', parent_study_id: 10, position: 0 },
  ])
  const bookId = ref(55)

  const hierarchy = useStudyHierarchy(studies, null, bookId)

  // Padrão: pai inicia expandido
  assert.equal(hierarchy.isNodeExpanded(10), true)

  hierarchy.toggleNode(10)
  assert.equal(hierarchy.isNodeExpanded(10), false)

  const saved = globalThis.localStorage.getItem('caderno_tree_expanded_55')
  assert.ok(saved)
})
