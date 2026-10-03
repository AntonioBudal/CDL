# Tasks: F0.6.8 — Presença Pública e SEO do Leitorum

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/seo-public-api.yaml](./contracts/seo-public-api.yaml)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura base, tipagens e schemas de dados para SEO e presença pública

- [x] T001 Criar schemas Pydantic de metadados, robots e sitemap em `caderno-leitura-0.1/backend/app/schemas/seo.py`
- [x] T002 [P] Criar tipagens TypeScript para metadados de rota, Open Graph e Schema.org em `caderno-leitura-0.1/frontend/src/types/seo.ts`
- [x] T003 [P] Criar ícone vetorial `favicon.svg` e manifesto web `site.webmanifest` em `caderno-leitura-0.1/frontend/public/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Endpoints de rastreadores no backend, composable de SEO reativo e suíte de testes de isolamento

- [x] T004 Implementar serviço de agregação de URLs públicas e geração de XML/TXT em `caderno-leitura-0.1/backend/app/services/seo_service.py`
- [x] T005 [P] Criar roteador FastAPI com endpoints `/robots.txt` e `/sitemap.xml` em `caderno-leitura-0.1/backend/app/routers/seo.py`
- [x] T006 [P] Implementar composable reativo `useSeoMeta.ts` para sincronização dinâmica de metadados no frontend em `caderno-leitura-0.1/frontend/src/composables/useSeoMeta.ts`
- [x] T007 Criar suíte de testes de integração e isolamento de SEO no backend em `caderno-leitura-0.1/backend/tests/test_seo_and_public_presence.py`

**Checkpoint**: Fundação pronta — endpoints `/robots.txt` e `/sitemap.xml` funcionais e composable de SEO validado.

---

## Phase 3: User Story 1 - Página Pública "Sobre o Leitorum" e Apresentação Institucional (Priority: P1) 🎯 MVP

**Goal**: Permitir que qualquer visitante ou mecanismo de busca acerte na raiz institucional do Leitorum e consulte a página `/sobre` com toda a filosofia editorial e metodologia em 4 partes sem exigir login.

**Independent Test**: Acessar `/` e `/sobre` em janela anônima e verificar que a Landing Page e a página Sobre carregam perfeitamente sem exigir autenticação, enquanto usuários autenticados são redirecionados de `/` para `/livros`.

- [x] T008 [P] [US1] Criar view institucional pública `AboutView.vue` com apresentação editorial, metodologia e garantia sem anúncios em `caderno-leitura-0.1/frontend/src/views/AboutView.vue`
- [x] T009 [P] [US1] Criar Landing Page pública na raiz `LandingView.vue` com proposta de valor e chamadas de ação em `caderno-leitura-0.1/frontend/src/views/LandingView.vue`
- [x] T010 [US1] Atualizar roteamento no `router/index.ts` com rotas `/`, `/sobre` e guarda de navegação para redirecionar usuários logados em `caderno-leitura-0.1/frontend/src/router/index.ts`
- [x] T011 [US1] Padronizar rodapé da aplicação com links institucionais "Sobre", "Apoie o Leitorum" e informações de versão em `caderno-leitura-0.1/frontend/src/components/layout/AppFooter.vue`
- [x] T012 [P] [US1] Criar testes automatizados de navegação pública e redirecionamento de rotas em `caderno-leitura-0.1/frontend/tests/public_navigation.test.mjs`

**Checkpoint**: User Story 1 funcional e testável de forma independente — navegação institucional pública e landing page ativas (MVP).

---

## Phase 4: User Story 2 - SEO Técnico, Metadados Semânticos e Blindagem Privada (Priority: P2)

**Goal**: Assegurar que links públicos compartilhados exibam cartões ricos em redes sociais e que 100% dos dados e páginas privadas emitam `noindex, nofollow` e sejam bloqueados contra rastreamento.

**Independent Test**: Inspecionar cabeçalhos de rotas privadas e verificar emissão de `X-Robots-Tag: noindex, nofollow`, bem como validar a presença de tags Open Graph e Twitter Cards nas rotas públicas.

- [x] T013 [P] [US2] Integrar injeção de Open Graph (`og:*`) e Twitter Cards (`twitter:*`) no hook global `router.afterEach` em `caderno-leitura-0.1/frontend/src/router/index.ts`
- [x] T014 [US2] Adicionar middleware de segurança em `caderno-leitura-0.1/backend/app/main.py` para emitir cabeçalho HTTP `X-Robots-Tag: noindex, nofollow` em rotas da API e áreas privadas
- [x] T015 [P] [US2] Integrar consulta dinâmica a estudos públicos em `seo_service.py` garantindo exclusão de estudos privados do `sitemap.xml` em `caderno-leitura-0.1/backend/app/services/seo_service.py`
- [x] T016 [P] [US2] Criar testes automatizados para metadados sociais e blindagem de rotas privadas em `caderno-leitura-0.1/frontend/tests/seo_metadata.test.mjs`

**Checkpoint**: User Stories 1 e 2 funcionais — cartões sociais ricos e blindagem estrita de dados privados ativos.

---

## Phase 5: User Story 3 - Identidade Visual, Favicon Multi-Resolução e Dados Estruturados Schema.org (Priority: P3)

**Goal**: Apresentar identidade visual nítida para o Google Search (favicons conforme diretrizes do Google) e fornecer marcação Schema.org JSON-LD para a aplicação e artigos públicos.

**Independent Test**: Validar que os favicons atendem aos critérios de tamanho do Google (≥ 48x48 px e SVG) e que o bloco JSON-LD é aprovado no validador Schema.org.

- [x] T017 [P] [US3] Fornecer ativos de favicon em múltiplas resoluções (`favicon-48x48.png`, `apple-touch-icon.png`, `favicon.ico`) e `og-cover.png` (1200x630) em `caderno-leitura-0.1/frontend/public/`
- [x] T018 [US3] Atualizar `index.html` com tags canônicas de favicon, webmanifest e baseline estático de SEO em `caderno-leitura-0.1/frontend/index.html`
- [x] T019 [P] [US3] Implementar injeção dinâmica de blocos Schema.org JSON-LD (`WebApplication` e `Article`) no composable `useSeoMeta.ts` em `caderno-leitura-0.1/frontend/src/composables/useSeoMeta.ts`
- [x] T020 [P] [US3] Criar testes unitários para geração e injeção de Schema.org JSON-LD em `caderno-leitura-0.1/frontend/tests/schema_structured_data.test.mjs`

**Checkpoint**: Todas as histórias de usuário implementadas e verificáveis de forma independente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de integridade, testes de regressão, build de produção e auditoria de privacidade

- [x] T021 [P] Validar todos os cenários do guia `quickstart.md` em `caderno-leitura-0.1/backend/tests/test_seo_and_public_presence.py`
- [x] T022 [P] Executar suíte completa de testes do backend (`.venv\Scripts\python.exe -m pytest tests/`)
- [x] T023 [P] Executar suíte de testes do frontend e build de produção (`npm test` e `npm run build`)
- [x] T024 Auditoria final de privacidade e conformidade com o Princípio I da Constituição (zero dados privados em respostas públicas)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA as histórias de usuário.
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 2 — Páginas públicas e navegação institucional.
- **User Story 2 (Phase 4)**: Depende da Phase 2 — Metadados sociais e blindagem privada.
- **User Story 3 (Phase 5)**: Depende da Phase 2 — Favicons e Schema.org JSON-LD.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

### Parallel Opportunities
- T001, T002 e T003 podem ser executados em paralelo.
- T005, T006 e T007 podem ser implementados em paralelo na Phase 2.
- T008 e T009 podem ser desenvolvidos em paralelo na Phase 3.
- T013, T015 e T016 podem rodar em paralelo na Phase 4.
- T017, T019 e T020 podem rodar em paralelo na Phase 5.
- T022 e T023 podem rodar em paralelo na Phase 6.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 — MVP).
3. **Validar e Homologar**: Visitantes anônimos conseguem navegar na Landing Page e na página Sobre sem quebras no acervo.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Infraestrutura de SEO e roteadores pronta.
2. User Story 1 $\rightarrow$ Páginas institucionais públicas ativas (MVP).
3. User Story 2 $\rightarrow$ Metadados sociais ricos e blindagem de privacidade.
4. User Story 3 $\rightarrow$ Favicons Google e Schema.org JSON-LD.
5. Polish $\rightarrow$ Regressão geral, build e auditoria final.
