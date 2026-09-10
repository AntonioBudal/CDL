import { computed, reactive } from 'vue'
import { ApiError, errorMessage } from '../services/api.ts'
import { positiveId, SECTION_LABELS } from '../types.ts'
import type { AnalysisSections, ImportPreview, Study, StudyCreate } from '../types.ts'

interface ImportGateway {
  preview: (source: string) => Promise<ImportPreview>
  createStudy: (payload: StudyCreate) => Promise<Study>
}

const emptySections = (): AnalysisSections => ({ summary: '', explanation: '', concepts: '', references: '' })

export function useImportDraft(gateway: ImportGateway) {
  const state = reactive({
    bookId: '', chapterId: '', title: '', location: '', sourceResponse: '', notes: '',
    sections: emptySections(), preview: null as ImportPreview | null, saved: null as Study | null,
    preparing: false, saving: false, previewError: '', saveError: '',
  })
  const stale = computed(() => state.preview !== null && state.sourceResponse !== state.preview.source_response)
  const hasManualChanges = computed(() => state.preview !== null && SECTION_LABELS.some(({ key }) => state.sections[key] !== state.preview?.[key]))
  const hasAnalysis = computed(() => SECTION_LABELS.some(({ key }) => state.sections[key].trim()))
  const dirty = computed(() => state.saved === null && !!(state.sourceResponse || state.title || state.location || state.notes
    || SECTION_LABELS.some(({ key }) => state.sections[key])))
  const canSave = computed(() => state.preview !== null && !stale.value && hasAnalysis.value
    && positiveId(state.bookId) !== null && positiveId(state.chapterId) !== null
    && !state.preparing && !state.saving && state.saved === null)

  async function prepare(): Promise<boolean> {
    if (state.preparing || state.saving || state.saved) return false
    if (!state.sourceResponse.trim()) { state.previewError = 'Cole a resposta do ChatGPT.'; return false }
    const source = state.sourceResponse
    state.preparing = true
    state.previewError = ''
    try {
      const preview = await gateway.preview(source)
      if (state.sourceResponse !== source) {
        state.previewError = 'O texto mudou durante a preparação. Prepare a prévia novamente.'
        return false
      }
      state.preview = preview
      for (const { key } of SECTION_LABELS) state.sections[key] = preview[key]
      state.saveError = ''
      return true
    } catch (error) {
      state.previewError = errorMessage(error)
      return false
    } finally { state.preparing = false }
  }

  async function save(): Promise<Study | null> {
    if (state.saving || state.preparing || state.saved) return null
    if (!canSave.value || !state.preview) {
      state.saveError = stale.value
        ? 'A resposta foi alterada. Prepare uma nova prévia antes de salvar.'
        : 'Escolha o livro e o capítulo, prepare a prévia e preencha ao menos uma seção.'
      return null
    }
    const payload: StudyCreate = {
      chapter_id: positiveId(state.chapterId)!, title: state.title.trim() || null, location: state.location,
      source_response: state.preview.source_response, ...state.sections, notes: state.notes,
    }
    state.saving = true
    state.saveError = ''
    try {
      const saved = await gateway.createStudy(payload)
      state.saved = saved
      return saved
    } catch (error) {
      state.saveError = error instanceof ApiError && error.status === 0
        ? 'Não foi possível confirmar o salvamento. Seus textos continuam aqui. Confira os estudos do capítulo antes de reenviar.'
        : errorMessage(error)
      return null
    } finally { state.saving = false }
  }

  function reset() {
    if (state.saving || state.preparing) return
    state.title = ''; state.location = ''; state.sourceResponse = ''; state.notes = ''
    state.sections = emptySections(); state.preview = null; state.saved = null
    state.previewError = ''; state.saveError = ''
  }

  return { state, stale, hasManualChanges, hasAnalysis, canSave, dirty, prepare, save, reset }
}
