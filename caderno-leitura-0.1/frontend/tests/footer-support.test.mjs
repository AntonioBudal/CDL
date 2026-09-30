import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), '../src')

test('App.vue inclui link discreto para /apoie no rodapé global', () => {
  const appVuePath = path.join(srcDir, 'App.vue')
  const content = fs.readFileSync(appVuePath, 'utf8')

  assert.ok(content.includes('class="app-footer"'), 'Deve conter tag app-footer')
  assert.ok(content.includes('to="/apoie"'), 'Deve conter RouterLink apontando para /apoie')
  assert.ok(content.includes('Apoie o Leitorum'), 'Deve conter texto canônico "Apoie o Leitorum"')
})

test('MobileMoreMenu.vue inclui item Apoie o Leitorum no menu lateral móvel', () => {
  const mobileMenuPath = path.join(srcDir, 'components', 'navigation', 'MobileMoreMenu.vue')
  const content = fs.readFileSync(mobileMenuPath, 'utf8')

  assert.ok(content.includes('to="/apoie"'), 'MobileMoreMenu deve apontar para /apoie')
  assert.ok(content.includes('Apoie o Leitorum'), 'MobileMoreMenu deve conter rótulo Apoie o Leitorum')
})

test('router/index.ts define rota /apoie com alias /apoiar e meta public', () => {
  const routerPath = path.join(srcDir, 'router', 'index.ts')
  const content = fs.readFileSync(routerPath, 'utf8')

  assert.ok(content.includes("path: '/apoie'"), 'Deve conter rota /apoie')
  assert.ok(content.includes("alias: ['/apoiar']"), 'Deve conter alias /apoiar')
  assert.ok(content.includes('public: true'), 'Rota de apoio deve ser pública')
})

test('SupportView.vue existe, implementa acessibilidade de cópia e zero emojis', () => {
  const supportViewPath = path.join(srcDir, 'views', 'SupportView.vue')
  assert.ok(fs.existsSync(supportViewPath), 'SupportView.vue deve existir')

  const content = fs.readFileSync(supportViewPath, 'utf8')
  assert.ok(content.includes('handleCopyPix'), 'Deve conter função de cópia de chave PIX')
  assert.ok(content.includes('role="region"'), 'Deve possuir semântica de região WAI-ARIA')
  assert.ok(content.includes('min-height: 44px') || content.includes('44px'), 'Elementos interativos devem respeitar alvo mínimo de 44px')

  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'SupportView.vue não deve conter emojis')
})
