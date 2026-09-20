# Tasks: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Declaração de interfaces TypeScript e tokens CSS de dimensões.

- [X] T001 Declarar interfaces e tipos TypeScript (`PaneId`, `LayoutMode`, `PaneConfig`, `PaneState`, `SplitLayoutDimensions`) em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T002 Declarar variáveis e tokens CSS para larguras e divisores de split pane (`--pane-left-width`, `--pane-right-width`, `--gutter-width`, `--pane-min-width`, `--pane-max-width`) em `caderno-leitura-0.1/frontend/src/tokens.css`

---

## Phase 2: Foundational (Componentes Base de Layout)

**Purpose**: Infraestrutura reativa e componentes de layout que sustentam todas as histórias de usuário.

**CRITICAL**: Nenhuma alteração nas views pode iniciar antes da conclusão desta fase.

- [X] T003 Criar composable `useSplitPanes.ts` com gestão reativa de larguras, cálculo de limites min/max, arrasto nativo via `PointerEvents` e persistência híbrida em `localStorage` em `caderno-leitura-0.1/frontend/src/composables/useSplitPanes.ts`
- [X] T004 [P] Criar componente de divisória interativa `SplitGutter.vue` com captura de ponteiro (`setPointerCapture`), reset por duplo clique e botões de alternância rápida de colapso em `caderno-leitura-0.1/frontend/src/components/layout/SplitGutter.vue`
- [X] T005 [P] Criar componente de painel individual `SplitPane.vue` com controle de estados (`.is-collapsed`, `.is-resizing`) e transições em `caderno-leitura-0.1/frontend/src/components/layout/SplitPane.vue`
- [X] T006 Criar componente contêiner `SplitLayout.vue` articulando as três colunas (navegação, palco central e inspetor) com slots nomeados em `caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue`

**Checkpoint**: Componentes de split layout prontos para integração e validação de histórias de usuário.

---

## Phase 3: User Story 1 - Redimensionamento e Colapso de Painéis no Desktop com Persistência (Priority: P1) 🎯 MVP

**Goal**: Permitir que leitores em ambiente desktop ajustem a largura das colunas por arrasto, recolham painéis com um clique, restaurem dimensões padrão e preservem preferências no `localStorage`.

**Independent Test**: Abrir a visão de um livro no desktop, arrastar a divisória esquerda para alargar o navegador, colapsar o painel direito, recarregar a página e confirmar que as larguras e estados persistem íntegros.

### Testes para User Story 1

- [X] T007 [P] [US1] Criar suíte de testes unitários para o composable `useSplitPanes.ts` cobrindo arrasto, limites (240px a 600px), snap-to-collapse e persistência híbrida em `caderno-leitura-0.1/frontend/tests/split-panes.test.mjs`

### Implementação para User Story 1

- [X] T008 [US1] Implementar neutralização de seleção de texto (`.split-resizing` com `user-select: none; cursor: col-resize`) durante o arrasto de divisores em `caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue`
- [X] T009 [US1] Implementar persistência híbrida de larguras (`caderno_pane_sizes_global` e `caderno_pane_sizes_book_{id}`) com precedência por livro em `caderno-leitura-0.1/frontend/src/composables/useSplitPanes.ts`
- [X] T010 [US1] Refatorar `BookView.vue` integrando `SplitLayout` para hospedar o navegador de capítulos na coluna esquerda e a área de leitura/estudos no palco central em `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: MVP funcional! Três colunas com redimensionamento, colapso e persistência operando no desktop.

---

## Phase 4: User Story 2 - Acessibilidade e Ajuste Ergonômico por Teclado (Priority: P2)

**Goal**: Garantir conformidade WAI-ARIA completa para tecnologia assistiva e navegação por teclado sem mouse nas barras divisoras.

**Independent Test**: Navegar por Tab até a barra divisora, validar foco de alto contraste e usar setas direcionais para alterar dimensões em passos de 10px.

### Testes para User Story 2

- [X] T011 [P] [US2] Adicionar testes unitários para redimensionamento por teclado (passos de 10px com setas, Home/End para min/max, Enter para alternar colapso) em `caderno-leitura-0.1/frontend/tests/split-panes.test.mjs`

### Implementação para User Story 2

- [X] T012 [US2] Implementar semântica WAI-ARIA (`role="separator"`, `tabindex="0"`, `aria-orientation="vertical"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`) e atalhos de teclado no divisor em `caderno-leitura-0.1/frontend/src/components/layout/SplitGutter.vue`
- [X] T013 [US2] Estilizar foco acessível visível (`focus-visible`) nos divisores e botões de alternância de colapso em conformidade com o tema ativo em `caderno-leitura-0.1/frontend/src/components/layout/SplitGutter.vue`

**Checkpoint**: Divisores 100% operáveis por teclado e compatíveis com leitores de tela.

---

## Phase 5: User Story 3 - Adaptação Responsiva e Gavetas Deslizantes em Tablets e Celulares (Priority: P3)

**Goal**: Adaptar o layout de três colunas para gavetas sobrepostas suaves em tablets e gavetas deslizantes completas (*drawers*) em smartphones.

**Independent Test**: Reduzir a viewport para largura mobile (390px) e confirmar que o palco de leitura ocupa a tela inteira, com botões táteis acionando gavetas de navegação e contexto.

### Testes para User Story 3

- [X] T014 [P] [US3] Adicionar testes unitários para comutação reativa de layout (`split`, `drawer`, `mobile`) conforme dimensões de tela em `caderno-leitura-0.1/frontend/tests/split-panes.test.mjs`

### Implementação para User Story 3

- [X] T015 [US3] Implementar modo gaveta (*drawer/bottom sheet*) com backdrop, animação suave e fechamento por toque externo para telas móveis em `caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue`
- [X] T016 [US3] Integrar botões de acionamento das gavetas com área de toque ergonômica mínima de 44x44px no cabeçalho e barra móvel em `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [X] T017 [US3] Configurar supressão automática das barras divisoras de arrasto em resoluções inferiores a 768px em `caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue`

**Checkpoint**: Experiência responsiva completa e ergonômica do desktop ao celular.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Harmonização de estilo, testes de regressão e compilação de produção.

- [X] T018 Calibrar transições suaves de colapso e expansão respeitando as 5 Superclasses de interface e a diretriz `@media (prefers-reduced-motion: reduce)` em `caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue`
- [X] T019 Executar build estrito de produção do frontend via `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T020 Executar suíte completa de testes automatizados do frontend via `npm test` e do backend via `pytest`
- [X] T021 Validar acessibilidade e cenários manuais ponta a ponta conforme `specs/018-paineis-redimensionaveis/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (Tipos e Tokens)
   └──> Phase 2: Foundational (useSplitPanes, SplitGutter, SplitPane, SplitLayout)
           ├──> Phase 3: User Story 1 (P1 - Desktop Drag & Persistência) [MVP]
           ├──> Phase 4: User Story 2 (P2 - Acessibilidade por Teclado WAI-ARIA)
           └──> Phase 5: User Story 3 (P3 - Adaptação Mobile e Gavetas)
                   └──> Phase 6: Polish & Cross-Cutting Concerns
```

### User Story Dependencies

- **User Story 1 (P1)**: Depende apenas da Fase 2. Entrega o MVP funcional com arrasto, limites físicos e persistência.
- **User Story 2 (P2)**: Depende da Fase 2 e enriquece o `SplitGutter` com eventos de teclado e WAI-ARIA.
- **User Story 3 (P3)**: Depende da Fase 2 e adiciona a camada de responsividade mobile ao `SplitLayout`.

### Parallel Opportunities

- `T004` (`SplitGutter.vue`) e `T005` (`SplitPane.vue`) podem ser criados em paralelo.
- `T007` (testes US1), `T011` (testes US2) e `T014` (testes US3) podem ser elaborados em paralelo.

---

## Parallel Example: User Story 1

```bash
# Teste unitário e estilos utilitários podem ser desenvolvidos em paralelo:
Task: "Criar suíte de testes unitários em caderno-leitura-0.1/frontend/tests/split-panes.test.mjs"
Task: "Implementar neutralização de seleção de texto em caderno-leitura-0.1/frontend/src/components/layout/SplitLayout.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Setup de tipos e tokens CSS).
2. Concluir Phase 2 (Foundational: composable e componentes de layout).
3. Concluir Phase 3 (User Story 1: integração no `BookView.vue` com arrasto e persistência).
4. **Validar MVP**: Testar redimensionamento por mouse no desktop com limites seguros e persistência em `localStorage`.

### Incremental Delivery

1. Setup + Foundational -> Estrutura base pronta.
2. US1 -> Desktop drag & drop e colapso operacional (MVP).
3. US2 -> Navegação por teclado acessível via setas e WAI-ARIA.
4. US3 -> Gavetas responsivas para smartphones e tablets.
5. Polish -> Validação com Superclasses, `npm run build` e suíte completa de testes.
