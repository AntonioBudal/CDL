# Implementation Tasks: Leitor e Disposição de Conteúdo Responsivo

**Feature**: `078-conteudo-responsivo` | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/078-conteudo-responsivo/spec.md) | **Plan**: [plan.md](file:///c:/Users/User/caderno/specs/078-conteudo-responsivo/plan.md)

---

## Phase 1: Setup & Infraestrutura de Testes

- [x] T001 Criar arquivo de teste automatizado `caderno-leitura-0.1/frontend/tests/feature-078-conteudo-responsivo.test.mjs`
- [x] T002 Validar execução inicial de teste para a Feature 078 com Node test runner

---

## Phase 2: User Story 1 - Leitor Focado e Navegação de Capítulos sem Bloqueio (Priority: P1)

- [x] T003 [US1] Atualizar `caderno-leitura-0.1/frontend/src/composables/useSplitPanes.ts` para inicializar `leftCollapsed` como `true` (gaveta recolhida) em mobile (`< 768px`) quando não houver valor salvo em cache
- [x] T004 [US1] Reorganizar o cabeçalho em `caderno-leitura-0.1/frontend/src/views/BookView.vue` para compactar ações secundárias (Exportar, Editar, Lixeira) em menu contextual em viewports `< 768px`
- [x] T005 [US1] Assegurar alvos táteis mínimos de $44 \times 44\text{ px}$ e transição suave na gaveta de capítulos em `BookView.vue`

---

## Phase 3: User Story 2 - Gestão Administrativa em Cartões Adaptativos (Priority: P1)

- [x] T006 [US2] Em `caderno-leitura-0.1/frontend/src/components/admin/AdminUsersTable.vue`, estruturar template e classes semânticas para apresentação em cartões adaptativos em viewports `< 768px`
- [x] T007 [US2] Exibir dados de identidade, crachás de papel/status, contadores de estudos/sessões, data de último acesso e botões de ação rápida em cada cartão
- [x] T008 [US2] Garantir alvos de toque $\ge 44 \times 44\text{ px}$ nos botões de ação operacional e preservar a tabela tradicional com cabeçalhos em viewports $\ge 768\text{px}$

---

## Phase 4: User Story 3 - Blindagem de Grids em 320px e Telas Ultra-Estreitas (Priority: P2)

- [x] T009 [P] [US3] Atualizar declarações de grid em `caderno-leitura-0.1/frontend/src/views/FriendsView.vue` para conter colunas mínimas fluidas sem transbordamento em 320px
- [x] T010 [P] [US3] Atualizar declarações de grid em `caderno-leitura-0.1/frontend/src/views/AdminView.vue` para suportar 320px sem overflow horizontal
- [x] T011 [P] [US3] Atualizar grade de cartões em `caderno-leitura-0.1/frontend/src/components/landing/SovereigntySection.vue` para evitar overflow em 320px

---

## Phase 5: User Story 4 - Modais com Altura Dinâmica `dvh` e Blindagem de Hover Tátil (Priority: P2)

- [x] T012 [P] [US4] Adicionar declaração de altura dinâmica `max-height: 90dvh` em `caderno-leitura-0.1/frontend/src/components/BookEditModal.vue` com fallback para `90vh`
- [x] T013 [P] [US4] Adicionar declaração de altura dinâmica em `caderno-leitura-0.1/frontend/src/components/ExportModal.vue` com fallback seguro
- [x] T014 [P] [US4] Adicionar declaração de altura dinâmica `height: 85dvh` em `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue` com fallback
- [x] T015 [P] [US4] Adicionar altura dinâmica `dvh` em modais de `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- [x] T016 [P] [US4] Proteger elevações em `:hover` (`transform: translateY`) com `@media (hover: hover) and (pointer: fine)` em `style.css` e componentes de cartões

---

## Phase 6: Validação, Qualidade e Finalização

- [x] T017 Integrar asserções de validação em `caderno-leitura-0.1/frontend/tests/feature-078-conteudo-responsivo.test.mjs`
- [x] T018 Executar suíte completa de testes do frontend com `npm test`
- [x] T019 Compilar projeto via `npm run build` para validar verificação estática de tipos e bundle
- [x] T020 Validar ausência estrita de emojis no código-fonte e na documentação
- [x] T021 Marcar todos os itens no checklist `specs/078-conteudo-responsivo/checklists/requirements.md`
