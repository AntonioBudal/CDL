# Tasks: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Input**: Design documents from `specs/084-seguranca-leitor-refinamento-estudos/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/  
**Tests**: Suíte de testes unitários automatizada incluída em `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs`  
**Organization**: Tarefas agrupadas por histórias de usuário para entrega e teste independentes.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos distintos, sem dependências cruzadas)
- **[Story]**: Mapeamento da história de usuário correspondente (ex.: US1, US2, US3)
- Caminhos absolutos e relativos exatos em cada tarefa

---

## Phase 1: Setup & Foundational (Shared Infrastructure)

**Purpose**: Criação do arquivo de testes unitários da feature e verificação de contratos de componentes base

- [x] T001 [P] Setup test suite file in `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs`
- [x] T002 [P] Verify `DropdownMenu.vue` contract and slot exports in `caderno-leitura-0.1/frontend/src/components/ui/DropdownMenu.vue`

---

## Phase 2: User Story 1 - Menu Contextual de Ações Secundárias no Leitor (Priority: P1) [MVP]

**Goal**: No cabeçalho de `StudyView.vue`, manter em destaque primário apenas o botão "Editar estudo" e a pílula de status, encapsulando as ações de Compartilhar, Exportar, Histórico de Versões e Mover para a Lixeira dentro do menu contextual `DropdownMenu.vue` ("Mais opções"), protegendo o leitor contra exclusões acidentais.

**Independent Test**: Acessar um estudo em `/livros/:bookId/estudos/:studyId`; constatar que o botão de lixeira não está visível na barra primária; clicar no menu "Mais opções" e verificar que as ações são listadas com separador e estilo de perigo na lixeira, abrindo o `TrashConfirmModal.vue`.

### Tests for User Story 1

- [x] T003 [P] [US1] Write unit tests for contextual actions menu and delete button protection in `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs`

### Implementation for User Story 1

- [x] T004 [US1] Import `DropdownMenu` and `Icon` in `caderno-leitura-0.1/frontend/src/views/StudyView.vue`
- [x] T005 [US1] Refactor `.header-actions` markup in `caderno-leitura-0.1/frontend/src/views/StudyView.vue` to retain only "Editar estudo" as primary action and replace the loose icon strip with `DropdownMenu`
- [x] T006 [US1] Implement dropdown menu items in `StudyView.vue`: Compartilhar (condicionado a `canEdit`), Exportar, Histórico de Versões, separador e Mover para a Lixeira (`.danger-item`, condicionado a `canEdit`)
- [x] T007 [US1] Add responsive and theme-compliant styles for `.study-actions-menu`, `.dropdown-divider` and `.dropdown-item.danger-item` using CSS tokens in `caderno-leitura-0.1/frontend/src/views/StudyView.vue`
- [x] T008 [US1] Ensure touch targets for study header buttons and menu trigger have min 44x44px in `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: User Story 1 funcional e testável de forma independente no leitor.

---

## Phase 3: User Story 2 - Indicador Visual de Persistência e Rascunho no Editor (Priority: P1)

**Goal**: Adicionar pílula sutil de status (`.draft-status-pill`) ao lado do título em `StudyEditView.vue`, refletindo de forma reativa os estados de "Salvando…", "Rascunho salvo neste navegador" e "Alterações salvas".

**Independent Test**: Editar um estudo em `StudyEditView.vue`; constatar que ao digitar texto a pílula exibe "Rascunho salvo neste navegador", ao clicar em salvar exibe "Salvando…", e ao sincronizar retorna para "Alterações salvas".

### Tests for User Story 2

- [x] T009 [P] [US2] Write unit tests for reactive draft/saving status pill in `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs`

### Implementation for User Story 2

- [x] T010 [US2] Import `Icon` and define computed properties `draftStatusLabel`, `draftStatusClass` and `draftStatusIcon` in `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`
- [x] T011 [US2] Update template in `StudyEditView.vue` to render `.draft-status-pill` inside `.edit-title-row` with `role="status"` and `aria-live="polite"`
- [x] T012 [US2] Add CSS styles for `.edit-title-row` and `.draft-status-pill` (`.saving`, `.draft-local`, `.saved`) using theme CSS variables in `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`
- [x] T013 [US2] Ensure smooth transition and non-intrusive geometry for the status pill on mobile and desktop in `StudyEditView.vue`
- [x] T014 [US2] Integrate status transitions with `useStudyDraft` and `editor.state.saving` in `StudyEditView.vue`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas sem conflitos.

---

## Phase 4: User Story 3 - Alvos de Toque Ergonômicos na Barra de Leitura e Abas (Priority: P2)

**Goal**: Calibrar todos os botões de `ActiveReadingBar.vue` (inclusive `.close-btn`) e as abas em `StudyTabs.vue` para garantir dimensão tátil mínima de 44x44px em ponteiros táteis (`@media (pointer: coarse)`) e telas móveis (`<= 767px`).

**Independent Test**: Inspecionar no DevTools móvel as dimensões calculadas de `.close-btn` e `.reading-bar-btn` em `ActiveReadingBar.vue`, e de `[role="tab"]` em `StudyTabs.vue`, confirmando que todos atendem a `min-height: 44px` e `min-width: 44px`.

### Tests for User Story 3

- [x] T015 [P] [US3] Write unit tests for 44x44px touch targets in `ActiveReadingBar.vue` and `StudyTabs.vue` in `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs`

### Implementation for User Story 3

- [x] T016 [US3] Update CSS in `caderno-leitura-0.1/frontend/src/components/ActiveReadingBar.vue` to ensure `.reading-bar-btn` and `.close-btn` have `min-height: 44px; min-width: 44px;` under mobile and coarse pointers
- [x] T017 [US3] Update CSS in `caderno-leitura-0.1/frontend/src/style.css` and `caderno-leitura-0.1/frontend/src/components/StudyTabs.vue` ensuring `.study-tabs [role="tab"]` maintains `min-height: 44px` on mobile/touch
- [x] T018 [US3] Verify focus rings and active states with `prefers-reduced-motion` in `ActiveReadingBar.vue` and `StudyTabs.vue`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e em conformidade estrita com WCAG 2.5.5.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, conformidade estética, integridade de temas e validação integral com suítes de testes

- [x] T019 [P] Audit all modified files (`StudyView.vue`, `StudyEditView.vue`, `ActiveReadingBar.vue`, `StudyTabs.vue`, tests) for strict zero emojis compliance
- [x] T020 [P] Audit CSS variables in modified files to guarantee no undefined CSS tokens (running `tests/feature-075-css-tokens-integrity.test.mjs`)
- [x] T021 Run dedicated feature test suite `node --test tests/feature-084-study-reader-safety.test.mjs` in `caderno-leitura-0.1/frontend`
- [x] T022 Run full frontend test suite `npm test` and build check `npm run build` in `caderno-leitura-0.1/frontend`
- [x] T023 Run backend test suite `.venv/Scripts/pytest.exe` in `caderno-leitura-0.1/backend`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phase 1)**: Sem dependências, inicia de imediato.
- **User Story 1 (Phase 2)**: Depende de Phase 1. Fornece a proteção de exclusão no leitor.
- **User Story 2 (Phase 3)**: Depende de Phase 1. Pode rodar em paralelo ou sequencialmente com US1.
- **User Story 3 (Phase 4)**: Depende de Phase 1. Pode rodar em paralelo ou sequencialmente.
- **Polish (Phase 5)**: Depende da conclusão de US1, US2 e US3.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Fase 1 (Setup de testes).
2. Implementar Fase 2 (Menu contextual e proteção de lixeira no leitor).
3. Validar US1 com `node --test tests/feature-084-study-reader-safety.test.mjs`.

### Incremental Delivery
1. Implementar Fase 3 (Pílula de persistência no editor).
2. Implementar Fase 4 (Alvos táteis em `ActiveReadingBar` e `StudyTabs`).
3. Executar Fase 5 (Polimento, Verificação de Tokens CSS, Build e Pytest).
4. Gerar commit atômico: `feature — seguranca operacional e refinamento do leitor de estudos`.
