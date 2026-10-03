# Research: F0.6.8 — Presença Pública e SEO do Leitorum

**Feature**: `047-presenca-publica-seo`  
**Date**: 2026-10-02  
**Status**: Concluído

---

## 1. Roteamento Público e Landing Page na Raiz (`/`)

### Decisão
Criar o componente `LandingView.vue` mapeado para a rota `/` no Vue Router com guarda de navegação:
- Visitantes não autenticados visualizam a Landing Page com proposta de valor, apresentação dos recursos (acervo, fichamento em 4 partes, privacidade local) e botões de ação ("Entrar" e "Criar Conta").
- Usuários autenticados (com sessão ativa em `useAuth()`) que acessam `/` são redirecionados de forma síncrona para `/livros`.
- A rota `/sobre` renderiza `AboutView.vue` tanto para anônimos quanto para usuários logados.

### Racional
Atualmente, visitantes que chegam a `leitorum.com` sem sessão encontram apenas a caixa de login, sem qualquer contexto do que é a ferramenta. A Landing Page e a página Sobre estabelecem a presença pública institucional recomendada pelo Roadmap 0.6 sem impactar o fluxo de leitores já cadastrados.

### Alternativas Consideradas
- **Manter apenas o modal de login na raiz e isolar apresentação em `/sobre`**: Rejeitado pelo usuário durante a fase de esclarecimento, pois uma ferramenta pública precisa de uma porta de entrada acolhedora para novos leitores.
- **Renderizar páginas públicas em subdomínio ou site estático separado**: Rejeitado, pois viola o Princípio III da Constituição (processo único local e arquitetura coesa sem dependências externas).

---

## 2. SEO Técnico em Single Page Application (Vue 3 + Vite)

### Decisão
Implementar um composable nativo `useSeoMeta` em `frontend/src/composables/useSeoMeta.ts` associado aos metadados de rota do Vue Router (`meta.seo`):
- O `index.html` fornece metadados canônicos estáticos do Leitorum como baseline para indexadores básicos que não executam JavaScript.
- A cada transição de rota (`router.afterEach`), `useSeoMeta` sincroniza:
  - `document.title`: Formato `"{Título da Página} — Leitorum"`.
  - `<meta name="description">`: Descrição resumida da página.
  - `<meta name="robots">`: `index, follow` para rotas públicas (`/`, `/sobre`, `/apoie`, `/compartilhado/:id`) e `noindex, nofollow` estrito para todas as demais.
  - Tags Open Graph (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`).
  - Tags Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`).
  - Link canônico `<link rel="canonical">`.
  - Injeção/atualização do bloco JSON-LD Schema.org.

### Racional
Dispensa bibliotecas externas adicionais (como `vue-meta` ou `@unhead/vue`), mantendo o bundle leve, auditável e 100% sob controle da arquitetura existente.

### Alternativas Consideradas
- **Adotar bibliotecas pesadas de SSR/SSG (Nuxt.js)**: Rejeitado por complexidade desproporcional e quebra da arquitetura SPA + FastAPI do Leitorum.

---

## 3. Endpoints de Rastreadores no Backend (`/robots.txt` e `/sitemap.xml`)

### Decisão
Implementar o router `backend/app/routers/seo.py` conectado ao FastAPI:
- `GET /robots.txt` (MIME `text/plain`):
  - Permite: `/`, `/sobre`, `/apoie`, `/compartilhado/`.
  - Proíbe: `/api/`, `/dashboard`, `/livros`, `/admin`, `/estudos/`.
  - Declara a URL canônica do Sitemap: `Sitemap: https://leitorum.com/sitemap.xml`.
- `GET /sitemap.xml` (MIME `application/xml`):
  - Retorna XML padrão `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`.
  - Inclui páginas institucionais com `priority="1.0"` (`/`) e `priority="0.8"` (`/sobre`, `/apoie`).
  - Consulta o banco SQLite para obter estudos com `visibility == 'public'` e `deleted_at IS NULL`, formatando suas URLs públicas com `priority="0.7"` e `lastmod` formatado em W3C Datetime.
  - Exclui imediatamente estudos privados, rascunhos ou excluídos na lixeira.
- Middleware / Cabeçalhos HTTP:
  - Em endpoints de API e rotas de administração, emitir cabeçalho `X-Robots-Tag: noindex, nofollow`.

### Racional
Garante que o Googlebot e outros crawlers recebam respostas XML/TXT diretamente do backend FastAPI em menos de 20ms, com garantia absoluta de que nenhum estudo privado seja indexado (Princípio I da Constituição).

### Alternativas Consideradas
- **Arquivo `sitemap.xml` estático pré-gerado**: Rejeitado no esclarecimento, pois não refletiria a publicação ou privatização de estudos compartilhados pelos usuários em tempo real.

---

## 4. Identidade Visual e Requisitos do Favicon Google

### Decisão
Fornecer ativos vetoriais e rasterizados no diretório `frontend/public/`:
- `favicon.svg`: Ícone vetorial SVG escalável com símbolo canônico do Leitorum (livro estilizado com contraste adaptativo).
- `favicon-48x48.png`: Ícone PNG quadrado atendendo à diretriz de tamanho mínimo do Google (superior ou igual a 48x48 px).
- `apple-touch-icon.png` (180x180 px) e ícones PWA (192x192 e 512x512 px).
- `site.webmanifest`: Metadados da aplicação web para navegadores móveis e desktop.
- `og-cover.png`: Imagem oficial em resolução 1200x630 px para compartilhamento em redes sociais.

### Racional
Atende estritamente às diretrizes de Favicon do Google Search Central, garantindo que o buscador exiba o logotipo oficial ao lado do título nas páginas de resultados.

---

## 5. Marcação Semântica e Dados Estruturados Schema.org

### Decisão
- **Páginas Institucionais (`/` e `/sobre`)**:
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
- **Estudos Públicos Compartilhados**:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{Título do Estudo}",
    "description": "{Resumo do Estudo}",
    "dateModified": "{updated_at}",
    "mainEntityOfPage": "https://leitorum.com/compartilhado/{id}"
  }
  ```

### Racional
O Google Search Central recomenda os tipos `WebApplication` para aplicativos web e `Article` para publicações textuais. Essa estrutura qualifica o site para cartões de rich snippets e exibições semânticas precisas.
