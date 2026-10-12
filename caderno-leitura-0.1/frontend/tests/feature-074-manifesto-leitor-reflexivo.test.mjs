import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test('Feature 074 - Página Inicial sem Login (SEO): Manifesto do Leitor Reflexivo', async (t) => {
  const landingViewPath = path.resolve(__dirname, '../src/views/LandingView.vue')
  const headerPath = path.resolve(__dirname, '../src/components/landing/PublicHeader.vue')
  const heroPath = path.resolve(__dirname, '../src/components/landing/HeroSection.vue')
  const simulatorPath = path.resolve(__dirname, '../src/components/landing/MethodSimulator.vue')
  const showcasePath = path.resolve(__dirname, '../src/components/landing/ThemeShowcase.vue')
  const sovereigntyPath = path.resolve(__dirname, '../src/components/landing/SovereigntySection.vue')
  const footerPath = path.resolve(__dirname, '../src/components/landing/PublicFooter.vue')
  const dataPath = path.resolve(__dirname, '../src/data/landingSimulator.ts')
  const composablePath = path.resolve(__dirname, '../src/composables/useVisitorTheme.ts')
  const fontsCssPath = path.resolve(__dirname, '../src/fonts.css')
  const palettesCssPath = path.resolve(__dirname, '../src/palettes.css')
  const settingsPath = path.resolve(__dirname, '../src/types/settings.ts')
  const indexPath = path.resolve(__dirname, '../index.html')
  const routerPath = path.resolve(__dirname, '../src/router/index.ts')

  await t.test('1. [US1] Hero Editorial, Ficha de Leitura e Cabeçalho Público', () => {
    assert.ok(fs.existsSync(headerPath), 'PublicHeader.vue deve existir')
    assert.ok(fs.existsSync(heroPath), 'HeroSection.vue deve existir')

    const header = fs.readFileSync(headerPath, 'utf-8')
    assert.match(header, /href="#conteudo-principal"/, 'Header deve ter skip-link acessível')
    assert.match(header, /href="#metodo"/, 'Header deve conter âncora para o método')
    assert.match(header, /href="#temas"/, 'Header deve conter âncora para os temas')
    assert.match(header, /href="#principios"/, 'Header deve conter âncora para os princípios')
    assert.match(header, /to="\/login"/, 'Header deve conter link para identificação')

    const hero = fs.readFileSync(heroPath, 'utf-8')
    assert.match(hero, /Ler devagar é uma forma de pensar/, 'Hero deve conter o título editorial')
    assert.match(hero, /to="\/registro"/, 'Hero deve conter CTA para criar conta')
    assert.match(hero, /to="\/login"/, 'Hero deve conter CTA secundário para entrar')
    assert.match(hero, /Ficha de Leitura/, 'Hero deve conter a Ficha de Leitura conceitual')
    assert.match(hero, /Edmund Burke/, 'Hero deve conter citação clássica')
  })

  await t.test('2. [US2] Bancada do Simulador em 4 Dimensões (Machado de Assis)', () => {
    assert.ok(fs.existsSync(simulatorPath), 'MethodSimulator.vue deve existir')
    assert.ok(fs.existsSync(dataPath), 'landingSimulator.ts deve existir')

    const sim = fs.readFileSync(simulatorPath, 'utf-8')
    assert.match(sim, /id="metodo"/, 'Simulador deve responder à âncora #metodo')
    assert.match(sim, /role="tablist"/, 'Caderno deve possuir tablist acessível')
    assert.match(sim, /role="tab"/, 'Dimensões devem ser tabs acessíveis')
    assert.match(sim, /role="tabpanel"/, 'Painel de dimensão deve ser tabpanel')
    assert.match(sim, /highlight-text/, 'Texto da obra deve conter classes de destaque sincronizado')
    assert.match(sim, /marginal-note/, 'Texto da obra deve conter nota marginal')

    const data = fs.readFileSync(dataPath, 'utf-8')
    assert.match(data, /Machado de Assis/, 'Dados devem conter Machado de Assis')
    assert.match(data, /Memórias Póstumas de Brás Cubas/, 'Dados devem conter Memórias Póstumas')
    assert.match(data, /resumo/, 'Deve conter dimensão resumo')
    assert.match(data, /explicacao/, 'Deve conter dimensão explicacao')
    assert.match(data, /conceitos/, 'Deve conter dimensão conceitos')
    assert.match(data, /referencias/, 'Deve conter dimensão referencias')
  })

  await t.test('3. [US3] Ateliê dos 10 Temas e Composable de Tema Efêmero', () => {
    assert.ok(fs.existsSync(showcasePath), 'ThemeShowcase.vue deve existir')
    assert.ok(fs.existsSync(composablePath), 'useVisitorTheme.ts deve existir')

    const showcase = fs.readFileSync(showcasePath, 'utf-8')
    assert.match(showcase, /id="temas"/, 'Mostruário deve responder à âncora #temas')
    assert.match(showcase, /ThemePreviewGrid/, 'Deve reutilizar ThemePreviewGrid')
    assert.match(showcase, /aria-live="polite"/, 'Deve conter anúncio aria-live acessível')

    const comp = fs.readFileSync(composablePath, 'utf-8')
    assert.match(comp, /document\.documentElement\.dataset\.theme/, 'Deve alterar data-theme no DOM')
    assert.match(comp, /resetToOriginal/, 'Deve possuir método de restauração')
    assert.match(comp, /onBeforeUnmount/, 'Deve restaurar tema ao desmontar')
  })

  await t.test('4. [US4] Soberania de Dados e Tradição dos Commonplace Books', () => {
    assert.ok(fs.existsSync(sovereigntyPath), 'SovereigntySection.vue deve existir')
    assert.ok(fs.existsSync(footerPath), 'PublicFooter.vue deve existir')

    const sov = fs.readFileSync(sovereigntyPath, 'utf-8')
    assert.match(sov, /id="principios"/, 'Deve responder à âncora #principios')
    assert.match(sov, /Sem anúncios nem rastreadores/, 'Princípio 1 presente')
    assert.match(sov, /não alimentam modelos/, 'Princípio 2 presente')
    assert.match(sov, /levar tudo embora/, 'Princípio 3 presente')
    assert.match(sov, /Software independente mantido para leitores/, 'Princípio 4 presente')
    assert.match(sov, /John Locke/, 'Marco de John Locke presente')
    assert.match(sov, /Século XVI/, 'Marco do séc. XVI presente')

    const footer = fs.readFileSync(footerPath, 'utf-8')
    assert.match(footer, /Comece pelo próximo livro que você pretende ler devagar/, 'Chamada final presente')
    assert.match(footer, /to="\/sobre"/, 'Link para sobre o projeto presente')
    assert.match(footer, /to="\/apoie"/, 'Link para apoie o projeto presente')
  })

  await t.test('5. [US5] Excelência de SEO, Acessibilidade e Otimização de Chunks', () => {
    const landing = fs.readFileSync(landingViewPath, 'utf-8')
    assert.match(landing, /PublicHeader/, 'LandingView deve importar PublicHeader')
    assert.match(landing, /HeroSection/, 'LandingView deve importar HeroSection')
    assert.match(landing, /MethodSimulator/, 'LandingView deve importar MethodSimulator')
    assert.match(landing, /ThemeShowcase/, 'LandingView deve importar ThemeShowcase')
    assert.match(landing, /SovereigntySection/, 'LandingView deve importar SovereigntySection')
    assert.match(landing, /PublicFooter/, 'LandingView deve importar PublicFooter')

    const palettes = fs.readFileSync(palettesCssPath, 'utf-8')
    assert.match(palettes, /--color-text:\s*#2E4249/, 'Solário deve usar #2E4249 para atingir contraste >= 7:1')

    const settings = fs.readFileSync(settingsPath, 'utf-8')
    assert.match(settings, /text:\s*'#2E4249'/, 'Catálogo canônico de settings deve refletir cor com alto contraste')

    const fonts = fs.readFileSync(fontsCssPath, 'utf-8')
    assert.doesNotMatch(fonts, /font-display:\s*block/, 'Nenhuma fonte deve usar font-display: block')
    assert.match(fonts, /font-display:\s*swap/, 'Fontes devem usar font-display: swap')

    const indexHtml = fs.readFileSync(indexPath, 'utf-8')
    assert.match(indexHtml, /rel="preload" href="\/fonts\/eb-garamond/, 'Preload de EB Garamond presente')
    assert.match(indexHtml, /rel="preload" href="\/fonts\/source-sans-3/, 'Preload de Source Sans 3 presente')
    assert.match(indexHtml, /<div id="app">[\s\S]*<h1>Ler devagar é uma forma de pensar\.<\/h1>/, 'Conteúdo vital indexável dentro de #app')

    const router = fs.readFileSync(routerPath, 'utf-8')
    assert.match(router, /component:\s*\(\)\s*=>\s*import\('\.\.\/views\/BooksView\.vue'\)/, 'Rotas pesadas devem usar dynamic import')
    assert.match(router, /component:\s*\(\)\s*=>\s*import\('\.\.\/views\/DashboardView\.vue'\)/, 'DashboardView deve usar dynamic import')
  })

  await t.test('6. Verificação Constitucional: Zero Emojis', () => {
    const filesToCheck = [headerPath, heroPath, simulatorPath, showcasePath, sovereigntyPath, footerPath, dataPath]
    const emojiRegex = /[\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

    for (const file of filesToCheck) {
      const content = fs.readFileSync(file, 'utf-8')
      assert.ok(!emojiRegex.test(content), `O arquivo ${path.basename(file)} não deve conter emojis (Regra Constitucional)`)
    }
  })
})
