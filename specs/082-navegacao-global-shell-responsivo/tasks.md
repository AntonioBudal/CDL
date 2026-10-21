# Tasks: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Input**: Design documents from `specs/082-navegacao-global-shell-responsivo/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/  
**Tests**: Suíte de testes unitários automatizada incluída em `caderno-leitura-0.1/frontend/tests/feature-082-navigation-shell.test.mjs`  
**Organization**: Tarefas agrupadas por histórias de usuário para entrega e teste independentes.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos distintos, sem dependências cruzadas)
- **[Story]**: Mapeamento da história de usuário correspondente (ex.: US1, US2, US3)
- Caminhos absolutos e relativos exatos em cada tarefa

---

## Phase 1: Setup & Foundational (Shared Infrastructure)

**Purpose**: Definição de contratos de tipagem e base de testes compartilhada

- [x] T001 [P] Create navigation types in `caderno-leitura-0.1/frontend/src/types/navigation.ts` and re-export in `caderno-leitura-0.1/frontend/src/types/index.ts`
- [x] T002 Setup test file structure in `caderno-leitura-0.1/frontend/tests/feature-082-navigation-shell.test.mjs`

---

## Phase 2: User Story 1 - Acesso Simultâneo a Dashboard e Livros no Desktop (Priority: P1) [MVP]

**Goal**: Garantir que o Dashboard (`/dashboard`) e o Acervo de Livros (`/livros`) coexistam de forma permanente na barra de navegação desktop, eliminando a dependência excludente de `homeViewPreference`.

**Independent Test**: Definir `caderno_home_view = 'dashboard'` e verificar que ambas as abas permanecem visíveis, clicáveis e com destaque de rota ativa correto no desktop (`>= 768px`).

### Tests for User Story 1

- [x] T003 [P] [US1] Write unit tests for NavigationTabs desktop primary items in `caderno-leitura-0.1/frontend/tests/feature-082-navigation-shell.test.mjs`

### Implementation for User Story 1

- [x] T004 [US1] Refactor `primaryNavItems` in `caderno-leitura-0.1/frontend/src/components/layout/NavigationTabs.vue` to include both Dashboard and Livros as permanent primary items
- [x] T005 [US1] Update route matching logic in `caderno-leitura-0.1/frontend/src/components/layout/NavigationTabs.vue` to isolate `dashboard` from `books`, `book`, `study` and `study-edit`
- [x] T006 [US1] Ensure logo link in `caderno-leitura-0.1/frontend/src/components/layout/GlobalHeader.vue` preserves redirection based on `homeViewPreference` without hiding tabs

**Checkpoint**: User Story 1 totalmente funcional e testável de forma independente no desktop.

---

## Phase 3: User Story 2 - Respiro Inferior Dinâmico no Mobile sem Sobreposição (Priority: P1)

**Goal**: Assegurar que o rodapé (`.app-footer`) e conteúdos longos no celular terminem acima da barra móvel fixa (`MobileTabBar.vue`), removendo também o botão duplicado de menu no cabeçalho superior.

**Independent Test**: Simular viewport móvel (390x844px e 360x740px) e verificar que o rodapé global e os botões inferiores mantêm respiro de pelo menos 1.5rem acima da `MobileTabBar`.

### Tests for User Story 2

- [x] T007 [P] [US2] Write unit tests for mobile footer offset and trigger cleanup in `caderno-leitura-0.1/frontend/tests/feature-082-navigation-shell.test.mjs`

### Implementation for User Story 2

- [x] T008 [US2] Add responsive `margin-bottom` calculation for `.app-footer` in `caderno-leitura-0.1/frontend/src/App.vue` under `@media (max-width: 767px)` for authenticated users
- [x] T009 [US2] Remove duplicate `.mobile-more-trigger` button and associated CSS in `caderno-leitura-0.1/frontend/src/components/layout/GlobalHeader.vue`
- [x] T010 [US2] Ensure minimum breathing room and safe-area padding in `caderno-leitura-0.1/frontend/src/App.vue` for `#conteudo`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas sem sobreposição na casca móvel.

---

## Phase 4: User Story 3 - Trilha de Navegação Universal e Previsível (AppBreadcrumb) (Priority: P2)

**Goal**: Criar o componente semântico `AppBreadcrumb.vue` e integrá-lo de forma padronizada em todas as telas com hierarquia de navegação.

**Independent Test**: Navegar para `/livros/:bookId/estudos/:studyId` e verificar que o breadcrumb exibe a trilha completa com links válidos para `/livros`, para o livro/capítulo e página atual marcada com `aria-current="page"`.

### Tests for User Story 3

- [x] T011 [P] [US3] Write unit tests for AppBreadcrumb component in `caderno-leitura-0.1/frontend/tests/feature-082-navigation-shell.test.mjs`

### Implementation for User Story 3

- [x] T012 [P] [US3] Create component `caderno-leitura-0.1/frontend/src/components/ui/AppBreadcrumb.vue` with HTML5 `<nav>`, `<ol>`, `<li>`, separator and truncation styling
- [x] T013 [US3] Replace ad-hoc breadcrumb in `caderno-leitura-0.1/frontend/src/views/BookView.vue` with `AppBreadcrumb` linking to `/livros`
- [x] T014 [US3] Replace ad-hoc breadcrumb in `caderno-leitura-0.1/frontend/src/views/StudyView.vue` with `AppBreadcrumb`
- [x] T015 [US3] Replace ad-hoc breadcrumb in `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue` with `AppBreadcrumb`
- [x] T016 [US3] Replace ad-hoc breadcrumb in `caderno-leitura-0.1/frontend/src/views/UserProfileView.vue` with `AppBreadcrumb`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e verificáveis.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, conformidade estética e validação com suítes de testes

- [x] T017 [P] Audit all modified components to verify strict zero emojis compliance
- [x] T018 [P] Audit all 10 theme styles in palettes to ensure breadcrumb and navigation elements use theme CSS variables without fixed hex codes
- [x] T019 Run full frontend test suite `npm test` in `caderno-leitura-0.1/frontend`
- [x] T020 Run production build `npm run build` (`vue-tsc -b && vite build`) to verify type check and bundle compilation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phase 1)**: Sem dependências externas, executa imediatamente.
- **User Story 1 (Phase 2)**: Depende de Phase 1. Fornece a fundação de navegação desktop.
- **User Story 2 (Phase 3)**: Depende de Phase 1. Pode rodar em paralelo com US1 ou sequencialmente.
- **User Story 3 (Phase 4)**: Depende de Phase 1 (tipos em `navigation.ts`). Pode rodar em paralelo ou sequencialmente.
- **Polish (Phase 5)**: Depende da conclusão de US1, US2 e US3.

### Parallel Opportunities

- `T001` (tipos) e `T002` (estrutura de teste) podem rodar em paralelo.
- `T003` (testes US1), `T007` (testes US2) e `T011` (testes US3) podem ser desenvolvidos em paralelo no arquivo de testes.
- `T012` (`AppBreadcrumb.vue`) pode ser criado independentemente das alterações em `NavigationTabs.vue`.
- `T013`, `T014`, `T015` e `T016` (integração do breadcrumb nas views) podem ser executados em paralelo após `T012`.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Completar Fase 1 (Tipagem e Setup de Teste).
2. Implementar Fase 2 (User Story 1: Desktop Navigation).
3. Validar US1 de forma isolada com `npm test`.

### Incremental Delivery
1. Implementar Fase 3 (User Story 2: Mobile Offset).
2. Implementar Fase 4 (User Story 3: AppBreadcrumb).
3. Executar Fase 5 (Polimento, Verificação de 10 Temas e Build).
4. Commitar atômico seguindo a convenção: `feature — arquitetura de navegação global e shell responsivo`.
