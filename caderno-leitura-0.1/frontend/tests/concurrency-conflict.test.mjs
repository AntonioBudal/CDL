import test from 'node:test'
import assert from 'node:assert/strict'
import { ApiError } from '../src/services/api.ts'
import { useStudyEdit } from '../src/composables/useStudyEdit.ts'

const sampleStudy = {
  id: 10,
  book_id: 1,
  chapter_id: 2,
  title: 'Estudo Inicial',
  location: 'Página 12',
  notes: 'Notas originais',
  summary: 'Resumo original',
  explanation: 'Explicação original',
  concepts: 'Conceito original',
  references: 'Ref original',
  source_response: 'Texto fonte',
  created_at: '2026-09-19T10:00:00Z',
  updated_at: '2026-09-19T10:00:00Z',
  deleted_at: null,
}

test('useStudyEdit detecta conflito 409, ativa isConflict e preserva formulário intacto', async () => {
  const editor = useStudyEdit({
    updateStudy: async () => {
      throw new ApiError('Conflito de concorrência: estudo modificado em outro dispositivo.', 409)
    },
  })

  editor.load(sampleStudy)

  // O usuário digita novos dados
  editor.state.title = 'Título Editado no PC'
  editor.state.notes = 'Reflexão que não pode ser perdida'

  assert.equal(editor.dirty.value, true)

  const result = await editor.save()
  assert.equal(result, null)

  // Verifica que o estado de conflito foi ativado
  assert.equal(editor.state.isConflict, true)
  assert.match(editor.state.conflictMessage, /concorrência/i)

  // Verifica que os dados digitados permanecem intactos
  assert.equal(editor.state.title, 'Título Editado no PC')
  assert.equal(editor.state.notes, 'Reflexão que não pode ser perdida')
  assert.equal(editor.dirty.value, true)
})

test('useStudyEdit.overwrite atualiza timestamp e reenvia dados locais com sucesso', async () => {
  let updateCalls = 0
  let sentPatch = null

  const remoteStudy = {
    ...sampleStudy,
    title: 'Título Alterado no Celular',
    updated_at: '2026-09-19T10:05:00Z',
  }

  const editor = useStudyEdit({
    getStudy: async () => remoteStudy,
    updateStudy: async (_id, patch) => {
      updateCalls++
      sentPatch = patch
      if (updateCalls === 1) {
        throw new ApiError('Conflito 409', 409)
      }
      return {
        ...remoteStudy,
        ...patch,
        updated_at: '2026-09-19T10:06:00Z',
      }
    },
  })

  editor.load(sampleStudy)
  editor.state.title = 'Título que Deve Sobrescrever'
  editor.state.notes = 'Minha anotação local'

  // Primeiro salvamento dá 409
  await editor.save()
  assert.equal(editor.state.isConflict, true)

  // Usuário escolhe 'Sobrescrever com minhas alterações'
  const saved = await editor.overwrite()
  assert.ok(saved)
  assert.equal(saved.title, 'Título que Deve Sobrescrever')
  assert.equal(editor.state.isConflict, false)
  assert.equal(sentPatch.expected_updated_at, '2026-09-19T10:05:00Z')
})

test('useStudyEdit.reload descarta alterações locais e carrega versão externa', async () => {
  const remoteStudy = {
    ...sampleStudy,
    title: 'Versão do Servidor Mais Recente',
    notes: 'Anotações feitas no celular',
    updated_at: '2026-09-19T10:15:00Z',
  }

  const editor = useStudyEdit({
    getStudy: async () => remoteStudy,
    updateStudy: async () => {
      throw new ApiError('Conflito 409', 409)
    },
  })

  editor.load(sampleStudy)
  editor.state.title = 'Edição Local Descartável'
  await editor.save()
  assert.equal(editor.state.isConflict, true)

  // Usuário escolhe 'Recarregar versão externa'
  const reloaded = await editor.reload()
  assert.ok(reloaded)
  assert.equal(editor.state.title, 'Versão do Servidor Mais Recente')
  assert.equal(editor.state.notes, 'Anotações feitas no celular')
  assert.equal(editor.state.isConflict, false)
  assert.equal(editor.dirty.value, false)
})

test('useStudyEdit.dismissConflict fecha o modal mantendo os campos e estado dirty', () => {
  const editor = useStudyEdit({
    updateStudy: async () => sampleStudy,
  })

  editor.load(sampleStudy)
  editor.state.isConflict = true
  editor.state.title = 'Texto Mantido'

  editor.dismissConflict()
  assert.equal(editor.state.isConflict, false)
  assert.equal(editor.state.title, 'Texto Mantido')
})
