import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { HIGHLIGHT_SEMANTIC_CATEGORIES } from '../src/types/toolbar.ts'

const srcDir = path.resolve(process.cwd(), 'src')

test('US1: HighlightCard implementa estrutura de Ficha Literária com tipografia editorial', () => {
  const cardPath = path.resolve(srcDir, 'components/highlights/HighlightCard.vue')
  assert.ok(fs.existsSync(cardPath), 'HighlightCard.vue deve existir')

  const content = fs.readFileSync(cardPath, 'utf-8')
  assert.ok(content.includes('highlight-card-commonplace'), 'Deve conter classe de ficha literária commonplace')
  assert.ok(content.includes('editorial-quote'), 'Deve conter classe de citação editorial')
  assert.ok(content.includes('editorial-quote-mark'), 'Deve conter aspas editoriais estilizadas')
  assert.ok(content.includes('reader-note-box'), 'Deve conter bloco subordinado de anotação de estudo')
  assert.ok(content.includes('reader-note-content'), 'Deve conter conteúdo de reflexão do leitor')
  assert.ok(content.includes('context-book-link'), 'Deve conter link direto para o acervo da obra')

  // Zero emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'HighlightCard.vue não deve conter emojis')
})

test('US1/US2: Categorias semânticas de grifo estão registradas com intenções de estudo cognitivas', () => {
  assert.equal(HIGHLIGHT_SEMANTIC_CATEGORIES.yellow.semanticName, 'Ideia Central')
  assert.equal(HIGHLIGHT_SEMANTIC_CATEGORIES.green.semanticName, 'Citação-chave')
  assert.equal(HIGHLIGHT_SEMANTIC_CATEGORIES.blue.semanticName, 'Dúvida')
  assert.equal(HIGHLIGHT_SEMANTIC_CATEGORIES.pink.semanticName, 'Refutação')
  assert.equal(HIGHLIGHT_SEMANTIC_CATEGORIES.purple.semanticName, 'Síntese')

  assert.ok(HIGHLIGHT_SEMANTIC_CATEGORIES.yellow.description.length > 0)
  assert.ok(HIGHLIGHT_SEMANTIC_CATEGORIES.green.description.length > 0)
})

test('US2: HighlightFilterToolbar consome categorias semânticas com acessibilidade e sem cores estáticas', () => {
  const toolbarPath = path.resolve(srcDir, 'components/highlights/HighlightFilterToolbar.vue')
  assert.ok(fs.existsSync(toolbarPath), 'HighlightFilterToolbar.vue deve existir')

  const content = fs.readFileSync(toolbarPath, 'utf-8')
  assert.ok(content.includes('category-pills'), 'Deve conter contêiner de pílulas semânticas')
  assert.ok(content.includes('pill-category'), 'Deve conter classe de pílula por categoria')
  assert.ok(content.includes('cat.semanticName'), 'Deve exibir nome da intenção intelectual')
  assert.ok(content.includes(':aria-label="`Filtrar por ${cat.semanticName}'), 'Deve conter aria-label descritivo')
  assert.ok(content.includes('role="group"'), 'Deve possuir agrupamento semântico acessível')

  // Não deve conter os hexadecimais de erro ou swatches estáticos
  assert.ok(!content.includes('#fef2f2'), 'Não deve conter fundo vermelho rígido #fef2f2')
  assert.ok(!content.includes('#991b1b'), 'Não deve conter texto vermelho rígido #991b1b')

  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'HighlightFilterToolbar.vue não deve conter emojis')
})

test('US3: HighlightCard integra ação de cópia contextual multiformato e emissão de evento', () => {
  const cardPath = path.resolve(srcDir, 'components/highlights/HighlightCard.vue')
  const content = fs.readFileSync(cardPath, 'utf-8')

  assert.ok(content.includes('handleCopyCitation'), 'Deve conter função de cópia multiformato')
  assert.ok(content.includes('formatCitationABNT'), 'Deve utilizar formatador ABNT')
  assert.ok(content.includes('formatCitationMarkdown'), 'Deve utilizar formatador Markdown')
  assert.ok(content.includes('btn-copy-quote'), 'Deve conter botão de ação de cópia')
  assert.ok(content.includes('btn-copy-dropdown-trigger'), 'Deve conter gatilho para menu de formatos')
  assert.ok(content.includes("emit('copied',"), 'Deve emitir evento copied para feedback integrado')
  assert.ok(content.includes('isCopied'), 'Deve conter estado reativo de microfeedback no botão')
})

test('US4: HighlightCard suporta truncamento de 260 chars e confirmação defensiva de exclusão', () => {
  const cardPath = path.resolve(srcDir, 'components/highlights/HighlightCard.vue')
  const content = fs.readFileSync(cardPath, 'utf-8')

  assert.ok(content.includes('maxLength = 260'), 'Deve definir truncamento defensivo em 260 caracteres')
  assert.ok(content.includes('btn-toggle-expand'), 'Deve conter botão de expandir contexto')
  assert.ok(content.includes('delete-confirmation-banner'), 'Deve conter banner de confirmação de exclusão')
  assert.ok(content.includes('btn-confirm-delete'), 'Deve conter botão para confirmar exclusão')
  assert.ok(content.includes('btn-cancel-delete'), 'Deve conter botão para cancelar exclusão')
})

test('US5: ErrorNoticeCard existe e HighlightsLibraryView baniu o antigo notice-error', () => {
  const errorCardPath = path.resolve(srcDir, 'components/ui/ErrorNoticeCard.vue')
  assert.ok(fs.existsSync(errorCardPath), 'ErrorNoticeCard.vue deve existir')

  const errorCardContent = fs.readFileSync(errorCardPath, 'utf-8')
  assert.ok(errorCardContent.includes('role="alert"'), 'ErrorNoticeCard deve ter role alert')
  assert.ok(errorCardContent.includes('btn-error-retry'), 'ErrorNoticeCard deve conter botão de tentar novamente')
  assert.ok(errorCardContent.includes(':focus-visible'), 'ErrorNoticeCard deve ter foco acessível')

  const viewPath = path.resolve(srcDir, 'views/HighlightsLibraryView.vue')
  const viewContent = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(viewContent.includes('ErrorNoticeCard'), 'HighlightsLibraryView deve renderizar ErrorNoticeCard')
  assert.ok(!viewContent.includes('.notice-error {'), 'HighlightsLibraryView não deve conter estilos legados de .notice-error')
  assert.ok(!viewContent.includes('#fef2f2'), 'HighlightsLibraryView não deve conter #fef2f2')
  assert.ok(!viewContent.includes('#991b1b'), 'HighlightsLibraryView não deve conter #991b1b')
  assert.ok(viewContent.includes('study-micro-toast'), 'HighlightsLibraryView deve conter micro-toast de feedback')
  assert.ok(viewContent.includes('handleHighlightCopied'), 'HighlightsLibraryView deve tratar cópia de citação')

  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(errorCardContent), 'ErrorNoticeCard não deve conter emojis')
  assert.ok(!emojiRegex.test(viewContent), 'HighlightsLibraryView não deve conter emojis')
})
