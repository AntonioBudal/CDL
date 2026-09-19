# Tasks: 007 — Zero-G: Superclasse Flutuante & Magnética

**Branch**: `007-zero-g-flutuante` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação da estrutura de pastas e integração do arquivo de estilos modular da Superclasse Zero-G.

- [X] T001 [P] Criar diretório modular de estilos de superclasses e inicializar arquivo base em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T002 [P] Importar `styles/superclasses/zero-g.css` no arquivo principal de estilos em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extensão do subsistema de preferências de aparência (`cadernoAppearance`), tipagem TypeScript e testes de infraestrutura básica.

**⚠️ CRITICAL**: Nenhuma implementação de User Story pode começar antes da conclusão desta fase.

- [X] T003 Atualizar tipagem de preferências com `superclass` e `superclass-intensity` em `caderno-leitura-0.1/frontend/src/appearance.d.ts`
- [X] T004 Estender catálogo declarativo de campos, normalização e persistência no bootstrap em `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js`
- [X] T005 [P] Criar suíte de testes unitários para validação de catálogo e persistência em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

**Checkpoint**: Base de tipos, catálogo e persistência pronta e testada.

---

## Phase 3: User Story 1 - Ativação e Vivência da Superclasse Zero-G no Acervo (Priority: P1) 🎯 MVP

**Goal**: Permitir a ativação da Superclasse Zero-G nas configurações, aplicando aos cartões do acervo bordas discretas, sombras amplas e profundas, oscilação vertical sutil de repouso e atração magnética omnidirecional ao cursor com amortecimento elástico.

**Independent Test**: Ativar "Zero-G" nas configurações de aparência, navegar até a estante de livros (`/books`) e constatar que os cartões oscilam suavemente de forma assíncrona em repouso e respondem com atração física de até 4px ao mover o cursor, retornando com amortecimento elástico gracioso.

- [X] T006 [P] [US1] Definir tokens de geometria, bordas discretas e sombras profundas em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T007 [P] [US1] Definir keyframes de respiração de repouso (idle breathing) e defasagem de fase para `.book-grid > li` em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T008 [P] [US1] Implementar composable `useMagneticHover.ts` para cálculo de deslocamento relativo do cursor em `caderno-leitura-0.1/frontend/src/composables/useMagneticHover.ts`
- [X] T009 [US1] Atribuir variável `--card-index` nos itens da grade e acoplar manipuladores de ponteiro magnético em `caderno-leitura-0.1/frontend/src/views/BooksView.vue`
- [X] T010 [US1] Integrar controles da Superclasse no grupo 11 do painel de configurações em `caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue`

**Checkpoint**: User Story 1 (MVP) 100% funcional e verificável de forma independente.

---

## Phase 4: User Story 2 - Calibração de Intensidade da Física pelo Usuário (Priority: P2)

**Goal**: Disponibilizar o controle de "Intensidade da física" com as opções Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x), escalando matematicamente todas as forças físicas via `--sc-intensity`.

**Independent Test**: Alternar a intensidade no painel de Ajustes e constatar em tempo real que a amplitude de respiração e o deslocamento magnético dobram, diminuem pela metade ou zeram imediatamente sem recarregar a página.

- [X] T011 [P] [US2] Mapear o fator multiplicador `--sc-intensity` para os níveis standard, subtle, high e off em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T012 [P] [US2] Parametrizar cálculos de translação magnética e oscilação vertical via `calc(... * var(--sc-intensity))` em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T013 [US2] Adicionar testes unitários de escala proporcional de intensidade em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

**Checkpoint**: User Stories 1 e 2 operacionais e calibradas parametricamente.

---

## Phase 5: User Story 3 - Estabilidade e Quietude Absoluta no Modo de Leitura (Priority: P3)

**Goal**: Garantir que as telas de leitura de capítulos, anotações de estudo e blocos de texto contínuo permaneçam 100% imóveis e estáticos sob qualquer circunstância.

**Independent Test**: Abrir um capítulo ou anotação de leitura com Zero-G ativado e verificar que nenhum elemento textual sofre translação, oscilação ou atração ao passar o mouse.

- [X] T014 [P] [US3] Isolar explicitamente contêineres de leitura e anotações contra transformações dinâmicas em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T015 [US3] Adicionar asserções de estabilidade de leitura na suíte de testes em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

**Checkpoint**: Soberania ergonômica da leitura garantida e testada.

---

## Phase 6: User Story 4 - Acessibilidade Universal e Neutralização sob Redução de Movimento (Priority: P4)

**Goal**: Neutralizar imediata e completamente qualquer oscilação dinâmica ou efeito magnético quando a preferência do usuário ou do SO indicar redução de movimento (`prefers-reduced-motion` ou opção `motion="off"`).

**Independent Test**: Definir *Transições* como *Desativadas* ou ativar redução de movimento no SO e constatar que a intensidade física é anulada para 0.0x, cessando todo movimento e preservando o acabamento visual estático.

- [X] T016 [P] [US4] Implementar regras de override forçando `--sc-intensity: 0.0 !important;` sob redução de movimento em `caderno-leitura-0.1/frontend/src/styles/superclasses/zero-g.css`
- [X] T017 [US4] Adicionar testes para validação de neutralização total de movimento em `caderno-leitura-0.1/frontend/tests/superclasses.test.mjs`

**Checkpoint**: Conformidade total com acessibilidade WCAG/a11y para distúrbios vestibulares.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de tipos, compilação de produção e homologação com o guia de validação rápida.

- [X] T018 [P] Atualizar documentação e comentários de cabeçalho de estilos em `caderno-leitura-0.1/frontend/src/style.css`
- [X] T019 Executar suíte completa de testes do frontend com `npm test` em `caderno-leitura-0.1/frontend`
- [X] T020 Executar verificação estrita de tipagem e build de produção com `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T021 Executar validação manual interativa guiada por `caderno-leitura-0.1/specs/007-zero-g-flutuante/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Concluída com sucesso.
- **Phase 2 (Foundational)**: Concluída com sucesso.
- **Phase 3 (US1 - MVP)**: Concluída com sucesso.
- **Phase 4 (US2)**: Concluída com sucesso.
- **Phase 5 (US3)**: Concluída com sucesso.
- **Phase 6 (US4)**: Concluída com sucesso.
- **Phase 7 (Polish)**: Concluída com sucesso.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001-T002) [X].
2. Completar Foundational (T003-T005) [X].
3. Implementar User Story 1 (T006-T010) [X].
4. Validar MVP [X].

### Incremental Delivery
1. Setup + Foundational $\to$ Fundação de tipos e catálogo ativa [X].
2. User Story 1 $\to$ Zero-G opera no acervo com estética e magnetismo padrão (MVP) [X].
3. User Story 2 $\to$ Usuário pode calibrar a intensidade (Sutil, Padrão, Alta, Desativada) [X].
4. User Story 3 $\to$ Blindagem do modo de leitura [X].
5. User Story 4 $\to$ Acessibilidade irrestrita via redução de movimento [X].
6. Polish $\to$ Build de produção e homologação ponta a ponta [X].
