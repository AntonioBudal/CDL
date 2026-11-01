import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test('Feature 074 - Página Inicial sem Login (SEO), revisada: apresentação objetiva', async (t) => {
  const landingViewPath = path.resolve(__dirname, '../src/views/LandingView.vue')
  const heroPath = path.resolve(__dirname, '../src/components/landing/HeroSection.vue')
  const simulatorPath = path.resolve(__dirname, '../src/components/landing/MethodSimulator.vue')
  const featuresPath = path.resolve(__dirname, '../src/components/landing/FeatureList.vue')
  const showcasePath = path.resolve(__dirname, '../src/components/landing/ThemeShowcase.vue')
  const sovereigntyPath = path.resolve(__dirname, '../src/components/landing/SovereigntySection.vue')
  const dataPath = path.resolve(__dirname, '../src/data/landingSimulator.ts')
  const composablePath = path.resolve(__dirname, '../src/composables/useVisitorTheme.ts')
  const fontsCssPath = path.resolve(__dirname, '../src/fonts.css')
  const palettesCssPath = path.resolve(__dirname, '../src/palettes.css')
  const settingsPath = path.resolve(__dirname, '../src/types/settings.ts')
  const indexPath = path.resolve(__dirname, '../index.html')
  const routerPath = path.resolve(__dirname, '../src/router/index.ts')

  await t.test('1. [US1] Hero informativo com uma chamada principal', () => {
    const hero = fs.readFileSync(heroPath, 'utf-8')
    assert.match(hero, /<h1[^>]*>[\s\S]*Leitorum[\s\S]*caderno de leitura e fichamento[\s\S]*<\/h1>/, 'H1 deve trazer a marca e dizer o que o produto é')
    assert.match(hero, /HeroShowcase/, 'Hero deve exibir a ilustração da interface')
    assert.match(hero, /to="\/registro"/, 'Hero deve conter CTA para criar conta')
    assert.match(hero, /href="#exemplo"/, 'Hero deve levar ao exemplo de estudo')
    assert.doesNotMatch(hero, /Ler devagar é uma forma de pensar/, 'Slogan antigo não deve voltar')
  })

  await t.test('2. [US2] Exemplo de estudo em quatro partes (Machado de Assis)', () => {
    assert.ok(fs.existsSync(simulatorPath), 'MethodSimulator.vue deve existir')
    assert.ok(fs.existsSync(dataPath), 'landingSimulator.ts deve existir')

    const sim = fs.readFileSync(simulatorPath, 'utf-8')
    assert.match(sim, /id="exemplo"/, 'Exemplo deve responder à âncora #exemplo')
    assert.match(sim, /role="tablist"/, 'Partes do estudo devem formar um tablist acessível')
    assert.match(sim, /role="tab"/, 'Partes devem ser tabs acessíveis')
    assert.match(sim, /role="tabpanel"/, 'Conteúdo da parte deve ser tabpanel')
    assert.match(sim, /highlight-text/, 'Trecho deve destacar a passagem da parte ativa')
    assert.doesNotMatch(sim, /Simulador In-Place|bancada do método/i, 'Rótulos artificiais não devem voltar')

    const data = fs.readFileSync(dataPath, 'utf-8')
    assert.match(data, /Machado de Assis/, 'Dados devem conter Machado de Assis')
    assert.match(data, /Memórias Póstumas de Brás Cubas/, 'Dados devem conter Memórias Póstumas')
    for (const label of ['Resumo', 'Explicação', 'Conceitos', 'Referências']) {
      assert.match(data, new RegExp(`label: '${label}'`), `Deve conter a parte ${label}`)
    }
    // Trecho conferido com o Projeto Gutenberg (ebook 54829); a versão anterior trazia frases inexistentes.
    assert.match(data, /duas colunas máximas da opinião/, 'Trecho deve seguir o texto original do prólogo')
    assert.doesNotMatch(data, /angariar as simpatias da posteridade/, 'Frase inventada não deve voltar')
  })

  await t.test('2b. Lista de recursos descreve funções existentes', () => {
    const features = fs.readFileSync(featuresPath, 'utf-8')
    assert.match(features, /id="recursos"/, 'Lista de recursos deve ter âncora')
    for (const term of ['Revisão', 'Importação', 'Compartilhamento', 'Marcações']) {
      assert.match(features, new RegExp(term), `Recurso ${term} deve constar`)
    }
  })

  await t.test('3. [US3] Temas em seção curta, com prévia na própria página', () => {
    assert.ok(fs.existsSync(showcasePath), 'ThemeShowcase.vue deve existir')
    assert.ok(fs.existsSync(composablePath), 'useVisitorTheme.ts deve existir')

    const showcase = fs.readFileSync(showcasePath, 'utf-8')
    assert.match(showcase, /id="temas"/, 'Mostruário deve responder à âncora #temas')
    assert.match(showcase, /CANONICAL_THEME_PREVIEWS/, 'Prévia deve usar as cores do catálogo canônico de temas')
    assert.match(showcase, /aria-live="polite"/, 'Deve conter anúncio aria-live acessível')
    assert.doesNotMatch(showcase, /Ateliê de Paletas/, 'Rótulo antigo não deve voltar')

    const comp = fs.readFileSync(composablePath, 'utf-8')
    assert.match(comp, /document\.documentElement\.dataset\.theme/, 'Deve alterar data-theme no DOM')
    assert.match(comp, /resetToOriginal/, 'Deve possuir método de restauração')
    assert.match(comp, /onBeforeUnmount/, 'Deve restaurar tema ao desmontar')
  })

  await t.test('4. [US4] Seus dados: afirmações verificáveis, sem linha do tempo histórica', () => {
    assert.ok(fs.existsSync(sovereigntyPath), 'SovereigntySection.vue deve existir')

    const sov = fs.readFileSync(sovereigntyPath, 'utf-8')
    assert.match(sov, /id="dados"/, 'Deve responder à âncora #dados')
    assert.match(sov, /SQLite/, 'Deve dizer onde os dados ficam')
    assert.match(sov, /Markdown/, 'Deve citar o formato de exportação')
    assert.match(sov, /\.zip/, 'Deve citar a exportação completa da conta')
    assert.match(sov, /https:\/\/github\.com\/AntonioBudal\/CDL/, 'Deve apontar para o código-fonte')
    assert.doesNotMatch(sov, /John Locke|Século XVI|para sempre|inviolável|MIT/, 'Sem história, promessas absolutas ou licença não comprovada')
  })

  await t.test('5. [US5] SEO, estrutura sem duplicação e otimização de chunks', () => {
    const landing = fs.readFileSync(landingViewPath, 'utf-8')
    for (const name of ['HeroSection', 'MethodSimulator', 'FeatureList', 'ThemeShowcase', 'SovereigntySection']) {
      assert.match(landing, new RegExp(name), `LandingView deve importar ${name}`)
    }
    assert.doesNotMatch(landing, /PublicHeader|PublicFooter/, 'Cabeçalho e rodapé vêm do App.vue, sem duplicar')
    assert.match(landing, /title: 'Caderno de leitura e fichamento'/, 'Título não deve repetir "Leitorum" (o sufixo já é adicionado)')

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
    assert.match(indexHtml, /<div id="app">[\s\S]*<h1>Leitorum: seu caderno de leitura e fichamento<\/h1>/, 'Conteúdo vital indexável dentro de #app')
    assert.match(indexHtml, /<title>Caderno de leitura e fichamento — Leitorum<\/title>/, 'Título estático igual ao da página montada')

    const router = fs.readFileSync(routerPath, 'utf-8')
    assert.match(router, /component:\s*\(\)\s*=>\s*import\('\.\.\/views\/BooksView\.vue'\)/, 'Rotas pesadas devem usar dynamic import')
    assert.match(router, /component:\s*\(\)\s*=>\s*import\('\.\.\/views\/DashboardView\.vue'\)/, 'DashboardView deve usar dynamic import')
  })

  await t.test('6. Verificação Constitucional: Zero Emojis', () => {
    const filesToCheck = [heroPath, simulatorPath, featuresPath, showcasePath, sovereigntyPath, dataPath]
    const emojiRegex = /[\u{1F300}-\u{1F5FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u

    for (const file of filesToCheck) {
      const content = fs.readFileSync(file, 'utf-8')
      assert.ok(!emojiRegex.test(content), `O arquivo ${path.basename(file)} não deve conter emojis (Regra Constitucional)`)
    }
  })
})
