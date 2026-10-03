/**
 * Sanitizador leve e estrito para HTML gerado a partir de Markdown no Leitorum.
 * Neutraliza injeções XSS (tags executáveis, manipuladores on* e esquemas perigosos)
 * preservando integralmente nós semânticos e marcações de Leitura Ativa.
 */

const DANGEROUS_TAGS = new Set([
  'script',
  'style',
  'iframe',
  'object',
  'embed',
  'applet',
  'form',
  'input',
  'textarea',
  'select',
  'meta',
  'link',
  'base',
])

const SAFE_PROTOCOLS = /^(https?:|mailto:|\/|#)/i
const DANGEROUS_PROTOCOLS = /^(javascript:|vbscript:|data:)/i

/**
 * Valida se uma URL é segura para uso em atributos href/src.
 */
export function isSafeUrl(url: string): boolean {
  if (!url) return false
  const trimmed = url.trim().toLowerCase()
  if (DANGEROUS_PROTOCOLS.test(trimmed)) {
    return false
  }
  return SAFE_PROTOCOLS.test(trimmed)
}

/**
 * Sanitiza uma string HTML removendo tags perigosas e manipuladores de eventos.
 */
export function sanitizeHtml(dirtyHtml: string): string {
  if (!dirtyHtml || typeof dirtyHtml !== 'string') {
    return ''
  }

  // Se executando em ambiente de navegador ou Node com DOMParser
  if (typeof DOMParser !== 'undefined') {
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(dirtyHtml, 'text/html')
      cleanNode(doc.body)
      return doc.body.innerHTML
    } catch {
      // Fallback defensivo por regex caso o parser falhe
      return regexSanitize(dirtyHtml)
    }
  }

  return regexSanitize(dirtyHtml)
}

/**
 * Limpa recursivamente os nós DOM, eliminando tags e atributos inseguros.
 */
function cleanNode(node: Node): void {
  const children = Array.from(node.childNodes)

  for (const child of children) {
    if (child.nodeType === Node.ELEMENT_NODE) {
      const el = child as HTMLElement
      const tagName = el.tagName.toLowerCase()

      if (DANGEROUS_TAGS.has(tagName)) {
        el.remove()
        continue
      }

      // Remover todos os atributos on* (onload, onerror, onclick, etc.)
      const attrNames = Array.from(el.attributes).map((a) => a.name)
      for (const name of attrNames) {
        const lower = name.toLowerCase()
        if (lower.startsWith('on')) {
          el.removeAttribute(name)
        }
      }

      // Sanitizar links
      if (tagName === 'a') {
        const href = el.getAttribute('href')
        if (href && !isSafeUrl(href)) {
          el.removeAttribute('href')
          el.setAttribute('data-blocked-scheme', 'true')
        }
        // Assegurar proteção contra tabnabbing
        if (el.getAttribute('target') === '_blank') {
          el.setAttribute('rel', 'noopener noreferrer')
        }
      }

      cleanNode(child)
    }
  }
}

/**
 * Sanitização textual defensiva para ambientes sem suporte completo a DOM.
 */
function regexSanitize(html: string): string {
  let clean = html
  // Remove tags de script e iframe com conteúdo
  clean = clean.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
  clean = clean.replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
  clean = clean.replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
  clean = clean.replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '')
  clean = clean.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
  
  // Remove atributos on*
  clean = clean.replace(/\s+on[a-z]+="[^"]*"/gi, '')
  clean = clean.replace(/\s+on[a-z]+='[^']*'/gi, '')
  clean = clean.replace(/\s+on[a-z]+=[^\s>]+/gi, '')

  // Neutraliza javascript: em hrefs
  clean = clean.replace(/href=["']?\s*javascript:[^"'>]*["']?/gi, 'href="#"')
  clean = clean.replace(/href=["']?\s*data:[^"'>]*["']?/gi, 'href="#"')

  return clean
}
