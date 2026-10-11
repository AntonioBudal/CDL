# Tasks: Ajustes — Ateliê de Preferências e Leitura Viva

**Feature**: `072-ajustes-atelie-preferencias`
**Input**: Design artifacts from `specs/072-ajustes-atelie-preferencias/`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de tipos compartilhados e catálogo canônico de temas

- [x] T001 Criar definições de tipos e catálogo CANONICAL_THEME_PREVIEWS em caderno-leitura-0.1/frontend/src/types/settings.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Suíte de testes de contrato e integração da feature

- [x] T002 [P] Criar suíte de testes automatizados de contrato e acessibilidade em caderno-leitura-0.1/frontend/tests/feature-072-ajustes-atelie-preferencias.test.mjs
- [x] T003 [P] Declarar exportações de constantes e utilitários de tema em caderno-leitura-0.1/frontend/src/types/index.ts

**Checkpoint**: Base de tipos e suíte de testes prontas para guiar o desenvolvimento.

---

## Phase 3: User Story 1 - Ateliê de Temas Estilo Windows 11 (Priority: P1) 🎯 MVP

**Goal**: Galeria de cartões visuais para cada um dos 10 temas canônicos com caixas de amostra de cor real (fundo, superfície, texto e acento), indicação de tema ativo e acessibilidade total por teclado (`role="radiogroup"` / `role="radio"`).

**Independent Test**: Acessar `/ajustes?tab=aparencia` e verificar a exibição da grade de 10 cartões de pré-visualização cromática, permitindo selecionar temas com resposta imediata e navegação por setas.

### Implementation for User Story 1

- [x] T004 [P] [US1] Criar componente ThemePreviewGrid.vue com boxes de cores reais e marcação WAI-ARIA em caderno-leitura-0.1/frontend/src/components/ThemePreviewGrid.vue
- [x] T005 [US1] Integrar ThemePreviewGrid.vue no seletor de tema em caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue
- [x] T006 [US1] Estilizar ThemePreviewGrid.vue com anel luminoso de seleção, suporte a alto contraste, fidelidade monocromática do tema e-ink e alvos móveis >= 44x44px em caderno-leitura-0.1/frontend/src/components/ThemePreviewGrid.vue

**Checkpoint**: User Story 1 concluída e testável isoladamente como MVP visual!

---

## Phase 4: User Story 2 - Bancada de Leitura Viva e Sincronia Imediata (Priority: P2)

**Goal**: Simulador de leitura em tempo real que reflete a 60 FPS ajustes de tipografia, tamanho de texto, alinhamento e densidade, comportando-se como gaveta inferior retrátil em telas móveis.

**Independent Test**: Modificar tamanho de fonte e entrelinha na aba de Leitura e comprovar que o parágrafo de exemplo da amostra ao vivo reage no mesmo instante sem recarga de tela.

### Implementation for User Story 2

- [x] T007 [P] [US2] Atualizar AppearancePreview.vue para aplicar variáveis CSS locais instantâneas de tipografia e tamanho em caderno-leitura-0.1/frontend/src/components/AppearancePreview.vue
- [x] T008 [US2] Implementar suporte a modo gaveta retrátil (bottom sheet) e botão de recolhimento em caderno-leitura-0.1/frontend/src/components/AppearancePreview.vue

**Checkpoint**: User Stories 1 e 2 operando conjuntamente com feedback ergonômico instantâneo.

---

## Phase 5: User Story 3 - Navegação Contínua por Menu Lateral Vertical (Priority: P3)

**Goal**: Menu lateral vertical de 5 seções substituindo abas horizontais no topo, com sincronização transparente via query string da URL (`/ajustes?tab=...`).

**Independent Test**: Navegar entre as seções pelo menu lateral, verificando transições suaves, destaque do item ativo e manutenção da URL ao recarregar.

### Implementation for User Story 3

- [x] T009 [P] [US3] Reestruturar layout de SettingsView.vue com menu lateral vertical de 5 seções em caderno-leitura-0.1/frontend/src/views/SettingsView.vue
- [x] T010 [US3] Implementar sincronização bidirecional de seção ativa com route.query.tab em caderno-leitura-0.1/frontend/src/views/SettingsView.vue
- [x] T011 [US3] Integrar gatilho móvel para abertura do simulador de leitura como bottom sheet em caderno-leitura-0.1/frontend/src/views/SettingsView.vue

**Checkpoint**: Navegação vertical ergonômica com layout responsivo de 3 colunas em desktop.

---

## Phase 6: User Story 4 - Ateliê de Perfil e Curadoria de Avatar (Priority: P4)

**Goal**: Validação defensiva de upload de avatar (WebP/PNG/JPEG até 2MB, corte 256x256), pré-visualização recortada e preservação da ação de visualizar perfil público.

**Independent Test**: Carregar imagem válida e testar arquivo maior que 2MB na aba de Perfil, confirmando validação e pré-visualização.

### Implementation for User Story 4

- [x] T012 [US4] Refinar validação defensiva de avatar (<= 2MB) e visualização de corte em caderno-leitura-0.1/frontend/src/views/SettingsView.vue

**Checkpoint**: Perfil de usuário refinado com identidade visual protegida.

---

## Phase 7: User Story 5 - Gestão de Conta, Segurança e Diagnóstico (Priority: P5)

**Goal**: Preservação consolidada dos fluxos de alteração de senha, revogação de sessões secundárias, diagnóstico de armazenamento e backup local com tokens semânticos.

**Independent Test**: Acessar as abas de Sistema e Conta & Dispositivos, verificando funcionamento dos diagnósticos e credenciais.

### Implementation for User Story 5

- [x] T013 [US5] Ajustar estilos semânticos e alvos móveis >= 44x44px nos formulários de conta e sistema em caderno-leitura-0.1/frontend/src/views/SettingsView.vue

**Checkpoint**: Todas as 5 User Stories implementadas e funcionais.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validação de acessibilidade, contraste, ausência de emojis e testes globais

- [x] T014 [P] Auditar conformidade estrita de zero emojis e tokens CSS semânticos em caderno-leitura-0.1/frontend/src/components/ThemePreviewGrid.vue
- [x] T015 Executar suíte completa de testes automatizados e compilação de produção conforme caderno-leitura-0.1/frontend/tests/feature-072-ajustes-atelie-preferencias.test.mjs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências, inicia imediatamente.
- **Foundational (Phase 2)**: Depende da Phase 1; bloqueia a implementação das histórias.
- **User Story 1 (Phase 3 - P1)**: Depende da Phase 2; não depende de outras histórias.
- **User Story 2 (Phase 4 - P2)**: Depende da Phase 2; integra-se com preferências.
- **User Story 3 (Phase 5 - P3)**: Depende das fases 3 e 4 para layout integrado.
- **User Story 4 (Phase 6 - P4)**: Depende da Phase 5 (seção de perfil no layout).
- **User Story 5 (Phase 7 - P5)**: Depende da Phase 5 (seções de conta e sistema no layout).
- **Polish (Phase 8)**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- `T002` e `T003` podem ser executadas em paralelo.
- `T004` (novo componente `ThemePreviewGrid.vue`) e `T007` (`AppearancePreview.vue`) afetam arquivos diferentes e podem ser desenvolvidos em paralelo.
- `T014` pode rodar em paralelo com as revisões finais de estilo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Tipos) e Phase 2 (Testes de contrato).
2. Concluir Phase 3 (Cartões de preview estilo Windows 11 com caixas de cores reais).
3. **VALIDAÇÃO MVP**: Comprovar que os 10 temas têm boxes visuais funcionais.
4. Avançar para as fases seguintes de forma incremental.
