import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const palettesPath = path.resolve('src/palettes.css')
const studyStatusBadgePath = path.resolve('src/components/StudyStatusBadge.vue')
const studyListViewPath = path.resolve('src/components/views/StudyListView.vue')
const bookViewPath = path.resolve('src/views/BookView.vue')
const studyViewPath = path.resolve('src/views/StudyView.vue')

// ============================================================================
// 1. Dropdown de Status e Paletas de Cores (10 Temas com Alto Contraste)
// ============================================================================

test('Palettes.css define tokens semanticos de status para os 10 temas', () => {
  const css = fs.readFileSync(palettesPath, 'utf-8')
  const canonicalThemes = [
    'papel-fosco',
    'noite-suave',
    'cinza-neutro',
    'grafite',
    'monocromatico',
    'pergaminho',
    'e-ink',
    'solario',
    'fiorde',
    'voltagem'
  ]

  for (const theme of canonicalThemes) {
    const themeIndex = css.indexOf(`data-theme="${theme}"`)
    assert.ok(themeIndex !== -1, `Tema ${theme} deve existir em palettes.css`)
    const nextCloseBrace = css.indexOf('}', themeIndex)
    const themeSlice = css.slice(themeIndex, nextCloseBrace !== -1 ? nextCloseBrace : undefined)
    assert.match(themeSlice, /--color-status-rascunho-text:/, `Tema ${theme} deve ter --color-status-rascunho-text`)
    assert.match(themeSlice, /--color-status-estudo-text:/, `Tema ${theme} deve ter --color-status-estudo-text`)
    assert.match(themeSlice, /--color-status-revisado-text:/, `Tema ${theme} deve ter --color-status-revisado-border`)
    assert.match(themeSlice, /--color-status-concluido-text:/, `Tema ${theme} deve ter --color-status-concluido-text`)
  }
})

test('StudyStatusBadge.vue utiliza variaveis semanticas e contraste adaptativo', () => {
  const content = fs.readFileSync(studyStatusBadgePath, 'utf-8')

  // Usa tokens do tema nas classes de badge
  assert.match(content, /\.badge-rascunho\s*\{[^}]*--color-status-rascunho-text/s)
  assert.match(content, /\.badge-em-estudo\s*\{[^}]*--color-status-estudo-text/s)
  assert.match(content, /\.badge-revisado\s*\{[^}]*--color-status-revisado-text/s)
  assert.match(content, /\.badge-concluido\s*\{[^}]*--color-status-concluido-text/s)

  // Preserva fundo transparente em rascunho
  assert.match(content, /\.badge-rascunho\s*\{[^}]*background-color:\s*transparent/s)

  // Suporte a abertura para cima e z-index elevado
  assert.match(content, /opens-upward/)
  assert.match(content, /\.status-dropdown-menu\s*\{[^}]*z-index:\s*1200/s)

  // Emite evento toggle-open
  assert.match(content, /emit\('toggle-open'/)
})

// ============================================================================
// 2. Cabeçalho da Lista e Prevenção de Clipping na List View
// ============================================================================

test('StudyListView.vue - Icone de ordenacao herda cor do texto com stroke currentColor', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  assert.match(content, /\.sort-indicator\s*\{[^}]*stroke:\s*currentColor/s)
  assert.match(content, /\.sort-indicator\s*\{[^}]*color:\s*currentColor/s)
  assert.match(content, /:deep\(\.sort-indicator\s+svg\)\s*\{[^}]*stroke:\s*currentColor/s)
})

test('StudyListView.vue - Distribuicao uniforme de colunas e alinhamento do cabecalho', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  // Grade proporcional
  assert.match(content, /\.list-header-row\s*\{[^}]*grid-template-columns:/s)
  assert.match(content, /\.study-row-item\s*\{[^}]*grid-template-columns:/s)

  // Alinhamento harmonioso de colunas no cabeçalho e dados
  assert.match(content, /\.col-sections\.header-cell\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-actions\.header-cell\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-sections\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-actions\s*\{[^}]*justify-content:\s*center/s)
})

test('StudyListView.vue - Previne clipping com overflow visible e z-index em linha com dropdown aberto', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  assert.match(content, /\.study-tabular-list\s*\{[^}]*overflow:\s*visible/s)
  assert.match(content, /\.col-status\s*\{[^}]*overflow:\s*visible/s)
  assert.match(content, /\.study-row-item\.has-dropdown-open/s)
  assert.match(content, /z-index:\s*200/)
})

// ============================================================================
// 3. Compactação Mobile na Página de Livros (BookView.vue)
// ============================================================================

test('BookView.vue - Espacamento vertical compacto no mobile sem espaco em branco excessivo', () => {
  const content = fs.readFileSync(bookViewPath, 'utf-8')

  const mediaIdx = content.indexOf('@media (max-width: 768px)')
  assert.ok(mediaIdx !== -1, 'Media query 768px deve existir em BookView.vue')
  const mediaBlock = content.slice(mediaIdx)

  // Cabeçalho dos estudos compacto e alinhado no mobile
  assert.match(mediaBlock, /\.studies-header-bar\s*\{[^}]*justify-content:\s*flex-start/s)
  assert.match(mediaBlock, /\.studies-header-bar\s*\{[^}]*gap:\s*0\.5rem/s)
  assert.match(mediaBlock, /\.studies-header-bar\s*>\s*div:first-child\s*\{[^}]*flex:\s*initial/s)

  // SplitLayout e studies-area compactos sem min-height excessivo
  assert.match(mediaBlock, /\.book-split-layout\s*\{[^}]*min-height:\s*0/s)
  assert.match(mediaBlock, /\.studies-area\s*\{[^}]*height:\s*auto/s)
})

// ============================================================================
// 4. Compactação Mobile na Página de Estudos (StudyView.vue)
// ============================================================================

test('StudyView.vue - Cabecalho do estudo compacto no mobile sem vao entre status e acoes', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  const mediaIdx = content.indexOf('@media (max-width: 768px)')
  assert.ok(mediaIdx !== -1, 'Media query 768px deve existir em StudyView.vue')
  const mediaBlock = content.slice(mediaIdx)

  assert.match(mediaBlock, /\.page-header\.reader-heading\s*\{[^}]*justify-content:\s*flex-start/s)
  assert.match(mediaBlock, /\.reader-heading-main\s*\{[^}]*flex:\s*initial/s)
  assert.match(mediaBlock, /\.reader-heading-main\s*\{[^}]*margin-bottom:\s*0/s)
  assert.match(mediaBlock, /\.header-actions\s*\{[^}]*justify-content:\s*flex-start/s)
})

// ============================================================================
// 5. Conformidade de Estilo: Zero Emojis
// ============================================================================

test('Conformidade de estilo: Zero presenca de emojis em todos os arquivos modificados', () => {
  const files = [palettesPath, studyStatusBadgePath, studyListViewPath, bookViewPath, studyViewPath]
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

  for (const f of files) {
    const fileContent = fs.readFileSync(f, 'utf-8')
    assert.doesNotMatch(fileContent, emojiRegex, `Arquivo ${path.basename(f)} nao deve conter emojis`)
  }
})
