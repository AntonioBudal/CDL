# Tasks: F 0.7.10 — Central de Revisão de Perguntas e Clozes

**Feature Branch**: `059-central-de-revisao`  
**Date**: 2026-10-04  
**Spec**: [specs/059-central-de-revisao/spec.md](spec.md) | **Plan**: [specs/059-central-de-revisao/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de contratos compartilhados de dados e tipos TypeScript/Pydantic para suporte à Central de Revisão.

- [X] T001 Definir tipos de dados para itens de revisão, estatísticas agregadas e avaliações (`ReviewItemRead`, `ReviewStatsResponse`, `ReviewBookItem`, `ReviewRating`) em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T002 [P] Criar schemas Pydantic para requisições e respostas da API de revisão (`ReviewItemRead`, `ReviewRecordRequest`, `ReviewStatsResponse`, `ReviewBookItem`) em `caderno-leitura-0.1/backend/app/schemas/review.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de persistência, modelo de banco estendido, migração Alembic e serviço de consulta e avaliação no backend.

**⚠️ CRITICAL**: Nenhuma história de usuário deve avançar sem a base de dados e os endpoints da API de revisão validados.

- [X] T003 Estender modelo SQLAlchemy `StudyHighlight` com colunas `last_reviewed_at`, `review_count`, `last_rating` e índice `ix_study_highlights_review` em `caderno-leitura-0.1/backend/app/models/study_highlight.py`
- [X] T004 Criar migração Alembic `0024_add_review_metadata_to_highlights.py` aplicando as novas colunas e o índice relacional de revisão em `caderno-leitura-0.1/backend/migrations/versions/0024_add_review_metadata_to_highlights.py`
- [X] T005 Implementar serviço `review_service.py` com heurística de priorização relacional simples (itens não revisados primeiro, seguidos por difíceis e mais antigos), contagens agregadas e registro atômico de avaliações em `caderno-leitura-0.1/backend/app/services/review_service.py`
- [X] T006 Implementar router FastAPI com rotas `GET /api/review/stats`, `GET /api/review/items` e `POST /api/review/items/{id}/record` em `caderno-leitura-0.1/backend/app/routers/review.py` e registrar no `caderno-leitura-0.1/backend/app/main.py`
- [X] T007 Criar testes de integração de backend para a API de revisão validando priorização, isolamento multiusuário, descarte de itens na lixeira e persistência de avaliações em `caderno-leitura-0.1/backend/tests/test_review_hub.py`

**Checkpoint**: Base de banco de dados e endpoints de backend operacionais e 100% testados com banco isolado.

---

## Phase 3: User Story 1 - Hub Central de Revisão e Seleção por Escopo (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor acesse a rota `/review`, visualize contadores de perguntas e termos ocultos (clozes) do seu acervo e aplique filtros por livro/capítulo antes de disparar uma rodada de estudo.

**Independent Test**: Acessar a rota `/review`; verificar a renderização dos cards de estatísticas totais; selecionar um livro e confirmar que o botão "Iniciar Revisão" atualiza a contagem dos itens elegíveis correspondentes.

### Tests for User Story 1 🧪

- [X] T008 [US1] Criar testes unitários para a rota `/review`, carregamento de estatísticas e filtros por livro/capítulo em `caderno-leitura-0.1/frontend/tests/review-hub-view.test.mjs`

### Implementation for User Story 1

- [X] T009 [US1] Criar cliente HTTP de API para os endpoints de revisão em `caderno-leitura-0.1/frontend/src/api/review.ts`
- [X] T010 [US1] Criar componente `ReviewStatsHeader.vue` exibindo cards de métricas, pílulas de alternância de tipo e seletores de livro/capítulo em `caderno-leitura-0.1/frontend/src/components/review/ReviewStatsHeader.vue`
- [X] T011 [US1] Criar view `ReviewHubView.vue` com cabeçalho de estatísticas, estado vazio acolhedor e botão primário "Iniciar Revisão" em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- [X] T012 [US1] Registrar a rota `/review` no Vue Router em `caderno-leitura-0.1/frontend/src/router/index.ts` e adicionar item de menu "Revisão" na barra de navegação principal em `caderno-leitura-0.1/frontend/src/App.vue`

**Checkpoint**: User Story 1 (MVP) funcional e testável de forma independente. O leitor já consegue acessar a Central de Revisão e consultar o panorama do seu acervo.

---

## Phase 4: User Story 2 - Sessão Interativa de Active Recall em Tela Limpa (Priority: P2)

**Goal**: Fornecer uma experiência de estudo focada em tela limpa com cards interativos de perguntas e clozes, revelação instantânea por clique ou `Espaço`, e avaliação de assimilação (*Difícil*, *Médio*, *Fácil* ou teclas `1`, `2`, `3`).

**Independent Test**: Iniciar uma rodada; verificar card de pergunta com resposta oculta; pressionar `Espaço` e validar revelação in-place; pressionar `3` e validar avanço para o card seguinte com atualização da barra de progresso.

### Tests for User Story 2 🧪

- [X] T013 [P] [US2] Criar testes unitários para o composable `useReviewSession.ts` validando máquina de estados, revelação, submissão de notas e avanço de índice em `caderno-leitura-0.1/frontend/tests/review-session.test.mjs`
- [X] T014 [P] [US2] Criar testes unitários para o componente `ReviewCard.vue` cobrindo atalhos de teclado (`Espaço`, `1`, `2`, `3`), alvos táteis de 44px e acessibilidade `aria-live` em `caderno-leitura-0.1/frontend/tests/review-card.test.mjs`

### Implementation for User Story 2

- [X] T015 [US2] Implementar composable `useReviewSession.ts` gerenciando o lote padrão de 10 itens, estados `isRevealed` e avanço automático de cards em `caderno-leitura-0.1/frontend/src/composables/useReviewSession.ts`
- [X] T016 [P] [US2] Implementar componente `ReviewCard.vue` com tipografia editorial, renderização segura de Markdown, atalhos universais de teclado e alvos de toque $\ge 44 \times 44$px em `caderno-leitura-0.1/frontend/src/components/review/ReviewCard.vue`
- [X] T017 [US2] Integrar o fluxo interativo de cards dentro da view `ReviewHubView.vue`, alternando entre o modo painel e o modo imersivo de estudo em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`

**Checkpoint**: User Stories 1 e 2 integradas. Prática completa de Active Recall funcional no Desktop e Mobile.

---

## Phase 5: User Story 3 - Conclusão de Sessão, Estatísticas de Assimilação e Feedback (Priority: P3)

**Goal**: Exibir tela de fechamento de ciclo após a conclusão do 10º item da rodada, com gráficos e percentuais de retenção (*Fácil*, *Médio*, *Difícil*) e ações diretas para "Revisar mais 10" ou retornar ao acervo.

**Independent Test**: Resolver 10 cards em sequência; verificar aparecimento imediato da tela de conclusão com contagens exatas das avaliações atribuídas; clicar em "Revisar mais 10" e confirmar inicialização do próximo bloco.

### Tests for User Story 3 🧪

- [X] T018 [US3] Estender testes de `ReviewHubView` para validar exibição do resumo ao término do lote e reinicialização de rodada em `caderno-leitura-0.1/frontend/tests/review-hub-view.test.mjs`

### Implementation for User Story 3

- [X] T019 [US3] Implementar componente `ReviewSummaryModal.vue` com balanço de retenção da sessão, contagens por cor/dificuldade e botões de continuidade em `caderno-leitura-0.1/frontend/src/components/review/ReviewSummaryModal.vue`
- [X] T020 [US3] Conectar o gatilho de conclusão de lote e fluxo de continuidade ("Revisar mais 10" vs "Concluir") na view `ReviewHubView.vue` em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e integradas fim a fim.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação global de integridade, validação dos 5 cenários do quickstart, execução das suítes de testes e checagem estrita de compilação.

- [X] T021 Executar validação manual e automatizada dos 5 cenários descritos em `specs/059-central-de-revisao/quickstart.md`
- [X] T022 Rodar suíte completa de testes de frontend via `npm test` em `caderno-leitura-0.1/frontend/`
- [X] T023 Rodar suíte completa de testes de backend via `pytest` garantindo isolamento total do banco de dados ativo
- [X] T024 Executar verificação estrita de tipagem TypeScript e compilação de produção via `npm run build` em `caderno-leitura-0.1/frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências externas. Início imediato.
- **Foundational (Phase 2)**: Depende da Phase 1. Estabelece schema, migração Alembic e endpoints da API. Bloqueia o início das histórias no frontend.
- **User Story 1 (Phase 3 - P1 MVP)**: Depende da Phase 2. Estabelece a rota `/review`, painel de controle e menu.
- **User Story 2 (Phase 4 - P2)**: Depende da Phase 3. Implementa a sessão imersiva e os cards de perguntas/clozes.
- **User Story 3 (Phase 5 - P3)**: Depende da Phase 4. Adiciona a tela de encerramento de ciclo e métricas de retenção.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- **Fase 1**: T001 e T002 podem ser desenvolvidos em paralelo.
- **Fase 4 (US2)**: T013 e T014 (testes) e T016 (componente do card) podem rodar em paralelo.

---

## Parallel Example: User Story 2

```bash
# Executar paralelamente os testes e o componente do card de revisão:
Task: T013 "Criar testes unitários para useReviewSession em frontend/tests/review-session.test.mjs"
Task: T014 "Criar testes unitários para ReviewCard em frontend/tests/review-card.test.mjs"
Task: T016 "Implementar componente ReviewCard.vue em frontend/src/components/review/ReviewCard.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Tipos TypeScript e Schemas Pydantic).
2. Concluir Phase 2 (Migração Alembic, serviço de priorização e endpoints FastAPI).
3. Concluir Phase 3 (Cliente HTTP, `ReviewStatsHeader.vue`, `ReviewHubView.vue` e rota `/review`).
4. **Validar MVP**: O leitor visualiza todas as estatísticas consolidadas e filtra seu acervo de Active Recall.

### Entrega Incremental

1. MVP concluído -> Adicionar US2 (Sessão imersiva com `ReviewCard.vue`, `useReviewSession.ts` e atalhos de teclado).
2. US2 concluída -> Adicionar US3 (Modal de encerramento de lote `ReviewSummaryModal.vue` e fluxo contínuo).
3. Executar Phase 6 (Validação dos 5 cenários, `npm test`, `pytest`, `npm run build`).
4. Commit atômico: `feature — central de revisao de perguntas e clozes`.
