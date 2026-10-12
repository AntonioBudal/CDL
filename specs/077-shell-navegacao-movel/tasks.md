# Tasks: Shell e Navegação Móvel

**Feature**: `077-shell-navegacao-movel`  
**Input**: [spec.md](spec.md) | [plan.md](plan.md) | [shell-navigation.contract.md](contracts/shell-navigation.contract.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparação de baseline e contratos de arquivos

- [x] T001 Criar arquivo esqueleto `caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue`
- [x] T002 Criar arquivo de teste dedicado `caderno-leitura-0.1/frontend/tests/feature-077-shell-mobile.test.mjs`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tokens globais de offset e variáveis de navegação móvel compartilhados entre todas as histórias

**CRITICAL**: As regras de token bloqueiam o posicionamento da barra e de elementos flutuantes.

- [x] T003 Declarar tokens `--mobile-nav-height: 56px;` e `--mobile-nav-offset: calc(var(--mobile-nav-height) + env(safe-area-inset-bottom, 0px));` em `:root` dentro de `caderno-leitura-0.1/frontend/src/mobile-navigation.css` e `tokens.css`
- [x] T004 [P] Configurar variáveis CSS de safe-area e regras de container em `caderno-leitura-0.1/frontend/src/style.css` e `mobile-navigation.css`

**Checkpoint**: Tokens fundamentais registrados e disponíveis para todos os componentes.

---

## Phase 3: User Story 1 - Navegação Móvel por Barra Inferior (Priority: P1) [MVP]

**Goal**: Restaurar a barra móvel inferior (`MobileTabBar.vue`) com 5 colunas simétricas, alvos de toque $\ge 44 \times 44\text{ px}$ e safe-area.

**Independent Test**: Em viewport `< 768px`, a barra fixa de 5 colunas aparece no rodapé com indicador ativo na rota atual e respeita safe-area.

### Implementation for User Story 1

- [x] T005 [US1] Implementar template, script e estilos de `MobileTabBar.vue` em `caderno-leitura-0.1/frontend/src/components/layout/MobileTabBar.vue` com 5 itens (Início, Livros, Destaques, Revisão e gatilho Mais) e dimensões táteis mínimas de 44x44px
- [x] T006 [US1] Integrar `MobileTabBar.vue` no shell em `caderno-leitura-0.1/frontend/src/App.vue` (`v-if="!route.meta?.cleanScreen && auth.isAuthenticated.value"`)
- [x] T007 [US1] Ajustar regras de `.mobile-tab-bar` em `caderno-leitura-0.1/frontend/src/mobile-navigation.css` para garantir `display: none` em $\ge 768\text{px}$ e `display: grid` com 5 colunas proporcionais em `< 768px`

**Checkpoint**: Barra inferior renderizada e funcional no mobile sem afetar visualização desktop.

---

## Phase 4: User Story 2 - Cabeçalho Superior Limpo e Gaveta "Mais" Completa (Priority: P1)

**Goal**: Ocultar abas superiores em `< 768px` e expandir `MobileMoreMenu.vue` com Caixa de Entrada, Amigos, Ajustes, Lixeira, Importar e badges reativos.

**Independent Test**: Em `< 768px`, o cabeçalho superior não exibe abas textuais de navegação. Ao acionar o botão "Mais", a gaveta abre com todas as rotas secundárias e seus contadores.

### Implementation for User Story 2

- [x] T008 [US2] Adicionar media query em `caderno-leitura-0.1/frontend/src/components/layout/GlobalHeader.vue` e `NavigationTabs.vue` para aplicar `display: none` nas abas textuais em `@media (max-width: 767px)`
- [x] T009 [US2] Importar `useInboxCount` e `useFriends` em `caderno-leitura-0.1/frontend/src/components/navigation/MobileMoreMenu.vue` e incluir links para `/inbox`, `/amigos` e `/importar` com seus respectivos badges numéricos
- [x] T010 [US2] Conectar badge de notificação secundária em `MobileTabBar.vue` para sinalizar pendências de inbox ou amigos no botão "Mais"

**Checkpoint**: Cabeçalho móvel despoluído e gaveta secundária com acesso completo a todas as rotas da aplicação.

---

## Phase 5: User Story 3 - Offsets de Elementos Flutuantes e Notificações (Priority: P2)

**Goal**: Evitar sobreposição de elementos inferiores (toasts, lote da lixeira, FAB) e corrigir dropdown de notificações em telas estreitas ($\le 430\text{px}$).

**Independent Test**: Disparar toasts e inspecionar `.trash-batch-bar` e `.fab-preview` em `< 768px`; abrir notificações em $\le 430\text{px}$ sem corte lateral.

### Implementation for User Story 3

- [x] T011 [US3] Atualizar `caderno-leitura-0.1/frontend/src/views/StudyView.vue` e `HighlightsLibraryView.vue` para usar `--mobile-nav-offset` no posicionamento inferior do container de avisos
- [x] T012 [P] [US3] Ajustar posicionamento de `.trash-batch-bar` em `caderno-leitura-0.1/frontend/src/views/TrashView.vue` usando `bottom: calc(var(--mobile-nav-offset, 0px) + 0.75rem)`
- [x] T013 [P] [US3] Ajustar posicionamento de `.fab-preview` em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue` usando `bottom: calc(var(--mobile-nav-offset, 0px) + 1rem)`
- [x] T014 [US3] Atualizar `caderno-leitura-0.1/frontend/src/components/notifications/NotificationsDropdown.vue` com regras para viewports $\le 430\text{px}$ ocupando largura fluida total (`left: 0.5rem; right: 0.5rem; width: auto; max-width: calc(100vw - 1rem)`)

**Checkpoint**: Nenhum elemento fixo inferior sobrepõe a barra de navegação móvel e notificações não transbordam.

---

## Phase 6: User Story 4 - Reescrita Nativa do `ShareModal` e Purga de CSS Morto (Priority: P2)

**Goal**: Substituir classes Tailwind por CSS autoral com tokens de tema em `ShareModal.vue` e purgar seletores obsoletos em `App.vue`.

**Independent Test**: Abrir modal de compartilhamento em tema claro/escuro e verificar estilo íntegro; auditar CSS de `App.vue` sem regras órfãs.

### Implementation for User Story 4

- [x] T015 [US4] Reescrever markup e criar bloco `<style scoped>` em `caderno-leitura-0.1/frontend/src/components/sharing/ShareModal.vue` utilizando variáveis de tema nativas (`--color-surface`, `--color-border`, etc.) sem Tailwind
- [x] T016 [US4] Purgar estilos obsoletos e seletores legados de cabeçalho no bloco `<style scoped>` de `caderno-leitura-0.1/frontend/src/App.vue`

**Checkpoint**: `ShareModal` renderiza sem utilitários ausentes e CSS do shell está enxuto.

---

## Phase 7: User Story 5 - Testes de Navegação Móvel Amarrados aos Templates Reais (Priority: P1)

**Goal**: Validar no `node --test` que os seletores testados existem nos templates Vue reais, eliminando falsos positivos.

**Independent Test**: Executar `npm test` e constatar que remoção de classes dos templates acarreta falha nos testes.

### Implementation for User Story 5

- [x] T017 [US5] Atualizar `caderno-leitura-0.1/frontend/tests/mobile_navigation_contrast.test.mjs` para checar os seletores de `MobileTabBar.vue` e `MobileMoreMenu.vue` diretamente nos templates dos componentes
- [x] T018 [US5] Implementar asserções no novo teste `caderno-leitura-0.1/frontend/tests/feature-077-shell-mobile.test.mjs` cobrindo 100% dos requisitos (5 colunas, alvos de 44px, tokens de offset, ShareModal sem Tailwind e purge de CSS)

**Checkpoint**: Suíte de testes protege contra qualquer regressão estrutural no shell móvel.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificação global de integridade, acessibilidade e builds

- [x] T019 Executar testes completos do frontend com `npm test` em `caderno-leitura-0.1/frontend`
- [x] T020 Executar build de produção do frontend com `npm run build` em `caderno-leitura-0.1/frontend`
- [x] T021 Atualizar checklist em `specs/077-shell-navegacao-movel/checklists/requirements.md` com status de validação

---

## Dependencies & Execution Order

- **Phase 1 & Phase 2**: Podem iniciar imediatamente e bloqueiam as demais fases.
- **Phase 3 (US1)**: Inicia após a fase 2 (entrega o MVP da barra móvel).
- **Phase 4 (US2)**: Inicia após a fase 3 (completa cabeçalho e menu Mais).
- **Phase 5 (US3)** e **Phase 6 (US4)**: Podem ser executadas em paralelo ou em sequência após a fase 4.
- **Phase 7 (US5)**: Valida todos os componentes criados e modificados.
- **Phase 8**: Consolidação final e validação de build.
