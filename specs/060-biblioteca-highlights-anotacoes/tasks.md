# Tasks: F0.7.11 — Biblioteca Transversal de Highlights e Anotações

**Input**: Design artifacts from `specs/060-biblioteca-highlights-anotacoes/`
**Feature Branch**: `060-biblioteca-highlights-anotacoes`
**Specification**: [spec.md](spec.md) | **Implementation Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura inicial de dados, migrações e contratos compartilhados

- [X] T001 Criar migração Alembic para índice de consulta `ix_study_highlights_user_kind_color` em `caderno-leitura-0.1/backend/migrations/versions/0025_add_highlight_library_index.py`
- [X] T002 [P] Definir tipos TypeScript para biblioteca de destaques e query params em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T003 [P] Definir esquemas Pydantic `HighlightLibraryItemRead` e `HighlightLibraryResponse` em `caderno-leitura-0.1/backend/app/schemas/study_highlight.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura básica no backend e roteamento que bloqueia todas as histórias de usuário

- [X] T004 Implementar função de consulta agregada `list_library_highlights` com join em `Study`, `Chapter`, `Book` e exclusão de deletados em `caderno-leitura-0.1/backend/app/services/study_highlight_service.py`
- [X] T005 Implementar endpoint consolidado `GET /api/highlights/library` com isolamento multiusuário em `caderno-leitura-0.1/backend/app/routers/study_highlights.py`
- [X] T006 [P] Adicionar método cliente `getHighlightLibrary` no cliente HTTP em `caderno-leitura-0.1/frontend/src/api.ts`
- [X] T007 [P] Registrar rota `/highlights` apontando para `HighlightsLibraryView.vue` em `caderno-leitura-0.1/frontend/src/router/index.ts`
- [X] T008 [P] Adicionar atalho de navegação "Destaques" no menu principal e cabeçalho em `caderno-leitura-0.1/frontend/src/components/layout/AppHeader.vue`

**Checkpoint**: Base de dados, API e roteamento prontos. Implementação das histórias pode começar.

---

## Phase 3: User Story 1 - Exploração Transversal e Busca Textual Instantânea (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor visualize todas as suas marcações em uma tela centralizada, filtre por busca textual instantânea e alterne entre os modos "Recentes" e "Por Obra".

**Independent Test**: Navegar para `/highlights`, verificar a renderização de todos os destaques do usuário com metadados de obra/capítulo, alternar o modo de visão e digitar termos na busca confirmando filtragem instantânea sem recarregamento.

### Tests for User Story 1

- [X] T009 [P] [US1] Criar testes de backend para `GET /api/highlights/library` validando junção de entidades, busca `q` e isolamento em `caderno-leitura-0.1/backend/tests/test_highlights_library.py`
- [X] T010 [P] [US1] Criar testes de frontend para renderização da visão, busca e alternância de modos de exibição em `caderno-leitura-0.1/frontend/tests/highlights_library_view.test.mjs`

### Implementation for User Story 1

- [X] T011 [US1] Implementar componente `HighlightCard.vue` com exibição de trecho, nota, badges de tipo/cor e títulos de livro/capítulo em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [X] T012 [US1] Implementar barra de ferramentas com campo de busca com debounce de 250ms e alternador de modo "Recentes" / "Por Obra" com persistência em localStorage em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`
- [X] T013 [US1] Implementar visão principal `HighlightsLibraryView.vue` integrando busca, esqueleto de loading, estados vazios acolhedores e listagem nos modos "Recentes" e "Por Obra" em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`

**Checkpoint**: User Story 1 (MVP) completamente funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Filtragem Multidimensional e Sincronização na URL (Priority: P2)

**Goal**: Permitir a combinação de filtros de Obra/Livro, Tipo e Cor, com paginação estruturada e sincronização com parâmetros de URL.

**Independent Test**: Selecionar combinações de filtros na barra superior, verificar restrição precisa dos cards, restaurar estado via URL recarregada e navegar entre páginas.

### Tests for User Story 2

- [X] T014 [P] [US2] Adicionar testes de backend para filtros combinados de `book_id`, `kind`, `color` e paginação em `caderno-leitura-0.1/backend/tests/test_highlights_library.py`
- [X] T015 [P] [US2] Adicionar testes de frontend para sincronização de filtros na URL e restauração de parâmetros em `caderno-leitura-0.1/frontend/tests/highlights_library_view.test.mjs`

### Implementation for User Story 2

- [X] T016 [US2] Implementar seletores de Livro, Tipo e Cor cromática com contadores dinâmicos na barra de ferramentas em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`
- [X] T017 [US2] Implementar sincronização bidirecional de filtros com query params da URL e botão "Limpar filtros" em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [X] T018 [US2] Implementar barra de paginação com navegação de páginas e indicador de total de itens em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma independente.

---

## Phase 5: User Story 3 - Salto Contextual com Retorno ao Estudo e Gestão Rápida In-Card (Priority: P3)

**Goal**: Oferecer edição rápida da nota pessoal e exclusão com confirmação diretamente no cartão, além de salto contextual para o estudo original com rolagem suave e pulso luminoso guia.

**Independent Test**: Editar uma nota e excluir um destaque diretamente pelo cartão da biblioteca; acionar "Abrir no Estudo" e verificar navegação direta para o estudo com âncora `#highlight-{id}`, scroll centralizado e pulso luminoso de 2 segundos no trecho.

### Tests for User Story 3

- [X] T019 [P] [US3] Adicionar testes de backend para garantia de integridade em mutações e exclusões diretas em `caderno-leitura-0.1/backend/tests/test_highlights_library.py`
- [X] T020 [P] [US3] Adicionar testes de frontend para edição rápida in-card, diálogo de exclusão e disparo de salto contextual em `caderno-leitura-0.1/frontend/tests/highlights_library_view.test.mjs`

### Implementation for User Story 3

- [X] T021 [US3] Implementar edição inline de anotação com botões Salvar/Cancelar e exclusão com diálogo de confirmação in-card em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [X] T022 [US3] Conectar eventos de edição e exclusão de cartões com a API e atualização reativa da lista em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [X] T023 [US3] Implementar botão "Abrir no Estudo" acionando navegação com hash `#highlight-{id}` em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [X] T024 [US3] Adicionar listener de âncora `#highlight-{id}` com scroll suave e animação CSS de pulso luminoso (`highlight-glow-pulse`) de 2 segundos em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Todas as 3 histórias de usuário concluídas e integradas com ciclo bidirecional completo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinamentos ergonômicos, acessibilidade móvel e validação estrita das suítes de teste

- [X] T025 [P] Implementar layout responsivo móvel com gaveta expansível de filtros e alvos táteis mínimos de 44x44px em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`
- [X] T026 Executar verificação de conformidade do Design System (ausência de emojis informais) em `caderno-leitura-0.1/frontend/tests/visual_system.test.mjs`
- [X] T027 Executar suíte completa de testes do frontend via `npm test` em `caderno-leitura-0.1/frontend`
- [X] T028 Executar compilação de produção e validação de tipos TypeScript via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T029 Executar suíte completa de testes do backend via `pytest` em `caderno-leitura-0.1/backend`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências externas — executa imediatamente.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA a implementação das histórias.
- **User Story 1 (Phase 3)**: Depende de Phase 2 — Entrega o MVP funcional.
- **User Story 2 (Phase 4)**: Depende de Phase 2 e estende a interface da Phase 3.
- **User Story 3 (Phase 5)**: Depende de Phase 2 e estende os cartões da Phase 3 / navegação do leitor.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

### User Story Dependencies

- **User Story 1 (P1)**: Autônoma após Foundational. Define a visão principal e exibição de cartões.
- **User Story 2 (P2)**: Conecta filtros multidimensionais e paginação na visão existente.
- **User Story 3 (P3)**: Adiciona mutações in-card e acoplamento com o leitor de estudo.

### Parallel Opportunities

- **Phase 1**: T002 (TypeScript) e T003 (Pydantic) podem rodar em paralelo.
- **Phase 2**: T006 (API client), T007 (Router) e T008 (Header) podem rodar em paralelo.
- **Phase 3**: T009 (Backend tests) e T010 (Frontend tests) podem rodar em paralelo antes da implementação.
- **Phase 4**: T014 (Backend filter tests) e T015 (Frontend URL tests) podem rodar em paralelo.
- **Phase 5**: T019 (Backend tests) e T020 (Frontend tests) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001–T003).
2. Completar Foundational (T004–T008).
3. Completar User Story 1 (T009–T013).
4. **Validar MVP**: Navegar em `/highlights`, verificar listagem, testar busca com debounce e alternar modos de visão.

### Incremental Delivery
1. Setup + Foundational -> Base de dados e rotas prontas.
2. User Story 1 -> MVP: visão agregada transversal pesquisável com modos Recentes / Por Obra.
3. User Story 2 -> Filtros multidimensionais (livro, tipo, cor), paginação e URL sincronizada.
4. User Story 3 -> Gestão rápida in-card e salto contextual com pulso luminoso no estudo.
5. Polish -> Mobile 44px, conformidade de Design System e suítes completas verdes.
