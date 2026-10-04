import test from 'node:test'
import assert from 'node:assert/strict'
import { formatMarkdown } from '../src/utils/markdownFormatter.ts'

test('formatMarkdown: bold envolve texto selecionado com **', () => {
  const text = 'Este é um conceito importante para a análise.'
  // 'conceito importante' está em [10, 29]
  const result = formatMarkdown(text, 10, 29, 'bold')
  assert.equal(result.newText, 'Este é um **conceito importante** para a análise.')
  assert.equal(result.newSelectionStart, 12)
  assert.equal(result.newSelectionEnd, 31)
})

test('formatMarkdown: bold sem seleção insere placeholder selecionado', () => {
  const text = 'Início: '
  const result = formatMarkdown(text, 8, 8, 'bold')
  assert.equal(result.newText, 'Início: **texto em negrito**')
  assert.equal(result.newSelectionStart, 10)
  assert.equal(result.newSelectionEnd, 26)
})

test('formatMarkdown: bold desfaz ** se o texto já estiver entre asteriscos duplos', () => {
  const text = 'Este é um **conceito importante** para a análise.'
  // 'conceito importante' está em [12, 31]
  const result = formatMarkdown(text, 12, 31, 'bold')
  assert.equal(result.newText, 'Este é um conceito importante para a análise.')
  assert.equal(result.newSelectionStart, 10)
  assert.equal(result.newSelectionEnd, 29)
})

test('formatMarkdown: italic envolve texto selecionado com *', () => {
  const text = 'Uma ênfase sutil aqui.'
  const result = formatMarkdown(text, 4, 16, 'italic')
  assert.equal(result.newText, 'Uma *ênfase sutil* aqui.')
  assert.equal(result.newSelectionStart, 5)
  assert.equal(result.newSelectionEnd, 17)
})

test('formatMarkdown: italic sem seleção insere placeholder selecionado', () => {
  const text = 'Texto: '
  const result = formatMarkdown(text, 7, 7, 'italic')
  assert.equal(result.newText, 'Texto: *texto em itálico*')
  assert.equal(result.newSelectionStart, 8)
  assert.equal(result.newSelectionEnd, 24)
})

test('formatMarkdown: heading insere ### no início da linha atual', () => {
  const text = 'Introdução ao Tema\nConteúdo explicativo.'
  const result = formatMarkdown(text, 5, 5, 'heading')
  assert.equal(result.newText, '### Introdução ao Tema\nConteúdo explicativo.')
})

test('formatMarkdown: heading alterna (toggle off) se já tiver ###', () => {
  const text = '### Introdução ao Tema\nConteúdo explicativo.'
  const result = formatMarkdown(text, 8, 8, 'heading')
  assert.equal(result.newText, 'Introdução ao Tema\nConteúdo explicativo.')
})

test('formatMarkdown: bullet_list adiciona hífen e espaço nas linhas selecionadas', () => {
  const text = 'Primeiro item\nSegundo item'
  const result = formatMarkdown(text, 0, text.length, 'bullet_list')
  assert.equal(result.newText, '- Primeiro item\n- Segundo item')
})

test('formatMarkdown: bullet_list alterna (toggle off) se todas já forem lista', () => {
  const text = '- Primeiro item\n- Segundo item'
  const result = formatMarkdown(text, 0, text.length, 'bullet_list')
  assert.equal(result.newText, 'Primeiro item\nSegundo item')
})

test('formatMarkdown: quote adiciona > nas linhas selecionadas', () => {
  const text = 'Uma citação profunda do autor.\nSegunda linha.'
  const result = formatMarkdown(text, 0, text.length, 'quote')
  assert.equal(result.newText, '> Uma citação profunda do autor.\n> Segunda linha.')
})

test('formatMarkdown: code envolve texto com crase', () => {
  const text = 'Use a função calcularTotal() para somar.'
  const result = formatMarkdown(text, 13, 28, 'code')
  assert.equal(result.newText, 'Use a função `calcularTotal()` para somar.')
})

test('formatMarkdown: link cria sintaxe [texto](https://...)', () => {
  const text = 'Consulte a documentação oficial para mais detalhes.'
  const result = formatMarkdown(text, 11, 31, 'link')
  assert.equal(result.newText, 'Consulte a [documentação oficial](https://...) para mais detalhes.')
})

test('MarkdownToolbar.vue possui role="toolbar", aria-label e botões de formatação', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/MarkdownToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  assert.ok(content.includes('role="toolbar"'), 'Deve possuir role="toolbar"')
  assert.ok(content.includes('aria-label="Ferramentas de formatação Markdown"'), 'Deve possuir aria-label descritivo')
  assert.ok(content.includes('@mousedown.prevent="handleFormat(\'bold\')"'), 'Deve ter ação de negrito com prevent')
  assert.ok(content.includes('@mousedown.prevent="handleFormat(\'italic\')"'), 'Deve ter ação de itálico com prevent')
  assert.ok(content.includes('@mousedown.prevent="handleFormat(\'heading\')"'), 'Deve ter ação de título com prevent')
  assert.ok(content.includes('@mousedown.prevent="handleFormat(\'bullet_list\')"'), 'Deve ter ação de lista com prevent')
  assert.ok(content.includes('@mousedown.prevent="handleFormat(\'quote\')"'), 'Deve ter ação de citação com prevent')
})

test('StudyEditorFields.vue integra MarkdownToolbar nos campos de seções e notas', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const fieldsPath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(fieldsPath, 'utf-8')

  assert.ok(content.includes('<MarkdownToolbar :target-id="`${idPrefix}-${section.key}`" />'), 'Deve integrar toolbar nas seções')
  assert.ok(content.includes('<MarkdownToolbar :target-id="`${idPrefix}-notes`" />'), 'Deve integrar toolbar nas anotações')
})

test('FloatingActionsToolbar.vue emite payload com selection e previne perda de foco no mousedown', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/FloatingActionsToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  assert.ok(content.includes('selection: TextSelectionContext'), 'Deve definir tipagem de selection nos emits')
  assert.ok(content.includes('@mousedown="handleToolbarMouseDown"'), 'Deve prevenir perda de foco na toolbar')
  assert.ok(content.includes('currentSelection'), 'Deve preservar seleção capturada localmente')
})

test('MarkdownToolbar.vue implementa atalhos de teclado Ctrl+B, Ctrl+I e Ctrl+K', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/MarkdownToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  assert.ok(content.includes("e.key === 'b' || e.key === 'B'"), 'Deve responder a Ctrl+B')
  assert.ok(content.includes("e.key === 'i' || e.key === 'I'"), 'Deve responder a Ctrl+I')
  assert.ok(content.includes("e.key === 'k' || e.key === 'K'"), 'Deve responder a Ctrl+K')
  assert.ok(content.includes("e.preventDefault()"), 'Deve prevenir comportamento padrão nos atalhos')
})

test('MarkdownToolbar.vue atende ergonomia tátil móvel com alvos >= 44x44px e rolagem horizontal', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const toolbarPath = path.resolve('src/components/MarkdownToolbar.vue')
  const content = fs.readFileSync(toolbarPath, 'utf-8')

  assert.ok(content.includes('min-width: 44px') || content.includes('44px'), 'Botões móveis devem ter min-width >= 44px')
  assert.ok(content.includes('min-height: 44px') || content.includes('44px'), 'Botões móveis devem ter min-height >= 44px')
  assert.ok(content.includes('touch-action: manipulation'), 'Deve ter touch-action manipulation para resposta tátil rápida')
  assert.ok(content.includes('overflow-x: auto'), 'Deve ter suporte a rolagem horizontal suave no mobile')
})

test('StudyEditorFields.vue possui botão toggle Editar / Prévia in-place com renderizador de markdown', async () => {
  const fs = await import('node:fs')
  const path = await import('node:path')
  const fieldsPath = path.resolve('src/components/StudyEditorFields.vue')
  const content = fs.readFileSync(fieldsPath, 'utf-8')

  assert.ok(content.includes('preview-toggle-btn'), 'Deve possuir botão de toggle de prévia')
  assert.ok(content.includes('MarkdownContent'), 'Deve integrar componente de renderização segura')
  assert.ok(content.includes('togglePreview'), 'Deve possuir função de toggle de prévia')
  assert.ok(content.includes('preview-box'), 'Deve exibir caixa de prévia renderizada')
})

