// F0.12.09 (spec 122): datas e números pelo idioma da interface. Única porta de entrada do idioma para formatos;
// fora de `src/i18n/` não se escreve 'pt-BR' (teste-guarda).
import { currentLocale } from './index.ts'
export { CONTENT_LOCALE } from './content.ts'

/** Idioma dos formatos da interface (datas, números). Ler dentro de computed/template mantém a reatividade. */
export function uiLocale(): string {
  return currentLocale()
}


function toDate(value: string | number | Date): Date {
  return value instanceof Date ? value : new Date(value)
}

export function formatDate(value: string | number | Date, options: Intl.DateTimeFormatOptions = {}): string {
  return toDate(value).toLocaleDateString(uiLocale(), options)
}

export function formatDateTime(value: string | number | Date, options: Intl.DateTimeFormatOptions = {}): string {
  return toDate(value).toLocaleString(uiLocale(), options)
}

export function formatNumber(value: number, options: Intl.NumberFormatOptions = {}): string {
  return new Intl.NumberFormat(uiLocale(), options).format(value)
}
