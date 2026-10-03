import test from 'node:test'
import assert from 'node:assert/strict'

// Criamos um simulador de DOM leve para o ambiente de testes Node.js
function setupMockDom() {
  const elements = []
  globalThis.document = {
    title: '',
    head: {
      querySelector: (selector) => {
        return elements.find(el => el.matches(selector)) || null
      },
      appendChild: (element) => {
        if (!elements.includes(element)) {
          elements.push(element)
        }
        return element
      },
    },
    createElement: (tag) => {
      const attrs = {}
      const node = {
        tagName: tag.toUpperCase(),
        id: '',
        type: '',
        textContent: '',
        setAttribute: (k, v) => { attrs[k] = String(v) },
        getAttribute: (k) => attrs[k] ?? null,
        matches: (selector) => {
          if (selector.startsWith('#')) {
            return node.id === selector.slice(1)
          }
          if (selector.startsWith('meta[')) {
            const nameMatch = selector.match(/meta\[name="([^"]+)"\]/)
            if (nameMatch && attrs.name === nameMatch[1]) return true
            const propMatch = selector.match(/meta\[property="([^"]+)"\]/)
            if (propMatch && attrs.property === propMatch[1]) return true
          }
          if (selector.startsWith('link[')) {
            const relMatch = selector.match(/link\[rel="([^"]+)"\]/)
            if (relMatch && attrs.rel === relMatch[1]) return true
          }
          return false
        },
        remove: () => {
          const idx = elements.indexOf(node)
          if (idx !== -1) elements.splice(idx, 1)
        },
      }
      return node
    },
  }

  globalThis.window = {
    location: {
      origin: 'https://leitorum.com',
      href: 'https://leitorum.com/sobre',
    },
  }

  return { elements }
}

test('updateSeoMeta sincroniza título com padrão "Título — Leitorum"', async () => {
  setupMockDom()
  const { updateSeoMeta } = await import('../src/composables/useSeoMeta.ts')

  updateSeoMeta({
    title: 'Sobre o Leitorum',
    description: 'Filosofia e metodologia do Leitorum.',
  })

  assert.equal(document.title, 'Sobre o Leitorum — Leitorum')
})

test('updateSeoMeta injeta meta tags Open Graph e Twitter Cards para rotas públicas', async () => {
  setupMockDom()
  const { updateSeoMeta } = await import('../src/composables/useSeoMeta.ts')

  updateSeoMeta({
    title: 'Biblioteca',
    description: 'Catálogo de livros e estudos.',
    canonicalUrl: 'https://leitorum.com/livros',
    ogImage: '/assets/og-cover.png',
    ogType: 'website',
    robots: 'index, follow',
  })

  const descMeta = document.head.querySelector('meta[name="description"]')
  assert.ok(descMeta)
  assert.equal(descMeta.getAttribute('content'), 'Catálogo de livros e estudos.')

  const robotsMeta = document.head.querySelector('meta[name="robots"]')
  assert.ok(robotsMeta)
  assert.equal(robotsMeta.getAttribute('content'), 'index, follow')

  const ogTitle = document.head.querySelector('meta[property="og:title"]')
  assert.ok(ogTitle)
  assert.equal(ogTitle.getAttribute('content'), 'Biblioteca — Leitorum')

  const ogUrl = document.head.querySelector('meta[property="og:url"]')
  assert.ok(ogUrl)
  assert.equal(ogUrl.getAttribute('content'), 'https://leitorum.com/livros')

  const twitterCard = document.head.querySelector('meta[name="twitter:card"]')
  assert.ok(twitterCard)
  assert.equal(twitterCard.getAttribute('content'), 'summary_large_image')

  const canonical = document.head.querySelector('link[rel="canonical"]')
  assert.ok(canonical)
  assert.equal(canonical.getAttribute('href'), 'https://leitorum.com/livros')
})

test('updateSeoMeta aplica blindagem "noindex, nofollow" em rotas privadas (Princípio I)', async () => {
  setupMockDom()
  const { updateSeoMeta } = await import('../src/composables/useSeoMeta.ts')

  updateSeoMeta({
    title: 'Ajustes de Segurança',
    description: 'Página restrita do usuário.',
    robots: 'noindex, nofollow',
  })

  const robotsMeta = document.head.querySelector('meta[name="robots"]')
  assert.ok(robotsMeta)
  assert.equal(robotsMeta.getAttribute('content'), 'noindex, nofollow')
})

test('buildWebApplicationSchema e buildArticleSchema geram estruturas válidas Schema.org', async () => {
  const { buildWebApplicationSchema, buildArticleSchema } = await import('../src/composables/useSeoMeta.ts')

  const appSchema = buildWebApplicationSchema('https://leitorum.com')
  assert.equal(appSchema['@context'], 'https://schema.org')
  assert.equal(appSchema['@type'], 'WebApplication')
  assert.equal(appSchema.name, 'Leitorum')
  assert.equal(appSchema.url, 'https://leitorum.com')
  assert.equal(appSchema.offers?.price, '0')

  const articleSchema = buildArticleSchema({
    id: 42,
    title: 'Ética a Nicômaco — Livro I',
    summary: 'Análise teleológica da felicidade e virtude.',
    createdAt: '2026-10-01T12:00:00Z',
    updatedAt: '2026-10-02T15:30:00Z',
    authorName: 'Aristóteles',
  }, 'https://leitorum.com')

  assert.equal(articleSchema['@context'], 'https://schema.org')
  assert.equal(articleSchema['@type'], 'Article')
  assert.equal(articleSchema.headline, 'Ética a Nicômaco — Livro I')
  assert.equal(articleSchema.author?.name, 'Aristóteles')
  assert.equal(articleSchema.mainEntityOfPage, 'https://leitorum.com/compartilhado/42')
})
