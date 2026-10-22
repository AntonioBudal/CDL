# Tasks: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Input**: Design documents from `specs/083-ergonomia-mobile-pagina-livro/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/  
**Tests**: Suíte de testes unitários automatizada incluída em `caderno-leitura-0.1/frontend/tests/feature-083-book-mobile-layout.test.mjs`  
**Organization**: Tarefas agrupadas por histórias de usuário para entrega e teste independentes.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos distintos, sem dependências cruzadas)
- **[Story]**: Mapeamento da história de usuário correspondente (ex.: US1, US2, US3)
- Caminhos absolutos e relativos exatos em cada tarefa

---

## Phase 1: Setup & Foundational (Shared Infrastructure)

**Purpose**: Criação da estrutura de testes da feature e verificação de contratos de componentes compartilhados

- [x] T001 [P] Setup test suite file in `caderno-leitura-0.1/frontend/tests/feature-083-book-mobile-layout.test.mjs`
- [x] T002 [P] Verify `DropdownMenu.vue` contract and slots in `caderno-leitura-0.1/frontend/src/components/ui/DropdownMenu.vue`

---

## Phase 2: User Story 1 - Cabeçalho Condensado de Linha Dupla com Ações Agrupadas no Mobile (Priority: P1) [MVP]

**Goal**: Reorganizar o cabeçalho de `BookView.vue` em duas linhas compactas no celular (`<= 767px`): miniatura de capa (48x72px), título com clamp 2 linhas e autor na linha 1; categorias e menu agrupado de ações ("Ações do livro" com `DropdownMenu.vue`) na linha 2.

**Independent Test**: Acessar `/livros/:bookId` em viewport móvel (390x844px e 360x740px); constatar que a altura do cabeçalho não ultrapassa 160px e que o menu de ações abre e dispara Modo Foco, Exportar, Editar e Mover para a Lixeira com alvos táteis de no mínimo 44x44px.

### Tests for User Story 1

- [x] T003 [P] [US1] Write unit tests for mobile condensed header and actions dropdown in `caderno-leitura-0.1/frontend/tests/feature-083-book-mobile-layout.test.mjs`

### Implementation for User Story 1

- [x] T004 [US1] Import `DropdownMenu` and create mobile actions markup in `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [x] T005 [US1] Restructure header markup into 2-line mobile composition in `caderno-leitura-0.1/frontend/src/views/BookView.vue` (cover thumbnail 48x72px, 2-line title clamp, line 2 categories and actions trigger)
- [x] T006 [US1] Add responsive CSS rules for `@media (max-width: 767px)` to hide `.header-actions.desktop-actions` and style `.book-mobile-actions-wrapper` in `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [x] T007 [US1] Ensure touch targets for mobile action triggers and items have min 44x44px in `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: User Story 1 totalmente funcional e testável de forma independente no mobile.

---

## Phase 3: User Story 2 - Faixa de Capítulos Unificada sem Redundância no Celular (Priority: P1)

**Goal**: Suprimir a esteira horizontal de pílulas roláveis duplicada no celular (`.chapters-nav-strip`), mantendo exclusivamente o seletor unificado (`.chapters-mobile-select`) com contador de estudos e botão discreto de novo capítulo inline.

**Independent Test**: Simular viewport móvel (390x844px); constatar que `.chapters-nav-strip` está oculta via `display: none !important;` e que o seletor móvel permite troca de capítulos e adição de novo capítulo sem conflito visual.

### Tests for User Story 2

- [x] T008 [P] [US2] Write unit tests for chapter bar unification and duplicate strip suppression in `caderno-leitura-0.1/frontend/tests/feature-083-book-mobile-layout.test.mjs`

### Implementation for User Story 2

- [x] T009 [US2] Add responsive CSS rule in `caderno-leitura-0.1/frontend/src/views/BookView.vue` under `@media (max-width: 767px)` to suppress `.chapters-nav-strip`
- [x] T010 [US2] Refactor `.chapters-mobile-select-wrap` in `caderno-leitura-0.1/frontend/src/views/BookView.vue` to display chapter index, name and study count cleanly
- [x] T011 [US2] Optimize inline chapter creation trigger and form for mobile layout with min 44px height in `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas sem sobreposição na casca móvel do livro.

---

## Phase 4: User Story 3 - Inspetor Analítico Recolhível por Padrão no Celular (Priority: P2)

**Goal**: Adicionar estado reativo `isInspectorExpandedMobile` para manter a faixa do inspetor colapsada por padrão no celular, com botão de alternância acessível com `:aria-expanded`, liberando o rodapé para foco na leitura.

**Independent Test**: Carregar um livro no mobile; constatar que `.inspector-bar-content` inicia colapsado e que o botão "Ver detalhes do livro" expande e recolhe o painel suavemente.

### Tests for User Story 3

- [x] T012 [P] [US3] Write unit tests for collapsible inspector in `caderno-leitura-0.1/frontend/tests/feature-083-book-mobile-layout.test.mjs`

### Implementation for User Story 3

- [x] T013 [US3] Add reactive state `isInspectorExpandedMobile` in `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [x] T014 [US3] Add accordion toggle button `.inspector-mobile-toggle` with `aria-expanded` and `aria-controls` in `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [x] T015 [US3] Add responsive CSS in `caderno-leitura-0.1/frontend/src/views/BookView.vue` to hide `.inspector-mobile-toggle` on desktop (`>= 768px`) and collapse `.inspector-bar-content` by default on mobile (`<= 767px`)

**Checkpoint**: Todas as 3 histórias de usuário implementadas e verificáveis.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, conformidade estética, testes de regressão e validação com suítes de testes

- [x] T016 [P] Audit `BookView.vue` and new tests to verify strict zero emojis compliance
- [x] T017 [P] Audit all 10 theme styles in palettes to ensure new mobile elements use theme CSS variables without fixed hex codes
- [x] T018 Run desktop regression tests in `caderno-leitura-0.1/frontend/tests/book-horizontal-layout.test.mjs` and mobile tests in `tests/feature-083-book-mobile-layout.test.mjs`
- [x] T019 Run full frontend test suite `npm test` in `caderno-leitura-0.1/frontend`
- [x] T020 Run production build `npm run build` (`vue-tsc -b && vite build`) to verify type check and bundle compilation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phase 1)**: Sem dependências externas, executa imediatamente.
- **User Story 1 (Phase 2)**: Depende de Phase 1. Fornece o cabeçalho condensado e menu de ações.
- **User Story 2 (Phase 3)**: Depende de Phase 1. Pode rodar em paralelo ou sequencialmente com US1.
- **User Story 3 (Phase 4)**: Depende de Phase 1. Pode rodar em paralelo ou sequencialmente.
- **Polish (Phase 5)**: Depende da conclusão de US1, US2 e US3.

### Parallel Opportunities

- `T001` (setup de testes) e `T002` (verificação de `DropdownMenu.vue`) podem rodar em paralelo.
- `T003` (testes US1), `T008` (testes US2) e `T012` (testes US3) podem ser estruturados em paralelo no arquivo de testes.
- As tarefas de estilo e template de cada história de usuário em `BookView.vue` podem ser implementadas incrementalmente.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Completar Fase 1 (Setup de Teste).
2. Implementar Fase 2 (User Story 1: Cabeçalho Condensado no Mobile).
3. Validar US1 de forma isolada com `node --test tests/feature-083-book-mobile-layout.test.mjs`.

### Incremental Delivery
1. Implementar Fase 3 (User Story 2: Faixa de Capítulos Unificada).
2. Implementar Fase 4 (User Story 3: Inspetor Analítico Recolhível).
3. Executar Fase 5 (Polimento, Regressão Desktop, Suíte Completa e Build).
4. Commitar atômico seguindo a convenção: `feature — ergonomia mobile e descongestionamento da pagina do livro`.
