import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('ReactivateAccountModal template e lógica de reativação', () => {
  const modalPath = path.resolve(process.cwd(), 'src/components/settings/ReactivateAccountModal.vue')
  assert.ok(fs.existsSync(modalPath), 'ReactivateAccountModal.vue deve existir')

  const content = fs.readFileSync(modalPath, 'utf-8')
  assert.ok(content.includes('Reativação de Conta'), 'Deve exibir título de reativação')
  assert.ok(content.includes('accountApi.reactivateAccount'), 'Deve chamar endpoint de reativação')
  assert.ok(content.includes("emit('reactivated'"), 'Deve emitir evento reactivated após sucesso')
  assert.ok(content.includes("emit('close')"), 'Deve emitir evento close ao cancelar')
  assert.ok(content.includes('aria-modal="true"'), 'Deve conter acessibilidade WAI-ARIA')
})

test('DeactivateAccountModal validação e desativação temporária', () => {
  const modalPath = path.resolve(process.cwd(), 'src/components/settings/DeactivateAccountModal.vue')
  assert.ok(fs.existsSync(modalPath), 'DeactivateAccountModal.vue deve existir')

  const content = fs.readFileSync(modalPath, 'utf-8')
  assert.ok(content.includes('Desativar Conta Temporariamente'), 'Deve conter cabeçalho de desativação')
  assert.ok(content.includes('warning-box'), 'Deve conter caixa de aviso sobre preservação de acervo')
  assert.ok(content.includes("emit('confirm'"), 'Deve emitir confirm com a senha')
  assert.ok(content.includes("emit('close')"), 'Deve emitir close ao cancelar')
})

test('DeleteAccountModal validação estrita com confirmação do username (LGPD)', () => {
  const modalPath = path.resolve(process.cwd(), 'src/components/settings/DeleteAccountModal.vue')
  assert.ok(fs.existsSync(modalPath), 'DeleteAccountModal.vue deve existir')

  const content = fs.readFileSync(modalPath, 'utf-8')
  assert.ok(content.includes('Excluir Conta Permanentemente'), 'Deve conter cabeçalho de exclusão definitiva')
  assert.ok(content.includes('isConfirmationValid'), 'Deve ter verificação computada do texto de confirmação')
  assert.ok(content.includes('expectedUsername'), 'Deve exigir digitação do identificador esperado')
  assert.ok(content.includes(':disabled="!isConfirmationValid'), 'Botão de confirmação deve permanecer desabilitado até texto coincidir')
  assert.ok(content.includes("emit('confirm'"), 'Deve emitir confirm com confirmation_text e password')
})

test('LoginView integra tratamento de conta desativada e modal de reativação', () => {
  const loginViewPath = path.resolve(process.cwd(), 'src/views/LoginView.vue')
  const content = fs.readFileSync(loginViewPath, 'utf-8')

  assert.ok(content.includes('ReactivateAccountModal'), 'LoginView deve importar ReactivateAccountModal')
  assert.ok(content.includes('ACCOUNT_DEACTIVATED'), 'LoginView deve interceptar erro ACCOUNT_DEACTIVATED')
  assert.ok(content.includes('account_deactivated'), 'LoginView deve verificar query param account_deactivated')
  assert.ok(content.includes('<ReactivateAccountModal'), 'LoginView deve renderizar ReactivateAccountModal')
})

test('SettingsView integra Portabilidade ZIP e Ciclo de Vida da Conta', () => {
  const settingsPath = path.resolve(process.cwd(), 'src/views/SettingsView.vue')
  const content = fs.readFileSync(settingsPath, 'utf-8')

  assert.ok(content.includes('Portabilidade e Exportação Completa'), 'SettingsView deve conter seção de portabilidade')
  assert.ok(content.includes('handleExportAcervo'), 'SettingsView deve ter handler de exportação de dados')
  assert.ok(content.includes('Ciclo de Vida da Conta'), 'SettingsView deve conter seção de ciclo de vida')
  assert.ok(content.includes('isDeactivateModalOpen'), 'SettingsView deve controlar abertura do modal de desativação')
  assert.ok(content.includes('isDeleteModalOpen'), 'SettingsView deve controlar abertura do modal de exclusão')
  assert.ok(content.includes('<DeactivateAccountModal'), 'SettingsView deve renderizar DeactivateAccountModal')
  assert.ok(content.includes('<DeleteAccountModal'), 'SettingsView deve renderizar DeleteAccountModal')
})

test('GoogleSignInButton suporta fallback redirect para OAuth 2.0 Web', () => {
  const googleBtnPath = path.resolve(process.cwd(), 'src/components/auth/GoogleSignInButton.vue')
  const content = fs.readFileSync(googleBtnPath, 'utf-8')

  assert.ok(content.includes('/api/auth/google/login'), 'Deve ter fallback de redirecionamento para login web do Google')
  assert.ok(content.includes('google-redirect-btn'), 'Deve ter botão de fallback em caso de falha no GIS')
})

test('Cliente accountApi exporta contratos requeridos para F10', () => {
  const apiPath = path.resolve(process.cwd(), 'src/api/account.ts')
  const content = fs.readFileSync(apiPath, 'utf-8')

  assert.ok(content.includes('deactivateAccount'), 'accountApi deve conter deactivateAccount')
  assert.ok(content.includes('reactivateAccount'), 'accountApi deve conter reactivateAccount')
  assert.ok(content.includes('deleteAccount'), 'accountApi deve conter deleteAccount')
  assert.ok(content.includes('exportAccountData'), 'accountApi deve conter exportAccountData')
  assert.ok(content.includes('getAuditLogs'), 'accountApi deve conter getAuditLogs')
})
