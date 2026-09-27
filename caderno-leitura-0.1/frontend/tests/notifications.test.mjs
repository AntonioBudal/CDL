import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('validação de tipos e contratos de notificações em types/notifications.ts', () => {
  const typesContent = fs.readFileSync(
    path.resolve(srcDir, 'types/notifications.ts'),
    'utf-8',
  )

  // Tipos de eventos
  assert.ok(
    typesContent.includes("'friend_request'"),
    'Deve incluir friend_request',
  )
  assert.ok(
    typesContent.includes("'friend_accepted'"),
    'Deve incluir friend_accepted',
  )
  assert.ok(
    typesContent.includes("'study_shared'"),
    'Deve incluir study_shared',
  )
  assert.ok(
    typesContent.includes("'system_alert'"),
    'Deve incluir system_alert',
  )

  // Interfaces
  assert.ok(
    typesContent.includes('interface NotificationItem'),
    'Deve declarar NotificationItem',
  )
  assert.ok(
    typesContent.includes('interface NotificationListResponse'),
    'Deve declarar NotificationListResponse',
  )
  assert.ok(
    typesContent.includes('interface UnreadCountResponse'),
    'Deve declarar UnreadCountResponse',
  )
  assert.ok(
    typesContent.includes('interface BroadcastNotificationRequest'),
    'Deve declarar BroadcastNotificationRequest',
  )
})

test('validação de métodos de API de notificações em api.ts e api/notifications.ts', () => {
  const apiContent = fs.readFileSync(
    path.resolve(srcDir, 'services/api.ts'),
    'utf-8',
  )
  const clientContent = fs.readFileSync(
    path.resolve(srcDir, 'api/notifications.ts'),
    'utf-8',
  )

  const methods = [
    'getNotifications',
    'getUnreadCount',
    'markAsRead',
    'markAllAsRead',
    'broadcastNotification',
    'purgeNotifications',
  ]

  for (const m of methods) {
    assert.ok(
      clientContent.includes(m),
      `api/notifications.ts deve expor ${m}`,
    )
  }

  assert.ok(
    apiContent.includes('/notifications/unread-count'),
    'api.ts deve mapear /notifications/unread-count',
  )
  assert.ok(
    apiContent.includes('/notifications/read-all'),
    'api.ts deve mapear /notifications/read-all',
  )
})

test('validação do composable useNotifications.ts', () => {
  const composableContent = fs.readFileSync(
    path.resolve(srcDir, 'composables/useNotifications.ts'),
    'utf-8',
  )

  assert.ok(
    composableContent.includes('export function useNotifications()'),
    'Deve exportar useNotifications',
  )
  assert.ok(
    composableContent.includes('startPolling'),
    'Deve implementar startPolling',
  )
  assert.ok(
    composableContent.includes('stopPolling'),
    'Deve implementar stopPolling',
  )
  assert.ok(
    composableContent.includes("window.addEventListener('focus'"),
    'Deve revalidar no foco da janela',
  )
  assert.ok(
    composableContent.includes('respondFriendRequest'),
    'Deve suportar ações rápidas de amizade',
  )
})

test('validação de acessibilidade WAI-ARIA em NotificationsDropdown.vue', () => {
  const dropdownContent = fs.readFileSync(
    path.resolve(srcDir, 'components/notifications/NotificationsDropdown.vue'),
    'utf-8',
  )

  assert.ok(
    dropdownContent.includes('role="region"'),
    'Deve possuir role="region"',
  )
  assert.ok(
    dropdownContent.includes('aria-label='),
    'Deve possuir aria-label descritivo',
  )
  assert.ok(
    dropdownContent.includes("event.key === 'Escape'"),
    'Deve fechar com a tecla Escape',
  )
  assert.ok(
    dropdownContent.includes('handleClickOutside'),
    'Deve fechar ao clicar fora',
  )
  assert.ok(
    dropdownContent.includes(':aria-busy="loading"'),
    'Deve indicar estado de carregamento acessível',
  )
})

test('validação de ações inline e feedback em NotificationItem.vue', () => {
  const itemContent = fs.readFileSync(
    path.resolve(srcDir, 'components/notifications/NotificationItem.vue'),
    'utf-8',
  )

  assert.ok(
    itemContent.includes('role="article"'),
    'Deve possuir role="article"',
  )
  assert.ok(
    itemContent.includes('handleAcceptFriend'),
    'Deve implementar handleAcceptFriend',
  )
  assert.ok(
    itemContent.includes('handleRejectFriend'),
    'Deve implementar handleRejectFriend',
  )
  assert.ok(
    itemContent.includes('inline-feedback-msg'),
    'Deve exibir mensagem de feedback inline sem remoção abrupta do card',
  )
})

test('validação do botão de notificações no cabeçalho em App.vue', () => {
  const appContent = fs.readFileSync(
    path.resolve(srcDir, 'App.vue'),
    'utf-8',
  )

  assert.ok(
    appContent.includes('notifications-nav-container'),
    'Deve conter container de notificações',
  )
  assert.ok(
    appContent.includes('btn-notifications-trigger'),
    'Deve conter botão de disparo de notificações',
  )
  assert.ok(
    appContent.includes('notifications-badge'),
    'Deve conter badge dinâmico de contagem',
  )
  assert.ok(
    appContent.includes('NotificationsDropdown'),
    'Deve incluir o componente NotificationsDropdown',
  )
  assert.ok(
    appContent.includes('notificationsService.startPolling(45000)'),
    'Deve iniciar polling de 45s quando autenticado',
  )
})
