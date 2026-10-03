# Tasks: Responsividade Mobile, Toque Nativo e Micro-Toast de Ferramentas

**Feature**: `051-mobile-toque-microtoast`  
**Input**: [spec.md](spec.md) | [plan.md](plan.md) | [data-model.md](data-model.md) | [research.md](research.md) | [contracts/](contracts/)  
**Status**: Concluído

---

## Phase 1: Setup (Infraestrutura Compartilhada e Tipagens)

**Purpose**: Estruturar as tipagens TypeScript e o esqueleto do composable de notificação.

- [X] T001 [P] Criar tipagens e interfaces para micro-toast e toque em `frontend/src/types/toast.ts`
- [X] T002 [P] Criar esqueleto do composable `useFloatingToast.ts` em `frontend/src/composables/useFloatingToast.ts`

---

## Phase 2: Foundational (Composable useFloatingToast e Testes de Feedback)

**Purpose**: Construir e testar o composable reativo `useFloatingToast.ts` que gerencia a exibição e temporização do micro-toast.

- [X] T003 Implementar reatividade, timers de 1.8s e cancelamento/substituição atômica em `frontend/src/composables/useFloatingToast.ts`
- [X] T004 [P] Criar testes unitários para a máquina de estados do toast em `frontend/tests/floating_toast.test.mjs`

**Checkpoint**: Composable `useFloatingToast` funcional e testado isoladamente.

---

## Phase 3: User Story 1 - Seleção Rápida de Palavra por Duplo Toque (Priority: P1)

**Goal**: Permitir seleção ágil de palavras por duplo toque/duplo clique sem atrito de alças manuais ou cancelamentos por scroll acidental.

**Independent Test**: Simular dois toques rápidos com menos de 320ms de intervalo sobre o texto e verificar que a palavra é selecionada e o contexto é preenchido.

- [X] T005 [US1] Implementar rastreamento de duplo toque e tolerância a rolagem em `frontend/src/composables/useTextSelection.ts`
- [X] T006 [US1] Adicionar resolução de limites de palavras sob o ponto de toque no leitor em `frontend/src/composables/useTextSelection.ts`
- [X] T007 [P] [US1] Criar testes unitários para a lógica de detecção de duplo toque em `frontend/tests/mobile_touch_selection.test.mjs`

**Checkpoint**: Seleção por duplo toque mobile funcionando com alta precisão e tolerância a scroll.

---

## Phase 4: User Story 2 - Barra Mobile com Ícones Puros de 44x44px (Priority: P1) 🎯 MVP

**Goal**: Converter a barra de ações flutuante mobile para exibir exclusivamente ícones táteis de 44x44px, ocultando legendas textuais.

**Independent Test**: Emular viewport móvel (< 768px), inspecionar a barra de ferramentas e conferir que os textos estão ocultos, os ícones têm 44x44px e atributos `aria-label` estão preservados.

- [X] T008 [US2] Reestruturar botões da barra flutuante em `frontend/src/components/FloatingActionsToolbar.vue` para envolver legendas em tags identificáveis
- [X] T009 [US2] Ocultar legendas no modo mobile e assegurar dimensões táteis mínimas de 44x44px em `frontend/src/components/FloatingActionsToolbar.vue`
- [X] T010 [US2] Ajustar paleta de cores para botões táteis ampliados no mobile em `frontend/src/components/FloatingActionsToolbar.vue`

**Checkpoint**: Barra flutuante mobile limpa, moderna, sem sobrecargas de texto e ergonômica.

---

## Phase 5: User Story 3 - Micro-Toast Flutuante no Topo da Aba de Leitura (Priority: P1)

**Goal**: Exibir notificação flutuante elegante no topo do leitor por 1.8 segundos ao acionar qualquer ferramenta no celular.

**Independent Test**: Disparar ações da barra (Marca-texto, Oclusão, Citação) e verificar que uma div com mensagem correspondente surge no topo do leitor e fecha suavemente em 1.8s com `pointer-events: none`.

- [X] T011 [US3] Integrar composable `useFloatingToast` no template de `frontend/src/views/StudyView.vue` posicionado no topo (`top: 1rem`)
- [X] T012 [US3] Conectar eventos da barra de ferramentas (`@highlight`, `@copy-quote`, `@occlude`) ao disparo do micro-toast com mensagens canônicas em `frontend/src/views/StudyView.vue`
- [X] T013 [US3] Estilizar o micro-toast com `pointer-events: none`, transições suaves e semântica de leitor de tela em `frontend/src/views/StudyView.vue`

**Checkpoint**: Micro-toast funcional, não invasivo e visualmente integrado ao design editorial do leitor.

---

## Phase 6: User Story 4 - Submenus e Prompts Móveis de Anotação e Pergunta (Priority: P2)

**Goal**: Garantir que as caixas de entrada de anotação e pergunta se adaptem com conforto no celular sem transbordar a tela.

**Independent Test**: Abrir os formulários de anotação e pergunta no mobile, preencher texto e verificar fechamento e confirmação por toast.

- [X] T014 [US4] Ajustar layout móvel dos prompts de anotação e pergunta em `frontend/src/components/FloatingActionsToolbar.vue` para evitar transbordamento com teclado virtual
- [X] T015 [US4] Disparar micro-toast ao confirmar anotação ou criação de pergunta em `frontend/src/views/StudyView.vue`

**Checkpoint**: Prompts móveis confortáveis e integrados ao ciclo de feedback.

---

## Phase 7: Polish & Validação Global

**Purpose**: Testes integrados, compilação de produção e auditoria final.

- [X] T016 [P] Criar testes de integração e contrato mobile em `frontend/tests/mobile_toolbar_actions.test.mjs`
- [X] T017 Executar validação automatizada completa (`npm test` e `npm run build`), assegurando zero regressão e conformidade com `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Pode iniciar imediatamente.
- **Phase 2 (Foundational)**: Depende da Phase 1.
- **Phase 3 (User Story 1)**: Pode iniciar após Phase 1.
- **Phase 4 (User Story 2)**: Pode rodar em paralelo ou após Phase 3.
- **Phase 5 (User Story 3)**: Depende da Phase 2 e Phase 4.
- **Phase 6 (User Story 4)**: Depende da Phase 4 e 5.
- **Phase 7 (Polish)**: Depende de todas as fases anteriores.

---

## Implementation Strategy

### MVP First (User Story 2 & 3)
1. Completar Setup e Foundational (`T001` a `T004`).
2. Implementar ícones puros na barra mobile (`T008` a `T010`).
3. Integrar micro-toast no topo do leitor (`T011` a `T013`).
4. **Validar MVP**: Confirmar que a barra mobile ficou limpa e o leitor recebe confirmações elegantes no topo da tela.

### Incrementos
1. Adicionar seleção por duplo toque (`US1`).
2. Refinar prompts móveis de anotação e pergunta (`US4`).
3. Executar bateria de testes completa (`T016`, `T017`).
