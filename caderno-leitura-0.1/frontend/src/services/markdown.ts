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

export function renderMarkdown(source: string): string {
  const rawHtml = markdown.render(source || '')
  return sanitizeHtml(rawHtml)
}
