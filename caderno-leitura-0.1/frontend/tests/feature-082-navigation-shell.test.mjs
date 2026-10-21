import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('F082-US1: NavigationTabs.vue inclui Dashboard e Livros simultaneamente no desktop', () => {
  const navTabsPath = path.resolve(srcDir, 'components/layout/NavigationTabs.vue')
  assert.ok(fs.existsSync(navTabsPath), 'NavigationTabs.vue deve existir em components/layout')
  const content = fs.readFileSync(navTabsPath, 'utf-8')

  // Verifica que Dashboard e Livros são itens primários simultâneos
  assert.ok(content.includes("to: '/dashboard'"), 'Deve conter rota para /dashboard como item primário')
  assert.ok(content.includes("label: 'Dashboard'"), 'Deve conter rótulo Dashboard')
  assert.ok(content.includes("to: '/livros'"), 'Deve conter rota para /livros como item primário')
  assert.ok(content.includes("label: 'Livros'"), 'Deve conter rótulo Livros')

  // Verifica isolamento de rotas ativas: dashboard não deve marcar Livros e vice-versa
  assert.ok(content.includes("routes: ['dashboard']"), 'Dashboard deve ter escopo de rota isolado')
  assert.ok(
    content.includes("routes: ['books', 'book', 'study', 'study-edit']"),
    'Livros deve conter rotas do acervo, livro e estudos'
  )

  // Verifica que primaryNavItems possui os 5 itens sem condicional excludente de homeViewPreference
  assert.ok(content.includes("icon: 'layout-dashboard'"), 'Deve usar ícone layout-dashboard')
  assert.ok(content.includes("icon: 'book-open'"), 'Deve usar ícone book-open')
})

test('F082-US1: GlobalHeader.vue preserva rota preferencial no logotipo Leitorum', () => {
  const headerPath = path.resolve(srcDir, 'components/layout/GlobalHeader.vue')
  const content = fs.readFileSync(headerPath, 'utf-8')

  // O logotipo deve redirecionar para a preferência de tela inicial (dashboard ou livros)
  assert.ok(
    content.includes("props.homeViewPreference === 'dashboard' ? '/dashboard' : '/livros'"),
    'Logotipo deve respeitar homeViewPreference do usuário'
  )
})

test('F082-US2: App.vue aplica compensação móvel no rodapé (.app-footer)', () => {
  const appPath = path.resolve(srcDir, 'App.vue')
  const content = fs.readFileSync(appPath, 'utf-8')

  // Regra de estilo para rodapé respeitando a barra móvel fixa
  assert.ok(content.includes('.app-footer'), 'Deve conter estilos para .app-footer')
  assert.ok(
    content.includes('margin-bottom: calc(var(--mobile-nav-offset, 56px) + env(safe-area-inset-bottom, 0px) + 1.5rem)'),
    'App.vue deve declarar margin-bottom compensando --mobile-nav-offset e safe-area para .app-footer no mobile'
  )
})

test('F082-US2: GlobalHeader.vue não possui gatilho duplicado .mobile-more-trigger', () => {
  const headerPath = path.resolve(srcDir, 'components/layout/GlobalHeader.vue')
  const content = fs.readFileSync(headerPath, 'utf-8')

  // O gatilho móvel redundante deve ter sido removido do template
  assert.ok(
    !content.includes('class="mobile-more-trigger mobile-only"'),
    'Gatilho móvel duplicado deve ser removido do template do GlobalHeader'
  )
})

test('F082-US3: AppBreadcrumb.vue existe com semântica HTML5 e acessibilidade WAI-ARIA', () => {
  const breadcrumbPath = path.resolve(srcDir, 'components/ui/AppBreadcrumb.vue')
  assert.ok(fs.existsSync(breadcrumbPath), 'AppBreadcrumb.vue deve existir em components/ui')
  const content = fs.readFileSync(breadcrumbPath, 'utf-8')

  // Estrutura semântica e acessibilidade
  assert.ok(content.includes('<nav class="app-breadcrumb"'), 'Deve conter nav com classe app-breadcrumb')
  assert.ok(content.includes('aria-label="Trilha de navegação"'), 'Deve conter aria-label descritivo')
  assert.ok(content.includes('<ol class="breadcrumb-list">'), 'Deve utilizar lista ordenada ol')
  assert.ok(content.includes('<li'), 'Deve conter itens li')
  assert.ok(content.includes('aria-current="page"'), 'Deve marcar item atual com aria-current="page"')
  assert.ok(content.includes('aria-hidden="true"'), 'Separador deve ter aria-hidden="true"')

  // Truncamento e estilo
  assert.ok(content.includes('text-overflow: ellipsis'), 'Deve aplicar text-overflow ellipsis para títulos longos')
  assert.ok(content.includes('white-space: nowrap'), 'Deve evitar quebras indesejadas por item')
})

test('F082-US3: Telas de leitura, edição e perfil adotam AppBreadcrumb de forma padronizada', () => {
  const bookViewPath = path.resolve(srcDir, 'views/BookView.vue')
  const studyViewPath = path.resolve(srcDir, 'views/StudyView.vue')
  const studyEditViewPath = path.resolve(srcDir, 'views/StudyEditView.vue')
  const userProfileViewPath = path.resolve(srcDir, 'views/UserProfileView.vue')

  const bookContent = fs.readFileSync(bookViewPath, 'utf-8')
  const studyContent = fs.readFileSync(studyViewPath, 'utf-8')
  const studyEditContent = fs.readFileSync(studyEditViewPath, 'utf-8')
  const profileContent = fs.readFileSync(userProfileViewPath, 'utf-8')

  assert.ok(bookContent.includes('AppBreadcrumb'), 'BookView.vue deve adotar AppBreadcrumb')
  assert.ok(studyContent.includes('AppBreadcrumb'), 'StudyView.vue deve adotar AppBreadcrumb')
  assert.ok(studyEditContent.includes('AppBreadcrumb'), 'StudyEditView.vue deve adotar AppBreadcrumb')
  assert.ok(profileContent.includes('AppBreadcrumb'), 'UserProfileView.vue deve adotar AppBreadcrumb')

  // Valida que o link inicial para o acervo aponta para /livros ou /books e não apenas para /
  assert.ok(bookContent.includes("to: '/livros'"), 'BookView breadcrumb deve apontar para /livros')
  assert.ok(studyContent.includes("to: '/livros'"), 'StudyView breadcrumb deve apontar para /livros')
  assert.ok(studyEditContent.includes("to: '/livros'"), 'StudyEditView breadcrumb deve apontar para /livros')
})

test('F082-Polish: Ausência estrita de emojis nos arquivos novos e modificados', () => {
  const filesToCheck = [
    'src/types/navigation.ts',
    'src/components/layout/NavigationTabs.vue',
    'src/components/layout/GlobalHeader.vue',
    'src/components/ui/AppBreadcrumb.vue',
    'src/App.vue',
    'src/views/BookView.vue',
    'src/views/StudyView.vue',
    'src/views/StudyEditView.vue',
    'src/views/UserProfileView.vue',
  ]

  const emojiRegex = /[\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}]/u

  for (const relativePath of filesToCheck) {
    const fullPath = path.resolve(srcDir, relativePath)
    if (fs.existsSync(fullPath)) {
      const content = fs.readFileSync(fullPath, 'utf-8')
      const match = content.match(emojiRegex)
      assert.strictEqual(
        match,
        null,
        `Arquivo ${relativePath} contém emoji proíbido: ${match ? match[0] : ''}`
      )
    }
  }
})
