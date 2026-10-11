# Tasks: Lixeira — Arquivo de Salvaguarda e Segurança

**Feature**: `073-lixeira-arquivo-salvaguarda`  
**Spec**: [specs/073-lixeira-arquivo-salvaguarda/spec.md](spec.md)  
**Plan**: [specs/073-lixeira-arquivo-salvaguarda/plan.md](plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura de tipos TypeScript e contratos compartilhados para gestão da lixeira

- [x] T001 [P] Definir tipos e interfaces de itens de lixeira, chaves de seleção e métricas de retenção em `caderno-leitura-0.1/frontend/src/types/trash.ts`
- [x] T002 [P] Exportar os tipos de lixeira no arquivo central `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Componentes base de salvaguarda e suíte de testes de componente

**CRITICAL**: As histórias de usuário dependem do modal com acessibilidade reforçada e da suíte de testes da feature

- [x] T003 [P] Aprimorar `TrashConfirmModal.vue` com suporte a `role="alertdialog"`, variáveis semânticas de perigo e foco padrão no botão cancelar em `caderno-leitura-0.1/frontend/src/components/TrashConfirmModal.vue`
- [x] T004 [P] Criar suíte de testes de validação automatizada em `caderno-leitura-0.1/frontend/tests/feature-073-lixeira-salvaguarda.test.mjs`

**Checkpoint**: Fundação pronta - componentes de diálogo e suíte de testes configurados

---

## Phase 3: User Story 1 - Visão de Custódia e Contagem Regressiva Temporal (Priority: P1) — MVP

**Goal**: Apresentar os cartões de itens descartados com hierarquia clara, distinção Livro/Estudo e contagem regressiva visual dos 30 dias com alerta de urgência

**Independent Test**: Acessar `/lixeira` com itens descartados e verificar a renderização dos cartões, tipo, metadados e o badge com barra de progresso e destaque para $\le 5$ dias

- [x] T005 [US1] Implementar cálculo das métricas de retenção (`daysRemaining`, `elapsedPercentage`, `isUrgent`) em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- [x] T006 [US1] Redesenhar os cartões de Livro e Estudo em `caderno-leitura-0.1/frontend/src/views/TrashView.vue` com tipo explícito, hierarquia de origem (`Livro ancestral > Capítulo`) e indicador visual de retenção
- [x] T007 [US1] Adicionar estilos do badge de retenção temporal, barra de progresso inferior e classe de urgência em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`

**Checkpoint**: MVP funcional — visualização dos cartões com custódia de 30 dias e contagem regressiva operando

---

## Phase 4: User Story 2 - Seleção em Lote e Barra Flutuante de Ações Múltiplas (Priority: P2)

**Goal**: Permitir seleção individual e múltipla de itens descartados com barra flutuante inferior para comandos em lote

**Independent Test**: Marcar caixas de seleção, confirmar exibição da barra flutuante com a contagem, testar seleção total e acionar restauração em lote

- [x] T008 [US2] Adicionar caixas de seleção acessíveis (`checkbox`) em cada cartão de item descartado com rótulos descritivos em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- [x] T009 [US2] Implementar estado reativo de seleção (`selectedKeys`) e controles de selecionar/desmarcar todos da aba ativa em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- [x] T010 [US2] Implementar a barra flutuante de ações em lote (`.trash-batch-bar`) com animação de subida (200ms), contador e botões em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- [x] T011 [US2] Implementar a ação de restauração em lote com execução paralela, indicador de carregamento e notificação de sucesso em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`

**Checkpoint**: Histórias 1 e 2 operando com seleção e restauração em massa

---

## Phase 5: User Story 3 - Proteção Reforçada e Barreira Contra Expurgo Acidental (Priority: P3)

**Goal**: Proteger o esvaziamento total e a exclusão definitiva em lote com diálogos modais de confirmação deliberada

**Independent Test**: Clicar em "Esvaziar lixeira" ou "Excluir definitivamente" na barra de lote, confirmar mensagem quantitativa detalhada e verificar cancelamento via tecla Escape

- [x] T012 [US3] Atualizar a mensagem do modal de esvaziamento total em `caderno-leitura-0.1/frontend/src/views/TrashView.vue` detalhando a quantidade de livros e estudos a serem purgados
- [x] T013 [US3] Implementar modal de confirmação reforçada para a ação de exclusão definitiva em lote disparada pela barra flutuante em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`

**Checkpoint**: Barreira deliberada contra perda acidental ativa em 100% dos fluxos destrutivos

---

## Phase 6: User Story 4 - Restauração Fluida e Resolução de Dependências (Priority: P4)

**Goal**: Oferecer animação suave de saída na restauração individual e notificação clara sobre reativação de livro ancestral

**Independent Test**: Restaurar um estudo cujo livro estava na lixeira e confirmar animação de saída de 180ms e mensagem informativa no toast

- [x] T014 [US4] Implementar a transição suave de saída de 180ms (`.is-restoring`) com elevação e desvanecimento na restauração de itens em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`
- [x] T015 [US4] Integrar feedback específico para estudos cujo livro de origem foi reativado no acervo em `caderno-leitura-0.1/frontend/src/views/TrashView.vue`

**Checkpoint**: Todas as 4 histórias de usuário concluídas e integradas com máxima fluidez e segurança

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação completa de acessibilidade, testes automatizados e compilação

- [x] T016 Executar e aprovar a suíte `feature-073-lixeira-salvaguarda.test.mjs` e testes de regressão visual em `caderno-leitura-0.1/frontend`
- [x] T017 Executar build de produção (`npm run build`) e suítes completas (`npm test` e `pytest`) garantindo 100% de sucesso

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Concluída com sucesso.
- **Phase 2 (Foundational)**: Concluída com sucesso.
- **Phase 3 (User Story 1 - MVP)**: Concluída com sucesso.
- **Phase 4 (User Story 2)**: Concluída com sucesso.
- **Phase 5 (User Story 3)**: Concluída com sucesso.
- **Phase 6 (User Story 4)**: Concluída com sucesso.
- **Phase 7 (Polish)**: Concluída com sucesso.

### Parallel Opportunities
- T001 e T002 desenvolvidos em paralelo com T003 e T004.
- Testes automatizados em T004 escritos em paralelo com aprimoramento de componentes.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001 - T002) e Foundational (T003 - T004).
2. Completar User Story 1 (T005 - T007).
3. Validar de forma independente a visualização de retenção temporal e urgência ($\le 5$ dias).

### Entrega Incremental
1. MVP entregue (visão da lixeira informativa e acolhedora com contagem regressiva).
2. Adição da User Story 2 (seleção múltipla e barra flutuante de ações em lote).
3. Adição da User Story 3 (proteção reforçada em esvaziamento e expurgo em lote).
4. Adição da User Story 4 (animação fluida de saída de 180ms e resolução de dependências).
5. Polimento final e suítes de testes globais 100% GREEN.
