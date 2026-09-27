import { computed, reactive } from 'vue'
import { preferencesApi } from '../api/preferences.ts'
import type {
  FontFamilyPreference,
  PreferredViewMode,
  SuperclassName,
  ThemeModePreference,
  UserPreferences,
  UserPreferencesPatch,
} from '../types.ts'

const STORAGE_KEY_PREFS = 'caderno_user_preferences'
const STORAGE_KEY_APPEARANCE = 'caderno.aparencia.v2'

export const CANONICAL_THEME_IDS = new Set<string>([
  'papel-fosco',
  'noite-suave',
  'cinza-neutro',
  'grafite',
  'monocromatico',
  'pergaminho',
  'e-ink',
  'solario',
  'fiorde',
  'voltagem',
])

export const LEGACY_THEME_MAP: Record<string, string> = {
  porcelana: 'papel-fosco',
  breu: 'noite-suave',
  vinil: 'grafite',
  sequoia: 'noite-suave',
  vespera: 'noite-suave',
  light: 'papel-fosco',
  dark: 'noite-suave',
  sepia: 'pergaminho',
}

export function resolveCanonicalTheme(theme: string | undefined | null): string {
  if (!theme) return 'papel-fosco'
  const mapped = LEGACY_THEME_MAP[theme] || theme
  return CANONICAL_THEME_IDS.has(mapped) ? mapped : 'papel-fosco'
}

const state = reactive({
  user_id: '',
  active_superclass: 'mecanica' as SuperclassName,
  superclass_intensity: 1.0,
  preferred_view_mode: 'grid' as PreferredViewMode,
  tree_collapsed_state: [] as number[],
  font_family: 'garamond' as FontFamilyPreference,
  font_scale: 1.0,
  theme_mode: 'papel-fosco' as ThemeModePreference,
  version: 1,
  updated_at: '',
  loading: false,
  error: null as string | null,
})

function applyPreferencesToDocument(prefs: Partial<UserPreferences>) {
  if (typeof document === 'undefined') return

  const root = document.documentElement

  if (prefs.active_superclass) {
    root.setAttribute('data-superclass', prefs.active_superclass)
  }
  if (typeof prefs.superclass_intensity === 'number') {
    root.style.setProperty('--sc-intensity', String(prefs.superclass_intensity))
  }
  if (prefs.theme_mode) {
    const canonical = resolveCanonicalTheme(prefs.theme_mode)
    root.setAttribute('data-theme', canonical)
    if (typeof window !== 'undefined' && window.cadernoAppearance?.get()?.theme !== canonical) {
      window.cadernoAppearance?.set({ theme: canonical as any })
    }
  }
  if (prefs.font_family) {
    root.setAttribute('data-font', prefs.font_family)
  }
  if (typeof prefs.font_scale === 'number') {
    root.style.setProperty('--font-scale', String(prefs.font_scale))
  }
}

export function usePreferences() {
  const activeSuperclass = computed(() => state.active_superclass)
  const superclassIntensity = computed(() => state.superclass_intensity)
  const preferredViewMode = computed(() => state.preferred_view_mode)
  const treeCollapsedState = computed(() => state.tree_collapsed_state)
  const fontFamily = computed(() => state.font_family)
  const fontScale = computed(() => state.font_scale)
  const themeMode = computed(() => state.theme_mode)
  const version = computed(() => state.version)
  const loading = computed(() => state.loading)
  const error = computed(() => state.error)

  function loadFromLocal(): void {
    if (typeof localStorage === 'undefined') return
    try {
      const rawAp = localStorage.getItem(STORAGE_KEY_APPEARANCE)
      if (rawAp) {
        const ap = JSON.parse(rawAp)
        if (ap && typeof ap.theme === 'string') {
          state.theme_mode = resolveCanonicalTheme(ap.theme) as ThemeModePreference
        }
      }

      const raw = localStorage.getItem(STORAGE_KEY_PREFS)
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<UserPreferences>
        if (parsed.theme_mode) {
          parsed.theme_mode = resolveCanonicalTheme(parsed.theme_mode) as ThemeModePreference
        } else {
          parsed.theme_mode = state.theme_mode
        }
        Object.assign(state, parsed)
      }
      applyPreferencesToDocument(state)
    } catch {
      // Falha silenciosa
    }
  }

  function saveToLocal(): void {
    if (typeof localStorage === 'undefined') return
    try {
      localStorage.setItem(STORAGE_KEY_PREFS, JSON.stringify(state))
    } catch {
      // Falha silenciosa
    }
  }

  async function loadPreferences(): Promise<UserPreferences | null> {
    state.loading = true
    state.error = null

    try {
      const prefs = await preferencesApi.getPreferences()
      Object.assign(state, prefs)
      saveToLocal()
      applyPreferencesToDocument(prefs)
      return prefs
    } catch (err: any) {
      state.error = err instanceof Error ? err.message : 'Falha ao carregar preferências'
      loadFromLocal()
      return null
    } finally {
      state.loading = false
    }
  }

  async function updatePreferences(patch: UserPreferencesPatch): Promise<UserPreferences | null> {
    state.loading = true
    state.error = null

    try {
      const payload: UserPreferencesPatch = {
        ...patch,
        expected_version: state.version,
      }
      const updated = await preferencesApi.updatePreferences(payload)
      Object.assign(state, updated)
      saveToLocal()
      applyPreferencesToDocument(updated)
      return updated
    } catch (err: any) {
      state.error = err instanceof Error ? err.message : 'Falha ao salvar preferências'
      // Em caso de erro, recarrega para sincronizar versão
      await loadPreferences()
      return null
    } finally {
      state.loading = false
    }
  }

  function handleSyncApplied(event: Event) {
    const customEvt = event as CustomEvent
    const prefs = customEvt.detail?.updated?.preferences
    if (prefs) {
      Object.assign(state, prefs)
      saveToLocal()
      applyPreferencesToDocument(prefs)
    }
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('caderno:sync-applied', handleSyncApplied)
  }

  return {
    activeSuperclass,
    superclassIntensity,
    preferredViewMode,
    treeCollapsedState,
    fontFamily,
    fontScale,
    themeMode,
    version,
    loading,
    error,
    loadPreferences,
    updatePreferences,
    loadFromLocal,
    applyPreferencesToDocument,
  }
}
