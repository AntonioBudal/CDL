# Tasks: F04 — Relações entre Estudos

**Feature Branch**: `022-relacoes-estudos`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Implementation Plan**: [plan.md](./plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura relacional, migração de banco e tipagens compartilhadas.

- [X] T001 Criar migração Alembic para criação da tabela study_relations com constraints ck_study_relations_no_self, ck_study_relations_type, uq_study_relations_src_tgt_type e índices de performance em caderno-leitura-0.1/backend/migrations/versions/0008_add_study_relations.py
- [X] T002 Criar modelo declarativo SQLAlchemy StudyRelation com relacionamentos source_study e target_study em caderno-leitura-0.1/backend/app/models/study_relation.py e registrar em caderno-leitura-0.1/backend/app/models/__init__.py
- [X] T003 [P] Criar schemas Pydantic v2 para validação de entrada, saída, resumos conectados e tipos semânticos em caderno-leitura-0.1/backend/app/schemas/study_relation.py
- [X] T004 [P] Definir tipos TypeScript para StudyRelationType, StudyRelationItem, StudyRelationsResponse e payloads em caderno-leitura-0.1/frontend/src/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura transacional do backend, consultas de integridade e cliente de API.

- [X] T005 Implementar serviço StudyRelationService com criação de relações, validação anti-duplicação, consulta unificada de backlinks com junções de títulos/livros e filtragem de soft delete em caderno-leitura-0.1/backend/app/services/study_relation_service.py
- [X] T006 Implementar roteador REST de relações com endpoints GET/POST /api/studies/{id}/relations e registrar em caderno-leitura-0.1/backend/app/routers/study_relations.py e caderno-leitura-0.1/backend/app/main.py
- [X] T007 [P] Implementar métodos no cliente HTTP api.ts para consumo de relações, criação, remoção e consulta de candidatos em caderno-leitura-0.1/frontend/src/services/api.ts
- [X] T008 [P] Criar suíte de testes de integração automatizados da API de relações e integridade de restrições em caderno-leitura-0.1/backend/tests/test_study_relations_api.py

**Checkpoint**: Base relacional, integridade de banco e endpoints REST essenciais 100% funcionais e testados.

---

## Phase 3: User Story 1 - Conexões Semânticas e Referências Cruzadas Bidirecionais (Priority: P1) [MVP]

**Goal**: Permitir que o leitor crie vínculos conceituais explícitos entre dois estudos e visualize automaticamente os backlinks reversos no estudo de destino com navegação bidirecional imediata.

**Independent Test**: Criar uma relação do tipo "complementa" entre o Estudo A e o Estudo B com uma anotação; abrir o Estudo B e confirmar que o backlink recebido de Estudo A é exibido claramente com navegação de retorno.

### Implementation for User Story 1

- [X] T009 [US1] Implementar composable reativo useStudyRelations para gerenciamento de relações de saída, backlinks e estado de carregamento em caderno-leitura-0.1/frontend/src/composables/useStudyRelations.ts
- [X] T010 [US1] Criar componente StudyRelationsList para exibição de relações ativas de saída e referências cruzadas recebidas com badges semânticos em caderno-leitura-0.1/frontend/src/components/relations/StudyRelationsList.vue
- [X] T011 [US1] Integrar componente StudyRelationsList na tela de leitura de estudos com links de navegação para os estudos conectados em caderno-leitura-0.1/frontend/src/views/StudyView.vue
- [X] T012 [P] [US1] Criar testes unitários para carregamento de relações, normalização de backlinks e navegação em caderno-leitura-0.1/frontend/tests/study-relations.test.mjs

**Checkpoint**: MVP funcional. O usuário pode relacionar estudos e navegar pela malha semântica bidirecional.

---

## Phase 4: User Story 2 - Visualização Gráfica com Setas Direcionadas no Canvas e Mapa (Priority: P2)

**Goal**: Projetar graficamente as relações semânticas como arestas vetoriais com curvas Bézier dinâmicas, pontas de seta direcionais e badges compactos sobre o Canvas 2D e o modo Mapa.

**Independent Test**: Abrir o Canvas de um livro com estudos conectados; verificar que curvas Bézier unem os cards com setas indicando a direção e badges com o tipo da relação, recalculando posições dinamicamente durante arrasto a 60fps.

### Implementation for User Story 2

- [X] T013 [US2] Implementar endpoint GET /api/books/{book_id}/relations no backend para consulta em lote de todas as arestas semânticas ativas do livro em caderno-leitura-0.1/backend/app/routers/study_relations.py
- [X] T014 [US2] Implementar composable useCanvasConnections para cálculo geométrico de pontos de ancoragem nas bordas dos cards, curvatura Bézier e posicionamento de badges em caderno-leitura-0.1/frontend/src/composables/useCanvasConnections.ts
- [X] T015 [US2] Criar componente CanvasConnectionsLayer com camada SVG sobreposta, marcadores de seta defs e rótulos semânticos em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasConnectionsLayer.vue
- [X] T016 [US2] Integrar CanvasConnectionsLayer dentro do palco 2D mantendo sincronização de coordenadas do mundo em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue e atualizar conexões no modo radial em caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue
- [X] T017 [P] [US2] Criar testes unitários para cálculo geométrico de ancoragem, traçado Bézier e atualização reativa em caderno-leitura-0.1/frontend/tests/canvas-relations.test.mjs

**Checkpoint**: Visualização gráfica espacial das relações operando com aceleração GPU a 60fps no Canvas 2D e Mapa.

---

## Phase 5: User Story 3 - Gestão, Anotação e Remoção Segura de Vínculos (Priority: P3)

**Goal**: Permitir a edição da nota textual explicativa, alteração de tipologia semântica e remoção segura de relações sem afetar o conteúdo dos estudos, com preservação latente sob lixeira.

**Independent Test**: Editar a nota explicativa de um vínculo, verificar a persistência, enviar um estudo participante para a lixeira (constatando a ocultação do vínculo) e restaurá-lo (constatando o reaparecimento intacto).

### Implementation for User Story 3

- [X] T018 [US3] Implementar endpoints PATCH /api/relations/{relation_id} e DELETE /api/relations/{relation_id} com tratamento atômico e respostas claras em caderno-leitura-0.1/backend/app/routers/study_relations.py
- [X] T019 [US3] Adicionar controles de edição rápida de descrição/tipo e botão de exclusão de vínculo no componente StudyRelationsList em caderno-leitura-0.1/frontend/src/components/relations/StudyRelationsList.vue
- [X] T020 [US3] Garantir que consultas de relações ocultem estudos em soft delete e implementar testes de preservação latente sob lixeira em caderno-leitura-0.1/backend/tests/test_study_relations_trash.py
- [X] T021 [P] [US3] Implementar testes de atualização e remoção segura de relações na suíte de testes em caderno-leitura-0.1/backend/tests/test_study_relations_api.py

**Checkpoint**: Gestão completa, anotações detalhadas e resiliência total contra perda de dados sob lixeira.

---

## Phase 6: User Story 4 - Ergonomia Móvel, Busca Rápida e Acessibilidade (Priority: P4)

**Goal**: Disponibilizar modal de criação de relações com busca rápida incremental em todo o acervo, alvos de toque mínimos de 44x44px e navegação acessível por teclado WAI-ARIA.

**Independent Test**: Emular tela de smartphone de 375px; acionar a criação de relação, buscar estudos por digitação incremental, selecionar com toque confortável e gerenciar com teclado via Tab e Enter.

### Implementation for User Story 4

- [X] T022 [US4] Implementar endpoint GET /api/studies/search-candidates com busca incremental transversal por título/capítulo e exclusão do estudo de origem em caderno-leitura-0.1/backend/app/routers/study_relations.py
- [X] T023 [US4] Criar componente CreateRelationModal com campo de busca incremental com debounce, seletor visual de tipo semântico, campo de anotação e alvos táteis mínimos de 44x44px em caderno-leitura-0.1/frontend/src/components/relations/CreateRelationModal.vue
- [X] T024 [US4] Integrar CreateRelationModal com suporte a WAI-ARIA, foco automático no input de busca e fechamento por tecla Escape em caderno-leitura-0.1/frontend/src/views/StudyView.vue
- [X] T025 [P] [US4] Criar testes automatizados de ergonomia tátil, filtragem de busca transversal e acessibilidade por teclado em caderno-leitura-0.1/frontend/tests/study-relations-a11y.test.mjs

**Checkpoint**: Interface 100% acessível, rápida e confortável tanto no desktop quanto em smartphones.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação rigorosa de regressão, compilação de produção e integridade da Constituição.

- [X] T026 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T027 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T028 Atualizar guia de validação executável e registrar evidências finais em specs/022-relacoes-estudos/quickstart.md

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
Phase 3: User Story 1 (T009-T012)  [MVP]  (Conexões semânticas e backlinks bidirecionais)
        │
        ▼
Phase 4: User Story 2 (T013-T017)         (Arestas vetoriais Bézier no Canvas e Mapa)
        │
        ▼
Phase 5: User Story 3 (T018-T021)         (Edição, anotação, remoção e ciclo com lixeira)
        │
        ▼
Phase 6: User Story 4 (T022-T025)         (Busca transversal, ergonomia móvel e acessibilidade)
        │
        ▼
Phase 7: Polish (T026-T028)               (Regressão completa, build Vite e validação)
```

### Parallel Opportunities

- **Phase 1**: T003 (schemas Pydantic) e T004 (types TypeScript) podem rodar em paralelo.
- **Phase 2**: T007 (cliente de API frontend) e T008 (testes de API backend) podem rodar em paralelo.
- **Phase 3**: T010 (StudyRelationsList) e T012 (testes unitários frontend) podem rodar em paralelo.
- **Phase 4**: T015 (CanvasConnectionsLayer) e T017 (testes geométricos) podem rodar em paralelo com T014.
- **Phase 5**: T020 (testes de lixeira) e T021 (testes de edição/remoção) podem rodar em paralelo.
- **Phase 6**: T023 (CreateRelationModal) e T025 (testes a11y) podem rodar em paralelo.
- **Phase 7**: T026 (regressão backend) e T027 (regressão frontend + build) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T004) e Foundational (T005-T008).
2. Concluir User Story 1 (T009-T012).
3. **Validar MVP**: Vinculação conceitual explícita entre estudos e navegação imediata por backlinks bidirecionais.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Tabela `study_relations`, validação de constraints e endpoints REST prontos.
2. US1 $\rightarrow$ Vínculos conceituais e backlinks no leitor de estudos (MVP).
3. US2 $\rightarrow$ Arestas dinâmicas em curvas Bézier com setas e badges no Canvas 2D e Mapa.
4. US3 $\rightarrow$ Gestão de notas, edição de tipo e proteção latente sob lixeira.
5. US4 $\rightarrow$ Busca transversal em todo o acervo com modal responsivo de 44x44px e WAI-ARIA.
6. Polish $\rightarrow$ Regressão integral e verificação de conformidade com a Constituição.
