import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fullVersion, isValidSemver, parseSemver, roadmapOf } from '../src/utils/appVersion.ts'
import { VERSION_HISTORY } from '../src/data/versionHistory.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')
const VERSION = fs.readFileSync(path.resolve(process.cwd(), '..', 'VERSION'), 'utf-8').trim()

test('114: VERSION é SemVer e o package.json acompanha', () => {
  assert.ok(isValidSemver(VERSION), VERSION)
  const pkg = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), 'package.json'), 'utf-8'))
  assert.equal(pkg.version, VERSION)
  assert.match(fs.readFileSync(path.resolve(process.cwd(), 'vite.config.ts'), 'utf-8'), /__APP_VERSION__: JSON\.stringify\(appVersion\(\)\)/)
})

test('114: utilitário de versão', () => {
  assert.deepEqual(parseSemver('0.12.0-alpha.1+a1b2c3d'), { major: 0, minor: 12, patch: 0, prerelease: 'alpha.1', build: 'a1b2c3d' })
  assert.equal(parseSemver('0.12'), null)
  assert.equal(parseSemver('v0.12.0'), null)
  assert.equal(parseSemver('01.2.3'), null)
  assert.equal(roadmapOf('0.12.0-alpha.3'), '0.12')
  assert.equal(fullVersion('0.12.0-alpha.1', 'a1b2c3d'), '0.12.0-alpha.1+a1b2c3d')
  assert.equal(fullVersion('0.12.0-alpha.1', 'desconhecido'), '0.12.0-alpha.1')
  assert.equal(fullVersion('0.12.0-alpha.1', ''), '0.12.0-alpha.1')
})

test('114: histórico ordenado, com a versão atual em andamento e o alpha.N batendo com as entregas', () => {
  const minors = VERSION_HISTORY.map((e) => parseSemver(e.version).minor)
  assert.deepEqual(minors, [...minors].sort((a, b) => b - a), 'do mais recente ao mais antigo')
  assert.equal(minors.length, new Set(minors).size)
  const current = VERSION_HISTORY.find((e) => e.roadmap === roadmapOf(VERSION))
  assert.ok(current, 'o roadmap da versão atual está no histórico')
  assert.equal(current.status, 'in_progress')
  assert.equal(VERSION_HISTORY.filter((e) => e.status === 'in_progress').length, 1)
  const done = current.features.filter((f) => f.done).length
  assert.equal(parseSemver(VERSION).prerelease, `alpha.${done}`, 'alpha.N = features entregues do roadmap')
  for (const entry of VERSION_HISTORY) {
    assert.ok(isValidSemver(entry.version) && entry.highlights.length > 0, entry.version)
    assert.match(entry.started, /^\d{4}-\d{2}-\d{2}$/)
  }
})

test('114: rodapé com a versão (sem link) e tela só pelo Sobre', () => {
  const app = read('App.vue')
  assert.match(app, /<span class="footer-version" :title="`Versão \$\{appVersionDetail\}`"/)
  assert.doesNotMatch(app, /\/sobre\/versoes/, 'a versão do rodapé não leva à tela')
  assert.match(read('views/AboutView.vue'), /<RouterLink to="\/sobre\/versoes" class="button quiet versions-button">Evolução das versões<\/RouterLink>/)
  const router = read('router/index.ts')
  assert.match(router, /path: '\/sobre\/versoes', name: 'versions'.*public: true, noindex: true/)
  assert.match(router, /robots: isPublic && to\.meta\.noindex !== true/)
  for (const menu of ['components/layout/NavigationTabs.vue', 'components/navigation/MobileMoreMenu.vue', 'components/layout/UserDropdown.vue', 'components/layout/GlobalHeader.vue']) {
    assert.doesNotMatch(read(menu), /\/sobre\/versoes/, `${menu} não aponta para a tela escondida`)
  }
})
