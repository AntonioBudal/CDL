export type SuperclassName = 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'
export type PreferredViewMode = 'grid' | 'list' | 'tree' | 'canvas' | 'cockpit'
export type FontFamilyPreference = 'garamond' | 'sans' | 'dyslexic'
export type ThemeModePreference = 'dark' | 'light' | 'e-ink'

export interface UserPreferences {
  user_id: string
  active_superclass: SuperclassName
  superclass_intensity: number
  preferred_view_mode: PreferredViewMode
  tree_collapsed_state: number[]
  font_family: FontFamilyPreference
  font_scale: number
  theme_mode: ThemeModePreference
  version: number
  updated_at: string
}

export interface UserPreferencesPatch {
  active_superclass?: SuperclassName
  superclass_intensity?: number
  preferred_view_mode?: PreferredViewMode
  tree_collapsed_state?: number[]
  font_family?: FontFamilyPreference
  font_scale?: number
  theme_mode?: ThemeModePreference
  expected_version?: number
}

export type UserPreferenceRead = UserPreferences
export type UserPreferenceUpdate = UserPreferencesPatch

