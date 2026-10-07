import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('Tipos de Inbox exportados em types.ts', () => {
  const filePath = path.resolve('src/types.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('export interface InboxCapture'), 'Deve exportar interface InboxCapture')
  assert.ok(content.includes('export type InboxStatus'), 'Deve exportar tipo InboxStatus')
  assert.ok(content.includes('export interface InboxCaptureCreatePayload'), 'Deve exportar InboxCaptureCreatePayload')
  assert.ok(content.includes('export interface InboxCountResponse'), 'Deve exportar InboxCountResponse')
  assert.ok(content.includes('export interface InboxPromotePayload'), 'Deve exportar InboxPromotePayload')
  assert.ok(content.includes('export interface InboxLinkPayload'), 'Deve exportar InboxLinkPayload')
})

test('Métodos de API do Inbox declarados em api.ts', () => {
  const filePath = path.resolve('src/services/api.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('getInboxCaptures'), 'api.ts deve declarar getInboxCaptures')
  assert.ok(content.includes('getInboxCount'), 'api.ts deve declarar getInboxCount')
  assert.ok(content.includes('createInboxCapture'), 'api.ts deve declarar createInboxCapture')
  assert.ok(content.includes('updateInboxCapture'), 'api.ts deve declarar updateInboxCapture')
  assert.ok(content.includes('deleteInboxCapture'), 'api.ts deve declarar deleteInboxCapture')
  assert.ok(content.includes('promoteInboxCapture'), 'api.ts deve declarar promoteInboxCapture')
  assert.ok(content.includes('linkInboxCapture'), 'api.ts deve declarar linkInboxCapture')
})

test('Composables useInboxCount e useQuickCapture declarados corretamente', () => {
  const countPath = path.resolve('src/composables/useInboxCount.ts')
  const capturePath = path.resolve('src/composables/useQuickCapture.ts')

  assert.ok(fs.existsSync(countPath), 'useInboxCount.ts deve existir')
  assert.ok(fs.existsSync(capturePath), 'useQuickCapture.ts deve existir')

  const countContent = fs.readFileSync(countPath, 'utf-8')
  assert.ok(countContent.includes('refreshCount'), 'useInboxCount deve ter refreshCount')
  assert.ok(countContent.includes('pendingCount'), 'useInboxCount deve ter pendingCount')

  const captureContent = fs.readFileSync(capturePath, 'utf-8')
  assert.ok(captureContent.includes('submit'), 'useQuickCapture deve ter submit')
  assert.ok(captureContent.includes('open'), 'useQuickCapture deve ter open')
  assert.ok(captureContent.includes('close'), 'useQuickCapture deve ter close')
})

test('Componentes de Inbox existem e implementam funcionalidades necessárias', () => {
  const modalPath = path.resolve('src/components/inbox/QuickCaptureModal.vue')
  const cardPath = path.resolve('src/components/inbox/CaptureItemCard.vue')
  const linkModalPath = path.resolve('src/components/inbox/LinkToStudyModal.vue')
  const viewPath = path.resolve('src/views/InboxView.vue')

  assert.ok(fs.existsSync(modalPath), 'QuickCaptureModal.vue deve existir')
  assert.ok(fs.existsSync(cardPath), 'CaptureItemCard.vue deve existir')
  assert.ok(fs.existsSync(linkModalPath), 'LinkToStudyModal.vue deve existir')
  assert.ok(fs.existsSync(viewPath), 'InboxView.vue deve existir')

  const modalContent = fs.readFileSync(modalPath, 'utf-8')
  assert.ok(modalContent.includes('textarea') || modalContent.includes('content'), 'Modal deve ter campo de texto')
  assert.ok(modalContent.includes('useQuickCapture'), 'Modal deve utilizar useQuickCapture')

  const cardContent = fs.readFileSync(cardPath, 'utf-8')
  assert.ok(cardContent.includes('promote') || cardContent.includes('promover') || cardContent.includes('Promover'), 'Card deve ter opção de promover')
  assert.ok(cardContent.includes('vincular') || cardContent.includes('link') || cardContent.includes('Vincular'), 'Card deve ter opção de vincular')

  const linkModalContent = fs.readFileSync(linkModalPath, 'utf-8')
  assert.ok(linkModalContent.includes('searchStudyCandidates'), 'LinkToStudyModal deve buscar candidatos')
  assert.ok(linkModalContent.includes('linkInboxCapture'), 'LinkToStudyModal deve vincular captura')
  assert.ok(linkModalContent.includes('targetSection'), 'LinkToStudyModal deve selecionar seção alvo')

  const viewContent = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(viewContent.includes('getInboxCaptures'), 'InboxView deve chamar getInboxCaptures')
  assert.ok(viewContent.includes('activeTab'), 'InboxView deve ter controle de abas')
  assert.ok(viewContent.includes('searchQuery'), 'InboxView deve ter busca')
  assert.ok(viewContent.includes('CaptureItemCard'), 'InboxView deve renderizar CaptureItemCard')
  assert.ok(viewContent.includes('LinkToStudyModal'), 'InboxView deve renderizar LinkToStudyModal')
})

test('Rota /inbox registrada no router', () => {
  const routerPath = path.resolve('src/router/index.ts')
  const routerContent = fs.readFileSync(routerPath, 'utf-8')
  assert.ok(routerContent.includes("path: '/inbox'"), 'router deve registrar /inbox')
  assert.ok(routerContent.includes('InboxView'), 'router deve referenciar InboxView')
})

test('Fluxo de promoção integrado no ImportView', () => {
  const importPath = path.resolve('src/views/ImportView.vue')
  const importContent = fs.readFileSync(importPath, 'utf-8')
  assert.ok(importContent.includes('promote_inbox_id'), 'ImportView deve tratar query promote_inbox_id')
  assert.ok(importContent.includes('promoteInboxCapture'), 'ImportView deve invocar promoteInboxCapture ao salvar')
  assert.ok(importContent.includes('loadPromotionCapture'), 'ImportView deve carregar dados da captura')
})

