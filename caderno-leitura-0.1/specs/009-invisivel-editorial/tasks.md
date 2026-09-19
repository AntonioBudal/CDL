# Tasks: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes

**Input**: Design documents from `specs/009-invisivel-editorial/`  
**Prerequisites**: [plan.md](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/plan.md), [spec.md](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/spec.md), [research.md](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/research.md), [data-model.md](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/data-model.md), [contracts/](file:///c:/Users/User/caderno/specs/009-invisivel-editorial/contracts/)  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação da folha de estilos modular da Superclasse Invisível e integração com o sistema global de estilos.

- [X] T001 [P] Create stylesheet `invisivel.css` skeleton in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T002 Import `invisivel.css` in `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Declaração dos tokens físicos centrais e blindagem inviolável do leitor antes da implementação das histórias de usuário.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Declare root CSS variables (`--sc-border-radius`, `--sc-shadow-idle`, `--sc-shadow-hover`, `--sc-shadow-active`, `--sc-reading-shift-x`, `--sc-transition-duration`, `--sc-transition-easing`) for `:is(:root[data-superclass="invisivel"], .superclass-invisivel)` in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T004 Define inviolable reading shielding (`.markdown-content`, `.study-section`, `.reader-tools` with `transform: none !important; animation: none !important;`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ativação da Superclasse Invisível com Desmaterialização de Caixas e Microinterações Editoriais (Priority: P1) 🎯 MVP

**Goal**: Implementar a desmaterialização de caixas rígidas e sombras em cartões e blocos estruturais, aplicando microinterações editoriais (deslocamento lateral no hover e sublinhado progressivo da esquerda para a direita) e botões editoriais limpos.

**Independent Test**: Ativar "invisivel" nas preferências, inspecionar `.book-card` e `.book-list-item` para confirmar ausência de bordas duras/sombras de elevação, verificar `translateX(4px)` e sublinhado progressivo com `scaleX(1)` no hover, e botões tipográficos elegantes.

### Tests for User Story 1

- [X] T005 [P] [US1] Add unit tests for Invisível CSS token declaration and box desubstantialization in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`
- [X] T006 [P] [US1] Add unit tests for reading lateral shift and progressive underline microinteractions in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 1

- [X] T007 [US1] Implement box desubstantialization rules for `.book-card`, `.book-list-item`, `.panel`, and `.appearance-group` (transparent backgrounds, borderless, subtle bottom border) in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T008 [US1] Implement horizontal reading shift microinteractions (`translateX(var(--sc-reading-shift-x))`) on book cards and list items in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T009 [US1] Implement progressive underline pseudo-element (`::after` with `transform: scaleX(0) -> scaleX(1)`, `transform-origin: left`) for `.text-link`, `.book-card h2 a`, and `.chapter-list a` in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T010 [US1] Implement editorial button styling (`border-radius: 0`, `box-shadow: none !important`, subtle 1px border and 2px hover shift) for `button, .button, .btn` in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`

**Checkpoint**: At this point, User Story 1 is fully functional and delivers the core editorial MVP experience.

---

## Phase 4: User Story 2 - Transição de Página em Cascata Temporal (*Staggered Fade-Up*) (Priority: P2)

**Goal**: Criar transição de rota fluida em cascata temporal (*staggered fade-up*) defasada em 40ms entre cabeçalhos, metadados e corpo do conteúdo sob a Superclasse Invisível.

**Independent Test**: Navegar entre rotas sob a Superclasse Invisível e observar a entrada sequencial suave dos elementos (`.page-header` a 0ms, `.reader-heading/.breadcrumb` a 40ms, `.reader-analysis/.book-grid` a 80ms) e a saída sem solavancos.

### Tests for User Story 2

- [X] T011 [P] [US2] Add unit tests for Invisível route transition keyframes and staggered cascading rules in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 2

- [X] T012 [US2] Implement `@keyframes sc-invisivel-fade-up` and staggered entry timing (`.page-header` 0ms, `.reader-heading/.breadcrumb/.intro` 40ms, `.reader-analysis/.book-grid/.chapter-layout` 80ms) in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`
- [X] T013 [US2] Implement smooth route exit rules (`.page-leave-active` with fade-out) in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`

**Checkpoint**: At this point, User Stories 1 AND 2 are fully functional and integrated.

---

## Phase 5: User Story 3 - Simplificação do Painel de Ajustes via Remoção dos Controles Obsoletos (Priority: P3)

**Goal**: Podar do frontend os controles obsoletos de formato de caixas (`style`), contraste de cartões (`surface`) e preenchimento de botões (`button-style`), garantindo normalização tolerante para migração de `localStorage` e integridade de tipos.

**Independent Test**: Abrir o painel de Ajustes e constatar ausência de `style`, `surface` e `button-style`, verificar persistência sem erros no `localStorage` com dados legados, e compilar TypeScript com sucesso.

### Tests for User Story 3

- [X] T014 [P] [US3] Add unit tests verifying `style`, `surface`, and `button-style` are absent from `cadernoAppearance.fields` and legacy keys are safely ignored in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 3

- [X] T015 [US3] Prune `style`, `surface`, and `button-style` fields, update group titles and bump version in `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js`
- [X] T016 [US3] Update `normalize()` in `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js` to ensure backward-tolerant migration from `localStorage` without resetting active preferences
- [X] T017 [US3] Update TypeScript definition `AppearancePreferences` to remove pruned properties in `caderno-leitura-0.1/frontend/src/appearance.d.ts`
- [X] T018 [US3] Remove `surface` from `ignored()` list and verify fieldset rendering in `caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue`

**Checkpoint**: At this point, User Stories 1, 2, and 3 are complete, the settings panel is pruned, and legacy preferences remain intact.

---

## Phase 6: User Story 4 - Intensidade Paramétrica, Blindagem de Leitura e Acessibilidade Universal (Priority: P4)

**Goal**: Garantir que todas as microinterações e transições da Superclasse Invisível respondam proporcionalmente a `--sc-intensity` e sejam totalmente neutralizadas sob redução de movimento.

**Independent Test**: Testar intensidades 0.5x, 1.0x, 1.5x e 0.0x, além de simular `prefers-reduced-motion: reduce` e `data-motion="off"`, garantindo supressão de movimento e texto de leitura 100% imóvel.

### Tests for User Story 4

- [X] T019 [P] [US4] Add unit tests for parametric intensity scaling, motion reduction neutralization, and reader stillness in `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 4

- [X] T020 [US4] Implement `--sc-intensity` multiplier rules and motion reduction override (`prefers-reduced-motion: reduce` and `data-motion="off"` forcing `--sc-intensity: 0.0 !important; animation: none !important;`) in `caderno-leitura-0.1/frontend/src/styles/superclasses/invisivel.css`

**Checkpoint**: All user stories are functionally complete and verified for universal accessibility.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada, conformidade arquitetural e atualização documental do repositório.

- [X] T021 [P] Update superclasses architecture documentation and changelog in `caderno-leitura-0.1/docs/contexto/ESTADO-E-DIAGNOSTICO.md`
- [X] T022 Run complete test suite `npm test` across all superclasses in `caderno-leitura-0.1/frontend`
- [X] T023 Run production build and type checking `npm run build` in `caderno-leitura-0.1/frontend`
- [X] T024 Run quickstart validation checklist per `specs/009-invisivel-editorial/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion (T001, T002) - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion (T003, T004).
  - User stories can proceed in parallel if independent files are targeted, or sequentially (US1 → US2 → US3 → US4).
- **Polish (Phase 7)**: Depends on all user stories (Phases 3, 4, 5, 6) being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2. Can be implemented and delivered as MVP immediately.
- **User Story 2 (P2)**: Depends on Phase 2. Adds route transition keyframes in `invisivel.css`.
- **User Story 3 (P3)**: Depends on Phase 2. Touches `appearance-bootstrap.js`, `appearance.d.ts`, `AppearanceControls.vue`.
- **User Story 4 (P4)**: Depends on US1/US2 tokens in `invisivel.css`. Configures intensity overrides and accessibility fallbacks.

### Within Each User Story

- Tests written and verified to fail or establish contract expectations before or alongside implementation.
- CSS token foundations before selector rules.
- Core styles before animations.
- Story complete before final integration polish.

### Parallel Opportunities

- **Setup**: T001 can run in parallel with planning/review.
- **Tests**: T005, T006, T011, T014, T019 are test specifications and can be prepared in parallel.
- **Cross-file work**: US3 (JavaScript/TypeScript/Vue files) can proceed in parallel with US1/US2 (CSS file).
- **Polish**: T021 (docs) can run in parallel with test suite runs.

---

## Parallel Example: User Story 1 & User Story 3

```bash
# CSS track (US1):
Task: "T005 [P] [US1] Add unit tests for Invisível CSS token declaration in frontend/tests/superclasses.test.mjs"
Task: "T007 [US1] Implement box desubstantialization rules in frontend/src/styles/superclasses/invisivel.css"

# Settings Pruning track (US3):
Task: "T014 [P] [US3] Add unit tests verifying pruned fields in frontend/tests/superclasses.test.mjs"
Task: "T015 [US3] Prune style, surface, and button-style in frontend/src/appearance-bootstrap.js"
Task: "T017 [US3] Update TypeScript definition in frontend/src/appearance.d.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`invisivel.css` and import in `style.css`).
2. Complete Phase 2: Foundational (Root tokens and reader shielding).
3. Complete Phase 3: User Story 1 (Desubstantialized cards, reading shift, progressive underline, editorial buttons).
4. **STOP and VALIDATE**: Verify US1 independently in browser and run tests.

### Incremental Delivery

1. Setup + Foundation → Foundation ready.
2. User Story 1 → Test independently → Editorial MVP active!
3. User Story 2 → Test independently → Staggered fade-up route transitions active.
4. User Story 3 → Test independently → Pruned settings panel with backward-compatible storage.
5. User Story 4 → Test independently → Parametric intensity and reduced-motion compliance.
6. Polish → Test suite, production build, and documentation updated.
