/**
 * Referências em 3 escopos (F0.11.05, spec 107): obra, trecho e obras citadas, em ABNT (NBR 6023), APA (7ª ed.),
 * BibTeX e CSL-JSON. Puro (sem Vue). Usa só os dados que o Leitorum guarda; nada é inventado.
 */
import { CONTENT_LOCALE } from '../i18n/content.ts'
import { abntAuthorCall, formatReferenceABNT, parsePersonName, splitAuthors } from './citationFormatter.ts'
import { formatLocator, parseLocator, type Locator } from './referenceScopes.ts'

export type ReferenceFormat = 'abnt' | 'apa' | 'bibtex' | 'csl'

export interface ReferenceBook {
  title: string
  subtitle?: string | null
  author?: string | null
  year?: number | null
  publisher?: string | null
  publication_place?: string | null
  isbn?: string | null
}

export interface ReferencePassage {
  chapter?: string | null
  location?: string | null
}

export interface ReferenceOutput {
  text: string
  html: string
}

export const REFERENCE_FORMATS: readonly { value: ReferenceFormat; label: string; extension: string; mime: string }[] = [
  { value: 'abnt', label: 'ABNT', extension: 'txt', mime: 'text/plain' },
  { value: 'apa', label: 'APA', extension: 'txt', mime: 'text/plain' },
  { value: 'bibtex', label: 'BibTeX', extension: 'bib', mime: 'application/x-bibtex' },
  { value: 'csl', label: 'CSL-JSON', extension: 'json', mime: 'application/json' },
] as const

interface Person {
  family: string
  given: string
}

function clean(value: string | null | undefined): string {
  return (value || '').replace(/\s+/g, ' ').trim()
}

function people(author: string | null | undefined): Person[] {
  return splitAuthors(author).map((name) => {
    const { surname, given } = parsePersonName(name)
    return { family: surname, given }
  })
}

function escapeHtml(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function fullTitle(book: ReferenceBook): string {
  const title = clean(book.title) || 'Obra sem título'
  const subtitle = clean(book.subtitle)
  return subtitle ? `${title}: ${subtitle}` : title
}

/** Campos que faltam para uma referência completa (para o aviso do painel). */
export function missingReferenceFields(book: ReferenceBook): string[] {
  const missing: string[] = []
  if (!clean(book.author)) missing.push('autor')
  if (!book.year) missing.push('ano')
  if (!clean(book.publisher)) missing.push('editora')
  if (!clean(book.publication_place)) missing.push('local')
  return missing
}

// ---------- ABNT ----------

export function toABNT(book: ReferenceBook): ReferenceOutput {
  return formatReferenceABNT({
    selected_text: '',
    book_title: clean(book.title),
    book_subtitle: clean(book.subtitle),
    book_author: book.author ?? null,
    book_year: book.year ?? null,
    book_publisher: book.publisher ?? null,
    book_publication_place: book.publication_place ?? null,
    chapter_title: '',
  })
}

function rangeText(locator: Locator): string {
  return formatLocator(locator)
}

/** Chamada ABNT com a localização do trecho: "(Fictícia, 2001, p. 32–34)". */
export function abntInTextCall(book: ReferenceBook, passage?: ReferencePassage): string {
  const parts = [abntAuthorCall(book.author, book.title), book.year ? String(book.year) : '[s. d.]']
  const locator = parseLocator(passage?.location)
  if (locator.kind === 'page' || locator.kind === 'loc') parts.push(rangeText(locator))
  return `(${parts.join(', ')})`
}

// ---------- APA ----------

const PARTICLES = new Set(['de', 'da', 'do', 'dos', 'das', 'e', 'van', 'von', 'der', 'di', 'du', 'la', 'le'])

function initials(given: string): string {
  return given
    .split(/\s+/)
    .filter((part) => part && !PARTICLES.has(part.toLowerCase()))
    .map((part) => part.split('-').map((piece) => `${piece.charAt(0).toUpperCase()}.`).join('-'))
    .join(' ')
}

function apaName(person: Person): string {
  const init = initials(person.given)
  return init ? `${person.family}, ${init}` : person.family
}

function apaAuthors(list: Person[]): string {
  const names = list.map(apaName)
  if (names.length === 1) return names[0]!
  if (names.length <= 20) return `${names.slice(0, -1).join(', ')}, & ${names[names.length - 1]}`
  return `${names.slice(0, 19).join(', ')}, . . . ${names[names.length - 1]}`
}

export function toAPA(book: ReferenceBook): ReferenceOutput {
  const list = people(book.author)
  const year = book.year ? `(${book.year}).` : '(s.d.).'
  const title = fullTitle(book)
  const publisher = clean(book.publisher)
  const tail = publisher ? ` ${publisher}.` : ''
  if (list.length === 0) {
    return {
      text: `${title}. ${year}${tail}`,
      html: `<i>${escapeHtml(title)}</i>. ${escapeHtml(year)}${escapeHtml(tail)}`,
    }
  }
  const authors = apaAuthors(list)
  const lead = authors.endsWith('.') ? authors : `${authors}.`
  return {
    text: `${lead} ${year} ${title}.${tail}`,
    html: `${escapeHtml(lead)} ${escapeHtml(year)} <i>${escapeHtml(title)}</i>.${escapeHtml(tail)}`,
  }
}

/** Chamada APA: "(Fictícia, 2001, p. 32)", "(A & B, 2001, pp. 32–34)", "(A et al., 2001)". */
export function apaInTextCall(book: ReferenceBook, passage?: ReferencePassage): string {
  const list = people(book.author)
  let who: string
  if (list.length === 0) who = clean(book.title) || 'Obra sem título'
  else if (list.length === 1) who = list[0]!.family
  else if (list.length === 2) who = `${list[0]!.family} & ${list[1]!.family}`
  else who = `${list[0]!.family} et al.`
  const parts = [who, book.year ? String(book.year) : 's.d.']
  const locator = parseLocator(passage?.location)
  if (locator.kind === 'page') parts.push(`${locator.value.includes('–') ? 'pp.' : 'p.'} ${locator.value}`)
  else if (locator.kind === 'loc') parts.push(`pos. ${locator.value}`)
  return `(${parts.join(', ')})`
}

// ---------- BibTeX ----------

function ascii(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '')
}

export function bibtexKey(book: ReferenceBook): string {
  const family = people(book.author)[0]?.family ?? ''
  const titleWord = clean(book.title)
    .split(' ')
    .map(ascii)
    .find((word) => word.length > 3) ?? ascii(clean(book.title).split(' ')[0] ?? '')
  return `${ascii(family) || 'anon'}${book.year ?? 'sd'}${titleWord || 'obra'}`
}

const BIBTEX_ESCAPES: Record<string, string> = {
  '\\': '\\textbackslash{}',
  '~': '\\textasciitilde{}',
  '^': '\\textasciicircum{}',
}

/** Escapa numa passada só (escapar em etapas faria as chaves de \textbackslash{} serem escapadas de novo). */
export function escapeBibtex(text: string): string {
  return text.replace(/[\\{}%&$#_~^]/g, (char) => BIBTEX_ESCAPES[char] ?? `\\${char}`)
}

export function toBibTeX(book: ReferenceBook, passage?: ReferencePassage, key = bibtexKey(book)): string {
  const fields: [string, string][] = []
  const list = people(book.author)
  if (list.length) {
    // Nome único fica entre chaves para o BibTeX não o tratar como "Nome Sobrenome".
    fields.push(['author', list.map((p) => (p.given ? `${escapeBibtex(p.family)}, ${escapeBibtex(p.given)}` : `{${escapeBibtex(p.family)}}`)).join(' and ')])
  }
  fields.push(['title', escapeBibtex(fullTitle(book))])
  if (book.year) fields.push(['year', String(book.year)])
  if (clean(book.publisher)) fields.push(['publisher', escapeBibtex(clean(book.publisher))])
  if (clean(book.publication_place)) fields.push(['address', escapeBibtex(clean(book.publication_place))])
  if (clean(book.isbn)) fields.push(['isbn', clean(book.isbn)])
  if (passage) {
    if (clean(passage.chapter)) fields.push(['chapter', escapeBibtex(clean(passage.chapter))])
    const locator = parseLocator(passage.location)
    if (locator.kind === 'page') fields.push(['pages', locator.value.replace('–', '--')])
    else if (locator.kind === 'loc') fields.push(['note', `pos. ${locator.value.replace('–', '--')}`])
    else if (locator.kind === 'raw') fields.push(['note', escapeBibtex(locator.value)])
  }
  const body = fields.map(([name, value]) => `  ${name} = {${value}}`).join(',\n')
  return `@book{${key},\n${body}\n}`
}

// ---------- CSL-JSON ----------

export interface CslItem {
  id: string
  type: 'book'
  title: string
  author?: ({ family: string; given?: string } | { literal: string })[]
  issued?: { 'date-parts': number[][] }
  publisher?: string
  'publisher-place'?: string
  ISBN?: string
  page?: string
  note?: string
}

export function toCSLItem(book: ReferenceBook, passage?: ReferencePassage, id = bibtexKey(book)): CslItem {
  const item: CslItem = { id, type: 'book', title: fullTitle(book) }
  const list = people(book.author)
  if (list.length) item.author = list.map((p) => (p.given ? { family: p.family, given: p.given } : { literal: p.family }))
  if (book.year) item.issued = { 'date-parts': [[book.year]] }
  if (clean(book.publisher)) item.publisher = clean(book.publisher)
  if (clean(book.publication_place)) item['publisher-place'] = clean(book.publication_place)
  if (clean(book.isbn)) item.ISBN = clean(book.isbn)
  if (passage) {
    const notes: string[] = []
    if (clean(passage.chapter)) notes.push(`cap. ${clean(passage.chapter)}`)
    const locator = parseLocator(passage.location)
    if (locator.kind === 'page') item.page = locator.value.replace('–', '-')
    else if (locator.kind === 'loc') notes.push(`pos. ${locator.value}`)
    else if (locator.kind === 'raw') notes.push(locator.value)
    if (notes.length) item.note = notes.join('; ')
  }
  return item
}

export function toCSL(book: ReferenceBook, passage?: ReferencePassage): string {
  return JSON.stringify([toCSLItem(book, passage)], null, 2)
}

// ---------- Saída única e bibliografia ----------

export function formatReference(book: ReferenceBook, format: ReferenceFormat, passage?: ReferencePassage): ReferenceOutput {
  if (format === 'abnt') return toABNT(book)
  if (format === 'apa') return toAPA(book)
  const text = format === 'bibtex' ? toBibTeX(book, passage) : toCSL(book, passage)
  return { text, html: `<pre>${escapeHtml(text)}</pre>` }
}

/** Chaves únicas: repetidas ganham sufixo a, b, c… (todas, inclusive a primeira). */
export function uniqueKeys(books: ReferenceBook[]): string[] {
  const base = books.map(bibtexKey)
  const counts = new Map<string, number>()
  base.forEach((key) => counts.set(key, (counts.get(key) ?? 0) + 1))
  const seen = new Map<string, number>()
  return base.map((key) => {
    if ((counts.get(key) ?? 0) < 2) return key
    const index = seen.get(key) ?? 0
    seen.set(key, index + 1)
    return `${key}${String.fromCharCode(97 + (index % 26))}`
  })
}

export function bibliography(books: ReferenceBook[], format: ReferenceFormat): string {
  if (format === 'abnt' || format === 'apa') {
    const texts = books.map((book) => (format === 'abnt' ? toABNT(book) : toAPA(book)).text)
    return texts.sort((a, b) => a.localeCompare(b, CONTENT_LOCALE)).join('\n\n') + '\n'
  }
  const keys = uniqueKeys(books)
  if (format === 'bibtex') return books.map((book, i) => toBibTeX(book, undefined, keys[i])).join('\n\n') + '\n'
  return JSON.stringify(books.map((book, i) => toCSLItem(book, undefined, keys[i])), null, 2) + '\n'
}
