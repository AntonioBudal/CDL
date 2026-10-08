# Tasks: F0.7.14 — Sessões Estruturadas de Estudo e Auditoria de Aprendizado

**Feature**: F0.7.14 — Sessões Estruturadas de Estudo  
**Branch**: `063-sessoes-estudo` | **Date**: 2026-10-10  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Inicialização dos arquivos, tipos e contratos compartilhados.

- [X] T001 Criar estrutura de modelos e schemas em `backend/app/models/study_session.py` e `backend/app/schemas/study_session.py`
- [X] T002 Preparar arquivos de serviço e router em `backend/app/services/study_session_service.py` e `backend/app/routers/study_sessions.py`
- [X] T003 [P] Declarar contratos de tipos em `frontend/src/types.ts` e métodos de chamada em `frontend/src/services/api.ts`

---

## Phase 2: Foundational (Pré-requisitos Bloqueantes)

**Purpose**: Infraestrutura de banco de dados e backend necessária antes de qualquer fluxo de usuário.

**CRITICAL**: Nenhuma interface pode ser implementada antes da conclusão desta fase.

- [X] T004 Criar migração Alembic `0028_add_study_sessions_tables.py` com tabelas `study_sessions` e `study_session_items`, chaves estrangeiras e índices
- [X] T005 [P] Implementar mapeamento SQLAlchemy `StudySession` e `StudySessionItem` em `backend/app/models/study_session.py` e registrar em `backend/app/models/__init__.py`
- [X] T006 [P] Implementar schemas Pydantic (`StudySessionStartRequest`, `StudySessionResponse`, etc.) em `backend/app/schemas/study_session.py` e registrar em `backend/app/schemas/__init__.py`
- [X] T007 Configurar router base `backend/app/routers/study_sessions.py` e registrar em `backend/app/main.py` com isolamento multiusuário por `user_id`
- [X] T008 Criar suíte de testes de integração do backend em `backend/tests/test_study_sessions.py` com banco efêmero `tmp_path`

**Checkpoint**: Fundação de dados e contratos pronta para implementação das histórias de usuário.

---

## Phase 3: User Story 1 - Início e Execução de Sessão Imersiva (Priority: P1) [MVP]

**Goal**: Permitir ao leitor iniciar uma sessão de estudo com escopo definido e executá-la em modo imersivo com barra de progresso e avaliação atômica.

**Independent Test**: Iniciar uma sessão rápida de 10 itens (ou lote disponível), responder aos cartões sequencialmente e verificar a atualização dos carimbos em `study_highlights`.

### Implementação de Backend para User Story 1

- [X] T009 [P] [US1] Implementar endpoint `POST /api/study-sessions/start` com suporte a escopos (`quick`, `book`, `all`) e ajuste dinâmico para lotes menores (Q2: A) em `backend/app/services/study_session_service.py`
- [X] T010 [P] [US1] Implementar endpoint `POST /api/study-sessions/{id}/items` para registro atômico de resposta e avanço de repetição espaçada em `study_highlights`
- [X] T011 [P] [US1] Implementar endpoint `POST /api/study-sessions/{id}/interrupt` para tratamento de sessões interrompidas preservando itens respondidos (Q1: A)
- [X] T012 [P] [US1] Adicionar testes automatizados para US1 em `backend/tests/test_study_sessions.py`

### Implementação de Frontend para User Story 1

- [X] T013 [US1] Implementar composable `useActiveReadingSession.ts` gerenciando o ciclo de vida reativo, cronômetro, atalhos de teclado e proteção contra saída acidental
- [X] T014 [US1] Implementar componente `SessionProgressHeader.vue` com barra de progresso horizontal suave, contador de itens e botão de saída segura
- [X] T015 [US1] Implementar View imersiva `StudySessionView.vue` em modo tela limpa sem barras periféricas, com suporte a revelação e avaliação (Fácil, Médio, Difícil)
- [X] T016 [US1] Registrar rota `/estudo/sessao/:sessionId` em `frontend/src/router/index.ts` e adicionar gatilho "Iniciar Sessão de Estudo" em `ReviewHubView.vue`

**Checkpoint**: User Story 1 funcional de ponta a ponta (MVP entregue).

---

## Phase 4: User Story 2 - Conclusão, Resumo de Auditoria e Feedback Cognitivo (Priority: P2)

**Goal**: Apresentar painel de encerramento solene e triunfante com métricas consolidadas ao responder ao último cartão da sessão.

**Independent Test**: Concluir todos os cartões de uma sessão e verificar a abertura do modal com cálculo de tempo dedicado e taxa de aproveitamento.

### Implementação para User Story 2

- [X] T017 [P] [US2] Implementar endpoint `POST /api/study-sessions/{id}/complete` consolidando duração, acertos e taxas em `backend/app/services/study_session_service.py`
- [X] T018 [P] [US2] Implementar endpoint `GET /api/study-sessions/{id}/summary` para retorno estatístico e próximas revisões
- [X] T019 [US2] Implementar componente solene `SessionSummaryModal.vue` com métricas tipográficas limpas, resumo de aproveitamento e ações de retorno
- [X] T020 [US2] Integrar disparo automático do modal de encerramento em `StudySessionView.vue` ao avaliar o último cartão
- [X] T021 [P] [US2] Adicionar testes automatizados de encerramento e resumo em `backend/tests/test_study_sessions.py`

**Checkpoint**: User Stories 1 e 2 funcionais conjuntamente.

---

## Phase 5: User Story 3 - Histórico de Sessões e Desempenho Retrospectivo (Priority: P3)

**Goal**: Permitir ao leitor auditar sua constância histórica de estudo através de listagem cronológica de sessões passadas.

**Independent Test**: Acessar o histórico na Central de Revisão após realizar múltiplas sessões e verificar ordenação cronológica e estatísticas.

### Implementação para User Story 3

- [X] T022 [P] [US3] Implementar endpoint `GET /api/study-sessions/history` com paginação, filtros e ordenação decrescente por data em `backend/app/routers/study_sessions.py`
- [X] T023 [US3] Implementar aba de Histórico de Sessões em `ReviewHubView.vue` exibindo data, duração, itens e aproveitamento
- [X] T024 [P] [US3] Adicionar testes automatizados de histórico e isolamento multiusuário em `backend/tests/test_study_sessions.py`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e integradas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de conformidade visual, acessibilidade, estabilidade e suítes completas de testes.

- [X] T025 [P] Criar suíte de testes de frontend em `frontend/tests/study_sessions.test.mjs` validando contratos, acessibilidade e ausência de emojis
- [X] T026 Garantir alvos táteis mínimos ($\ge 44 \times 44$px) e suporte a navegação por teclado (`1`/`2`/`3`, `Espaço`, `Esc`)
- [X] T027 Executar validação completa do quickstart e rodar `npm test`, `pytest` e `npm run build`

---

## Dependencies & Execution Order

### Dependência entre Fases

1. **Setup (Phase 1)**: Sem dependências — execução imediata.
2. **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA todas as histórias de usuário.
3. **User Stories (Phases 3 a 5)**: Dependem da conclusão da Phase 2.
   - US1 (P1): MVP principal.
   - US2 (P2): Depende do fluxo de US1 para disparar conclusão.
   - US3 (P3): Depende da persistência gerada em US1 e US2.
4. **Polish (Phase 6)**: Executada ao término das histórias de usuário.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir Setup e Foundational (migração, modelo, router base).
2. Concluir User Story 1 (início da sessão, view imersiva, avaliação atômica).
3. **Validar US1**: Testar sessão de 5 a 10 itens de forma independente.
4. Concluir User Story 2 (painel triunfante de conclusão).
5. Concluir User Story 3 (histórico retrospectivo).
6. Rodar testes de regressão completos.
