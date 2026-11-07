/**
 * Ganchos para referências em 3 escopos (F0.10.06, spec 099).
 *
 * Reúne, a partir dos dados que já existem, o que uma referência precisa:
 * - obra (livro): autor, título, subtítulo, ano;
 * - trecho (estudo): capítulo e localização interpretada;
 * - obras citadas: linhas da seção Referências do estudo.
 *
 * Módulo puro (sem Vue). O Roadmap 0.11 transforma estes escopos em CSL-JSON, BibTeX e ABNT/APA.
 */
import { abntAuthorCall } from './citationFormatter.ts'

export type LocatorKind = 'page' | 'loc' | 'raw' | 'none'

export interface Locator {
  kind: LocatorKind
  /** Valor normalizado: "32–34" para página, "1820" para posição, o texto original para `raw`. */
  value: string
}

export interface ReferenceBookInput {
  title?: string | null
  author?: string | null
  subtitle?: string | null
  year?: number | null
}

export interface ReferenceScopesInput {
  book?: ReferenceBookInput | null
  chapter?: { name?: string | null } | null
  location?: string | null
  referencesText?: string | null
}

export type WorkMissing = 'author' | 'year'

export interface ReferenceScopes {
  work: {
    title: string
    author: string
    subtitle: string
    year: number | null
    missing: WorkMissing[]
    complete: boolean
  }
  passage: {
    chapter: string
    locator: Locator
  }
  cited: {
    lines: string[]
    count: number
  }
}

function clean(value: string | null | undefined): string {
  return (value || '').replace(/\s+/g, ' ').trim()
}

/** Intervalos com meia-risca (ABNT): "32-34" e "32 – 34" viram "32–34". */
function normalizeRange(value: string): string {
  return value.replace(/\s*[-–—]+\s*/g, '–').replace(/\s+/g, ' ').trim()
}

const PAGE_PREFIX = /^(?:p[áa]g(?:ina)?s?\.?|pg\.?|p{1,2}\.?)\s*/i
const LOC_PREFIX = /^(?:loc(?:aliza[çc][ãa]o)?\.?|posi[çc][ãa]o|pos\.?)\s*/i
const NUMERIC_RANGE = /^\d+(?:\s*[-–—]+\s*\d+)?$/

/** Interpreta a localização livre do estudo ("p. 32–34", "Loc. 1820", "32-34"). */
export function parseLocator(location: string | null | undefined): Locator {
  const text = clean(location)
  if (!text) return { kind: 'none', value: '' }

  const pageRest = text.replace(PAGE_PREFIX, '')
  if (pageRest !== text && NUMERIC_RANGE.test(pageRest)) {
    return { kind: 'page', value: normalizeRange(pageRest) }
  }
  if (NUMERIC_RANGE.test(text)) {
    return { kind: 'page', value: normalizeRange(text) }
  }
  const locRest = text.replace(LOC_PREFIX, '')
  if (locRest !== text && NUMERIC_RANGE.test(locRest)) {
    return { kind: 'loc', value: normalizeRange(locRest) }
  }
  return { kind: 'raw', value: text }
}

/** Texto curto do localizador para a tela e para a chamada: "p. 32–34", "loc. 1820". */
export function formatLocator(locator: Locator): string {
  if (locator.kind === 'page') return `p. ${locator.value}`
  if (locator.kind === 'loc') return `loc. ${locator.value}`
  return locator.value
}

/** Linhas não vazias da seção Referências, sem marcadores de lista. */
export function referenceLines(text: string | null | undefined): string[] {
  return (text || '')
    .split(/\r?\n/)
    .map((line) => line.replace(/^\s*(?:[-*+•]|\d+[.)])\s+/, '').trim())
    .filter((line) => line.length > 0 && !/^#{1,6}\s/.test(line))
}

export function buildReferenceScopes(input: ReferenceScopesInput): ReferenceScopes {
  const book = input.book || {}
  const author = clean(book.author)
  const year = typeof book.year === 'number' && Number.isFinite(book.year) ? book.year : null
  const missing: WorkMissing[] = []
  if (!author) missing.push('author')
  if (year === null) missing.push('year')
  const lines = referenceLines(input.referencesText)
  return {
    work: {
      title: clean(book.title),
      author,
      subtitle: clean(book.subtitle),
      year,
      missing,
      complete: missing.length === 0,
    },
    passage: {
      chapter: clean(input.chapter?.name),
      locator: parseLocator(input.location),
    },
    cited: { lines, count: lines.length },
  }
}

/**
 * Chamada ABNT (NBR 10520:2023) com o localizador quando ele for de página ou posição:
 * "(Fictícia, 2001, p. 32–34)". Sem ano: "[s. d.]".
 */
export function abntCallWithLocator(scopes: ReferenceScopes): string {
  const parts = [
    abntAuthorCall(scopes.work.author, scopes.work.title),
    scopes.work.year ? String(scopes.work.year) : '[s. d.]',
  ]
  const { locator } = scopes.passage
  if (locator.kind === 'page' || locator.kind === 'loc') parts.push(formatLocator(locator))
  return `(${parts.join(', ')})`
}

/**
 * Citação indireta (texto do leitor) com a chamada ABNT e o localizador do estudo (F0.10.10):
 * "trecho (Fictícia, 2001, p. 32–34)." Quebras de linha viram espaço; ponto final do trecho não se repete.
 */
export function formatIndirectCitationWithLocator(text: string, scopes: ReferenceScopes): string {
  const body = (text || '').replace(/\s+/g, ' ').trim().replace(/[.\s]+$/, '')
  return `${body} ${abntCallWithLocator(scopes)}.`
}
