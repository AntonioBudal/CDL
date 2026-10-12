import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const studyViewPath = path.resolve('src/views/StudyView.vue')
const shareModalPath = path.resolve('src/components/sharing/ShareModal.vue')
const historyModalPath = path.resolve('src/components/StudyHistoryModal.vue')
const diffViewerPath = path.resolve('src/components/StudyDiffViewer.vue')

// ============================================================================
// 1. Cabeçalho Responsivo da Página de Estudos (StudyView.vue)
// ============================================================================

test('StudyView.vue - Cabecalho compacto no mobile com altura reduzida', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  // Estrutura principal presente
  assert.match(content, /class="page-header reader-heading"/)
  assert.match(content, /class="reader-heading-main"/)
  assert.match(content, /class="reader-title"/)
  assert.match(content, /class="reader-meta-row"/)

  // Reducao de espacamentos verticais e margens no mobile
  const mediaIdx = content.indexOf('@media (max-width: 768px)')
  assert.ok(mediaIdx !== -1, 'Media query 768px deve existir')
  const mediaBlock = content.slice(mediaIdx)

  assert.match(mediaBlock, /\.page-header\.reader-heading\s*\{[^}]*gap:\s*0\.5rem/s)
  assert.match(mediaBlock, /\.page-header\.reader-heading\s*\{[^}]*margin-bottom:\s*0\.875rem/s)
  assert.match(mediaBlock, /\.reader-meta-row\s*\{[^}]*margin-top:\s*0\.25rem/s)
})

test('StudyView.vue - Acoes de cabecalho alinhadas a esquerda e integradas no mobile', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')
  const mediaIdx = content.indexOf('@media (max-width: 768px)')
  assert.ok(mediaIdx !== -1, 'Media query 768px deve existir')
  const mediaBlock = content.slice(mediaIdx)

  // Acoes sem borda superior e sem padding-top inflado no mobile
  assert.match(mediaBlock, /\.header-actions\s*\{[^}]*justify-content:\s*flex-start/s)
  assert.match(mediaBlock, /\.header-actions\s*\{[^}]*border-top:\s*none/s)
  assert.match(mediaBlock, /\.header-actions\s*\{[^}]*padding-top:\s*0/s)

  // Divisor visual preservado sem display: none
  assert.match(mediaBlock, /\.header-actions-divider\s*\{[^}]*display:\s*block/s)

  // Acao de perigo agrupada sem margin-left: auto
  assert.match(mediaBlock, /\.header-actions\s*\.danger-action\s*\{[^}]*margin-left:\s*0/s)

  // Alvos táteis mínimos de 44x44px preservados
  assert.match(mediaBlock, /\.header-icon-btn\s*\{[^}]*min-width:\s*44px/s)
  assert.match(mediaBlock, /\.header-icon-btn\s*\{[^}]*min-height:\s*44px/s)
})

test('StudyView.vue - Preserva layout e composicao na versao desktop', () => {
  const content = fs.readFileSync(studyViewPath, 'utf-8')

  // Regra base desktop com alinhamento horizontal
  assert.match(content, /\.page-header\.reader-heading\s*\{[^}]*justify-content:\s*space-between/s)
  assert.match(content, /\.page-header\.reader-heading\s*\{[^}]*align-items:\s*flex-start/s)
  assert.match(content, /\.header-actions\s*\{[^}]*flex-wrap:\s*nowrap/s)
})

// ============================================================================
// 2. Modal de Compartilhamento Responsivo (ShareModal.vue)
// ============================================================================

test('ShareModal.vue - Opcao de visibilidade utiliza largura total sem compressao', () => {
  const content = fs.readFileSync(shareModalPath, 'utf-8')

  // Estrutura das opcoes com largura total e box-sizing
  assert.match(content, /\.share-visibility-options\s*\{[^}]*width:\s*100%/s)
  assert.match(content, /\.share-visibility-option\s*\{[^}]*width:\s*100%/s)
  assert.match(content, /\.share-visibility-option\s*\{[^}]*box-sizing:\s*border-box/s)

  // Botao radio com flex-shrink: 0 e dimensoes explicitas
  assert.match(content, /\.share-radio-input\s*\{[^}]*flex-shrink:\s*0/s)
  assert.match(content, /\.share-radio-input\s*\{[^}]*width:\s*1\.125rem/s)

  // Texto da opcao flexivel e com quebra suave
  assert.match(content, /\.share-option-text\s*\{[^}]*flex:\s*1\s*1\s*auto/s)
  assert.match(content, /\.share-option-text\s*\{[^}]*min-width:\s*0/s)
  assert.match(content, /\.share-option-label\s*\{[^}]*overflow-wrap:\s*break-word/s)
  assert.match(content, /\.share-option-desc\s*\{[^}]*overflow-wrap:\s*break-word/s)
})

test('ShareModal.vue - Input de link e botao de copiar responsivos', () => {
  const content = fs.readFileSync(shareModalPath, 'utf-8')

  assert.match(content, /\.share-input-row\s*\{[^}]*width:\s*100%/s)
  assert.match(content, /\.share-link-input\s*\{[^}]*min-width:\s*0/s)
  assert.match(content, /\.share-copy-btn\s*\{[^}]*flex-shrink:\s*0/s)
  assert.match(content, /\.share-copy-btn\s*\{[^}]*white-space:\s*nowrap/s)
})

test('ShareModal.vue - Media query mobile compacta o padding e altura do modal', () => {
  const content = fs.readFileSync(shareModalPath, 'utf-8')

  assert.match(content, /@media\s*\(\s*max-width:\s*640px\s*\)/)
  const mediaIdx = content.indexOf('@media (max-width: 640px)')
  assert.ok(mediaIdx !== -1, 'Media query 640px deve existir')
  const mediaBlock = content.slice(mediaIdx)

  assert.match(mediaBlock, /\.share-modal-backdrop\s*\{[^}]*padding:\s*0\.5rem/s)
  assert.match(mediaBlock, /\.share-modal-body\s*\{[^}]*padding:\s*1rem/s)
  assert.match(mediaBlock, /\.share-modal-card\s*\{[^}]*100dvh/s)
})

// ============================================================================
// 3. Alinhamento de Texto no Histórico de Versões
// ============================================================================

test('StudyHistoryModal.vue - Centralizacao harmoniosa de empty-state e loading no container', () => {
  const content = fs.readFileSync(historyModalPath, 'utf-8')

  // empty-state e state-loading centralizados com flexbox
  assert.match(content, /\.empty-state\s*\{[^}]*display:\s*flex/s)
  assert.match(content, /\.empty-state\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.empty-state\s*\{[^}]*align-items:\s*center/s)
  assert.match(content, /\.empty-state\s*\{[^}]*text-align:\s*center/s)
  assert.match(content, /\.empty-state\s*\{[^}]*flex:\s*1/s)

  // Botões de abas com alinhamento centralizado
  assert.match(content, /\.tab-toggle\s*button\s*\{[^}]*display:\s*inline-flex/s)
  assert.match(content, /\.tab-toggle\s*button\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.tab-toggle\s*button\s*\{[^}]*text-align:\s*center/s)

  // Badges com alinhamento centralizado
  assert.match(content, /\.current-badge\s*\{[^}]*display:\s*inline-flex/s)
  assert.match(content, /\.current-badge\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.summary-badge\s*\{[^}]*display:\s*inline-flex/s)
  assert.match(content, /\.summary-badge\s*\{[^}]*justify-content:\s*center/s)
})

test('StudyDiffViewer.vue - Secao inalterada e badges centralizados no card', () => {
  const content = fs.readFileSync(diffViewerPath, 'utf-8')

  // Texto da secao inalterada centralizado dentro do card
  assert.match(content, /\.section-diff-empty\s*\{[^}]*text-align:\s*center/s)
  assert.match(content, /\.section-diff-empty\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.section-diff-empty\s*\{[^}]*display:\s*flex/s)

  // Badge de status da secao com alinhamento centralizado
  assert.match(content, /\.section-status-badge\s*\{[^}]*display:\s*inline-flex/s)
  assert.match(content, /\.section-status-badge\s*\{[^}]*justify-content:\s*center/s)
  assert.match(content, /\.section-status-badge\s*\{[^}]*text-align:\s*center/s)
})

// ============================================================================
// 4. Conformidade de Estilo: Zero Emojis
// ============================================================================

test('Conformidade de estilo: Zero presenca de emojis nos arquivos modificados', () => {
  const files = [studyViewPath, shareModalPath, historyModalPath, diffViewerPath]
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

  for (const f of files) {
    const fileContent = fs.readFileSync(f, 'utf-8')
    assert.doesNotMatch(fileContent, emojiRegex, `Arquivo ${path.basename(f)} nao deve conter emojis`)
  }
})
