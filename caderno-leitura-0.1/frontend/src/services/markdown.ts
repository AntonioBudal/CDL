import mark from 'markdown-it-mark'
import MarkdownIt from 'markdown-it'

// Only this renderer may supply HTML to MarkdownContent. Raw source is never HTML.

const markdown = new MarkdownIt({ html: false, linkify: false, typographer: false })
markdown.use(mark)
markdown.disable('image')
const renderLink = markdown.renderer.rules.link_open
markdown.renderer.rules.link_open = (tokens, index, options, env, renderer) => {
  tokens[index]!.attrSet('target', '_blank')
  tokens[index]!.attrSet('rel', 'noopener noreferrer')
  return renderLink
    ? renderLink(tokens, index, options, env, renderer)
    : renderer.renderToken(tokens, index, options)
}

export function renderMarkdown(source: string): string {
  return markdown.render(source)
}
