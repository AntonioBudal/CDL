# Tasks: 010 — Dimensional: Superclasse Cinemática & Profunda (3D Parallax Espacial)

**Input**: Design documents from `specs/010-dimensional-parallax/`  
**Prerequisites**: [plan.md](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/plan.md), [spec.md](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/spec.md), [research.md](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/research.md), [data-model.md](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/data-model.md), [contracts/](file:///c:/Users/User/caderno/specs/010-dimensional-parallax/contracts/)  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação da folha de estilos modular da Superclasse Dimensional e integração com a folha global de estilos.

- [X] T001 [P] Create stylesheet `dimensional.css` skeleton in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T002 Import `dimensional.css` in `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Declaração dos tokens de perspectiva, limites de inclinação 3D e blindagem de leitura.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Declare root CSS variables (`--sc-border-radius`, `--sc-perspective`, `--sc-tilt-max-x`, `--sc-tilt-max-y`, `--sc-shadow-idle`, `--sc-transition-duration`, `--sc-transition-easing`) for `:is(:root[data-superclass="dimensional"], .superclass-dimensional)` in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T004 Define inviolable reading shielding (`.markdown-content`, `.study-section`, `.reader-tools` with `transform: none !important; animation: none !important;`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ativação da Superclasse Dimensional com Tilt 3D Microcontrolado e Sombras em Perspectiva (Priority: P1) 🎯 MVP

**Goal**: Implementar a física de perspectiva tridimensional (`perspective: 1000px`), inclinação angular controlada no hover do mouse (`rotateX: ±1.5°`, `rotateY: ±2.0°`) e sombras projetadas em perspectiva oposta ao cursor.

**Independent Test**: Ativar "dimensional" nas preferências, passar o cursor sobre `.book-card` no acervo e verificar inclinação suave dentro dos limites angulares com sombras direcionais e retorno inercial em ~320ms.

### Tests for User Story 1

- [X] T005 [P] [US1] Add unit tests for Dimensional CSS tokens, perspective, and tilt 3D angle limits in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 1

- [X] T006 [US1] Implement 3D perspective (`perspective: 1000px`, `transform-style: preserve-3d`) and bounded tilt formula (`rotateX: calc(var(--sc-magnetic-y) * -1.5deg * var(--sc-intensity))`, `rotateY: calc(var(--sc-magnetic-x) * 2.0deg * var(--sc-intensity))`) on `.book-card` in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T007 [US1] Implement dynamic projected shadows on hover moving opposite to tilt angle in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T008 [US1] Implement dimensional styling for global buttons (`button, .button, .btn`) with subtle Z elevation and directional shadow in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`

**Checkpoint**: At this point, User Story 1 is fully functional and delivers the core 3D tilt MVP experience.

---

## Phase 4: User Story 2 - Relevo Espacial Multicamada e Parallax Interno nas Capas e Cartões (Priority: P2)

**Goal**: Criar defasagem de profundidade espacial interna nos cartões, deslocando a miniatura da capa (1px), o título (2px) e os marcadores/badges (3px) sob o vetor do cursor.

**Independent Test**: Mover o cursor sobre um cartão de livro e verificar a movimentação coordenada em camadas relativas distintas, criando ilusão de relevo volumétrico de galeria.

### Tests for User Story 2

- [X] T009 [P] [US2] Add unit tests for multi-layer parallax offsets (cover, title, badges) in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 2

- [X] T010 [US2] Implement staggered internal parallax on `.book-card .book-card-cover-wrapper` (1px * intensity) in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T011 [US2] Implement staggered internal parallax on `.book-card h2` (2px * intensity) in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`
- [X] T012 [US2] Implement staggered internal parallax on `.book-card :is(.book-number, .card-action, .category-badge)` (3px * intensity) in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Transição de Rota Cinemática com Profundidade Espacial (Priority: P3)

**Goal**: Aplicar transição de rota fluida com aproximação suave de profundidade Z (`scale(0.985) → scale(1.0)` e `translateY(4px → 0)`) em ~300ms com curva cinemática.

**Independent Test**: Navegar entre a estante de livros e os detalhes de um livro ou capítulo e observar a aproximação suave de tela sem saltos ou oscilações na viewport.

### Tests for User Story 3

- [X] T013 [P] [US3] Add unit tests for Dimensional cinematic route transition rules and scale interpolations in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 3

- [X] T014 [US3] Implement cinematic route entry (`.page-enter-active`, `.page-enter-from` with `scale(0.985)` and `translateY(4px)`) and exit (`.page-leave-active`, `.page-leave-to` with `scale(1.01)`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`

**Checkpoint**: At this point, User Stories 1, 2, and 3 are functionally complete.

---

## Phase 6: User Story 4 - Multiplicador Paramétrico de Profundidade, Blindagem do Leitor e Acessibilidade (Priority: P4)

**Goal**: Garantir que toda rotação angular, paralaxe e transição cinemática responda ao multiplicador `--sc-intensity` e seja totalmente neutralizada sob redução de movimento.

**Independent Test**: Testar intensidades 0.5x, 1.0x, 1.5x e 0.0x; verificar que com `prefers-reduced-motion: reduce` e `data-motion="off"`, todos os efeitos 3D são anulados (`0deg`, sem rotação), mantendo `.markdown-content` 100% imóvel.

### Tests for User Story 4

- [X] T015 [P] [US4] Add unit tests for parametric intensity scaling (0.5x, 1.0x, 1.5x, 0.0x) and motion reduction neutralization in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 4

- [X] T016 [US4] Implement `--sc-intensity` multiplier scaling and complete neutralization under `prefers-reduced-motion: reduce` and `data-motion="off"` in `caderno-leitura-0.1/frontend/src/styles/superclasses/dimensional.css`

**Checkpoint**: All user stories are functionally complete and verified for universal accessibility.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada, conformidade arquitetural e atualização documental do repositório.

- [X] T017 [P] Update superclasses architecture documentation and changelog in `caderno-leitura-0.1/docs/contexto/ESTADO-E-DIAGNOSTICO.md`
- [X] T018 Run complete test suite `npm test` across all superclasses in `caderno-leitura-0.1/frontend`
- [X] T019 Run production build and type checking `npm run build` in `caderno-leitura-0.1/frontend`
- [X] T020 Run quickstart validation checklist per `specs/010-dimensional-parallax/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion (T001, T002) - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion (T003, T004).
  - User stories can proceed sequentially (US1 → US2 → US3 → US4).
- **Polish (Phase 7)**: Depends on all user stories (Phases 3, 4, 5, 6) being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2. Core 3D tilt delivered as MVP.
- **User Story 2 (P2)**: Depends on US1 (adiciona paralaxe nas camadas internas do cartão).
- **User Story 3 (P3)**: Depends on Phase 2 (regras de transição de rota).
- **User Story 4 (P4)**: Depends on US1/US2 tokens (aplica overrides de intensidade e acessibilidade).

### Parallel Opportunities

- **Setup**: T001 can run in parallel with planning.
- **Tests**: T005, T009, T013, T015 can be drafted in parallel within `superclasses.test.mjs`.
- **Polish**: T017 (documentação) can run in parallel with test suite verification.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`dimensional.css` e import em `style.css`).
2. Complete Phase 2: Foundational (Tokens raiz e blindagem de leitura).
3. Complete Phase 3: User Story 1 (Perspectiva 3D, tilt angular delimitado e sombras projetadas).
4. **STOP and VALIDATE**: Verificar no navegador o tilt 3D e rodar testes unitários.

### Incremental Delivery

1. Setup + Foundation → Foundation ready.
2. User Story 1 → Testar independentemente → MVP de Tilt 3D ativo!
3. User Story 2 → Testar independentemente → Relevo em paralaxe multicamada ativo.
4. User Story 3 → Testar independentemente → Transição de rota cinemática ativa.
5. User Story 4 → Testar independentemente → Intensidade paramétrica e conformidade de movimento reduzido.
6. Polish → Suite completa `npm test` e build `npm run build` validados.
