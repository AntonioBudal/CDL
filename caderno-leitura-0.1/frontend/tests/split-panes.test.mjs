import test from 'node:test'
import assert from 'node:assert/strict'

// Mock simples de localStorage e window para execução isolada no Node test runner
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
  innerWidth: 1280,
  localStorage: globalThis.localStorage,
  addEventListener: () => {},
  removeEventListener: () => {}
}

const {
  useSplitPanes,
  loadStoredDimensions,
  saveStoredDimensions,
  GLOBAL_STORAGE_KEY,
  BOOK_STORAGE_KEY_PREFIX
} = await import('../src/composables/useSplitPanes.ts')

test('useSplitPanes inicializa com valores padrão e painel direito recolhido (Q1)', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes()

  assert.equal(split.leftWidth.value, 300)
  assert.equal(split.rightWidth.value, 300)
  assert.equal(split.leftCollapsed.value, false)
  assert.equal(split.rightCollapsed.value, true, 'Painel direito deve iniciar recolhido por padrão na primeira visita')
  assert.equal(split.layoutMode.value, 'split')
})

test('useSplitPanes respeita persistência híbrida (global vs por livro)', () => {
  globalThis.localStorage.clear()

  // 1. Salva configuração global
  const globalDims = {
    leftWidth: 350,
    rightWidth: 280,
    leftCollapsed: false,
    rightCollapsed: false,
    updatedAt: new Date().toISOString()
  }
  saveStoredDimensions(globalDims)

  // Ao carregar sem bookId, deve refletir as dimensões globais
  const loadedGlobal = loadStoredDimensions()
  assert.equal(loadedGlobal.leftWidth, 350)
  assert.equal(loadedGlobal.rightWidth, 280)

  // 2. Salva configuração específica para o livro '42'
  const book42Dims = {
    leftWidth: 400,
    rightWidth: 320,
    leftCollapsed: true,
    rightCollapsed: false,
    updatedAt: new Date().toISOString()
  }
  saveStoredDimensions(book42Dims, '42')

  // Ao carregar para o livro 42, deve ter precedência sobre o global
  const loadedBook42 = loadStoredDimensions('42')
  assert.equal(loadedBook42.leftWidth, 400)
  assert.equal(loadedBook42.leftCollapsed, true)

  // Outro livro sem configuração específica deve herdar a global mais recente
  const loadedOtherBook = loadStoredDimensions('99')
  assert.equal(loadedOtherBook.leftWidth, 400, 'Herdou a última configuração global salva')
})

test('useSplitPanes aplica clamping min/max (240px a 600px)', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes({ minWidth: 240, maxWidth: 600 })

  // Passo positivo grande não deve ultrapassar 600px
  split.stepResize('left', 500)
  assert.ok(split.leftWidth.value <= 600)
  assert.equal(split.leftWidth.value, 600)

  // Passo negativo grande não deve ficar abaixo de 240px se não colapsar
  split.stepResize('left', -200)
  assert.equal(split.leftWidth.value, 400)

  split.stepResize('left', -150)
  assert.equal(split.leftWidth.value, 250)
})

test('useSplitPanes snap-to-collapse quando largura diminui abaixo de 60px', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes({ minWidth: 240, maxWidth: 600, snapThreshold: 60 })

  assert.equal(split.leftCollapsed.value, false)

  // Reduzir além do limiar de snap (ex: de 300 para 50) deve colapsar o painel
  split.stepResize('left', -250)
  assert.equal(split.leftCollapsed.value, true)

  // Passo positivo descolapsa o painel na largura mínima
  split.stepResize('left', 20)
  assert.equal(split.leftCollapsed.value, false)
  assert.equal(split.leftWidth.value, 240)
})

test('useSplitPanes alterna colapso e restaura valores padrão', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes()

  // Alternar painel direito
  assert.equal(split.rightCollapsed.value, true)
  split.toggleCollapse('right')
  assert.equal(split.rightCollapsed.value, false)

  // Reset to default
  split.stepResize('right', 80)
  assert.equal(split.rightWidth.value, 380)

  split.resetToDefault('right')
  assert.equal(split.rightWidth.value, 300)
  assert.equal(split.rightCollapsed.value, false)
})

test('comutação de layoutMode conforme largura da janela', () => {
  // Mobile (< 768px)
  globalThis.window.innerWidth = 480
  const mobileSplit = useSplitPanes()
  assert.equal(mobileSplit.layoutMode.value, 'mobile')

  // Tablet (768px a 1023px)
  globalThis.window.innerWidth = 800
  const tabletSplit = useSplitPanes()
  assert.equal(tabletSplit.layoutMode.value, 'drawer')

  // Desktop (>= 1024px)
  globalThis.window.innerWidth = 1440
  const desktopSplit = useSplitPanes()
  assert.equal(desktopSplit.layoutMode.value, 'split')
})

test('US2: controle por teclado (passos de 10px, limites Home/End e alternância Enter)', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes({ minWidth: 240, maxWidth: 600, initialLeftWidth: 300 })

  // 1. Passos de 10px com setas direcionais
  assert.equal(split.leftWidth.value, 300)
  split.stepResize('left', 10)
  assert.equal(split.leftWidth.value, 310)

  split.stepResize('left', -10)
  assert.equal(split.leftWidth.value, 300)

  // 2. Simulação de tecla Home: salto direto para a largura mínima (240px)
  const toMinDelta = 240 - split.leftWidth.value
  split.stepResize('left', toMinDelta)
  assert.equal(split.leftWidth.value, 240)

  // 3. Simulação de tecla End: salto direto para a largura máxima (600px)
  const toMaxDelta = 600 - split.leftWidth.value
  split.stepResize('left', toMaxDelta)
  assert.equal(split.leftWidth.value, 600)

  // 4. Tecla Enter ou Espaço: alternância de colapso
  assert.equal(split.leftCollapsed.value, false)
  split.toggleCollapse('left')
  assert.equal(split.leftCollapsed.value, true)

  split.toggleCollapse('left')
  assert.equal(split.leftCollapsed.value, false)
})

test('US2: cálculo de semântica WAI-ARIA do separador', () => {
  globalThis.localStorage.clear()
  const split = useSplitPanes({ minWidth: 240, maxWidth: 600, initialLeftWidth: 320 })

  // Quando expandido, aria-valuenow reflete a largura atual
  const ariaValueNowExpanded = split.leftCollapsed.value ? 0 : Math.round(split.leftWidth.value)
  assert.equal(ariaValueNowExpanded, 320)

  // Quando colapsado, aria-valuenow reporta 0
  split.toggleCollapse('left')
  const ariaValueNowCollapsed = split.leftCollapsed.value ? 0 : Math.round(split.leftWidth.value)
  assert.equal(ariaValueNowCollapsed, 0)
})
