# Tasks: 011 — Monolítica: Superclasse Pesada & Solene (Brutalista & Arquitetura em Pedra)

**Input**: Design documents from `specs/011-monolitica-solene/`  
**Prerequisites**: [plan.md](file:///c:/Users/User/caderno/specs/011-monolitica-solene/plan.md), [spec.md](file:///c:/Users/User/caderno/specs/011-monolitica-solene/spec.md), [research.md](file:///c:/Users/User/caderno/specs/011-monolitica-solene/research.md), [data-model.md](file:///c:/Users/User/caderno/specs/011-monolitica-solene/data-model.md), [contracts/](file:///c:/Users/User/caderno/specs/011-monolitica-solene/contracts/)  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação da folha de estilos modular da Superclasse Monolítica e integração com a folha global de estilos.

- [X] T001 [P] Create stylesheet `monolitica.css` skeleton in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T002 Import `monolitica.css` in `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Declaração dos tokens de geometria brutalista, supressão de sombras e blindagem de leitura.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Declare root CSS variables (`--sc-border-radius`, `--sc-border-width`, `--sc-shadow-idle`, `--sc-shadow-hover`, `--sc-shadow-active`, `--sc-transition-duration`, `--sc-transition-easing`) for `:is(:root[data-superclass="monolitica"], .superclass-monolitica)` in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T004 Define inviolable reading shielding (`.markdown-content`, `.study-section`, `.reader-tools`, `.reading-page` with `transform: none !important; animation: none !important;`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ativação da Superclasse Monolítica com Cantos Estritamente Retos e Ausência de Sombras Flutuantes (Priority: P1) 🎯 MVP

**Goal**: Implementar a assinatura brutalista de cantos retos (`0px !important`), ausência total de sombras difusas (`box-shadow: none !important`) e contornos estruturais densos nos cartões do acervo (`.book-card`), painéis e recipientes.

**Independent Test**: Ativar "monolitica" nas preferências de aparência e verificar que todos os cartões, painéis e botões possuem `border-radius: 0px`, sem sombras flutuantes e com contornos sólidos.

### Tests for User Story 1

- [X] T005 [P] [US1] Add unit tests for Monolítica CSS tokens, border radius (0px), border width, and complete shadow suppression in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 1

- [X] T006 [US1] Implement strict zero border-radius (`border-radius: var(--sc-border-radius)`) and shadow suppression on `.book-card` in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T007 [US1] Implement solid structural borders (`border: var(--sc-border-width) solid var(--color-border-strong)`) on `.book-card` and `.book-list-item` in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T008 [US1] Implement brutalist rectangular styling for global panels (`.panel`, `.appearance-group`) and controls (`input`, `textarea`, `select`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`

**Checkpoint**: At this point, User Story 1 is fully functional and delivers the core brutalist MVP experience.

---

## Phase 4: User Story 2 - Microinterações Solenes e Inversão de Alto Contraste no Hover e Active (Priority: P2)

**Goal**: Implementar microinterações deliberadas, ponderadas e solenes no hover (~380ms) e resposta de inversão de alto contraste no clique (`:active`), sem saltos físicos verticais ou inclinações 3D.

**Independent Test**: Passar o cursor sobre cartões e botões e verificar preenchimento lento ponderado em ~380ms; clicar e verificar inversão brutalista imediata de alto contraste sem deslocamento vertical.

### Tests for User Story 2

- [X] T009 [P] [US2] Add unit tests for Monolítica solemn hover transition timings (380ms) and active high-contrast inversion in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 2

- [X] T010 [US2] Implement solemn hover contrast transitions on `.book-card` (background-color and border-color transition in 380ms) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T011 [US2] Implement brutalist rectangular styling and solemn hover on global buttons (`button`, `.button`, `.btn`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`
- [X] T012 [US2] Implement active high-contrast inversion on global buttons (`:active:not(:disabled)` with `background-color: var(--color-text); color: var(--color-page)`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Transição de Rota Solene e Ponderada (Dissolução Lapidar) (Priority: P3)

**Goal**: Aplicar transição de tela contemplativa e solene com dissolução em opacidade ponderada (~380ms) sem translações em eixos físicos ou distorções de escala.

**Independent Test**: Navegar entre estante e detalhes de um livro e verificar entrada em fade ponderado (~380ms) com estabilidade visual absoluta do viewport.

### Tests for User Story 3

- [X] T013 [P] [US3] Add unit tests for Monolítica solemn route dissolution rules and absence of physical translations in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 3

- [X] T014 [US3] Implement solemn route entry (`.page-enter-active` with `opacity 380ms cubic-bezier(0.25, 1, 0.5, 1)` and `transform: none !important`) and exit (`.page-leave-active` with `opacity 220ms ease`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`

**Checkpoint**: At this point, User Stories 1, 2, and 3 are functionally complete.

---

## Phase 6: User Story 4 - Multiplicador Paramétrico, Blindagem do Leitor e Acessibilidade Universal (Priority: P4)

**Goal**: Garantir que as espessuras de borda e contrastes respeitem `--sc-intensity`, e que sob redução de movimento todas as transições tornem-se imediatas (`0ms`).

**Independent Test**: Testar intensidades 0.5x, 1.0x, 1.5x e 0.0x; verificar que com `prefers-reduced-motion: reduce` e `data-motion="off"`, todas as transições são neutralizadas (`transition: none !important`), mantendo `.markdown-content` 100% imóvel.

### Tests for User Story 4

- [X] T015 [P] [US4] Add unit tests for parametric intensity scaling (0.5x, 1.0x, 1.5x, 0.0x) and immediate transition neutralization under reduced motion in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 4

- [X] T016 [US4] Implement `--sc-intensity` multiplier overrides and immediate transition neutralization under `prefers-reduced-motion: reduce` and `data-motion="off"` in `caderno-leitura-0.1/frontend/src/styles/superclasses/monolitica.css`

**Checkpoint**: All user stories are functionally complete and verified for universal accessibility.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada, conformidade arquitetural e atualização documental do repositório.

- [X] T017 [P] Update superclasses architecture documentation and changelog in `caderno-leitura-0.1/docs/contexto/ESTADO-E-DIAGNOSTICO.md`
- [X] T018 Run complete test suite `npm test` across all superclasses in `caderno-leitura-0.1/frontend`
- [X] T019 Run production build and type checking `npm run build` in `caderno-leitura-0.1/frontend`
- [X] T020 Run quickstart validation checklist per `specs/011-monolitica-solene/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion (T001, T002) - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion (T003, T004).
  - User stories can proceed sequentially (US1 → US2 → US3 → US4).
- **Polish (Phase 7)**: Depends on all user stories (Phases 3, 4, 5, 6) being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2. Core brutalist geometry delivered as MVP.
- **User Story 2 (P2)**: Depends on US1 (adiciona microinterações e inversão sobre a estrutura base).
- **User Story 3 (P3)**: Depends on Phase 2 (regras de transição de rota).
- **User Story 4 (P4)**: Depends on US1/US2 tokens (aplica overrides de intensidade e acessibilidade).

### Parallel Opportunities

- **Setup**: T001 can run in parallel with planning.
- **Tests**: T005, T009, T013, T015 can be drafted in parallel within `superclasses.test.mjs`.
- **Polish**: T017 (documentação) can run in parallel with test suite verification.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`monolitica.css` e import em `style.css`).
2. Complete Phase 2: Foundational (Tokens raiz e blindagem de leitura).
3. Complete Phase 3: User Story 1 (Cantos retos de 0px, supressão de sombras e bordas estruturais).
4. **STOP and VALIDATE**: Verificar no navegador a geometria brutalista e rodar testes unitários.

### Incremental Delivery

1. Setup + Foundation → Foundation ready.
2. User Story 1 → Testar independentemente → MVP brutalista ativo!
3. User Story 2 → Testar independentemente → Microinterações ponderadas e inversão de contraste ativas.
4. User Story 3 → Testar independentemente → Transição de rota solene ativa.
5. User Story 4 → Testar independentemente → Intensidade paramétrica e conformidade de movimento reduzido.
6. Polish → Suite completa `npm test` e build `npm run build` validados.
