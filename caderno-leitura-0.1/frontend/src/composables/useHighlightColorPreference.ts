import { computed, ref, type ComputedRef, type Ref } from 'vue'
import {
  HIGHLIGHT_COLORS,
  HIGHLIGHT_COLOR_HEX,
  HIGHLIGHT_COLOR_LABELS,
  type HighlightColor,
} from '../types/toolbar.ts'

export const HIGHLIGHT_COLOR_STORAGE_KEY = 'caderno_last_highlight_color'
export const DEFAULT_HIGHLIGHT_COLOR: HighlightColor = 'yellow'

export interface HighlightColorPreferenceReturn {
  activeColor: Ref<HighlightColor>
  colorHex: ComputedRef<string>
  colorLabel: ComputedRef<string>
  setColor: (color: HighlightColor) => void
  resetToDefault: () => void
}

function isValidHighlightColor(color: unknown): color is HighlightColor {
  return typeof color === 'string' && (HIGHLIGHT_COLORS as readonly string[]).includes(color)
}

function getStoredColor(): HighlightColor {
  try {
    const storage = typeof localStorage !== 'undefined' ? localStorage : null
    if (!storage) return DEFAULT_HIGHLIGHT_COLOR
    const stored = storage.getItem(HIGHLIGHT_COLOR_STORAGE_KEY)
    if (isValidHighlightColor(stored)) {
      return stored
    }
  } catch {
    // Falha silenciosa de acesso a storage (ex: navegação privada restrita)
  }
  return DEFAULT_HIGHLIGHT_COLOR
}

function persistColor(color: HighlightColor): void {
  try {
    const storage = typeof localStorage !== 'undefined' ? localStorage : null
    if (!storage) return
    storage.setItem(HIGHLIGHT_COLOR_STORAGE_KEY, color)
  } catch {
    // Falha silenciosa
  }
}

export function useHighlightColorPreference(): HighlightColorPreferenceReturn {
  const activeColor = ref<HighlightColor>(getStoredColor())

  const colorHex = computed(() => {
    return HIGHLIGHT_COLOR_HEX[activeColor.value] || HIGHLIGHT_COLOR_HEX[DEFAULT_HIGHLIGHT_COLOR]
  })

  const colorLabel = computed(() => {
    return HIGHLIGHT_COLOR_LABELS[activeColor.value] || HIGHLIGHT_COLOR_LABELS[DEFAULT_HIGHLIGHT_COLOR]
  })

  function setColor(color: HighlightColor) {
    if (isValidHighlightColor(color)) {
      activeColor.value = color
      persistColor(color)
    }
  }

  function resetToDefault() {
    activeColor.value = DEFAULT_HIGHLIGHT_COLOR
    persistColor(DEFAULT_HIGHLIGHT_COLOR)
  }

  return {
    activeColor,
    colorHex,
    colorLabel,
    setColor,
    resetToDefault,
  }
}
