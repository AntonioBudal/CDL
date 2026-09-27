import { computed, ref, watch, type Ref } from 'vue'
import type {
  StudyHighlight,
  StudyHighlightCreatePayload,
  StudyHighlightUpdatePayload,
  StudySectionKey,
} from '../types.ts'
import { api, errorMessage } from '../services/api.ts'

export interface StudyHighlightsGateway {
  listStudyHighlights: (studyId: number, section?: string, signal?: AbortSignal) => Promise<StudyHighlight[]>
  createStudyHighlight: (studyId: number, payload: StudyHighlightCreatePayload) => Promise<StudyHighlight>
  updateStudyHighlight: (studyId: number, highlightId: number, payload: StudyHighlightUpdatePayload) => Promise<StudyHighlight>
  deleteStudyHighlight: (studyId: number, highlightId: number) => Promise<void>
}

export function useStudyHighlights(
  studyIdRef: Ref<number | undefined | null>,
  gateway: StudyHighlightsGateway = api,
) {
  const highlights = ref<StudyHighlight[]>([])
  const loading = ref(false)
  const error = ref('')

  // Gestão de popover para destaque clicado
  const activeHighlight = ref<StudyHighlight | null>(null)
  const popoverRect = ref<DOMRect | null>(null)

  async function loadHighlights(signal?: AbortSignal) {
    const id = studyIdRef.value
    if (!id) {
      highlights.value = []
      return
    }
    loading.value = true
    error.value = ''
    try {
      const data = await gateway.listStudyHighlights(id, undefined, signal)
      highlights.value = data
    } catch (err) {
      if ((err as Error)?.name === 'AbortError') return
      error.value = errorMessage(err)
    } finally {
      loading.value = false
    }
  }

  async function addHighlight(payload: StudyHighlightCreatePayload): Promise<StudyHighlight | null> {
    const id = studyIdRef.value
    if (!id) return null
    try {
      const created = await gateway.createStudyHighlight(id, payload)
      highlights.value = [...highlights.value, created]
      return created
    } catch (err) {
      error.value = errorMessage(err)
      return null
    }
  }

  async function editHighlight(
    highlightId: number,
    payload: StudyHighlightUpdatePayload,
  ): Promise<StudyHighlight | null> {
    const id = studyIdRef.value
    if (!id) return null
    try {
      const updated = await gateway.updateStudyHighlight(id, highlightId, payload)
      highlights.value = highlights.value.map((h) => (h.id === highlightId ? updated : h))
      if (activeHighlight.value?.id === highlightId) {
        activeHighlight.value = updated
      }
      return updated
    } catch (err) {
      error.value = errorMessage(err)
      return null
    }
  }

  async function removeHighlight(highlightId: number): Promise<boolean> {
    const id = studyIdRef.value
    if (!id) return false
    try {
      await gateway.deleteStudyHighlight(id, highlightId)
      highlights.value = highlights.value.filter((h) => h.id !== highlightId)
      if (activeHighlight.value?.id === highlightId) {
        closeHighlightPopover()
      }
      return true
    } catch (err) {
      error.value = errorMessage(err)
      return false
    }
  }

  function getHighlightsForSection(section: StudySectionKey) {
    return computed(() => highlights.value.filter((h) => h.section === section))
  }

  function openHighlightPopover(hl: StudyHighlight, rect: DOMRect) {
    activeHighlight.value = hl
    popoverRect.value = rect
  }

  function closeHighlightPopover() {
    activeHighlight.value = null
    popoverRect.value = null
  }

  watch(
    () => studyIdRef.value,
    () => {
      loadHighlights()
    },
    { immediate: true },
  )

  return {
    highlights,
    loading,
    error,
    activeHighlight,
    popoverRect,
    loadHighlights,
    addHighlight,
    editHighlight,
    removeHighlight,
    getHighlightsForSection,
    openHighlightPopover,
    closeHighlightPopover,
  }
}
