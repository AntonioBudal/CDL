# Data Model: F0.6.8 — Presença Pública e SEO do Leitorum

**Feature**: `047-presenca-publica-seo`  
**Date**: 2026-10-02  
**Status**: Concluído

---

## 1. Visão Geral

A feature de Presença Pública e SEO não introduz novas tabelas no banco de dados SQLite, reaproveitando integralmente os modelos existentes (`Study`, `Book`, `User`, `SupportSetting`) e definindo estruturas em memória, schemas Pydantic e tipos TypeScript para metadados de rotas, sitemap XML e dados estruturados JSON-LD.

---

## 2. Entidades Conceituais e Modelos de Dados

### 2.1 PublicRouteMetadata (TypeScript / Frontend)
Representa os metadados associados a cada rota pública gerenciada pelo Vue Router e pelo composable `useSeoMeta`.

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `title` | `string` | Título da página exibido na aba e no `og:title` | `"Sobre o Leitorum"` |
| `description` | `string` | Descrição sucinta (meta description e `og:description`) | `"Conheça a proposta editorial do Leitorum..."` |
| `canonicalUrl` | `string` | URL canônica absoluta da página | `"https://leitorum.com/sobre"` |
| `ogImage` | `string` | URL absoluta da imagem de compartilhamento | `"https://leitorum.com/assets/og-cover.png"` |
| `ogType` | `'website' \| 'article'` | Tipo Open Graph da entidade | `'website'` |
| `robots` | `'index, follow' \| 'noindex, nofollow'` | Instrução para rastreadores | `'index, follow'` |
| `jsonLd` | `Record<string, unknown> \| null` | Objeto Schema.org injetado no `<head>` | `SchemaObject` |

### 2.2 SitemapUrlItem (Pydantic / Backend)
Representa uma entrada individual para renderização no XML do sitemap.

| Campo | Tipo | Validação | Descrição |
|---|---|---|---|
| `loc` | `str` | URL absoluta válida | Localização canônica do recurso |
| `lastmod` | `str` | Formato W3C Datetime (ISO 8601) | Data da última alteração (`updated_at`) |
| `changefreq` | `str` | `always \| hourly \| daily \| weekly \| monthly \| yearly \| never` | Frequência estimada de alteração |
| `priority` | `float` | `0.0` a `1.0` | Prioridade relativa da URL |

### 2.3 WebApplicationSchema (JSON-LD)
Estrutura padronizada conforme especificação Schema.org para o tipo `WebApplication`.

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Leitorum",
  "url": "https://leitorum.com",
  "description": "Caderno pessoal de leitura e estudos em camadas.",
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "All",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "BRL"
  }
}
```

### 2.4 ArticleSchema (JSON-LD para Estudos Públicos)
Estrutura Schema.org injetada ao visualizar um estudo com visibilidade pública ativa.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{summary}",
  "datePublished": "{created_at}",
  "dateModified": "{updated_at}",
  "author": {
    "@type": "Person",
    "name": "{author_display_name}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Leitorum",
    "url": "https://leitorum.com"
  },
  "mainEntityOfPage": "https://leitorum.com/compartilhado/{id}"
}
```

---

## 3. Regras de Blindagem e Filtragem de Dados

1. **Estudos Privados:** Qualquer estudo com `visibility != 'public'` ou `deleted_at IS NOT NULL` é estritamente ignorado na montagem do `sitemap.xml` e no cabeçalho de resposta pública.
2. **Prevenção de Enumeração de Usuários:** Nenhuma URL pública ou sitemap expõe IDs de usuários, e-mails ou hashes de sessão.
3. **Ambiente Local e Domínio Base:** O domínio canônico utiliza `APP_BASE_URL` (padrão `https://leitorum.com`), adaptável pelo host da requisição em ambientes de teste.
