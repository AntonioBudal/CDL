import { isRef, watch, type Ref } from 'vue'
import type { ArticleSchema, SeoMeta, WebApplicationSchema } from '../types/seo'

function setMetaTag(selector: string, attributeName: string, attributeValue: string, content: string): void {
  if (typeof document === 'undefined') return
  let element = document.head.querySelector<HTMLMetaElement>(selector)
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attributeName, attributeValue)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

function setCanonicalUrl(url: string): void {
  if (typeof document === 'undefined') return
  let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  link.setAttribute('href', url)
}

function setJsonLdScript(data: Record<string, unknown> | null | undefined): void {
  if (typeof document === 'undefined') return
  const id = 'schema-json-ld'
  let script = document.head.querySelector<HTMLScriptElement>(`#${id}`)

  if (!data) {
    if (script) {
      script.remove()
    }
    return
  }

  if (!script) {
    script = document.createElement('script')
    script.id = id
    script.type = 'application/ld+json'
    document.head.appendChild(script)
  }
  script.textContent = JSON.stringify(data)
}

export function updateSeoMeta(meta: SeoMeta): void {
  if (typeof document === 'undefined') return

  // Título da aba e Open Graph (FR-009)
  const formattedTitle = meta.title ? `${meta.title} — Leitorum` : 'Leitorum — Caderno de Leitura'
  document.title = formattedTitle

  // Meta description
  if (meta.description) {
    setMetaTag('meta[name="description"]', 'name', 'description', meta.description)
  }

  // Meta robots
  const robots = meta.robots || 'index, follow'
  setMetaTag('meta[name="robots"]', 'name', 'robots', robots)

  // Canonical URL
  const canonicalUrl = meta.canonicalUrl || (typeof window !== 'undefined' ? window.location.href : 'https://leitorum.com')
  setCanonicalUrl(canonicalUrl)

  // Open Graph
  setMetaTag('meta[property="og:title"]', 'property', 'og:title', formattedTitle)
  if (meta.description) {
    setMetaTag('meta[property="og:description"]', 'property', 'og:description', meta.description)
  }
  setMetaTag('meta[property="og:url"]', 'property', 'og:url', canonicalUrl)
  setMetaTag('meta[property="og:type"]', 'property', 'og:type', meta.ogType || 'website')
  setMetaTag('meta[property="og:site_name"]', 'property', 'og:site_name', 'Leitorum')
  const ogImage = meta.ogImage || '/assets/og-cover.png'
  setMetaTag('meta[property="og:image"]', 'property', 'og:image', ogImage)

  // Twitter Card
  setMetaTag('meta[name="twitter:card"]', 'name', 'twitter:card', 'summary_large_image')
  setMetaTag('meta[name="twitter:title"]', 'name', 'twitter:title', formattedTitle)
  if (meta.description) {
    setMetaTag('meta[name="twitter:description"]', 'name', 'twitter:description', meta.description)
  }
  setMetaTag('meta[name="twitter:image"]', 'name', 'twitter:image', ogImage)

  // Schema.org JSON-LD
  setJsonLdScript(meta.jsonLd)
}

export function buildWebApplicationSchema(baseUrl = 'https://leitorum.com'): WebApplicationSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Leitorum',
    url: baseUrl,
    description: 'Caderno pessoal de leitura e estudos em camadas.',
    applicationCategory: 'EducationalApplication',
    operatingSystem: 'All',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'BRL',
    },
  }
}

export function buildArticleSchema(
  study: {
    id: number | string
    title: string
    summary?: string
    createdAt?: string
    updatedAt?: string
    authorName?: string
  },
  baseUrl = 'https://leitorum.com',
): ArticleSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: study.title,
    description: study.summary || '',
    datePublished: study.createdAt,
    dateModified: study.updatedAt,
    author: study.authorName
      ? {
          '@type': 'Person',
          name: study.authorName,
        }
      : undefined,
    publisher: {
      '@type': 'Organization',
      name: 'Leitorum',
      url: baseUrl,
    },
    mainEntityOfPage: `${baseUrl}/compartilhado/${study.id}`,
  }
}

export function useSeoMeta(metaInput?: SeoMeta | Ref<SeoMeta>) {
  if (metaInput) {
    const apply = () => {
      const val = isRef(metaInput) ? metaInput.value : metaInput
      updateSeoMeta(val)
    }

    apply()

    if (isRef(metaInput)) {
      watch(metaInput, () => apply(), { deep: true })
    }
  }

  return {
    updateSeoMeta,
    buildWebApplicationSchema,
    buildArticleSchema,
  }
}
