# Tasks: 012 — Correção de Roteamento, Fonte Global e Limpeza de Ajustes

**Input**: Design documents from `specs/012-roteamento-fonte-ajustes/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/appearance-settings.contract.md](contracts/appearance-settings.contract.md)  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação inicial e contratos de interfaces tipadas.

- [X] T001 Mapear contratos de roteamento, preferências e tipografia entre `plan.md` e `caderno-leitura-0.1/frontend/src/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tipagem estrita e saneamento de tipos compartilhados.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Atualizar a interface `AppearancePreferences` removendo campos obsoletos `motion`, `button-width` e `tabs` em `caderno-leitura-0.1/frontend/src/appearance.d.ts`

**Checkpoint**: Fundação tipada pronta - implementação das histórias de usuário desbloqueada.

---

## Phase 3: User Story 1 - Navegação Fluida e Confiável sem Telas Vazias (Priority: P1) 🎯 MVP

**Goal**: Eliminar definitivamente o bug da tela em branco nas trocas de abas e rotas do Vue Router através de `:key="$route.fullPath"` e encapsulamento em nós raiz únicos nas 5 visualizações que possuíam fragmentos.

**Independent Test**: Navegar sequencialmente entre Livros (`/`), Detalhes (`/livros/:id`), Leitura (`/livros/:id/estudos/:id`), Importar (`/importar`), Ajustes (`/ajustes`) e Lixeira (`/lixeira`), comprovando que todas as telas montam e renderizam instantaneamente sem telas brancas e sem exigir F5.

### Tests for User Story 1

- [X] T003 [P] [US1] Adicionar testes unitários de renderização de rotas e estabilidade de chaves reativas em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 1

- [X] T004 [US1] Configurar `:key="$route.fullPath"` no `<component :is="Component" />` sob `<Transition>` em `caderno-leitura-0.1/frontend/src/App.vue`
- [X] T005 [P] [US1] Envolver template em nó raiz único `<div class="books-view">` em `caderno-leitura-0.1/frontend/src/views/BooksView.vue`
- [X] T006 [P] [US1] Envolver template em nó raiz único `<div class="book-view">` em `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [X] T007 [P] [US1] Envolver template em nó raiz único `<div class="study-view">` em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`
- [X] T008 [P] [US1] Envolver template em nó raiz único `<div class="study-edit-view">` em `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`
- [X] T009 [P] [US1] Envolver template em nó raiz único `<div class="import-view">` em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

**Checkpoint**: User Story 1 concluída e testável de forma 100% independente (MVP alcançado: navegação estável e sem telas vazias).

---

## Phase 4: User Story 2 - Herança Global e Preview Imediato da Tipografia Escolhida (Priority: P2)

**Goal**: Elevar a variável `--font-reading` para a interface global e aplicá-la de forma irrestrita em 100% dos elementos da página (`:root, body, #app, button, input, select, textarea, code, pre`), proporcionando preview instantâneo.

**Independent Test**: Abrir Ajustes, selecionar diferentes famílias de fonte no catálogo e verificar que botões, títulos, formulários, menus e o card de preview mudam imediatamente a tipografia sem recarregar a página.

### Tests for User Story 2

- [X] T010 [P] [US2] Adicionar testes unitários para propagação global de `--font-ui` e herança em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 2

- [X] T011 [US2] Vincular `--font-ui: var(--font-reading);` no escopo raiz em `caderno-leitura-0.1/frontend/src/tokens.css`
- [X] T012 [US2] Aplicar `font-family: var(--font-reading)` a `:root, body, #app, button, input, select, textarea, code, pre` em `caderno-leitura-0.1/frontend/src/style.css`

**Checkpoint**: User Story 2 funcional. A troca de fonte passa a surtir efeito em toda a aplicação em tempo real.

---

## Phase 5: User Story 3 - Poda de Ajustes Redundantes, Purga de `localStorage` e Renumeração Limpa (Priority: P3)

**Goal**: Remover as opções obsoletas `motion`, `button-width` e `tabs` absorvidas pelas Superclasses, purgar chaves legadas do `localStorage` e renumerar os 7 grupos restantes de 1 a 7.

**Independent Test**: Abrir Ajustes e confirmar exatamente 7 grupos numerados (1 a 7) além de Aparência básica, sem menção a Movimento, Botões ou Abas, e validar a higienização do `localStorage`.

### Tests for User Story 3

- [X] T013 [P] [US3] Adicionar testes unitários para a validação dos 7 grupos numerados e purga de `localStorage` em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

### Implementation for User Story 3

- [X] T014 [US3] Remover `motion`, `button-width` e `tabs` do catálogo `fields` e implementar purga ativa de chaves antigas em `normalize()` em `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js`
- [X] T015 [US3] Renumerar sequencialmente os 7 grupos (1. Cor, 2. Densidade, 3. Leitura, 4. Marcação, 5. Acervo, 6. Largura, 7. Superclasse) em `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js`
- [X] T016 [US3] Atualizar dicas contextuais e textos de ajuda eliminando menções a controles podados em `caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue`

**Checkpoint**: Todas as 3 histórias de usuário concluídas e integradas com sucesso.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação automatizada, compilação de produção e auditoria documental.

- [X] T017 [P] Executar bateria completa de testes unitários via `npm test` em `caderno-leitura-0.1/frontend`
- [X] T018 [P] Executar verificação estrita de tipos TypeScript e build Vite via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T019 Executar validação manual dos cenários 1 a 5 de `quickstart.md`
- [X] T020 Atualizar documentação de diagnóstico e registro de transição em `caderno-leitura-0.1/docs/contexto/RETOMADA.md` e `ESTADO-E-DIAGNOSTICO.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA todas as histórias de usuário.
- **User Stories (Phase 3+)**: Dependem de Foundational (Phase 2). Podem ser executadas em sequência ordenada (US1 → US2 → US3) ou com tarefas [P] paralelas.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

### User Story Dependencies

- **User Story 1 (P1)**: Desbloqueada após Phase 2. Foco exclusivo em roteamento e enraizamento de views. Não depende de US2 nem US3.
- **User Story 2 (P2)**: Desbloqueada após Phase 2. Foco em CSS/tokens de tipografia.
- **User Story 3 (P3)**: Desbloqueada após Phase 2. Foco em catálogo de aparência, `localStorage` e componentes de ajustes.

### Parallel Opportunities

- Tarefas T005, T006, T007, T008 e T009 em US1 alteram arquivos de visualizações distintos e podem ser executadas em paralelo.
- Testes T003, T010, T013 podem ser escritos em paralelo com o planejamento das histórias.
- T017 e T018 em Polish podem rodar concorrentemente.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001) e Foundational (T002).
2. Implementar User Story 1 (T003 a T009).
3. **Validar MVP**: Navegar entre as páginas e comprovar a eliminação do bug da tela vazia.

### Incremental Delivery
1. MVP entregue (Navegação 100% estável).
2. Adicionar User Story 2 (T010 a T012) → Fonte global refletida instantaneamente.
3. Adicionar User Story 3 (T013 a T016) → Painel de Ajustes simplificado para 7 grupos e `localStorage` purgado.
4. Polish (T017 a T020) → Testes verdes, build validado e documentação sincronizada.
