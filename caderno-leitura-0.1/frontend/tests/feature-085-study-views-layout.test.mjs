import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyStatusBadgePath = path.resolve('src/components/StudyStatusBadge.vue')
const studyListViewPath = path.resolve('src/components/views/StudyListView.vue')
const studyGridViewPath = path.resolve('src/components/views/StudyGridView.vue')

// ============================================================================
// 1. User Story 1 (P1) - Prevenção de Corte de Dropdown (Clipping)
// ============================================================================

test('StudyStatusBadge.vue - Limiar de abertura ascendente considera altura real e espaco relativo', () => {
  const content = fs.readFileSync(studyStatusBadgePath, 'utf-8')

  // Limiar de 210px ou comparador relativo
  assert.match(
    content,
    /opensUpward\.value\s*=\s*\(?window\.innerHeight\s*-\s*rect\.bottom\s*<\s*210/,
    'Deve verificar limiar de 210px para evitar corte inferior'
  )
  assert.match(content, /\.status-dropdown-menu\s*\{[^}]*z-index:\s*1200/s)
  assert.match(content, /\.status-dropdown-menu\.opens-upward\s*\{[^}]*bottom:\s*calc\(100%\s*\+\s*4px\)/s)
  assert.match(content, /\.study-status-badge-container\.is-open\s*\{[^}]*z-index:\s*1000/s)
})

test('StudyListView.vue - Elevacao de z-index de 1000 e overflow visible na linha com dropdown aberto', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  assert.match(content, /\.study-tabular-list\s*\{[^}]*overflow:\s*visible/s)
  assert.match(content, /\.col-status\s*\{[^}]*overflow:\s*visible/s)
  assert.match(content, /\.study-row-item:has\(\.is-open\),\s*\.study-row-item\.has-dropdown-open\s*\{[^}]*z-index:\s*1000/s)
})

test('StudyGridView.vue - Elevacao de z-index e sincronizacao de dropdown aberto nos cartoes', () => {
  const content = fs.readFileSync(studyGridViewPath, 'utf-8')

  assert.match(content, /@toggle-open/, 'StudyStatusBadge deve emitir toggle-open ou vincular manipulador')
  assert.match(
    content,
    /\.study-card:has\(\.is-open\),\s*\.study-card\.has-dropdown-open\s*\{[^}]*z-index:\s*(?:50|100)/s,
    'Cartao de estudo deve elevar z-index quando o dropdown estiver aberto'
  )
})

// ============================================================================
// 2. User Story 2 (P2) - Legibilidade do Ícone SVG de Ordenação
// ============================================================================

test('StudyListView.vue - Icone de ordenacao define stroke currentColor e fill none', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  assert.match(content, /\.sort-indicator\s*\{[^}]*stroke:\s*currentColor/s)
  assert.match(content, /\.sort-indicator\s*\{[^}]*fill:\s*none/s)
  assert.match(content, /\.sort-indicator\s*\{[^}]*color:\s*currentColor/s)
  assert.match(content, /:deep\(\.sort-indicator\s+svg\)\s*\{[^}]*stroke:\s*currentColor/s)
  assert.match(content, /:deep\(\.sort-indicator\s+svg\)\s*\{[^}]*fill:\s*none/s)
})

// ============================================================================
// 3. User Story 3 (P3) - Alinhamento Geométrico Estrito do Grid Tabular
// ============================================================================

test('StudyListView.vue - Grade de colunas padronizada e alinhamento vertical estrito', () => {
  const content = fs.readFileSync(studyListViewPath, 'utf-8')

  // Extrair regra de colunas do cabeçalho
  const headerMatch = content.match(/\.list-header-row\s*\{[^}]*grid-template-columns:\s*([^;]+);/s)
  assert.ok(headerMatch, 'list-header-row deve ter grid-template-columns')
  const headerCols = headerMatch[1].trim().replace(/\s+/g, ' ')

  // Extrair regra de colunas das linhas de dados
  const rowMatch = content.match(/\.study-row-item\s*\{[^}]*grid-template-columns:\s*([^;]+);/s)
  assert.ok(rowMatch, 'study-row-item deve ter grid-template-columns')
  const rowCols = rowMatch[1].trim().replace(/\s+/g, ' ')

  // Extrair regra de colunas do esqueleto
  const skeletonMatch = content.match(/\.skeleton-row\s*\{[^}]*grid-template-columns:\s*([^;]+);/s)
  assert.ok(skeletonMatch, 'skeleton-row deve ter grid-template-columns')
  const skeletonCols = skeletonMatch[1].trim().replace(/\s+/g, ' ')

  // As 3 linhas devem compartilhar a exata mesma malha
  assert.equal(rowCols, headerCols, 'study-row-item deve usar o mesmo grid-template-columns que list-header-row')
  assert.equal(skeletonCols, headerCols, 'skeleton-row deve usar o mesmo grid-template-columns que list-header-row')

  // Alinhamento vertical centralizado
  assert.match(content, /\.list-header-row\s*\{[^}]*align-items:\s*center/s)
  assert.match(content, /\.study-row-item\s*\{[^}]*align-items:\s*center/s)
  assert.match(content, /\.skeleton-row\s*\{[^}]*align-items:\s*center/s)

  // Centralização de seções e ações
  assert.match(content, /\.col-sections\.header-cell\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-actions\.header-cell\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-sections\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.col-actions\s*\{[^}]*justify-content:\s*center/s)
})

// ============================================================================
// 4. Conformidade de Estilo e Sem Emojis
// ============================================================================

test('Conformidade de estilo: Zero presenca de emojis nos arquivos da feature F04', () => {
  const emojiRegex = /[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

  for (const filePath of [studyStatusBadgePath, studyListViewPath, studyGridViewPath]) {
    const content = fs.readFileSync(filePath, 'utf-8')
    assert.equal(emojiRegex.test(content), false, `Arquivo ${filePath} nao deve conter emojis`)
  }
})
