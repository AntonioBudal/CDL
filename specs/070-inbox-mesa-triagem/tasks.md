# Tasks: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Branch**: `070-inbox-mesa-triagem` | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/070-inbox-mesa-triagem/spec.md) | **Plan**: [plan.md](file:///c:/Users/User/caderno/specs/070-inbox-mesa-triagem/plan.md)

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Preparação de tipos e criação da suíte inicial de testes de contrato da Feature F0.8.04.

- [x] T001 [P] Declarar tipos e enums de triagem (TriageFilterTab, TriageKeyboardState) em caderno-leitura-0.1/frontend/src/types.ts
- [x] T002 [P] Criar suíte de testes de contrato e integração da Feature 070 em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

---

## Phase 2: Foundational (Pré-Requisitos Bloqueantes)

**Purpose**: Infraestrutura de estado reativo e contagem do Inbox compartilhada entre todas as histórias.

- [x] T003 Aprimorar composable useInboxCount em caderno-leitura-0.1/frontend/src/composables/useInboxCount.ts para suportar atualização de contagem síncrona/reativa e decremento seguro

**Checkpoint**: Base de tipos e composables pronta — a implementação das histórias de usuário pode iniciar.

---

## Phase 3: User Story 1 - Despejo Rápido Permanente no Topo (*Quick Thought Drop*) (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor digite pensamentos instantaneamente no topo de `/inbox` sem modais e salve via `Ctrl+Enter` (e `Cmd+Enter`), inserindo a nota imediatamente no topo da fila de pendentes.

**Independent Test**: Acessar `/inbox`, digitar no campo superior permanente, pressionar `Ctrl+Enter` e confirmar inserção da nota no topo da lista sem recarga de página.

### Tests for User Story 1

- [x] T004 [P] [US1] Adicionar testes unitários/contrato para QuickThoughtDrop (expansão, atalho Ctrl+Enter, rejeição de texto vazio) em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

### Implementation for User Story 1

- [x] T005 [P] [US1] Criar componente QuickThoughtDrop.vue com textarea expansível (:focus-within), atalho Ctrl+Enter/Cmd+Enter e botão editorial em caderno-leitura-0.1/frontend/src/components/inbox/QuickThoughtDrop.vue
- [x] T006 [US1] Integrar QuickThoughtDrop.vue no topo de InboxView.vue conectando a inserção imediata de novas capturas em caderno-leitura-0.1/frontend/src/views/InboxView.vue

**Checkpoint**: User Story 1 funcional de forma independente. O descarrego mental opera com zero atrito (MVP entregue).

---

## Phase 4: User Story 2 - Barra Segmentada de Triagem com Contadores Dinâmicos (Priority: P1) 🎯 MVP

**Goal**: Exibir uma barra segmentada com contadores em tempo real para os 5 estados (`Pendentes`, `Promovidos`, `Vinculados`, `Arquivados`, `Todos`) com acessibilidade WAI-ARIA.

**Independent Test**: Alternar entre os segmentos da barra, validar filtragem imediata e verificar que o contador reflete a contagem precisa de pendências.

### Tests for User Story 2

- [x] T007 [P] [US2] Adicionar testes de contrato para a barra segmentada e contadores dinâmicos em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

### Implementation for User Story 2

- [x] T008 [US2] Implementar barra segmentada de triagem com role="tablist", contadores dinâmicos e scroll horizontal móvel em caderno-leitura-0.1/frontend/src/views/InboxView.vue

**Checkpoint**: User Stories 1 e 2 operando integradas com navegação segmentada fluida.

---

## Phase 5: User Story 3 - Triagem Contextual com Transição Cinética Suave (Priority: P1) 🎯 MVP

**Goal**: Disponibilizar ferramentas contextuais de triagem (Promover, Vincular, Arquivar/Desarquivar, Excluir) no cartão e executar transição cinética de saída acelerada por GPU (`transform: translateX(30px)`, `opacity: 0`, 180ms).

**Independent Test**: Clicar em "Arquivar" em um cartão pendente e validar que o item desliza com desvanecimento suave em 180ms e a lista se reorganiza sem saltos abruptos.

### Tests for User Story 3

- [x] T009 [P] [US3] Adicionar testes de contrato para ações de triagem (arquivar, desarquivar, transição cinética) no CaptureItemCard em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

### Implementation for User Story 3

- [x] T010 [US3] Redesenhar CaptureItemCard.vue adicionando botões de arquivar/desarquivar, animação cinética de saída (.is-exiting) e tokens semânticos em caderno-leitura-0.1/frontend/src/components/inbox/CaptureItemCard.vue
- [x] T011 [US3] Conectar o ciclo de vida de saída cinética (180ms) e persistência de arquivamento no container de capturas em caderno-leitura-0.1/frontend/src/views/InboxView.vue

**Checkpoint**: Mesa de triagem completa e funcional com ações diretas e feedback tátil fluido.

---

## Phase 6: User Story 4 - Operação 100% por Teclado e Acessibilidade (Priority: P2)

**Goal**: Permitir processamento em lote rápido por teclado (`J`/`K` para percorrer notas, `E` para arquivar, `Ctrl+Shift+C` para focar a captura) com anel de foco e guarda defensiva estrita.

**Independent Test**: Percorrer notas via teclas `J`/`K`, arquivar nota selecionada via `E`, e saltar para o campo de captura via `Ctrl+Shift+C`.

### Tests for User Story 4

- [x] T012 [P] [US4] Adicionar testes de navegação por teclado (J, K, E, Ctrl+Shift+C e guarda em inputs) em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

### Implementation for User Story 4

- [x] T013 [US4] Adicionar indicador visual de seleção por teclado (is-keyboard-selected) e anel de foco em caderno-leitura-0.1/frontend/src/components/inbox/CaptureItemCard.vue
- [x] T014 [US4] Implementar listener de teclado global na tela com navegação J/K, arquivamento E, foco Ctrl+Shift+C e guarda contra campos de texto em caderno-leitura-0.1/frontend/src/views/InboxView.vue

**Checkpoint**: Mesa de triagem 100% operável via teclado com suporte a atalhos ergonômicos.

---

## Phase 7: User Story 5 - Estado Vazio "Mesa Limpa" e Tratamento Elegante de Erros (Priority: P3)

**Goal**: Exibir estado visual acolhedor ("Mesa Limpa" serena, zero emojis) e substituir mensagens técnicas cruas por cartão editorial acessível em caso de falha de conexão.

**Independent Test**: Esvaziar pendências e validar mensagem editorial "Mesa Limpa"; simular erro de conexão e confirmar exibição do cartão com `role="alert"` e botão "Tentar Novamente".

### Tests for User Story 5

- [x] T015 [P] [US5] Adicionar testes para o estado vazio Mesa Limpa e tratamento editorial de erro em caderno-leitura-0.1/frontend/tests/feature-070-inbox-mesa-triagem.test.mjs

### Implementation for User Story 5

- [x] T016 [US5] Implementar estado vazio editorial "Mesa Limpa" (zero emojis, ícone vetorial) e cartão editorial de falha de conexão com role="alert" em caderno-leitura-0.1/frontend/src/views/InboxView.vue

**Checkpoint**: Experiência visual refinada tanto no êxito quanto na recuperação de falhas.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificações finais de imunidade cromática, conformidade com os 10 temas, ergonomia móvel e validação integrada.

- [x] T017 [P] Garantir imunidade cromática total (zero hexadecimais fixos, 100% variáveis CSS semânticas) em caderno-leitura-0.1/frontend/src/views/InboxView.vue e caderno-leitura-0.1/frontend/src/components/inbox/CaptureItemCard.vue
- [x] T018 [P] Validar alvos de toque móveis (min-height e min-width >= 44px) em todos os botões de ação de caderno-leitura-0.1/frontend/src/views/InboxView.vue
- [x] T019 Executar suíte completa de testes automatizados (npm test, npm run build, pytest) validando quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup (Phase 1) — BLOQUEIA as histórias de usuário.
- **User Stories (Phase 3 a Phase 7)**:
  - US1 (Phase 3 - P1): Depende da Phase 2. Não depende de outras histórias.
  - US2 (Phase 4 - P1): Depende da Phase 2 e integra com US1 no `InboxView.vue`.
  - US3 (Phase 5 - P1): Depende da Phase 2 e atua sobre `CaptureItemCard.vue`.
  - US4 (Phase 6 - P2): Depende de US1 e US3 para navegar e arquivar cartões.
  - US5 (Phase 7 - P3): Depende de US2 e US3 (renderiza quando contagem de pendências = 0).
- **Polish (Phase 8)**: Depende da conclusão de todas as histórias.

### User Story Dependencies

```
Phase 1 (Setup) ──> Phase 2 (Foundational)
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
Phase 3 (US1: Quick Drop) Phase 4 (US2: Segmentos) Phase 5 (US3: Triagem Cartão)
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                  Phase 6 (US4: Teclado)
                           │
                           ▼
                  Phase 7 (US5: Mesa Limpa / Erros)
                           │
                           ▼
                  Phase 8 (Polish)
```

---

## Parallel Opportunities

- **Tarefas de Setup e Testes**: T001 e T002 podem ser executadas em paralelo.
- **Testes por História**: T004, T007, T009, T012 e T015 podem ser preparados em paralelo.
- **Componentes Independentes**: A criação de `QuickThoughtDrop.vue` (T005) e a refatoração inicial de `CaptureItemCard.vue` (T010) podem ocorrer de forma paralela antes da orquestração em `InboxView.vue`.
- **Refinamento Final**: T017 (imunidade cromática) e T018 (alvos móveis) podem rodar em paralelo antes da validação geral (T019).

---

## Implementation Strategy

### MVP First (Foco Inicial: US1 + US2 + US3)
1. Concluir Setup (T001-T002) e Foundational (T003).
2. Implementar US1 (T004-T006): Quick Thought Drop funcional com `Ctrl+Enter`.
3. Implementar US2 (T007-T008): Barra segmentada e contadores.
4. Implementar US3 (T009-T011): Ações de triagem direta e animação de saída.
5. **Validar MVP**: `npm test` e verificação manual básica do fluxo de triagem.

### Entrega Incremental
6. Implementar US4 (T012-T014): Navegação e arquivamento por teclado (`J`/`K`/`E`).
7. Implementar US5 (T015-T016): Estado "Mesa Limpa" e tratamento editorial de falhas.
8. Polish (T017-T019): Imunidade aos 10 temas, toque móvel $\ge 44$px e suítes completas aprovadas (`npm test`, `npm run build`, `pytest backend/tests`).
