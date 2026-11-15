import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// F0.12.09 (spec 122): seletor de idioma, só a fundação.
const SRC = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.join(SRC, rel), 'utf-8')

async function messages() {
  const pt = (await import(`../src/i18n/messages/pt-BR.ts`)).default
  const en = (await import(`../src/i18n/messages/en.ts`)).default
  return { pt, en }
}

function keys(obj, prefix = '') {
  return Object.entries(obj).flatMap(([k, v]) => (typeof v === 'object' ? keys(v, `${prefix}${k}.`) : [`${prefix}${k}`]))
}

function files(dir = SRC) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) return files(full)
    return /\.(vue|ts)$/.test(entry.name) ? [full] : []
  })
}

test('122: português e inglês com as mesmas chaves, sem texto vazio', async () => {
  const { pt, en } = await messages()
  assert.deepEqual(keys(en).sort(), keys(pt).sort())
  for (const lang of [pt, en]) {
    for (const key of keys(lang)) {
      const value = key.split('.').reduce((o, k) => o[k], lang)
      assert.ok(typeof value === 'string' && value.trim(), key)
    }
  }
  assert.equal(en.nav.dashboard, 'Dashboard')
  assert.equal(en.nav.inbox, 'Inbox')
})

test('122: os títulos em português são os mesmos das rotas', async () => {
  const { pt } = await messages()
  const router = read('router/index.ts')
  for (const [name, title] of Object.entries(pt.titles)) {
    assert.match(router, new RegExp(`name: '${name}'[\\s\\S]{0,160}?meta: \\{ title: '${title}'`), name)
  }
  assert.match(router, /const title = routeTitle\(to\.name, /)
})

test('122: menus, cabeçalho, rodapé e avisos gerais por chave', () => {
  const chrome = {
    'components/layout/NavigationTabs.vue': ["label: t('nav.dashboard')", "t('nav.more')", "t('nav.mainNav')"],
    'components/navigation/MobileMoreMenu.vue': ["t('nav.myProfile')", "t('nav.logout')", "t('nav.circleInvites', { count: circleInviteCount }, circleInviteCount)"],
    'components/layout/MobileTabBar.vue': ["t('nav.dashboard')", "t('nav.mobileNav')"],
    'components/layout/UserDropdown.vue': ["t('nav.myProfile')", "t('nav.logout')", "t('nav.userMenu', { name: displayName })"],
    'components/layout/GlobalHeader.vue': ["t('header.search')", "t('header.quickCaptureAria')", "t('nav.login')"],
    'components/sync/SyncStatusBadge.vue': ["t('sync.synced')", "t('sync.aria', { label })"],
    'components/notifications/NotificationsDropdown.vue': ["t('notifications.title')", "t('notifications.emptyTitle')"],
    'App.vue': ["t('footer.about')", "t('footer.source')", "t('footer.version', { version: appVersionDetail })"],
    'services/api.ts': ["t('common.genericError')", "t('common.serverUnreachable')", "t('common.invalidResponse')"],
  }
  for (const [file, expected] of Object.entries(chrome)) {
    const text = read(file)
    for (const piece of expected) assert.ok(text.includes(piece), `${file}: ${piece}`)
  }
  // Nenhum texto fixo em português sobra nos menus do celular e do usuário.
  assert.doesNotMatch(read('components/navigation/MobileMoreMenu.vue'), /drawer-item-label">[A-ZÀ-Ú]/)
  assert.doesNotMatch(read('components/layout/UserDropdown.vue'), /<span>[A-ZÀ-Ú][a-zà-ú]+(?: [a-zà-ú]+)*<\/span>/)
})

test('122: nenhum pt-BR fixo fora de src/i18n; conteúdo segue o português', () => {
  const found = []
  for (const file of files()) {
    const rel = path.relative(SRC, file).replaceAll('\\', '/')
    if (rel.startsWith('i18n/')) continue
    if (fs.readFileSync(file, 'utf-8').includes("'pt-BR'")) found.push(rel)
  }
  assert.deepEqual(found, [])
  assert.match(read('i18n/content.ts'), /export const CONTENT_LOCALE = 'pt-BR'/)
  assert.match(read('utils/referenceFormats.ts'), /localeCompare\(b, CONTENT_LOCALE\)/)
  assert.match(read('views/DashboardView.vue'), /uiLocale\(\)/)
})

test('122: instalação, idioma inicial, seletor e preferências', () => {
  assert.match(read('main.ts'), /createApp\(App\)\.use\(i18n\)\.use\(router\)/)
  const index = read('i18n/index.ts')
  assert.match(index, /legacy: false/)
  assert.match(index, /fallbackLocale: DEFAULT_LOCALE/)
  assert.match(index, /localStorage\.getItem\(LOCALE_STORAGE_KEY\)/)
  assert.match(index, /browser\.toLowerCase\(\)\.startsWith\('en'\) \? 'en' : DEFAULT_LOCALE/)
  assert.match(index, /document\.documentElement\.lang = locale/)
  const selector = read('components/settings/LanguageSelector.vue')
  assert.match(selector, /preferences\.updatePreferences\(\{ locale: value \}\)/)
  assert.match(selector, /setLocale\(value\)/)
  assert.match(read('views/SettingsView.vue'), /<LanguageSelector \/>/)
  assert.match(read('composables/usePreferences.ts'), /if \(isAppLocale\(prefs\.locale\) && prefs\.locale !== currentLocale\(\)\) setLocale\(prefs\.locale\)/)
  const vite = fs.readFileSync(path.resolve(process.cwd(), 'vite.config.ts'), 'utf-8')
  assert.match(vite, /__INTLIFY_JIT_COMPILATION__: true/)
  const pkg = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), 'package.json'), 'utf-8'))
  assert.equal(pkg.dependencies['vue-i18n'], '11.4.16', 'versão exata')
})
