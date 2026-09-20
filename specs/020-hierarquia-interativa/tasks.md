# Tasks: F02 — Hierarquia Interativa

**Feature Branch**: `020-hierarquia-interativa`  
**Date**: 2026-09-19  
**Status**: Completed  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura básica de banco de dados, migração e contratos de tipos compartilhados.

- [X] T001 Criar migração Alembic adicionando parent_study_id, position e índices em caderno-leitura-0.1/backend/migrations/versions/0006_add_study_hierarchy_and_position.py
- [X] T002 Atualizar modelo SQLAlchemy Study com parent_study_id, position e relacionamentos hierárquicos em caderno-leitura-0.1/backend/app/models/study.py
- [X] T003 [P] Atualizar schemas Pydantic StudySummary, StudyRead, StudyPatch e StudyMoveRequest em caderno-leitura-0.1/backend/app/schemas/study.py
- [X] T004 [P] Atualizar definições de tipos TypeScript com parent_study_id, position, StudyTreeNode e StudyMovePayload em caderno-leitura-0.1/frontend/src/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Regras de negócio centrais no backend (prevenção DAG, limite de 5 níveis, cascata na lixeira e endpoint de movimentação) que bloqueiam a interface.

- [X] T005 Implementar serviço de integridade hierárquica e validação de ciclos DAG com limite de 5 níveis em caderno-leitura-0.1/backend/app/services/study_service.py
- [X] T006 Atualizar serviço de lixeira com soft delete e restauração em cascata lógica pai/filhos em caderno-leitura-0.1/backend/app/services/trash_service.py
- [X] T007 Implementar endpoint POST /api/studies/{study_id}/move com verificação de concorrência em caderno-leitura-0.1/backend/app/routers/studies.py
- [X] T008 [P] Criar testes automatizados de backend para integridade DAG, profundidade máxima, concorrência e cascata na lixeira em caderno-leitura-0.1/backend/tests/test_study_hierarchy.py

**Checkpoint**: Base relacional e API autoritativa prontas — implementação das histórias de usuário pode prosseguir.

---

## Phase 3: User Story 1 - Estruturação e Visualização Hierárquica em Árvore (Priority: P1) 🎯 MVP

**Goal**: Permitir visualizar estudos estruturados em ramos hierárquicos com indentação proporcional, recolhimento/expansão de nós, contadores de filhos e persistência do estado da árvore.

**Independent Test**: Carregar capítulo com estudos aninhados, verificar indentação progressiva visual, colapsar/expandir ramos e confirmar persistência após recarregar página.

### Implementation for User Story 1

- [X] T009 [US1] Criar composable useStudyHierarchy com algoritmo de montagem de árvore, cálculo de profundidade e persistência de expansão em caderno-leitura-0.1/frontend/src/composables/useStudyHierarchy.ts
- [X] T010 [P] [US1] Criar componente atômico StudyTreeNodeItem para renderização recursiva, chevrons e badges de contagem em caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue
- [X] T011 [US1] Refatorar componente StudyTreeView para integrar useStudyHierarchy e renderizar ramos hierárquicos em caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue
- [X] T012 [P] [US1] Criar testes unitários para useStudyHierarchy e renderização visual da árvore em caderno-leitura-0.1/frontend/tests/study-tree.test.mjs

**Checkpoint**: Visualização em Árvore com hierarquia pura, recolhimento e persistência funcional de forma independente (MVP).

---

## Phase 4: User Story 2 - Reorganização por Drag-and-Drop e Prevenção Matemática de Ciclos (Priority: P2)

**Goal**: Arrastar e soltar estudos para reposicionar entre irmãos ou aninhar como filhos, com drop zones verticais distintas (25% superior/inferior para irmãos, 50% central para adoção) e bloqueio preventivo visual e autoritativo de ciclos.

**Independent Test**: Arrastar um nó sobre outro para aninhar; reordenar nós entre irmãos; tentar soltar um nó pai em seu próprio filho e verificar indicação de proibição e bloqueio.

### Implementation for User Story 2

- [X] T013 [US2] Estender useStudyHierarchy com manipuladores HTML5 Drag and Drop nativo e detecção preventiva de ciclos em caderno-leitura-0.1/frontend/src/composables/useStudyHierarchy.ts
- [X] T014 [US2] Atualizar StudyTreeNodeItem com drag handles, feedback de drop zone (irmão vs filho) e classes de proibição em caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue
- [X] T015 [US2] Integrar despacho de movimentação à API /api/studies/{study_id}/move com controle de concorrência e rollback em caso de erro em caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue
- [X] T016 [P] [US2] Criar testes unitários para drag-and-drop, detecção de ciclos no cliente e chamadas de persistência em caderno-leitura-0.1/frontend/tests/study-tree-dnd.test.mjs

**Checkpoint**: Reorganização por Drag and Drop fluida e protegida contra loops infinitos em desktop.

---

## Phase 5: User Story 3 - Ergonomia Móvel e Ações Acessíveis de Hierarquia (Priority: P3)

**Goal**: Menu tátil de ações rápidas no card ("Promover nó", "Recuar nó", "Mover para cima", "Mover para baixo") com alvos mínimos de 44x44px no mobile e atalhos WAI-ARIA Treeview no teclado.

**Independent Test**: Emular tela móvel (< 768px), abrir menu tátil e reordenar/aninhar estudos com toque confortável; navegar e reorganizar árvore utilizando apenas o teclado.

### Implementation for User Story 3

- [X] T017 [US3] Implementar menu tátil de ações rápidas (Promover, Recuar, Subir, Descer) com botões mínimos de 44x44px em caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue
- [X] T018 [US3] Implementar navegação acessível por teclado WAI-ARIA Treeview e atalhos de reordenação estrutural em caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue
- [X] T019 [P] [US3] Criar testes automatizados de acessibilidade móvel e atalhos de teclado em caderno-leitura-0.1/frontend/tests/study-tree-a11y.test.mjs

**Checkpoint**: Hierarquia totalmente controlável e inclusiva em dispositivos móveis e tecnologias assistivas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação de regressão, build de produção e verificação cruzada de integridade.

- [X] T020 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T021 [P] Executar suíte de testes de regressão do frontend e build de produção Vite em caderno-leitura-0.1/frontend/
- [X] T022 Atualizar documentação e registrar guia de execução em specs/020-hierarquia-interativa/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T004)
        │
        ▼
Phase 2: Foundational (T005-T008)
        │
        ├────────────────────────────────┐
        ▼                                ▼
Phase 3: User Story 1 (T009-T012)  [MVP]  (Base para visualização)
        │
        ▼
Phase 4: User Story 2 (T013-T016)         (Reorganização Drag-and-Drop)
        │
        ▼
Phase 5: User Story 3 (T017-T019)         (Ergonomia Móvel e Acessibilidade)
        │
        ▼
Phase 6: Polish (T020-T022)               (Validação final e build)
```

### Parallel Opportunities

- **Phase 1**: T003 (schemas Pydantic) e T004 (types TypeScript) podem rodar em paralelo.
- **Phase 2**: T008 (testes de backend) pode ser iniciado em paralelo com T006/T007.
- **Phase 3**: T010 (`StudyTreeNodeItem.vue`) e T012 (testes do frontend) podem ser desenvolvidos em paralelo com T009.
- **Phase 4**: T016 (testes DnD) pode rodar em paralelo após T013.
- **Phase 5**: T019 (testes A11y) pode rodar em paralelo com T017/T018.
- **Phase 6**: T020 (testes backend) e T021 (testes/build frontend) rodam em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001 a T004) e Foundational (T005 a T008).
2. Concluir User Story 1 (T009 a T012).
3. **VALIDAR MVP**: Testar a visualização hierárquica em árvore pura com dados de exemplo.

### Incremental Delivery
1. Setup + Foundational: Banco, modelos, serviços e endpoint prontos.
2. User Story 1 (P1): Visualização em árvore com expansão/recolhimento e persistência.
3. User Story 2 (P2): Drag and drop nativo com zonas de drop e proteção contra ciclos.
4. User Story 3 (P3): Menu tátil 44x44px e acessibilidade WAI-ARIA no mobile.
5. Polish: Validação ponta a ponta sem qualquer impacto no banco ativo.
