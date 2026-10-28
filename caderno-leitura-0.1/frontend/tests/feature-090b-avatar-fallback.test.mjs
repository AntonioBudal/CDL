import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { handleAvatarError, installAvatarFallback, isAvatarImage, TRANSPARENT_PIXEL } from '../src/utils/avatarFallback.ts'

const img = (src, className = '') => ({
  tagName: 'IMG', src, dataset: {},
  getAttribute: name => (name === 'src' ? src : name === 'class' ? className : null),
})

test('avatar do cofre que falha vira pixel transparente, uma única vez', () => {
  const avatar = img('/api/avatars/6f1c0000-0000-4000-8000-000000000000')
  assert.equal(handleAvatarError(avatar), true)
  assert.equal(avatar.src, TRANSPARENT_PIXEL)
  assert.equal(avatar.dataset.avatarFallback, '1')
  assert.equal(handleAvatarError(avatar), false, 'não entra em laço se o pixel também falhar')
})

test('avatar externo marcado pela classe também é tratado; capas e outras imagens não', () => {
  assert.equal(isAvatarImage(img('https://exemplo.invalid/foto.png', 'menu-avatar-img')), true)
  assert.equal(isAvatarImage(img('/api/covers/6f1c0000-0000-4000-8000-000000000000', 'cover-img')), false)
  assert.equal(isAvatarImage({ tagName: 'DIV', getAttribute: () => '/api/avatars/x' }), false)
  assert.equal(isAvatarImage(img(TRANSPARENT_PIXEL, 'avatar-img')), false)
})

test('o tratador é instalado em captura no documento ao iniciar o app', () => {
  const calls = []
  installAvatarFallback({ addEventListener: (type, _fn, capture) => calls.push([type, capture]) })
  assert.deepEqual(calls, [['error', true]])
  const main = fs.readFileSync(path.resolve(process.cwd(), 'src/main.ts'), 'utf-8')
  assert.ok(main.includes('installAvatarFallback()'))
})
