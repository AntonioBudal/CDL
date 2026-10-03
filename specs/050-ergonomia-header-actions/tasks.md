# Tasks: Hierarquia e Ergonomia de Header Actions no Leitor

**Feature**: `050-ergonomia-header-actions`  
**Input**: [spec.md](spec.md) | [plan.md](plan.md) | [data-model.md](data-model.md) | [research.md](research.md) | [contracts/](contracts/)  
**Status**: Completed (18/18 tarefas concluídas)

---

## Phase 1: Setup (Infraestrutura Compartilhada e Tipagens)

**Purpose**: Estruturar as tipagens TypeScript e o esqueleto do componente modular.

- [x] T001 [P] Criar interfaces TypeScript para itens e contratos do menu suspenso em `frontend/src/types/dropdown.ts`
- [x] T002 [P] Criar esqueleto do componente `DropdownMenu.vue` em `frontend/src/components/ui/DropdownMenu.vue`

---

## Phase 2: Foundational (Componente Reutilizável DropdownMenu)

**Purpose**: Construir e testar o componente modular `DropdownMenu.vue` que serve a todas as histórias de usuário.

- [x] T003 Implementar markup, estado reativo aberto/fechado, slots (`trigger`, `default`) e props em `frontend/src/components/ui/DropdownMenu.vue`
- [x] T004 Implementar detecção de clique externo (`click-outside`) e fechamento defensivo com `Escape` em `frontend/src/components/ui/DropdownMenu.vue`
- [x] T005 [P] Criar testes unitários para montagem e abertura/fechamento em `frontend/tests/dropdown_menu.test.mjs`

**Checkpoint**: Componente `DropdownMenu.vue` funcional e testado isoladamente. As histórias de usuário podem ser implementadas.

---

## Phase 3: User Story 1 - Experiência Desktop: Hierarquia Editorial e Ação Primária (Priority: P1) 🎯 MVP

**Goal**: Transformar a barra de ações desktop de `StudyView.vue` em uma hierarquia limpa com "Editar estudo" primário, "Compartilhar" secundário e utilitários colapsados no menu `•••`.

**Independent Test**: Abrir um estudo no desktop (≥ 768px), verificar destaque de "Editar estudo", visibilidade de "Compartilhar" e verificar que "Histórico", "Exportar" e "Lixeira" estão acessíveis via dropdown `•••`.

- [x] T006 [US1] Reestruturar markup do cabeçalho em `frontend/src/views/StudyView.vue` definindo botão primário de destaque para "Editar estudo", botão secundário "Compartilhar" e integrando `DropdownMenu.vue`
- [x] T007 [US1] Configurar opções secundárias ("Histórico de versões", "Exportar estudo", "Mover para a lixeira") com ícones e variante danger dentro do `DropdownMenu` em `frontend/src/views/StudyView.vue`
- [x] T008 [US1] Ajustar estilos CSS do cabeçalho desktop para hierarquia visual editorial, respiro tipográfico e alinhamento em linha única em `frontend/src/views/StudyView.vue`

**Checkpoint**: Experiência desktop do cabeçalho entregue com hierarquia editorial limpa e zero poluição visual.

---

## Phase 4: User Story 2 - Experiência Mobile: Linha Única Compacta e Toque Acessível (Priority: P1)

**Goal**: Condensar o cabeçalho no mobile (< 768px / < 640px) para caber rigorosamente em uma linha única, garantindo alvos de toque de 44x44px e breadcrumb inteligente `← Voltar ao capítulo`.

**Independent Test**: Redimensionar para largura de smartphone (360px a 480px), verificar que os botões não quebram em mais de 1 linha, área de toque é ≥ 44x44px e o breadcrumb colapsa em botão inteligente de retorno.

- [x] T009 [US2] Implementar botão inteligente de retorno `← Voltar ao capítulo` com truncamento elegante para viewports estreitas (< 640px) em `frontend/src/views/StudyView.vue`
- [x] T010 [US2] Condensar bloco de ações em viewports móveis (< 768px) para exibir apenas "Editar" compacto e o disparador `•••` (com "Compartilhar" agrupado dentro do dropdown) em `frontend/src/views/StudyView.vue`
- [x] T011 [US2] Ajustar regras de layout responsivo, flexbox sem quebra (`nowrap`) e dimensões mínimas de toque de 44x44px em `frontend/src/views/StudyView.vue` e `frontend/src/mobile-navigation.css`

**Checkpoint**: Experiência mobile perfeitamente adaptada, compacta, sem quebras irregulares e em estrito cumprimento da WCAG 2.1.

---

## Phase 5: User Story 3 - Acessibilidade WAI-ARIA e Navegação por Teclado (Priority: P2)

**Goal**: Garantir conformidade WAI-ARIA Menu com ciclo de foco, navegação por setas e isolamento de atalhos em relação ao Active Recall.

**Independent Test**: Operar o menu utilizando apenas teclado (`Tab`, `Enter`, `Setas`, `Escape`), confirmando foco cíclico e constatando que atalhos do leitor (como `Escape` do Active Recall) não são disparados acidentalmente.

- [x] T012 [US3] Implementar atributos semânticos WAI-ARIA (`role="menu"`, `role="menuitem"`, `aria-haspopup="menu"`, `:aria-expanded`) em `frontend/src/components/ui/DropdownMenu.vue`
- [x] T013 [US3] Implementar navegação cíclica por teclado (`ArrowDown`, `ArrowUp`, `Home`, `End`) com gerenciamento de foco nos itens em `frontend/src/components/ui/DropdownMenu.vue`
- [x] T014 [US3] Adicionar contenção de propagação de eventos de teclado (`stopPropagation`) no `DropdownMenu.vue` para blindar contra conflitos com atalhos de Active Recall em `frontend/src/views/StudyView.vue`

**Checkpoint**: Acessibilidade WAI-ARIA completa e navegação de teclado aprovada sem armadilhas de foco.

---

## Phase 6: User Story 4 - Modo Somente Leitura e Visualização de Convidado (Priority: P2)

**Goal**: Exibir um cabeçalho contextual adaptado para visitantes sem permissão de escrita (`canEdit === false`), omitindo ações mutáveis.

**Independent Test**: Abrir estudo com `canEdit === false` e verificar que "Editar" e "Mover para lixeira" não são exibidos, restando apenas "Exportar estudo".

- [x] T015 [US4] Implementar renderização defensiva para convidados em `frontend/src/views/StudyView.vue`, omitindo botão "Editar estudo", ação "Compartilhar" e opção "Mover para a lixeira"
- [x] T016 [US4] Ajustar o `DropdownMenu` em `frontend/src/views/StudyView.vue` para exibir apenas opções permitidas de consumo quando `canEdit === false`

**Checkpoint**: Visualização de convidado/somente leitura coesa e sem opções proibidas.

---

## Phase 7: Polish & Validação Global

**Purpose**: Testes integrados, compilação de produção e auditoria final.

- [x] T017 [P] Criar testes de integração e regressão para o cabeçalho em `frontend/tests/study_header_actions.test.mjs`
- [x] T018 Executar validação automatizada completa (`npm test` e `npm run build`), assegurando zero regressão e conformidade com `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Concluída.
- **Phase 2 (Foundational)**: Concluída.
- **Phase 3 (User Story 1)**: Concluída.
- **Phase 4 (User Story 2)**: Concluída.
- **Phase 5 (User Story 3)**: Concluída.
- **Phase 6 (User Story 4)**: Concluída.
- **Phase 7 (Polish)**: Concluída.

---

## Status Final
Todas as 18 tarefas foram implementadas e validadas com sucesso.
Suítes de testes 100% verdes: 364 testes de frontend passando (`npm test`), build de produção aprovado (`npm run build`), 420 testes de backend preservados (`pytest`).
