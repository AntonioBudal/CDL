# Tasks: Edição Completa de Metadados de Livros, Capítulos e Anotações

**Feature Branch**: `002-edicao-livros-estudos` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação de esquemas Pydantic e ambiente de testes isolados compartilhado.

- [X] T001 Preparar schemas Pydantic de entrada e saída para edição de livros e capítulos em `backend/app/schemas/book.py` e `backend/app/schemas/chapter.py`
- [X] T002 [P] Criar arquivo base de testes isolados da feature com fixture `tmp_path` em `backend/tests/test_edit_acervo.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Evolução de modelos de dados, migração de banco e infraestrutura de concorrência que BLOQUEIAM todas as histórias de usuário.

- [X] T003 Adicionar campos `subtitle`, `year` e `updated_at` no modelo `Book` e `updated_at` no modelo `Chapter` em `backend/app/models/book.py` e `backend/app/models/chapter.py`
- [X] T004 Criar e registrar migração incremental do Alembic `0002_add_book_metadata_and_concurrency.py` em `backend/migrations/versions/`
- [X] T005 [P] Implementar utilitário de validação de concorrência otimista (`check_optimistic_lock`) em `backend/app/services/persistence.py`
- [X] T006 [P] Atualizar interfaces TypeScript (`Book`, `Chapter`, `Study`) com novos metadados e `updated_at` em `frontend/src/types.ts`

**Checkpoint**: Fundação de dados e concorrência pronta — implementação das histórias de usuário desbloqueada.

---

## Phase 3: User Story 1 - Edição de Metadados de Livros (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor edite título (obrigatório), autor, subtítulo e ano de publicação (opcionais) de qualquer livro, com concorrência otimista e preservação de capítulos e estudos.

**Independent Test**: Abrir detalhes de um livro existente com capítulos e estudos em base temporária, alterar título/autor/subtítulo/ano, salvar e comprovar persistência e integridade sem perda de vínculos.

### Tests for User Story 1
> **Escrever os testes antes da implementação e garantir que falhem.**

- [X] T007 [P] [US1] Implementar testes de integração para `PATCH /api/books/{id}` (sucesso, validações de título/ano e conflito 409) em `backend/tests/test_edit_acervo.py`

### Implementation for User Story 1

- [X] T008 [US1] Implementar endpoint `PATCH /books/{book_id}` com validação e concorrência otimista em `backend/app/routers/books.py`
- [X] T009 [P] [US1] Adicionar método `updateBook` no cliente de API frontend em `frontend/src/services/api.ts`
- [X] T010 [US1] Criar componente modal `BookEditModal.vue` com validação e acessibilidade por teclado em `frontend/src/components/BookEditModal.vue`
- [X] T011 [US1] Integrar botão "Editar livro" e acionamento do modal na visualização `BookView.vue` em `frontend/src/views/BookView.vue`

**Checkpoint**: User Story 1 funcional e testável de forma 100% independente (MVP alcançado).


---

## Phase 4: User Story 2 - Edição e Reordenação de Capítulos (Priority: P2)

**Goal**: Permitir renomear capítulos e reordenar a sequência de exibição através dos botões subir/descer (▲ / ▼), de forma atômica e transacional.

**Independent Test**: Criar livro com 3 capítulos, renomear um capítulo e mover outro para cima, comprovando que a lista reflete a nova ordem e nome sem órfãos nem duplicidades.

### Tests for User Story 2

- [X] T012 [P] [US2] Implementar testes para `PATCH /api/books/{id}/chapters/{id}` e `POST /api/books/{id}/chapters/{id}/move` em `backend/tests/test_edit_acervo.py`

### Implementation for User Story 2

- [X] T013 [US2] Implementar endpoint de renomeação `PATCH /books/{book_id}/chapters/{chapter_id}` em `backend/app/routers/chapters.py`
- [X] T014 [US2] Implementar endpoint de reordenação atômica `POST /books/{book_id}/chapters/{chapter_id}/move` em `backend/app/routers/chapters.py`
- [X] T015 [P] [US2] Adicionar métodos `updateChapter` e `moveChapter` no cliente de API frontend em `frontend/src/services/api.ts`
- [X] T016 [US2] Adicionar botões de movimentação (▲ / ▼) e ação de renomear capítulos em `frontend/src/views/BookView.vue`

**Checkpoint**: User Stories 1 e 2 plenamente operacionais e integradas.


---

## Phase 5: User Story 3 - Edição e Refinamento de Estudos e Anotações (Priority: P3)

**Goal**: Refinar o fluxo de edição de estudos garantindo proteção contra perda de dados em concorrência (HTTP 409) e imutabilidade total da resposta de origem.

**Independent Test**: Editar anotações e seções analíticas de um estudo existente, simular conflito concorrente de versão com 409 e verificar que o texto digitado permanece preservado na tela.

### Tests for User Story 3

- [X] T017 [P] [US3] Implementar testes de concorrência e preservação de `source_response` em `backend/tests/test_edit_acervo.py`

### Implementation for User Story 3

- [X] T018 [US3] Atualizar endpoint `PATCH /studies/{study_id}` em `backend/app/routers/studies.py` para suportar verificação de `expected_updated_at`
- [X] T019 [US3] Atualizar `StudyEditView.vue` para enviar `expected_updated_at`, tratar erro 409 e exibir banner de aviso com preservação do formulário em `frontend/src/views/StudyEditView.vue`

**Checkpoint**: Todas as três histórias de usuário implementadas e validadas.


---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada, build do frontend, suíte de regressão e documentação.

- [X] T020 Executar validação completa dos cenários de `specs/002-edicao-livros-estudos/quickstart.md`
- [X] T021 [P] Recompilar o frontend com `npm run build` e executar suíte de testes em `frontend/`
- [X] T022 [P] Atualizar registros de evidências e histórico em `docs/contexto/RETOMADA.md`

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Phase 1 (Setup)**: Pode iniciar imediatamente.
2. **Phase 2 (Foundational)**: Depende da Phase 1. Bloqueia todas as histórias de usuário.
3. **Phase 3 (User Story 1 - MVP)**: Depende da Phase 2. Entrega a edição de livros (valor central imediato).
4. **Phase 4 (User Story 2)**: Depende da Phase 2. Pode ser executada sequencialmente após US1.
5. **Phase 5 (User Story 3)**: Depende da Phase 2. Refina a edição de estudos existente com concorrência.
6. **Phase 6 (Polish)**: Depende da conclusão de todas as histórias desejadas.

### Parallel Opportunities

- **Setup**: T001 e T002 podem rodar em paralelo.
- **Foundational**: T005 e T006 podem rodar em paralelo com T003/T004.
- **US1 Tests**: T007 pode ser implementado antes de T008.
- **US1 Frontend**: T009 e T010 podem ser implementados em paralelo antes de T011.
- **US2 Tests**: T012 pode ser implementado antes de T013/T014.
- **Polish**: T021 e T022 podem rodar em paralelo após T020.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Executar Phase 1 (Setup) e Phase 2 (Foundational).
2. Executar Phase 3 (User Story 1 - Edição de metadados de livros).
3. Validar MVP isoladamente: comprovar que livros são editados e persistem com novos metadados sem quebrar capítulos.

### Incremental Delivery
- Incremento 1: Fundação + Edição de Livros (US1).
- Incremento 2: Edição e Reordenação de Capítulos (US2).
- Incremento 3: Blindagem de Concorrência em Estudos (US3).
- Validação Final: Build de produção, suíte completa de testes e registro em RETOMADA.md.
