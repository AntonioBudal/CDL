# Tasks: F03 — Canvas de Estudos

**Feature Branch**: `021-canvas-estudos`  
**Date**: 2026-09-19  
**Status**: Ready for Implementation  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura relacional do SQLite, migração Alembic, modelos e contratos de tipos compartilhados entre backend e frontend.

- [X] T001 Criar migração Alembic para tabela study_canvas_nodes com chaves estrangeiras CASCADE, restrição única (study_id, book_id) e índices em caderno-leitura-0.1/backend/migrations/versions/0007_add_study_canvas_nodes.py
- [X] T002 Criar modelo declarativo SQLAlchemy StudyCanvasNode em caderno-leitura-0.1/backend/app/models/study_canvas_node.py e registrá-lo em caderno-leitura-0.1/backend/app/models/__init__.py
- [X] T003 [P] Criar schemas Pydantic CanvasNodeItem, CanvasNodeRead, CanvasBatchUpdateRequest e BookCanvasResponse em caderno-leitura-0.1/backend/app/schemas/study_canvas_node.py
- [X] T004 [P] Atualizar definições de tipos TypeScript com StudyCanvasNode, CanvasViewportState, CanvasPositionedCard e CanvasBoundingBox em caderno-leitura-0.1/frontend/src/types.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Serviços centrais de persistência, rotas REST autoritativas e cliente HTTP que bloqueiam a interface do Canvas.

- [X] T005 Implementar serviço canvas_service.py com listagem de nós por obra, batch upsert atômico de coordenadas e garantia de isolamento da hierarquia canônica em caderno-leitura-0.1/backend/app/services/canvas_service.py
- [X] T006 Implementar router FastAPI canvas.py com endpoints GET /api/books/{book_id}/canvas, PUT /api/books/{book_id}/canvas e PATCH /api/studies/{study_id}/canvas, registrando-o em caderno-leitura-0.1/backend/app/routers/canvas.py e caderno-leitura-0.1/backend/app/main.py
- [X] T007 [P] Criar testes automatizados de backend para integridade relacional, batch update atômico, isolamento e validação de números finitos em caderno-leitura-0.1/backend/tests/test_canvas_api.py
- [X] T008 [P] Atualizar cliente HTTP de API do frontend com métodos getCanvasNodes, saveCanvasBatch e patchCanvasNode em caderno-leitura-0.1/frontend/src/api.ts

**Checkpoint**: Camada de persistência e endpoints REST prontos — implementação das histórias de usuário pode prosseguir.

---

## Phase 3: User Story 1 - Navegação Espacial Infinita com Pan e Zoom Fluido (Priority: P1) 🎯 MVP

**Goal**: Permitir navegar pelo espaço bidimensional livre (Canvas 2D) com translação contínua (pan), aproximação focal ancorada no cursor (zoom 0.25x a 2.0x), aceleração por GPU e persistência do viewport no navegador.

**Independent Test**: Acessar o modo Canvas de uma obra, arrastar o fundo para deslocamento livre, utilizar a roda do mouse para zoom focal contínuo, recarregar a página e confirmar a restauração exata da janela de visão.

### Implementation for User Story 1

- [X] T009 [US1] Criar composable useCanvasViewport com matemática afim de tela vs mundo, pan contínuo, zoom focal centrado no cursor (0.25x a 2.0x) e persistência em localStorage em caderno-leitura-0.1/frontend/src/composables/useCanvasViewport.ts
- [X] T010 [P] [US1] Criar componente CanvasToolbar com botões táteis de zoom in, zoom out, indicador percentual e reset 100% em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasToolbar.vue
- [X] T011 [US1] Refatorar StudyCanvasView para integrar useCanvasViewport, palco transformável com translate3d e scale, grade responsiva e listeners de arrasto/scroll em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T012 [P] [US1] Criar testes unitários para matemática de conversão de coordenadas mundo/tela, limites de escala e persistência de viewport em caderno-leitura-0.1/frontend/tests/canvas-viewport.test.mjs

**Checkpoint**: Viewport bidimensional infinito com pan, zoom fluido e persistência funcional de forma independente (MVP).

---

## Phase 4: User Story 2 - Posicionamento Livre, Seleção e Persistência de Coordenadas (Priority: P2)

**Goal**: Permitir arrastar cards livremente para qualquer coordenada (x, y), selecionar nós individualmente ou via caixa retangular (marquee), mover blocos preservando distâncias relativas, elevar z-index e sincronizar com o backend via debounce sem quebrar a árvore de estudos.

**Independent Test**: Mover cards para posições arbitrárias; selecionar múltiplos cards com caixa de seleção retangular; arrastar o conjunto; confirmar persistência no banco e verificar que parentesco e capítulos permanecem inalterados.

### Implementation for User Story 2

- [X] T013 [US2] Implementar composable useCanvasNodes com algoritmo determinístico de auto-grid por capítulo para novos estudos, cálculo de arrasto com delta, elevação de z-index e batch sync com debounce de 300ms em caderno-leitura-0.1/frontend/src/composables/useCanvasNodes.ts
- [X] T014 [P] [US2] Criar componente atômico CanvasNode para renderização de cards no espaço do mundo, com manipulador de arrasto, tags temáticas, metadados e destaque de seleção em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasNode.vue
- [X] T015 [US2] Implementar composable useCanvasSelection com seleção simples e seleção retangular em bloco (marquee selection) no fundo livre em caderno-leitura-0.1/frontend/src/composables/useCanvasSelection.ts
- [X] T016 [US2] Integrar CanvasNode, useCanvasNodes e useCanvasSelection no StudyCanvasView, conectando com a API REST em lote em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T017 [P] [US2] Criar testes unitários para o algoritmo de auto-grid, seleção simples, marquee selection e arrasto em bloco em caderno-leitura-0.1/frontend/tests/canvas-nodes.test.mjs

**Checkpoint**: Organização espacial livre de cards, seleção múltipla e sincronização atômica ativas e estáveis.

---

## Phase 5: User Story 3 - Orientação Espacial, Radar (Mini-mapa) e Controles de Viewport (Priority: P3)

**Goal**: Exibir mini-mapa interativo de radar com projeção escalar dos nós e janela indicadora do viewport visível, permitindo teletransporte imediato por clique e comando "Ajustar à Tela" (Fit to View) via cálculo de Bounding Box.

**Independent Test**: Afastar-se dos cards, localizar a silhueta no mini-mapa, clicar no mini-mapa para recentralizar e acionar "Ajustar à Tela" para enquadrar todo o acervo perfeitamente na visualização.

### Implementation for User Story 3

- [X] T018 [US3] Criar componente CanvasMinimap com projeção escalar dos nós, janela indicadora do viewport visível e navegação por clique e arrasto no radar em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasMinimap.vue
- [X] T019 [US3] Implementar função Fit to View com cálculo de Bounding Box de todos os cards com margem de segurança de 60px no useCanvasViewport e botão de disparo na CanvasToolbar em caderno-leitura-0.1/frontend/src/composables/useCanvasViewport.ts
- [X] T020 [US3] Integrar CanvasMinimap flutuante no canto inferior de StudyCanvasView com transição suave e botão de colapso em caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue
- [X] T021 [P] [US3] Criar testes unitários para cálculo de Bounding Box, projeção proporcional no radar e teletransporte de viewport em caderno-leitura-0.1/frontend/tests/canvas-minimap.test.mjs

**Checkpoint**: Orientação topológica total com mini-mapa radar e enquadramento automático funcional.

---

## Phase 6: User Story 4 - Ergonomia Tátil Móvel e Acessibilidade Espacial (Priority: P4)

**Goal**: Garantir suporte completo a telas de toque (toque direto em cards, pan de fundo livre com 1 dedo, pinça com 2 dedos para zoom), botões táteis flutuantes mínimos de 44x44px e navegação acessível por teclado via Tab e Shift+Setas.

**Independent Test**: Emular dispositivo móvel com toque, realizar gestos de pinça para zoom e arrasto de tela; verificar botões táteis com dimensão mínima de 44x44px; navegar e reposicionar cards usando apenas o teclado.

### Implementation for User Story 4

- [X] T022 [US4] Implementar detecção de gestos multitoque com Pointer Events (pinch-to-zoom com 2 dedos e pan com toque no fundo) sem colisão com a rolagem do navegador em caderno-leitura-0.1/frontend/src/composables/useCanvasViewport.ts
- [X] T023 [US4] Assegurar alvos de toque mínimos de 44x44px nos botões da CanvasToolbar, no card CanvasNode e no contêiner tátil flutuante em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasToolbar.vue
- [X] T024 [US4] Implementar suporte a teclado com navegação Tab entre cards e reposicionamento espacial por Shift + Setas direcionais em caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasNode.vue
- [X] T025 [P] [US4] Criar testes automatizados de ergonomia tátil e atalhos de teclado acessíveis em caderno-leitura-0.1/frontend/tests/canvas-a11y.test.mjs

**Checkpoint**: Canvas de estudos 100% acessível, inclusivo e ergonômico em dispositivos móveis e desktops.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação rigorosa de regressão, compilação de produção e auditoria contra a Constituição.

- [X] T026 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T027 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T028 Atualizar guia de validação executável e registrar evidências finais em specs/021-canvas-estudos/quickstart.md

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
Phase 3: User Story 1 (T009-T012)  [MVP]  (Base do viewport 2D e navegação)
        │
        ▼
Phase 4: User Story 2 (T013-T017)         (Cards, auto-grid, seleção e persistência)
        │
        ▼
Phase 5: User Story 3 (T018-T021)         (Radar / mini-mapa e Fit to View)
        │
        ▼
Phase 6: User Story 4 (T022-T025)         (Ergonomia tátil móvel e teclado)
        │
        ▼
Phase 7: Polish (T026-T028)               (Validação final, testes e build)
```

### Parallel Opportunities

- **Phase 1**: T003 (schemas Pydantic) e T004 (types TypeScript) podem rodar em paralelo.
- **Phase 2**: T007 (testes de backend) e T008 (cliente de API frontend) podem rodar em paralelo.
- **Phase 3**: T010 (CanvasToolbar) e T012 (testes do viewport) podem rodar em paralelo.
- **Phase 4**: T014 (CanvasNode) e T017 (testes de auto-grid e seleção) podem rodar em paralelo.
- **Phase 5**: T021 (testes do mini-mapa) pode rodar em paralelo com T019/T020.
- **Phase 6**: T025 (testes a11y) pode rodar em paralelo com T023/T024.
- **Phase 7**: T026 (regressão backend) e T027 (regressão frontend + build) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T004) e Foundational (T005-T008).
2. Concluir User Story 1 (T009-T012).
3. **Validar MVP**: Navegação espacial fluida no Canvas a 60fps com pan, zoom e persistência de viewport.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Banco e endpoints prontos.
2. US1 $\rightarrow$ Viewport 2D infinito e navegação fluida (MVP).
3. US2 $\rightarrow$ Posicionamento livre de cards, auto-grid e persistência atômica.
4. US3 $\rightarrow$ Consciência espacial com mini-mapa radar e Ajustar à Tela.
5. US4 $\rightarrow$ Ergonomia multitoque em smartphones e acessibilidade WAI-ARIA.
6. Polish $\rightarrow$ Regressão integral e verificação de integridade da Constituição.
