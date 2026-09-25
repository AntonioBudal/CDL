import { computed, reactive } from 'vue'
import { ApiError, ConcurrencyConflictApiError, errorMessage } from '../services/api.ts'
import { SECTION_LABELS, type AnalysisSections, type ConflictData, type Study, type StudyPatch } from '../types.ts'

interface EditGateway {
  updateStudy: (id: number, patch: StudyPatch) => Promise<Study>
  getStudy?: (id: number) => Promise<Study>
}

const emptySections = (): AnalysisSections => ({
  summary: '',
  explanation: '',
  concepts: '',
  references: '',
})

export function useStudyEdit(gateway: EditGateway) {
  const state = reactive({
    original: null as Study | null,
    title: '',
    location: '',
    notes: '',
    sections: emptySections(),
    saving: false,
    error: '',
    isConflict: false,
    conflictMessage: '',
    conflictData: null as ConflictData | null,
  })

  function load(study: Study) {
    state.original = { ...study }
    state.title = study.title
    state.location = study.location
    state.notes = study.notes
    for (const { key } of SECTION_LABELS) state.sections[key] = study[key]
    state.error = ''
    state.isConflict = false
    state.conflictMessage = ''
    state.conflictData = null
  }

  function clear() {
    state.original = null
    state.title = ''
    state.location = ''
    state.notes = ''
    state.sections = emptySections()
    state.error = ''
    state.isConflict = false
    state.conflictMessage = ''
    state.conflictData = null
  }

  const patch = computed<StudyPatch>(() => {
    const original = state.original
    if (!original) return {}
    const changes: StudyPatch = {}
    if (state.title.trim() !== original.title) changes.title = state.title.trim()
    if (state.location !== original.location) changes.location = state.location
    if (state.notes !== original.notes) changes.notes = state.notes
    for (const { key } of SECTION_LABELS) {
      if (state.sections[key] !== original[key]) changes[key] = state.sections[key]
    }
    return changes
  })

  const dirty = computed(() => Object.keys(patch.value).length > 0)
  const hasAnalysis = computed(() => SECTION_LABELS.some(({ key }) => state.sections[key].trim()))
  const canSave = computed(() => dirty.value && !!state.title.trim() && hasAnalysis.value && !state.saving)

  async function save(): Promise<Study | null> {
    if (!state.original || state.saving || !dirty.value) return null
    if (!canSave.value) {
      state.error = 'Preencha o título e ao menos uma das quatro seções.'
      return null
    }

    const id = state.original.id
    const changes: StudyPatch = {
      ...patch.value,
      expected_version: state.original.version ?? 1,
      expected_updated_at: state.original.updated_at ?? null,
    }

    state.saving = true
    state.error = ''

    try {
      const saved = await gateway.updateStudy(id, changes)
      load(saved)
      return saved
    } catch (error) {
      if (error instanceof ConcurrencyConflictApiError) {
        state.isConflict = true
        state.conflictData = error.conflictData
        state.conflictMessage = error.message
        state.error = error.message
      } else if (error instanceof ApiError && error.status === 409) {
        state.isConflict = true
        if (error.data && typeof error.data === 'object' && 'server_version' in error.data) {
          state.conflictData = error.data as ConflictData
        }
        state.conflictMessage = errorMessage(error)
        state.error = errorMessage(error)
      } else if (error instanceof ApiError && error.status === 0) {
        state.error =
          'Não foi possível confirmar o salvamento. Suas alterações continuam aqui. Você pode tentar salvar novamente.'
      } else {
        state.error = errorMessage(error)
      }
      return null
    } finally {
      state.saving = false
    }
  }

  async function overwrite(): Promise<Study | null> {
    if (!state.original) return null

    if (state.conflictData) {
      state.original.version = state.conflictData.server_version
      state.original.updated_at = state.conflictData.server_updated_at
    } else if (gateway.getStudy) {
      try {
        const latest = await gateway.getStudy(state.original.id)
        state.original.version = latest.version
        state.original.updated_at = latest.updated_at
      } catch {
        // Se a busca falhar, tenta salvar com o estado local
      }
    }

    state.isConflict = false
    state.conflictData = null
    state.conflictMessage = ''
    return save()
  }

  async function reload(): Promise<Study | null> {
    if (!state.original) return null

    if (state.conflictData?.server_data && Object.keys(state.conflictData.server_data).length > 0) {
      load(state.conflictData.server_data as unknown as Study)
      state.isConflict = false
      state.conflictData = null
      return state.original
    }

    if (gateway.getStudy) {
      try {
        state.saving = true
        const latest = await gateway.getStudy(state.original.id)
        load(latest)
        return latest
      } catch (err) {
        state.error = errorMessage(err)
      } finally {
        state.saving = false
      }
    }

    state.isConflict = false
    state.conflictData = null
    return null
  }

  function dismissConflict() {
    state.isConflict = false
  }

  return {
    state,
    dirty,
    hasAnalysis,
    canSave,
    load,
    clear,
    save,
    overwrite,
    reload,
    dismissConflict,
  }
}
