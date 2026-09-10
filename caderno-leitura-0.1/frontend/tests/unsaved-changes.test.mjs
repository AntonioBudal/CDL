import test from 'node:test'
import assert from 'node:assert/strict'
import { createRenderer, defineComponent, h, nextTick, reactive } from 'vue'
import { createMemoryHistory, createRouter, RouterView } from 'vue-router'
import { useUnsavedChanges } from '../src/composables/useUnsavedChanges.ts'

// Headless Vue host: exercises the real router guards without a browser or DOM.
const node = type => ({ type, children: [], parent: null })
const renderer = createRenderer({
  createElement: node, createText: node, createComment: node,
  setText: () => {}, setElementText: () => {}, patchProp: () => {},
  parentNode: item => item.parent,
  nextSibling: item => item.parent?.children[item.parent.children.indexOf(item) + 1] ?? null,
  insert: (item, parent, anchor = null) => {
    if (item.parent) item.parent.children.splice(item.parent.children.indexOf(item), 1)
    item.parent = parent
    const index = anchor ? parent.children.indexOf(anchor) : -1
    if (index < 0) parent.children.push(item)
    else parent.children.splice(index, 0, item)
  },
  remove: item => { if (item.parent) item.parent.children.splice(item.parent.children.indexOf(item), 1) },
})

async function harness(t) {
  const previousWindow = globalThis.window
  const state = reactive({ dirty: false, busy: false })
  const calls = { confirmations: 0, alerts: 0 }
  const listeners = new Set()
  let accepts = false
  globalThis.window = {
    confirm: () => { calls.confirmations++; return accepts },
    alert: () => { calls.alerts++ },
    addEventListener: (name, listener) => { if (name === 'beforeunload') listeners.add(listener) },
    removeEventListener: (name, listener) => { if (name === 'beforeunload') listeners.delete(listener) },
  }
  const Form = defineComponent({ setup() {
    useUnsavedChanges(() => state.dirty, () => state.busy)
    return () => h('form')
  } })
  const router = createRouter({ history: createMemoryHistory(), routes: [
    { path: '/editar/:id', component: Form },
    { path: '/livros', component: { render: () => h('div') } },
  ] })
  await router.push('/editar/1')
  const app = renderer.createApp({ render: () => h(RouterView) })
  app.use(router)
  app.mount(node('root'))
  await nextTick()
  t.after(() => {
    app.unmount()
    if (previousWindow === undefined) delete globalThis.window
    else globalThis.window = previousWindow
  })
  return { state, calls, listeners, router, accept: () => { accepts = true } }
}

test('recusar a saída mantém a rota; aceitar permite abandonar o formulário', async t => {
  const { state, calls, router, accept } = await harness(t)
  state.dirty = true
  await router.push('/livros')
  assert.equal(router.currentRoute.value.path, '/editar/1')
  assert.equal(calls.confirmations, 1)
  accept()
  await router.push('/livros')
  assert.equal(router.currentRoute.value.path, '/livros')
  assert.equal(calls.confirmations, 2)
})

test('trocar o registro exige confirmação; alterar só query não abandona o formulário', async t => {
  const { state, calls, router } = await harness(t)
  state.dirty = true
  await router.push('/editar/1?aba=resumo')
  assert.equal(router.currentRoute.value.fullPath, '/editar/1?aba=resumo')
  assert.equal(calls.confirmations, 0)
  await router.push('/editar/2')
  assert.equal(router.currentRoute.value.path, '/editar/1')
  assert.equal(calls.confirmations, 1)
})

test('operação pendente bloqueia navegação; depois de salvar, sai sem confirmação', async t => {
  const { state, calls, router } = await harness(t)
  state.busy = true
  await router.push('/livros')
  assert.equal(router.currentRoute.value.path, '/editar/1')
  assert.equal(calls.alerts, 1)
  state.busy = false
  await router.push('/livros')
  assert.equal(router.currentRoute.value.path, '/livros')
  assert.equal(calls.confirmations, 0)
})

test('recarregar recebe proteção apenas enquanto houver alterações ou operação pendente', async t => {
  const { state, listeners, router } = await harness(t)
  assert.equal(listeners.size, 0)
  state.dirty = true
  assert.equal(listeners.size, 1)
  let prevented = false
  const event = { preventDefault: () => { prevented = true }, returnValue: undefined }
  for (const listener of listeners) listener(event)
  assert.equal(prevented, true)
  assert.equal(event.returnValue, '')
  state.dirty = false
  assert.equal(listeners.size, 0)
  state.busy = true
  assert.equal(listeners.size, 1)
  state.busy = false
  await router.push('/livros')
  await nextTick()
  assert.equal(listeners.size, 0)
})
