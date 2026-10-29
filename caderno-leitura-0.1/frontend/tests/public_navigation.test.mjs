import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), '../src')

test('router/index.ts define rotas públicas da raiz (/) e Sobre (/sobre)', () => {
  const routerPath = path.join(srcDir, 'router', 'index.ts')
  const content = fs.readFileSync(routerPath, 'utf8')

  assert.ok(content.includes("path: '/'"), 'Deve conter rota raiz /')
  assert.ok(content.includes("name: 'landing'"), 'Deve nomear rota raiz como landing')
  assert.ok(content.includes("path: '/sobre'"), 'Deve conter rota /sobre')
  assert.ok(content.includes("name: 'about'"), 'Deve nomear rota sobre como about')
  assert.ok(content.includes("path: '/dashboard'"), 'Deve conter rota /dashboard')
  assert.ok(content.includes("path: '/books'"), 'Deve conter rota /books')
})

test('router/index.ts redireciona usuários autenticados da raiz (/) para o acervo', () => {
  // A decisão saiu para router/guard.ts (correção do laço do primeiro acesso); o comportamento é testado em
  // router-owner-setup-guard.test.mjs.
  const content = fs.readFileSync(path.join(srcDir, 'router', 'guard.ts'), 'utf8')
  const router = fs.readFileSync(path.join(srcDir, 'router', 'index.ts'), 'utf8')

  assert.ok(content.includes("input.path === '/'"), 'Guarda deve interceptar navegação para a raiz')
  assert.ok(router.includes('isAuthenticated: auth.isAuthenticated.value'), 'Guarda deve checar se usuário está autenticado')
  assert.ok(content.includes("'/livros'"), 'Alvo padrão para logados deve ser /livros')
})

test('Página inicial oferece cadastro, entrada, Sobre e Apoie sem repetir a navegação do App', () => {
  const landingPath = path.join(srcDir, 'views', 'LandingView.vue')
  assert.ok(fs.existsSync(landingPath), 'LandingView.vue deve existir')

  // A chamada principal fica no hero; Entrar, Sobre e Apoie vêm do cabeçalho público do App (GlobalHeader).
  const hero = fs.readFileSync(path.join(srcDir, 'components', 'landing', 'HeroSection.vue'), 'utf8')
  assert.ok(hero.includes('to="/registro"'), 'Hero deve conter link para criar conta /registro')

  const header = fs.readFileSync(path.join(srcDir, 'components', 'layout', 'GlobalHeader.vue'), 'utf8')
  assert.ok(header.includes('to="/login"'), 'Cabeçalho público deve conter link para /login')
  assert.ok(header.includes('to="/sobre"'), 'Cabeçalho público deve conter link para /sobre')
  assert.ok(header.includes('to="/apoie"'), 'Cabeçalho público deve conter link para /apoie')

  const landing = fs.readFileSync(landingPath, 'utf8')
  assert.ok(!landing.includes('PublicHeader') && !landing.includes('PublicFooter'), 'Landing não deve renderizar um segundo cabeçalho ou rodapé')
  assert.ok(!/<main[\s>]/.test(landing), 'Landing não deve abrir um segundo <main> dentro do App')
})

test('AboutView.vue detalha a metodologia de estudos em 4 partes', () => {
  const aboutPath = path.join(srcDir, 'views', 'AboutView.vue')
  assert.ok(fs.existsSync(aboutPath), 'AboutView.vue deve existir')

  const content = fs.readFileSync(aboutPath, 'utf8')
  assert.ok(content.includes('Resumo Analítico'), 'Deve descrever o pilar Resumo Analítico')
  assert.ok(content.includes('Explicação Detalhada'), 'Deve descrever o pilar Explicação Detalhada')
  assert.ok(content.includes('Conceitos'), 'Deve descrever o pilar Conceitos')
  assert.ok(content.includes('Referências'), 'Deve descrever o pilar Referências')
  assert.ok(content.includes('Privacidade'), 'Deve enfatizar a proteção e soberania de dados')
})

test('App.vue renderiza rodapé com links institucionais "Sobre o Leitorum" e "Apoie o Leitorum"', () => {
  const appPath = path.join(srcDir, 'App.vue')
  const content = fs.readFileSync(appPath, 'utf8')

  assert.ok(content.includes('to="/sobre"'), 'Rodapé deve conter link para /sobre')
  assert.ok(content.includes('Sobre o Leitorum'), 'Rodapé deve conter texto "Sobre o Leitorum"')
  assert.ok(content.includes('to="/apoie"'), 'Rodapé deve conter link para /apoie')
  assert.ok(content.includes('Apoie o Leitorum'), 'Rodapé deve conter texto "Apoie o Leitorum"')
})
