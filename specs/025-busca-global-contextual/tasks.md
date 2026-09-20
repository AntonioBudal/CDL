# Tasks: F08 — Busca Global Contextual

**Feature Branch**: `025-busca-global-contextual`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Implementation Plan**: [plan.md](./plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação de funções de banco compartilhadas, schemas Pydantic, tipagens TypeScript e cliente de API.

- [X] T001 [P] Registrar UDF unaccent de normalização Unicode na conexão SQLite em caderno-leitura-0.1/backend/app/db/session.py
- [X] T002 [P] Criar schemas Pydantic v2 SearchMatchItem, SearchResponse, SearchHistoryItem e SearchHistoryResponse em caderno-leitura-0.1/backend/app/schemas/search.py
- [X] T003 [P] Definir e exportar tipagens TypeScript SearchMatchItem, SearchResponse, SearchHistoryItem e SearchHistoryResponse em caderno-leitura-0.1/frontend/src/types.ts
- [X] T004 [P] Atualizar cliente HTTP com métodos searchStudies, getSearchHistory, deleteSearchHistoryItem e clearSearchHistory em caderno-leitura-0.1/frontend/src/services/api.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de banco de dados, migração Alembic, serviço de busca transversal e rotas REST no backend.

- [X] T005 Criar modelo declarativo SQLAlchemy SearchHistory com colunas id, query, created_at e updated_at em caderno-leitura-0.1/backend/app/models/search_history.py e registrar em caderno-leitura-0.1/backend/app/models/__init__.py
- [X] T006 Criar migração Alembic reversível 0010_add_search_history.py para a tabela search_history em caderno-leitura-0.1/backend/migrations/versions/0010_add_search_history.py
- [X] T007 Implementar serviço SearchService com suporte a UDF unaccent, busca multi-campo, combinação AND/OR, geração de snippets sanitizados com mark e isolamento de soft delete em caderno-leitura-0.1/backend/app/services/search_service.py
- [X] T008 Criar router REST /api/search e /api/search/history em caderno-leitura-0.1/backend/app/routers/search.py e registrar em caderno-leitura-0.1/backend/app/main.py
- [X] T009 [P] Criar suíte de testes de integração automatizados para busca transversal, snippets e soft delete em caderno-leitura-0.1/backend/tests/test_search_api.py

**Checkpoint**: Backend unificado, testado e respondendo consultas com insensibilidade a acentos, snippets destacados e exclusão de soft delete em < 200ms.

---

## Phase 3: User Story 1 - Busca Transversal Instantânea e Navegação com Contexto (Priority: P1) [MVP]

**Goal**: Permitir ao leitor abrir a busca a partir de qualquer tela, digitar um termo ou conceito e visualizar resultados de estudos com trechos destacados e navegação direta de 1 clique.

**Independent Test**: Acionar a busca; digitar um termo presente em múltiplos estudos; constatar os resultados com o nome da obra, capítulo, título do estudo e snippet com a palavra realçada; clicar no resultado e verificar a navegação para o estudo em foco.

### Implementation for User Story 1

- [X] T010 [US1] Implementar composable useGlobalSearch com debounce de 250ms, estado reativo de busca e navegação para /books/{book_id}?study={study_id} em caderno-leitura-0.1/frontend/src/composables/useGlobalSearch.ts
- [X] T011 [P] [US1] Criar componente SearchResultItem com trilha do livro (Livro > Capítulo > Estudo), badge de status de leitura e snippet sanitizado com mark em caderno-leitura-0.1/frontend/src/components/search/SearchResultItem.vue
- [X] T012 [US1] Criar componente GlobalSearchModal com input de busca, lista de resultados, estados de carregamento e estado vazio amigável em caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue
- [X] T013 [US1] Integrar botão de busca rápida na barra superior global e montagem do GlobalSearchModal em caderno-leitura-0.1/frontend/src/App.vue
- [X] T014 [P] [US1] Criar testes unitários para o fluxo de busca, renderização de snippets e navegação de 1 clique em caderno-leitura-0.1/frontend/tests/global-search.test.mjs

**Checkpoint**: MVP da Busca Global 100% funcional e operando ponta a ponta com navegação de 1 clique.

---

## Phase 4: User Story 2 - Filtragem Contextual por Obra e Categoria Taxonômica (Priority: P2)

**Goal**: Permitir ao leitor filtrar os resultados por livro específico ou categoria temática da taxonomia, além de alternar entre modo estrito (AND) e modo abrangente (OR assistido).

**Independent Test**: Realizar uma busca ampla; aplicar o filtro de uma obra ou categoria; constatar a restrição imediata dos resultados ao contexto selecionado; testar a sugestão de modo OR quando AND não encontrar ocorrências.

### Implementation for User Story 2

- [X] T015 [US2] Adicionar seletores de filtro por Livro e Categoria taxonômica e controle de modo AND/OR assistido com botão de limpar filtros em caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue
- [X] T016 [P] [US2] Implementar testes de integração para filtragem por book_id, category_id e modo disjuntivo assistido (suggest_or) em caderno-leitura-0.1/backend/tests/test_search_api.py

**Checkpoint**: Busca refinada por contexto de leitura e taxonomia operacional.

---

## Phase 5: User Story 3 - Histórico Recente de Pesquisas Persistido (Priority: P3)

**Goal**: Persistir as pesquisas recentes no backend (SQLite) com retenção dos 10 termos mais recentes, sincronização em rede local e descarte atômico (unitário ou total).

**Independent Test**: Realizar buscas com termos diferentes; verificar a listagem ao reabrir a busca com campo vazio; testar a execução ao clicar no termo; testar a exclusão de um termo específico e a limpeza completa.

### Implementation for User Story 3

- [X] T017 [US3] Implementar métodos record_search_query, get_recent_searches, delete_search_query e clear_all_searches com retenção dos 10 mais recentes em caderno-leitura-0.1/backend/app/services/search_service.py
- [X] T018 [P] [US3] Criar componente SearchHistoryList para exibição dos termos recentes quando o campo de busca estiver vazio, com botões para exclusão unitária e limpeza total em caderno-leitura-0.1/frontend/src/components/search/SearchHistoryList.vue
- [X] T019 [US3] Integrar SearchHistoryList dentro de GlobalSearchModal com execução instantânea ao clicar no termo em caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue
- [X] T020 [P] [US3] Implementar testes automatizados para o ciclo de vida do histórico de buscas no backend em caderno-leitura-0.1/backend/tests/test_search_api.py

**Checkpoint**: Histórico recente persistido e sincronizado, pronto para integração futura com conta Google.

---

## Phase 6: User Story 4 - Ergonomia Móvel, Acessibilidade e Navegação Ágil por Teclado (Priority: P4)

**Goal**: Assegurar atalhos de teclado (Ctrl+K / /), captura de foco acessível, navegação por setas, overlay em tela cheia mobile (<768px), alvos táteis mínimos de 44x44px e contenção de overflow lateral.

**Independent Test**: Pressionar Ctrl+K no teclado e constatar o foco no input; navegar com setas e fechar com Esc; emular smartphone e verificar o layout em tela cheia, alvos ≥ 44px e ausência de rolagem horizontal.

### Implementation for User Story 4

- [X] T021 [US4] Implementar atalho global de teclado (Ctrl+K e /), captura de foco (focus trap), navegação por setas (cima/baixo) e fechamento via tecla Esc em caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue
- [X] T022 [US4] Implementar adaptação para dispositivos móveis (<768px): overlay em tela cheia, alvos táteis mínimos de 44x44px e contenção overflow-x: hidden em caderno-leitura-0.1/frontend/src/components/search/GlobalSearchModal.vue
- [X] T023 [P] [US4] Criar testes automatizados de ergonomia móvel, foco, teclado e acessibilidade WAI-ARIA em caderno-leitura-0.1/frontend/tests/global-search-a11y.test.mjs

**Checkpoint**: Experiência de busca ágil, acessível e confortável em desktop e smartphones.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação rigorosa de regressão, compilação de produção e homologação final.

- [X] T024 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T025 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T026 Atualizar guia de validação executável e registrar evidências finais em specs/025-busca-global-contextual/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T004)
        │
        ▼
Phase 2: Foundational (T005-T009)
        │
        ├────────────────────────────────┐
        ▼                                ▼
Phase 3: User Story 1 (T010-T014)  [MVP]  (Busca Transversal, Snippets e Navegação Direta)
        │
        ▼
Phase 4: User Story 2 (T015-T016)         (Filtros por Livro/Categoria e Modo AND/OR)
        │
        ▼
Phase 5: User Story 3 (T017-T020)         (Histórico Recente Persistido no Backend)
        │
        ▼
Phase 6: User Story 4 (T021-T023)         (Ergonomia Móvel, Acessibilidade e Teclado)
        │
        ▼
Phase 7: Polish (T024-T026)               (Regressão completa, build Vite e validação)
```

### Parallel Opportunities

- **Phase 1**: T001, T002, T003 e T004 podem ser executadas em paralelo.
- **Phase 2**: T009 (testes de integração) pode ser desenvolvido em paralelo com T007 e T008.
- **Phase 3**: T011 (SearchResultItem) e T014 (testes unitários) podem rodar em paralelo com T010 e T012.
- **Phase 4**: T015 (frontend) e T016 (testes backend) podem rodar em paralelo.
- **Phase 5**: T018 (SearchHistoryList) e T020 (testes backend) podem rodar em paralelo.
- **Phase 6**: T021 (atalhos) e T023 (testes acessibilidade) podem rodar em paralelo.
- **Phase 7**: T024 (regressão backend) e T025 (regressão frontend + build Vite) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T004) e Foundational (T005-T009).
2. Implementar User Story 1 (T010-T014).
3. **Validar MVP**: O leitor já possui a busca transversal ativa no cabeçalho com realce de termos e navegação de 1 clique para o estudo.

### Incremental Delivery
- US2 adiciona filtros contextuais por obra e categoria e modo AND/OR.
- US3 adiciona histórico recente persistido no SQLite e preparado para sincronização.
- US4 adiciona atalhos de teclado (`Ctrl+K`), navegação por setas, foco acessível e overlay responsivo para smartphones.
- Phase 7 garante 100% de integridade com zero regressões no sistema.
