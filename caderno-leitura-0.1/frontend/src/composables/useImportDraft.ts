import { computed, reactive } from 'vue'
import { ApiError, errorMessage } from '../services/api.ts'
import { positiveId, SECTION_LABELS } from '../types.ts'
import type { AnalysisSections, ImportPreview, Study, StudyCreate, StudyTemplateId } from '../types.ts'
import { toSuggestion } from '../types/organize.ts'
import type { OrganizerFeedbackRequest, OrganizerSuggestion, OrganizeRequest, OrganizeResult } from '../types/organize.ts'

interface ImportGateway {
  preview: (source: string) => Promise<ImportPreview>
  createStudy: (payload: StudyCreate) => Promise<Study>
  /** Organização nas 4 seções (feature 089); opcional. */
  organizeText?: (payload: OrganizeRequest, signal?: AbortSignal) => Promise<OrganizeResult>
  /** Registro silencioso do feedback do organizador (feature 091-B); só quando houve organização. */
  sendOrganizerFeedback?: (studyId: number, payload: OrganizerFeedbackRequest) => Promise<void>
}

interface OrganizeSnapshot {
  sections: AnalysisSections
  unassigned: string
}

const emptySections = (): AnalysisSections => ({ summary: '', explanation: '', concepts: '', references: '' })

export function useImportDraft(gateway: ImportGateway) {
  const state = reactive({
    bookId: '', chapterId: '', title: '', location: '', sourceResponse: '', notes: '',
    template_id: 'classico' as StudyTemplateId,
    sections: emptySections(), preview: null as ImportPreview | null, saved: null as Study | null,
    preparing: false, saving: false, previewError: '', saveError: '',
    organizing: false, organizeError: '', organizeSnapshot: null as OrganizeSnapshot | null,
  })
  // Sugestão da última organização, para o registro do feedback (091-B); fora do estado reativo, não aparece na tela.
  let suggestion: OrganizerSuggestion | null = null
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
    if (!state.sourceResponse.trim()) { state.previewError = 'Cole o texto-base do fichamento.'; return false }
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
      state.organizeSnapshot = null
      state.organizeError = ''
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
        ? 'O fichamento da fonte foi alterado. Prepare uma nova prévia antes de salvar.'
        : 'Escolha o livro e o capítulo, prepare a prévia e preencha ao menos uma seção.'
      return null
    }
    const sectionsToSave = { ...state.sections }
    if (state.preview.unassigned_text && state.preview.unassigned_text.trim()) {
      const unassigned = state.preview.unassigned_text.trim()
      const alreadyIncluded = SECTION_LABELS.some(({ key }) => sectionsToSave[key].includes(unassigned))
      if (!alreadyIncluded) {
        const currentExplanation = sectionsToSave.explanation.trim()
        sectionsToSave.explanation = currentExplanation
          ? `${currentExplanation}\n\n---\n**Conteúdo Adicional / Não Classificado:**\n${unassigned}`
          : unassigned
      }
    }
    const payload: StudyCreate = {
      chapter_id: positiveId(state.chapterId)!, title: state.title.trim() || null, location: state.location,
      source_response: state.preview.source_response, ...sectionsToSave, notes: state.notes,
      template_id: state.template_id || 'classico',
    }
    state.saving = true
    state.saveError = ''
    try {
      const saved = await gateway.createStudy(payload)
      state.saved = saved
      // Registro do feedback (091-B): em silêncio e sem esperar; uma falha nunca chega ao leitor (FR-007).
      const send = gateway.sendOrganizerFeedback
      const organizer = suggestion
      if (send && organizer) {
        Promise.resolve().then(() => send(saved.id, { origin: 'import', organizer })).catch(() => {})
      }
      return saved
    } catch (error) {
      state.saveError = error instanceof ApiError && error.status === 0
        ? 'Não foi possível confirmar o salvamento. Seus textos continuam aqui. Confira os estudos do capítulo antes de reenviar.'
        : errorMessage(error)
      return null
    } finally { state.saving = false }
  }

  async function handlePaste(text?: string): Promise<boolean> {
    if (typeof text === 'string') {
      state.sourceResponse = text
    }
    return prepare()
  }

  function assignUnassignedToSection(sectionKey: keyof AnalysisSections) {
    if (!state.preview || !state.preview.unassigned_text.trim()) return
    const unassigned = state.preview.unassigned_text.trim()
    const current = state.sections[sectionKey].trim()
    state.sections[sectionKey] = current ? `${current}\n\n${unassigned}` : unassigned
    state.preview.unassigned_text = ''
  }

  /** Distribui o texto não classificado entre as 4 seções (sugestão), guardando o estado para desfazer. */
  async function organizeUnassigned(): Promise<boolean> {
    const unassigned = state.preview?.unassigned_text ?? ''
    if (!gateway.organizeText || state.organizing || !state.preview || !unassigned.trim()) return false
    state.organizing = true
    state.organizeError = ''
    try {
      const result = await gateway.organizeText({ text: unassigned })
      if (!state.preview || state.preview.unassigned_text !== unassigned) return false
      state.organizeSnapshot = { sections: { ...state.sections }, unassigned }
      suggestion = toSuggestion(result, unassigned)
      for (const { key } of SECTION_LABELS) {
        const addition = result.sections[key]
        if (!addition) continue
        state.sections[key] = state.sections[key].trim() ? `${state.sections[key].trimEnd()}\n\n${addition}` : addition
      }
      state.preview.unassigned_text = ''
      return true
    } catch (error) {
      state.organizeError = errorMessage(error)
      return false
    } finally { state.organizing = false }
  }

  /** Desfaz a última organização: seções e texto não classificado voltam exatamente ao que eram. */
  function undoOrganize(): boolean {
    const snapshot = state.organizeSnapshot
    if (!snapshot || !state.preview) return false
    state.sections = { ...snapshot.sections }
    state.preview.unassigned_text = snapshot.unassigned
    state.organizeSnapshot = null
    if (suggestion) suggestion = { ...suggestion, outcome: 'reverted' }
    return true
  }

  function reset() {
    if (state.saving || state.preparing) return
    state.title = ''; state.location = ''; state.sourceResponse = ''; state.notes = ''
    state.template_id = 'classico'
    state.sections = emptySections(); state.preview = null; state.saved = null
    state.previewError = ''; state.saveError = ''
    state.organizeSnapshot = null; state.organizeError = ''
    suggestion = null
  }

  return {
    state,
    stale,
    hasManualChanges,
    hasAnalysis,
    canSave,
    dirty,
    prepare,
    handlePaste,
    assignUnassignedToSection,
    organizeUnassigned,
    undoOrganize,
    save,
    reset,
  }
}

