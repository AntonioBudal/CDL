import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('validação de tipos e contratos de amizade no frontend', () => {
  const typesContent = fs.readFileSync(
    path.resolve(srcDir, 'types/friendship.ts'),
    'utf-8'
  )

  // Verifica estados canônicos e perspectivas
  assert.ok(typesContent.includes("'pending' | 'accepted' | 'blocked'"), 'FriendshipStatus deve conter pending, accepted, blocked')
  assert.ok(typesContent.includes('pending_sent'), 'RelationPerspectiveStatus deve conter pending_sent')
  assert.ok(typesContent.includes('pending_received'), 'RelationPerspectiveStatus deve conter pending_received')
  assert.ok(typesContent.includes('friends'), 'RelationPerspectiveStatus deve conter friends')
  assert.ok(typesContent.includes('blocked_by_me'), 'RelationPerspectiveStatus deve conter blocked_by_me')

  // Verifica interfaces essenciais
  assert.ok(typesContent.includes('interface FriendUser'), 'Deve declarar FriendUser')
  assert.ok(typesContent.includes('interface FriendItem'), 'Deve declarar FriendItem')
  assert.ok(typesContent.includes('interface FriendRequestItem'), 'Deve declarar FriendRequestItem')
  assert.ok(typesContent.includes('interface FriendsSummary'), 'Deve declarar FriendsSummary')
  assert.ok(typesContent.includes('interface FriendshipStatusResponse'), 'Deve declarar FriendshipStatusResponse')
})

test('validação de métodos da API de amizades em api.ts e friendsApi', () => {
  const apiContent = fs.readFileSync(
    path.resolve(srcDir, 'services/api.ts'),
    'utf-8'
  )
  const wrapperContent = fs.readFileSync(
    path.resolve(srcDir, 'api/friends.ts'),
    'utf-8'
  )

  const requiredMethods = [
    'sendFriendRequest',
    'acceptFriendRequest',
    'rejectFriendRequest',
    'cancelFriendRequest',
    'removeFriend',
    'blockUser',
    'unblockUser',
    'getFriends',
    'getFriendRequests',
    'getBlockedUsers',
    'getFriendsSummary',
    'getRelationStatus',
  ]

  for (const method of requiredMethods) {
    assert.ok(apiContent.includes(method), `api.ts deve declarar ${method}`)
    assert.ok(wrapperContent.includes(method), `friendsApi deve expor ${method}`)
  }
})

test('validação do composable useFriends', () => {
  const composableContent = fs.readFileSync(
    path.resolve(srcDir, 'composables/useFriends.ts'),
    'utf-8'
  )

  assert.ok(composableContent.includes('export function useFriends()'), 'useFriends deve ser exportado')
  assert.ok(composableContent.includes('fetchSummary'), 'useFriends deve conter fetchSummary')
  assert.ok(composableContent.includes('fetchFriends'), 'useFriends deve conter fetchFriends')
  assert.ok(composableContent.includes('fetchRequests'), 'useFriends deve conter fetchRequests')
  assert.ok(composableContent.includes('fetchBlocked'), 'useFriends deve conter fetchBlocked')
  assert.ok(composableContent.includes('sendRequest'), 'useFriends deve conter sendRequest')
  assert.ok(composableContent.includes('acceptRequest'), 'useFriends deve conter acceptRequest')
  assert.ok(composableContent.includes('rejectRequest'), 'useFriends deve conter rejectRequest')
  assert.ok(composableContent.includes('cancelRequest'), 'useFriends deve conter cancelRequest')
  assert.ok(composableContent.includes('removeFriend'), 'useFriends deve conter removeFriend')
  assert.ok(composableContent.includes('blockUser'), 'useFriends deve conter blockUser')
  assert.ok(composableContent.includes('unblockUser'), 'useFriends deve conter unblockUser')
  assert.ok(composableContent.includes('getRelationStatus'), 'useFriends deve conter getRelationStatus')
})

test('validação de acessibilidade e semântica no FriendActionButtons.vue', () => {
  const componentContent = fs.readFileSync(
    path.resolve(srcDir, 'components/FriendActionButtons.vue'),
    'utf-8'
  )

  // Acessibilidade WAI-ARIA
  assert.ok(componentContent.includes(':aria-label='), 'Botões devem ter atributos aria-label dinâmicos')
  assert.ok(componentContent.includes('role="dialog"'), 'Modais de confirmação devem ter role="dialog"')
  assert.ok(componentContent.includes('aria-modal="true"'), 'Modais devem ter aria-modal="true"')

  // Alvos táteis e responsividade (mínimo 44px de altura)
  assert.ok(componentContent.includes('min-height: 44px;'), 'Botões e pills de ação devem ter min-height de 44px para toque')

  // Sem emojis nos textos institucionais
  assert.doesNotMatch(componentContent, /[\u{1F300}-\u{1F6FF}\u{1F900}-\u{1F9FF}]/u, 'Não deve conter emojis no componente')
})

test('validação de abas WAI-ARIA e nó raiz único em FriendsView.vue', () => {
  const viewContent = fs.readFileSync(
    path.resolve(srcDir, 'views/FriendsView.vue'),
    'utf-8'
  )

  // Nó raiz único sem fragmento
  assert.ok(viewContent.includes('<template>\n  <main class="friends-view wrap">'), 'Deve possuir nó raiz único <main>')

  // WAI-ARIA para abas
  assert.ok(viewContent.includes('role="tablist"'), 'Navegação deve ter role="tablist"')
  assert.ok(viewContent.includes('role="tab"'), 'Botões de abas devem ter role="tab"')
  assert.ok(viewContent.includes('role="tabpanel"'), 'Painéis devem ter role="tabpanel"')
  assert.ok(viewContent.includes(':aria-selected='), 'Abas devem alternar aria-selected')
  assert.ok(viewContent.includes('aria-controls='), 'Abas devem indicar seus respectivos aria-controls')

  // 4 abas estruturadas conforme especificação (Q2: A)
  assert.ok(viewContent.includes('Meus Amigos'), 'Deve conter aba Meus Amigos')
  assert.ok(viewContent.includes('Solicitações'), 'Deve conter aba Solicitações')
  assert.ok(viewContent.includes('Descobrir Leitores'), 'Deve conter aba Descobrir Leitores')
  assert.ok(viewContent.includes('Bloqueados'), 'Deve conter aba Bloqueados')
})

test('validação de rota /amigos e cabeçalho de navegação com crachá', () => {
  const routerContent = fs.readFileSync(
    path.resolve(srcDir, 'router/index.ts'),
    'utf-8'
  )
  const appContent = fs.readFileSync(
    path.resolve(srcDir, 'App.vue'),
    'utf-8'
  )

  // Rota registrada
  assert.ok(routerContent.includes("path: '/amigos'"), 'Router deve conter rota /amigos')
  assert.ok(routerContent.includes("FriendsView"), 'Router deve associar FriendsView')

  // Link no cabeçalho com crachá de pendências
  assert.ok(appContent.includes("to: '/amigos'"), 'App.vue deve conter link para /amigos')
  assert.ok(appContent.includes("nav-badge"), 'App.vue deve exibir nav-badge quando houver pendências')
})

test('validação de exibição de friends_count e privacidade no perfil do leitor', () => {
  const profileCardContent = fs.readFileSync(
    path.resolve(srcDir, 'components/profile/UserProfileCard.vue'),
    'utf-8'
  )

  // Exibição do contador
  assert.ok(profileCardContent.includes('profile.friends_count'), 'UserProfileCard deve exibir contagem quantitativa de amigos')
  assert.ok(profileCardContent.includes('FriendActionButtons'), 'UserProfileCard deve conter FriendActionButtons para visitantes')
})
