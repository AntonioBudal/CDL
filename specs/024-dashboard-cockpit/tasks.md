# Tasks: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Feature Branch**: `024-dashboard-cockpit`  
**Date**: 2026-09-19  
**Specification**: [spec.md](./spec.md)  
**Implementation Plan**: [plan.md](./plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de schemas unificados, tipagens estritas no frontend e cliente de API compartilhado.

- [X] T001 [P] Adicionar schemas Pydantic v2 para RecentStudyActivityItem, UnlinkedStudyItem, RecentRelationItem e estender DashboardSummary e DashboardResponse em caderno-leitura-0.1/backend/app/schemas/dashboard.py
- [X] T002 [P] Definir e exportar tipos TypeScript para RecentStudyActivityItem, UnlinkedStudyItem, RecentRelationItem, DashboardSummary, DashboardResponse, DashboardBlockVisibility e HomeViewPreference em caderno-leitura-0.1/frontend/src/types.ts
- [X] T003 [P] Atualizar tipagem de retorno e parâmetros do método getDashboard no cliente HTTP em caderno-leitura-0.1/frontend/src/services/api.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura transacional do backend com queries otimizadas no SQLite para agregação analítica e isolamento de soft delete.

- [X] T004 Estender o serviço get_dashboard_data com queries SQL otimizadas para estudos recentes ordenados por updated_at DESC, identificação de estudos órfãos via NOT EXISTS em study_relations, últimas relações semânticas ativas e contadores em caderno-leitura-0.1/backend/app/services/dashboard_service.py
- [X] T005 Atualizar endpoint REST GET /api/dashboard/summary para retornar o payload completo do DashboardResponse em caderno-leitura-0.1/backend/app/routers/dashboard.py
- [X] T006 [P] Criar suíte de testes de integração automatizados para validação do endpoint unificado, contagens exatas de órfãos e exclusão estrita de itens na lixeira em caderno-leitura-0.1/backend/tests/test_dashboard_v2.py

**Checkpoint**: Backend unificado e testado retornando todos os indicadores analíticos, estudos recentes, órfãos e conexões semânticas em < 300ms.

---

## Phase 3: User Story 1 - Retomada Imediata do Trabalho Intelectual (Priority: P1) [MVP]

**Goal**: Permitir ao leitor abrir a aplicação e encontrar imediatamente o bloco "Continuar Estudos" com atalho direto de 1 clique para retomar a leitura no ponto exato onde parou, com rota inicial configurável.

**Independent Test**: Abrir o Dashboard com múltiplos estudos modificados em momentos diferentes; constatar os 5 estudos mais recentemente alterados no bloco "Continuar Estudos"; clicar no botão "Ver mais" para expandir para 10; clicar em um estudo e constatar a navegação direta com foco preservado.

### Implementation for User Story 1

- [X] T007 [US1] Criar componente ResumeStudiesWidget com lista de estudos recentes, metadados de livro/capítulo, status de leitura, botão Ver mais (5 a 10) e atalho direto de 1 clique em caderno-leitura-0.1/frontend/src/components/dashboard/ResumeStudiesWidget.vue
- [X] T008 [US1] Configurar rota raiz inicial condicional baseada na preferência do localStorage em caderno-leitura-0.1/frontend/src/router/index.ts e adicionar seletor de tela inicial padrão em caderno-leitura-0.1/frontend/src/views/SettingsView.vue
- [X] T009 [US1] Integrar ResumeStudiesWidget no palco principal da tela inicial em caderno-leitura-0.1/frontend/src/views/DashboardView.vue
- [X] T010 [P] [US1] Criar testes unitários para exibição de estudos recentes, expansão de itens e navegação de 1 clique em caderno-leitura-0.1/frontend/tests/dashboard-cockpit.test.mjs

**Checkpoint**: MVP do Dashboard 2.0 funcional. O leitor pode retomar seu estudo mais recente com exatamente 1 clique assim que abre o Caderno.

---

## Phase 4: User Story 2 - Identificação de Estudos Sem Vínculos e Apoio à Sistematização (Priority: P2)

**Goal**: Identificar proativamente estudos que ainda não possuem conexões conceituais no grafo (estudos órfãos) e oferecer um atalho imediato para conectá-los a outras ideias.

**Independent Test**: Cadastrar estudos com e sem conexões; acessar o Dashboard e constatar que o widget "Estudos para Conectar" exibe a contagem real de órfãos e permite clicar para iniciar a criação de relações semânticas.

### Implementation for User Story 2

- [X] T011 [US2] Criar componente OrphanStudiesWidget exibindo contador de estudos órfãos, lista amostral de itens para enriquecimento e atalho de ação rápida Criar relação em caderno-leitura-0.1/frontend/src/components/dashboard/OrphanStudiesWidget.vue
- [X] T012 [US2] Integrar OrphanStudiesWidget na coluna de trabalho e no seletor modular de blocos em caderno-leitura-0.1/frontend/src/views/DashboardView.vue
- [X] T013 [P] [US2] Implementar testes automatizados de cálculo e isolamento de estudos órfãos em caderno-leitura-0.1/backend/tests/test_dashboard_v2.py

**Checkpoint**: Ferramenta ativa de combate a silos de anotações e estímulo ao crescimento do grafo de conhecimento.

---

## Phase 5: User Story 3 - Conexões Semânticas Recentes e Pulso do Grafo (Priority: P3)

**Goal**: Exibir as últimas relações conceituais estabelecidas no acervo, demonstrando a evolução dinâmica dos vínculos entre autores e conceitos.

**Independent Test**: Estabelecer relações semânticas entre estudos de diferentes livros; acessar o Dashboard e constatar a listagem atualizada com nomes das obras, estudos e badges conceituais correspondentes.

### Implementation for User Story 3

- [X] T014 [US3] Criar componente RecentConnectionsWidget exibindo as últimas relações semânticas com badges direcionais canônicos, títulos dos estudos conectados e links navegáveis em caderno-leitura-0.1/frontend/src/components/dashboard/RecentConnectionsWidget.vue
- [X] T015 [US3] Integrar RecentConnectionsWidget na visualização em grade modular de caderno-leitura-0.1/frontend/src/views/DashboardView.vue
- [X] T016 [P] [US3] Implementar testes de ordenação e integridade para conexões recentes em caderno-leitura-0.1/backend/tests/test_dashboard_v2.py

**Checkpoint**: Pulso e dinamismo do grafo semântico visíveis logo na entrada do sistema.

---

## Phase 6: User Story 4 - Linha do Tempo, Calibração de Temas no Calendário e Ergonomia Móvel (Priority: P4)

**Goal**: Assegurar calibração nítida de opacidade e contraste no calendário de 12 meses em todos os temas alternativos, e garantir layout móvel condensado com abas, atalhos táteis e blindagem contra overflow lateral.

**Independent Test**: Alternar para temas escuro, sépia, solarizado e e-ink, constatando o contraste visível entre dias com e sem atividade no calendário; emular smartphone de 375px e constatar a grade métrica 2x2, navegação por abas para widgets secundários e zero rolagem horizontal.

### Implementation for User Story 4

- [X] T017 [US4] Implementar tokens semânticos e regras CSS de contraste e opacidade para dias sem atividade (.level-0) e com atividade (.level-1 a .level-3) nos temas clássico, escuro, sépia, solarizado, e-ink e superclasses em caderno-leitura-0.1/frontend/src/components/HeatmapCalendar.vue
- [X] T018 [US4] Criar componente QuickNavChips com chips de navegação rápida aderente para telas móveis em caderno-leitura-0.1/frontend/src/components/dashboard/QuickNavChips.vue
- [X] T019 [US4] Reestruturar DashboardView com layout responsivo: grade métrica compacta 2x2 no topo para mobile, abas comutáveis para widgets secundários, blindagem overflow-x: hidden e alvos táteis mínimos de 44x44px em caderno-leitura-0.1/frontend/src/views/DashboardView.vue
- [X] T020 [P] [US4] Criar testes unitários para verificação de tokens e contraste de opacidade do calendário nos múltiplos temas em caderno-leitura-0.1/frontend/tests/dashboard-theme-contrast.test.mjs
- [X] T021 [P] [US4] Criar testes automatizados de ergonomia móvel, abas comutáveis, alvos de 44px e ausência de overflow horizontal em caderno-leitura-0.1/frontend/tests/dashboard-mobile-a11y.test.mjs

**Checkpoint**: Interface 100% legível e contrastada em todos os temas de cor, e ergonomicamente desenhada para smartphones.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação rigorosa de regressão, compilação de produção e homologação final.

- [X] T022 [P] Executar suíte completa de testes de regressão do backend em caderno-leitura-0.1/backend/tests/
- [X] T023 [P] Executar suíte de testes de regressão do frontend e compilação de produção Vite em caderno-leitura-0.1/frontend/
- [X] T024 Atualizar guia de validação executável e registrar evidências finais em specs/024-dashboard-cockpit/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T003)
        │
        ▼
Phase 2: Foundational (T004-T006)
        │
        ├────────────────────────────────┐
        ▼                                ▼
Phase 3: User Story 1 (T007-T010)  [MVP]  (Retoma Imediata e Rota Inicial Configurável)
        │
        ▼
Phase 4: User Story 2 (T011-T013)         (Estudos Órfãos e Apoio à Sistematização)
        │
        ▼
Phase 5: User Story 3 (T014-T016)         (Conexões Semânticas Recentes)
        │
        ▼
Phase 6: User Story 4 (T017-T021)         (Contraste Multitema do Heatmap e Layout Mobile)
        │
        ▼
Phase 7: Polish (T022-T024)               (Regressão completa, build Vite e validação)
```

### Parallel Opportunities

- **Phase 1**: T001 (schemas Pydantic), T002 (tipos TypeScript) e T003 (cliente de API) podem rodar em paralelo.
- **Phase 2**: T006 (testes backend) pode ser escrito em paralelo com T004 e T005.
- **Phase 3**: T008 (roteamento inicial) e T010 (testes unitários) podem rodar em paralelo com T007.
- **Phase 4**: T011 (OrphanStudiesWidget) e T013 (testes de órfãos) podem rodar em paralelo.
- **Phase 5**: T014 (RecentConnectionsWidget) e T016 (testes de conexões) podem rodar em paralelo.
- **Phase 6**: T017 (tokens de contraste no Heatmap), T018 (QuickNavChips), T020 e T021 (testes) podem rodar em paralelo.
- **Phase 7**: T022 (regressão backend) e T023 (regressão frontend + build Vite) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001-T003) e Foundational (T004-T006).
2. Implementar User Story 1 (T007-T010).
3. **Validar MVP**: O leitor já possui o cockpit operacional para retoma de estudos em 1 clique.

### Incremental Delivery
- US2 adiciona o widget de estudos sem vínculos.
- US3 expõe a rede de relações semânticas recentes.
- US4 resolve definitivamente a diferenciação de contraste nos outros temas do calendário de 12 meses e consolida a organização mobile em abas e chips de navegação.
- Phase 7 garante 100% de integridade com zero regressões.
