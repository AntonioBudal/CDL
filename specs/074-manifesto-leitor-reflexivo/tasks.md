# Tasks: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Feature**: `074-manifesto-leitor-reflexivo`  
**Input**: Design artifacts from `specs/074-manifesto-leitor-reflexivo/`  

---

## Phase 1: Setup (Shared Infrastructure \u0026 Static Data)

**Purpose**: Estruturação inicial de diretórios, dados estáticos de domínio público e composables de suporte.

- [X] T001 Criar diretório para subcomponentes modulares da landing em `caderno-leitura-0.1/frontend/src/components/landing/`
- [X] T002 [P] Criar catálogo de dados estáticos do simulador e obra de Machado de Assis em `caderno-leitura-0.1/frontend/src/data/landingSimulator.ts`
- [X] T003 [P] Criar composable para controle efêmero de tema em memória na visita anônima em `caderno-leitura-0.1/frontend/src/composables/useVisitorTheme.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ajustes de contraste, fontes e pré-carregamento que afetam todas as histórias de usuário.

- [X] T004 Ajustar token de contraste `--color-text` do tema solario para conformidade WCAG AAA (>= 7:1) em `caderno-leitura-0.1/frontend/src/palettes.css` e `caderno-leitura-0.1/frontend/src/types/settings.ts`
- [X] T005 [P] Atualizar declarações de fontes locais para `font-display: swap` eliminando FOIT em `caderno-leitura-0.1/frontend/src/fonts.css`
- [X] T006 [P] Configurar pré-carregamento das famílias de fonte críticas (EB Garamond e Source Sans 3) em `caderno-leitura-0.1/frontend/index.html`

---

## Phase 3: User Story 1 - Hero Editorial Assimétrico e Manifesto (Priority: P1) ⭐ MVP

**Goal**: Apresentar abertura tipográfica clássica marcante com sobrelinha, título editorial, subtítulo manifesto, ficha de leitura conceitual em 4 partes e CTAs calmos.

**Independent Test**: Acessar `/` deslogado e verificar composição assimétrica, links de conversão (`/registro`, `/login`), navegação pública e link de salto de conteúdo.

- [X] T007 [P] [US1] Criar componente de cabeçalho público acessível com skip-link e ações em `caderno-leitura-0.1/frontend/src/components/landing/PublicHeader.vue`
- [X] T008 [P] [US1] Criar componente do Hero editorial assimétrico com Ficha de Leitura flutuante e CTAs em `caderno-leitura-0.1/frontend/src/components/landing/HeroSection.vue`
- [X] T009 [US1] Integrar `PublicHeader` e `HeroSection` na visualização principal em `caderno-leitura-0.1/frontend/src/views/LandingView.vue`
- [X] T010 [US1] Escrever testes unitários para renderização do Hero, Ficha de Leitura e CTAs em `caderno-leitura-0.1/frontend/tests/feature-074-manifesto-leitor-reflexivo.test.mjs`

**Checkpoint**: User Story 1 funcional e testável de forma independente (MVP visual concluído).

---

## Phase 4: User Story 2 - Bancada Interativa do Simulador em 4 Dimensões (Priority: P2)

**Goal**: Permitir ao visitante experimentar o método de estudo em camadas com o trecho de Machado de Assis e caderno analítico em 4 abas sem login ou rede.

**Independent Test**: Interagir com o simulador na seção `#metodo`, alternar as 4 abas e verificar a sincronização de destaques visuais no texto e transição suave sem CLS.

- [X] T011 [US2] Criar componente da bancada do simulador com metáfora de livro aberto e abas analíticas em `caderno-leitura-0.1/frontend/src/components/landing/MethodSimulator.vue`
- [X] T012 [US2] Implementar navegação acessível por teclado (setas, Home, End) e sincronização reativa de destaques ativos entre texto e dimensões em `caderno-leitura-0.1/frontend/src/components/landing/MethodSimulator.vue`
- [X] T013 [US2] Integrar a bancada do simulador na seção `#metodo` em `caderno-leitura-0.1/frontend/src/views/LandingView.vue`
- [X] T014 [US2] Adicionar testes unitários cobrindo alternância das 4 dimensões, teclado e sincronização visual em `caderno-leitura-0.1/frontend/tests/feature-074-manifesto-leitor-reflexivo.test.mjs`

**Checkpoint**: User Stories 1 e 2 operacionais e testáveis conjuntamente.

---

## Phase 5: User Story 3 - Ateliê Vitrine dos 10 Temas Canônicos (Priority: P3)

**Goal**: Exibir grade com as 10 paletas oficiais e permitir repintura instantânea da página em memória com anúncio acessível via `aria-live`.

**Independent Test**: Selecionar paletas na seção `#temas`, verificar repintura imediata de `document.documentElement.dataset.theme` e restauração ao navegar para fora da página.

- [X] T015 [US3] Criar componente do mostruário de temas reutilizando a grade canônica em `caderno-leitura-0.1/frontend/src/components/landing/ThemeShowcase.vue`
- [X] T016 [US3] Implementar repintura efêmera em memória, região `aria-live="polite"` e restauração no desmonte em `caderno-leitura-0.1/frontend/src/components/landing/ThemeShowcase.vue`
- [X] T017 [US3] Integrar o mostruário de temas na seção `#temas` em `caderno-leitura-0.1/frontend/src/views/LandingView.vue`
- [X] T018 [US3] Escrever testes unitários para a repintura em memória e isolamento no desmonte em `caderno-leitura-0.1/frontend/tests/feature-074-manifesto-leitor-reflexivo.test.mjs`

**Checkpoint**: User Stories 1, 2 e 3 funcionando e testáveis de forma independente.

---

## Phase 6: User Story 4 - Soberania de Dados e Tradição Histórica (Priority: P4)

**Goal**: Declarar os 4 compromissos de soberania (*local-first*, sem IA externa, sem rastreadores) e os 3 marcos históricos dos *commonplace books*, seguidos de chamada de fecho e rodapé.

**Independent Test**: Percorrer a seção `#principios`, validar os 4 princípios, a linha do tempo histórica e os links institucionais no rodapé.

- [X] T019 [P] [US4] Criar componente de soberania e linha do tempo histórica dos lugares-comuns em `caderno-leitura-0.1/frontend/src/components/landing/SovereigntySection.vue`
- [X] T020 [P] [US4] Criar componente do rodapé público com chamada reflexiva e links institucionais em `caderno-leitura-0.1/frontend/src/components/landing/PublicFooter.vue`
- [X] T021 [US4] Integrar a seção de soberania e o rodapé público em `caderno-leitura-0.1/frontend/src/views/LandingView.vue`
- [X] T022 [US4] Adicionar testes unitários cobrindo renderização de princípios, marcos temporais e links de rodapé em `caderno-leitura-0.1/frontend/tests/feature-074-manifesto-leitor-reflexivo.test.mjs`

**Checkpoint**: User Stories 1 a 4 totalmente integradas.

---

## Phase 7: User Story 5 - Infraestrutura de SEO, Acessibilidade e Performance (Priority: P5)

**Goal**: Garantir dados estruturados Schema.org válidos, metatags completas, HTML inicial semântico para rastreadores e dynamic imports no roteador para pontuação Lighthouse >= 95.

**Independent Test**: Inspecionar JSON-LD no DOM, validar metatags Open Graph/Twitter, inspecionar chunks do build Vite e rodar testes de SEO do backend.

- [X] T023 [P] [US5] Refinar esquema JSON-LD Schema.org (`WebApplication` / `EducationalApplication`) e metatags em `caderno-leitura-0.1/frontend/src/composables/useSeoMeta.ts`
- [X] T024 [P] [US5] Configurar carregamento assíncrono sob demanda (`() => import(...)`) para rotas autenticadas pesadas em `caderno-leitura-0.1/frontend/src/router/index.ts`
- [X] T025 [US5] Injetar marcação HTML semântica inicial acessível dentro do nó `#app` para indexação direta em `caderno-leitura-0.1/frontend/index.html`
- [X] T026 [US5] Executar e validar testes da suíte de SEO do backend em `caderno-leitura-0.1/backend/tests/test_seo_and_public_presence.py`

**Checkpoint**: Todas as 5 histórias de usuário concluídas com excelência de SEO e performance.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificação constitucional, auditoria visual de Zero Emojis e validação integrada completa.

- [X] T027 [P] Realizar auditoria estrita de Zero Emojis em 100% dos arquivos novos e modificados da landing page
- [X] T028 [P] Executar build de produção do frontend (`npm run build`) e suíte de testes unitários (`npm test`) em `caderno-leitura-0.1/frontend`
- [X] T029 Executar suíte completa de testes no backend via `pytest` em `caderno-leitura-0.1/backend`
- [X] T030 Executar validação completa dos cenários manuais e automatizados descritos em `specs/074-manifesto-leitor-reflexivo/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências, inicia imediatamente.
- **Foundational (Phase 2)**: Depende do Setup; ajusta tokens de contraste e fontes antes dos componentes visuais.
- **User Stories (Phases 3 a 7)**:
  - US1 (Hero/MVP) inicia logo após a Foundational.
  - US2 (Simulador) depende dos dados estáticos de Setup (T002).
  - US3 (Vitrine de Temas) depende do composable efêmero (T003) e do ajuste de contraste (T004).
  - US4 (Soberania) pode ser desenvolvida em paralelo aos componentes centrais.
  - US5 (SEO e Performance) consolida metadados, chunks e roteador após a composição da view.
- **Polish (Phase 8)**: Depende da conclusão de todas as histórias de usuário.

---

## Parallel Opportunities

- **Phase 1**: T002 (`landingSimulator.ts`) e T003 (`useVisitorTheme.ts`) foram criados em paralelo.
- **Phase 2**: T005 (`fonts.css`) e T006 (`index.html`) foram executados em paralelo.
- **Phase 3**: T007 (`PublicHeader.vue`) e T008 (`HeroSection.vue`) foram criados em paralelo.
- **Phase 6**: T019 (`SovereigntySection.vue`) e T020 (`PublicFooter.vue`) foram criados em paralelo.
- **Phase 7**: T023 (`useSeoMeta.ts`) e T024 (`router/index.ts`) foram otimizados em paralelo.
- **Phase 8**: T027 (auditoria Zero Emojis) e T028 (build/testes frontend) validados com êxito.

---

## Implementation Strategy

1. **MVP Incremental (User Story 1)**:
   - Configurado Setup e Foundational.
   - Entregue Hero Editorial com manifesto e CTAs de entrada.
   - Validada atmosfera e layout tipográfico responsivo.
2. **Camada Interativa (User Stories 2 e 3)**:
   - Adicionado o Simulador literário em 4 dimensões (Machado de Assis).
   - Adicionado o Mostruário dos 10 temas com repintura em memória.
3. **Autoridade e Confiança (User Story 4)**:
   - Inseridas as garantias de soberania e linhagem histórica dos *commonplace books*.
4. **Excelência de Mecanismo e Acessibilidade (User Story 5 e Polimento)**:
   - Otimizados chunks, metadados Schema.org, build Vite e validação total de testes (100% GREEN).
