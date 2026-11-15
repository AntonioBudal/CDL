// F0.12.09 (spec 122): idioma da interface. Só a fundação: os textos de toda tela, datas e avisos gerais; o resto da
// interface segue em português e migra aos poucos. Mensagens em objetos TypeScript (sem compilação por `eval`, o que a
// CSP `script-src 'self'` não permite).
import { createI18n } from 'vue-i18n'
import en from './messages/en.ts'
import ptBR from './messages/pt-BR.ts'

export const SUPPORTED_LOCALES = ['pt-BR', 'en'] as const
export type AppLocale = (typeof SUPPORTED_LOCALES)[number]
export const DEFAULT_LOCALE: AppLocale = 'pt-BR'
export const LOCALE_STORAGE_KEY = 'leitorum_locale'
/** Nome de cada idioma no próprio idioma (o seletor mostra assim nos dois). */
export const LOCALE_NAMES: Record<AppLocale, string> = { 'pt-BR': 'Português (Brasil)', en: 'English' }

export function isAppLocale(value: unknown): value is AppLocale {
  return typeof value === 'string' && (SUPPORTED_LOCALES as readonly string[]).includes(value)
}

/** Idioma inicial: o salvo no navegador; senão o do navegador, se for inglês; senão português. */
export function initialLocale(): AppLocale {
  try {
    const saved = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (isAppLocale(saved)) return saved
  } catch {
    // sem armazenamento local
  }
  const browser = typeof navigator !== 'undefined' ? navigator.language || '' : ''
  return browser.toLowerCase().startsWith('en') ? 'en' : DEFAULT_LOCALE
}

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { 'pt-BR': ptBR, en },
  missingWarn: false,
  fallbackWarn: false,
})

export function currentLocale(): AppLocale {
  return i18n.global.locale.value as AppLocale
}

/** Troca o idioma na hora: textos, `<html lang>` e a lembrança no navegador. */
export function setLocale(locale: AppLocale): void {
  i18n.global.locale.value = locale
  if (typeof document !== 'undefined') document.documentElement.lang = locale
  try {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  } catch {
    // sem armazenamento local: vale só nesta aba
  }
}

/** Texto por chave fora de componentes (avisos gerais, títulos da aba). */
export function t(key: string, params?: Record<string, unknown>): string {
  return params ? i18n.global.t(key, params) : i18n.global.t(key)
}

/** Título da tela pelo nome da rota; sem tradução, o título escrito na rota. */
export function routeTitle(name: unknown, fallback: string): string {
  const key = `titles.${String(name)}`
  return i18n.global.te(key) || i18n.global.te(key, DEFAULT_LOCALE) ? t(key) : fallback
}

if (typeof document !== 'undefined') document.documentElement.lang = currentLocale()
