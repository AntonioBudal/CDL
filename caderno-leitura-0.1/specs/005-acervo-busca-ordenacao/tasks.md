# Tasks: Acervo — Visualização, Busca e Ordenação

**Branch**: `005-acervo-busca-ordenacao` | **Date**: 2026-09-18 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Shared Types & Test Skeletons)

**Purpose**: Definições de tipos compartilhados e arquivos de teste para a feature de busca, ordenação e visualização do acervo.

- [X] T001 Declarar e exportar os tipos `LibraryViewMode`, `BookSortOption` e `LibraryFilterState` em `frontend/src/types.ts`
- [X] T002 [P] Criar o esqueleto da suíte de testes unitários do filtro em `frontend/tests/library-filter.test.mjs`
- [X] T003 [P] Criar o esqueleto de testes de integração de busca e ordenação em `backend/tests/test_books_search_and_sort.py`

---

## Phase 2: Foundational (Backend Query Support & Base Filter Composable)

**Purpose**: Infraestrutura básica no backend e composable base no frontend que sustentam todas as histórias de usuário.

**CRITICAL**: As histórias de usuário dependem do suporte de busca/ordenação na API e da lógica base do composable.

- [X] T004 Atualizar a rota `GET /api/books` em `backend/app/routers/books.py` para aceitar parâmetros opcionais de consulta `q`, `sort` e `order`, preservando o isolamento de itens da lixeira (`deleted_at IS NULL`)
- [X] T005 [P] Implementar testes automatizados para `GET /api/books` com `q`, `sort` e `order` em `backend/tests/test_books_search_and_sort.py`
- [X] T006 Criar a estrutura base do composable `useLibraryFilter.ts` com normalização de texto Unicode NFD em `frontend/src/composables/useLibraryFilter.ts`

**Checkpoint**: Base pronta — implementação das histórias de usuário pode prosseguir.

---

## Phase 3: User Story 1 - Busca Instantânea e Filtragem de Obras (Priority: P1) 🎯 MVP

**Goal**: Permitir ao leitor encontrar instantaneamente qualquer livro digitando termos de título, autor ou subtítulo, insensível a maiúsculas e acentuação, com contagem dinâmica e botão de limpeza.

**Independent Test**: Digitar termos de pesquisa (com ou sem acento, ex.: "memorias") no campo de busca e confirmar que a listagem filtra instantaneamente, atualiza a contagem e permite limpar o filtro.

### Tests for User Story 1
- [X] T007 [P] [US1] Adicionar testes unitários para normalização de acentos e busca por múltiplos tokens AND em `frontend/tests/library-filter.test.mjs`

### Implementation for User Story 1
- [X] T008 [US1] Implementar a função reativa de filtragem por tokens e cálculo de contagem em `frontend/src/composables/useLibraryFilter.ts`
- [X] T009 [US1] Criar o componente `LibraryToolbar.vue` com campo de busca acessível (`input type="search"`), indicador de contagem e botão de limpar em `frontend/src/components/LibraryToolbar.vue`
- [X] T010 [US1] Integrar o `LibraryToolbar` e o estado vazio específico de busca sem resultados em `frontend/src/views/BooksView.vue`

**Checkpoint**: User Story 1 funcional de forma independente (MVP do acervo navegável).

---

## Phase 4: User Story 2 - Modos de Visualização: Grade de Capas vs. Lista Compacta (Priority: P2)

**Goal**: Permitir ao leitor alternar entre a visão de Grade de Capas (proporção 2:3) e a Lista Compacta (linhas horizontais densas), persistindo a escolha no navegador.

**Independent Test**: Clicar nos botões de alternância de modo e conferir a renderização imediata da grade e da lista, recarregar a página e confirmar que a escolha persiste.

### Tests for User Story 2
- [X] T011 [P] [US2] Adicionar testes unitários para recuperação e persistência do modo de visualização no `localStorage` em `frontend/tests/library-filter.test.mjs`

### Implementation for User Story 2
- [X] T012 [US2] Implementar a reatividade de `viewMode` (`grid` | `list`) com sincronização com `localStorage` e `cadernoAppearance` em `frontend/src/composables/useLibraryFilter.ts`
- [X] T013 [US2] Adicionar botões segmentados acessíveis com `aria-pressed` para alternância Grade/Lista em `frontend/src/components/LibraryToolbar.vue`
- [X] T014 [US2] Implementar a renderização do layout de Lista Compacta (`.book-list-compact`) com miniatura de capa, metadados alinhados e link de navegação em `frontend/src/views/BooksView.vue`
- [X] T015 [US2] Adicionar regras de CSS para lista compacta, truncate de títulos longos e responsividade para telas móveis em `frontend/src/views/BooksView.vue`

**Checkpoint**: User Stories 1 e 2 funcionais e combinadas.

---

## Phase 5: User Story 3 - Ordenação Flexível do Acervo (Priority: P3)

**Goal**: Disponibilizar opções explícitas de ordenação por título (A–Z, Z–A), autor, recentemente adicionados (`created_at`), recentemente modificados (`updated_at`), mais antigos adicionados e ano de publicação, combinável com a busca.

**Independent Test**: Selecionar diferentes opções de ordenação e conferir o rearranjo imediato dos livros na grade e na lista, inclusive com filtros de busca ativos.

### Tests for User Story 3
- [X] T016 [P] [US3] Adicionar testes unitários para os comparadores de ordenação (alfabética pt-BR, timestamps e anos nulos) em `frontend/tests/library-filter.test.mjs`

### Implementation for User Story 3
- [X] T017 [US3] Implementar funções determinísticas de ordenação para todas as 7 opções e persistência da preferência em `frontend/src/composables/useLibraryFilter.ts`
- [X] T018 [US3] Adicionar o elemento `<select>` de ordenação com opções legíveis em português em `frontend/src/components/LibraryToolbar.vue`
- [X] T019 [US3] Conectar a ordenação reativa à lista de exibição de livros em `frontend/src/views/BooksView.vue`

**Checkpoint**: Todas as histórias de usuário implementadas e integradas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Garantir acessibilidade, robustez, integridade de testes e build de produção.

- [X] T020 [P] Implementar atalho de teclado `Escape` para limpar a busca e manter foco no campo de texto em `frontend/src/components/LibraryToolbar.vue`
- [X] T021 [P] Executar a suíte completa de testes do backend com isolamento em `backend/tests/`
- [X] T022 [P] Executar testes unitários do frontend (`node --test`) e typecheck estrito com `npm run build` em `frontend/`
- [X] T023 Validar manualmente todos os cenários do guia rápido de validação em `specs/005-acervo-busca-ordenacao/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão do Setup (Phase 1).
- **User Story 1 (Phase 3)**: Depende do Foundational (Phase 2).
- **User Story 2 (Phase 4)**: Depende do Foundational (Phase 2); integra-se com a barra de ferramentas de US1.
- **User Story 3 (Phase 5)**: Depende do Foundational (Phase 2); integra-se com a barra de ferramentas de US1.
- **Polish (Phase 6)**: Depende da conclusão das fases 3, 4 e 5.

---

## Parallel Opportunities

- `T002` e `T003` (esqueletos de testes frontend e backend) podem ser criados em paralelo.
- `T005` (testes backend) e `T006` (composable frontend) podem ser desenvolvidos em paralelo.
- `T007` (testes unitários de busca), `T011` (testes de persistência de visualização) e `T016` (testes de ordenação) podem rodar em paralelo em suas respectivas fases.
- `T020`, `T021` e `T022` da fase de Polish podem ser executados concorrentemente.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Phase 1: Setup (`T001` a `T003`)
2. Completar Phase 2: Foundational (`T004` a `T006`)
3. Completar Phase 3: User Story 1 (`T007` a `T010`)
4. **Validar MVP**: Buscar livros com e sem acentos, conferir contagem dinâmica e limpeza.

### Entrega Incremental
1. MVP entregue (busca instantânea ativa).
2. Adicionar Phase 4: Alternância entre Grade de Capas e Lista Compacta (`T011` a `T015`).
3. Adicionar Phase 5: Ordenação flexível completa (`T016` a `T019`).
4. Concluir Phase 6: Polish, validação e build (`T020` a `T023`).
