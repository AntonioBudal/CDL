import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const frontendDir = path.resolve(new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1'), '..')

test('index.html contém baseline Schema.org JSON-LD sintaticamente válido', () => {
  const indexPath = path.join(frontendDir, 'index.html')
  const content = fs.readFileSync(indexPath, 'utf8')

  const match = content.match(/<script id="schema-json-ld" type="application\/ld\+json">([\s\S]*?)<\/script>/)
  assert.ok(match, 'Deve conter tag script com id schema-json-ld e type application/ld+json')

  const parsed = JSON.parse(match[1])
  assert.equal(parsed['@context'], 'https://schema.org')
  assert.equal(parsed['@type'], 'WebApplication')
  assert.equal(parsed.name, 'Leitorum')
  assert.equal(parsed.applicationCategory, 'EducationalApplication')
})

test('index.html inclui diretrizes do Google para favicons e manifesto web', () => {
  const indexPath = path.join(frontendDir, 'index.html')
  const content = fs.readFileSync(indexPath, 'utf8')

  assert.ok(content.includes('rel="icon" type="image/svg+xml" href="/favicon.svg"'), 'Deve referenciar favicon vetorial SVG')
  assert.ok(content.includes('sizes="48x48" href="/favicon-48x48.png"'), 'Deve referenciar favicon PNG mínimo 48x48 do Google')
  assert.ok(content.includes('rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"'), 'Deve referenciar ícone Apple 180x180')
  assert.ok(content.includes('rel="manifest" href="/site.webmanifest"'), 'Deve referenciar site.webmanifest')
})

test('Arquivos de identidade visual existem na pasta public e public/assets', () => {
  const publicDir = path.join(frontendDir, 'public')
  assert.ok(fs.existsSync(path.join(publicDir, 'favicon.svg')), 'favicon.svg deve existir')
  assert.ok(fs.existsSync(path.join(publicDir, 'favicon-48x48.png')), 'favicon-48x48.png deve existir')
  assert.ok(fs.existsSync(path.join(publicDir, 'apple-touch-icon.png')), 'apple-touch-icon.png deve existir')
  assert.ok(fs.existsSync(path.join(publicDir, 'favicon.ico')), 'favicon.ico deve existir')
  assert.ok(fs.existsSync(path.join(publicDir, 'site.webmanifest')), 'site.webmanifest deve existir')
  assert.ok(fs.existsSync(path.join(publicDir, 'assets', 'og-cover.png')), 'og-cover.png deve existir em public/assets')
})

test('site.webmanifest é JSON válido e define ícones da aplicação', () => {
  const manifestPath = path.join(frontendDir, 'public', 'site.webmanifest')
  const content = fs.readFileSync(manifestPath, 'utf8')
  const manifest = JSON.parse(content)

  assert.equal(manifest.name, 'Leitorum — Caderno de Leitura')
  assert.equal(manifest.short_name, 'Leitorum')
  assert.equal(manifest.start_url, '/')
  assert.ok(Array.isArray(manifest.icons) && manifest.icons.length >= 2, 'Deve ter pelo menos 2 ícones')
})
