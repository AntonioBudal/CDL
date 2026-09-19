# Tasks: 013 — Dashboard de Leitura com Calendário e Timeline

**Input**: Design documents from `specs/013-dashboard-calendario-timeline/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/dashboard.contract.md](contracts/dashboard.contract.md), [quickstart.md](quickstart.md)  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação inicial e mapeamento de contratos de dados.

- [X] T001 Mapear contratos de API, schemas e rotas entre `specs/013-dashboard-calendario-timeline/` e `caderno-leitura-0.1/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schemas e contratos tipados compartilhados que bloqueiam a implementação das histórias de usuário.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Criar schemas Pydantic de entrada e saída do Dashboard em `caderno-leitura-0.1/backend/app/schemas/dashboard.py`
- [X] T003 [P] Definir interfaces TypeScript do Dashboard em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T004 Adicionar método `getDashboard` no cliente HTTP em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: Fundação tipada e cliente de API prontos — implementação das histórias de usuário desbloqueada.

---

## Phase 3: User Story 1 - Visão Geral de Produtividade e Métricas Principais (Priority: P1) 🎯 MVP

**Goal**: Exibir cartões de métricas consolidadas (total de livros ativos, total de estudos, dias de leitura, média de estudos/livro e sequência de dias ativos), com estado vazio acolhedor e navegação integrada.

**Independent Test**: Acessar `/dashboard` e verificar que os cartões de resumo são renderizados com precisão matemática a partir do banco de dados ativo, sem dados falsos de recarga.

### Tests for User Story 1

- [X] T005 [P] [US1] Criar testes unitários e de integração de cálculo de métricas e streak em `caderno-leitura-0.1/backend/tests/test_dashboard.py`

### Implementation for User Story 1

- [X] T006 [US1] Implementar serviço de agregação de métricas e cálculo de streak em `caderno-leitura-0.1/backend/app/services/dashboard_service.py`
- [X] T007 [US1] Criar router `GET /api/dashboard` com suporte a `tz_offset` em `caderno-leitura-0.1/backend/app/routers/dashboard.py` e registrar em `caderno-leitura-0.1/backend/app/main.py`
- [X] T008 [P] [US1] Registrar a rota `/dashboard` em `caderno-leitura-0.1/frontend/src/router/index.ts`
- [X] T009 [P] [US1] Adicionar link de navegação do Dashboard com ícone SVG em `caderno-leitura-0.1/frontend/src/App.vue`
- [X] T010 [US1] Criar view principal `DashboardView.vue` com cartões de métricas, estados vazios acolhedores e nó raiz único em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue`

**Checkpoint**: User Story 1 concluída e testável de forma 100% independente (MVP alcançado: painel de métricas operando).

---

## Phase 4: User Story 2 - Mapa de Calor Responsivo e Frequência em Calendário (Priority: P2)

**Goal**: Exibir mapa de calor visual de semanas/dias com 4 níveis de intensidade com `color-mix`, recorte adaptativo (12 meses desktop, 3 a 6 meses mobile), tooltips contextuais por data e interação de clique para filtrar.

**Independent Test**: Gerar livros e estudos em datas variadas e verificar no navegador a plotagem das células do heatmap, suas cores por intensidade, dicas contextuais ao passar o mouse e a adaptação responsiva no mobile.

### Tests for User Story 2

- [X] T011 [P] [US2] Adicionar testes unitários para a agregação do mapa de calor e cálculo de níveis de intensidade em `caderno-leitura-0.1/backend/tests/test_dashboard.py`

### Implementation for User Story 2

- [X] T012 [US2] Implementar projeção de datas no `dashboard_service.py` para gerar pontos do heatmap (365 dias ou parâmetro `days`) com nível de 0 a 3 em `caderno-leitura-0.1/backend/app/services/dashboard_service.py`
- [X] T013 [P] [US2] Criar componente visual `HeatmapCalendar.vue` com grid de dias/semanas, tooltips por data e estilização `color-mix` harmonizada com Superclasses em `caderno-leitura-0.1/frontend/src/components/HeatmapCalendar.vue`
- [X] T014 [US2] Implementar recorte responsivo adaptativo (12 meses em desktop vs 3 a 6 meses em mobile com toggle "Ver ano completo") em `caderno-leitura-0.1/frontend/src/components/HeatmapCalendar.vue`
- [X] T015 [US2] Integrar o componente `HeatmapCalendar` na `DashboardView.vue` conectando evento de seleção de data em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue`

**Checkpoint**: User Story 2 concluída e integrada com sucesso (heatmap adaptativo funcional).

---

## Phase 5: User Story 3 - Linha do Tempo Cronológica de Atividades Recentes e Filtros (Priority: P3)

**Goal**: Exibir lista cronológica reversa detalhando ações de estudo (criação de estudo, edição de anotação, cadastro de livro) com atalhos diretos, filtragem por dia selecionado no heatmap e exclusão imediata de itens na lixeira.

**Independent Test**: Realizar ações de criação de livro, estudo e edição de anotações, confirmando que a lista cronológica exibe as entradas com links para leitura e que itens na lixeira deixam de pontuar imediatamente.

### Tests for User Story 3

- [X] T016 [P] [US3] Adicionar testes de integração para listagem da timeline, filtro por data e exclusão estrita de itens da lixeira em `caderno-leitura-0.1/backend/tests/test_dashboard.py`

### Implementation for User Story 3

- [X] T017 [US3] Implementar consulta da timeline de eventos no `dashboard_service.py` com suporte ao filtro `?date=YYYY-MM-DD` e exclusão de soft-deleted em `caderno-leitura-0.1/backend/app/services/dashboard_service.py`
- [X] T018 [US3] Renderizar lista da timeline com badges de ação, links diretos de leitura e banner de filtro ativo com botão de limpeza em `caderno-leitura-0.1/frontend/src/views/DashboardView.vue`
- [X] T019 [P] [US3] Adicionar testes frontend para renderização do Dashboard, heatmap e filtragem de timeline em `caderno-leitura-0.1/frontend/tests/dashboard.test.mjs`

**Checkpoint**: Todas as 3 histórias de usuário concluídas e integradas com sucesso.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação automatizada, compilação de produção e sincronização documental.

- [X] T020 [P] Executar bateria de testes do backend via `pytest` cobrindo cenários do Dashboard em `caderno-leitura-0.1/backend`
- [X] T021 [P] Executar bateria de testes do frontend via `npm test` em `caderno-leitura-0.1/frontend`
- [X] T022 [P] Executar verificação estrita de tipos TypeScript e build de produção Vite via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T023 Executar validação manual dos cenários 1 a 5 de `quickstart.md`
- [X] T024 Atualizar documentação de governança e histórico de transição em `caderno-leitura-0.1/docs/contexto/RETOMADA.md` e `ESTADO-E-DIAGNOSTICO.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA todas as histórias de usuário.
- **User Stories (Phase 3+)**: Dependem de Foundational (Phase 2). Executadas em sequência ordenada (US1 → US2 → US3) com tarefas [P] paralelas.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

### User Story Dependencies

- **User Story 1 (P1)**: Desbloqueada após Phase 2. Foco exclusivo nas métricas e na casca da view do Dashboard.
- **User Story 2 (P2)**: Desbloqueada após Phase 2. Foco no mapa de calor visual e adaptação responsiva.
- **User Story 3 (P3)**: Desbloqueada após Phase 2. Foco na timeline cronológica e na interação de filtro cruzado com o heatmap.

### Parallel Opportunities

- Tarefas T002 e T003 em Foundational podem rodar concorrentemente (backend vs frontend).
- Testes T005, T011 e T016 em backend podem ser preparados paralelamente às tarefas de visualização frontend T008 e T009.
- Tarefas T020, T021 e T022 em Polish podem rodar concorrentemente.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001) e Foundational (T002 a T004).
2. Implementar User Story 1 (T005 a T010).
3. **Validar MVP**: Acessar `/dashboard` e validar as métricas essenciais.

### Incremental Delivery
1. MVP entregue (Métricas e estado vazio acolhedor).
2. Adicionar User Story 2 (T011 a T015) → Mapa de calor responsivo com 4 níveis.
3. Adicionar User Story 3 (T016 a T019) → Timeline detalhada com filtro por clique.
4. Polish (T020 a T024) → Testes verdes em backend/frontend, build validado e documentação sincronizada.
