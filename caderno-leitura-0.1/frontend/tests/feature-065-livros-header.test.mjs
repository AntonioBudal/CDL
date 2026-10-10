import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

// Testes da Feature 01 (Roadmap 0.8) - Curadoria Editorial, Biblioteca Ativa e Novo Header Global

test('F0.8.01 - GlobalHeader.vue estrutura 3 blocos semânticos e ferramentas', () => {
  const file = path.resolve(srcDir, 'components/layout/GlobalHeader.vue')
  assert.ok(fs.existsSync(file), 'GlobalHeader.vue deve existir em components/layout/')

  const content = fs.readFileSync(file, 'utf-8')
  assert.ok(content.includes('header-left'), 'Deve conter bloco esquerdo (marca)')
  assert.ok(content.includes('header-center'), 'Deve conter bloco central (navegação)')
  assert.ok(content.includes('header-right'), 'Deve conter bloco direito (ferramentas e usuário)')
  assert.ok(content.includes('NavigationTabs'), 'Deve integrar o componente NavigationTabs')
  assert.ok(content.includes('UserDropdown'), 'Deve integrar o componente UserDropdown')
  assert.ok(content.includes('search-trigger-btn'), 'Deve conter botão de busca rápida')
  assert.ok(content.includes('quick-capture-trigger-btn'), 'Deve conter botão de captura rápida')
  assert.ok(content.includes('SyncStatusBadge'), 'Deve conter badge de sincronização')
})

test('F0.8.01 - NavigationTabs.vue expõe 4 abas primárias e menu retrátil Mais', () => {
  const file = path.resolve(srcDir, 'components/layout/NavigationTabs.vue')
  assert.ok(fs.existsSync(file), 'NavigationTabs.vue deve existir em components/layout/')

  const content = fs.readFileSync(file, 'utf-8')
  // 4 Abas Primárias
  assert.ok(content.includes('Destaques'), 'Deve conter aba Destaques')
  assert.ok(content.includes('Revisão'), 'Deve conter aba Revisão')
  assert.ok(content.includes('Inbox'), 'Deve conter aba Inbox')

  // Menu Mais
  assert.ok(content.includes('more-dropdown-menu'), 'Deve conter dropdown menu Mais')
  assert.ok(content.includes('Importar'), 'Menu Mais deve conter Importar')
  assert.ok(content.includes('Amigos'), 'Menu Mais deve conter Amigos')
  assert.ok(content.includes('Ajustes'), 'Menu Mais deve conter Ajustes')
  assert.ok(content.includes('Lixeira'), 'Menu Mais deve conter Lixeira')
  assert.ok(content.includes('aria-expanded'), 'Menu Mais deve gerenciar aria-expanded')
})

test('F0.8.01 - UserDropdown.vue encapsula botão Sair de forma segura e acessível', () => {
  const file = path.resolve(srcDir, 'components/layout/UserDropdown.vue')
  assert.ok(fs.existsSync(file), 'UserDropdown.vue deve existir em components/layout/')

  const content = fs.readFileSync(file, 'utf-8')
  assert.ok(content.includes('user-trigger-btn'), 'Deve conter gatilho com avatar/iniciais')
  assert.ok(content.includes('user-dropdown-menu'), 'Deve conter menu suspenso do usuário')
  assert.ok(content.includes('handleLogout'), 'Deve implementar ação handleLogout')
  assert.ok(content.includes('Encerrar Sessão') || content.includes('Sair'), 'Deve conter texto de logout')
  assert.ok(content.includes('aria-haspopup="menu"'), 'Deve possuir aria-haspopup="menu"')
})

test('F0.8.01 - Drawer.vue acessível com aceleração por GPU e prefers-reduced-motion', () => {
  const file = path.resolve(srcDir, 'components/ui/Drawer.vue')
  assert.ok(fs.existsSync(file), 'Drawer.vue deve existir em components/ui/')

  const content = fs.readFileSync(file, 'utf-8')
  assert.ok(content.includes('role="dialog"'), 'Drawer deve declarar role="dialog"')
  assert.ok(content.includes('aria-modal="true"'), 'Drawer deve declarar aria-modal="true"')
  assert.ok(content.includes('drawer-backdrop'), 'Drawer deve possuir backdrop')
  assert.ok(content.includes("e.key === 'Escape'"), 'Drawer deve suportar fechamento via tecla Escape')
  assert.ok(content.includes('transform'), 'Drawer deve usar animação acelerada via transform')
  assert.ok(content.includes('prefers-reduced-motion'), 'Drawer deve ter suporte a prefers-reduced-motion')
  assert.ok(content.includes('420px'), 'Drawer deve ter largura padrão desktop de 420px')
})

test('F0.8.01 - BookHeroCard.vue implementa destaque de leitura ativa', () => {
  const file = path.resolve(srcDir, 'components/library/BookHeroCard.vue')
  assert.ok(fs.existsSync(file), 'BookHeroCard.vue deve existir em components/library/')

  const content = fs.readFileSync(file, 'utf-8')
  assert.ok(content.includes('book-hero-card'), 'Deve declarar classe .book-hero-card')
  assert.ok(content.includes('Em Andamento'), 'Deve exibir badge Em Andamento')
  assert.ok(content.includes('Continuar Leitura'), 'Deve possuir botão de ação Continuar Leitura')
  assert.ok(content.includes('BookCover'), 'Deve renderizar BookCover')
})

test('F0.8.01 - BooksView.vue opera em largura total com Drawer e sem coluna fixa de formulário', () => {
  const file = path.resolve(srcDir, 'views/BooksView.vue')
  const content = fs.readFileSync(file, 'utf-8')

  assert.ok(!content.includes('class="panel form-panel"'), 'Coluna estática de formulário foi removida do layout principal')
  assert.ok(content.includes('<Drawer'), 'BooksView deve incorporar Drawer para novo livro')
  assert.ok(content.includes('<BookHeroCard'), 'BooksView deve incorporar BookHeroCard no topo')
  assert.ok(content.includes('add-book-btn'), 'BooksView deve conter botão de adicionar livro')
  assert.ok(content.includes('isDrawerOpen'), 'BooksView deve controlar estado reativo isDrawerOpen')
})

test('F0.8.01 - Conformidade Constitucional: Ausência de emojis nos novos arquivos', () => {
  const filesToCheck = [
    'components/ui/Drawer.vue',
    'components/layout/GlobalHeader.vue',
    'components/layout/NavigationTabs.vue',
    'components/layout/UserDropdown.vue',
    'components/library/BookHeroCard.vue',
  ]

  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u

  for (const rel of filesToCheck) {
    const fullPath = path.resolve(srcDir, rel)
    assert.ok(fs.existsSync(fullPath), `Arquivo ${rel} deve existir`)
    const content = fs.readFileSync(fullPath, 'utf-8')
    assert.ok(!emojiRegex.test(content), `Arquivo ${rel} não deve conter emojis`)
  }
})
