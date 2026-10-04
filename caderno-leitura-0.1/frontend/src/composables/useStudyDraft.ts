import { ref, toValue, type MaybeRefOrGetter } from 'vue'
import type { AnalysisSections, StudyEditorDraftPayload } from '../types'

export interface UseStudyDraftOptions {
  studyId: MaybeRefOrGetter<number | undefined>
  getCurrentData: () => {
    title: string
    location: string
    sections: AnalysisSections
    notes: string
  }
  onRestore?: (draft: StudyEditorDraftPayload) => void
  debounceMs?: number
  storage?: Storage
}

export function getStudyDraftKey(studyId: number): string {
  return `caderno_draft_study_${studyId}`
}

export function useStudyDraft(options: UseStudyDraftOptions) {
  const hasDraft = ref(false)
  const isDraftRestored = ref(false)
  let timer: ReturnType<typeof setTimeout> | null = null

  function getStorage(): Storage | null {
    if (options.storage) return options.storage
    if (typeof window !== 'undefined' && window.sessionStorage) return window.sessionStorage
    if (typeof sessionStorage !== 'undefined') return sessionStorage
    return null
  }

  function resolveId(): number | undefined {
    return toValue(options.studyId)
  }

  function checkHasDraft(): boolean {
    const id = resolveId()
    if (!id) {
      hasDraft.value = false
      return false
    }
    const storage = getStorage()
    if (!storage) {
      hasDraft.value = false
      return false
    }
    const key = getStudyDraftKey(id)
    const exists = storage.getItem(key) !== null
    hasDraft.value = exists
    return exists
  }

  checkHasDraft()

  function saveDraft() {
    const id = resolveId()
    if (!id) return
    const storage = getStorage()
    if (!storage) return

    if (timer) clearTimeout(timer)
    const delay = options.debounceMs ?? 500

    timer = setTimeout(() => {
      const current = options.getCurrentData()
      const payload: StudyEditorDraftPayload = {
        studyId: id,
        title: current.title,
        location: current.location,
        sections: current.sections,
        notes: current.notes,
        savedAt: Date.now(),
      }
      try {
        storage.setItem(getStudyDraftKey(id), JSON.stringify(payload))
        hasDraft.value = true
      } catch (err) {
        console.warn('[useStudyDraft] Falha ao salvar rascunho no sessionStorage:', err)
      }
    }, delay)
  }

  function restoreDraft(): boolean {
    const id = resolveId()
    if (!id) return false
    const storage = getStorage()
    if (!storage) return false

    const raw = storage.getItem(getStudyDraftKey(id))
    if (!raw) {
      hasDraft.value = false
      return false
    }

    try {
      const parsed: StudyEditorDraftPayload = JSON.parse(raw)
      if (options.onRestore) {
        options.onRestore(parsed)
      }
      isDraftRestored.value = true
      hasDraft.value = true
      return true
    } catch (err) {
      console.warn('[useStudyDraft] Falha ao restaurar rascunho:', err)
      return false
    }
  }

  function discardDraft() {
    const id = resolveId()
    if (timer) clearTimeout(timer)
    isDraftRestored.value = false
    hasDraft.value = false
    if (!id) return
    const storage = getStorage()
    if (storage) {
      storage.removeItem(getStudyDraftKey(id))
    }
  }

  function clearDraft() {
    const id = resolveId()
    if (timer) clearTimeout(timer)
    isDraftRestored.value = false
    hasDraft.value = false
    if (!id) return
    const storage = getStorage()
    if (storage) {
      storage.removeItem(getStudyDraftKey(id))
    }
  }

  return {
    hasDraft,
    isDraftRestored,
    checkHasDraft,
    saveDraft,
    restoreDraft,
    discardDraft,
    clearDraft,
  }
}
