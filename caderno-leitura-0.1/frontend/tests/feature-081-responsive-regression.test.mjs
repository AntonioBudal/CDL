import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

function findRepoRoot(startDir) {
  let curr = startDir
  while (curr && curr !== path.dirname(curr)) {
    if (fs.existsSync(path.join(curr, 'specs', '081-regressao-responsiva'))) {
      return curr
    }
    curr = path.dirname(curr)
  }
  return path.resolve(startDir, '../../..')
}

const repoRoot = findRepoRoot(__dirname)
const specsDir = path.join(repoRoot, 'specs', '081-regressao-responsiva')

describe('Feature 081: Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade', () => {
  describe('US1: Matriz Completa de Rotas × Viewports sem Transbordamento', () => {
    it('Todas as 25 rotas nomeadas de router/index.ts constam no contrato normativo de cobertura', () => {
      const routerPath = path.join(srcDir, 'router', 'index.ts')
      const contractPath = path.join(specsDir, 'contracts', 'regression-coverage.contract.md')
      const dataModelPath = path.join(specsDir, 'data-model.md')

      assert.ok(fs.existsSync(routerPath), 'router/index.ts deve existir')
      assert.ok(fs.existsSync(contractPath), 'regression-coverage.contract.md deve existir')
      assert.ok(fs.existsSync(dataModelPath), 'data-model.md deve existir')

      const routerContent = fs.readFileSync(routerPath, 'utf-8')
      const contractContent = fs.readFileSync(contractPath, 'utf-8')
      const dataModelContent = fs.readFileSync(dataModelPath, 'utf-8')

      const routeNameRegex = /name:\s*['"]([^'"]+)['"]/g
      const matchedRoutes = []
      let match
      while ((match = routeNameRegex.exec(routerContent)) !== null) {
        matchedRoutes.push(match[1])
      }

      const uniqueRoutes = [...new Set(matchedRoutes)]
      // O router possui 24 rotas nomeadas e 1 catch-all not-found (totalizando as 25 rotas mapeadas)
      assert.ok(uniqueRoutes.length >= 24, 'Roteador deve conter pelo menos 24 rotas nomeadas')

      for (const routeName of uniqueRoutes) {
        const pattern = new RegExp(`\`${routeName}\``)
        assert.ok(
          pattern.test(contractContent),
          `Rota nomeada '${routeName}' deve estar registrada em regression-coverage.contract.md`
        )
        assert.ok(
          pattern.test(dataModelContent),
          `Rota nomeada '${routeName}' deve estar registrada em data-model.md`
        )
      }
    })

    it('Contrato normativo cobre as 8 viewports canônicas e o modo paisagem móvel com status de aprovação', () => {
      const contractPath = path.join(specsDir, 'contracts', 'regression-coverage.contract.md')
      const contractContent = fs.readFileSync(contractPath, 'utf-8')

      const requiredViewports = ['320px', '375px', '390px', '430px', '767px', '768px', '1024px', '1440px', '844×390px']
      for (const vp of requiredViewports) {
        assert.ok(
          contractContent.includes(vp),
          `Contrato de regressão deve contemplar a viewport/resolução ${vp}`
        )
      }
      assert.ok(
        contractContent.includes('scrollWidth') && contractContent.includes('clientWidth'),
        'Contrato deve formalizar o critério scrollWidth === clientWidth'
      )
    })

    it('style.css define formalmente o token --mobile-nav-offset em :root e no breakpoint móvel', () => {
      const stylePath = path.join(srcDir, 'style.css')
      const styleContent = fs.readFileSync(stylePath, 'utf-8')

      assert.match(
        styleContent,
        /--mobile-nav-offset:\s*0px/,
        'style.css deve declarar valor padrão de --mobile-nav-offset: 0px em :root'
      )
      assert.match(
        styleContent,
        /@media\s*\(\s*max-width:\s*767px\s*\)[\s\S]*?--mobile-nav-offset:\s*calc\(56px\s*\+\s*env\(safe-area-inset-bottom/,
        'style.css deve definir --mobile-nav-offset com 56px + safe-area no mobile'
      )
    })

    it('Componentes de exibição e elementos flutuantes utilizam --mobile-nav-offset', () => {
      const highlightsView = path.join(srcDir, 'views/HighlightsLibraryView.vue')
      const settingsView = path.join(srcDir, 'views/SettingsView.vue')
      const studyView = path.join(srcDir, 'views/StudyView.vue')
      const trashView = path.join(srcDir, 'views/TrashView.vue')

      const highlightsContent = fs.readFileSync(highlightsView, 'utf-8')
      const settingsContent = fs.readFileSync(settingsView, 'utf-8')
      const studyContent = fs.readFileSync(studyView, 'utf-8')
      const trashContent = fs.readFileSync(trashView, 'utf-8')

      assert.ok(highlightsContent.includes('--mobile-nav-offset'), 'HighlightsLibraryView deve usar --mobile-nav-offset')
      assert.ok(settingsContent.includes('--mobile-nav-offset'), 'SettingsView deve usar --mobile-nav-offset')
      assert.ok(studyContent.includes('--mobile-nav-offset'), 'StudyView deve usar --mobile-nav-offset')
      assert.ok(trashContent.includes('--mobile-nav-offset'), 'TrashView deve usar --mobile-nav-offset')
    })
  })

  describe('US2: Rastreabilidade e Encerramento dos 19 Problemas Auditados (P-01 a P-19)', () => {
    it('P-01 e P-02: Shell móvel possui MobileTabBar com 5 alvos e classes físicas inspecionadas', () => {
      const tabBarPath = path.join(srcDir, 'components/layout/MobileTabBar.vue')
      const appPath = path.join(srcDir, 'App.vue')

      const tabContent = fs.readFileSync(tabBarPath, 'utf-8')
      const appContent = fs.readFileSync(appPath, 'utf-8')

      assert.match(tabContent, /class="mobile-tab-bar"/, 'MobileTabBar deve conter a classe mobile-tab-bar')
      assert.match(tabContent, /repeat\(5,\s*minmax\(0,\s*1fr\)\)/, 'MobileTabBar deve ter 5 colunas')
      assert.match(appContent, /<MobileTabBar/, 'App.vue deve renderizar MobileTabBar')
    })

    it('P-03: ShareModal.vue utiliza tokens canônicos sem utilitários residuais do Tailwind', () => {
      const shareModalPath = path.join(srcDir, 'components/sharing/ShareModal.vue')
      const content = fs.readFileSync(shareModalPath, 'utf-8')

      assert.ok(!content.includes('space-y-6'), 'ShareModal não deve conter classes do Tailwind (space-y-6)')
      assert.ok(content.includes('var(--color-surface)'), 'ShareModal deve utilizar var(--color-surface)')
      assert.ok(content.includes('var(--color-border)'), 'ShareModal deve utilizar var(--color-border)')
    })

    it('P-04 a P-08: Visualizações experimentais (Map, Canvas, Tree) removidas em favor da Grade e Lista estáveis', () => {
      const bookViewPath = path.join(srcDir, 'views/BookView.vue')
      const typesPath = path.join(srcDir, 'types.ts')

      const bookViewContent = fs.readFileSync(bookViewPath, 'utf-8')
      const typesContent = fs.readFileSync(typesPath, 'utf-8')

      assert.ok(!bookViewContent.includes('StudyMapView'), 'StudyMapView não deve ser referenciado')
      assert.ok(!bookViewContent.includes('StudyCanvasView'), 'StudyCanvasView não deve ser referenciado')
      assert.ok(!bookViewContent.includes('StudyTreeView'), 'StudyTreeView não deve ser referenciado')
      assert.match(typesContent, /export type StudyViewMode = 'grid' \| 'list'/)
    })

    it('P-09: NotificationsDropdown.vue previne estouro em telas estreitas <= 430px', () => {
      const notifPath = path.join(srcDir, 'components/notifications/NotificationsDropdown.vue')
      const content = fs.readFileSync(notifPath, 'utf-8')

      assert.match(
        content,
        /@media\s*\(\s*max-width:\s*430px\s*\)[\s\S]*?\.notifications-dropdown\s*\{[^}]*max-width:\s*calc\(100vw\s*-\s*1rem\)/,
        'NotificationsDropdown deve conter contenção de largura para <= 430px'
      )
    })

    it('P-11: Limites canônicos de breakpoints consolidados (767px mobile, 768px tablet/desktop)', () => {
      const stylePath = path.join(srcDir, 'style.css')
      const content = fs.readFileSync(stylePath, 'utf-8')

      assert.match(content, /@media\s*\(\s*max-width:\s*767px\s*\)/, 'style.css deve usar max-width: 767px para mobile')
      assert.match(content, /@media\s*\(\s*max-width:\s*768px\s*\)/, 'style.css deve suportar max-width: 768px para tablet/transicao')
    })

    it('P-12: Palco de estudos declara container query study-stage', () => {
      const stylePath = path.join(srcDir, 'style.css')
      const content = fs.readFileSync(stylePath, 'utf-8')

      assert.match(content, /container-name:\s*study-stage/, 'style.css deve declarar container-name: study-stage')
      assert.match(content, /container-type:\s*inline-size/, 'style.css deve declarar container-type: inline-size')
    })

    it('P-13: App.vue expurgado de regras scoped órfãs e classes mortas', () => {
      const appPath = path.join(srcDir, 'App.vue')
      const content = fs.readFileSync(appPath, 'utf-8')

      assert.ok(!content.includes('.user-chip {'), 'App.vue não deve conter estilo scoped morto .user-chip')
      assert.ok(!content.includes('.header-avatar-img {'), 'App.vue não deve conter .header-avatar-img')
    })

    it('P-14: AdminUsersTable.vue suporta apresentação em blocos/cartões no mobile', () => {
      const adminPath = path.join(srcDir, 'components/admin/AdminUsersTable.vue')
      const content = fs.readFileSync(adminPath, 'utf-8')

      assert.match(
        content,
        /@media\s*\(\s*max-width:\s*76[78]px\s*\)/,
        'AdminUsersTable deve possuir media query para mobile'
      )
    })

    it('P-15: Grids com colunas fluidas adaptam sem estourar em 320px', () => {
      const friendsPath = path.join(srcDir, 'views/FriendsView.vue')
      const adminPath = path.join(srcDir, 'views/AdminView.vue')

      const friendsContent = fs.readFileSync(friendsPath, 'utf-8')
      const adminContent = fs.readFileSync(adminPath, 'utf-8')

      assert.doesNotMatch(friendsContent, /minmax\(280px,\s*1fr\)/, 'FriendsView deve evitar minmax estático de 280px')
      assert.doesNotMatch(adminContent, /minmax\(280px,\s*1fr\)/, 'AdminView deve evitar minmax estático de 280px')
    })

    it('P-16: Modais adotam dvh ou altura flexível para acomodar teclado virtual', () => {
      const bookEditPath = path.join(srcDir, 'components/BookEditModal.vue')
      const historyPath = path.join(srcDir, 'components/StudyHistoryModal.vue')

      const bookEditContent = fs.readFileSync(bookEditPath, 'utf-8')
      const historyContent = fs.readFileSync(historyPath, 'utf-8')

      assert.match(bookEditContent, /dvh|vh|max-height/, 'BookEditModal deve usar altura flexível')
      assert.match(historyContent, /dvh|vh|max-height/, 'StudyHistoryModal deve usar altura flexível')
    })

    it('P-17: BookView.vue possui controle de recolhimento da gaveta de capítulos', () => {
      const bookViewPath = path.join(srcDir, 'views/BookView.vue')
      const content = fs.readFileSync(bookViewPath, 'utf-8')

      assert.match(content, /leftCollapsed/, 'BookView deve controlar estado da gaveta de capítulos')
    })

    it('P-18: Efeitos de transformação hover protegidos com pointer: fine', () => {
      const stylePath = path.join(srcDir, 'style.css')
      const content = fs.readFileSync(stylePath, 'utf-8')

      assert.match(
        content,
        /@media\s*\(hover:\s*hover\)\s*and\s*\(pointer:\s*fine\)/,
        'style.css deve proteger efeitos hover com pointer: fine'
      )
    })

    it('P-19: Botões de ação em style.css possuem white-space: nowrap e flex-shrink: 0', () => {
      const stylePath = path.join(srcDir, 'style.css')
      const content = fs.readFileSync(stylePath, 'utf-8')

      assert.match(
        content,
        /button,\s*\.button\s*\{[^}]*white-space:\s*nowrap/,
        'button deve definir white-space: nowrap para evitar quebras em 2 linhas'
      )
      assert.match(
        content,
        /button,\s*\.button\s*\{[^}]*flex-shrink:\s*0/,
        'button deve definir flex-shrink: 0 para evitar esmagamento'
      )
    })
  })

  describe('US3: Alvos Táteis e Suíte de Testes-Guarda', () => {
    it('Botões e alvos móveis respeitam dimensões mínimas ergonômicas de 44x44px', () => {
      const tabBarPath = path.join(srcDir, 'components/layout/MobileTabBar.vue')
      const stylePath = path.join(srcDir, 'style.css')

      const tabContent = fs.readFileSync(tabBarPath, 'utf-8')
      const styleContent = fs.readFileSync(stylePath, 'utf-8')

      assert.match(tabContent, /min-height:\s*44px/)
      assert.match(tabContent, /min-width:\s*44px/)
      assert.match(styleContent, /min-height:\s*2\.875rem/) // 2.875rem = 46px > 44px
    })

    it('Limites canônicos de breakpoints móveis e tablet são estritamente preservados', () => {
      const globalHeaderPath = path.join(srcDir, 'components/layout/GlobalHeader.vue')
      const navTabsPath = path.join(srcDir, 'components/layout/NavigationTabs.vue')
      const mobileTabBarPath = path.join(srcDir, 'components/layout/MobileTabBar.vue')

      const headerContent = fs.readFileSync(globalHeaderPath, 'utf-8')
      const navTabsContent = fs.readFileSync(navTabsPath, 'utf-8')
      const tabContent = fs.readFileSync(mobileTabBarPath, 'utf-8')

      assert.match(headerContent, /max-width:\s*767px/)
      assert.match(navTabsContent, /max-width:\s*767px/)
      assert.match(tabContent, /max-width:\s*767px/)
    })
  })

  describe('US4: Documentação e Homologação Física', () => {
    it('quickstart.md consolida roteiro de homologação em aparelho físico sob rede local/Tailscale', () => {
      const quickstartPath = path.join(specsDir, 'quickstart.md')
      assert.ok(fs.existsSync(quickstartPath), 'quickstart.md deve existir')

      const content = fs.readFileSync(quickstartPath, 'utf-8')
      assert.ok(content.includes('Cenário 1'), 'quickstart.md deve ter Cenário 1')
      assert.ok(content.includes('Cenário 2'), 'quickstart.md deve ter Cenário 2')
      assert.ok(content.includes('Cenário 3'), 'quickstart.md deve ter Cenário 3')
      assert.ok(content.includes('Cenário 4'), 'quickstart.md deve ter Cenário 4')
      assert.ok(content.includes('Cenário 5'), 'quickstart.md deve ter Cenário 5')
      assert.ok(content.includes('iniciar.py'), 'quickstart.md deve citar iniciar.py')
    })
  })

  describe('Conformidade de Estilo: Regra Inviolável de Zero Emojis', () => {
    it('Zero caracteres emoji nos arquivos da Feature 081', () => {
      const filesToCheck = [
        path.join(specsDir, 'spec.md'),
        path.join(specsDir, 'plan.md'),
        path.join(specsDir, 'research.md'),
        path.join(specsDir, 'data-model.md'),
        path.join(specsDir, 'quickstart.md'),
        path.join(specsDir, 'contracts', 'regression-coverage.contract.md'),
        path.join(specsDir, 'checklists', 'requirements.md'),
        path.join(specsDir, 'tasks.md'),
        path.join(srcDir, 'style.css'),
        path.join(__dirname, 'feature-081-responsive-regression.test.mjs'),
      ]

      const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

      for (const file of filesToCheck) {
        if (fs.existsSync(file)) {
          const content = fs.readFileSync(file, 'utf-8')
          assert.doesNotMatch(
            content,
            emojiRegex,
            `Arquivo ${path.relative(repoRoot, file)} nao deve conter nenhum caractere emoji`
          )
        }
      }
    })
  })
})
