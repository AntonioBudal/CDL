# Tasks: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial

**Feature**: F 0.7.8 — Redesenho do Canvas  
**Branch**: `057-redesenho-canvas`  
**Date**: 2026-10-04  
**Spec**: [specs/057-redesenho-canvas/spec.md](spec.md) | **Plan**: [specs/057-redesenho-canvas/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estruturas de tipos e modelos de estado para o Canvas 2D, molduras, conexões e guias magnéticas.

- [x] T001 [P] Estender e definir tipos TypeScript para nós, molduras, guias magnéticas e ferramentas do Canvas em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Algoritmo puro de alinhamento magnético inteligente (Smart Guides) e testes unitários fundamentais.

- [x] T002 [P] Implementar composable `useSmartSnapping.ts` com a função pura `computeSmartSnapping` para cálculo de guias magnéticas de centro e bordas em `caderno-leitura-0.1/frontend/src/composables/useSmartSnapping.ts`
- [x] T003 [P] Criar testes unitários para o algoritmo de alinhamento magnético e cálculo de guias em `caderno-leitura-0.1/frontend/tests/canvas-snapping.test.mjs`

**Checkpoint**: Base matemática pronta — qualquer arrasto de retângulos calcula pontos de atração magnética suave em $\pm 10$px com coordenadas de linhas visuais.

---

## Phase 3: User Story 1 - Mesa de Trabalho Espacial Livre e Criação Rápida In-Place (Priority: P1) 🎯 MVP

**Goal**: Permitir duplo clique em qualquer coordenada livre da mesa espacial para abrir mini-card inline in-place registrando novo estudo imediatamente com `Enter`, e manipular cartões com persistência cartesiana fluida.

**Independent Test**: Abrir o Canvas de um capítulo; dar duplo clique em área livre; preencher título e seção inicial no mini-card; salvar com `Enter`; verificar que o novo cartão de estudo aparece exatamente nas coordenadas do clique e persiste após recarregamento.

#### Tests for User Story 1 🧪

- [x] T004 [P] [US1] Criar testes unitários para a captura de duplo clique, conversão inversa de coordenadas `(clientX, clientY) -> (worldX, worldY)` e renderização do mini-card de criação in-place em `caderno-leitura-0.1/frontend/tests/study_canvas_view.test.mjs`

### Implementation for User Story 1

- [x] T005 [US1] Integrar mini-card inline in-place de criação rápida com duplo clique em área livre do Canvas (`@dblclick`) e botão de adição rápida na toolbar em `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`
- [x] T006 [US1] Refinar manipulação e persistência de nós em `useCanvasNodes.ts` com suporte a coordenadas livres e debounce de 500ms em `caderno-leitura-0.1/frontend/src/composables/useCanvasNodes.ts`

**Checkpoint**: User Story 1 concluída — o Canvas opera como uma mesa de trabalho espacial ativa onde o leitor cria e move estudos livremente (MVP).

---

## Phase 4: User Story 2 - Molduras Espaciais (Frames) e Agrupamento Temático Solidário (Priority: P2)

**Goal**: Desenhar e redimensionar molduras retangulares coloridas no Canvas, com títulos editáveis, paletas temáticas e movimento solidário automático de todos os cartões geometricamente contidos no seu interior.

**Independent Test**: Selecionar a ferramenta de moldura; desenhar retângulo envolvendo múltiplos cartões; editar título e cor; arrastar a moldura e verificar que todos os cartões internos movem-se solidariamente mantendo suas posições relativas.

### Tests for User Story 2 🧪

- [x] T007 [P] [US2] Criar testes unitários para a detecção geométrica de nós contidos na moldura e movimento solidário conjunto em `caderno-leitura-0.1/frontend/tests/canvas-frames.test.mjs`

### Implementation for User Story 2

- [x] T008 [US2] Estender `useCanvasFrames.ts` com o método `getContainedNodes` e suporte à translação solidária de nós agrupados em `caderno-leitura-0.1/frontend/src/composables/useCanvasFrames.ts`
- [x] T009 [US2] Atualizar `CanvasFrameNode.vue` com título inline editável, seletor de paletas de cor temática e alças de redimensionamento bidirecional em `caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasFrameNode.vue`
- [x] T010 [US2] Integrar arrasto solidário de moldura e ferramenta de desenho de moldura (`activeTool === 'frame'`) em `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`

**Checkpoint**: User Stories 1 e 2 integradas — o leitor consegue organizar grandes conjuntos de estudos em áreas temáticas delimitadas e movê-las em bloco.

---

## Phase 5: User Story 3 - Conexões Direcionadas, Snapping Inteligente e Navegação Precisa (Priority: P3)

**Goal**: Traçar conexões direcionadas com setas e badges semânticos entre cartões, alinhar elementos com guias magnéticas inteligentes (Smart Guides), alternar ferramentas na toolbar (`select`, `pan`, `frame`, `connect`), navegar via mini-mapa reativo e operar com ergonomia mobile de 44px.

**Independent Test**: Puxar aresta conectora entre dois cartões e associar relação semântica; arrastar cartão e verificar guias magnéticas pontilhadas na cor de acento; usar o mini-mapa para navegar o viewport; testar alvos táteis de 44px no mobile.

### Tests for User Story 3 🧪

- [x] T011 [P] [US3] Criar testes unitários para a projeção de guias magnéticas (Smart Guides), alternância de ferramentas e ergonomia mobile em `caderno-leitura-0.1/frontend/tests/study_canvas_view.test.mjs`

### Implementation for User Story 3

- [x] T012 [US3] Integrar projeção visual de guias magnéticas temporárias (`SmartGuide`) na renderização SVG do Canvas durante o arrasto de cartões em `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`
- [x] T013 [US3] Integrar alças de conexão nos cartões (`CanvasNode.vue`) com abertura do popover de relações semânticas e persistência via `createStudyRelation` em `caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasNode.vue` e `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`
- [x] T014 [US3] Atualizar `CanvasToolbar.vue` com alternância clara de ferramentas (`select`, `pan`, `frame`, `connect`), atalhos de teclado (barra de espaço para pan) e controles táteis de 44×44px no mobile em `caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasToolbar.vue`

**Checkpoint**: Todas as 3 User Stories concluídas, polidas e integradas com máxima fluidez no Desktop e Mobile.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, testes de regressão de ponta a ponta e build de produção.

- [x] T015 [P] Validar os 5 cenários de teste fim a fim de `specs/057-redesenho-canvas/quickstart.md`
- [x] T016 Executar e validar suite de testes completa com `npm test` e `pytest`
- [x] T017 Validar tipagem e build de produção com `npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as User Stories.
- **User Story 1 (Phase 3)**: Depende da Phase 2 (Foundational) — MVP.
- **User Story 2 (Phase 4)**: Depende da Phase 2 e integra com os cartões da US1.
- **User Story 3 (Phase 5)**: Depende da Phase 2 e integra com cartões e molduras da US1/US2.
- **Polish (Phase 6)**: Depende da conclusão de todas as User Stories.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir Setup (T001) e Foundational (T002, T003).
2. Concluir User Story 1 (T004, T005, T006).
3. Validar de forma independente: criação in-place via duplo clique e posicionamento cartesiano livre de cartões.

### Incremental Delivery

1. Setup + Foundational (algoritmo puro de snapping em `useSmartSnapping.ts`).
2. Adicionar US1 (MVP da mesa espacial com duplo clique e criação in-place).
3. Adicionar US2 (desenho de molduras e movimento solidário de cartões agrupados).
4. Adicionar US3 (guias magnéticas inteligentes, conectores semânticos, minimapa e toolbar mobile de 44px).
5. Polish e build de produção.
