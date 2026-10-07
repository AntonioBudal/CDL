# Tasks: F0.7.13 — Caixa de Entrada de Capturas (Inbox de Conhecimento)

**Input**: Design artifacts from `specs/062-inbox-capturas/`
**Feature Branch**: `062-inbox-capturas`
**Specification**: [spec.md](spec.md) | **Implementation Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura de dados inicial, migração relacional e contratos compartilhados de tipos

- [X] T001 Criar migração Alembic para tabela `inbox_captures` com chaves estrangeiras e índices em `caderno-leitura-0.1/backend/migrations/versions/0027_add_inbox_captures_table.py`
- [X] T002 [P] Criar modelo SQLAlchemy `InboxCapture` em `caderno-leitura-0.1/backend/app/models/inbox_capture.py` e registrar em `caderno-leitura-0.1/backend/app/models/__init__.py`
- [X] T003 [P] Definir tipos TypeScript para `InboxCapture`, `InboxStatus`, payloads de criação/edição/promoção/vinculação e contagem em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T004 [P] Definir esquemas Pydantic `InboxCaptureCreate`, `InboxCapturePatch`, `InboxCaptureRead`, `InboxCountResponse`, `InboxPromoteRequest` e `InboxLinkRequest` em `caderno-leitura-0.1/backend/app/schemas/inbox_capture.py` e registrar em `backend/app/schemas/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Serviços centrais de banco de dados, endpoints REST e composables que bloqueiam as histórias de usuário

- [X] T005 Implementar serviço `inbox_service.py` com operações de CRUD, contagem rápida, promoção e vinculação textual a estudo em `caderno-leitura-0.1/backend/app/services/inbox_service.py`
- [X] T006 Implementar roteador `inbox.py` com endpoints `/api/inbox`, `/api/inbox/count`, `/api/inbox/{id}`, `/api/inbox/{id}/promote`, `/api/inbox/{id}/link` em `caderno-leitura-0.1/backend/app/routers/inbox.py` e registrá-lo em `caderno-leitura-0.1/backend/app/main.py`
- [X] T007 [P] Adicionar métodos clientes da API do Inbox (`getInboxCaptures`, `createInboxCapture`, `getInboxCount`, `updateInboxCapture`, `deleteInboxCapture`, `promoteInboxCapture`, `linkInboxCapture`) em `caderno-leitura-0.1/frontend/src/services/api.ts`
- [X] T008 [P] Implementar composables `useInboxCount.ts` (para estado reativo do badge) e `useQuickCapture.ts` (para controle global do modal de captura) em `caderno-leitura-0.1/frontend/src/composables/`

**Checkpoint**: Base de dados, serviços backend, métodos de API e composables prontos. A implementação das histórias de usuário pode começar.

---

## Phase 3: User Story 1 - Captura Rápida Global de Pensamentos e Citações (Priority: P1) 🎯 MVP

**Goal**: Permitir registrar ideias e citações em menos de 5 segundos via modal global (`Ctrl+Shift+C` ou botão de topo) sem sair do contexto da tela atual.

**Independent Test**: Pressionar o atalho `Ctrl+Shift+C` em qualquer tela, digitar uma nota com fonte opcional, pressionar `Ctrl+Enter` para salvar e constatar o fechamento com microtoast e incremento do badge no menu.

### Tests for User Story 1

- [X] T009 [P] [US1] Criar testes de backend para `POST /api/inbox` e `GET /api/inbox/count` com validação de dados e isolamento multiusuário em `caderno-leitura-0.1/backend/tests/test_inbox.py`
- [X] T010 [P] [US1] Criar testes de frontend para `useQuickCapture`, modal de captura e atalho `Ctrl+Shift+C` em `caderno-leitura-0.1/frontend/tests/inbox.test.mjs`

### Implementation for User Story 1

- [X] T011 [US1] Implementar componente `QuickCaptureModal.vue` com auto-foco, atalhos de teclado (`Ctrl+Enter`, `Escape`), seleção opcional de livro e indicação de fonte em `caderno-leitura-0.1/frontend/src/components/inbox/QuickCaptureModal.vue`
- [X] T012 [US1] Integrar `QuickCaptureModal.vue`, listener de atalho `Ctrl+Shift+C`, botão rápido "Capturar" no cabeçalho e badge numérico reativo no item "Inbox" do menu lateral em `caderno-leitura-0.1/frontend/src/App.vue`

**Checkpoint**: User Story 1 (MVP) completamente funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Central de Triagem e Gerenciamento do Inbox (Priority: P2)

**Goal**: Prover tela dedicada `/inbox` com cartões individuais, busca textual instantânea, filtros por status (`inbox`, `promoted`, `linked`, `archived`), edição rápida e descarte.

**Independent Test**: Acessar `/inbox`, visualizar a lista cronológica reversa de capturas, filtrar por texto no cabeçalho, editar uma captura existente inline e descartar/arquivar um item indesejado.

### Tests for User Story 2

- [X] T013 [P] [US2] Adicionar testes de backend para listagem filtrada por status, busca por texto e atualização/exclusão de capturas em `caderno-leitura-0.1/backend/tests/test_inbox.py`
- [X] T014 [P] [US2] Adicionar testes de frontend para listagem, filtros e ações do cartão em `caderno-leitura-0.1/frontend/tests/inbox.test.mjs`

### Implementation for User Story 2

- [X] T015 [US2] Implementar componente `CaptureItemCard.vue` com renderização de metadados, expansão de texto longo, modo de edição inline e menu de ações em `caderno-leitura-0.1/frontend/src/components/inbox/CaptureItemCard.vue`
- [X] T016 [US2] Implementar view `InboxView.vue` com filtros por abas de status, barra de busca textual, contadores e estado vazio informativo em `caderno-leitura-0.1/frontend/src/views/InboxView.vue`
- [X] T017 [US2] Registrar rota `/inbox` com metadados de título e ícone em `caderno-leitura-0.1/frontend/src/router/index.ts`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma independente.

---

## Phase 5: User Story 3 - Promoção de Captura para Estudo Formal ou Vinculação a Estudo Existente (Priority: P3)

**Goal**: Permitir transformar a captura em um estudo formal pré-preenchido no editor ou anexá-la como nota de citação em um estudo existente com 1 clique.

**Independent Test**: Clicar em "Promover para Estudo" em um cartão do Inbox, verificar o redirecionamento com texto pré-injetado no editor e a posterior marcação da captura como `promoted`; vincular captura a estudo existente através de modal de seleção confirmando a injeção na seção `references` e a marcação como `linked`.

### Tests for User Story 3

- [X] T018 [P] [US3] Adicionar testes de backend para `POST /api/inbox/{id}/promote` e `POST /api/inbox/{id}/link` com integridade relacional em `caderno-leitura-0.1/backend/tests/test_inbox.py`
- [X] T019 [P] [US3] Adicionar testes de frontend para fluxo de promoção e modal de vinculação em `caderno-leitura-0.1/frontend/tests/inbox.test.mjs`

### Implementation for User Story 3

- [X] T020 [US3] Implementar componente `LinkToStudyModal.vue` com busca de estudos existentes do usuário e seleção de seção de destino para vinculação em `caderno-leitura-0.1/frontend/src/components/inbox/LinkToStudyModal.vue`
- [X] T021 [US3] Integrar suporte a promoção de capturas no editor/importador com pré-preenchimento de campos e callback de finalização via `POST /api/inbox/{id}/promote` em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` e `caderno-leitura-0.1/frontend/src/views/InboxView.vue`

**Checkpoint**: Todas as 3 histórias de usuário concluídas e integradas com ciclo de conhecimento completo (`[CAPTURAR] -> [ORGANIZAR] -> [CONECTAR]`).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinamentos ergonômicos, acessibilidade móvel e validação estrita das suítes de teste

- [X] T022 [P] Ajustar responsividade móvel (áreas de toque $\ge 44 \times 44$px, adaptação à viewport do teclado no modal) em `caderno-leitura-0.1/frontend/src/components/inbox/QuickCaptureModal.vue` e `caderno-leitura-0.1/frontend/src/views/InboxView.vue`
- [X] T023 Executar verificação de conformidade do Design System (ausência de emojis informais) em `caderno-leitura-0.1/frontend/tests/visual_system.test.mjs`
- [X] T024 Executar suíte completa de testes do backend via `pytest` em `caderno-leitura-0.1/backend`
- [X] T025 Executar suíte completa de testes do frontend via `npm test` em `caderno-leitura-0.1/frontend`
- [X] T026 Executar validação de tipos TypeScript e build de produção via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T027 Executar validação dos cenários manuais de ponta a ponta descritos em `specs/062-inbox-capturas/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA todas as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende de Phase 2 — MVP de captura rápida.
- **User Story 2 (Phase 4)**: Depende de Phase 2 e complementa US1 com a tela de gerenciamento.
- **User Story 3 (Phase 5)**: Depende de Phase 2, US1 e US2 para fluxo completo de promoção e vinculação.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- T002, T003, T004 podem ser executadas em paralelo dentro da Phase 1.
- T007 e T008 podem ser executadas em paralelo dentro da Phase 2.
- Testes T009 e T010 podem ser desenvolvidos em paralelo no início de US1.
- Testes T013 e T014 podem ser desenvolvidos em paralelo no início de US2.
- Testes T018 e T019 podem ser desenvolvidos em paralelo no início de US3.
