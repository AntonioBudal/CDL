# Tasks: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Branch**: `081-regressao-responsiva`  
**Input**: Design artifacts from `specs/081-regressao-responsiva/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/regression-coverage.contract.md`, `quickstart.md`)  
**Status**: Ready for implementation  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificação de ambiente e conferência de integridade dos contratos e rotas.

- [x] T001 [P] Verificar integridade do ambiente e arquivos de especificação em specs/081-regressao-responsiva/
- [x] T002 [P] Auditar rotas registradas em caderno-leitura-0.1/frontend/src/router/index.ts contra o contrato specs/081-regressao-responsiva/contracts/regression-coverage.contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Preparação do scaffold da suíte de testes-guarda e conferência de tokens fundamentais.

- [x] T003 Preparar scaffold da suíte de testes de regressão em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T004 [P] Validar integridade dos tokens de viewport e offsets móveis em caderno-leitura-0.1/frontend/src/style.css

---

## Phase 3: User Story 1 - Validação da Matriz de Rotas e Viewports sem Transbordamento (Priority: P1) [MVP]

**Goal**: Garantir que as 25 rotas nomeadas de `router/index.ts` e suas visualizações não apresentem rolagem horizontal (`scrollWidth === clientWidth`) através das 8 viewports normativas (320px, 375px, 390px, 430px, 767px, 768px, 1024px, 1440px) e no modo paisagem móvel.

**Independent Test**: Executar asserções automatizadas da matriz completa em `tests/feature-081-responsive-regression.test.mjs` e constatar 100% de conformidade de largura e offsets.

- [x] T005 [P] [US1] Implementar asserções da matriz de 25 rotas e 8 viewports em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T006 [P] [US1] Implementar verificação de contenção de largura e scrollWidth em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T007 [US1] Implementar verificação de offsets de navegação móvel (--mobile-nav-offset) em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs

**Checkpoint**: User Story 1 concluída e testável de forma autônoma como MVP.

---

## Phase 4: User Story 2 - Rastreabilidade e Encerramento dos Problemas Auditados (P-01 a P-19) (Priority: P1)

**Goal**: Verificar e blindar o encerramento formal dos 19 problemas diagnosticados na auditoria estática original (P-01 a P-19).

**Independent Test**: Testes automatizados inspecionam as regras canônicas de cada problema (shell, mapa, canvas, árvore, modais, botões, quebras de linha e Tailwind) e confirmam status de resolvido.

- [x] T008 [P] [US2] Implementar testes-guarda para os problemas de shell P-01 a P-03 em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T009 [P] [US2] Implementar testes-guarda para os problemas de visualizações móveis P-04 a P-08 em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T010 [P] [US2] Implementar testes-guarda para os problemas de componentes e layout P-09 a P-19 em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs

**Checkpoint**: User Stories 1 e 2 plenamente funcionais e validadas.

---

## Phase 5: User Story 3 - Suíte de Testes-Guarda Automatizados contra Regressões (Priority: P2)

**Goal**: Assegurar que novos desenvolvimentos ou refatorações não quebrem regras contratuais de responsividade, alvos táteis mínimos ($\ge 44 \times 44\text{ px}$) ou breakpoints canônicos.

**Independent Test**: Executar `npm test` no frontend e certificar que todos os testes de responsividade passam sem alertas.

- [x] T011 [P] [US3] Implementar verificação de alvos táteis mínimos de 44x44px em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T012 [P] [US3] Implementar verificação de limites canônicos de breakpoints em caderno-leitura-0.1/frontend/tests/feature-081-responsive-regression.test.mjs
- [x] T013 [US3] Executar e validar suíte completa via npm test em caderno-leitura-0.1/frontend

**Checkpoint**: Suíte de testes-guarda totalmente integrada ao processo de teste local.

---

## Phase 6: User Story 4 - Protocolo de Homologação em Aparelho Físico e Encerramento (Priority: P2)

**Goal**: Fornecer roteiro estruturado para testes em smartphones físicos reais (Android/iOS via rede local/Tailscale) e registrar a consolidação final do roadmap de responsividade.

**Independent Test**: Conferir roteiro operacional em `quickstart.md` e validar documentação consolidada de encerramento em `RETOMADA.md`.

- [x] T014 [US4] Consolidar roteiro de homologação em aparelho físico em specs/081-regressao-responsiva/quickstart.md
- [x] T015 [US4] Atualizar relatório de encerramento do marco de responsividade em docs/contexto/RETOMADA.md

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificações finais de qualidade de código, compilação e conformidade.

- [x] T016 [P] Validar conformidade de zero emojis em todos os arquivos da feature em specs/081-regressao-responsiva/ e caderno-leitura-0.1/frontend/tests/
- [x] T017 Validar compilação estrita de tipos via npm run build em caderno-leitura-0.1/frontend
- [x] T018 Executar suíte de testes de backend via pytest em caderno-leitura-0.1/backend

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências, inicia imediatamente.
- **Foundational (Phase 2)**: Depende da Phase 1; bloqueia a criação dos testes das histórias de usuário.
- **User Story 1 (Phase 3 - P1)**: Depende da Phase 2; estabelece o MVP.
- **User Story 2 (Phase 4 - P1)**: Depende da Phase 2; pode ser executada em paralelo ou em sequência a US1.
- **User Story 3 (Phase 5 - P2)**: Depende de US1 e US2 para integração completa da suíte de testes.
- **User Story 4 (Phase 6 - P2)**: Depende da validação das histórias anteriores.
- **Polish (Phase 7)**: Executado após todas as histórias de usuário estarem concluídas.

### Parallel Opportunities

- `T001` e `T002` podem rodar em paralelo na Phase 1.
- `T004` pode rodar em paralelo com `T003` na Phase 2.
- `T005` e `T006` podem ser implementados concorrentemente na Phase 3.
- `T008`, `T009` e `T010` podem ser implementados concorrentemente na Phase 4.
- `T011` e `T012` podem ser implementados concorrentemente na Phase 5.
- `T016` pode rodar em paralelo com `T017` e `T018` na Phase 7.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (Phase 1) e Foundational (Phase 2).
2. Implementar as asserções de US1 em `tests/feature-081-responsive-regression.test.mjs`.
3. Validar US1 isoladamente via `node --test tests/feature-081-responsive-regression.test.mjs`.

### Incremental Delivery
1. Setup + Foundational concluídos.
2. Adicionar asserções de US1 (Matriz de 25 rotas e 8 viewports) -> Validar.
3. Adicionar asserções de US2 (Rastreabilidade P-01 a P-19) -> Validar.
4. Adicionar asserções de US3 (Alvos táteis, breakpoints canônicos, npm test) -> Validar.
5. Consolidar US4 (Quickstart, RETOMADA.md) -> Validar.
6. Executar Polish (Zero emojis, npm run build, pytest).
