# Implementation Tasks: Rótulos de Botões e Linhas Texto + Botão em Telas Estreitas

**Feature**: `079-rotulos-botoes-responsivos` | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/079-rotulos-botoes-responsivos/spec.md) | **Plan**: [plan.md](file:///c:/Users/User/caderno/specs/079-rotulos-botoes-responsivos/plan.md)

---

## Phase 1: Setup & Infraestrutura de Testes

- [x] T001 Criar arquivo de teste automatizado `caderno-leitura-0.1/frontend/tests/feature-079-button-labels.test.mjs`
- [x] T002 Validar execução e falha inicial dos testes com Node test runner (TDD)

---

## Phase 2: Foundational & Regra-Base Universal (Priority: P1 / US4)

- [x] T003 [US4] Atualizar regra-base geral em `caderno-leitura-0.1/frontend/src/style.css:31` para incluir `white-space: nowrap` e `flex-shrink: 0` em `button, .button`
- [x] T004 [US4] Declarar nominalmente `white-space: normal` para os controles do Tipo C (botões-cartão) em `ConcurrencyConflictModal.vue`, `ConflictResolutionModal.vue`, `StudySessionView.vue` e `GlobalSearchModal.vue`

---

## Phase 3: User Story 2 - Botões de Ação com Rótulo Íntegro em Uma Linha (Priority: P1)

- [x] T005 [US2] Reorganizar a barra de ações em lote da Lixeira em `caderno-leitura-0.1/frontend/src/views/TrashView.vue` com `flex-wrap: wrap`, variantes de rótulo curto e alvos táteis mínimos
- [x] T006 [US2] Ajustar grupos de botões nos cartões e filtros da Lixeira (`views/TrashView.vue`) para prevenir quebras entre palavras
- [x] T007 [US2] Reorganizar botões de início de sessão estruturada e prática rápida na Central de Revisão em `caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue`
- [x] T008 [US2] Ajustar o botão de estado pedagógico vazio em `caderno-leitura-0.1/frontend/src/components/review/ReviewPedagogicalEmpty.vue` com variante curta em telas estreitas
- [x] T009 [US2] Reorganizar botões nos modais de resumo (`ReviewSummaryModal.vue` e `SessionSummaryModal.vue`) com flex-wrap e botões em linha única
- [x] T010 [US2] Flexibilizar altura de botões de 48px na landing page e rodapé público em `HeroSection.vue` e `PublicFooter.vue` para eliminar risco de corte de texto
- [x] T011 [US2] Reorganizar grupos de ações nos Ajustes (`SettingsView.vue`) e gerenciamento de sessões (`SessionsManager.vue`)

---

## Phase 4: User Story 3 - Linhas "Texto + Botão" Legíveis e sem Estrangulamento (Priority: P2)

- [x] T012 [US3] Atualizar as classes globais `.section-heading` e `.save-bar` em `caderno-leitura-0.1/frontend/src/style.css` com flex-wrap, base mínima para o texto (`flex: 1 1 12rem`) e empilhamento suave da ação
- [x] T013 [US3] Ajustar linhas híbridas de título e ações em `BookView.vue`, `StudyView.vue` e `StudyEditView.vue` para suportar 320px sem estrangular títulos

---

## Phase 5: User Story 1 - Auditoria e Rastreabilidade dos 24 Candidatos (Priority: P1)

- [x] T014 [US1] Auditar a matriz dos 24 candidatos em testes e registrar o status final de cada ocorrência

---

## Phase 6: Validação, Conformidade e Finalização

- [x] T015 Consolidar asserções completas em `caderno-leitura-0.1/frontend/tests/feature-079-button-labels.test.mjs`
- [x] T016 Executar suíte completa do frontend via `npm test`
- [x] T017 Compilar bundle com `npm run build` para validar tipos e módulos
- [x] T018 Validar ausência absoluta de emojis no código e documentação
- [x] T019 Marcar todos os requisitos e critérios no checklist `specs/079-rotulos-botoes-responsivos/checklists/requirements.md`
