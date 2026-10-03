# Tasks: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar

**Feature**: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar  
**Status**: Completed  
**Artifact**: `tasks.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de contratos de tipo e preparação da suíte de testes unitários da toolbar.

- [x] T001 Definir tipos e constantes de toolbar, cores e popover em `caderno-leitura-0.1/frontend/src/types/toolbar.ts`
- [x] T002 [P] Criar arquivo de testes unitários para a toolbar dinâmica em `caderno-leitura-0.1/frontend/tests/floating_toolbar_dynamic.test.mjs`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de persistência de cor e cálculo geométrico de ancoragem para a régua e o popover.

**CRITICAL**: Nenhuma User Story pode ser iniciada antes da conclusão desta fase.

- [x] T003 [P] Implementar composable de preferência e memorização de cor `caderno-leitura-0.1/frontend/src/composables/useHighlightColorPreference.ts` com persistência em `localStorage`
- [x] T004 Atualizar utilitário de posicionamento e detecção de bordas em `caderno-leitura-0.1/frontend/src/utils/toolbarPosition.ts` para suportar tanto a régua quanto o popover ancorado

**Checkpoint**: Fundação pronta — implementação das User Stories desbloqueada.

---

## Phase 3: User Story 1 - Destaque em 1 Clique com Memorização de Cor e Ações Imediatas (Priority: P1) 🎯 MVP

**Goal**: Permitir grifar texto imediatamente com 1 clique usando a última cor utilizada (Split Button), com acesso a paleta de 5 cores sem deformar a régua, além de oclusão e cópia direta.

**Independent Test**: Selecionar texto no leitor e clicar no botão do marca-texto: o destaque deve ser criado instantaneamente na cor memorizada sem exigir abertura de paleta.

### Tests for User Story 1 🧪
- [x] T005 [P] [US1] Adicionar testes unitários para o Split Button, memorização de cor e ações imediatas em `caderno-leitura-0.1/frontend/tests/floating_toolbar_dynamic.test.mjs`

### Implementation for User Story 1
- [x] T006 [US1] Refatorar `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue` para estruturar o Split Button de marca-texto (ícone grifa direto na cor ativa, seta expansora abre paleta de 5 cores)
- [x] T007 [US1] Integrar o composable `useHighlightColorPreference` no `FloatingActionsToolbar.vue` e sincronizar eventos de ação imediata (`highlight`, `occlude`, `copy-quote`)
- [x] T008 [US1] Validar integração da régua de 1 clique em `caderno-leitura-0.1/frontend/src/views/StudyView.vue` com sincronização dos micro-toasts informativos

**Checkpoint**: User Story 1 concluída e testável de forma autônoma como MVP.

---

## Phase 4: User Story 2 - Camada Desacoplada de Anotação e Pergunta com Foco Ágil (Priority: P2)

**Goal**: Desacoplar formulários de anotação e pergunta em `NoteQuestionPopover.vue`, mantendo a régua recolhida durante a escrita e permitindo salvamento com `Enter`, nova linha com `Shift+Enter` e cancelamento com `Escape`.

**Independent Test**: Selecionar texto e clicar em "Anotar": a régua se recolhe, o popover abre ancorado com autofocus no textarea, `Enter` salva diretamente e `Escape` cancela.

### Tests for User Story 2 🧪
- [x] T009 [P] [US2] Adicionar testes unitários para o componente `NoteQuestionPopover.vue`, foco automático e atalhos de teclado em `caderno-leitura-0.1/frontend/tests/floating_toolbar_dynamic.test.mjs`

### Implementation for User Story 2
- [x] T010 [US2] Criar componente `caderno-leitura-0.1/frontend/src/components/NoteQuestionPopover.vue` com textarea, autofocus, botão de confirmação e atalhos de teclado (`Enter`, `Shift+Enter`, `Escape`)
- [x] T011 [US2] Remover blocos legados acoplados de anotação e pergunta de dentro de `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue`
- [x] T012 [US2] Integrar `NoteQuestionPopover.vue` em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`, gerenciando o recolhimento temporário da régua de ações enquanto o popover estiver aberto

**Checkpoint**: User Stories 1 e 2 operando integradas de forma estável.

---

## Phase 5: User Story 3 - Ergonomia Mobile com Gaveta Inferior e Proteção de Teclado Virtual (Priority: P3)

**Goal**: Adaptar o popover para formato de gaveta inferior (*bottom sheet*) no mobile (< 768px), integrando `window.visualViewport` para elevar a gaveta acima do teclado virtual sem sobrepor botões ou campos.

**Independent Test**: Em viewport móvel (< 768px), abrir "Anotar" ou "Pergunta": a gaveta surge na base da tela e se reposiciona dinamicamente ao abrir o teclado virtual.

### Tests for User Story 3 🧪
- [x] T013 [P] [US3] Adicionar testes unitários para layout móvel e cálculo de viewport da gaveta inferior em `caderno-leitura-0.1/frontend/tests/floating_toolbar_dynamic.test.mjs`

### Implementation for User Story 3
- [x] T014 [US3] Implementar estilos de gaveta móvel (*bottom sheet*) e alvos táteis mínimos de 44x44px em `caderno-leitura-0.1/frontend/src/components/NoteQuestionPopover.vue`
- [x] T015 [US3] Integrar listeners de `window.visualViewport` (resize e scroll) em `NoteQuestionPopover.vue` para elevação dinâmica da gaveta acima do teclado virtual móvel

**Checkpoint**: Todas as 3 User Stories concluídas e testadas nos ambientes desktop e mobile.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de regressão, homologação fim a fim e empacotamento de produção.

- [x] T016 [P] Validar cenários do guia `specs/052-toolbar-acoes-dinamica/quickstart.md`
- [x] T017 Executar suítes de testes de frontend e backend (`npm test` e `pytest`)
- [x] T018 Executar compilação estrita de produção do frontend (`npm run build`)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Fase 1 — BLOQUEIA todas as User Stories.
- **User Story 1 (Phase 3 - MVP)**: Depende da Fase 2.
- **User Story 2 (Phase 4)**: Depende da Fase 2 e pode rodar após US1.
- **User Story 3 (Phase 5)**: Depende da Fase 4 (estende `NoteQuestionPopover.vue`).
- **Polish (Phase 6)**: Depende da conclusão de todas as User Stories.

### Parallel Opportunities
- T001 e T002 podem rodar em paralelo.
- T003 e T004 podem rodar em paralelo.
- T005, T009 e T013 (testes unitários) podem ser preparados antecipadamente.
- T016 (quickstart) pode rodar em paralelo antes do build final.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (Phase 1) e Foundational (Phase 2).
2. Implementar Split Button de marca-texto em 1 clique e persistência de cor (Phase 3 - US1).
3. **STOP and VALIDATE**: Verificar grifo em 1 clique e persistência no localStorage.

### Incremental Delivery
1. Foundation pronta (Phase 1 + 2).
2. US1 entrega marca-texto ágil em 1 clique (MVP).
3. US2 desacopla anotações e perguntas em `NoteQuestionPopover.vue` com atalhos de teclado.
4. US3 adiciona adaptação de gaveta móvel com proteção de teclado virtual (`visualViewport`).
5. Phase 6 consolida testes, build e aceite fim a fim.
