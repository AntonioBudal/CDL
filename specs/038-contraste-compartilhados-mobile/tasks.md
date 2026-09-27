# Tasks: F09.5.2 — Contraste Dinâmico, Estudos Compartilhados e Responsividade Mobile

**Branch**: `038-contraste-compartilhados-mobile` | **Date**: 2026-09-26 | **Spec**: [specs/038-contraste-compartilhados-mobile/spec.md](file:///c:/Users/User/caderno/specs/038-contraste-compartilhados-mobile/spec.md) | **Plan**: [specs/038-contraste-compartilhados-mobile/plan.md](file:///c:/Users/User/caderno/specs/038-contraste-compartilhados-mobile/plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estruturar interfaces TypeScript compartilhadas e preparar o ambiente de testes para a feature.

- [X] T001 Preparar ambiente e verificar scripts de validação em `caderno-leitura-0.1/frontend/package.json`
- [X] T002 [P] Adicionar interfaces TypeScript para contraste (`ContrastResult`, `ContrastCalculationOptions`, `DynamicThemeVariables`) e navegação móvel (`MobileNavItem`, `MobileMoreMenuItem`) em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fundação central matemática e reativa de contraste WCAG 2.1 necessária para todos os componentes.

- [X] T003 [P] Criar a suíte de testes unitários do motor de contraste em `caderno-leitura-0.1/frontend/tests/contrast_engine.test.mjs`
- [X] T004 Implementar o utilitário matemático puro de luminância relativa e contraste WCAG 2.1 (`parseCssColor`, `getRelativeLuminance`, `getContrastRatio`, `blendAlpha`, `getAccessibleTextColor`) em `caderno-leitura-0.1/frontend/src/utils/contrast.ts`
- [X] T005 Implementar o composable reativo `useAccessibleContrast` para geração e injeção de variáveis CSS locais (`--dynamic-fg`, `--dynamic-hover-fg`, etc.) em `caderno-leitura-0.1/frontend/src/composables/useAccessibleContrast.ts`

---

## Phase 3: User Story 1 - Contraste Dinâmico Centralizado e Acessível para Estados de Interface (Priority: P1) 🎯 MVP

**Goal**: Erradicar regras de cores hard-coded (`#FFFFFF !important`, `#18181b`, `text-white`) e garantir taxa de contraste $\ge 4.5:1$ em todos os estados de interação (`default`, `hover`, `focus`, `active`, `selected`) em abas, selects e botões.

**Independent Test**: Executar `node --test tests/contrast_engine.test.mjs`; alternar temas claros e escuros nos Ajustes e inspecionar abas e campos de seleção, confirmando que texto e ícones adaptam suas cores ao fundo sem regras estáticas de exceção.

### Implementation for User Story 1

- [X] T006 [US1] Executar e validar a suíte de testes unitários do motor de contraste com `node --test tests/contrast_engine.test.mjs`
- [X] T007 [US1] Remover regras estáticas com `!important` para cor de texto em `<select>` e botões secundários em `caderno-leitura-0.1/frontend/src/style.css`
- [X] T008 [US1] Refatorar as abas de biblioteca em `caderno-leitura-0.1/frontend/src/views/BooksView.vue` eliminando classes hard-coded `#18181b` e fundos opacos em hover
- [X] T009 [US1] Integrar o consumo de `--color-surface` e variáveis semânticas de contraste dinâmico em campos de formulário e botões secundários em `caderno-leitura-0.1/frontend/src/style.css`

**Checkpoint**: User Story 1 completa e testada de forma independente. O sistema calcula contraste matematicamente sem exceções hard-coded.

---

## Phase 4: User Story 2 - Diagnóstico Estrutural e Reformulação Integral de Estudos Compartilhados (Priority: P2)

**Goal**: Reformular a tela `SharedStudiesList.vue`, expurgando classes órfãs do Tailwind, usando `<Icon />` com dimensões contidas (16px a 20px) e padronizando os cartões e estados com os tokens do Leitorum.

**Independent Test**: Acessar `/books` na aba "Compartilhados Comigo"; verificar que o ícone de busca mede 16px, que os cards usam tokens de tema do Leitorum e que os estados de busca, erro e vazio são proporcionais e esteticamente integrados.

### Implementation for User Story 2

- [X] T010 [US2] Expurgar todas as classes utilitárias órfãs do Tailwind (`w-4 h-4`, `text-zinc-400`, `dark:bg-zinc-900`, `border-zinc-200`) em `caderno-leitura-0.1/frontend/src/components/library/SharedStudiesList.vue`
- [X] T011 [US2] Substituir tags `<svg>` soltas pelo componente oficial `<Icon :name="..." :size="..." />` com dimensões fixas de 16px a 20px em `caderno-leitura-0.1/frontend/src/components/library/SharedStudiesList.vue`
- [X] T012 [US2] Reformular a barra de pesquisa, o campo de filtro por `@autor` e os cartões de estudo compartilhado usando exclusivamente variáveis semânticas (`--color-surface`, `--color-border`, `--color-text`, `--color-accent`) em `caderno-leitura-0.1/frontend/src/components/library/SharedStudiesList.vue`
- [X] T013 [US2] Implementar os estados de carregamento (esqueleto animado com tokens `--skeleton-base`), erro com botão de nova tentativa e empty state contido ($\le 120\text{px}$) em `caderno-leitura-0.1/frontend/src/components/library/SharedStudiesList.vue`

**Checkpoint**: User Stories 1 e 2 completas. A tela de Estudos Compartilhados está totalmente curada e harmonizada com a identidade do sistema.

---

## Phase 5: User Story 3 - Auditoria de Arquitetura de Navegação e Responsividade Mobile (Priority: P3)

**Goal**: Implementar a barra de navegação móvel de 5 colunas com botão "Mais" acionando a gaveta inferior `MobileMoreMenu.vue` e rolagem horizontal suave com máscara de desvanecimento (*fade mask*) para abas em celulares.

**Independent Test**: Emular viewport de smartphone (375x667px); constatar 5 alvos de toque na barra inferior ($\ge 44\text{px}$), abrir o menu "Mais" para acessar rotas secundárias (`Lixeira`, `Admin`, `Conexão`) e verificar rolagem suave das abas nos Ajustes com máscara gradiente nas laterais.

### Implementation for User Story 3

- [X] T014 [P] [US3] Criar o componente de gaveta inferior `MobileMoreMenu.vue` com opções secundárias (`Lixeira`, `Administração`, `Conexão`, `Perfil`, `Logout`), animação tátil e acessibilidade WAI-ARIA em `caderno-leitura-0.1/frontend/src/components/navigation/MobileMoreMenu.vue`
- [X] T015 [US3] Refatorar a lista de links da barra `.main-nav` em `caderno-leitura-0.1/frontend/src/App.vue` para estruturar os 4 destinos prioritários e o acionador da gaveta 'Mais'
- [X] T016 [US3] Atualizar a grade da barra móvel para 5 colunas proporcionais (`repeat(5, minmax(0, 1fr))`) e alvos de toque mínimos de 44x44px em `caderno-leitura-0.1/frontend/src/mobile-navigation.css`
- [X] T017 [US3] Implementar classes de fita de abas com rolagem horizontal contida e máscara gradiente (*fade mask*) nas extremidades em `caderno-leitura-0.1/frontend/src/mobile-navigation.css` e `caderno-leitura-0.1/frontend/src/appearance-advanced.css`
- [X] T018 [US3] Ajustar a densidade do cabeçalho superior (`app-header`) e quebra de toolbars em viewports estreitas (< 380px) em `caderno-leitura-0.1/frontend/src/mobile-navigation.css`

**Checkpoint**: Todas as 3 User Stories implementadas e funcionais. Navegação móvel e abas plenamente responsivas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação rigorosa de integridade, checagem de tipos, testes automatizados e conformidade com as regras do projeto.

- [X] T019 Executar suíte completa de testes automatizados (`npm test`) em `caderno-leitura-0.1/frontend`
- [X] T020 Executar checagem estrita de tipos TypeScript com `npm run build` (`vue-tsc -b`) em `caderno-leitura-0.1/frontend`
- [X] T021 Executar o roteiro de validação manual de ponta a ponta descrito em `specs/038-contraste-compartilhados-mobile/quickstart.md`
- [X] T022 Auditar o repositório garantindo conformidade estrita com as diretrizes anti-emoji e sem resquícios de arquivos temporários

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA a implementação das User Stories.
- **User Story 1 (Phase 3)**: Depende da Phase 2 — Entrega o MVP de contraste dinâmico.
- **User Story 2 (Phase 4)**: Depende da Phase 2 — Pode ser executada em sequência ou em paralelo com US1.
- **User Story 3 (Phase 5)**: Depende da Phase 2 — Pode ser executada em sequência ou em paralelo com US1/US2.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias desejadas.

### User Story Dependencies

```
[Phase 1: Setup]
       │
       ▼
[Phase 2: Foundational: contrast.ts + useAccessibleContrast.ts]
       │
       ├─────────────────────────┬─────────────────────────┐
       ▼                         ▼                         ▼
[Phase 3: US1 - Contraste]  [Phase 4: US2 - Estudos]  [Phase 5: US3 - Mobile]
       │                         │                         │
       └─────────────────────────┼─────────────────────────┘
                                 │
                                 ▼
                     [Phase 6: Polish & Build]
```

---

## Parallel Opportunities

- **Na Phase 1**: T002 pode ser executada em paralelo com a revisão de T001.
- **Na Phase 2**: T003 (testes) e T004 (utilitário puro) podem ser desenvolvidos em paralelo antes de T005 (composable).
- **Após a Phase 2**: As User Stories (US1, US2 e US3) possuem fronteiras de arquivo e componentes totalmente desacopladas e podem ser executadas em paralelo:
  - US1 atua em `contrast.ts`, `useAccessibleContrast.ts`, `style.css` e `BooksView.vue`.
  - US2 atua exclusivamente em `SharedStudiesList.vue`.
  - US3 atua em `MobileMoreMenu.vue`, `App.vue` e `mobile-navigation.css`.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Setup (Phase 1) e Foundational (Phase 2).
2. Concluir User Story 1 (Phase 3).
3. **Parar e Validar**: O motor de contraste centralizado funciona, os testes passam e as exceções `!important` foram expurgadas.

### Entrega Incremental Completa
1. Setup + Foundational concluídos.
2. User Story 1 (Contraste dinâmico WCAG 2.1) implementada e validada.
3. User Story 2 (Estudos Compartilhados curados, SVGs contidos) implementada e validada.
4. User Story 3 (Navegação mobile 5 colunas com gaveta 'Mais' e abas com fade) implementada e validada.
5. Polish: `npm test` e `vue-tsc -b` aprovados com zero erros.
