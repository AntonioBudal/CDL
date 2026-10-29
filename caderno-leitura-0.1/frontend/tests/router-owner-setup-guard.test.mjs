import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { resolveNavigation, SETUP_PATH } from '../src/router/guard.ts'

// Guarda de navegação (router.beforeEach): decisão pura, sem Vue. Correção do laço do primeiro acesso.

const base = {
  path: '/livros', fullPath: '/livros', isPublicMeta: false, requiresAdmin: false,
  isAuthenticated: true, isAdmin: false, ownerSetupRequired: false, homePreference: null,
}
const nav = overrides => resolveNavigation({ ...base, ...overrides })

/** Segue os redirecionamentos como o vue-router faria; falha se não parar em poucos passos. */
function settle(start, state) {
  let target = start
  const visited = [target]
  for (let i = 0; i < 10; i++) {
    const redirect = nav({ ...state, path: target, fullPath: target })
    if (redirect === null) return { final: target, visited }
    target = typeof redirect === 'string' ? redirect : redirect.path
    visited.push(target)
  }
  throw new Error(`laço de redirecionamento: ${visited.join(' → ')}`)
}

test('primeiro acesso pendente e proprietário já autenticado (sem login obrigatório): para no primeiro acesso', () => {
  const state = { isAuthenticated: true, isAdmin: true, ownerSetupRequired: true }
  for (const start of ['/', '/livros', '/digitalizar', '/login', SETUP_PATH]) {
    assert.equal(settle(start, state).final, SETUP_PATH, start)
  }
  assert.equal(nav({ ...state, path: SETUP_PATH, fullPath: SETUP_PATH }), null)
})

test('primeiro acesso pendente e sem sessão: também vai para o primeiro acesso', () => {
  assert.equal(settle('/livros', { isAuthenticated: false, ownerSetupRequired: true }).final, SETUP_PATH)
})

test('depois do primeiro acesso, o autenticado sai das telas de entrada para a página inicial preferida', () => {
  assert.equal(settle(SETUP_PATH, { isAuthenticated: true }).final, '/livros')
  assert.equal(settle('/', { isAuthenticated: true, homePreference: 'dashboard' }).final, '/dashboard')
  assert.equal(nav({ path: '/livros' }), null)
})

test('sem sessão, rota protegida vai para o login com o retorno; rota pública segue', () => {
  assert.deepEqual(nav({ isAuthenticated: false, path: '/digitalizar', fullPath: '/digitalizar?x=1' }), {
    path: '/login', query: { redirect: '/digitalizar?x=1' },
  })
  assert.equal(nav({ isAuthenticated: false, path: '/', fullPath: '/', isPublicMeta: true }), null) // landing pública
  assert.equal(nav({ isAuthenticated: false, path: '/sobre', fullPath: '/sobre', isPublicMeta: true }), null)
  assert.equal(nav({ isAuthenticated: false, path: '/login', fullPath: '/login' }), null)
})

test('área de administrador continua restrita', () => {
  assert.deepEqual(nav({ path: '/admin', fullPath: '/admin' }), { path: '/livros', query: { aviso: 'acesso-restrito' } })
  assert.equal(nav({ path: '/admin', fullPath: '/admin', isAdmin: true }), null)
  assert.deepEqual(nav({ path: '/x', fullPath: '/x', requiresAdmin: true }), { path: '/livros', query: { aviso: 'acesso-restrito' } })
})

test('o router usa a decisão pura', () => {
  const router = fs.readFileSync(path.resolve(process.cwd(), 'src/router/index.ts'), 'utf-8')
  assert.ok(router.includes("import { resolveNavigation } from './guard.ts'"))
  assert.ok(router.includes('resolveNavigation({'))
})
