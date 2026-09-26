import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('validação de tipos e contratos de administração e RBAC no frontend', () => {
  const typesContent = fs.readFileSync(
    path.resolve(srcDir, 'types/admin.ts'),
    'utf-8'
  )

  // Papéis e status
  assert.ok(typesContent.includes("'user' | 'admin'"), 'UserRole deve incluir user e admin')
  assert.ok(typesContent.includes("'ativo' | 'suspenso'"), 'UserStatus deve incluir ativo e suspenso')
  assert.ok(typesContent.includes("'local' | 'google' | 'ambos'"), 'LoginProvider deve incluir provedores válidos')

  // Interfaces principais
  assert.ok(typesContent.includes('interface AdminUserItem'), 'Deve declarar AdminUserItem')
  assert.ok(typesContent.includes('interface AdminUsersResponse'), 'Deve declarar AdminUsersResponse')
  assert.ok(typesContent.includes('interface AdminStatsSummary'), 'Deve declarar AdminStatsSummary')
  assert.ok(typesContent.includes('interface AdminSuspendRequest'), 'Deve declarar AdminSuspendRequest')
  assert.ok(typesContent.includes('interface AdminSuspendResponse'), 'Deve declarar AdminSuspendResponse')
  assert.ok(typesContent.includes('interface AdminReactivateResponse'), 'Deve declarar AdminReactivateResponse')
  assert.ok(typesContent.includes('interface AdminRoleUpdateRequest'), 'Deve declarar AdminRoleUpdateRequest')
  assert.ok(typesContent.includes('interface AdminRoleUpdateResponse'), 'Deve declarar AdminRoleUpdateResponse')
  assert.ok(typesContent.includes('interface AdminRevokeSessionsResponse'), 'Deve declarar AdminRevokeSessionsResponse')
})

test('validação de métodos de API de administração em api.ts e admin.ts', () => {
  const apiContent = fs.readFileSync(
    path.resolve(srcDir, 'services/api.ts'),
    'utf-8'
  )
  const wrapperContent = fs.readFileSync(
    path.resolve(srcDir, 'api/admin.ts'),
    'utf-8'
  )

  const methods = [
    'getAdminUsers',
    'getAdminStats',
    'suspendUser',
    'reactivateUser',
    'updateUserRole',
    'revokeAllSessions',
  ]

  for (const method of methods) {
    assert.ok(apiContent.includes(method), `api.ts deve declarar ${method}`)
  }

  const wrapperMethods = [
    'getUsers',
    'getStats',
    'suspendUser',
    'reactivateUser',
    'updateUserRole',
    'revokeAllSessions',
  ]

  for (const method of wrapperMethods) {
    assert.ok(wrapperContent.includes(method), `adminApi deve expor ${method}`)
  }
})

test('validação de acessibilidade WAI-ARIA e alvos táteis em AdminConfirmModal.vue', () => {
  const modalContent = fs.readFileSync(
    path.resolve(srcDir, 'components/admin/AdminConfirmModal.vue'),
    'utf-8'
  )

  // Diálogo modal acessível
  assert.ok(modalContent.includes('role="dialog"'), 'AdminConfirmModal deve ter role="dialog"')
  assert.ok(modalContent.includes('aria-modal="true"'), 'AdminConfirmModal deve ter aria-modal="true"')
  assert.ok(modalContent.includes('aria-labelledby="admin-confirm-title"'), 'AdminConfirmModal deve associar título via aria-labelledby')

  // Alvos táteis e botões de toque
  assert.ok(modalContent.includes('touch-button'), 'Deve aplicar classe touch-button nos botões de ação')
  assert.ok(modalContent.includes('min-height: 44px') || modalContent.includes('min-h: 44px') || modalContent.includes('44px'), 'Deve garantir altura mínima de 44px')

  // Sem emojis informais
  const emojiRegex = /[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(modalContent), 'AdminConfirmModal não deve conter emojis informais')
})

test('validação de semântica e ergonomia em AdminUsersTable.vue', () => {
  const tableContent = fs.readFileSync(
    path.resolve(srcDir, 'components/admin/AdminUsersTable.vue'),
    'utf-8'
  )

  // Semântica tabular WAI-ARIA
  assert.ok(tableContent.includes('<table'), 'Deve utilizar elemento semântico <table>')
  assert.ok(tableContent.includes('<th scope="col"'), 'Cabeçalhos devem ter scope="col"')
  assert.ok(tableContent.includes('aria-label="Tabela de usuários cadastrados"'), 'Deve rotular tabela com aria-label')

  // Alvos de toque de 44px nas ações
  assert.ok(tableContent.includes('min-height: 44px'), 'Botões de ação devem ter min-height de 44px')
  assert.ok(tableContent.includes('min-width: 44px'), 'Botões de ação devem ter min-width de 44px')

  // Rotulagem acessível dos botões para leitor de tela
  assert.ok(tableContent.includes('aria-label='), 'Botões de ação devem conter aria-label')

  // Sem emojis informais
  const emojiRegex = /[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(tableContent), 'AdminUsersTable não deve conter emojis informais')
})

test('validação de proteção de rotas e navegação condicional', () => {
  const routerContent = fs.readFileSync(
    path.resolve(srcDir, 'router/index.ts'),
    'utf-8'
  )
  const appContent = fs.readFileSync(
    path.resolve(srcDir, 'App.vue'),
    'utf-8'
  )
  const authStoreContent = fs.readFileSync(
    path.resolve(srcDir, 'stores/auth.ts'),
    'utf-8'
  )

  // Rota /admin configurada
  assert.ok(routerContent.includes("path: '/admin'"), 'Router deve definir rota /admin')
  assert.ok(routerContent.includes('requiresAdmin: true'), 'Rota /admin deve requerer papel de admin')
  assert.ok(routerContent.includes('auth.isAdmin.value'), 'Router deve validar auth.isAdmin no navigation guard')

  // Link visível exclusivamente para admins no App.vue
  assert.ok(appContent.includes("to: '/admin'"), 'App.vue deve ter link para /admin')
  assert.ok(appContent.includes('requiresAdmin: true'), 'Link deve marcar requiresAdmin')
  assert.ok(appContent.includes('!auth.isAdmin.value'), 'App.vue deve ocultar link quando não for admin')

  // Propriedade computada isAdmin no auth store
  assert.ok(authStoreContent.includes("currentUser.value?.role === 'admin'"), 'useAuthStore deve computar isAdmin a partir do role')
})
