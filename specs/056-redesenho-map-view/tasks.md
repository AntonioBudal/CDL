# Tasks: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Feature**: F 0.7.7 — Redesenho da Map View  
**Branch**: `056-redesenho-map-view`  
**Date**: 2026-10-04  
**Spec**: [specs/056-redesenho-map-view/spec.md](spec.md) | **Plan**: [specs/056-redesenho-map-view/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição das estruturas e tipos TypeScript para nós, arestas e estados do grafo semântico.

- [x] T001 [P] Estender e definir tipos TypeScript `MapNodeItem`, `MapConnectionEdge`, `RelationPopoverState`, `QuickCreateState` e `MapViewportState` em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Algoritmo determinístico de distribuição radial concêntrica e repulsão suave para o grafo.

- [x] T002 Implementar composable `useMapLayout.ts` com a função pura `computeRadialLayout` (ancoragem do nó núcleo ao centro, anéis orbitais $R_1$ e $R_2$, e repulsão angular suave) em `caderno-leitura-0.1/frontend/src/composables/useMapLayout.ts`
- [x] T003 [P] Criar testes unitários para a distribuição radial concêntrica, posicionamento do nó núcleo e algoritmo de repulsão suave em `caderno-leitura-0.1/frontend/tests/study-map.test.mjs`

**Checkpoint**: Base matemática e espacial pronta — qualquer lista de estudos com relações é projetada em um grafo concêntrico legível.

---

## Phase 3: User Story 1 - Visualização Radial Semântica e Destaque do Estudo Núcleo (Priority: P1) 🎯 MVP

**Goal**: Renderizar o mapa conceitual com o Estudo Núcleo em destaque visual proeminente ao centro, nós periféricos distribuídos em anéis concêntricos sem sobreposição, arestas direcionadas com setas e rótulos semânticos, e navegação suave por pan e zoom.

**Independent Test**: Carregar um capítulo com estudos e relações; abrir a Map View; verificar que o estudo focal ocupa o centro com destaque dimensional e halo, e estudos relacionados orbitam conectados por arestas direcionadas com rótulos e setas.

### Tests for User Story 1 🧪

- [x] T004 [P] [US1] Criar testes unitários para a renderização do nó núcleo (`isCore`), anéis orbitais concêntricos e arestas direcionadas com rótulos em `caderno-leitura-0.1/frontend/tests/study_map_view.test.mjs`

### Implementation for User Story 1

- [x] T005 [US1] Redesenhar superfície gráfica de `StudyMapView.vue` com SVG integrado ao `computeRadialLayout`, anéis concêntricos, destaque do nó núcleo (`central-core-node`) e nós periféricos orbitais em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`
- [x] T006 [US1] Implementar controles de navegação de pan (arrasto do canvas com mouse/touch) e zoom suave (botões `+`, `-`, `reset` e roda do mouse) com limites calibrados em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`

**Checkpoint**: User Story 1 concluída — a Map View funciona como uma representação visual clara e navegável do grafo de argumentos (MVP).

---

## Phase 4: User Story 2 - Traçado Interativo de Conexões e Mini-Popover de Relações (Priority: P2)

**Goal**: Permitir arrastar a linha elástica SVG a partir da alça de um nó de estudo até outro nó de destino e abrir o mini-popover contextual `MapRelationPopover.vue` para definir o tipo da relação com inversão rápida `⇄` e persistência imediata na API.

**Independent Test**: Clicar e arrastar da alça conectora de um nó A até um nó B; verificar abertura de `MapRelationPopover.vue`; selecionar relação ("fundamenta"), testar inversão `⇄` e salvar, confirmando que a nova aresta é desenhada e persistida.

### Tests for User Story 2 🧪

- [x] T007 [P] [US2] Criar testes unitários para abertura do popover ancorado, oração ativa orientada, inversão de sentido `⇄` e bloqueio de auto-relação em `caderno-leitura-0.1/frontend/tests/study_map_view.test.mjs`

### Implementation for User Story 2

- [x] T008 [P] [US2] Desenvolver o componente `MapRelationPopover.vue` com oração semântica ativa, seletor canônico de tipos de relação, botão de inversão `⇄`, campo de justificativa opcional e atalhos `Enter`/`Esc` em `caderno-leitura-0.1/frontend/src/components/views/map/MapRelationPopover.vue`
- [x] T009 [US2] Integrar modo interativo de conexão (`isConnecting`, alça `.node-connect-handle` e linha elástica `.elastic-draft-line`) com abertura e disparo de ações de `MapRelationPopover.vue` em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`

**Checkpoint**: User Stories 1 e 2 integradas — o leitor consegue modelar e articular raciocínios conceituais diretamente pelo mapa.

---

## Phase 5: User Story 3 - Criação Direta de Estudos no Mapa e Ergonomia Mobile (Priority: P3)

**Goal**: Duplo clique no canvas ou botão flutuante `+` para abrir o mini-card `MapQuickCreateCard.vue` in-place registrando novo estudo no capítulo sem sair da tela, acompanhado por modo assistido de toque e alvos táteis mínimos de 44×44px no mobile.

**Independent Test**: Duplo clique em área livre do mapa; preencher título e seção inicial no mini-card; salvar com `Enter` e verificar o novo nó posicionado no grafo. No mobile, acionar o modo assistido de toque e validar dimensões de 44px.

### Tests for User Story 3 🧪

- [x] T010 [P] [US3] Criar testes unitários para o mini-card de criação in-place, duplo clique no canvas e modo assistido de toque com alvos táteis de 44px em `caderno-leitura-0.1/frontend/tests/study_map_view.test.mjs`

### Implementation for User Story 3

- [x] T011 [P] [US3] Desenvolver componente `MapQuickCreateCard.vue` com inputs compactos com autofocus, seletor de seção analítica inicial (Resumo, Conceito, Explicação) e submissão rápida com `Enter` em `caderno-leitura-0.1/frontend/src/components/views/map/MapQuickCreateCard.vue`
- [x] T012 [US3] Integrar captura de duplo clique no mapa, botão flutuante "+ Novo Estudo" e barra de ações táteis de rodapé para mobile com alvos de 44×44px em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`

**Checkpoint**: Todas as 3 User Stories concluídas, acessíveis e operacionais em desktop e mobile.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, testes de regressão de ponta a ponta e build de produção.

- [x] T013 [P] Validar os 5 cenários de teste fim a fim de `specs/056-redesenho-map-view/quickstart.md`
- [x] T014 Executar e validar suite de testes completa com `npm test` e `pytest`
- [x] T015 Validar tipagem e build de produção com `npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as User Stories.
- **User Story 1 (Phase 3)**: Depende da Phase 2 (Foundational) — MVP.
- **User Story 2 (Phase 4)**: Depende da Phase 2 e integra com US1.
- **User Story 3 (Phase 5)**: Depende da Phase 2 e integra com US1/US2.
- **Polish (Phase 6)**: Depende da conclusão de todas as User Stories.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir Setup (T001) e Foundational (T002, T003).
2. Concluir User Story 1 (T004, T005, T006).
3. Validar de forma independente: mapa radial concêntrico com nó núcleo destacado e navegação pan/zoom.

### Incremental Delivery

1. Setup + Foundational (algoritmo radial em `useMapLayout.ts`).
2. Adicionar US1 (MVP de visualização em anéis concêntricos e pan/zoom).
3. Adicionar US2 (linha elástica de conexão e popover `MapRelationPopover.vue` com inversão `⇄`).
4. Adicionar US3 (criação rápida in-place `MapQuickCreateCard.vue` e ergonomia mobile de 44px).
5. Polish e build de produção.
