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

export function replaceStudyMentions(html: string): string {
  if (!html) return ''
  const codeBlocks: string[] = []
  const protectedHtml = html.replace(/(<code\b[^>]*>[\s\S]*?<\/code>|<pre\b[^>]*>[\s\S]*?<\/pre>)/gi, (match) => {
    codeBlocks.push(match)
    return `__CODE_BLOCK_${codeBlocks.length - 1}__`
  })

  const replaced = protectedHtml.replace(/\[\[([^\]|]+?)(?:\s*\|\s*([^\]]+?))?\]\]/g, (_match, rawTitle, rawId) => {
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

