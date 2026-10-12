# Implementation Tasks: Feature 080 — Visualizações Móveis e Responsividade de Destaques

**Feature**: `080-visualizacoes-e-destaques-moveis` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Infraestrutura de Testes)

**Purpose**: Criação do arcabouço de testes unitários focados da Feature 080

- [x] T001 Criar arquivo de teste automatizado `caderno-leitura-0.1/frontend/tests/feature-080-mobile-views-highlights.test.mjs`
- [x] T002 Validar execução e falha inicial dos testes com Node test runner (TDD)

---

## Phase 2: Foundational (Pré-requisitos Compartilhados do Shell e Palco)

**Purpose**: Garantir contenção de overflow e container queries no palco

- [x] T003 [P] Declarar container query canônica no palco central de estudos em `caderno-leitura-0.1/frontend/src/style.css` (`container-type: inline-size; container-name: study-stage;`)

---

## Phase 3: User Story 1 - Biblioteca de Destaques sem Transbordamento e com Navegação Inferior Íntegra (Priority: P1) - MVP

**Goal**: Eliminar a rolagem horizontal da rota `/destaques`, reorganizar a barra de busca e filtros no mobile e garantir espaçamento seguro com `--mobile-nav-offset` para a barra inferior móvel e paginação.

**Independent Test**: Acessar `/destaques` em 320px, 375px e 767px; confirmar que `scrollWidth <= clientWidth`, que os botões de paginação estão acessíveis acima da barra inferior e que o campo de busca expande para 100%.

- [x] T004 [US1] Reorganizar a barra primária de filtros em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue` com `flex-wrap: wrap`, campo de busca em largura total (100%) em $\le 767\text{px}$ e quebra suave do alternador de modo e gatilho de filtros
- [x] T005 [P] [US1] Ajustar truncamento de títulos com reticências e quebra de ações em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue` para prevenir estouro em telas estreitas
- [x] T006 [US1] Aplicar contenção de transbordamento (`max-width: 100%; box-sizing: border-box; overflow-x: hidden;`) e padding inferior canônico (`padding-bottom: calc(var(--mobile-nav-offset, 56px) + 1.5rem);`) em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [x] T007 [P] [US1] Reorganizar a barra de paginação (`.pagination-nav`) com flex-wrap e alvos mínimos de $44 \times 44\text{ px}$ em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [x] T008 [P] [US1] Posicionar o micro-toast flutuante de confirmação (`.study-micro-toast`) com `bottom: calc(var(--mobile-nav-offset, 56px) + 1rem);` em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`

**Checkpoint**: User Story 1 completa e testável de forma independente.

---

## Phase 4: User Story 2 - Navegação Tátil e Alternativa Acessível no Mapa de Estudos (Priority: P1)

**Goal**: Habilitar gestos táteis de pan e pinch zoom no grafo radial e disponibilizar visualização alternativa em lista semântica de relações no celular.

**Independent Test**: Tocar no palco do Mapa e arrastar (pan); fazer pinça com dois dedos (pinch zoom em $[0.5, 2.5]$); comutar para a lista semântica e executar ações táteis com botões $\ge 44 \times 44\text{ px}$.

- [x] T009 [US2] Implementar handlers de multitoque (`touchstart`, `touchmove`, `touchend`, `touchcancel`) para pan e pinch zoom contínuo em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`
- [x] T010 [US2] Implementar alternador de exibição ("Grafo" / "Lista de Relações") em viewports móveis ($\le 767\text{px}$) em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`
- [x] T011 [US2] Estruturar a lista semântica móvel de relações com ações táteis explícitas (editar, inverter sentido, desvincular) com alvos $\ge 44 \times 44\text{ px}$ em `caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue`

**Checkpoint**: User Stories 1 e 2 completas e testáveis.

---

## Phase 5: User Story 3 - Rolagem Vertical e Exploração Tátil no Canvas de Estudos (Priority: P2)

**Goal**: Desbloquear a rolagem vertical da página no modo Canvas em smartphones e compactar a toolbar em telas $< 1024\text{px}$.

**Independent Test**: Deslizar verticalmente sobre a viewport do canvas em 375px e constatar rolagem normal da página; verificar condensação da barra de ferramentas.

- [x] T012 [US3] Desbloquear a rolagem vertical aplicando `touch-action: pan-y;` sob `@media (max-width: 767px)` no contêiner `.canvas-viewport` em `caderno-leitura-0.1/frontend/src/components/views/StudyCanvasView.vue`
- [x] T013 [US3] Compactar ferramentas secundárias da barra de ferramentas em menu suspenso ou botões agrupados em `caderno-leitura-0.1/frontend/src/components/views/canvas/CanvasToolbar.vue`

**Checkpoint**: User Stories 1, 2 e 3 completas e funcionais.

---

## Phase 6: User Story 4 - Hierarquia e Reordenação Acessível na Árvore de Estudos (Priority: P2)

**Goal**: Ocultar alças de arrasto dependentes de mouse em telas de toque e garantir reordenação e aninhamento fluidos via menu contextual tátil na Árvore.

**Independent Test**: Em emulação de `pointer: coarse`, confirmar ocultação de drag handles e funcionamento do menu contextual com alvos táteis $\ge 44 \times 44\text{ px}$.

- [x] T014 [US4] Ocultar `.tree-drag-handle` sob `@media (pointer: coarse)` e evidenciar o gatilho `.mobile-menu-toggle-btn` com alvo $\ge 44 \times 44\text{ px}$ em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue`
- [x] T015 [US4] Assegurar que as opções de menu contextual ("Mover para cima", "Mover para baixo", "Aninhar") mantenham alvos táteis $\ge 44 \times 44\text{ px}$ e executem reordenação imediata em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue`
- [x] T016 [US4] Aplicar compressão de margens de indentação em nós aninhados para telas compactas em `caderno-leitura-0.1/frontend/src/components/views/StudyTreeView.vue`

**Checkpoint**: Todas as 4 User Stories implementadas e testáveis.

---

## Phase 7: Polish, Validação, Conformidade e Finalização

**Purpose**: Validações cruzadas de qualidade, ausência de regressões e commit atômico

- [x] T017 Consolidar asserções completas em `caderno-leitura-0.1/frontend/tests/feature-080-mobile-views-highlights.test.mjs`
- [x] T018 Executar suíte completa do frontend via `npm test`
- [x] T019 Compilar bundle do frontend via `npm run build` para validar tipos e módulos
- [x] T020 Executar suíte de testes do backend via `pytest` em ambiente isolado
- [x] T021 Validar ausência absoluta de emojis no código e documentação
- [x] T022 Marcar todos os requisitos e critérios no checklist `specs/080-visualizacoes-e-destaques-moveis/checklists/requirements.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Pode iniciar imediatamente.
- **Phase 2 (Foundational)**: Bloqueia as User Stories que dependem de container queries.
- **Phase 3 (US1 - Destaques)**: Pode iniciar após Foundational; entrega o MVP de maior impacto visual.
- **Phase 4 (US2 - Mapa)**: Independente da US1; foca em gestos e lista semântica.
- **Phase 5 (US3 - Canvas)**: Independente; foca em rolagem e toolbar.
- **Phase 6 (US4 - Árvore)**: Independente; foca em ações de toque e hierarquia.
- **Phase 7 (Polish)**: Executada após a conclusão das User Stories.

---

## Implementation Strategy

### MVP First (User Story 1 - Biblioteca de Destaques)
1. Completar Setup (T001, T002) e Foundational (T003).
2. Implementar US1 (T004 a T008): resolver de imediato o transbordamento da tela de Destaques e a integridade da barra inferior móvel.
3. Validar US1 de forma independente em 320px e 375px.

### Entrega Incremental das Visualizações
4. Implementar US2 (Mapa de Estudos: pan, pinch e lista tátil).
5. Implementar US3 (Canvas de Estudos: rolagem vertical e toolbar compacta).
6. Implementar US4 (Árvore de Estudos: menu contextual tátil e indentação móvel).
7. Executar bateria final de regressão e validação com suítes 100% verdes.
