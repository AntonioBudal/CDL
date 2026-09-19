# Tasks: 008 — Mecânica: Superclasse Tátil & Responsiva

**Branch**: `008-mecanica-tatil` | **Date**: 2026-09-19 | **Spec**: [specs/008-mecanica-tatil/spec.md](file:///c:/Users/User/caderno/specs/008-mecanica-tatil/spec.md) | **Plan**: [specs/008-mecanica-tatil/plan.md](file:///c:/Users/User/caderno/specs/008-mecanica-tatil/plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação do módulo CSS e registro no pipeline global de estilos.

- [X] T001 Create dedicated stylesheet in frontend/src/styles/superclasses/mecanica.css
- [X] T002 Import stylesheet frontend/src/styles/superclasses/mecanica.css in frontend/src/style.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tokens físicos centrais, escopo nominal da Mecânica e cláusula pétrea de imobilidade do leitor.

**⚠️ CRITICAL**: Nenhuma tarefa de User Story pode ser implementada sem a conclusão desta fase.

- [X] T003 Define core mechanical CSS custom properties (--sc-border-radius, --sc-shadow-idle, --sc-shadow-hover, --sc-shadow-active, --sc-transition-duration, --sc-transition-easing) under :is(:root[data-superclass="mecanica"], .superclass-mecanica) in frontend/src/styles/superclasses/mecanica.css
- [X] T004 Enforce reading mode absolute immobility and suppression of idle breathing or magnetic cursor tracking in frontend/src/styles/superclasses/mecanica.css

**Checkpoint**: Base física estabelecida — implementação das user stories liberada.

---

## Phase 3: User Story 1 - Ativação da Superclasse Mecânica e Feedback Tátil Push-Down em Botões e Cards (Priority: P1) 🎯 MVP

**Goal**: Entregar feedback tátil com repouso rígido, cantos de 2px, sombras sólidas sem blur, micro-elevação no hover (100ms linear) e afundamento (*push-down*) de 3px com anulação exata da sombra no clique (`:active`).

**Independent Test**: Ativar "Mecânica" nos Ajustes de Aparência, clicar/passar o mouse sobre botões e cartões de livros; verificar bordas de 2px, sombra sólida de 3px, afundamento de 3px no clique e ausência total de oscilação contínua.

### Tests for User Story 1
- [X] T005 [P] [US1] Add automated tests for Mecânica CSS tokens, push-down behavior, and hover elevation in frontend/tests/superclasses.test.mjs

### Implementation for User Story 1
- [X] T006 [US1] Implement button and interactive element tactile styling (button, .button, .btn, chips) with 2px corners, solid shadow, 100ms linear transition, hover lift, and active push-down in frontend/src/styles/superclasses/mecanica.css
- [X] T007 [US1] Implement library card and list item styling (.book-card, .book-list-item) with 2px corners, solid shadow, and hover/active tactile reactions in frontend/src/styles/superclasses/mecanica.css

**Checkpoint**: User Story 1 (MVP) completamente funcional e testável de forma independente.

---

## Phase 4: User Story 2 - Escopo Sistêmico em Formulários, Inputs Escavados e Caixas de Ajustes (Priority: P2)

**Goal**: Expandir a sensação tátil para campos de formulário como cavidades escavadas (sombra `inset`), foco de alto atrito visual sem flutuação, e painéis aparafusados (`.appearance-group`, `.panel`).

**Independent Test**: Acessar telas de Ajustes e formulários de cadastro; verificar que os campos possuem sombra interna de cavidade, cantos de 2px, foco sem flutuação e contêineres estruturados com sombras duras.

### Tests for User Story 2
- [X] T008 [P] [US2] Add automated tests for form inputs (inset cavity shadow, solid high-friction focus) and panel containment in frontend/tests/superclasses.test.mjs

### Implementation for User Story 2
- [X] T009 [US2] Implement form fields (input, textarea, select) styling with 2px radius, inset cavity shadow, and high-friction solid focus in frontend/src/styles/superclasses/mecanica.css
- [X] T010 [US2] Implement appearance group boxes (.appearance-group), panels (.panel, .form-panel), and modals with rigid 2px corners and solid mounting shadows in frontend/src/styles/superclasses/mecanica.css

**Checkpoint**: User Stories 1 e 2 funcionando de forma consistente e integrada.

---

## Phase 5: User Story 3 - Controles Booleanos com Estalo e Transições de Rota em Corte Seco (Priority: P3)

**Goal**: Prover comutação ultrarrápida de 60ms para switches/toggles e transição de páginas Vue Router em corte seco limpo de 100ms.

**Independent Test**: Alternar switches para constatar a velocidade de estalo de 60ms; navegar entre rotas (Biblioteca $\leftrightarrow$ Ajustes) observando o corte limpo de opacidade em 100ms sem atrasos perceptíveis.

### Tests for User Story 3
- [X] T011 [P] [US3] Add automated tests for switch snap timing and router transition tokens in frontend/tests/superclasses.test.mjs

### Implementation for User Story 3
- [X] T012 [US3] Implement rapid switch/toggle kinematics (50-80ms linear pin snap) and tactile checkbox push-down in frontend/src/styles/superclasses/mecanica.css
- [X] T013 [US3] Configure RouterView transition wrapper with Transition name="page" mode="out-in" in frontend/src/App.vue
- [X] T014 [US3] Implement Vue Router page transition rules (.page-enter-active, .page-leave-active, .page-enter-from, .page-leave-to) for clean 100ms linear opacity cut under Mecânica in frontend/src/styles/superclasses/mecanica.css

**Checkpoint**: User Stories 1, 2 e 3 integradas com resposta cinemática completa em rotas e controles.

---

## Phase 6: User Story 4 - Calibração de Intensidade Paramétrica e Neutralização Universal de Movimento (Priority: P4)

**Goal**: Escalonar o curso de afundamento e as sombras sólidas pelo multiplicador `--sc-intensity` (0.5x, 1.0x, 1.5x) e neutralizar 100% das translações sob preferências de redução de movimento.

**Independent Test**: Alternar o seletor de intensidade nos Ajustes e verificar o afundamento proporcional (1.5px em Sutil, 3px em Padrão, 4.5px em Alta, 0px em Desativada); testar sob `prefers-reduced-motion` e constatar imobilidade total.

### Tests for User Story 4
- [X] T015 [P] [US4] Add automated tests for parametric intensity scaling and motion neutralization in frontend/tests/superclasses.test.mjs

### Implementation for User Story 4
- [X] T016 [US4] Implement intensity multiplier formulas and strict reduced-motion / data-motion="off" override rules (--sc-intensity: 0.0 !important; transform: none !important;) in frontend/src/styles/superclasses/mecanica.css

**Checkpoint**: Todas as user stories completas, com controle paramétrico e conformidade estrita de acessibilidade.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validação integrada da suíte de testes, verificação de tipos e garantia de qualidade.

- [X] T017 [P] Run full automated test suite npm test in frontend/tests/superclasses.test.mjs and verify all assertions pass
- [X] T018 Run type check and production build via npm run build in frontend/ ensuring zero bundle or typing errors
- [X] T019 Execute manual and interactive quickstart validation scenarios per specs/008-mecanica-tatil/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da conclusão da Fase 1 — BLOQUEIA todas as User Stories.
- **User Story 1 (Phase 3)**: Depende da Fase 2. Constitui o MVP.
- **User Story 2 (Phase 4)**: Depende da Fase 2 (pode ser executada em sequência após US1).
- **User Story 3 (Phase 5)**: Depende da Fase 2.
- **User Story 4 (Phase 6)**: Depende da Fase 2 e consolida as fórmulas de intensidade para US1–US3.
- **Polish (Phase 7)**: Depende da conclusão de todas as User Stories (US1–US4).

### Parallel Opportunities

- `T005`, `T008`, `T011`, `T015`: Testes automatizados marcados com `[P]` podem ser escritos em paralelo com os contratos correspondentes.
- As regras específicas de CSS em `mecanica.css` são organizadas em seções lógicas independentes (Botões, Formulários, Switches, Transição de Rota).

---

## Parallel Example: User Story 1

```powershell
# Executar testes da User Story 1 enquanto valida folha de estilo:
node --test frontend/tests/superclasses.test.mjs
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (T001–T002).
2. Concluir Foundational (T003–T004).
3. Concluir User Story 1 (T005–T007).
4. **Validar MVP**: Ativar Mecânica nos Ajustes e testar o *push-down* de botões e cartões na biblioteca.

### Entrega Incremental
1. Setup + Foundational $\to$ Base e tokens operacionais.
2. User Story 1 $\to$ Botões, cards e feedback tátil (MVP entregue).
3. User Story 2 $\to$ Formulários, inputs escavados e painéis.
4. User Story 3 $\to$ Switches ultrarrápidos e corte seco de páginas.
5. User Story 4 $\to$ Calibração de intensidade paramétrica e acessibilidade.
6. Polish $\to$ Validação integral (`npm test` e `npm run build`).
