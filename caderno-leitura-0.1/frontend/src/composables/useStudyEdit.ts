import { computed, reactive } from 'vue'
import { ApiError, errorMessage } from '../services/api.ts'
import { SECTION_LABELS, type AnalysisSections, type Study, type StudyPatch } from '../types.ts'

interface EditGateway { updateStudy: (id: number, patch: StudyPatch) => Promise<Study> }
const emptySections = (): AnalysisSections => ({ summary: '', explanation: '', concepts: '', references: '' })

export function useStudyEdit(gateway: EditGateway) {
  const state = reactive({
    original: null as Study | null, title: '', location: '', notes: '',
    sections: emptySections(), saving: false, error: '',
  })

  function load(study: Study) {
    state.original = { ...study }
    state.title = study.title
    state.location = study.location
    state.notes = study.notes
    for (const { key } of SECTION_LABELS) state.sections[key] = study[key]
    state.error = ''
  }

  function clear() {
    state.original = null
    state.title = ''; state.location = ''; state.notes = ''
    state.sections = emptySections(); state.error = ''
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
    const changes = { ...patch.value }
    state.saving = true
    state.error = ''
    try {
      const saved = await gateway.updateStudy(id, changes)
      load(saved)
      return saved
    } catch (error) {
      state.error = error instanceof ApiError && error.status === 0
        ? 'Não foi possível confirmar o salvamento. Suas alterações continuam aqui. Você pode tentar salvar novamente.'
        : errorMessage(error)
      return null
    } finally { state.saving = false }
  }

  return { state, dirty, hasAnalysis, canSave, load, clear, save }
}
