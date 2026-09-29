# Tasks: F0.6.5 — Histórico Automático de Versões de Estudo

**Branch**: `044-historico-automatico`  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura inicial e definições compartilhadas de tipos e esquemas

- [X] T001 Inicializar estrutura de arquivos e diretórios da feature em `specs/044-historico-automatico/`
- [X] T002 [P] Definir tipos TypeScript para versões, linha do tempo e diff em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T003 [P] Criar esquemas Pydantic de entrada, saída e diff de versão em `caderno-leitura-0.1/backend/app/schemas/study_version.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de persistência, modelo relacional e serviços base que bloqueiam todas as histórias

- [X] T004 Criar modelo SQLAlchemy `StudyVersion` em `caderno-leitura-0.1/backend/app/models/study_version.py`
- [X] T005 Atualizar modelo `Study` adicionando relacionamento com `StudyVersion` em `caderno-leitura-0.1/backend/app/models/study.py`
- [X] T006 Criar migração Alembic para a tabela `study_versions` em `caderno-leitura-0.1/backend/migrations/versions/0021_add_study_versions.py`
- [X] T007 Criar serviço base de manipulação de versões em `caderno-leitura-0.1/backend/app/services/study_version_service.py`
- [X] T008 Criar router `study_versions.py` em `caderno-leitura-0.1/backend/app/routers/study_versions.py` e registrar em `caderno-leitura-0.1/backend/app/main.py`
- [X] T009 Criar métodos clientes para listar, inspecionar, comparar e restaurar versões em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: Fundação pronta — implementação das histórias de usuário pode iniciar de forma independente.

---

## Phase 3: User Story 1 - Registro Automático e Consulta da Linha do Tempo (Priority: P1) [MVP]

**Goal**: Gravar automaticamente snapshots de estudo ao persistir edições e disponibilizar linha do tempo para inspeção do histórico.

**Independent Test**: Editar e salvar um estudo com alterações no título e seções; abrir a modal "Histórico de Versões"; verificar que a versão anterior foi catalogada com data, hora, autor e resumo de alterações.

### Tests for User Story 1
- [X] T010 [P] [US1] Criar testes unitários e de integração para captura automática e listagem de versões em `caderno-leitura-0.1/backend/tests/test_study_versions.py`

### Implementation for User Story 1
- [X] T011 [US1] Implementar gancho de captura de versão ao persistir alterações no endpoint `PATCH /api/studies/{study_id}` em `caderno-leitura-0.1/backend/app/routers/studies.py`
- [X] T012 [US1] Implementar endpoints `GET /api/studies/{study_id}/versions` e `GET /api/studies/{study_id}/versions/{version_id}` em `caderno-leitura-0.1/backend/app/routers/study_versions.py`
- [X] T013 [P] [US1] Criar componente `StudyHistoryModal.vue` com linha do tempo lateral e painel de inspeção de conteúdo em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue`
- [X] T014 [US1] Integrar botão de acionamento do histórico nas telas `caderno-leitura-0.1/frontend/src/views/StudyView.vue` e `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`

**Checkpoint**: Neste ponto, o registro automático e a visualização da linha do tempo estão 100% funcionais e testáveis (MVP entregue).

---

## Phase 4: User Story 2 - Visualização Comparativa e Diff entre Versões (Priority: P1)

**Goal**: Comparar visualmente duas versões destacando acréscimos e exclusões de texto por seção.

**Independent Test**: Selecionar uma versão anterior na linha do tempo; alternar para a aba "Comparar Diferenças"; verificar que trechos adicionados aparecem com destaque verde e removidos com destaque vermelho em cada seção.

### Tests for User Story 2
- [X] T015 [P] [US2] Criar testes automatizados para cálculo de diff estruturado por seção em `caderno-leitura-0.1/backend/tests/test_study_versions.py`

### Implementation for User Story 2
- [X] T016 [US2] Implementar algoritmo de comparação textual utilizando `difflib.SequenceMatcher` em `caderno-leitura-0.1/backend/app/services/study_version_service.py`
- [X] T017 [US2] Implementar endpoint `GET /api/studies/{study_id}/versions/{version_id}/diff` em `caderno-leitura-0.1/backend/app/routers/study_versions.py`
- [X] T018 [P] [US2] Criar componente `StudyDiffViewer.vue` com renderização acessível de chunks de texto (inserção, exclusão e inalterado) em `caderno-leitura-0.1/frontend/src/components/StudyDiffViewer.vue`
- [X] T019 [US2] Integrar `StudyDiffViewer.vue` e alternador de abas ("Inspeção" e "Comparar") no modal em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue`

**Checkpoint**: Neste ponto, a inspeção e a comparação visual (diff) entre versões funcionam de forma independente e integrada.

---

## Phase 5: User Story 3 - Restauração Segura de Versão Anterior (Priority: P1)

**Goal**: Permitir que o usuário reverta o estudo para qualquer versão anterior com preservação do estado presente e recuperação de destaques.

**Independent Test**: Selecionar uma versão anterior; clicar em "Restaurar esta versão"; confirmar no diálogo; verificar que o estudo reflete o conteúdo e os destaques daquela versão e que uma nova versão de restauração foi gerada.

### Tests for User Story 3
- [X] T020 [P] [US3] Criar testes automatizados para o fluxo de restauração atômica e restauração de destaques em `caderno-leitura-0.1/backend/tests/test_study_versions.py`

### Implementation for User Story 3
- [X] T021 [US3] Implementar serviço de restauração com snapshot preventivo, atualização do `Study` e reconstituição de `study_highlights` em `caderno-leitura-0.1/backend/app/services/study_version_service.py`
- [X] T022 [US3] Implementar endpoint `POST /api/studies/{study_id}/versions/{version_id}/restore` com checagem de permissão em `caderno-leitura-0.1/backend/app/routers/study_versions.py`
- [X] T023 [US3] Implementar botão de restauração com diálogo de confirmação explícita e atualização da interface em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue`

**Checkpoint**: Neste ponto, o ciclo completo de auditoria, comparação e recuperação segura de versões está finalizado.

---

## Phase 6: User Story 4 - Agrupamento e Retenção Inteligente de Histórico (Priority: P2)

**Goal**: Consolidar salvamentos consecutivos realizados dentro da janela de 5 minutos pelo mesmo autor em um único marco de versão.

**Independent Test**: Realizar salvamentos sucessivos com intervalo menor que 5 minutos; verificar que a linha do tempo mantém a versão agrupada, e que após 5 minutos um novo registro é gerado.

### Tests for User Story 4
- [X] T024 [P] [US4] Criar testes automatizados validando a janela de coalescência de 5 minutos e criação de novo registro após o limite em `caderno-leitura-0.1/backend/tests/test_study_versions.py`

### Implementation for User Story 4
- [X] T025 [US4] Implementar lógica de debounce/coalescência temporal baseada em `updated_at` e `user_id` em `caderno-leitura-0.1/backend/app/services/study_version_service.py`
- [X] T026 [US4] Adicionar indicador visual de consolidação e carimbos de tempo atualizados na linha do tempo em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue`

**Checkpoint**: Histórico protegido contra poluição por micro-salvamentos frequentes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Acessibilidade, conformidade visual estrita (sem emojis), validação de suite completa e testes manuais

- [X] T027 [P] Garantir conformidade com acessibilidade por teclado, suporte a temas e ausência estrita de emojis em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue` e `StudyDiffViewer.vue`
- [X] T028 Executar suite completa de testes automatizados (`pytest tests/test_study_versions.py`, `npm test` e `npm run build`)
- [X] T029 Executar verificação dos cenários de ponta a ponta descritos em `specs/044-historico-automatico/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão do Setup — BLOQUEIA todas as histórias de usuário.
- **User Stories (Phase 3+)**: Todas dependem da conclusão da Fase 2 (Foundational).
  - Sequência recomendada: US1 (MVP) → US2 (Diff) → US3 (Restauração) → US4 (Coalescência).
- **Polish (Phase 7)**: Depende da conclusão das histórias desejadas.

### User Story Dependencies

- **User Story 1 (P1)**: Depende apenas da Fase 2. Não possui dependência de outras histórias.
- **User Story 2 (P1)**: Depende da Fase 2 e utiliza as versões persistidas por US1 para cálculo de diff.
- **User Story 3 (P1)**: Depende da Fase 2 e US1 para restaurar snapshots existentes.
- **User Story 4 (P2)**: Depende da lógica de gravação de US1, refinando a frequência de persistência.

---

## Parallel Opportunities

- **Setup**: `T002` (Frontend types) e `T003` (Backend schemas) podem rodar em paralelo.
- **Foundational**: `T004` (Model) e `T009` (Frontend API) podem rodar em paralelo.
- **User Story 1**: `T010` (Testes backend) e `T013` (Componente Vue da modal) podem ser desenvolvidos em paralelo.
- **User Story 2**: `T015` (Testes de diff) e `T018` (Componente de visualização de diff) podem ser desenvolvidos em paralelo.
- **User Story 3**: `T020` (Testes de restauração) pode ser escrito em paralelo com componentes de confirmação.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 - Registro e Linha do Tempo).
3. **VALIDAR**: Salvar edições em um estudo e verificar a listagem cronológica na modal de histórico.

### Incremental Delivery

1. Setup + Foundational → Base pronta.
2. User Story 1 → Captura e consulta de histórico (MVP).
3. User Story 2 → Comparação de diferenças (Diff).
4. User Story 3 → Restauração segura com recuperação de destaques.
5. User Story 4 → Janela de coalescência de 5 minutos.
6. Polish → Validação final de testes e conformidade sem emojis.
