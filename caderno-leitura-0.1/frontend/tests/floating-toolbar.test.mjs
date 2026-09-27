import test from 'node:test'
import assert from 'node:assert/strict'
import { computeToolbarPosition } from '../src/utils/toolbarPosition.ts'

test('computeToolbarPosition posiciona barra fixa na base quando em modo mobile', () => {
  const pos = computeToolbarPosition({
    selectionRect: { top: 200, bottom: 230, left: 50, right: 300, width: 250, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 56,
    viewportWidth: 390,
    viewportHeight: 844,
    isMobile: true,
  })

  assert.equal(pos.isBottomDocked, true)
  assert.equal(pos.bottom, '0px')
  assert.equal(pos.left, '0px')
})

test('computeToolbarPosition posiciona acima da seleção no desktop e centraliza', () => {
  const pos = computeToolbarPosition({
    selectionRect: { top: 300, bottom: 330, left: 400, right: 600, width: 200, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 48,
    viewportWidth: 1280,
    viewportHeight: 800,
    isMobile: false,
  })

  assert.equal(pos.isBottomDocked, false)
  // Horizontal center: 400 + 100 = 500. Ideal left: 500 - 160 = 340.
  assert.equal(pos.left, '340px')
  // Top: 300 - 48 - 10 = 242px.
  assert.equal(pos.top, '242px')
})

test('computeToolbarPosition inverte para baixo quando seleção está muito próxima ao topo', () => {
  const pos = computeToolbarPosition({
    selectionRect: { top: 20, bottom: 50, left: 400, right: 600, width: 200, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 48,
    viewportWidth: 1280,
    viewportHeight: 800,
    isMobile: false,
  })

  assert.equal(pos.isBottomDocked, false)
  // Top: abaixo da seleção: 50 + 10 = 60px.
  assert.equal(pos.top, '60px')
})

test('computeToolbarPosition clampa dentro do viewport nas bordas laterais', () => {
  const pos = computeToolbarPosition({
    selectionRect: { top: 300, bottom: 330, left: 1200, right: 1270, width: 70, height: 30 },
    toolbarWidth: 320,
    toolbarHeight: 48,
    viewportWidth: 1280,
    viewportHeight: 800,
    isMobile: false,
  })

  // Viewport width: 1280. Max left = 1280 - 320 - 12 = 948px.
  assert.equal(pos.left, '948px')
})

test('formatQuoteText formata citação apenas com título do estudo quando metadados opcionais estão ausentes', async () => {
  const { formatQuoteText } = await import('../src/composables/useTextSelection.ts')
  const formatted = formatQuoteText({
    selected_text: 'O ser determina a consciência.',
    studyTitle: 'Ideologia Alemã',
  })

  assert.ok(formatted.includes('> "O ser determina a consciência."'))
  assert.ok(formatted.includes('— *Ideologia Alemã*'))
  assert.ok(!formatted.includes('undefined'))
})

test('FloatingActionsToolbar.vue define acessibilidade WAI-ARIA e ergonomia móvel', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  // Semântica de Toolbar WAI-ARIA
  assert.ok(content.includes('role="toolbar"'), 'Deve conter role="toolbar"')
  assert.ok(content.includes('aria-label="Ações para o trecho selecionado"'), 'Deve conter aria-label descritivo')
  assert.ok(content.includes("event.key === 'Escape'"), 'Escape deve fechar a barra')

  // Alvos de toque móveis >= 44x44px
  assert.ok(content.includes('min-height: 44px;'), 'Botões móveis devem ter altura mínima de 44px')
  assert.ok(content.includes('min-width: 44px;'), 'Botões móveis devem ter largura mínima de 44px')

  // Suporte a permissão canEdit
  assert.ok(content.includes('v-if="canEdit"'), 'Ações de modificação devem respeitar canEdit')
  assert.ok(content.includes('triggerQuote'), 'Ação de citação deve estar sempre disponível')
})
