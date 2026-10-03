# Feature Specification: F0.6.8 — Presença Pública e SEO do Leitorum

**Feature Branch**: `047-presenca-publica-seo`

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: "F0.6.8 — Presença Pública e SEO do Leitorum (Roadmap 0.6: Preparar o Leitorum para ser corretamente identificado, compreendido e rastreado pelos mecanismos de busca, criando página pública Sobre o Leitorum acessível pelo rodapé, metadados semânticos Open Graph / Twitter, robots.txt, sitemap.xml, favicon adequado e isolamento de rotas privadas contra indexação indevida)."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Página Pública "Sobre o Leitorum" e Apresentação Institucional (Priority: P1 - MVP)

Como visitante, leitor em potencial ou usuário compartilhando o Leitorum, quero acessar uma página pública límpida, profissional e informativa (`/sobre`), com link direto no rodapé da aplicação, que explique detalhadamente o que é o sistema, sua filosofia (gratuito, sem anúncios, sem rastreamento invasivo), sua metodologia de fichamento em quatro seções e suas capacidades de estudo pessoal, para que pessoas e mecanismos de busca compreendam o valor do projeto sem depender de uma conta autenticada.

**Why this priority**: É o valor fundacional da presença pública. O Leitorum precisa de uma página institucional canônica que explique sua proposta aos visitantes e sirva como âncora textual primária para rastreadores da web, cumprindo o objetivo central do Roadmap 0.6.

**Independent Test**: Pode ser testado de forma isolada acessando a rota pública `/sobre` sem estar logado no sistema: a página carrega instantaneamente, exibe a apresentação editorial e institucional do Leitorum, oferece navegação de volta para acesso à biblioteca/login e inclui link no rodapé em todas as visualizações públicas.

**Acceptance Scenarios**:

1. **Given** um visitante não autenticado acessando `https://leitorum.com/sobre` (ou `localhost:8000/sobre`), **When** a página é renderizada, **Then** é apresentada a explicação completa do produto (o que é, para quem foi criado, como funciona o fichamento em 4 seções, organização em biblioteca e filosofia sem anúncios), com tipografia limpa, suporte a temas e layout responsivo.
2. **Given** qualquer página do Leitorum com rodapé institucional (incluindo tela de login, `/apoie` ou visualização pública), **When** o usuário clica no link "Sobre", **Then** é redirecionado suavemente para a página `/sobre`.
3. **Given** um visitante na página `/sobre`, **When** decide utilizar o produto, **Then** encontra botões de ação ("Acessar o Leitorum" / "Criar Conta") direcionando diretamente ao fluxo de entrada.

---

### User Story 2 - SEO Técnico, Metadados Semânticos e Blindagem Privada (Priority: P2)

Como gestor do produto e usuário compartilhando links do acervo, quero que as páginas públicas (Home institucional, Sobre, Apoie e Estudos Compartilhados Publicamente) disponham de títulos dinâmicos únicos, tags canônicas, meta descriptions precisas, cartões sociais Open Graph e Twitter Cards, enquanto todas as rotas e dados privados de usuários são rigorosamente blindados com `noindex, nofollow` e bloqueados em `robots.txt`, para garantir indexação correta apenas do conteúdo intencionalmente público sem violar a privacidade dos leitores.

**Why this priority**: Garante que o compartilhamento de links públicos gere prévias atraentes em redes e mensageiros (WhatsApp, Telegram, Twitter, LinkedIn) e assegura que os mecanismos de busca encontrem o sitemap oficial, respeitando o Princípio I da Constituição (Proteção Absoluta do Acervo).

**Independent Test**: Pode ser testado inspecionando o `<head>` das páginas e os endpoints `/robots.txt` e `/sitemap.xml`: as rotas públicas apresentam tags canônicas, meta tags de Open Graph e Twitter válidas, e o `robots.txt` proíbe o rastreamento de caminhos autenticados (`/api/`, `/dashboard`, `/livros`, `/estudos/privados`), mantendo o `sitemap.xml` restrito às rotas públicas.

**Acceptance Scenarios**:

1. **Given** um link público compartilhado (ex.: `/sobre` ou um estudo com visibilidade pública), **When** o link é analisado por um crawler de rede social, **Then** são fornecidos `og:title`, `og:description`, `og:image`, `og:url` e `twitter:card="summary_large_image"` coerentes com a página visualizada.
2. **Given** uma requisição HTTP para `/robots.txt`, **When** o arquivo é consultado por robôs de busca, **Then** ele instrui permissão para as páginas públicas (`/`, `/sobre`, `/apoie`, `/compartilhado/`), proíbe o rastreamento de rotas internas privadas (`Disallow: /api/`, `Disallow: /admin`, `Disallow: /dashboard`, etc.) e referencia a localização exata do `sitemap.xml`.
3. **Given** qualquer rota autenticada ou privada (biblioteca particular, detalhes de livro pessoal, fichamentos não compartilhados), **When** a página é renderizada ou requisitada, **Then** contém a meta tag `<meta name="robots" content="noindex, nofollow">` e cabeçalho `X-Robots-Tag: noindex, nofollow`.
4. **Given** um estudo cujo autor alterou a visibilidade de "público" para "privado", **When** o `sitemap.xml` é consultado novamente, **Then** a URL correspondente não consta mais no índice público.

---

### User Story 3 - Identidade Visual, Favicon Multi-Resolução e Dados Estruturados Schema.org (Priority: P3)

Como visitante, navegador moderno ou rastreador do Google, quero identificar o Leitorum através de um favicon nítido e padronizado em múltiplas resoluções (incluindo SVG vetorial e formatos PNG quadrados de 48x48, 192x192 e 512x512 para PWA/atalhos), acompanhado de marcação Schema.org JSON-LD (`SoftwareApplication` / `WebApplication`), para que a aplicação seja exibida com alto nível profissional em abas, favoritos de celular e resultados enriquecidos de busca.

**Why this priority**: Conclui o acabamento visual e semântico de acordo com as diretrizes oficiais do Google para identidade de sites e favicons, evitando ícones pixelados ou genéricos em telas retina e celulares.

**Independent Test**: Pode ser testado validando o manifesto Web (`site.webmanifest`), a resolução dos favicons nos navegadores (desktop e mobile) e executando a validação sintática do bloco JSON-LD Schema.org em ferramentas de teste de dados estruturados.

**Acceptance Scenarios**:

1. **Given** o carregamento do Leitorum em qualquer navegador moderno, **When** a página inicial ou interna é aberta, **Then** o navegador localiza e exibe o favicon oficial nas dimensões ideais recomendadas (superior a 48×48 px, com fallback SVG para nitidez infinita).
2. **Given** o código-fonte da página inicial e da página `/sobre`, **When** analisado por um validador de Schema.org, **Then** é detectado um bloco `<script type="application/ld+json">` válido descrevendo o Leitorum como `WebApplication` / `SoftwareApplication`, contendo nome oficial, URL canônica, licença/natureza gratuita e descrição institucional sem dados sensíveis.

---

### Edge Cases

- **Navegação SPA (Single Page Application)**: Ao navegar entre páginas sem recarregar o navegador (via Vue Router), as meta tags de título, descrição, canonical e robots devem ser atualizadas dinamicamente no DOM para refletir o contexto da rota atual.
- **Rastreamento de Estudos Compartilhados Excluídos ou Modificados**: Se um estudo compartilhado for excluído ou movido para a lixeira (soft delete), a rota pública correspondente deve retornar HTTP 404 limpo com meta tag `noindex`, e deixar de constar no `sitemap.xml`.
- **Visitante acessando a raiz (`/`)**: A rota raiz (`/`) exibe uma Landing Page pública de apresentação do produto para visitantes anônimos (com chamada institucional e botões para "Entrar" e "Criar Conta") e redireciona automaticamente usuários autenticados para a Biblioteca (`/livros`).
- **Sitemap Dinâmico vs Estático**: O `sitemap.xml` é servido dinamicamente via endpoint do backend, listando as páginas institucionais e estudos que possuem visibilidade pública ativa, excluindo imediatamente estudos com visibilidade privada ou removidos.
- **Profundidade dos Dados Estruturados**: As páginas institucionais (`/`, `/sobre`) incluem dados estruturados do tipo `WebApplication` / `SoftwareApplication`, enquanto as páginas de estudos públicos compartilhados incluem `Article` / `CreativeWork` com título, autor e data da última modificação.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer uma rota pública `/sobre` renderizando uma página institucional completa, acessível a visitantes anônimos e usuários autenticados, com navegação a partir do rodapé da aplicação.
- **FR-002**: A página institucional DEVE conter seções estruturadas descrevendo o propósito do Leitorum, metodologia de fichamento em quatro partes, organização de leituras e compromisso de privacidade sem publicidade.
- **FR-003**: O sistema DEVE disponibilizar uma rota pública `/robots.txt` que permita o rastreamento apenas de rotas públicas permitidas e proíba explicitamente todas as rotas privadas e de administração.
- **FR-004**: O sistema DEVE fornecer um endpoint dinâmico `/sitemap.xml` acessível publicamente contendo URLs canônicas das páginas institucionais (`/`, `/sobre`, `/apoie`) e de estudos com visibilidade pública ativa, com timestamps `lastmod` em padrão W3C Datetime.
- **FR-005**: O sistema DEVE injetar dinamicamente meta tags Open Graph (`og:title`, `og:description`, `og:url`, `og:image`, `og:type`, `og:site_name`) e Twitter Card (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`) em todas as páginas públicas.
- **FR-006**: O sistema DEVE assegurar que todas as páginas e rotas autenticadas ou restritas contenham a instrução `noindex, nofollow` tanto em meta tag HTML quanto no cabeçalho HTTP `X-Robots-Tag`.
- **FR-007**: O sistema DEVE fornecer um pacote de favicons de alta resolução conforme recomendações do Google (incluindo formatos SVG vetorial e PNGs dimensionados em 48x48, 192x192 e 512x512) acompanhado de `site.webmanifest`.
- **FR-008**: O sistema DEVE incluir marcação de dados estruturados JSON-LD Schema.org para o tipo `WebApplication` / `SoftwareApplication` nas páginas institucionais e `Article` / `CreativeWork` nas páginas de estudos públicos compartilhados.
- **FR-009**: A interface DEVE sincronizar o título do documento (`document.title`) a cada troca de rota no frontend, mantendo o padrão `"Título da Página — Leitorum"`.
- **FR-010**: A página pública e os metadados NÃO DEVEM vazar nenhuma informação privada de acervo, identificadores de sessão, nomes de leitores ou conteúdo não compartilhado (Princípio I da Constituição).
- **FR-011**: O sistema DEVE garantir que o carregamento e renderização da página `/sobre` permaneça acessível sem dependência de JavaScript habilitado para fins de rastreamento básico por crawlers HTTP simples.
- **FR-012**: O rodapé de todas as telas públicas e autenticadas DEVE padronizar os links institucionais: "Sobre", "Apoie o Leitorum" e informações de versão/licença.
- **FR-013**: A rota raiz (`/`) DEVE apresentar uma Landing Page institucional para visitantes não autenticados (com ações de acesso e cadastro) e redirecionar automaticamente usuários com sessão ativa para a Biblioteca (`/livros`).

---

### Key Entities *(include if feature involves data)*

- **PublicRouteMetadata**: Objeto de metadados associado a cada rota pública contendo título canônico, descrição concisa (meta description), imagem Open Graph correspondente, tipo de documento e regras de indexação.
- **SitemapEntry**: Registro de mapeamento para o arquivo XML contendo a URL canônica pública (`loc`), data da última modificação (`lastmod`), frequência de atualização (`changefreq`) e prioridade relativa (`priority`).
- **StructuredDataSchema**: Definição declarativa em formato JSON-LD Schema.org representando o Leitorum como software e aplicação web sem fins lucrativos.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das páginas públicas (`/`, `/sobre`, `/apoie`, estudos compartilhados) retornam meta tags válidas de Open Graph e Twitter Cards verificáveis por validadores sociais.
- **SC-002**: A rota `/robots.txt` bloqueia com sucesso 100% dos prefixos de rotas privadas do acervo e API (`/api/`, `/dashboard`, `/livros`), comprovado por testes automatizados de requisição.
- **SC-003**: O validador de Rich Results / Schema.org aprova o bloco JSON-LD da aplicação sem erros sintáticos ou propriedades obrigatórias faltantes.
- **SC-004**: O tempo de carregamento da página pública `/sobre` permanece abaixo de 200 milissegundos no servidor local.
- **SC-005**: 0% de vazamento de dados de acervo privado em metadados, sitemaps ou respostas públicas de indexação.

---

## Assumptions

- O domínio canônico de produção configurado para geração de URLs absolutas em Open Graph e Sitemap é `https://leitorum.com`.
- Para instâncias locais ou de teste em rede privada, o sistema utilizará o host requisitado ou fallback configurável via variável de ambiente.
- O Leitorum continuará operando como Single Page Application com FastAPI no backend e Vue 3 no frontend, com metadados estáticos pré-renderizados no `index.html` e complementados dinamicamente via composable no cliente.
