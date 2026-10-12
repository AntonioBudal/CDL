import { ref, onMounted, onBeforeUnmount } from 'vue'
import { CANONICAL_THEME_PREVIEWS } from '../types/settings'
import type { CanonicalThemeId } from '../types/settings'

export function useVisitorTheme() {
  const activeTheme = ref<CanonicalThemeId>('papel-fosco')
  const originalTheme = ref<string>('papel-fosco')
  const statusMessage = ref<string>('')

  function getThemeLabel(id: CanonicalThemeId): string {
    const item = CANONICAL_THEME_PREVIEWS.find((t) => t.id === id)
    return item ? item.label : id
  }

  function applyTheme(themeId: CanonicalThemeId) {
    activeTheme.value = themeId
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.theme = themeId
    }
    const label = getThemeLabel(themeId)
    statusMessage.value = `Tema aplicado: ${label}. A página inteira foi repintada.`
  }

  function resetToOriginal() {
    if (typeof document !== 'undefined' && originalTheme.value) {
      document.documentElement.dataset.theme = originalTheme.value
    }
  }

  onMounted(() => {
    if (typeof document !== 'undefined') {
      const current = document.documentElement.dataset.theme
      if (current) {
        originalTheme.value = current
        const exists = CANONICAL_THEME_PREVIEWS.some((t) => t.id === current)
        if (exists) {
          activeTheme.value = current as CanonicalThemeId
        }
      }
    }
  })

  onBeforeUnmount(() => {
    resetToOriginal()
  })

  return {
    activeTheme,
    originalTheme,
    statusMessage,
    applyTheme,
    resetToOriginal,
  }
}
