# Tasks: F0.6.7 — Normalização e Simplificação de Categorias

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/categories-api.yaml](./contracts/categories-api.yaml)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura base, catálogo canônico declarativo e schemas de dados

- [x] T001 Criar catálogo inicial declarativo das categorias canônicas em `caderno-leitura-0.1/backend/app/services/canonical_categories.py`
- [x] T002 [P] Criar schemas Pydantic de entrada, saída, sugestão e estatísticas em `caderno-leitura-0.1/backend/app/schemas/category.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Normalizador gramatical, modelo de taxonomia plana e migração distributiva

- [x] T003 Implementar módulo de normalização gramatical e singularização em `caderno-leitura-0.1/backend/app/services/category_normalizer.py`
- [x] T004 [P] Atualizar modelo SQLAlchemy `Category` em `caderno-leitura-0.1/backend/app/models/category.py` com campos `normalized_name`, `is_canonical` e taxonomia plana
- [x] T005 Criar migração Alembic incremental `caderno-leitura-0.1/backend/migrations/versions/0023_normalize_categories.py` com suporte à atribuição distributiva e consolidação em `book_categories`
- [x] T006 [P] Criar suíte de testes de integração e isolamento em `caderno-leitura-0.1/backend/tests/test_category_normalization.py`

**Checkpoint**: Fundação pronta — modelo, migração e regras gramaticais testadas em ambiente isolado.

---

## Phase 3: User Story 1 - Catálogo Canônico e Navegação Limpa do Acervo (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor visualize o acervo organizado por categorias curtas, canônicas e em forma singular, sem perda de vínculos de livros existentes.

**Independent Test**: Executar `pytest backend/tests/test_category_normalization.py -k "test_distributive_category_migration"` e verificar que livros herdaram as categorias canônicas correspondentes sem quebras no acervo.

- [x] T007 [P] [US1] Implementar métodos de consulta, ordenação alfabética e listagem canônica plana em `caderno-leitura-0.1/backend/app/services/category_service.py`
- [x] T008 [US1] Atualizar endpoints `GET /api/categories` com contagem de livros associados em `caderno-leitura-0.1/backend/app/routers/categories.py`
- [x] T009 [P] [US1] Criar cliente de API para categorias no frontend em `caderno-leitura-0.1/frontend/src/api/categories.ts`
- [x] T010 [US1] Atualizar visualização do catálogo e filtros de livros na biblioteca em `caderno-leitura-0.1/frontend/src/views/BooksView.vue`
- [x] T011 [US1] Atualizar exibição de badges canônicas na página de detalhes do livro em `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [x] T012 [P] [US1] Criar testes automatizados para listagem e filtragem canônica em `caderno-leitura-0.1/frontend/tests/category_filter.test.mjs`

**Checkpoint**: User Story 1 funcional e testável de forma independente — navegação e filtros do acervo totalmente normalizados.

---

## Phase 4: User Story 2 - Categorização e Criação Guiada por Regras Canônicas (Priority: P2)

**Goal**: Guiar e validar a entrada do leitor ao cadastrar ou editar livros com sugestões em tempo real e normalização assistida de termos.

**Independent Test**: Executar `pytest backend/tests/test_category_normalization.py -k "test_suggest_and_create_canonical_category"` e verificar que plurais como "Filosofias" sugerem "Filosofia".

- [x] T013 [P] [US2] Implementar endpoint de sugestão e autocompletar `GET /api/categories/suggest` em `caderno-leitura-0.1/backend/app/routers/categories.py`
- [x] T014 [US2] Implementar criação e validação de categorias no endpoint `POST /api/categories` com detecção de identidade canônica em `caderno-leitura-0.1/backend/app/services/category_service.py`
- [x] T015 [P] [US2] Criar componente reutilizável `CategoryInput.vue` com autocompletar e sugestão transparente em `caderno-leitura-0.1/frontend/src/components/CategoryInput.vue`
- [x] T016 [US2] Integrar `CategoryInput.vue` no modal de edição/cadastro de livros em `caderno-leitura-0.1/frontend/src/components/BookEditModal.vue`
- [x] T017 [P] [US2] Adicionar testes unitários para o componente de entrada assistida em `caderno-leitura-0.1/frontend/tests/category_input.test.mjs`

**Checkpoint**: User Stories 1 e 2 funcionais — edição e criação de categorias protegidas contra regressão taxonômica.

---

## Phase 5: User Story 3 - Painel e Relatório de Conformidade Taxonômica (Priority: P3)

**Goal**: Permitir que o gestor do acervo consulte estatísticas consolidadas e audite a saúde da taxonomia canônica.

**Independent Test**: Consultar `GET /api/categories/stats` e validar contagem consolidada de termos, livros associados e ausência de inconsistências.

- [x] T018 [P] [US3] Implementar endpoint de métricas de conformidade `GET /api/categories/stats` em `caderno-leitura-0.1/backend/app/routers/categories.py`
- [x] T019 [US3] Adicionar card de resumo taxonômico e métricas de categorias no painel administrativo em `caderno-leitura-0.1/frontend/src/views/AdminView.vue`
- [x] T020 [P] [US3] Criar testes de integração para o endpoint de estatísticas em `caderno-leitura-0.1/backend/tests/test_category_normalization.py`

**Checkpoint**: Todas as histórias de usuário implementadas e verificáveis.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de integridade, testes de regressão e compilação de produção

- [x] T021 [P] Atualizar rotina de inspeção de integridade taxonômica na CLI de manutenção em `caderno-leitura-0.1/backend/app/services/maintenance.py`
- [x] T022 Validar todos os cenários do guia `quickstart.md` em `caderno-leitura-0.1/backend/tests/test_category_normalization.py`
- [x] T023 [P] Executar suíte completa de testes do backend (`.venv\Scripts\python.exe -m pytest tests/`)
- [x] T024 [P] Executar suíte de testes do frontend e build de produção (`npm test` e `npm run build`)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA todas as histórias de usuário.
- **User Story 1 (Phase 3 - MVP)**: Depende da Phase 2 — Base para a navegação do acervo.
- **User Story 2 (Phase 4)**: Depende da Phase 2 — Integra com o catálogo da US1.
- **User Story 3 (Phase 5)**: Depende da Phase 2 — Relatórios e governança.
- **Polish (Phase 6)**: Depende da conclusão das histórias desejadas.

### Parallel Opportunities
- T001 e T002 podem rodar em paralelo.
- T004 e T006 podem ser preparados em paralelo à T003.
- T007 e T009 podem ser iniciados em paralelo.
- T013 e T015 podem ser desenvolvidos em paralelo.
- T023 e T024 rodam em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 — MVP).
3. **Validar e Homologar**: O acervo deve refletir a taxonomia canônica sem perda de livros.

### Incremental Delivery
1. Setup + Foundational $\rightarrow$ Infraestrutura validada.
2. User Story 1 $\rightarrow$ Acervo navegável e limpo (MVP).
3. User Story 2 $\rightarrow$ Formulários assistidos com autocompletar.
4. User Story 3 $\rightarrow$ Governança taxonômica no painel.
5. Polish $\rightarrow$ Regressão geral, build e homologação.
