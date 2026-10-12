import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test('Feature 075 - Correções Visuais, de Cor e de Disposição', async (t) => {
  const srcDir = path.resolve(__dirname, '../src')
  const tokensCssPath = path.resolve(srcDir, 'tokens.css')
  const palettesCssPath = path.resolve(srcDir, 'palettes.css')
  const appearanceCssPath = path.resolve(srcDir, 'appearance-advanced.css')
  const bookCoverPath = path.resolve(srcDir, 'components/BookCover.vue')
  const categoryBadgePath = path.resolve(srcDir, 'components/CategoryBadge.vue')
  const booksViewPath = path.resolve(srcDir, 'views/BooksView.vue')
  const libraryToolbarPath = path.resolve(srcDir, 'components/LibraryToolbar.vue')
  const studyStatusBadgePath = path.resolve(srcDir, 'components/StudyStatusBadge.vue')
  const studyListViewPath = path.resolve(srcDir, 'components/views/StudyListView.vue')
  const appFooterPath = path.resolve(srcDir, 'components/layout/AppFooter.vue')
  const userDropdownPath = path.resolve(srcDir, 'components/layout/UserDropdown.vue')
  const emptyStatePath = path.resolve(srcDir, 'components/ui/EmptyState.vue')
  const friendsViewPath = path.resolve(srcDir, 'views/FriendsView.vue')
  const publicFooterPath = path.resolve(srcDir, 'components/landing/PublicFooter.vue')
  const supportViewPath = path.resolve(srcDir, 'views/SupportView.vue')
  const useVisitorThemePath = path.resolve(srcDir, 'composables/useVisitorTheme.ts')

  await t.test('1. [Setup/Foundational & US1] Integridade da Camada de Compatibilidade de Tokens CSS', () => {
    assert.ok(fs.existsSync(tokensCssPath), 'tokens.css deve existir')
    assert.ok(fs.existsSync(palettesCssPath), 'palettes.css deve existir')

    const tokensCss = fs.readFileSync(tokensCssPath, 'utf-8')
    const palettesCss = fs.readFileSync(palettesCssPath, 'utf-8')

    // Coletar variáveis declaradas
    const definedVars = new Set()
    const declRegex = /(--[a-zA-Z0-9_-]+)\s*:/g
    let m
    while ((m = declRegex.exec(tokensCss)) !== null) definedVars.add(m[1])
    while ((m = declRegex.exec(palettesCss)) !== null) definedVars.add(m[1])

    // Coletar todos os arquivos .vue
    function walk(dir) {
      let results = []
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name)
        if (entry.isDirectory()) results.push(...walk(full))
        else if (entry.name.endsWith('.vue')) results.push(full)
      }
      return results
    }

    const vueFiles = walk(srcDir)
    const missingVars = new Map()
    const varUseRegex = /var\(\s*(--[a-zA-Z0-9_-]+)/g

    for (const file of vueFiles) {
      const content = fs.readFileSync(file, 'utf-8')
      while ((m = varUseRegex.exec(content)) !== null) {
        const v = m[1]
        if (!definedVars.has(v)) {
          missingVars.set(v, (missingVars.get(v) || 0) + 1)
        }
      }
    }

    const unmapped = Array.from(missingVars.entries())
    assert.strictEqual(
      unmapped.length,
      0,
      `Existem variáveis CSS indefinidas utilizadas em componentes .vue:\n${JSON.stringify(unmapped, null, 2)}`
    )
  })

  await t.test('2. [US1] EmptyState e Herança de Cores de Superfície em Temas Escuros', () => {
    assert.ok(fs.existsSync(emptyStatePath), 'EmptyState.vue deve existir')
    const content = fs.readFileSync(emptyStatePath, 'utf-8')

    // EmptyState não deve possuir fallback fixo #ffffff para superfície nem caixa branca
    assert.doesNotMatch(content, /#ffffff/, 'EmptyState não deve usar #ffffff fixo')
    assert.match(content, /var\(--color-surface\b/, 'EmptyState deve usar --color-surface')
    assert.match(content, /var\(--color-surface-soft\b/, 'EmptyState deve usar --color-surface-soft para a moldura')
  })

  await t.test('3. [US2] Livros: Grade com Auto-Fill, Miniatura de Capa, Selos e Toolbar', () => {
    const appearanceCss = fs.readFileSync(appearanceCssPath, 'utf-8')
    assert.match(
      appearanceCss,
      /:root\[data-library=['"]grid['"]\]\s*\.book-grid\s*\{[^}]*repeat\(auto-fill/,
      '.book-grid no modo grid deve usar auto-fill para alinhar à esquerda com poucos itens'
    )

    const bookCover = fs.readFileSync(bookCoverPath, 'utf-8')
    assert.match(
      bookCover,
      /v-if="size !== 'sm'"[^>]*class="placeholder-title"/,
      'BookCover deve ocultar placeholder-title quando size === "sm"'
    )

    const categoryBadge = fs.readFileSync(categoryBadgePath, 'utf-8')
    assert.match(
      categoryBadge,
      /background-color:\s*transparent/,
      'CategoryBadge deve ter fundo transparente'
    )

    const booksView = fs.readFileSync(booksViewPath, 'utf-8')
    assert.doesNotMatch(
      booksView,
      />\s*\+\s*Adicionar Livro/i,
      'BooksView não deve conter sinal "+" literal duplicado no texto do botão'
    )

    const toolbar = fs.readFileSync(libraryToolbarPath, 'utf-8')
    assert.match(
      toolbar,
      /\.view-mode-toggle\s*\{[^}]*background(-color)?:\s*transparent/i,
      'LibraryToolbar deve ter contêiner view-mode-toggle transparente'
    )
    assert.match(
      toolbar,
      /\.view-mode-toggle\s*\{[^}]*gap:\s*0\./i,
      'LibraryToolbar deve ter espaçamento visível entre botões de visualização'
    )
  })

  await t.test('4. [US3] Estudos em /livros/:id: Status e Lista', () => {
    const studyBadge = fs.readFileSync(studyStatusBadgePath, 'utf-8')
    assert.match(
      studyBadge,
      /\.badge-rascunho\s*\{[^}]*background-color:\s*transparent/i,
      'StudyStatusBadge deve ter fundo transparente para rascunho'
    )

    const studyList = fs.readFileSync(studyListViewPath, 'utf-8')
    assert.doesNotMatch(
      studyList,
      /\{\{\s*sortDirection\s*===\s*'asc'\s*\?\s*'↑'\s*:\s*'↓'\s*\}\}/,
      'StudyListView deve utilizar componentes de ícone em vez de setas ASCII no cabeçalho'
    )
  })

  await t.test('5. [US4] Layout Interno: AppFooter, UserDropdown e FriendsView Bloqueados', () => {
    const appFooter = fs.readFileSync(appFooterPath, 'utf-8')
    assert.match(
      appFooter,
      /justify-content:\s*space-between/i,
      'AppFooter deve usar space-between em desktop'
    )

    const userDropdown = fs.readFileSync(userDropdownPath, 'utf-8')
    assert.doesNotMatch(
      userDropdown,
      /<span class="user-trigger-name"/,
      'UserDropdown não deve exibir nome textual fora do avatar no botão de disparo'
    )
    assert.doesNotMatch(
      userDropdown,
      /<Icon name="chevron-down"/,
      'UserDropdown não deve exibir chevron no botão de disparo'
    )

    const friendsView = fs.readFileSync(friendsViewPath, 'utf-8')
    assert.match(
      friendsView,
      /<EmptyState[^>]*icon="ban"/,
      'FriendsView deve usar componente EmptyState padronizado na aba de bloqueados'
    )
  })

  await t.test('6. [US5] Páginas Públicas: Link Código Aberto, Apoio e Persistência do Tema da Visita', () => {
    const publicFooter = fs.readFileSync(publicFooterPath, 'utf-8')
    assert.match(
      publicFooter,
      /https:\/\/github\.com\/AntonioBudal\/CDL/,
      'PublicFooter deve apontar para o repositório oficial https://github.com/AntonioBudal/CDL'
    )

    const supportView = fs.readFileSync(supportViewPath, 'utf-8')
    assert.match(
      supportView,
      /https:\/\/github\.com\/AntonioBudal\/CDL|Repositório de Código Aberto/i,
      'SupportView deve enfatizar apoio comunitário e código aberto'
    )

    const useVisitorTheme = fs.readFileSync(useVisitorThemePath, 'utf-8')
    assert.match(
      useVisitorTheme,
      /sessionStorage/,
      'useVisitorTheme deve persistir tema da visita em sessionStorage'
    )
    assert.doesNotMatch(
      useVisitorTheme,
      /onBeforeUnmount\(\s*\(\)\s*=>\s*\{\s*resetToOriginal\(\)\s*\}\s*\)/,
      'useVisitorTheme não deve reverter o tema da visita no onBeforeUnmount'
    )
  })
})
