# Tasks: F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura

**Feature**: F 0.7.4 — Redesenho da Grid View  
**Branch**: `053-redesenho-grid-view`  
**Date**: 2026-10-03  
**Spec**: [specs/053-redesenho-grid-view/spec.md](spec.md) | **Plan**: [specs/053-redesenho-grid-view/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição dos tipos, schemas e contratos compartilhados de dados no backend e frontend.

- [X] T001 [P] Estender schema Pydantic `StudySummary` com `summary_preview`, `highlights_count` e `relations_count` em `caderno-leitura-0.1/backend/app/schemas/study.py`
- [X] T002 [P] Estender interface TypeScript `StudySummary` com `summary_preview`, `highlights_count` e `relations_count` em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Agregação de dados analíticos no backend em lote (O(1) round-trips) para alimentar a Grid View.

- [X] T003 Criar suíte de testes de integração backend para contagens agregadas em lote e prévia de resumo em `caderno-leitura-0.1/backend/tests/test_study_grid_summary.py`
- [X] T004 Implementar agregação em lote de `highlights_count`, `relations_count` e extração de `summary_preview` no endpoint `list_studies` em `caderno-leitura-0.1/backend/app/routers/studies.py`

**Checkpoint**: Base de dados agregada pronta — a API entrega metadados de densidade analítica e prévia textual com performance instantânea.

---

## Phase 3: User Story 1 - Identidade Editorial e Reconhecimento Cromático de Status (Priority: P1) 🎯 MVP

**Goal**: Apresentar cartões na grade com friso vertical de 4px na borda esquerda por status cromático, badge interativo no cabeçalho e clique integral que navega imediatamente para o estudo.

**Independent Test**: Renderizar a grade com estudos em múltiplos status (`rascunho`, `em_andamento`, `revisado`, `concluido`) e verificar a presença do friso cromático correspondente, foco por teclado (`tabindex="0"`, `@keydown.enter`) e clique integral com supressão de eventos na lixeira.

### Tests for User Story 1 🧪

- [X] T005 [P] [US1] Criar testes unitários para renderização de status cromáticos, clique integral do cartão e isolamento de eventos em `caderno-leitura-0.1/frontend/tests/study_grid_view.test.mjs`

### Implementation for User Story 1

- [X] T006 [US1] Implementar classes cromáticas de status com friso vertical esquerdo de 4px e superfície integral clicável com foco por teclado (`tabindex="0"`, `@keydown.enter`) em `caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue`

**Checkpoint**: User Story 1 concluída — a Grid View opera como um painel visual editorial imediato (MVP).

---

## Phase 4: User Story 2 - Cartografia de Densidade Analítica e Prévia do Resumo (Priority: P2)

**Goal**: Exibir nos cartões uma prévia tipográfica elegante de 2 a 3 linhas (`line-clamp`) e micro-indicadores visuais no rodapé informando quantidades de destaques e relações ativas.

**Independent Test**: Fornecer estudos com e sem resumo analítico, e com contagens de destaques/relações > 0: validar que o cartão exibe a prévia tipográfica suavemente cortada e os micro-badges no rodapé com ícone e contadores numéricos.

### Tests for User Story 2 🧪

- [X] T007 [P] [US2] Criar testes unitários para renderização da prévia analítica e dos mini-indicadores de contagem no rodapé em `caderno-leitura-0.1/frontend/tests/study_grid_view.test.mjs`

### Implementation for User Story 2

- [X] T008 [US2] Implementar bloco tipográfico de prévia analítica (`summary_preview` com fallback elegante) e micro-indicadores no rodapé em `caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue`

**Checkpoint**: User Stories 1 e 2 operando em harmonia — cada cartão carrega peso cognitivo e contexto analítico claro.

---

## Phase 5: User Story 3 - Grid Responsivo, Estados de Carregamento e Ergonomia Mobile (Priority: P3)

**Goal**: Garantir transição fluida entre 3, 2 e 1 colunas, telas de esqueleto (*Skeleton Screens*) animadas durante carregamento (`loading === true`) e alvos táteis mínimos de 44×44px no mobile.

**Independent Test**: Testar o componente com `loading: true` verificando 6 cartões esqueleto animados, e validar media queries responsivas (3 colunas > 1024px, 2 colunas 768-1023px, 1 coluna < 768px com botão de lixeira >= 44px).

### Tests for User Story 3 🧪

- [X] T009 [P] [US3] Criar testes unitários para verificação do estado de carregamento com Skeleton Screens e acessibilidade de botões em `caderno-leitura-0.1/frontend/tests/study_grid_view.test.mjs`

### Implementation for User Story 3

- [X] T010 [US3] Implementar componente de Skeleton Screens animados com geometria do cartão e media queries responsivas (3/2/1 colunas e alvo tátil de 44px) em `caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue`

**Checkpoint**: Todas as 3 User Stories concluídas e responsivas em qualquer dispositivo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, testes de regressão de ponta a ponta e build de produção.

- [X] T011 [P] Validar os 5 cenários de teste fim a fim de `specs/053-redesenho-grid-view/quickstart.md`
- [X] T012 Executar e validar suite de testes completa com `npm test` e `pytest`
- [X] T013 Validar tipagem e build de produção com `npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 (schemas Pydantic e TypeScript definidos). Bloqueia a integração de dados da grade.
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 2 para integração completa, ou pode ter testes e layout iniciados em paralelo.
- **User Story 2 (Phase 4)**: Depende da Phase 3 (estrutura de cartão base e schemas analíticos).
- **User Story 3 (Phase 5)**: Depende da Phase 3 e 4 (estrutura do cartão definida para replicação fiel do skeleton).
- **Polish (Phase 6)**: Depende de todas as fases anteriores estarem completas.

### User Story Dependencies

- **US1 (P1)**: Autônoma. Entrega valor imediato de reconhecimento visual cromático e navegação de 1 clique.
- **US2 (P2)**: Adiciona a camada de densidade de conteúdo sobre os cartões da US1.
- **US3 (P3)**: Adiciona skeletons e refinamentos responsivos para enriquecer a experiência de carregamento da US1 e US2.

---

## Parallel Execution Opportunities

- `T001` (Backend schemas) e `T002` (Frontend types) podem rodar em paralelo.
- `T005` (Testes US1), `T007` (Testes US2) e `T009` (Testes US3) podem ser elaborados de forma concorrente em blocos dedicados de testes.
- `T011` (Quickstart scenarios) pode ser validado em paralelo com a revisão de documentação.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1: cromatismo de status e clique integral).
3. **Validar MVP**: Navegação e reconhecimento imediato garantidos.

### Incremental Delivery
1. Setup + Foundational concluídos.
2. MVP (US1) validado e funcional.
3. Incorporar Densidade Analítica (US2: prévias e micro-badges).
4. Incorporar Responsividade e Skeletons (US3: 3/2/1 colunas e loading state).
5. Executar suíte completa de testes (`npm test`, `pytest`, `npm run build`) e commit atômico.
