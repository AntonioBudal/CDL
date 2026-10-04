import test from 'node:test'
import assert from 'node:assert/strict'
import { useStudyDraft, getStudyDraftKey } from '../src/composables/useStudyDraft.ts'

class StorageMock {
  constructor() {
    this.store = new Map()
  }
  getItem(key) {
    return this.store.has(key) ? this.store.get(key) : null
  }
  setItem(key, value) {
    this.store.set(key, String(value))
  }
  removeItem(key) {
    this.store.delete(key)
  }
  clear() {
    this.store.clear()
  }
}

test('getStudyDraftKey gera a chave correta com prefixo caderno_draft_study_', () => {
  assert.equal(getStudyDraftKey(15), 'caderno_draft_study_15')
})

test('useStudyDraft: salva rascunho com debounce e recupera payload completo', async () => {
  const storage = new StorageMock()
  let current = {
    title: 'Estudo em rascunho',
    location: 'p. 10',
    sections: {
      summary: 'Resumo inicial',
      explanation: 'Explicação detalhada',
      concepts: 'Conceito A',
      references: '',
    },
    notes: 'Minhas notas privadas',
  }

  const draft = useStudyDraft({
    studyId: 42,
    getCurrentData: () => current,
    debounceMs: 50,
    storage,
  })

  // Dispara salvamento
  draft.saveDraft()

  // Antes do debounce não gravou
  assert.equal(storage.getItem('caderno_draft_study_42'), null)

  // Aguarda debounce
  await new Promise((resolve) => setTimeout(resolve, 80))

  const raw = storage.getItem('caderno_draft_study_42')
  assert.ok(raw !== null, 'Deveria ter gravado no storage')
  const parsed = JSON.parse(raw)

  assert.equal(parsed.studyId, 42)
  assert.equal(parsed.title, 'Estudo em rascunho')
  assert.equal(parsed.location, 'p. 10')
  assert.equal(parsed.sections.summary, 'Resumo inicial')
  assert.equal(parsed.notes, 'Minhas notas privadas')
  assert.ok(typeof parsed.savedAt === 'number')
})

test('useStudyDraft: isola rascunhos por studyId', async () => {
  const storage = new StorageMock()

  const draft1 = useStudyDraft({
    studyId: 101,
    getCurrentData: () => ({
      title: 'Estudo 101',
      location: '',
      sections: { summary: 'S1', explanation: '', concepts: '', references: '' },
      notes: '',
    }),
    debounceMs: 10,
    storage,
  })

  const draft2 = useStudyDraft({
    studyId: 102,
    getCurrentData: () => ({
      title: 'Estudo 102',
      location: '',
      sections: { summary: 'S2', explanation: '', concepts: '', references: '' },
      notes: '',
    }),
    debounceMs: 10,
    storage,
  })

  draft1.saveDraft()
  draft2.saveDraft()

  await new Promise((resolve) => setTimeout(resolve, 30))

  const s1 = JSON.parse(storage.getItem('caderno_draft_study_101'))
  const s2 = JSON.parse(storage.getItem('caderno_draft_study_102'))

  assert.equal(s1.title, 'Estudo 101')
  assert.equal(s2.title, 'Estudo 102')
})

test('useStudyDraft: restoreDraft detecta rascunho diferente e invoca onRestore', () => {
  const storage = new StorageMock()
  storage.setItem(
    'caderno_draft_study_7',
    JSON.stringify({
      studyId: 7,
      title: 'Título no rascunho',
      location: 'p. 15',
      sections: {
        summary: 'Resumo recuperado',
        explanation: 'Exp',
        concepts: '',
        references: '',
      },
      notes: 'Notas recuperadas',
      savedAt: Date.now(),
    })
  )

  let restoredPayload = null
  const current = {
    title: 'Título no servidor',
    location: 'p. 10',
    sections: {
      summary: 'Resumo no servidor',
      explanation: 'Exp',
      concepts: '',
      references: '',
    },
    notes: '',
  }

  const draft = useStudyDraft({
    studyId: 7,
    getCurrentData: () => current,
    onRestore: (payload) => {
      restoredPayload = payload
    },
    storage,
  })

  assert.equal(draft.hasDraft.value, true)
  const didRestore = draft.restoreDraft()

  assert.equal(didRestore, true)
  assert.equal(draft.isDraftRestored.value, true)
  assert.ok(restoredPayload !== null)
  assert.equal(restoredPayload.summary, undefined)
  assert.equal(restoredPayload.title, 'Título no rascunho')
  assert.equal(restoredPayload.sections.summary, 'Resumo recuperado')
  assert.equal(restoredPayload.notes, 'Notas recuperadas')
})

test('useStudyDraft: discardDraft remove o rascunho do storage e reseta flags', () => {
  const storage = new StorageMock()
  storage.setItem('caderno_draft_study_7', JSON.stringify({ studyId: 7, title: 'Draft' }))

  const draft = useStudyDraft({
    studyId: 7,
    getCurrentData: () => ({ title: 'Original', location: '', sections: { summary: '', explanation: '', concepts: '', references: '' }, notes: '' }),
    storage,
  })

  draft.restoreDraft()
  assert.equal(draft.isDraftRestored.value, true)

  draft.discardDraft()
  assert.equal(draft.isDraftRestored.value, false)
  assert.equal(draft.hasDraft.value, false)
  assert.equal(storage.getItem('caderno_draft_study_7'), null)
})

test('useStudyDraft: clearDraft limpa storage após salvamento definitivo', () => {
  const storage = new StorageMock()
  storage.setItem('caderno_draft_study_99', JSON.stringify({ studyId: 99, title: 'Salvo' }))

  const draft = useStudyDraft({
    studyId: 99,
    getCurrentData: () => ({ title: 'Salvo', location: '', sections: { summary: '', explanation: '', concepts: '', references: '' }, notes: '' }),
    storage,
  })

  draft.clearDraft()
  assert.equal(storage.getItem('caderno_draft_study_99'), null)
  assert.equal(draft.hasDraft.value, false)
})
