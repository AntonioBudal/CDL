export interface WebApplicationSchema {
  [key: string]: unknown
  '@context': 'https://schema.org'
  '@type': 'WebApplication'
  name: string
  url: string
  description: string
  applicationCategory?: string
  operatingSystem?: string
  offers?: {
    '@type': 'Offer'
    price: string
    priceCurrency: string
  }
}

export interface ArticleSchema {
  [key: string]: unknown
  '@context': 'https://schema.org'
  '@type': 'Article'
  headline: string
  description?: string
  datePublished?: string
  dateModified?: string
  author?: {
    '@type': 'Person'
    name: string
  }
  publisher?: {
    '@type': 'Organization'
    name: string
    url: string
  }
  mainEntityOfPage?: string
}

export interface SeoMeta {
  title: string
  description: string
  canonicalUrl?: string
  ogImage?: string
  ogType?: 'website' | 'article'
  robots?: 'index, follow' | 'noindex, nofollow'
  jsonLd?: Record<string, unknown> | WebApplicationSchema | ArticleSchema | null
}

export interface BreadcrumbItem {
  name: string
  path: string
}

export interface SitemapItem {
  loc: string
  lastmod?: string
  changefreq?: string
  priority?: number
}
