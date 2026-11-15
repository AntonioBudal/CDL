import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const read = (rel) => fs.readFileSync(path.resolve(process.cwd(), 'src', rel), 'utf-8')

test('120: rotas, menus e contador de convites', () => {
  const router = read('router/index.ts')
  assert.match(router, /path: '\/circulos', name: 'circles'/)
  assert.match(router, /path: '\/circulos\/:id', name: 'circle'/)
  const nav = read('components/layout/NavigationTabs.vue')
  assert.match(nav, /to: '\/circulos',[\s\S]*?badgeCount: \(\) => circleInviteCount\.value/)
  assert.match(nav, /pendingFriendsCount\.value > 0 \|\| circleInviteCount\.value > 0/)
  assert.match(read('components/navigation/MobileMoreMenu.vue'), /to="\/circulos"[\s\S]*?t\('nav\.circlesLong'\)/) // F0.12.09: texto por chave (pt-BR em src/i18n/messages)
  assert.match(read('App.vue'), /void circleInvites\.refresh\(\)/)
  assert.match(read('composables/useCircleInvites.ts'), /api\.getCircleInviteCount\(signal\)/)
  const book = read('views/BookView.vue')
  assert.match(book, /router\.push\(\{ name: 'circles', query: \{ livro: String\(book\.value\.id\) \} \}\)/)
  assert.match(book, /Criar círculo deste livro/)
})

test('120: lista com convites e criação a partir de um livro meu', () => {
  const view = read('views/CirclesView.vue')
  assert.match(view, /api\.acceptCircle\(invite\.id\)/)
  assert.match(view, /api\.declineCircle\(invite\.id\)/)
  assert.match(view, /api\.createCircle\(Number\(bookId\.value\), name\.value\.trim\(\) \|\| undefined\)/)
  assert.match(view, /Number\(route\.query\.livro\)/)
})

test('120: página do círculo respeita a trava do servidor', () => {
  const view = read('views/CircleView.vue')
  assert.match(view, /v-else-if="posts\[part\.id\]\?\.locked"/)
  assert.match(view, /Avance seu progresso até ela para ler e escrever/)
  assert.match(view, /api\.setCircleProgress\(circleId\.value, totalParts\.value, true\)/)
  assert.match(view, /<option value="done">Terminei o livro<\/option>/)
  assert.match(view, /white-space: pre-wrap/)
  assert.ok(!/v-html/.test(view), 'mensagens como texto, nunca HTML')
  const api = read('services/api.ts')
  assert.match(api, /`\/circles\/\$\{id\}\/parts\/\$\{partId\}\/posts`/)
  assert.match(api, /`\/circles\/\$\{id\}\/progress`, \{ method: 'PUT'/)
})
