export type AppearancePreferences = {
  theme: 'porcelana' | 'breu' | 'pergaminho' | 'e-ink' | 'vespera'
  | 'solario' | 'fiorde' | 'vinil' | 'sequoia' | 'voltagem'
  font: 'inter' | 'merriweather' | 'lora' | 'roboto-serif' | 'source-serif-4'
  | 'literata' | 'eb-garamond' | 'libre-baskerville' | 'crimson-pro'
  | 'noto-serif' | 'bitter' | 'fira-sans' | 'source-sans-3' | 'noto-sans'
  | 'atkinson-hyperlegible' | 'opendyslexic' | 'nunito-sans'
  | 'ibm-plex-sans' | 'ibm-plex-serif' | 'jetbrains-mono' | 'victor-mono'
  | 'ibm-plex-mono' | 'source-code-pro' | 'roboto-mono'
  accent: 'theme' | 'blue' | 'green' | 'purple' | 'orange'
  density: 'standard' | 'compact' | 'comfortable'
  align: 'left' | 'justify'
  highlight: 'background' | 'underline' | 'bold'
  library: 'grid' | 'list'
  container: 'contained' | 'fluid'
  'reader-size': '100' | '110' | '120' | '130' | '140' | '150'
  | '160' | '170' | '180' | '190' | '200'
  superclass: 'none' | 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'
  'superclass-intensity': 'standard' | 'subtle' | 'high' | 'off'
}

export type AppearanceField = {
  key: keyof AppearancePreferences
  group: string
  label: string
  options: ReadonlyArray<readonly [string, string]>
}

declare global {
  interface Window {
    cadernoAppearance: {
      readonly version: number
      readonly fields: ReadonlyArray<AppearanceField>
      get(): AppearancePreferences
      set(value: Partial<AppearancePreferences>): boolean
      factoryReset(): boolean
      cleanOrphanKeys(): number
    }

    cadernoFontCatalog: {
  version: string
  options: ReadonlyArray<
    readonly [AppearancePreferences['font'], string]
  >
}
  }
}