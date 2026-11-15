import test from 'node:test'
import assert from 'node:assert/strict'

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

// F0.12.10: a barra flutuante virou a barra fixa StudyActionsBar.vue (posição junto da seleção saiu).
test('StudyActionsBar.vue define acessibilidade WAI-ARIA e ergonomia móvel', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/StudyActionsBar.vue')
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
