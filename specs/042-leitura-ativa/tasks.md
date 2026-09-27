# Tasks: F0.6.3 — Leitura Ativa

**Branch**: `042-leitura-ativa` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Definição de contratos de dados, interfaces TypeScript e tipos da sessão de estudo ativo.

- [X] T001 [P] Definir tipos TypeScript `ActiveStudyNode`, `ActiveReadingSessionState` e eventos de sessão em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Utilitários DOM e Métodos de Apoio)

**Purpose**: Utilitários centrais de manipulação não destrutiva no DOM e composable de sessão que bloqueiam as histórias de usuário.

- [X] T002 [P] Implementar métodos de manipulação em lote `setHighlightsRevealedState`, coleta `collectInteractiveHighlights` e rolagem focalizada `scrollAndFocusHighlight` em `caderno-leitura-0.1/frontend/src/utils/highlightRenderer.ts`
- [X] T003 Implementar composable `useActiveReadingSession.ts` com rastreamento reativo dos nós da aba ativa, contagem de revisados, comandos em lote e navegação em `caderno-leitura-0.1/frontend/src/composables/useActiveReadingSession.ts`

**Checkpoint**: Fundação e composable de sessão prontos — implementação das histórias de usuário pode prosseguir.

---

## Phase 3: User Story 1 - Sessão de Leitura Ativa Integrada ao Fichamento (Priority: P1) 🎯 MVP

**Goal**: Permitir ativar o modo de Leitura Ativa diretamente no leitor do estudo, com mascaramento inicial em lote e ações "Ocultar todos" e "Revelar todos".

**Independent Test**: Abrir um estudo com trechos interativos, clicar no botão "Leitura Ativa" no cabeçalho do leitor, verificar a aparição da barra de estudo ativo com todos os trechos mascarados e alternar entre "Revelar todos" e "Ocultar todos".

### Tests for User Story 1
- [X] T004 [P] [US1] Criar testes unitários para a sessão de leitura ativa e manipulação em lote em `caderno-leitura-0.1/frontend/tests/active-reading.test.mjs`

### Implementation for User Story 1
- [X] T005 [US1] Implementar componente `ActiveReadingBar.vue` com exibição de status, ações em massa (`Ocultar todos` e `Revelar todos`) e encerramento em `caderno-leitura-0.1/frontend/src/components/ActiveReadingBar.vue`
- [X] T006 [US1] Integrar botão acionador de Leitura Ativa com badge numérico em `caderno-leitura-0.1/frontend/src/components/ReaderTools.vue`
- [X] T007 [US1] Conectar `ActiveReadingBar.vue` e `useActiveReadingSession` ao leitor em `caderno-leitura-0.1/frontend/src/views/StudyView.vue` e `caderno-leitura-0.1/frontend/src/components/StudyTabs.vue`

**Checkpoint**: Sessão de Leitura Ativa operacional no leitor com controle em lote (MVP alcançado).

---

## Phase 4: User Story 2 - Interação Pontual de Revelação e Oclusão no Fluxo Textual (Priority: P1)

**Goal**: Permitir a revelação e oclusão pontual de termos e respostas no fluxo dos parágrafos, atualizando dinamicamente o status da sessão.

**Independent Test**: Clicar no botão `[Revelar]` de uma oclusão específica e constatar que apenas ela se torna legível, com atualização do contador da barra; clicar em `[Ver resposta]` de uma pergunta e constatar a exibição formatada.

### Tests for User Story 2
- [X] T008 [P] [US2] Adicionar testes de alternância pontual e atualização de progresso da sessão em `caderno-leitura-0.1/frontend/tests/active-reading.test.mjs`

### Implementation for User Story 2
- [X] T009 [US2] Conectar callbacks de clique pontual (`[Revelar]`/`[Ocultar]` e `[Ver resposta]`/`[Esconder resposta]`) para sincronizar instantaneamente o estado no `useActiveReadingSession.ts` em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Trechos individuais respondem instantaneamente ao clique e sincronizam o progresso da sessão.

---

## Phase 5: User Story 3 - Contador de Progresso e Navegação entre Trechos Interativos (Priority: P2)

**Goal**: Exibir contador de progresso e barra visual ("X de Y revisados"), e permitir navegação sequencial com rolagem suave e atalhos de teclado.

**Independent Test**: Navegar usando os botões "Anterior" / "Próximo" da barra ou as teclas `J` e `K`, conferindo a rolagem suave centralizada e a aplicação do anel de foco visual.

### Tests for User Story 3
- [X] T010 [P] [US3] Adicionar testes de navegação sequencial e foco cíclico em `caderno-leitura-0.1/frontend/tests/active-reading.test.mjs`

### Implementation for User Story 3
- [X] T011 [US3] Implementar indicador numérico de progresso, percentual e barra visual fina no componente `ActiveReadingBar.vue` em `caderno-leitura-0.1/frontend/src/components/ActiveReadingBar.vue`
- [X] T012 [US3] Implementar controles de navegação sequencial (`Anterior` e `Próximo`) e atalhos de teclado (`J`/`K` e `Escape`) em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Contador de progresso e navegação sequencial operando com atalhos de teclado.

---

## Phase 6: User Story 4 - Prática de Leitura Ativa em Estudos Compartilhados (Priority: P3)

**Goal**: Garantir que leitores convidados com acesso somente leitura consigam utilizar todas as ferramentas de Leitura Ativa sem restrições ou mutações no banco.

**Independent Test**: Abrir um estudo compartilhado com `canEdit = false`, acionar o modo de Leitura Ativa, interagir com todos os controles e verificar ausência de requisições de gravação.

### Tests for User Story 4
- [X] T013 [P] [US4] Adicionar teste de isolamento garantindo zero mutações ou requisições de escrita para usuários somente leitura em `caderno-leitura-0.1/frontend/tests/active-reading.test.mjs`

### Implementation for User Story 4
- [X] T014 [US4] Assegurar disponibilidade irrestrita de `ActiveReadingBar.vue` e `useActiveReadingSession` sob `canEdit === false` em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Leitura Ativa 100% funcional e segura em estudos compartilhados.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Acessibilidade, temas visuais e validação completa do sistema.

- [X] T015 [P] Ajustar estilos visuais da barra e anel de foco acessível para compatibilidade com os 10 temas visuais e modo E-Ink em `caderno-leitura-0.1/frontend/src/themes.css`
- [X] T016 [P] Garantir ergonomia móvel e alvos táteis mínimos ($\ge 44 \times 44\text{px}$) no mobile (`<= 768px`) em `caderno-leitura-0.1/frontend/src/components/ActiveReadingBar.vue`
- [X] T017 Executar suítes completas de testes no frontend (`npm test`), testes de integridade do backend (`pytest`) e compilação limpa do TypeScript e Vite (`npm run build`)
- [X] T018 Executar roteiro de validação manual conforme `specs/042-leitura-ativa/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA a execução de todas as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende da conclusão da Phase 2 (Foundational).
- **User Story 2 (Phase 4)**: Depende da Phase 3 (US1 - Barra e acionador integrados).
- **User Story 3 (Phase 5)**: Depende da Phase 3 e Phase 4.
- **User Story 4 (Phase 6)**: Depende da Phase 3.
- **Polish (Phase 7)**: Depende da conclusão das histórias de usuário.

---

## Parallel Opportunities

- **Phase 1**: T001 (Tipos TypeScript).
- **Phase 2**: T002 (Utilitários DOM) e T003 (Composable) podem ter lógica desenvolvida em paralelo.
- **Phase 3**: T004 (Testes de sessão) pode rodar em paralelo com T005 / T006.
- **Phase 4**: T008 (Testes de clique pontual) pode rodar em paralelo com T009.
- **Phase 5**: T010 (Testes de navegação) pode rodar em paralelo com T011 / T012.
- **Phase 7**: T015 (Temas e E-Ink) e T016 (Ergonomia móvel) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (Phase 1) e Foundational (Phase 2).
2. Implementar sessão de Leitura Ativa no leitor e controle em lote (Phase 3 - US1).
3. **STOP and VALIDATE**: Testar ativação, "Ocultar todos" e "Revelar todos".

### Incremental Delivery
1. Foundation pronta (Phase 1 + 2).
2. US1 entrega a barra de estudo ativo e oclusão em lote (MVP).
3. US2 adiciona feedback pontual e sincronização dinâmica com o progresso.
4. US3 adiciona contador numérico, barra de progresso e atalhos de teclado `J`/`K`.
5. US4 consolida a experiência de revisão em estudos compartilhados.
6. Phase 7 refina acessibilidade móvel, temas e validações completas do quickstart.
