import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('validação de tipos e contratos de compartilhamento no frontend', () => {
  const typesContent = fs.readFileSync(
    path.resolve(srcDir, 'types/sharing.ts'),
    'utf-8'
  )

  // Modos de visibilidade
  assert.ok(typesContent.includes("'inherit' | 'private' | 'friends' | 'custom' | 'public'"), 'ResourceVisibility deve incluir os 5 modos canônicos')
  assert.ok(typesContent.includes("'private' | 'friends' | 'public'"), 'BookVisibility deve incluir os 3 modos de livro')

  // Interfaces principais
  assert.ok(typesContent.includes('interface ResourceOwnerSummary'), 'Deve declarar ResourceOwnerSummary')
  assert.ok(typesContent.includes('interface ResourcePermissionItem'), 'Deve declarar ResourcePermissionItem')
  assert.ok(typesContent.includes('interface ResourcePermissionsRead'), 'Deve declarar ResourcePermissionsRead')
  assert.ok(typesContent.includes('interface SharedStudySummary'), 'Deve declarar SharedStudySummary')
  assert.ok(typesContent.includes('interface SharedBookSummary'), 'Deve declarar SharedBookSummary')
  assert.ok(typesContent.includes('interface SharedStudiesResponse'), 'Deve declarar SharedStudiesResponse')
})

test('validação de métodos de API de compartilhamento em api.ts e sharing.ts', () => {
  const apiContent = fs.readFileSync(
    path.resolve(srcDir, 'services/api.ts'),
    'utf-8'
  )
  const wrapperContent = fs.readFileSync(
    path.resolve(srcDir, 'api/sharing.ts'),
    'utf-8'
  )

  const methods = [
    'updateStudyVisibility',
    'updateBookVisibility',
    'getStudyPermissions',
    'grantStudyPermission',
    'revokeStudyPermission',
    'getSharedStudies',
    'getSharedBooks',
  ]

  for (const method of methods) {
    assert.ok(apiContent.includes(method), `api.ts deve declarar ${method}`)
    assert.ok(wrapperContent.includes(method), `sharingApi deve expor ${method}`)
  }
})

test('validação de acessibilidade WAI-ARIA e ergonomia tátil em ShareModal.vue', () => {
  const modalContent = fs.readFileSync(
    path.resolve(srcDir, 'components/sharing/ShareModal.vue'),
    'utf-8'
  )

  // Diálogo modal acessível
  assert.ok(modalContent.includes('role="dialog"'), 'ShareModal deve ter role="dialog"')
  assert.ok(modalContent.includes('aria-modal="true"'), 'ShareModal deve ter aria-modal="true"')
  assert.ok(modalContent.includes('aria-labelledby="share-modal-title"'), 'ShareModal deve vincular título com aria-labelledby')
  assert.ok(modalContent.includes('id="share-modal-title"'), 'ShareModal deve ter título identificado')

  // Grupo de opções de visibilidade
  assert.ok(modalContent.includes('role="radiogroup"'), 'Opções de visibilidade devem ser agrupadas com role="radiogroup"')
  assert.ok(modalContent.includes('aria-label='), 'Radiogroup deve ter aria-label')

  // Alvos táteis móveis mínimos de 44px
  assert.ok(modalContent.includes('w-11 h-11') || modalContent.includes('min-h-[44px]'), 'Botão de fechar ou botões de ação devem ter pelo menos 44px')
  assert.ok(modalContent.includes('min-h-[44px]'), 'Botões e inputs devem ter min-h-[44px]')
  assert.ok(modalContent.includes('min-w-[44px]'), 'Botão de revogação de permissão deve ter min-w-[44px]')

  // Sem emojis informais
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(modalContent), 'ShareModal não deve conter emojis informais')
})

test('validação de banner de somente leitura e controles condicionais em StudyView.vue', () => {
  const viewContent = fs.readFileSync(
    path.resolve(srcDir, 'views/StudyView.vue'),
    'utf-8'
  )

  // Banner informativo para convidados (canEdit = false)
  assert.ok(viewContent.includes('v-if="!canEdit" class="read-only-banner"'), 'StudyView deve exibir read-only-banner quando não canEdit')
  assert.ok(viewContent.includes('role="status"'), 'read-only-banner deve ter role="status"')
  assert.ok(viewContent.includes('aria-live="polite"'), 'read-only-banner deve ter aria-live="polite"')

  // Botões de escrita/mutação condicionados a canEdit
  assert.ok(viewContent.includes('v-if="canEdit"'), 'Botão de compartilhamento e edição devem verificar canEdit')
  assert.ok(viewContent.includes(':interactive="canEdit"'), 'StudyStatusBadge deve ter interatividade vinculada a canEdit')
  assert.ok(viewContent.includes(':read-only="!canEdit"'), 'StudyRelationsList deve receber prop read-only')
  assert.ok(viewContent.includes('ShareModal'), 'StudyView deve integrar componente ShareModal')

  // Sem emojis informais
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(viewContent), 'StudyView não deve conter emojis informais')
})

test('validação de abas WAI-ARIA em BooksView.vue', () => {
  const booksContent = fs.readFileSync(
    path.resolve(srcDir, 'views/BooksView.vue'),
    'utf-8'
  )

  // Abas semânticas WAI-ARIA
  assert.ok(booksContent.includes('role="tablist"'), 'BooksView deve conter tablist para alternar acervo')
  assert.ok(booksContent.includes('role="tab"'), 'Botões de aba devem ter role="tab"')
  assert.ok(booksContent.includes('role="tabpanel"'), 'Painéis de conteúdo devem ter role="tabpanel"')
  assert.ok(booksContent.includes(':aria-selected='), 'Abas devem ter aria-selected reativo')
  assert.ok(booksContent.includes('aria-controls='), 'Abas devem controlar seus respectivos painéis')

  // Componente de estudos compartilhados integrado
  assert.ok(booksContent.includes('<SharedStudiesList'), 'BooksView deve incorporar SharedStudiesList na aba compartilhados')
})

test('validação de SharedStudiesList.vue: acessibilidade e ergonomia', () => {
  const sharedListContent = fs.readFileSync(
    path.resolve(srcDir, 'components/library/SharedStudiesList.vue'),
    'utf-8'
  )

  // Estados de carregamento, erro e vazio
  assert.ok(sharedListContent.includes('role="status"'), 'Loading skeleton deve ter role="status"')
  assert.ok(sharedListContent.includes('role="alert"'), 'Mensagem de erro deve ter role="alert"')
  assert.ok(sharedListContent.includes('aria-label='), 'Campos de busca devem ter aria-label acessível')

  // Alvos táteis móveis de 44px
  assert.ok(
    sharedListContent.includes('min-h-[44px]') || sharedListContent.includes('min-height: 44px'),
    'Ações e botões devem cumprir 44px de ergonomia tátil'
  )

  // Sem emojis informais
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(sharedListContent), 'SharedStudiesList não deve conter emojis informais')
})
