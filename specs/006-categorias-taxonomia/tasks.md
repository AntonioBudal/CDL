# Tasks: Categorias e Taxonomia de Livros (T05)

**Feature**: `006-categorias-taxonomia` | **Branch**: `006-categorias-taxonomia`  
**Input**: Design artifacts from `/specs/006-categorias-taxonomia/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`)

---

## Phase 1: Setup & Data Infrastructure

**Purpose**: Estruturação inicial do catálogo canônico e contratos de tipos no backend e frontend.

- [X] T001 Criar arquivo de catálogo canônico com mais de 100 categorias em `backend/app/data/canonical_categories.json`
- [X] T002 [P] Implementar schemas Pydantic de categorias (`CategoryRead`, `CategoryTree`) em `backend/app/schemas/category.py`
- [X] T003 [P] Adicionar tipos TypeScript de categorias e estender `Book`, `BookPatch`, `LibraryFilterState` em `frontend/src/types.ts`

---

## Phase 2: Foundational (Model, Migração e Validação de Taxonomia)

**Purpose**: Persistência relacional em SQLite, migração Alembic e serviço de validação algorítmica da árvore taxonômica.

**⚠️ CRITICAL**: Pré-requisito bloqueante para todas as user stories.

- [X] T004 Implementar modelo SQLAlchemy `Category` e tabela associativa `book_categories` em `backend/app/models/category.py`
- [X] T005 Atualizar relacionamentos no modelo `Book` e exportações de modelos em `backend/app/models/book.py` e `backend/app/models/__init__.py`
- [X] T006 Criar migração incremental Alembic para as tabelas `categories` e `book_categories` em `backend/migrations/versions/0005_add_categories_and_taxonomy.py`
- [X] T007 Implementar serviço de validação de catálogo (sem ciclos, IDs únicos, parentesco) e sincronização idempotente em `backend/app/services/category_service.py`
- [X] T008 [P] Criar testes automatizados de integridade do catálogo canônico e idempotência de carga em `backend/tests/test_categories.py`

**Checkpoint**: Fundação de dados completa — tabelas, catálogo e serviço de validação operacionais.

---

## Phase 3: User Story 1 - Atribuição e Gestão de Categorias em Livros (Priority: P1) 🎯 MVP

**Goal**: Permitir associar múltiplas categorias canônicas a um livro no cadastro/edição, com persistência relacional N:N e preservação integral em edições parciais.

**Independent Test**: Abrir o modal de edição de um livro, associar duas categorias ("Literatura Brasileira" e "Ficção"), salvar e verificar que as etiquetas aparecem na estante e na ficha do livro, permanecendo intactas após editar outros campos ou recarregar a página.

### Implementation for User Story 1
- [X] T009 [P] [US1] Atualizar schemas `BookCreate`, `BookPatch` e `BookRead` com `category_ids` e `categories` em `backend/app/schemas/book.py`
- [X] T010 [US1] Atualizar rotas de criação, consulta e atualização parcial com sincronização de categorias em `backend/app/routers/books.py`
- [X] T011 [P] [US1] Criar componente visual de etiqueta `CategoryBadge.vue` com suporte a remoção em `frontend/src/components/CategoryBadge.vue`
- [X] T012 [US1] Integrar gestão e seleção de categorias no modal de livro em `frontend/src/components/BookEditModal.vue`
- [X] T013 [P] [US1] Exibir etiquetas de categorias nos cartões da estante e na ficha da obra em `frontend/src/views/BooksView.vue` e `frontend/src/views/BookView.vue`
- [X] T014 [US1] Escrever testes de integração para criação, edição e preservação de categorias em edições parciais em `backend/tests/test_categories.py`

**Checkpoint**: User Story 1 (MVP) concluída — livros possuem categorias associadas, editáveis e visualizáveis.

---

## Phase 4: User Story 2 - Busca Preditiva de Categorias com Caminho Hierárquico (Priority: P2)

**Goal**: Permitir que o usuário busque categorias digitando termos no seletor com autocomplete instantâneo e exibição da trilha hierárquica completa.

**Independent Test**: Digitar termos como "ética", "brasil" ou "computacao" no seletor de categorias do modal e verificar que as sugestões exibem a linhagem hierárquica (ex.: "Ciências Humanas / Filosofia / Ética") de forma insensível a acentos e maiúsculas.

### Implementation for User Story 2
- [X] T015 [P] [US2] Criar rota `GET /api/categories` com parâmetro de busca opcional em `backend/app/routers/categories.py` e registrar em `backend/app/main.py`
- [X] T016 [P] [US2] Adicionar métodos de API para listagem e busca de categorias em `frontend/src/api.ts`
- [X] T017 [US2] Criar composable `useCategories.ts` com cache local, normalização Unicode e busca preditiva em `frontend/src/composables/useCategories.ts`
- [X] T018 [US2] Criar componente `CategorySelector.vue` com autocomplete, navegação por teclado e trilha hierárquica em `frontend/src/components/CategorySelector.vue`
- [X] T019 [P] [US2] Escrever testes unitários do composable e autocomplete de categorias em `frontend/tests/categories.test.mjs`

**Checkpoint**: User Story 2 concluída — busca preditiva rápida e seleção assistida de categorias disponíveis.

---

## Phase 5: User Story 3 - Catálogo Canônico e Ciclo de Vida do Acervo (Priority: P3)

**Goal**: Garantir a carga automática do catálogo no startup do sistema e o isolamento seguro da taxonomia frente a ações de lixeira e exclusão definitiva.

**Independent Test**: Enviar um livro categorizado para a lixeira, comprovar que as categorias são mantidas na restauração e que a exclusão definitiva remove apenas os vínculos em `book_categories` sem tocar no catálogo geral.

### Implementation for User Story 3
- [X] T020 [US3] Integrar rotina `sync_canonical_categories` no ciclo de vida (lifespan) de inicialização em `backend/app/main.py`
- [X] T021 [US3] Escrever testes de integração para ciclo de vida com lixeira (soft delete) e exclusão definitiva em `backend/tests/test_categories.py`

**Checkpoint**: User Story 3 concluída — catálogo inicializa automaticamente e ciclo de vida da lixeira preserva a integridade.

---

## Phase 6: User Story 4 - Filtragem do Acervo por Categorias e Subcategorias Recursivas (Priority: P4)

**Goal**: Permitir filtrar os livros do acervo por categoria com resolução recursiva: selecionar uma categoria pai exibe todos os livros vinculados a ela e a qualquer uma de suas subcategorias descendentes.

**Independent Test**: Selecionar a categoria pai "Filosofia" no filtro da estante e verificar que livros associados a "Filosofia / Ética" ou "Filosofia / Epistemologia" aparecem no resultado, combináveis com busca textual e ordenação.

### Implementation for User Story 4
- [X] T022 [US4] Implementar resolução de subcategorias via CTE recursiva e filtro `?category=` em `backend/app/services/category_service.py` e `backend/app/routers/books.py`
- [X] T023 [P] [US4] Atualizar composable `useLibraryFilter.ts` com suporte a filtro recursivo de categoria em `frontend/src/composables/useLibraryFilter.ts`
- [X] T024 [US4] Integrar seletor de categorias e contagem dinâmica na barra de ferramentas do acervo em `frontend/src/components/LibraryToolbar.vue`
- [X] T025 [P] [US4] Escrever testes de filtro recursivo no backend em `backend/tests/test_categories.py` e no frontend em `frontend/tests/library-filter.test.mjs`

**Checkpoint**: User Story 4 concluída — estante filtra livros por categoria de forma recursiva e integrada à busca textual.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação integrada, validação de regras da constituição e homologação de build de produção.

- [X] T026 [P] Executar validação prática de ponta a ponta conforme o roteiro em `specs/006-categorias-taxonomia/quickstart.md`
- [X] T027 [P] Executar suíte completa de testes de regressão do backend em `backend/tests/`
- [X] T028 Validar compilação estrita de tipos e build estático de produção (`vue-tsc -b && vite build`) em `frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Sem dependências — execução imediata.
- **Phase 2 (Foundational)**: Depende de Phase 1. Bloqueia todas as User Stories.
- **Phase 3 (US1 - MVP)**: Depende de Phase 2. Entrega mínima viável de associação de categorias.
- **Phase 4 (US2 - Busca Preditiva)**: Depende de Phase 2 e integra com o modal de US1.
- **Phase 5 (US3 - Catálogo e Ciclo de Vida)**: Depende de Phase 2 e Phase 3.
- **Phase 6 (US4 - Filtro Recursivo)**: Depende de Phase 2, Phase 3 e Phase 4.
- **Phase 7 (Polish)**: Depende da conclusão de todas as fases anteriores.

### Parallel Opportunities
- Tarefas marcadas com `[P]` em arquivos distintos podem ser implementadas em paralelo:
  - T002 e T003 (schemas Pydantic e tipos TypeScript).
  - T009 e T011 (schemas de livros e componente visual de badge).
  - T015 e T016 (router backend de categorias e cliente frontend).
  - T023 e T025 (atualização do composable do frontend e testes do backend).
  - T026 e T027 (execução de testes de regressão e validação quickstart).

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Setup (T001 a T003) e Fundação (T004 a T008).
2. Implementar User Story 1 (T009 a T014).
3. **Validar MVP**: Cadastrar livro com categorias e verificar persistência.

### Entrega Incremental
1. Setup + Fundação: Banco, migração e taxonomia carregados.
2. User Story 1: Livros associados a múltiplas categorias (MVP funcional).
3. User Story 2: Seletor com busca preditiva e trilha hierárquica.
4. User Story 3: Carga automática no lifespan e isolamento da lixeira.
5. User Story 4: Filtragem inclusiva/recursiva na estante do acervo.
6. Polish: Validação integrada e build de produção.
