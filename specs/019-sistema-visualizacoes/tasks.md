# Tasks: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de tipagens TypeScript e tokens CSS fundamentais de visualização.

- [X] T001 Declarar tipos e interfaces TypeScript (`StudyViewMode`, `StudyViewOption`, `ViewPreferenceState`) e a lista canônica `STUDY_VIEW_OPTIONS` em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T002 [P] Adicionar tokens CSS e classes de transição de visualizações em `caderno-leitura-0.1/frontend/src/tokens.css`

---

## Phase 2: Foundational (Infraestrutura Reativa e Renderers Básicos)

**Purpose**: Infraestrutura reativa e renderers de base que sustentam a alternância de modos.

**CRITICAL**: Nenhuma integração na visão principal do livro pode ocorrer antes desta fase.

- [X] T003 Criar composable `useViewPreference.ts` com gestão reativa de visualização ativa, preservação de `activeStudyId` e persistência híbrida em `caderno-leitura-0.1/frontend/src/composables/useViewPreference.ts`
- [X] T004 [P] Criar componente `ViewSwitcher.vue` com semântica WAI-ARIA (`role="tablist"` / `role="tab"`) e botões táteis (mínimo 44x44px) em `caderno-leitura-0.1/frontend/src/components/views/ViewSwitcher.vue`
- [X] T005 [P] Criar componente renderer `StudyGridView.vue` (modo Grade com cartões ricos) em `caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue`
- [X] T006 [P] Criar componente renderer `StudyListView.vue` (modo Lista tabular compacta de alta densidade) em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`

**Checkpoint**: Base reativa e renderers fundamentais prontos para orquestração.

---

## Phase 3: User Story 1 - Alternância entre Modos de Visualização no Livro (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor alterne instantaneamente entre Grade, Lista, Árvore, Mapa e Canvas no topo da área de leitura, preservando o estudo ativo em foco.

**Independent Test**: Abrir um livro com estudos, comutar entre qualquer um dos 5 modos e verificar a renderização suave correspondente sem recarregar a página e sem perder o estudo destacado.

### Testes para User Story 1

- [X] T007 [P] [US1] Criar suíte de testes unitários para o composable `useViewPreference.ts` e comutação de modos em `caderno-leitura-0.1/frontend/tests/study-views.test.mjs`

### Implementação para User Story 1

- [X] T008 [P] [US1] Criar componente renderer `StudyTreeView.vue` (modo Árvore com hierarquia e ramos expansíveis) em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue`
- [X] T009 [P] [US1] Criar componente renderer `StudyMapView.vue` (modo Mapa com distribuição radial de rede conceitual) em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`
- [X] T010 [P] [US1] Criar componente renderer `StudyCanvasView.vue` (modo Canvas bidimensional 2D com cartões espaciais e pan/zoom) em `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`
- [X] T011 [US1] Integrar `ViewSwitcher` e os 5 renderers dinâmicos via `<component :is="...">` no palco central de `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: MVP funcional! 5 modos intercambiáveis operando no palco central do livro.

---

## Phase 4: User Story 2 - Persistência Híbrida e Acessibilidade do Seletor (Priority: P2)

**Goal**: Garantir que preferências sejam memorizadas por livro (com fallback global) e que a navegação por teclado e tecnologias assistivas seja completa.

**Independent Test**: Personalizar a visualização de um livro específico, recarregar a página e validar restauração; operar o seletor exclusivamente por teclado via setas e Tab.

### Testes para User Story 2

- [X] T012 [P] [US2] Adicionar testes unitários de persistência híbrida (`caderno_preferred_view_{bookId}` vs `caderno_default_view`) e controle de teclado em `caderno-leitura-0.1/frontend/tests/study-views.test.mjs`

### Implementação para User Story 2

- [X] T013 [US2] Implementar navegação acessível por teclado (setas direcionais, Home/End) e anéis de foco visíveis em `caderno-leitura-0.1/frontend/src/components/views/ViewSwitcher.vue`
- [X] T014 [US2] Assegurar sincronização bidirecional do estudo ativo (`activeStudyId`) entre a comutação de renderers e o painel de contexto em `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: Seletor 100% acessível (WAI-ARIA) e preferências persistidas de forma transparente.

---

## Phase 5: User Story 3 - Adaptação Responsiva do Dashboard de Leitura no Celular (Priority: P3)

**Goal**: Adequar a tela de Dashboard para smartphones (< 768px), com métricas em 2 colunas harmônicas, mapa de calor posicionado na semana atual e botões táteis de 44x44px.

**Independent Test**: Acessar o Dashboard em um celular ou janela de 375px a 390px e verificar grid equilibrada, mapa de calor focado na data atual e ausência de rolagem horizontal desnecessária.

### Testes para User Story 3

- [X] T015 [P] [US3] Adicionar testes unitários para a comutação responsiva e layout de 2 colunas do dashboard em `caderno-leitura-0.1/frontend/tests/study-views.test.mjs`

### Implementação para User Story 3

- [X] T016 [US3] Reajustar a grade de métricas de `DashboardView.vue` para 2 colunas proporcionais com destaque de largura total para o cartão de Sequência (`.streak-card span 2`) em resoluções móveis (< 768px)
- [X] T017 [US3] Implementar auto-scroll horizontal suave para o mês atual/semana corrente no carregamento móvel em `caderno-leitura-0.1/frontend/src/components/HeatmapCalendar.vue`
- [X] T018 [US3] Calibrar botões de ação e links da linha do tempo com área de toque mínima de 44x44px e tipografia responsiva em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue`

**Checkpoint**: Experiência do Dashboard agradável, ergonômica e perfeita no celular.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harmonização com as Superclasses, testes de regressão e compilação de produção.

- [X] T019 Calibrar transições suaves entre visualizações respeitando as 5 Superclasses de interface e a diretriz `@media (prefers-reduced-motion: reduce)` em `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [X] T020 Executar build estrito de produção do frontend via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T021 Executar suíte completa de testes automatizados do frontend via `npm test` e do backend via `pytest`
- [X] T022 Validar roteiro manual de visualizações e responsividade mobile conforme `specs/019-sistema-visualizacoes/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (Tipos e Tokens)
   └──> Phase 2: Foundational (useViewPreference, ViewSwitcher, Grid e List Renderers)
           ├──> Phase 3: User Story 1 (P1 - 5 Modos Plugáveis no Livro) [MVP]
           ├──> Phase 4: User Story 2 (P2 - Persistência Híbrida e Teclado WAI-ARIA)
           └──> Phase 5: User Story 3 (P3 - Dashboard Responsivo no Celular)
                   └──> Phase 6: Polish & Cross-Cutting Concerns
```

### User Story Dependencies

- **User Story 1 (P1)**: Depende da Fase 2. Entrega os 5 renderers funcionais na visão do livro (MVP).
- **User Story 2 (P2)**: Depende da Fase 2 e enriquece o `ViewSwitcher` com persistência e teclado.
- **User Story 3 (P3)**: Independente da visão do livro; foca no `DashboardView.vue` e `HeatmapCalendar.vue`.
- **Phase 6**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- `T004`, `T005` e `T006` podem ser desenvolvidos em paralelo dentro da Fase 2.
- `T008`, `T009` e `T010` (renderers Árvore, Mapa e Canvas) podem ser criados em paralelo na Fase 3.
- `T007`, `T012` e `T015` (testes de cada história) podem ser estruturados em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Tipos e Tokens).
2. Concluir Phase 2 (Foundational: composable e renderers Grade/Lista).
3. Concluir Phase 3 (Renderers Árvore, Mapa e Canvas + integração no `BookView.vue`).
4. **Validar MVP**: Comutação suave entre as 5 visões com preservação do estudo ativo.

### Incremental Delivery

1. Setup + Foundational -> Estrutura base pronta.
2. US1 -> 5 visualizações operacionais no livro (MVP).
3. US2 -> Teclado acessível e persistência híbrida.
4. US3 -> Reajuste responsivo do Dashboard no celular.
5. Polish -> `npm run build`, `npm test` e `pytest` 100% verdes.
