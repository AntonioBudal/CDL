# Tasks: F 0.7.6 — Redesenho da Tree View: Hierarquia Cognitiva e Estruturação de Tópicos

**Feature**: F 0.7.6 — Redesenho da Tree View  
**Branch**: `055-redesenho-tree-view`  
**Date**: 2026-10-04  
**Spec**: [specs/055-redesenho-tree-view/spec.md](spec.md) | **Plan**: [specs/055-redesenho-tree-view/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição dos tipos TypeScript para progresso agregado e nós estendidos de árvore.

- [x] T001 [P] Estender interface TypeScript `StudyTreeNode` e definir tipos `BranchProgress` e `BranchProgressDetails` em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de cálculo e métricas de progresso de ramo em tempo linear ($O(N)$).

- [x] T002 Implementar função pura `calculateBranchProgress` e estender `buildStudyTree` para computar métricas recursivas em `caderno-leitura-0.1/frontend/src/composables/useStudyHierarchy.ts`
- [x] T003 [P] Criar testes unitários para agregação recursiva de progresso, contagem de descendentes e completude consolidada em `caderno-leitura-0.1/frontend/tests/study-tree.test.mjs`

**Checkpoint**: Base de dados de progresso pronta — qualquer nó pai na árvore tem métricas precisas de completude do seu ramo temático.

---

## Phase 3: User Story 1 - Visualização Hierárquica Elegante e Controles Globais de Ramos (Priority: P1) 🎯 MVP

**Goal**: Renderizar a árvore com linhas guias conectoras contínuas em CSS puro, botões globais "Expandir Todos" e "Recolher Todos", e persistência no `localStorage` com estado inicial totalmente expandido.

**Independent Test**: Carregar um capítulo estruturado; verificar a presença de linhas guias em "L" unindo pais a filhos, acionar "Recolher Todos" e "Expandir Todos" no topo, e verificar persistência dos nós recolhidos no `localStorage`.

### Tests for User Story 1 🧪

- [x] T004 [P] [US1] Criar testes unitários para gerenciamento de nós colapsados, `expandAll`, `collapseAll` e persistência no localStorage sob `caderno_tree_collapsed_${bookId}` em `caderno-leitura-0.1/frontend/tests/study-tree.test.mjs`

### Implementation for User Story 1

- [x] T005 [US1] Implementar gerenciamento de `collapsedNodeIds` com abertura total padrão, métodos `expandAll()`, `collapseAll()` e sincronização com `localStorage` em `caderno-leitura-0.1/frontend/src/composables/useStudyHierarchy.ts`
- [x] T006 [US1] Implementar linhas guias conectoras contínuas em CSS puro (`::before` e `::after`) em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue` e `caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue`
- [x] T007 [US1] Integrar botões globais "Expandir Todos" e "Recolher Todos" e contador consolidado na barra superior em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue`

**Checkpoint**: User Story 1 concluída — a Tree View funciona como uma árvore visual elegante com controle total de expansão (MVP).

---

## Phase 4: User Story 2 - Percepção e Indicadores de Progresso Agregado por Ramo (Priority: P2)

**Goal**: Exibir em cada nó pai um micro-badge com fração textual (`2/4 concluídos`), mini-barra proporcional de progresso e tooltip contextual com detalhamento dos status do ramo.

**Independent Test**: Criar um nó pai com subestudos em múltiplos estados; verificar a renderização do micro-badge com fração e barra, e confirmar que nós folha não exibem o indicador.

### Tests for User Story 2 🧪

- [x] T008 [P] [US2] Criar testes unitários para a renderização de `branch-progress-badge`, fração textual e mini-barra de progresso em `caderno-leitura-0.1/frontend/tests/study_tree_view.test.mjs`

### Implementation for User Story 2

- [x] T009 [US2] Implementar marcação semântica e estilização do micro-badge `branch-progress-badge` com fração, mini-barra de progresso e tooltip informativo em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue`

**Checkpoint**: User Stories 1 e 2 integradas — a árvore agora atua como uma ferramenta diagnóstica viva do amadurecimento dos estudos.

---

## Phase 5: User Story 3 - Reorganização Magnética, Bloqueio de Ciclos e Ergonomia Mobile (Priority: P3)

**Goal**: Drag-and-drop magnético com distinção visual evidente de inserção linear vs aninhamento subordinado, bloqueio rigoroso de ciclos e profundidade máxima de 5 níveis, além de alvos táteis mínimos de 44×44px no mobile.

**Independent Test**: Arrastar nó sobre card e verificar moldura magnética na zona central; verificar que soltura em descendente ou profundidade > 4 é bloqueada; inspecionar alvos de 44px nos chevrons e menu de ações táteis.

### Tests for User Story 3 🧪

- [x] T010 [P] [US3] Criar testes unitários para as zonas de drag-and-drop, moldura magnética de absorção central e alvos de toque de 44px em `caderno-leitura-0.1/frontend/tests/study_tree_view.test.mjs`

### Implementation for User Story 3

- [x] T011 [US3] Aprimorar cálculo de zonas de drag-and-drop com moldura magnética de absorção no aninhamento e bloqueio determinístico de ciclos/profundidade em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue`
- [x] T012 [US3] Garantir alvos de toque mínimos de 44×44px nos botões de chevron e menu de ações táteis ("Mover para cima", "Mover para baixo", "Promover", "Recuar") em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue`

**Checkpoint**: Todas as 3 User Stories concluídas, acessíveis e responsivas em qualquer dispositivo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, testes de regressão de ponta a ponta e build de produção.

- [x] T013 [P] Validar os 5 cenários de teste fim a fim de `specs/055-redesenho-tree-view/quickstart.md`
- [x] T014 Executar e validar suite de testes completa com `npm test` e `pytest`
- [x] T015 Validar tipagem e build de produção com `npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as User Stories.
- **User Story 1 (Phase 3)**: Depende da Phase 2 (Foundational) — MVP.
- **User Story 2 (Phase 4)**: Depende da Phase 2 e integra com US1.
- **User Story 3 (Phase 5)**: Depende da Phase 2 e integra com US1.
- **Polish (Phase 6)**: Depende da conclusão de todas as User Stories.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir Setup (T001) e Foundational (T002, T003).
2. Concluir User Story 1 (T004, T005, T006, T007).
3. Validar de forma independente: árvore legível com linhas guias, botões de expandir/recolher funcionais e persistência.

### Incremental Delivery

1. Setup + Foundational (cálculo de BranchProgress).
2. Adicionar US1 (MVP de visualização e controle global).
3. Adicionar US2 (micro-badge de progresso em nós ancestrais).
4. Adicionar US3 (drag-and-drop magnético, bloqueio de ciclos e ergonomia mobile de 44px).
5. Polish e build de produção.
