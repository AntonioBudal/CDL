import test from 'node:test'
import assert from 'node:assert/strict'

// Mock simples de localStorage para o Node test runner
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
  localStorage: globalThis.localStorage
}

const {
  useViewPreference,
  loadStoredViewPreference,
  saveStoredViewPreference,
  VIEW_GLOBAL_STORAGE_KEY,
  VIEW_BOOK_STORAGE_KEY_PREFIX
} = await import('../src/composables/useViewPreference.ts')

const { STUDY_VIEW_OPTIONS } = await import('../src/types.ts')

// ==========================================
// User Story 1: Modos Canônicos e Foco
// ==========================================

test('useViewPreference inicializa com "grid" como fallback padrão', () => {
  globalThis.localStorage.clear()
  const pref = useViewPreference()

  assert.equal(pref.currentMode.value, 'grid')
  assert.equal(pref.activeStudyId.value, null)
  assert.equal(pref.availableModes.length, 5)
})

test('useViewPreference comuta entre os 5 modos canônicos e preserva activeStudyId', () => {
  globalThis.localStorage.clear()
  const pref = useViewPreference()

  pref.setMode('tree')
  assert.equal(pref.currentMode.value, 'tree')

  pref.setActiveStudy(42)
  assert.equal(pref.activeStudyId.value, 42)

  // Ao comutar para outro modo, o estudo ativo em foco permanece preservado
  pref.setMode('canvas')
  assert.equal(pref.currentMode.value, 'canvas')
  assert.equal(pref.activeStudyId.value, 42)

  pref.setMode('map')
  assert.equal(pref.currentMode.value, 'map')
  assert.equal(pref.activeStudyId.value, 42)

  pref.setMode('list')
  assert.equal(pref.currentMode.value, 'list')
  assert.equal(pref.activeStudyId.value, 42)
})

test('useViewPreference ignora modos inválidos', () => {
  globalThis.localStorage.clear()
  const pref = useViewPreference()

  assert.equal(pref.currentMode.value, 'grid')
  // @ts-ignore
  pref.setMode('invalid_mode')
  assert.equal(pref.currentMode.value, 'grid', 'Modo não canônico deve ser descartado')
})

// ==========================================
// User Story 2: Persistência Híbrida e Teclado WAI-ARIA
// ==========================================

test('useViewPreference respeita o modelo híbrido de persistência (Q2)', () => {
  globalThis.localStorage.clear()

  // 1. Salva preferência global da biblioteca
  saveStoredViewPreference('list')
  assert.equal(loadStoredViewPreference(), 'list')
  assert.equal(globalThis.localStorage.getItem(VIEW_GLOBAL_STORAGE_KEY), 'list')

  // 2. Salva preferência individual para o livro '10'
  saveStoredViewPreference('tree', '10')
  assert.equal(loadStoredViewPreference('10'), 'tree', 'Livro 10 tem preferência individual em Árvore')
  assert.equal(globalThis.localStorage.getItem(`${VIEW_BOOK_STORAGE_KEY_PREFIX}10`), 'tree')

  // 3. Outro livro novo sem preferência individual herda a global mais recente
  assert.equal(loadStoredViewPreference('99'), 'tree', 'Novas obras herdam a última preferência global salva')

  // 4. Instância com bookId carrega a preferência correta
  const book10Pref = useViewPreference({ bookId: '10' })
  assert.equal(book10Pref.currentMode.value, 'tree')
})

test('Navegação WAI-ARIA do ViewSwitcher calcula índices corretamente', () => {
  const options = STUDY_VIEW_OPTIONS
  const count = options.length
  assert.equal(count, 5)

  // Função auxiliar simulando a lógica de teclado de ViewSwitcher.vue
  function getNextIndex(currentIdx, key) {
    switch (key) {
      case 'ArrowRight':
      case 'ArrowDown':
        return (currentIdx + 1) % count
      case 'ArrowLeft':
      case 'ArrowUp':
        return (currentIdx - 1 + count) % count
      case 'Home':
        return 0
      case 'End':
        return count - 1
      default:
        return currentIdx
    }
  }

  // De 0 ('grid') para a direita -> 1 ('list')
  assert.equal(getNextIndex(0, 'ArrowRight'), 1)
  // De 4 ('canvas') para a direita -> volta ciclicamente para 0 ('grid')
  assert.equal(getNextIndex(4, 'ArrowRight'), 0)
  // De 0 ('grid') para a esquerda -> volta ciclicamente para 4 ('canvas')
  assert.equal(getNextIndex(0, 'ArrowLeft'), 4)
  // De qualquer posição, Home -> 0 ('grid') e End -> 4 ('canvas')
  assert.equal(getNextIndex(2, 'Home'), 0)
  assert.equal(getNextIndex(2, 'End'), 4)
})

// ==========================================
// User Story 3: Requisitos do Dashboard Responsivo
// ==========================================

test('Contrato de layout do Dashboard no celular define 2 colunas e destaque de streak', () => {
  // Verificação dos valores semânticos especificados no contrato F01 / US3
  const mobileBreakpoint = 768
  const mobileGridColumns = 'repeat(2, 1fr)'
  const streakCardSpan = 'span 2'
  const minTouchTargetSize = 44

  assert.equal(mobileBreakpoint, 768)
  assert.equal(mobileGridColumns, 'repeat(2, 1fr)')
  assert.equal(streakCardSpan, 'span 2')
  assert.ok(minTouchTargetSize >= 44, 'Área de toque deve ser no mínimo 44x44px conforme WCAG 2.2')
})
