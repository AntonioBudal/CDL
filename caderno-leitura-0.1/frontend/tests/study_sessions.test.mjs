import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('Tipos de Sessões de Estudo exportados em types.ts (T003)', () => {
  const filePath = path.resolve('src/types.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('export interface StudySession'), 'Deve exportar interface StudySession')
  assert.ok(content.includes('export interface StudySessionItem'), 'Deve exportar interface StudySessionItem')
  assert.ok(content.includes('export interface StudySessionSummary'), 'Deve exportar interface StudySessionSummary')
  assert.ok(content.includes('export interface StudySessionStartPayload'), 'Deve exportar StudySessionStartPayload')
  assert.ok(content.includes('export interface StudySessionAnswerPayload'), 'Deve exportar StudySessionAnswerPayload')
  assert.ok(content.includes('export type SessionScopeType'), 'Deve exportar tipo SessionScopeType')
})

test('Métodos de API de Sessões de Estudo declarados em api.ts (T003)', () => {
  const filePath = path.resolve('src/services/api.ts')
  const content = fs.readFileSync(filePath, 'utf-8')

  assert.ok(content.includes('startStudySession'), 'api.ts deve declarar startStudySession')
  assert.ok(content.includes('answerStudySessionItem'), 'api.ts deve declarar answerStudySessionItem')
  assert.ok(content.includes('completeStudySession'), 'api.ts deve declarar completeStudySession')
  assert.ok(content.includes('interruptStudySession'), 'api.ts deve declarar interruptStudySession')
  assert.ok(content.includes('getStudySessionSummary'), 'api.ts deve declarar getStudySessionSummary')
  assert.ok(content.includes('getStudySessionsHistory'), 'api.ts deve declarar getStudySessionsHistory')
})

test('Composable useStructuredStudySession implementado em useActiveReadingSession.ts (T013)', () => {
  const filePath = path.resolve('src/composables/useActiveReadingSession.ts')
  assert.ok(fs.existsSync(filePath), 'useActiveReadingSession.ts deve existir')

  const content = fs.readFileSync(filePath, 'utf-8')
  assert.ok(content.includes('useStructuredStudySession'), 'deve exportar useStructuredStudySession')
  assert.ok(content.includes('loadSession'), 'deve conter loadSession')
  assert.ok(content.includes('revealAnswer'), 'deve conter revealAnswer')
  assert.ok(content.includes('answerCard'), 'deve conter answerCard')
  assert.ok(content.includes('interruptAndExit'), 'deve conter interruptAndExit')
  assert.ok(content.includes('handleKeydown'), 'deve conter handleKeydown com suporte a atalhos de teclado')
  assert.ok(content.includes("'1'"), 'deve responder ao atalho 1 (Fácil)')
  assert.ok(content.includes("'2'"), 'deve responder ao atalho 2 (Médio)')
  assert.ok(content.includes("'3'"), 'deve responder ao atalho 3 (Difícil)')
  assert.ok(content.includes("' '") || content.includes("'Space'"), 'deve responder ao atalho Espaço (Revelar)')
  assert.ok(content.includes("'Escape'") || content.includes("'Esc'"), 'deve responder ao atalho Esc (Sair/Interromper)')
})

test('Componentes de Sessão de Estudo existem e possuem acessibilidade e alvos táteis >= 44px (T014, T019, T026)', () => {
  const headerPath = path.resolve('src/components/session/SessionProgressHeader.vue')
  const summaryPath = path.resolve('src/components/session/SessionSummaryModal.vue')
  const viewPath = path.resolve('src/views/StudySessionView.vue')

  assert.ok(fs.existsSync(headerPath), 'SessionProgressHeader.vue deve existir')
  assert.ok(fs.existsSync(summaryPath), 'SessionSummaryModal.vue deve existir')
  assert.ok(fs.existsSync(viewPath), 'StudySessionView.vue deve existir')

  const headerContent = fs.readFileSync(headerPath, 'utf-8')
  assert.ok(headerContent.includes('role="progressbar"'), 'Header deve ter barra de progresso com role progressbar')
  assert.ok(headerContent.includes('aria-valuenow'), 'Header deve ter aria-valuenow')
  assert.ok(headerContent.includes('min-height: 44px'), 'Botões e alvos no header devem ter min-height >= 44px')

  const summaryContent = fs.readFileSync(summaryPath, 'utf-8')
  assert.ok(summaryContent.includes('role="dialog"'), 'Modal de resumo deve ter role dialog')
  assert.ok(summaryContent.includes('aria-modal="true"'), 'Modal de resumo deve ter aria-modal true')
  assert.ok(summaryContent.includes('min-height: 44px'), 'Ações do modal de resumo devem ter min-height >= 44px')
  assert.ok(summaryContent.includes('retention-distribution'), 'Modal de resumo deve exibir distribuição de retenção')

  const viewContent = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(viewContent.includes('btn-reveal'), 'View deve ter botão de revelar')
  assert.ok(viewContent.includes('btn-rating'), 'View deve ter botões de avaliação')
  assert.ok(viewContent.includes('min-height: 52px') || viewContent.includes('min-height: 64px'), 'Botões principais devem atender ergonomia')
})

test('Rota /estudo/sessao/:sessionId registrada em router/index.ts (T016)', () => {
  const routerPath = path.resolve('src/router/index.ts')
  const routerContent = fs.readFileSync(routerPath, 'utf-8')

  assert.ok(routerContent.includes('/estudo/sessao/:sessionId'), 'Router deve registrar rota de sessão de estudo')
  assert.ok(routerContent.includes('StudySessionView'), 'Router deve carregar StudySessionView')
  assert.ok(routerContent.includes('cleanScreen: true'), 'Router deve definir meta cleanScreen: true para modo tela limpa')
})

test('Central de Revisão integra gatilho de sessão estruturada e histórico retrospectivo (T016, T023)', () => {
  const reviewViewPath = path.resolve('src/views/ReviewHubView.vue')
  const content = fs.readFileSync(reviewViewPath, 'utf-8')

  assert.ok(content.includes('startStructuredSession'), 'ReviewHubView deve ter função startStructuredSession')
  assert.ok(content.includes('start-structured-btn'), 'ReviewHubView deve renderizar botão de início de sessão estruturada')
  assert.ok(content.includes('getStudySessionsHistory'), 'ReviewHubView deve consumir getStudySessionsHistory')
  assert.ok(content.includes('Histórico de Sessões'), 'ReviewHubView deve ter aba Histórico de Sessões')
  assert.ok(content.includes('history-card'), 'ReviewHubView deve renderizar cards no histórico')
})

test('Ausência absoluta de emojis nos componentes da feature F0.7.14', () => {
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  const filesToCheck = [
    'src/components/session/SessionProgressHeader.vue',
    'src/components/session/SessionSummaryModal.vue',
    'src/views/StudySessionView.vue',
    'src/composables/useActiveReadingSession.ts',
  ]

  for (const relPath of filesToCheck) {
    const fullPath = path.resolve(relPath)
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf-8')
      assert.ok(!emojiRegex.test(content), `Arquivo ${relPath} não deve conter emojis`)
    }
  }
})
