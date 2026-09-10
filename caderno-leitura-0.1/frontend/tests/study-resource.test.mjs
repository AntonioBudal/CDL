import test from 'node:test'
import assert from 'node:assert/strict'
import { useStudyResource } from '../src/composables/useStudyResource.ts'
import { ApiError } from '../src/services/api.ts'

const book = { id: 1, title: 'Livro de teste', author: null }
const chapter = { id: 2, book_id: 1, name: 'Capítulo 1', position: 1 }
const study = { id: 7, chapter_id: 2, title: 'Estudo', location: '', source_response: 'Original',
  summary: 'Resumo', explanation: '', concepts: '', references: '', notes: 'Anotação', created_at: '', updated_at: '' }
const gateway = { getStudy: async () => study, listBooks: async () => [book], listChapters: async () => [chapter] }

test('leitura carrega o estudo com seu livro e capítulo', async () => {
  const resource = useStudyResource(gateway)
  assert.equal(resource.state.loading, true)
  assert.deepEqual(await resource.load('1', '7'), { book, chapter, study })
  assert.equal(resource.state.loading, false)
  assert.equal(resource.state.error, '')
})

test('endereço inválido não consulta a API', async () => {
  let calls = 0
  const resource = useStudyResource({ ...gateway, getStudy: async () => { calls++; return study } })
  assert.equal(await resource.load('1', 'abc'), null)
  assert.equal(calls, 0)
  assert.equal(resource.state.loading, false)
  assert.match(resource.state.error, /não encontrado/)
})

test('estudo de outro livro não recebe metadados incorretos', async () => {
  const resource = useStudyResource({ ...gateway, listChapters: async () => [{ ...chapter, book_id: 8 }] })
  assert.equal(await resource.load('1', '7'), null)
  assert.equal(resource.state.context, null)
  assert.match(resource.state.error, /neste livro/)
})

test('falha de leitura permite tentar novamente', async () => {
  let calls = 0
  const resource = useStudyResource({ ...gateway, getStudy: async () => {
    if (++calls === 1) throw new ApiError('Estudo não encontrado.', 404)
    return study
  } })
  assert.equal(await resource.load('1', '7'), null)
  assert.match(resource.state.error, /não encontrado/)
  assert.equal((await resource.load('1', '7')).study.id, 7)
  assert.equal(resource.state.error, '')
})

test('resposta atrasada de outra navegação não substitui o estudo atual', async () => {
  let resolve
  const pending = new Promise(done => { resolve = done })
  const resource = useStudyResource({ ...gateway, getStudy: async id => id === 7 ? pending : { ...study, id } })
  const first = resource.load('1', '7')
  await resource.load('1', '8')
  resolve(study)
  assert.equal(await first, null)
  assert.equal(resource.state.context.study.id, 8)
  assert.equal(resource.state.loading, false)
})
