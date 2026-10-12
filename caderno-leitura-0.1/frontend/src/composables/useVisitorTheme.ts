import { ref, onMounted } from 'vue'
import { CANONICAL_THEME_PREVIEWS } from '../types/settings'
import type { CanonicalThemeId } from '../types/settings'

const VISITOR_THEME_STORAGE_KEY = 'caderno_visitor_theme'

export function useVisitorTheme() {
  const activeTheme = ref<CanonicalThemeId>('papel-fosco')
  const originalTheme = ref<string>('papel-fosco')
  const statusMessage = ref<string>('')

  function getThemeLabel(id: CanonicalThemeId): string {
    const item = CANONICAL_THEME_PREVIEWS.find((t) => t.id === id)
    return item ? item.label : id
  }

  function readStoredTheme(): CanonicalThemeId | null {
    if (typeof window === 'undefined' || !window.sessionStorage) return null
    try {
      const stored = window.sessionStorage.getItem(VISITOR_THEME_STORAGE_KEY)
      if (stored && CANONICAL_THEME_PREVIEWS.some((t) => t.id === stored)) {
        return stored as CanonicalThemeId
      }
    } catch {
      // sessionStorage indisponível ou permissão negada
    }
    return null
  }

  function saveStoredTheme(themeId: CanonicalThemeId) {
    if (typeof window === 'undefined' || !window.sessionStorage) return
    try {
      window.sessionStorage.setItem(VISITOR_THEME_STORAGE_KEY, themeId)
    } catch {
      // Degradação graciosa se sessionStorage estiver indisponível
    }
  }

  function applyTheme(themeId: CanonicalThemeId) {
    activeTheme.value = themeId
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.theme = themeId
    }
    saveStoredTheme(themeId)
    const label = getThemeLabel(themeId)
    statusMessage.value = `Tema aplicado: ${label}. A página inteira foi repintada.`
  }

  function resetToOriginal() {
    if (typeof document !== 'undefined' && originalTheme.value) {
      document.documentElement.dataset.theme = originalTheme.value
    }
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        window.sessionStorage.removeItem(VISITOR_THEME_STORAGE_KEY)
      } catch {
        // Degradação graciosa
      }
    }
  }

  onMounted(() => {
    if (typeof document !== 'undefined') {
      const current = document.documentElement.dataset.theme
      if (current) {
        originalTheme.value = current
      }
      const stored = readStoredTheme()
      if (stored) {
        activeTheme.value = stored
        document.documentElement.dataset.theme = stored
      } else if (current && CANONICAL_THEME_PREVIEWS.some((t) => t.id === current)) {
        activeTheme.value = current as CanonicalThemeId
      }
    }
  })

  // Não chamamos resetToOriginal() no onBeforeUnmount para que a preferência do visitante
  // persista durante toda a sua navegação entre rotas públicas (/ , /sobre, /apoie).

  return {
    activeTheme,
    originalTheme,
    statusMessage,
    applyTheme,
    resetToOriginal,
  }
}
