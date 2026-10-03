# Tasks: F 0.7.5 — Redesenho da List View: Busca Rápida, Filtragem e Comparação Analítica

**Feature**: F 0.7.5 — Redesenho da List View  
**Branch**: `054-redesenho-list-view`  
**Date**: 2026-10-03  
**Spec**: [specs/054-redesenho-list-view/spec.md](spec.md) | **Plan**: [specs/054-redesenho-list-view/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição das extensões de schema e tipagens de completude analítica e ordenação.

- [x] T001 [P] Estender schema Pydantic `StudySummary` com `has_summary`, `has_explanation`, `has_concepts` e `has_references` em `caderno-leitura-0.1/backend/app/schemas/study.py`
- [x] T002 [P] Estender interface TypeScript `StudySummary` e tipos de ordenação em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: População das flags booleanas de seções preenchidas no backend com O(0) consultas adicionais.

- [x] T003 Criar suíte de testes de integração backend para as flags de seções analíticas em `caderno-leitura-0.1/backend/tests/test_study_list_summary.py`
- [x] T004 Popular flags `has_summary`, `has_explanation`, `has_concepts` e `has_references` no endpoint `list_studies` em `caderno-leitura-0.1/backend/app/routers/studies.py`

**Checkpoint**: Base de dados pronta — a API entrega flags leves de completude para alimentar os micro-chips analíticos da List View.

---

## Phase 3: User Story 1 - Tabela Analítica Densa com Ordenação Multicritério (Priority: P1) 🎯 MVP

**Goal**: Apresentar tabela estruturada de alta densidade no desktop com cabeçalhos ordenáveis por título, status e data com ciclo tripartite (`asc` -> `desc` -> `default`) persistido no `localStorage`.

**Independent Test**: Renderizar a lista de estudos, clicar nos cabeçalhos e verificar que as linhas reorganizam-se com setas de ordenação e que a preferência persiste ao recarregar.

### Tests for User Story 1 🧪

- [x] T005 [P] [US1] Criar testes unitários para ciclo tripartite de ordenação, persistência no localStorage e navegação em `caderno-leitura-0.1/frontend/tests/study_list_filters.test.mjs`

### Implementation for User Story 1

- [x] T006 [US1] Implementar lógica de ordenação multicritério tripartite e persistência em `caderno-leitura-0.1/frontend/src/composables/useStudyListFilters.ts`
- [x] T007 [US1] Implementar tabela semântica de alta densidade com cabeçalhos ordenáveis e indicadores visuais de direção em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`

**Checkpoint**: User Story 1 concluída — a List View opera como uma tabela de alta densidade e ordenação ágil (MVP).

---

## Phase 4: User Story 2 - Busca Textual Instantânea e Filtragem Rápida por Status (Priority: P2)

**Goal**: Permitir busca em tempo real insensível a acentos (< 50ms) e filtro de status, com contador de resultados e estado vazio acolhedor.

**Independent Test**: Digitar termos com/sem acentos no campo de busca e selecionar pílulas de status: a lista filtra instantaneamente sem recarregar e exibe botão "Limpar filtros" quando não houver correspondências.

### Tests for User Story 2 🧪

- [x] T008 [P] [US2] Criar testes unitários para busca textual sem acentos, filtro por status e reset em `caderno-leitura-0.1/frontend/tests/study_list_filters.test.mjs`

### Implementation for User Story 2

- [x] T009 [US2] Implementar busca reativa normalizada por diacríticos e filtro por status no composable `caderno-leitura-0.1/frontend/src/composables/useStudyListFilters.ts`
- [x] T010 [US2] Implementar campo de busca, pílulas de status, contador de resultados e estado vazio com ação "Limpar filtros" em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`

**Checkpoint**: User Stories 1 e 2 integradas — localização cirúrgica e segmentação de estudos operando com máxima velocidade.

---

## Phase 5: User Story 3 - Indicadores de Seções Preenchidas e Ergonomia Mobile Compacta (Priority: P3)

**Goal**: Exibir 4 micro-chips fixos com siglas (`R`, `E`, `C`, `Ref`) em cada estudo, layout mobile compacto de 2 linhas com gaveta expansível para filtros e alvos táteis mínimos de 44×44px.

**Independent Test**: Verificar que cada linha exibe os 4 micro-chips coloridos/esmaecidos conforme o preenchimento, e inspecionar que na viewport móvel (< 768px) o layout reorganiza-se em 2 níveis sem overflow horizontal.

### Tests for User Story 3 🧪

- [x] T011 [P] [US3] Criar testes unitários para micro-chips fixos de seções, layout móvel de 2 linhas e alvos táteis de 44px em `caderno-leitura-0.1/frontend/tests/study_list_view.test.mjs`

### Implementation for User Story 3

- [x] T012 [US3] Implementar micro-chips analíticos fixos (`R`, `E`, `C`, `Ref`), layout móvel compacto de 2 níveis com gaveta expansível e skeleton screens de carregamento em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`

**Checkpoint**: Todas as 3 User Stories concluídas e responsivas em qualquer dispositivo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, testes de regressão de ponta a ponta e build de produção.

- [x] T013 [P] Validar os 5 cenários de teste fim a fim de `specs/054-redesenho-list-view/quickstart.md`
- [x] T014 Executar e validar suite de testes completa com `npm test` e `pytest`
- [x] T015 Validar tipagem e build de produção com `npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 (schemas Pydantic e TypeScript definidos).
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 1 e 2.
- **User Story 2 (Phase 4)**: Depende da Phase 3 (composable base `useStudyListFilters.ts`).
- **User Story 3 (Phase 5)**: Depende da Phase 3 e 4 (estrutura tabular e de filtros finalizada).
- **Polish (Phase 6)**: Depende de todas as fases anteriores completas.

### User Story Dependencies

- **US1 (P1)**: Autônoma. Entrega tabela de alta densidade e ordenação tripartite.
- **US2 (P2)**: Conecta busca textual instantânea e filtro de status sobre a base da US1.
- **US3 (P3)**: Adiciona micro-chips analíticos de completude e layout compacto móvel de 2 níveis.

---

## Parallel Execution Opportunities

- `T001` (Backend schema) e `T002` (Frontend types) podem rodar em paralelo.
- `T005` (Testes ordenação), `T008` (Testes busca) e `T011` (Testes layout e chips) podem ser desenvolvidos em paralelo.
- `T013` (Quickstart) pode ser checado concorrentemente com os passos de compilação.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1: Tabela densa e ordenação tripartite).
3. **Validar MVP**: Navegação e ordenação rápida garantidas.

### Incremental Delivery
1. Setup + Foundational concluídos.
2. MVP (US1) validado e funcional.
3. Incorporar Busca Rápida e Filtros de Status (US2).
4. Incorporar Micro-Chips de Seções e Ergonomia Mobile (US3).
5. Executar suíte completa de testes (`npm test`, `pytest`, `npm run build`) e commit atômico.
