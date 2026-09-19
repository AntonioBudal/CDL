# Tasks: Lixeira e Restauração de Itens (Soft Delete)

**Feature Branch**: `003-lixeira-soft-delete` | **Date**: 2026-09-18 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação de esquemas Pydantic compartilhados e estrutura da suíte de testes isolados.

- [X] T001 Criar schemas Pydantic de entrada e saída para a lixeira (`TrashBookItem`, `TrashStudyItem`, `TrashSummaryResponse`, `TrashActionResponse`) em `backend/app/schemas/trash.py`
- [X] T002 [P] Criar arquivo base da suíte de testes isolados com fixtures `tmp_path` e fábrica de dados sintéticos em `backend/tests/test_trash_soft_delete.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evolução do modelo relacional, migração de banco e serviço central de soft delete que BLOQUEIAM todas as histórias de usuário.

- [X] T003 Adicionar campo `deleted_at: Mapped[datetime | None]` com índice `ix_books_deleted_at` no modelo `Book` em `backend/app/models/book.py`
- [X] T004 [P] Adicionar campo `deleted_at: Mapped[datetime | None]` com índice `ix_studies_deleted_at` no modelo `Study` em `backend/app/models/study.py`
- [X] T005 Criar e registrar migração incremental do Alembic adicionando `deleted_at` em `books` e `studies` em `backend/migrations/versions/0003_add_trash_soft_delete.py`
- [X] T006 Implementar serviço central de persistência de lixeira (`trash_service.py`) com funções atômicas de descarte, restauração, expurgo e purga temporal em `backend/app/services/trash_service.py`
- [X] T007 [P] Atualizar interfaces TypeScript (`Book`, `Study`) e adicionar novos tipos de lixeira (`TrashBookItem`, `TrashStudyItem`, `TrashSummary`) em `frontend/src/types.ts`

**Checkpoint**: Fundação de dados e serviços pronta — implementação das histórias de usuário desbloqueada.

---

## Phase 3: User Story 1 - Envio para a Lixeira e Proteção contra Exclusão Acidental (Priority: P1) 🎯 MVP

**Goal**: Permitir mover livros inteiros ou estudos individuais para a lixeira com confirmação na interface, ocultando-os instantaneamente das consultas e telas do acervo ativo.

**Independent Test**: Criar um livro com capítulos e estudos em banco efêmero, acionar o descarte do livro e de estudos específicos, verificando que deixam de aparecer em `GET /api/books`, `GET /api/books/{id}` e na visualização da interface, mantendo os registros intactos no banco.

### Tests for User Story 1
> **Escrever os testes antes da implementação e garantir que falhem.**

- [X] T008 [P] [US1] Implementar testes para `POST /api/books/{id}/trash` e `POST /api/studies/{id}/trash` e comprovar filtro do acervo ativo em `backend/tests/test_trash_soft_delete.py`

### Implementation for User Story 1

- [X] T009 [US1] Atualizar consultas do acervo ativo para filtrar `WHERE deleted_at IS NULL` e implementar endpoint `POST /books/{id}/trash` em `backend/app/routers/books.py`
- [X] T010 [US1] Atualizar consultas e implementar endpoint `POST /studies/{id}/trash` com bloqueio de leitura de estudos descartados em `backend/app/routers/studies.py`
- [X] T011 [P] [US1] Adicionar métodos `trashBook` e `trashStudy` no cliente de API em `frontend/src/services/api.ts`
- [X] T012 [US1] Criar componente reutilizável de diálogo de confirmação `TrashConfirmModal.vue` com acessibilidade por teclado em `frontend/src/components/TrashConfirmModal.vue`
- [X] T013 [US1] Integrar ação "Mover para Lixeira" com modal de confirmação no cabeçalho do livro e nos estudos em `frontend/src/views/BookView.vue`

**Checkpoint**: User Story 1 funcional e testável de forma 100% independente (MVP de proteção contra exclusão alcançado).

---

## Phase 4: User Story 2 - Visualização da Lixeira e Restauração de Itens (Priority: P2)

**Goal**: Fornecer a tela dedicada `TrashView.vue` listando todos os itens descartados com contagem de dias restantes, permitindo restaurar livros e estudos com cascata ascendente automática.

**Independent Test**: Enviar livro e estudos para a lixeira, acessar `GET /api/trash`, restaurar um estudo cujo livro pai estava na lixeira e comprovar que livro e estudo reaparecem reativados no acervo ativo.

### Tests for User Story 2

- [X] T014 [P] [US2] Implementar testes para `GET /api/trash`, `POST /api/books/{id}/restore` e restauração em cascata ascendente de `POST /api/studies/{id}/restore` em `backend/tests/test_trash_soft_delete.py`

### Implementation for User Story 2

- [X] T015 [US2] Criar router `backend/app/routers/trash.py` com endpoint `GET /api/trash` e registrá-lo em `backend/app/main.py`
- [X] T016 [US2] Implementar endpoint `POST /books/{id}/restore` em `backend/app/routers/books.py`
- [X] T017 [US2] Implementar endpoint `POST /studies/{id}/restore` com restauração em cascata do livro ancestral em `backend/app/routers/studies.py`
- [X] T018 [P] [US2] Adicionar métodos `getTrash`, `restoreBook` e `restoreStudy` no cliente em `frontend/src/services/api.ts`
- [X] T019 [US2] Criar nova view `TrashView.vue` com listagem de itens descartados, filtros e ações de restauração em `frontend/src/views/TrashView.vue`
- [X] T020 [US2] Configurar rota `/trash` no roteador do frontend em `frontend/src/router/index.ts` e adicionar link de acesso à Lixeira no cabeçalho/navegação global em `frontend/src/App.vue`

**Checkpoint**: User Stories 1 e 2 plenamente operacionais e integradas.

---

## Phase 5: User Story 3 - Exclusão Definitiva Consciente e Esvaziamento da Lixeira (Priority: P3)

**Goal**: Permitir o expurgo físico permanente transacional de itens selecionados, esvaziamento total da lixeira e purga automática de itens com mais de 30 dias de retenção.

**Independent Test**: Simular itens na lixeira com mais de 30 dias e verificar purga automática; executar exclusão definitiva de livro com capítulos e estudos verificando limpeza atômica sem falhas de foreign key; acionar esvaziamento total da lixeira.

### Tests for User Story 3

- [X] T021 [P] [US3] Implementar testes para exclusão definitiva (`DELETE /permanent`), esvaziamento (`POST /api/trash/empty`) e purga de 30 dias (`POST /api/trash/purge-expired`) em `backend/tests/test_trash_soft_delete.py`

### Implementation for User Story 3

- [X] T022 [US3] Implementar endpoint `DELETE /books/{id}/permanent` com exclusão em cascata atômica respeitando chaves estrangeiras em `backend/app/routers/books.py`
- [X] T023 [US3] Implementar endpoint `DELETE /studies/{id}/permanent` em `backend/app/routers/studies.py`
- [X] T024 [US3] Implementar endpoints `POST /api/trash/empty` e `POST /api/trash/purge-expired` em `backend/app/routers/trash.py`
- [X] T025 [US3] Integrar rotina de purga automática de 30 dias no lifespan/startup da aplicação e na chamada de `GET /api/trash` em `backend/app/main.py`
- [X] T026 [P] [US3] Adicionar métodos `permanentDeleteBook`, `permanentDeleteStudy`, `emptyTrash` e `purgeExpired` no cliente em `frontend/src/services/api.ts`
- [X] T027 [US3] Adicionar botões de exclusão definitiva por item e botão de destaque "Esvaziar Lixeira" com modal de confirmação enfático em `frontend/src/views/TrashView.vue`

**Checkpoint**: Todas as três histórias de usuário implementadas, com ciclo de vida completo do soft delete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada ponta a ponta, testes de regressão, build do frontend e atualização da documentação.

- [X] T028 Executar validação completa de todos os 5 cenários do guia `specs/003-lixeira-soft-delete/quickstart.md`
- [X] T029 [P] Executar suíte completa de testes do backend com `pytest backend/tests/ -v` garantindo zero quebras
- [X] T030 [P] Recompilar o frontend com `npm run build` e executar suíte de testes do frontend com `npm test` em `frontend/`
- [X] T031 [P] Atualizar registro de evidências e histórico do projeto em `docs/contexto/RETOMADA.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Não possui dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA todas as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende da Phase 2 — Entrega o MVP essencial de soft delete.
- **User Story 2 (Phase 4)**: Depende da Phase 3 (utiliza o descarte de US1 para restaurar e exibir).
- **User Story 3 (Phase 5)**: Depende da Phase 4 (opera sobre os itens visualizados na lixeira).
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

---

## Parallel Opportunities

- **Phase 1**: T002 pode ser preparado em paralelo com T001.
- **Phase 2**: T004 e T007 podem ser executados em paralelo com T003.
- **Phase 3**: T008 (testes) e T011 (API client) podem ser desenvolvidos em paralelo com T009/T010.
- **Phase 4**: T014 (testes) e T018 (API client) podem rodar em paralelo com T015/T016/T017.
- **Phase 5**: T021 (testes) e T026 (API client) podem rodar em paralelo com T022/T023/T024.
- **Phase 6**: T029, T030 e T031 podem ser executados em paralelo após a validação de T028.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Phase 1 (Setup) e Phase 2 (Foundational).
2. Implementar Phase 3 (User Story 1).
3. **Validar MVP**: Comprovar que livros e estudos podem ser movidos para a lixeira e deixam o acervo ativo sem perda de dados.

### Entrega Incremental
1. MVP entregue (descarte seguro ativo).
2. Adicionar Phase 4 (User Story 2): Tela de lixeira e restauração funcional.
3. Adicionar Phase 5 (User Story 3): Exclusão definitiva e purga automática de 30 dias.
4. Finalizar Phase 6: Validação integrada, build e regressão completa.
