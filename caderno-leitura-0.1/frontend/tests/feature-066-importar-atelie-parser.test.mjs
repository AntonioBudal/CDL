import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { formatMarkdown } from '../src/utils/markdownFormatter.ts'

const srcDir = path.resolve(process.cwd(), 'src')

test('US1/US2: markdownFormatter suporta formatação de tabela com template de colunas', () => {
  const result = formatMarkdown('Texto base', 0, 0, 'table')
  assert.ok(result.newText.includes('| Coluna 1 | Coluna 2 |'), 'Deve conter cabeçalho da tabela')
  assert.ok(result.newText.includes('| --- | --- |'), 'Deve conter separador Markdown da tabela')
  assert.ok(result.newText.includes('| Item 1 | Item 2 |'), 'Deve conter linha de exemplo')
})

test('US1: StudioViewModeToggle possui 3 modos de visualização acessíveis sem emojis', () => {
  const togglePath = path.resolve(srcDir, 'components/studies/StudioViewModeToggle.vue')
  assert.ok(fs.existsSync(togglePath), 'StudioViewModeToggle.vue deve existir')

  const content = fs.readFileSync(togglePath, 'utf-8')
  assert.ok(content.includes('Dividido'), 'Deve conter botão de modo Dividido')
  assert.ok(content.includes('Fonte'), 'Deve conter botão de modo Fonte')
  assert.ok(content.includes('Prévia'), 'Deve conter botão de modo Prévia')
  assert.ok(content.includes(':aria-pressed'), 'Deve conter aria-pressed para acessibilidade')

  // Sem emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'StudioViewModeToggle não deve conter emojis')
})

test('US2: FloatingMarkdownToolbar define ações de formatação, atalhos e fechamento no Escape', () => {
  const toolbarPath = path.resolve(srcDir, 'components/studies/FloatingMarkdownToolbar.vue')
  assert.ok(fs.existsSync(toolbarPath), 'FloatingMarkdownToolbar.vue deve existir')

  const content = fs.readFileSync(toolbarPath, 'utf-8')
  assert.ok(content.includes("handleFormat('bold')"), 'Deve suportar Negrito')
  assert.ok(content.includes("handleFormat('italic')"), 'Deve suportar Itálico')
  assert.ok(content.includes("handleFormat('heading')"), 'Deve suportar Título H3')
  assert.ok(content.includes("handleFormat('table')"), 'Deve suportar Tabela')
  assert.ok(content.includes("handleFormat('code')"), 'Deve suportar Código')
  assert.ok(content.includes("handleFormat('link')"), 'Deve suportar Link')
  assert.ok(content.includes("e.key === 'Escape'"), 'Deve fechar ao pressionar Escape')
  assert.ok(content.includes('role="toolbar"'), 'Deve possuir role="toolbar"')

  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'FloatingMarkdownToolbar não deve conter emojis')
})

test('US1/US3: ImportView implementa o layout Two-Pane Studio com faixa compacta e contadores', () => {
  const importViewPath = path.resolve(srcDir, 'views/ImportView.vue')
  const content = fs.readFileSync(importViewPath, 'utf-8')

  assert.ok(content.includes('import-top-bar'), 'Deve possuir faixa superior compacta de metadados')
  assert.ok(content.includes('import-studio-workspace'), 'Deve possuir contêiner mestre Two-Pane Studio')
  assert.ok(content.includes('source-pane'), 'Deve possuir painel de edição da fonte à esquerda')
  assert.ok(content.includes('preview-pane'), 'Deve possuir painel de prévia estruturada à direita')
  assert.ok(content.includes('StudioViewModeToggle'), 'Deve integrar seletor de modo de visualização')
  assert.ok(content.includes('FloatingMarkdownToolbar'), 'Deve integrar barra de ferramentas flutuante')
  assert.ok(content.includes('wordCount'), 'Deve calcular contagem dinâmica de palavras')
  assert.ok(content.includes('charCount'), 'Deve calcular contagem dinâmica de caracteres')
  assert.ok(content.includes('sectionPulse'), 'Deve disparar pulso luminoso na detecção estrutural')
  assert.ok(content.includes('mobile-studio-tabs'), 'Deve possuir abas responsivas para telas compactas')
})

test('US1: Preservação de contratos funcionais em ImportView (promoção do Inbox e ações rápidas)', () => {
  const importViewPath = path.resolve(srcDir, 'views/ImportView.vue')
  const content = fs.readFileSync(importViewPath, 'utf-8')

  assert.ok(content.includes('promote_inbox_id'), 'Deve tratar parâmetro de promoção do Inbox')
  assert.ok(content.includes('assignUnassignedToSection'), 'Deve permitir atribuir texto residual com 1 clique')
  assert.ok(content.includes('saved-panel'), 'Deve manter tela de salvamento concluído')
  assert.ok(content.includes('SECTION_LABELS'), 'Deve mapear as 4 seções estruturadas canônicas')
})

test('US3/US4: style.css inclui regras do Ateliê Two-Pane Studio e pulso luminoso com reduced motion', () => {
  const stylePath = path.resolve(srcDir, 'style.css')
  const content = fs.readFileSync(stylePath, 'utf-8')

  assert.ok(content.includes('.import-studio-workspace'), 'Deve conter regra CSS para .import-studio-workspace')
  assert.ok(content.includes('@keyframes section-pulse'), 'Deve definir keyframes section-pulse')
  assert.ok(content.includes('.is-source-only'), 'Deve suportar classe .is-source-only')
  assert.ok(content.includes('.is-preview-only'), 'Deve suportar classe .is-preview-only')
  assert.ok(content.includes('prefers-reduced-motion'), 'Deve neutralizar animações com prefers-reduced-motion')
})
