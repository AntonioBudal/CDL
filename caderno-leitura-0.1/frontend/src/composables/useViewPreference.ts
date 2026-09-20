import { ref, type Ref } from 'vue'
import { STUDY_VIEW_OPTIONS, type StudyViewMode, type StudyViewOption } from '../types.ts'

export const VIEW_GLOBAL_STORAGE_KEY = 'caderno_default_view'
export const VIEW_BOOK_STORAGE_KEY_PREFIX = 'caderno_preferred_view_'

const VALID_MODES: Set<StudyViewMode> = new Set(['grid', 'list', 'tree', 'map', 'canvas'])

export interface UseViewPreferenceOptions {
  bookId?: string | number | null
  initialMode?: StudyViewMode
  onModeChange?: (mode: StudyViewMode) => void
}

export interface UseViewPreferenceReturn {
  currentMode: Ref<StudyViewMode>
  activeStudyId: Ref<number | null>
  availableModes: StudyViewOption[]
  setMode: (mode: StudyViewMode) => void
  setActiveStudy: (id: number | null) => void
  resetToDefault: () => void
}

function getStorage(): Storage | null {
  if (typeof window !== 'undefined' && window.localStorage) {
    return window.localStorage
  }
  if (typeof localStorage !== 'undefined') {
    return localStorage
  }
  return null
}

/**
 * Lê preferência de visualização do localStorage:
 * 1. Chave específica da obra se bookId estiver presente
 * 2. Chave global de preferência da biblioteca
 * 3. Fallback null
 */
export function loadStoredViewPreference(bookId?: string | number | null): StudyViewMode | null {
  const storage = getStorage()
  if (!storage) {
    return null
  }

  try {
    if (bookId != null && String(bookId).trim() !== '') {
      const bookVal = storage.getItem(`${VIEW_BOOK_STORAGE_KEY_PREFIX}${bookId}`)
      if (bookVal && VALID_MODES.has(bookVal as StudyViewMode)) {
        return bookVal as StudyViewMode
      }
    }

    const globalVal = storage.getItem(VIEW_GLOBAL_STORAGE_KEY)
    if (globalVal && VALID_MODES.has(globalVal as StudyViewMode)) {
      return globalVal as StudyViewMode
    }
  } catch (err) {
    console.warn('[useViewPreference] Falha ao ler localStorage:', err)
  }

  return null
}

/**
 * Persiste preferência de visualização no localStorage com modelo híbrido
 */
export function saveStoredViewPreference(
  mode: StudyViewMode,
  bookId?: string | number | null
): void {
  const storage = getStorage()
  if (!storage) {
    return
  }

  if (!VALID_MODES.has(mode)) return

  try {
    if (bookId != null && String(bookId).trim() !== '') {
      storage.setItem(`${VIEW_BOOK_STORAGE_KEY_PREFIX}${bookId}`, mode)
    }
    // Atualiza a preferência global para que novas obras abram no modo favorito mais recente
    storage.setItem(VIEW_GLOBAL_STORAGE_KEY, mode)
  } catch (err) {
    console.warn('[useViewPreference] Falha ao gravar no localStorage:', err)
  }
}

export function useViewPreference(options: UseViewPreferenceOptions = {}): UseViewPreferenceReturn {
  const stored = loadStoredViewPreference(options.bookId)
  const currentMode = ref<StudyViewMode>(stored ?? options.initialMode ?? 'grid')
  const activeStudyId = ref<number | null>(null)

  function setMode(mode: StudyViewMode): void {
    if (!VALID_MODES.has(mode)) return
    currentMode.value = mode
    saveStoredViewPreference(mode, options.bookId)
    options.onModeChange?.(mode)
  }

  function setActiveStudy(id: number | null): void {
    activeStudyId.value = id
  }

  function resetToDefault(): void {
    setMode('grid')
  }

  return {
    currentMode,
    activeStudyId,
    availableModes: STUDY_VIEW_OPTIONS,
    setMode,
    setActiveStudy,
    resetToDefault
  }
}
