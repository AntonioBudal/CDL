import mark from 'markdown-it-mark'
import MarkdownIt from 'markdown-it'
import { isSafeUrl, sanitizeHtml } from './sanitizer.ts'

// Only this renderer may supply HTML to MarkdownContent. Raw source is never HTML.

const markdown = new MarkdownIt({ html: false, linkify: false, typographer: false })
markdown.use(mark)
markdown.disable('image')

// Validação estrita de URLs no parser Markdown-it
markdown.validateLink = (url: string) => isSafeUrl(url)

const renderLink = markdown.renderer.rules.link_open
markdown.renderer.rules.link_open = (tokens, index, options, env, renderer) => {
  const token = tokens[index]!
  const href = token.attrGet('href')
  if (!href || !isSafeUrl(href)) {
    token.attrSet('href', '#')
    token.attrSet('data-blocked-url', 'true')
  }
  token.attrSet('target', '_blank')
  token.attrSet('rel', 'noopener noreferrer')
  return renderLink
    ? renderLink(tokens, index, options, env, renderer)
    : renderer.renderToken(tokens, index, options)
}

/** Mesma chave do servidor (`concept_lexicon.concept_key`): sem acento, minúsculas, hífens. */
export function conceptKey(term: string): string {
  return term
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^0-9a-z]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function replaceStudyMentions(html: string): string {
  if (!html) return ''
  const codeBlocks: string[] = []
  const protectedHtml = html.replace(/(<code\b[^>]*>[\s\S]*?<\/code>|<pre\b[^>]*>[\s\S]*?<\/pre>)/gi, (match) => {
    codeBlocks.push(match)
    return `__CODE_BLOCK_${codeBlocks.length - 1}__`
  })

  // F0.11.06: [[conceito:Termo]] vira link para a página do conceito (antes das menções a estudos).
  const withConcepts = protectedHtml.replace(/\[\[\s*conceito\s*:\s*([^\]|]+?)\s*\]\]/gi, (_match, rawTerm) => {
    const term = String(rawTerm).trim()
    const key = conceptKey(term)
    if (!key) return _match
    return `<a href="/conceitos/${key}" class="study-concept-mention" data-concept-key="${key}" aria-label="conceito: ${term}">${term}</a>`
  })

  const replaced = withConcepts.replace(/\[\[([^\]|]+?)(?:\s*\|\s*([^\]]+?))?\]\]/g, (_match, rawTitle, rawId) => {
    const title = rawTitle.trim()
    const id = rawId && /^\d+$/.test(rawId.trim()) ? rawId.trim() : ''
    const dataIdAttr = id ? ` data-study-id="${id}"` : ''
    const href = id ? `/estudos/${id}` : '#'
    return `<a href="${href}" class="study-internal-mention"${dataIdAttr} data-study-title="${title}">${title}</a>`
  })

  return replaced.replace(/__CODE_BLOCK_(\d+)__/g, (_match, index) => codeBlocks[Number(index)] || '')
}

export function renderMarkdown(source: string): string {
  const rawHtml = markdown.render(source || '')
  const sanitized = sanitizeHtml(rawHtml)
  return replaceStudyMentions(sanitized)
}

