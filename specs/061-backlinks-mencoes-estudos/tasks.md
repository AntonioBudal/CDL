# Tasks: F0.7.12 — Backlinks e Menções entre Estudos

**Input**: Design artifacts from `specs/061-backlinks-mencoes-estudos/`
**Feature Branch**: `061-backlinks-mencoes-estudos`
**Specification**: [spec.md](spec.md) | **Implementation Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura inicial de dados, migrações e contratos compartilhados

- [X] T001 Criar migração Alembic para tabela `study_mentions` com chaves estrangeiras e índices em `caderno-leitura-0.1/backend/migrations/versions/0026_add_study_mentions_table.py`
- [X] T002 [P] Criar modelo SQLAlchemy `StudyMention` em `caderno-leitura-0.1/backend/app/models/study_mention.py` e registrar em `backend/app/models/__init__.py`
- [X] T003 [P] Definir tipos TypeScript para `BacklinkItem`, `BacklinksResponse` e `StudyCandidateOption` em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T004 [P] Definir esquemas Pydantic `BacklinkItemRead`, `BacklinksResponse` e `StudyCandidateOption` em `caderno-leitura-0.1/backend/app/schemas/study_mention.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura básica no backend e cliente HTTP que bloqueia todas as histórias de usuário

- [X] T005 Implementar serviço `study_mention_service.py` com extração de regex `[[...]]`, sincronização atômica e consulta de backlinks em `caderno-leitura-0.1/backend/app/services/study_mention_service.py`
- [X] T006 Conectar trigger de sincronização de menções nos endpoints de criação e edição de estudos em `caderno-leitura-0.1/backend/app/routers/studies.py`
- [X] T007 Implementar roteador `study_mentions.py` com endpoints `GET /api/studies/{study_id}/backlinks` e `GET /api/studies/search-candidates` em `caderno-leitura-0.1/backend/app/routers/study_mentions.py` e registrá-lo em `caderno-leitura-0.1/backend/app/main.py`
- [X] T008 [P] Adicionar métodos clientes `getStudyBacklinks` e `searchStudyCandidates` em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: Base de dados, serviços e contratos de API prontos. Implementação das histórias pode começar.

---

## Phase 3: User Story 1 - Autocomplete e Inserção de Menções no Editor de Estudo (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor digite `[[` em qualquer campo do editor de estudo para buscar e autocompletar menções a outros estudos do seu acervo.

**Independent Test**: Abrir o editor de estudo, posicionar o cursor em um campo analítico, digitar `[[`, verificar o surgimento do popover com sugestões filtradas por título, selecionar um item e confirmar a inserção do formato `[[Título]]` ou `[[Título|id]]`.

### Tests for User Story 1

- [X] T009 [P] [US1] Criar testes de backend para extração de menções `[[Título]]` e busca de estudos candidatos em `caderno-leitura-0.1/backend/tests/test_study_mentions.py`
- [X] T010 [P] [US1] Criar testes de frontend para autocomplete e inserção de menções em `caderno-leitura-0.1/frontend/tests/study_mentions.test.mjs`

### Implementation for User Story 1

- [X] T011 [US1] Implementar popover flutuante de autocomplete de menções disparado pelo prefixo `[[` com navegação por setas e Enter em `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`
- [X] T012 [US1] Conectar busca de candidatos com `searchStudyCandidates` e inserção determinística no texto (`[[Título]]` ou `[[Título|id]]`) em `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`

**Checkpoint**: User Story 1 (MVP) completamente funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Renderização de Links Internos e Navegação Direta no Leitor (Priority: P2)

**Goal**: Converter a sintaxe `[[...]]` em hiperlinks internos estilizados e navegáveis no leitor de markdown, permitindo explorar conexões diretamente no fluxo de leitura.

**Independent Test**: Visualizar um estudo contendo menções no leitor (`StudyView.vue`), verificar se os tokens são exibidos como links internos destacados e, ao clicar, navegar instantaneamente para o estudo referenciado sem recarregar a página.

### Tests for User Story 2

- [X] T013 [P] [US2] Adicionar testes de backend para integridade de links com estudos ativos e arquivados em `caderno-leitura-0.1/backend/tests/test_study_mentions.py`
- [X] T014 [P] [US2] Adicionar testes de frontend para parser e renderização de links `[[...]]` em `caderno-leitura-0.1/frontend/tests/study_mentions.test.mjs`

### Implementation for User Story 2

- [X] T015 [US2] Implementar parser e substituição de tokens `[[Título]]` e `[[Título|id]]` em tags `<a>` com classe `.study-internal-mention` e atributos `data-study-id` em `caderno-leitura-0.1/frontend/src/components/MarkdownContent.vue`
- [X] T016 [US2] Adicionar delegação de clique em `.study-internal-mention` com navegação SPA via `vue-router` e estilos visuais temáticos em `caderno-leitura-0.1/frontend/src/components/MarkdownContent.vue`

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma independente.

---

## Phase 5: User Story 3 - Painel Reverso de Backlinks no Rodapé da Coluna de Leitura (Priority: P3)

**Goal**: Exibir no rodapé da visualização de cada estudo uma seção com as referências reversas recebidas ("Mencionado em..."), com obra, capítulo e trecho da citação contextual.

**Independent Test**: Abrir um estudo citado por outros documentos, rolar até o rodapé da coluna central e verificar a listagem dos estudos de origem com citação contextual e link clicável de retorno.

### Tests for User Story 3

- [X] T017 [P] [US3] Adicionar testes de backend para `GET /api/studies/{study_id}/backlinks` com junção relacional, snippets contextuais e supressão de itens na lixeira em `caderno-leitura-0.1/backend/tests/test_study_mentions.py`
- [X] T018 [P] [US3] Adicionar testes de frontend para renderização do componente de lista de backlinks em `caderno-leitura-0.1/frontend/tests/study_mentions.test.mjs`

### Implementation for User Story 3

- [X] T019 [US3] Implementar componente `StudyBacklinksList.vue` com cabeçalho com contador de menções, cards estruturados com livro/capítulo/estudo e citação contextual em `caderno-leitura-0.1/frontend/src/components/studies/StudyBacklinksList.vue`
- [X] T020 [US3] Integrar `StudyBacklinksList.vue` no rodapé da coluna central de leitura abaixo das abas de análise em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Todas as 3 histórias de usuário concluídas e integradas com ciclo bidirecional completo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinamentos ergonômicos, acessibilidade móvel e validação estrita das suítes de teste

- [X] T021 [P] Implementar layout responsivo móvel do autocomplete e dos cartões de backlinks com alvos táteis mínimos de 44x44px em `caderno-leitura-0.1/frontend/src/components/studies/StudyBacklinksList.vue` e `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`
- [X] T022 Executar verificação de conformidade do Design System (ausência de emojis informais) em `caderno-leitura-0.1/frontend/tests/visual_system.test.mjs`
- [X] T023 Executar suíte completa de testes do frontend via `npm test` em `caderno-leitura-0.1/frontend`
- [X] T024 Executar validação de tipos TypeScript e compilação de produção via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T025 Executar suíte completa de testes do backend via `pytest` em `caderno-leitura-0.1/backend`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências externas — executa imediatamente.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA a implementação das histórias.
- **User Story 1 (Phase 3)**: Depende de Phase 2 — Entrega o MVP funcional.
- **User Story 2 (Phase 4)**: Depende de Phase 2 e estende a renderização do leitor.
- **User Story 3 (Phase 5)**: Depende de Phase 2 e adiciona o componente de rodapé de leitura.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

### User Story Dependencies

- **User Story 1 (P1)**: Autônoma após Foundational. Permite autocompletar e salvar menções no editor.
- **User Story 2 (P2)**: Autônoma após Foundational. Renderiza os links no leitor com navegação SPA.
- **User Story 3 (P3)**: Autônoma após Foundational. Consome os dados persistidos por US1 para listar os backlinks no leitor.

### Parallel Opportunities

- **Phase 1**: T002 (Model), T003 (TypeScript) e T004 (Pydantic) podem rodar em paralelo.
- **Phase 2**: T008 (API client) pode rodar em paralelo com os testes da Phase 3.
- **Phase 3**: T009 (Backend tests) e T010 (Frontend tests) podem rodar em paralelo.
- **Phase 4**: T013 (Backend tests) e T014 (Frontend tests) podem rodar em paralelo.
- **Phase 5**: T017 (Backend tests) e T018 (Frontend tests) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001–T004).
2. Completar Foundational (T005–T008).
3. Completar User Story 1 (T009–T012).
4. **Validar MVP**: Digitar `[[` no editor, selecionar um estudo candidato e confirmar persistência de `study_mentions`.

### Incremental Delivery
1. Setup + Foundational -> Migração, persistência e serviços prontos.
2. User Story 1 -> MVP: escrita fluida com autocomplete de menções.
3. User Story 2 -> Hiperlinks internos clicáveis no Markdown com navegação SPA.
4. User Story 3 -> Painel reverso de backlinks no rodapé da leitura.
5. Polish -> Mobile 44px, conformidade de Design System e suítes completas verdes.
