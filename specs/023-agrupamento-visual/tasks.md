# Tasks: F05 — Agrupamento Visual

**Feature Branch**: `023-agrupamento-visual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Implementation Plan**: [plan.md](./plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura relacional, migração de banco e tipagens compartilhadas.

- [X] T001 Criar migração Alembic para adição da coluna reading_status em studies com valor padrão 'rascunho' e criação da tabela canvas_frames com restrições e índices em caderno-leitura-0.1/backend/migrations/versions/0009_add_reading_status_and_canvas_frames.py
- [X] T002 Atualizar modelo declarativo SQLAlchemy Study com atributo reading_status em caderno-leitura-0.1/backend/app/models/study.py e criar modelo CanvasFrame em caderno-leitura-0.1/backend/app/models/canvas_frame.py registrando em caderno-leitura-0.1/backend/app/models/__init__.py
- [X] T003 [P] Criar schemas Pydantic v2 para validação de entrada, saída, atualização de status e molduras manuais em caderno-leitura-0.1/backend/app/schemas/study_grouping.py
- [X] T004 [P] Definir tipos TypeScript para ReadingStatus, StudyGroupByCriteria, CanvasFrameItem, StudyGroup e payloads em caderno-leitura-0.1/frontend/src/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura transacional do backend, consultas de integridade e cliente de API.

- [X] T005 Implementar métodos de persistência para atualização de reading_status com concorrência otimista e operações CRUD de canvas_frames em caderno-leitura-0.1/backend/app/services/study_service.py e caderno-leitura-0.1/backend/app/services/canvas_service.py
- [X] T006 Implementar endpoints REST para atualização de status em caderno-leitura-0.1/backend/app/routers/studies.py e rotas de molduras do canvas em caderno-leitura-0.1/backend/app/routers/canvas.py
- [X] T007 [P] Implementar métodos no cliente HTTP api.ts para atualização de status de leitura e gestão de molduras manuais em caderno-leitura-0.1/frontend/src/services/api.ts
- [X] T008 [P] Criar suíte de testes de integração automatizados da API de status de estudos, integridade de restrições e molduras manuais em caderno-leitura-0.1/backend/tests/test_study_grouping_api.py

**Checkpoint**: Base relacional, integridade de banco e endpoints REST essenciais 100% funcionais e testados.

---

## Phase 3: User Story 1 - Agrupamento Reativo em Grade e Lista por Critérios Estruturais (Priority: P1) [MVP]

**Goal**: Permitir que o leitor reparticione dinamicamente os estudos em seções visuais colapsáveis (por Capítulo, por Categoria e por Data) nas visões de Grade e Lista, com persistência no navegador e sem mutação dos dados estruturais.

**Independent Test**: Abrir um livro com múltiplos estudos e categorias; alternar o agrupamento para "Por Categoria" e "Por Data"; verificar o particionamento imediato em raias com contadores e controle de colapso, restaurando a ordenação por capítulo ao selecionar "Por Capítulo".

### Implementation for User Story 1

- [X] T009 [US1] Implementar composable reativo useStudyGrouping para particionamento funcional em memória por chapter, category e date em caderno-leitura-0.1/frontend/src/composables/useStudyGrouping.ts
- [X] T010 [US1] Criar componente GroupSection para renderização de seções de grupo com cabeçalho descritivo, contador de itens e botão de colapso em caderno-leitura-0.1/frontend/src/components/views/GroupSection.vue
- [X] T011 [US1] Criar componente GroupBySelector com menu visual de seleção do critério de agrupamento e persistência no localStorage em caderno-leitura-0.1/frontend/src/components/views/GroupBySelector.vue
- [X] T012 [US1] Integrar GroupBySelector e GroupSection nos renderers de visualização StudyGridView e StudyListView em caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue e caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue
- [X] T013 [P] [US1] Criar testes unitários para particionamento funcional por capítulo, categoria e data e preservação de estado colapsado em caderno-leitura-0.1/frontend/tests/study-grouping.test.mjs

**Checkpoint**: MVP funcional. O usuário pode reorganizar os estudos em Grade e Lista por múltiplos critérios estruturais instantaneamente.

---

## Phase 4: User Story 2 - Ciclo de Maturação e Agrupamento por Status de Leitura (Priority: P2)

**Goal**: Registrar o estado de maturação do estudo através do ciclo canônico de 4 estados (rascunho, em_estudo, revisado, concluido) e agrupar os estudos sob essas fases de síntese.

**Independent Test**: Atribuir status de leitura a três estudos; ativar o agrupamento "Por Status de Leitura" e verificar a separação nas 4 raias sequenciais, alterando o status de um estudo e confirmando sua transferência suave de grupo.

### Implementation for User Story 2

- [X] T014 [US2] Implementar endpoint PATCH /api/studies/{id}/status com validação de domínio canônico e concorrência otimista em caderno-leitura-0.1/backend/app/routers/studies.py
- [X] T015 [US2] Estender composable useStudyGrouping com a lógica de particionamento e ordenação das 4 raias de status em caderno-leitura-0.1/frontend/src/composables/useStudyGrouping.ts
- [X] T016 [US2] Criar componente StudyStatusBadge para seleção e exibição de status com transição reativa nos cards e na visualização de estudo em caderno-leitura-0.1/frontend/src/components/StudyStatusBadge.vue e caderno-leitura-0.1/frontend/src/views/StudyView.vue
- [X] T017 [P] [US2] Implementar testes de concorrência e transição de status na suíte de testes de integração em caderno-leitura-0.1/backend/tests/test_study_grouping_api.py

**Checkpoint**: Ciclo editorial de maturação integrado às telas de exploração e leitura.

---

## Phase 5: User Story 3 - Molduras Espaciais Manuais no Canvas 2D (Priority: P3)

**Goal**: Permitir a criação de molduras delimitadoras visuais (frames) coloridas e nomeadas no Canvas 2D, com movimentação solidária em bloco dos estudos contidos e projeção reversível não-destrutiva ao aplicar agrupamentos automáticos.

**Independent Test**: No Canvas de um livro, criar uma moldura retangular ao redor de estudos; arrastar a moldura e constatar que os nós contidos se movem juntos com a moldura; aplicar agrupamento por categoria e retornar para livre, comprovando a restauração intacta das coordenadas originais salvas.

### Implementation for User Story 3

- [X] T018 [US3] Implementar endpoints GET/POST /api/books/{id}/canvas/frames e PATCH/DELETE /api/canvas/frames/{id} com validação de dimensões e expurgo em cascata em caderno-leitura-0.1/backend/app/routers/canvas.py
- [X] T019 [US3] Implementar composable useCanvasFrames com cálculo geométrico de contenção retangular, arrasto solidário de nós contidos e projeção reversível em caderno-leitura-0.1/frontend/src/composables/useCanvasFrames.ts
- [X] T020 [US3] Criar componente CanvasFrameNode com retângulo visual, título editável, seletor de cor e alvos táteis de redimensionamento em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasFrameNode.vue
- [X] T021 [US3] Integrar CanvasFrameNode e motor de projeção reversível dentro do palco 2D mantendo sincronização de coordenadas em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T022 [P] [US3] Criar testes unitários para cálculo de contenção espacial de frames, movimentação solidária em bloco e projeção reversível em caderno-leitura-0.1/frontend/tests/canvas-frames.test.mjs

**Checkpoint**: Pensamento espacial no Canvas 2D com zoneamento por molduras manuais e arrasto em bloco operando a 60fps.

---

## Phase 6: User Story 4 - Ergonomia Móvel, Cabeçalhos Aderentes e Acessibilidade (Priority: P4)

**Goal**: Assegurar navegação fluida em telas móveis com cabeçalhos aderentes (sticky headers), contadores de itens por grupo, navegação acessível por teclado WAI-ARIA e alvos táteis mínimos de 44x44px.

**Independent Test**: Emular tela de smartphone de 375px; rolar verticalmente estudos agrupados constatando a fixação aderente dos cabeçalhos de grupo no topo da tela e alternar a expansão de seções via teclado com teclas Enter e Espaço.

### Implementation for User Story 4

- [X] T023 [US4] Implementar estilos de cabeçalho aderente (sticky position), contadores de itens e semântica WAI-ARIA role="region" e aria-expanded em caderno-leitura-0.1/frontend/src/components/views/GroupSection.vue
- [X] T024 [US4] Garantir que todos os seletores de agrupamento, botões de colapso e controles de status possuam áreas de toque mínimas de 44x44px em caderno-leitura-0.1/frontend/src/components/views/GroupBySelector.vue e caderno-leitura-0.1/frontend/src/components/views/GroupSection.vue
- [X] T025 [P] [US4] Criar testes automatizados de acessibilidade WAI-ARIA, cabeçalhos aderentes e ergonomia tátil em caderno-leitura-0.1/frontend/tests/study-grouping-a11y.test.mjs

**Checkpoint**: Interface 100% acessível, confortável e ergonômica tanto no desktop quanto em telas móveis.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação rigorosa de regressão, compilação de produção e integridade da Constituição.

- [X] T026 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T027 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T028 Atualizar guia de validação executável e registrar evidências finais em specs/023-agrupamento-visual/quickstart.md

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
Phase 3: User Story 1 (T009-T013)  [MVP]  (Agrupamento em Grade e Lista por Capítulo, Categoria e Data)
        │
        ▼
Phase 4: User Story 2 (T014-T017)         (Ciclo de leitura e agrupamento por Status de Maturação)
        │
        ▼
Phase 5: User Story 3 (T018-T022)         (Molduras espaciais no Canvas 2D e arrasto em bloco)
        │
        ▼
Phase 6: User Story 4 (T023-T025)         (Ergonomia móvel, sticky headers e acessibilidade)
        │
        ▼
Phase 7: Polish (T026-T028)               (Regressão completa, build Vite e validação)
```

### Parallel Opportunities

- **Phase 1**: T003 (schemas Pydantic) e T004 (types TypeScript) podem rodar em paralelo.
- **Phase 2**: T007 (cliente de API frontend) e T008 (testes de API backend) podem rodar em paralelo.
- **Phase 3**: T010 (GroupSection) e T013 (testes unitários) podem rodar em paralelo com T009.
- **Phase 4**: T016 (StudyStatusBadge) e T017 (testes de status) podem rodar em paralelo com T014.
- **Phase 5**: T020 (CanvasFrameNode) e T022 (testes de contenção) podem rodar em paralelo com T018.
- **Phase 6**: T024 (alvos táteis de 44px) e T025 (testes a11y) podem rodar em paralelo.
- **Phase 7**: T026 (regressão backend) e T027 (regressão frontend + build) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T004) e Foundational (T005-T008).
2. Concluir User Story 1 (T009-T013).
3. **Validar MVP**: Reparticionamento dinâmico em Grade e Lista por Capítulo, Categoria e Data com restauração instantânea.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Migração Alembic `0009`, modelo `CanvasFrame`, coluna `reading_status` e endpoints REST prontos.
2. US1 $\rightarrow$ Agrupamento reativo em Grade e Lista (MVP).
3. US2 $\rightarrow$ Ciclo editorial de maturação em 4 estados e agrupamento por status.
4. US3 $\rightarrow$ Molduras delimitadoras manuais (*frames*) no Canvas 2D com arrasto solidário e projeção reversível.
5. US4 $\rightarrow$ Cabeçalhos aderentes (*sticky headers*), contadores de itens e conformidade WAI-ARIA de 44x44px.
6. Polish $\rightarrow$ Regressão integral e verificação de conformidade com a Constituição.
