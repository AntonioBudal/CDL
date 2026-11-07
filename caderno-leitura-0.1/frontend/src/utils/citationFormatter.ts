import type { HighlightLibraryItem } from '../types'

export type CitationFormat = 'abnt' | 'reference' | 'markdown' | 'plain'

export type CitationSourceItem = Pick<
  HighlightLibraryItem,
  'selected_text' | 'book_title' | 'book_author' | 'chapter_title'
> &
  Partial<Pick<HighlightLibraryItem, 'book_year' | 'book_subtitle'>>

/** Sufixos que a ABNT agrega ao sobrenome (SILVA JÚNIOR, COSTA NETO). */
const SURNAME_SUFFIXES = new Set(['junior', 'júnior', 'jr', 'jr.', 'filho', 'neto', 'sobrinho'])

const NO_DATE = '[s. d.]'
const UNTITLED = 'Obra sem título'

function clean(value: string | null | undefined): string {
  return (value || '').replace(/\s+/g, ' ').trim()
}

/** Separa a autoria em pessoas: ";", " e ", " and " ou "&". */
export function splitAuthors(author: string | null | undefined): string[] {
  const text = clean(author)
  if (!text) return []
  return text
    .split(/\s*;\s*|\s+e\s+|\s+and\s+|\s*&\s*/i)
    .map((part) => part.trim())
    .filter(Boolean)
}

interface PersonName {
  surname: string
  given: string
}

/** Aceita "Nome Sobrenome" e "Sobrenome, Nome"; agrega Júnior, Filho, Neto e Sobrinho ao sobrenome. */
export function parsePersonName(name: string): PersonName {
  const text = clean(name)
  if (text.includes(',')) {
    const [surname = '', ...rest] = text.split(',')
    return { surname: surname.trim(), given: rest.join(',').trim() }
  }
  const words = text.split(' ').filter(Boolean)
  if (words.length <= 1) return { surname: text, given: '' }
  let take = 1
  const last = words[words.length - 1]!.toLowerCase()
  if (SURNAME_SUFFIXES.has(last) && words.length > 2) take = 2
  return {
    surname: words.slice(-take).join(' '),
    given: words.slice(0, -take).join(' '),
  }
}

/** Primeira palavra do título seguida de reticências (entrada pelo título, NBR 10520:2023). */
function titleEntry(title: string | null | undefined): string {
  const first = clean(title).split(' ')[0]
  return first ? `${first}...` : `${UNTITLED.split(' ')[0]}...`
}

/**
 * Chamada de autoria da NBR 10520:2023 (sobrenome em maiúsculas e minúsculas):
 * 1 autor → "Manguel"; 2 ou 3 → "Manguel; Borges"; 4 ou mais → "Manguel et al."; sem autor → "Título...".
 */
export function abntAuthorCall(author: string | null | undefined, title?: string | null): string {
  const people = splitAuthors(author)
  if (people.length === 0) return titleEntry(title)
  const surnames = people.map((person) => parsePersonName(person).surname)
  if (surnames.length >= 4) return `${surnames[0]} et al.`
  return surnames.join('; ')
}

function yearOf(item: CitationSourceItem): string {
  return item.book_year ? String(item.book_year) : NO_DATE
}

/** Na citação direta, aspas duplas internas viram simples. */
function normalizeQuote(text: string): string {
  return clean(text).replace(/[“”"]/g, "'")
}

function stripFinalPeriod(text: string): string {
  return text.replace(/[.\s]+$/, '')
}

/**
 * Citação no padrão ABNT.
 * - literal (palavras do autor): citação direta `"trecho" (Manguel, 1997).`
 * - texto do leitor: citação indireta `trecho (Manguel, 1997).`
 * Sem página no banco, a chamada sai sem `p.`.
 */
export function formatCitationABNT(
  item: CitationSourceItem,
  options: { literal?: boolean } = {}
): string {
  const call = `(${abntAuthorCall(item.book_author, item.book_title)}, ${yearOf(item)})`
  if (options.literal) {
    return `"${normalizeQuote(item.selected_text)}" ${call}.`
  }
  return `${stripFinalPeriod(clean(item.selected_text))} ${call}.`
}

function referenceAuthors(author: string | null | undefined): string {
  const people = splitAuthors(author)
  if (people.length === 0) return ''
  const formatted = people.map((person) => {
    const { surname, given } = parsePersonName(person)
    return given ? `${surname.toUpperCase()}, ${given}` : surname.toUpperCase()
  })
  if (formatted.length >= 4) return `${formatted[0]} et al.`
  return formatted.join('; ')
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/**
 * Referência (NBR 6023), só com os dados que o Leitorum guarda:
 * `MANGUEL, Alberto. Uma história da leitura: subtítulo. 1997.`
 * Devolve texto puro e HTML (título em itálico, para colar em editores de texto).
 */
export function formatReferenceABNT(item: CitationSourceItem): { text: string; html: string } {
  const authors = referenceAuthors(item.book_author)
  const title = clean(item.book_title) || UNTITLED
  const subtitle = clean(item.book_subtitle)
  const year = yearOf(item)
  const lead = authors ? `${stripFinalPeriod(authors)}. ` : ''
  const sub = subtitle ? `: ${subtitle}` : ''
  if (!authors) {
    // Entrada pelo título: primeira palavra em caixa alta, sem itálico.
    const [first = '', ...rest] = title.split(' ')
    const entry = [first.toUpperCase(), ...rest].join(' ')
    const text = `${entry}${sub}. ${year}.`
    return { text, html: escapeHtml(text) }
  }
  return {
    text: `${lead}${title}${sub}. ${year}.`,
    html: `${escapeHtml(lead)}<i>${escapeHtml(title)}</i>${escapeHtml(sub)}. ${escapeHtml(year)}.`,
  }
}

/**
 * Markdown com citação em bloco:
 * > Trecho da citação.
 * >
 * — Autor, *Título da Obra* (1997), Capítulo
 */
export function formatCitationMarkdown(item: CitationSourceItem): string {
  const lines = (item.selected_text || '')
    .trim()
    .split(/\r?\n/)
    .map((line) => `> ${line.trim()}`.trimEnd())
  const author = clean(item.book_author) ? `— ${clean(item.book_author)}, ` : '— '
  const book = clean(item.book_title) || UNTITLED
  const year = item.book_year ? ` (${item.book_year})` : ''
  const chapter = clean(item.chapter_title) ? `, ${clean(item.chapter_title)}` : ''
  return `${lines.join('\n')}\n>\n${author}*${book}*${year}${chapter}`
}

/**
 * Texto puro simples:
 * "Trecho da citação." — Autor - Título da Obra [Capítulo]
 */
export function formatCitationPlain(item: CitationSourceItem): string {
  const quote = (item.selected_text || '').trim()
  const author = item.book_author?.trim() ? `${item.book_author.trim()} - ` : ''
  const chapter = item.chapter_title?.trim() ? ` [${item.chapter_title.trim()}]` : ''
  const book = item.book_title?.trim() || UNTITLED
  return `"${quote}" — ${author}${book}${chapter}`
}
