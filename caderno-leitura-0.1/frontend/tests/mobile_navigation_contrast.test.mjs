import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('validação de arquitetura de navegação móvel em mobile-navigation.css', () => {
  const css = fs.readFileSync(path.resolve(srcDir, 'mobile-navigation.css'), 'utf-8')

  // RF-009: 5 colunas proporcionais na barra móvel
  assert.ok(
    css.includes('grid-template-columns: repeat(5, minmax(0, 1fr))'),
    'Barra móvel deve ter exatamente 5 colunas proporcionais'
  )

  // RF-011: Dimensões mínimas de toque de 44x44px
  assert.ok(
    css.includes('min-height: 44px') && css.includes('min-width: 44px'),
    'Alvos de toque na navegação móvel devem ter no mínimo 44x44px'
  )

  // RF-012: Classes de fita de abas com fade mask
  assert.ok(
    css.includes('.tabs-scroll-wrapper'),
    'Deve definir .tabs-scroll-wrapper'
  )
  assert.ok(
    css.includes('.tabs-scroll-content'),
    'Deve definir .tabs-scroll-content'
  )
  assert.ok(
    css.includes('linear-gradient(to right, var(--color-surface), transparent)'),
    'Deve aplicar máscara gradiente à esquerda'
  )
  assert.ok(
    css.includes('linear-gradient(to left, var(--color-surface), transparent)'),
    'Deve aplicar máscara gradiente à direita'
  )

  // RF-013: Densidade do cabeçalho em telas estreitas
  assert.ok(
    css.includes('@media (max-width: 380px)'),
    'Deve conter regras de densidade para viewports ultra estreitas (< 380px)'
  )
})

test('validação de gaveta inferior MobileMoreMenu.vue', () => {
  const menuPath = path.resolve(srcDir, 'components/navigation/MobileMoreMenu.vue')
  assert.ok(fs.existsSync(menuPath), 'MobileMoreMenu.vue deve existir em components/navigation')

  const content = fs.readFileSync(menuPath, 'utf-8')

  // RF-010: WAI-ARIA
  assert.ok(content.includes('role="dialog"'), 'Gaveta deve ter role="dialog"')
  assert.ok(content.includes('aria-modal="true"'), 'Gaveta deve ter aria-modal="true"')
  assert.ok(content.includes('aria-labelledby="mobile-more-title"'), 'Gaveta deve vincular título')

  // Destinos secundários essenciais
  assert.ok(content.includes('/lixeira'), 'Gaveta deve conter link para /lixeira')
  assert.ok(content.includes('/admin'), 'Gaveta deve conter link para /admin')
  assert.ok(content.includes('/ajustes'), 'Gaveta deve conter link para /ajustes')
  assert.ok(content.includes('Encerrar Sessão'), 'Gaveta deve conter opção de logout')

  // Fechamento tátil e por teclado
  assert.ok(content.includes("event.key === 'Escape'"), 'Gaveta deve fechar com Escape')
  assert.ok(content.includes('emit(\'close\')'), 'Gaveta deve emitir close no backdrop e nos itens')

  // RF-014: prefers-reduced-motion
  assert.ok(
    content.includes('@media (prefers-reduced-motion: reduce)'),
    'Gaveta deve respeitar prefers-reduced-motion'
  )

  // Anti-emoji
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'MobileMoreMenu não deve conter emojis')
})

test('validação de integração móvel em App.vue e MobileTabBar.vue', () => {
  const appContent = fs.readFileSync(path.resolve(srcDir, 'App.vue'), 'utf-8')
  const tabBarPath = path.resolve(srcDir, 'components/layout/MobileTabBar.vue')
  assert.ok(fs.existsSync(tabBarPath), 'MobileTabBar.vue deve existir em components/layout')
  const tabBarContent = fs.readFileSync(tabBarPath, 'utf-8')

  // Incorporação do MobileMoreMenu e MobileTabBar no App.vue
  assert.ok(appContent.includes('<MobileMoreMenu'), 'App.vue deve integrar MobileMoreMenu')
  assert.ok(appContent.includes('<MobileTabBar'), 'App.vue deve integrar MobileTabBar')

  // Botão Mais na barra móvel física (MobileTabBar.vue)
  assert.ok(tabBarContent.includes('mobile-more-trigger'), 'MobileTabBar.vue deve ter botão disparador mobile-more-trigger')
  assert.ok(tabBarContent.includes('more-horizontal'), 'Botão Mais deve utilizar ícone more-horizontal')

  // Destinos essenciais na barra móvel de 5 colunas
  assert.ok(tabBarContent.includes('/dashboard'), 'MobileTabBar.vue deve conter link para /dashboard')
  assert.ok(tabBarContent.includes('/books'), 'MobileTabBar.vue deve conter link para /books')
  assert.ok(tabBarContent.includes('/highlights'), 'MobileTabBar.vue deve conter link para /highlights')
  assert.ok(tabBarContent.includes('/review'), 'MobileTabBar.vue deve conter link para /review')
})
