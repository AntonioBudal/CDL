import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('F077-US1: MobileTabBar.vue possui 5 colunas simétricas, alvos táteis e safe-area', () => {
  const barPath = path.resolve(srcDir, 'components/layout/MobileTabBar.vue')
  assert.ok(fs.existsSync(barPath), 'MobileTabBar.vue deve existir em components/layout')
  const content = fs.readFileSync(barPath, 'utf-8')

  // Semântica e acessibilidade WAI-ARIA
  assert.ok(content.includes('class="mobile-tab-bar"'), 'Deve conter class="mobile-tab-bar"')
  assert.ok(content.includes('aria-label="Navegação móvel principal"'), 'Deve conter aria-label descritivo')
  assert.ok(content.includes('aria-haspopup="dialog"'), 'Botão Mais deve ter aria-haspopup="dialog"')

  // 5 colunas: Início, Livros, Destaques, Revisão e Mais
  assert.ok(content.includes('to="/dashboard"'), 'Deve conter link para /dashboard')
  assert.ok(content.includes('to="/books"'), 'Deve conter link para /books')
  assert.ok(content.includes('to="/highlights"'), 'Deve conter link para /highlights')
  assert.ok(content.includes('to="/review"'), 'Deve conter link para /review')
  assert.ok(content.includes('mobile-more-trigger'), 'Deve conter gatilho para menu Mais')

  // Alvo tátil e Safe area no estilo do componente
  assert.ok(content.includes('min-height: 44px') && content.includes('min-width: 44px'), 'Alvos de toque devem ter no mínimo 44x44px')
  assert.ok(content.includes('env(safe-area-inset-bottom'), 'Deve suportar safe-area-inset-bottom')
  assert.ok(content.includes('grid-template-columns: repeat(5, minmax(0, 1fr))'), 'Deve usar grid de 5 colunas proporcionais')
})

test('F077-US1: Integração no App.vue renderiza MobileTabBar para usuários autenticados', () => {
  const appPath = path.resolve(srcDir, 'App.vue')
  const content = fs.readFileSync(appPath, 'utf-8')

  assert.ok(content.includes("import MobileTabBar from './components/layout/MobileTabBar.vue'"), 'App.vue deve importar MobileTabBar')
  assert.ok(content.includes('<MobileTabBar'), 'App.vue deve instanciar MobileTabBar')
  assert.ok(content.includes('!route.meta?.cleanScreen'), 'MobileTabBar deve respeitar meta.cleanScreen')
  assert.ok(content.includes('auth.isAuthenticated.value'), 'MobileTabBar deve ser exibido apenas se autenticado')
  assert.ok(content.includes('@open-more="isMoreMenuOpen = true"'), 'MobileTabBar deve disparar abertura da gaveta Mais')
})

test('F077-US2: Cabeçalho superior despoluído e abas textuais ocultas em < 768px', () => {
  const navTabsPath = path.resolve(srcDir, 'components/layout/NavigationTabs.vue')
  const navTabsContent = fs.readFileSync(navTabsPath, 'utf-8')

  assert.ok(
    navTabsContent.includes('@media (max-width: 767px)') && navTabsContent.includes('display: none !important'),
    'NavigationTabs deve ser ocultado no cabeçalho em viewports < 768px'
  )

  const headerPath = path.resolve(srcDir, 'components/layout/GlobalHeader.vue')
  const headerContent = fs.readFileSync(headerPath, 'utf-8')

  assert.ok(
    headerContent.includes('@media (max-width: 767px)') && headerContent.includes('.header-center {\n    display: none !important;'),
    'GlobalHeader deve ocultar header-center em < 768px'
  )
})

test('F077-US2: MobileMoreMenu.vue expandido com rotas secundárias e badges reativos', () => {
  const menuPath = path.resolve(srcDir, 'components/navigation/MobileMoreMenu.vue')
  const content = fs.readFileSync(menuPath, 'utf-8')

  // Composables de contadores reativos
  assert.ok(content.includes('useInboxCount'), 'Deve importar useInboxCount')
  assert.ok(content.includes('useFriends'), 'Deve importar useFriends')

  // Links essenciais da gaveta
  assert.ok(content.includes('to="/inbox"'), 'Deve conter link para /inbox')
  assert.ok(content.includes('to="/amigos"'), 'Deve conter link para /amigos')
  assert.ok(content.includes('to="/importar"'), 'Deve conter link para /importar')
  assert.ok(content.includes('to="/lixeira"'), 'Deve conter link para /lixeira')
  assert.ok(content.includes('to="/ajustes"'), 'Deve conter link para /ajustes')

  // Badges numéricos
  assert.ok(content.includes('inboxCount > 0'), 'Deve exibir badge reativo para inboxCount')
  assert.ok(content.includes('pendingFriendsCount > 0'), 'Deve exibir badge reativo para solicitações de amigos')
})

test('F077-US3: Tokens de offset e elevação de elementos flutuantes inferiores', () => {
  const cssPath = path.resolve(srcDir, 'mobile-navigation.css')
  const css = fs.readFileSync(cssPath, 'utf-8')

  assert.ok(css.includes('--mobile-nav-height: 56px;'), 'Deve declarar --mobile-nav-height: 56px;')
  assert.ok(css.includes('--mobile-nav-offset:'), 'Deve declarar --mobile-nav-offset')

  // Elevação da barra de lote da lixeira
  const trashPath = path.resolve(srcDir, 'views/TrashView.vue')
  const trashContent = fs.readFileSync(trashPath, 'utf-8')
  assert.ok(
    trashContent.includes('bottom: calc(var(--mobile-nav-offset, 0px) + 0.75rem);'),
    'TrashView .trash-batch-bar deve respeitar --mobile-nav-offset'
  )

  // Elevação do FAB de Ajustes
  const settingsPath = path.resolve(srcDir, 'views/SettingsView.vue')
  const settingsContent = fs.readFileSync(settingsPath, 'utf-8')
  assert.ok(
    settingsContent.includes('bottom: calc(var(--mobile-nav-offset, 0px) + 1rem);'),
    'SettingsView .mobile-preview-fab-wrap deve respeitar --mobile-nav-offset'
  )

  // Adaptação de NotificationsDropdown para telas ultra estreitas (<= 430px)
  const notifPath = path.resolve(srcDir, 'components/notifications/NotificationsDropdown.vue')
  const notifContent = fs.readFileSync(notifPath, 'utf-8')
  assert.ok(
    notifContent.includes('@media (max-width: 430px)') && notifContent.includes('position: fixed') && notifContent.includes('left: 0.5rem'),
    'NotificationsDropdown deve ser adaptado para fluid width em telas <= 430px'
  )
})

test('F077-US4: ShareModal.vue reescrito com tokens CSS nativos sem utilitários Tailwind', () => {
  const modalPath = path.resolve(srcDir, 'components/sharing/ShareModal.vue')
  const content = fs.readFileSync(modalPath, 'utf-8')

  // Ausência de classes utilitárias típicas de Tailwind
  assert.ok(!content.includes('bg-black/60'), 'Não deve conter utilitários Tailwind (bg-black/60)')
  assert.ok(!content.includes('dark:bg-zinc-900'), 'Não deve conter utilitários Tailwind (dark:bg-zinc-900)')
  assert.ok(!content.includes('text-amber-600'), 'Não deve conter utilitários Tailwind (text-amber-600)')
  assert.ok(!content.includes('space-y-6'), 'Não deve conter utilitários Tailwind (space-y-6)')

  // Presença de classes semânticas e tokens de tema
  assert.ok(content.includes('.share-modal-backdrop'), 'Deve definir classe .share-modal-backdrop')
  assert.ok(content.includes('.share-modal-card'), 'Deve definir classe .share-modal-card')
  assert.ok(content.includes('var(--color-surface)'), 'Deve utilizar token --color-surface')
  assert.ok(content.includes('var(--color-border)'), 'Deve utilizar token --color-border')
  assert.ok(content.includes('var(--color-accent)'), 'Deve utilizar token --color-accent')
})

test('F077-US4: Purga de estilos scoped obsoletos em App.vue', () => {
  const appPath = path.resolve(srcDir, 'App.vue')
  const content = fs.readFileSync(appPath, 'utf-8')

  // Classes legadas mortas não devem existir no estilo scoped
  assert.ok(!content.includes('.user-chip {'), 'App.vue não deve conter estilo scoped morto .user-chip')
  assert.ok(!content.includes('.header-avatar-img {'), 'App.vue não deve conter estilo scoped morto .header-avatar-img')
  assert.ok(!content.includes('.quick-capture-kbd {'), 'App.vue não deve conter estilo scoped morto .quick-capture-kbd')
})

test('F077-AntiEmoji: Nenhum arquivo modificado ou criado contém emojis', () => {
  const filesToCheck = [
    'components/layout/MobileTabBar.vue',
    'components/layout/GlobalHeader.vue',
    'components/layout/NavigationTabs.vue',
    'components/navigation/MobileMoreMenu.vue',
    'components/sharing/ShareModal.vue',
    'components/notifications/NotificationsDropdown.vue',
    'mobile-navigation.css',
    'App.vue',
  ]

  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u

  for (const relativePath of filesToCheck) {
    const fullPath = path.resolve(srcDir, relativePath)
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf-8')
      assert.ok(!emojiRegex.test(content), `Arquivo ${relativePath} não deve conter emojis`)
    }
  }
})
