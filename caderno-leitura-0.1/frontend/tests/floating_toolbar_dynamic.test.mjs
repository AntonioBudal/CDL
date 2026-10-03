import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// Mock simples para ambiente de teste node sem window/localStorage nativo
function setupMockStorage(initialData = {}) {
  const store = { ...initialData }
  return {
    getItem: (key) => (key in store ? store[key] : null),
    setItem: (key, val) => {
      store[key] = String(val)
    },
    removeItem: (key) => {
      delete store[key]
    },
    clear: () => {
      Object.keys(store).forEach((k) => delete store[k])
    },
    _getStore: () => store,
  }
}

test('T001: Constantes de toolbar e cores canônicas estão devidamente definidas', async () => {
  const {
    HIGHLIGHT_COLORS,
    HIGHLIGHT_COLOR_HEX,
    HIGHLIGHT_COLOR_BORDER,
    HIGHLIGHT_COLOR_LABELS,
    HIGHLIGHT_COLOR_OPTIONS,
  } = await import('../src/types/toolbar.ts')

  assert.equal(HIGHLIGHT_COLORS.length, 5)
  assert.deepEqual([...HIGHLIGHT_COLORS], ['yellow', 'green', 'blue', 'pink', 'purple'])

  for (const color of HIGHLIGHT_COLORS) {
    assert.ok(HIGHLIGHT_COLOR_HEX[color], `Falta HEX para a cor ${color}`)
    assert.ok(HIGHLIGHT_COLOR_BORDER[color], `Falta borda para a cor ${color}`)
    assert.ok(HIGHLIGHT_COLOR_LABELS[color], `Falta rótulo para a cor ${color}`)
  }

  assert.equal(HIGHLIGHT_COLOR_OPTIONS.length, 5)
  assert.equal(HIGHLIGHT_COLOR_OPTIONS[0].id, 'yellow')
  assert.equal(HIGHLIGHT_COLOR_OPTIONS[0].label, 'Amarelo')
})

test('T003: useHighlightColorPreference gerencia estado reativo e sincroniza com localStorage', async () => {
  const mockStorage = setupMockStorage()
  globalThis.localStorage = mockStorage

  const { useHighlightColorPreference } = await import('../src/composables/useHighlightColorPreference.ts')

  // 1. Inicialização padrão quando vazio -> yellow
  const pref = useHighlightColorPreference()
  assert.equal(pref.activeColor.value, 'yellow')
  assert.equal(pref.colorHex.value, '#fef08a')
  assert.equal(pref.colorLabel.value, 'Amarelo')

  // 2. Mudança de cor -> atualiza ref e localStorage
  pref.setColor('green')
  assert.equal(pref.activeColor.value, 'green')
  assert.equal(mockStorage.getItem('caderno_last_highlight_color'), 'green')
  assert.equal(pref.colorHex.value, '#bbf7d0')

  // 3. Outra cor
  pref.setColor('purple')
  assert.equal(pref.activeColor.value, 'purple')
  assert.equal(mockStorage.getItem('caderno_last_highlight_color'), 'purple')

  // 4. Reset para default
  pref.resetToDefault()
  assert.equal(pref.activeColor.value, 'yellow')
  assert.equal(mockStorage.getItem('caderno_last_highlight_color'), 'yellow')

  // 5. Nova instância recupera cor salva
  mockStorage.setItem('caderno_last_highlight_color', 'blue')
  const pref2 = useHighlightColorPreference()
  assert.equal(pref2.activeColor.value, 'blue')

  // 6. Valor corrompido no storage faz fallback para yellow
  mockStorage.setItem('caderno_last_highlight_color', 'cor_invalida')
  const pref3 = useHighlightColorPreference()
  assert.equal(pref3.activeColor.value, 'yellow')
})

test('T004: computeToolbarPosition mantém compatibilidade para a régua flutuante', async () => {
  const { computeToolbarPosition } = await import('../src/utils/toolbarPosition.ts')

  // Desktop
  const posDesktop = computeToolbarPosition({
    selectionRect: { top: 200, bottom: 230, left: 100, right: 300, width: 200, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 48,
    viewportWidth: 1024,
    viewportHeight: 768,
    isMobile: false,
  })
  assert.equal(posDesktop.isBottomDocked, false)
  assert.equal(posDesktop.top, '142px') // 200 - 48 - 10 = 142
  assert.equal(posDesktop.left, '40px') // Center: 200. Ideal: 200 - 160 = 40

  // Mobile
  const posMobile = computeToolbarPosition({
    selectionRect: { top: 200, bottom: 230, left: 100, right: 300, width: 200, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 48,
    viewportWidth: 390,
    viewportHeight: 844,
    isMobile: true,
  })
  assert.equal(posMobile.isBottomDocked, true)
  assert.equal(posMobile.bottom, '0px')
})

test('T004 / T013: computePopoverPosition ancora adequadamente no desktop e adapta no mobile com visualViewport', async () => {
  const { computePopoverPosition } = await import('../src/utils/toolbarPosition.ts')

  // 1. Desktop padrão (espaço suficiente acima)
  const posDesktop = computePopoverPosition({
    selectionRect: { top: 300, bottom: 330, left: 400, right: 600, width: 200, height: 30 },
    popoverWidth: 320,
    popoverHeight: 140,
    viewportWidth: 1280,
    viewportHeight: 800,
    isMobile: false,
  })
  assert.equal(posDesktop.isMobile, false)
  assert.equal(posDesktop.placement, 'top')
  assert.equal(posDesktop.top, 300 - 140 - 8) // 152px
  assert.equal(posDesktop.left, 500 - 160) // 340px

  // 2. Desktop próximo ao topo (inverte para baixo)
  const posNearTop = computePopoverPosition({
    selectionRect: { top: 40, bottom: 70, left: 400, right: 600, width: 200, height: 30 },
    popoverWidth: 320,
    popoverHeight: 140,
    viewportWidth: 1280,
    viewportHeight: 800,
    isMobile: false,
  })
  assert.equal(posNearTop.placement, 'bottom')
  assert.equal(posNearTop.top, 70 + 8) // 78px

  // 3. Mobile sem teclado virtual aberto
  const posMobileNormal = computePopoverPosition({
    selectionRect: { top: 200, bottom: 230, left: 50, right: 250, width: 200, height: 30 },
    popoverWidth: 390,
    popoverHeight: 180,
    viewportWidth: 390,
    viewportHeight: 844,
    isMobile: true,
  })
  assert.equal(posMobileNormal.isMobile, true)
  assert.equal(posMobileNormal.bottom, 0)

  // 4. Mobile com teclado virtual aberto (visualViewportOffsetBottom informado)
  const posMobileWithKeyboard = computePopoverPosition({
    selectionRect: { top: 200, bottom: 230, left: 50, right: 250, width: 200, height: 30 },
    popoverWidth: 390,
    popoverHeight: 180,
    viewportWidth: 390,
    viewportHeight: 844,
    isMobile: true,
    visualViewportOffsetBottom: 280, // teclado ocupa 280px na base
  })
  assert.equal(posMobileWithKeyboard.isMobile, true)
  assert.equal(posMobileWithKeyboard.bottom, 280)
})

test('T005 / T006 / T007: Split Button possui 5 cores e ações diretas de 1 clique', async () => {
  const toolbarPath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  // Split button
  assert.ok(content.includes('split-button'), 'Deve conter estrutura split-button')
  assert.ok(content.includes('split-trigger'), 'Deve conter split-trigger')
  assert.ok(content.includes('split-expand'), 'Deve conter split-expand')
  assert.ok(content.includes('split-palette-popover'), 'Deve conter split-palette-popover')
  assert.ok(content.includes('HIGHLIGHT_COLOR_OPTIONS'), 'Deve renderizar opções a partir de HIGHLIGHT_COLOR_OPTIONS')
  assert.ok(content.includes('applyHighlight(activeColor)'), 'Split trigger deve aplicar diretamente na cor memorizada')
  assert.ok(content.includes('selectColorAndApply(color.id)'), 'Paleta deve memorizar e aplicar na seleção')

  // Eventos emitidos
  assert.ok(content.includes("'open-note'"), 'Deve emitir open-note')
  assert.ok(content.includes("'open-question'"), 'Deve emitir open-question')
  assert.ok(content.includes("'tool-selected'"), 'Deve emitir tool-selected')
})

test('T008 / T012: StudyView.vue integra a régua e o popover com recolhimento coordenado', async () => {
  const studyViewPath = path.resolve('src/views/StudyView.vue')
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  // Import e instanciação de NoteQuestionPopover
  assert.ok(content.includes("import NoteQuestionPopover from '../components/NoteQuestionPopover.vue'"), 'Deve importar NoteQuestionPopover')
  assert.ok(content.includes('<NoteQuestionPopover'), 'Deve renderizar NoteQuestionPopover no template')

  // Recolhimento coordenado da barra flutuante
  assert.ok(content.includes('!isNotePopoverOpen'), 'Barra flutuante deve se recolher quando popover estiver aberto')
  assert.ok(content.includes('@open-note="handleOpenNote"'), 'Deve capturar evento open-note')
  assert.ok(content.includes('@open-question="handleOpenQuestion"'), 'Deve capturar evento open-question')
  assert.ok(content.includes('@save="handlePopoverSave"'), 'Deve capturar evento save do popover')
  assert.ok(content.includes('@cancel="handlePopoverCancel"'), 'Deve capturar evento cancel do popover')

  // Toasts informativos
  assert.ok(content.includes("'Anotação salva'"), 'Deve disparar toast de anotação salva')
  assert.ok(content.includes("'Pergunta cadastrada'"), 'Deve disparar toast de pergunta cadastrada')
})

test('T009 / T010: NoteQuestionPopover.vue valida campo vazio, atalhos de teclado e autofocus', async () => {
  const popoverPath = path.resolve('src/components/NoteQuestionPopover.vue')
  const content = fs.readFileSync(popoverPath, 'utf-8')

  // Validação de texto vazio / apenas espaços
  assert.ok(content.includes(':disabled="!text.trim()"'), 'Botão submit deve ser desabilitado quando texto for vazio')
  assert.ok(content.includes('if (!clean || !props.selection) return'), 'handleSave deve ignorar submissão com texto vazio')

  // Atalhos de teclado
  assert.ok(content.includes("event.key === 'Enter' && !event.shiftKey"), 'Enter sem Shift deve salvar diretamente')
  assert.ok(content.includes("event.key === 'Escape'"), 'Escape deve cancelar e fechar')

  // Autofocus
  assert.ok(content.includes('textareaRef.value?.focus()'), 'Deve focalizar automaticamente o textarea ao abrir')
})

test('T014 / T015: Ergonomia móvel garante alvos de 44x44px e visualViewport', async () => {
  const toolbarPath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const toolbarContent = fs.readFileSync(toolbarPath, 'utf-8')
  assert.ok(toolbarContent.includes('min-height: 44px;'), 'Toolbar móvel deve garantir altura mínima de 44px')
  assert.ok(toolbarContent.includes('min-width: 44px;'), 'Toolbar móvel deve garantir largura mínima de 44px')

  const popoverPath = path.resolve('src/components/NoteQuestionPopover.vue')
  const popoverContent = fs.readFileSync(popoverPath, 'utf-8')
  assert.ok(popoverContent.includes('bottom-sheet'), 'Popover deve possuir modo bottom-sheet no mobile')
  assert.ok(popoverContent.includes('min-height: 44px;'), 'Botões móveis do popover devem ter pelo menos 44px de altura')
  assert.ok(popoverContent.includes('window.visualViewport'), 'Deve monitorar visualViewport para compensar teclado virtual')
  assert.ok(popoverContent.includes('viewportOffsetBottom'), 'Deve aplicar deslocamento inferior quando teclado estiver ativo')
})
