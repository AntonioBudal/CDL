import type { HighlightLibraryItem } from '../types'

export type CitationFormat = 'abnt' | 'markdown' | 'plain'

export type CitationSourceItem = Pick<
  HighlightLibraryItem,
  'selected_text' | 'book_title' | 'book_author' | 'chapter_title'
>

/**
 * Formata o destaque no padrão acadêmico/ABNT:
 * "Trecho da citação." (AUTOR, Título da Obra, cap. Título do Capítulo).
 */
export function formatCitationABNT(item: CitationSourceItem): string {
  const quote = (item.selected_text || '').trim()
  const author = item.book_author?.trim() ? `${item.book_author.trim().toUpperCase()}, ` : ''
  const chapter = item.chapter_title?.trim() ? `, cap. ${item.chapter_title.trim()}` : ''
  const book = item.book_title?.trim() || 'Obra sem título'
  return `"${quote}" (${author}${book}${chapter}).`
}

/**
 * Formata o destaque no padrão Markdown com citação em bloco:
 * > Trecho da citação.
 * >
 * — Autor, *Título da Obra* (Capítulo)
 */
export function formatCitationMarkdown(item: CitationSourceItem): string {
  const quote = (item.selected_text || '').trim()
  const author = item.book_author?.trim() ? `— ${item.book_author.trim()}, ` : '— '
  const chapter = item.chapter_title?.trim() ? ` (${item.chapter_title.trim()})` : ''
  const book = item.book_title?.trim() || 'Obra sem título'
  return `> ${quote}\n>\n${author}*${book}*${chapter}`
}

/**
 * Formata o destaque em texto puro simples:
 * "Trecho da citação." — Autor - Título da Obra [Capítulo]
 */
export function formatCitationPlain(item: CitationSourceItem): string {
  const quote = (item.selected_text || '').trim()
  const author = item.book_author?.trim() ? `${item.book_author.trim()} - ` : ''
  const chapter = item.chapter_title?.trim() ? ` [${item.chapter_title.trim()}]` : ''
  const book = item.book_title?.trim() || 'Obra sem título'
  return `"${quote}" — ${author}${book}${chapter}`
}
