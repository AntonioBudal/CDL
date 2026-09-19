# Tasks: Central de Ajustes com Preview ao Vivo e Organização em Três Seções

**Feature Branch**: `014-central-ajustes-preview`  
**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/settings-ui-contract.md](./contracts/settings-ui-contract.md), [quickstart.md](./quickstart.md)  
**Status**: Ready for Implementation  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificação do ambiente frontend e tipagens compartilhadas

- [x] T001 Validar infraestrutura do frontend e ambiente de testes com `npm test` em `caderno-leitura-0.1/frontend`
- [x] T002 [P] Configurar tipos e interfaces TypeScript para abas de ajustes (`SettingsTabId`), diagnósticos de armazenamento e estado de modal em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura básica de redefinição de aparência e métodos de diagnóstico

- [x] T003 Expandir declarações em `caderno-leitura-0.1/frontend/src/appearance.d.ts` com o método `factoryReset` e metadados de diagnóstico
- [x] T004 Atualizar `caderno-leitura-0.1/frontend/src/appearance-bootstrap.js` adicionando rotina atômica de restauração de fábrica (`factoryReset`) e purga de chaves órfãs/legadas
- [x] T005 [P] Criar esqueleto de testes automatizados para diagnóstico de storage e reset de aparência em `caderno-leitura-0.1/frontend/tests/settings-central.test.mjs`

---

## Phase 3: User Story 1 - Organização Estruturada em Três Seções (Priority: P1) 🎯 MVP

**Goal**: Permitir ao usuário alternar instantaneamente entre as seções de **Aparência**, **Leitura** e **Sistema** através de uma barra de abas segmentadas acessível WAI-ARIA.

**Independent Test**: Acessar `/ajustes` e alternar entre "Aparência", "Leitura" e "Sistema" usando o mouse e as teclas de setas horizontais, verificando que os controles de cada grupo são exibidos sem recarregar a página e sem quebrar a transição do Vue Router.

### Implementation for User Story 1

- [x] T006 [US1] Implementar barra de abas segmentadas WAI-ARIA (`role="tablist"`, `role="tab"`, `role="tabpanel"`) com navegação por teclado (ArrowLeft, ArrowRight, Enter, Space) em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- [x] T007 [US1] Refatorar `caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue` para suportar filtragem por seção ativa (`tab: 'aparencia' | 'leitura'`), exibindo temas/superclasses em Aparência e tipografia/densidade/marcação em Leitura
- [x] T008 [P] [US1] Adicionar estilos CSS para a barra de abas segmentadas (`.settings-tabs`, `.settings-tab`, foco acessível) em `caderno-leitura-0.1/frontend/src/appearance-advanced.css`
- [x] T009 [US1] Garantir envoltório raiz único `<section class="settings-page wrap">` em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue` para estabilidade estrita com `<Transition mode="out-in">` de `App.vue`

**Checkpoint**: User Story 1 completa e testável de forma independente. As abas de navegação alternam instantaneamente os blocos de configuração.

---

## Phase 4: User Story 2 - Amostra Dinâmica e Preview ao Vivo de Tokens e Estilos (Priority: P2)

**Goal**: Exibir amostra interativa com livro realista e abas de estudo em painel lateral direito fixo (*sticky*) no desktop e adaptativo no mobile, com reflexo imediato (< 50ms) de qualquer alteração de estilo.

**Independent Test**: Modificar tema, fonte, superclasse e modo de acervo (grade/lista), confirmando que o cartão de amostra, os botões e as abas de leitura atualizam na hora ao lado dos controles.

### Implementation for User Story 2

- [x] T010 [P] [US2] Implementar layout de 2 colunas no desktop (> 1024px) com painel de preview fixo/aderente (`position: sticky`) e rolagem independente em `caderno-leitura-0.1/frontend/src/appearance-advanced.css`
- [x] T011 [US2] Enriquecer `caderno-leitura-0.1/frontend/src/components/AppearancePreview.vue` para reagir dinamicamente a `preferences.library` exibindo amostra em modo grade (`.book-grid`) ou lista compacta (`.book-list`)
- [x] T012 [US2] Adicionar botões demonstrativos de ações primárias e desabilitadas na amostra de `caderno-leitura-0.1/frontend/src/components/AppearancePreview.vue` refletindo a física e tokens da Superclasse ativa
- [x] T013 [US2] Adaptar responsividade móvel (<= 1024px) para empilhar a amostra abaixo dos controles de forma fluida com áreas de toque de no mínimo 44px em `caderno-leitura-0.1/frontend/src/appearance-advanced.css`

**Checkpoint**: User Stories 1 e 2 funcionais juntas. O preview ao vivo acompanha a navegação dos controles e reflete todos os estados visuais.

---

## Phase 5: User Story 3 - Central de Diagnóstico, Precedência E-Ink e Persistência (Priority: P3)

**Goal**: Fornecer na aba "Sistema" um centro de diagnóstico completo com informativo de persistência, status da API local, uso de armazenamento do navegador, botão de reset de fábrica com diálogo de confirmação e painel de backup.

**Independent Test**: Acessar a aba "Sistema", verificar o status de conexão verde da API local, inspecionar a contagem de bytes do `localStorage`, clicar em "Restaurar Padrões", cancelar e em seguida confirmar o reset, verificando o retorno imediato aos padrões de fábrica.

### Implementation for User Story 3

- [x] T014 [US3] Implementar painel informativo de escopo de persistência (armazenamento local no navegador vs banco SQLite `caderno.db`) na aba Sistema em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- [x] T015 [P] [US3] Implementar utilitário de medição e exibição do armazenamento local (`localStorage` bytes estimados e contagem de chaves) na aba Sistema em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- [x] T016 [US3] Implementar verificação reativa de conectividade local via `GET /api/health` com medição de latência e atalho para `/conexao` em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- [x] T017 [US3] Criar componente de diálogo modal acessível `caderno-leitura-0.1/frontend/src/components/ConfirmResetModal.vue` com foco inicial, fechamento com `Esc` e trap de foco
- [x] T018 [US3] Conectar a ação de restauração de fábrica ao modal, disparando `factoryReset`, feedback visual com `aria-live` e embutindo `caderno-leitura-0.1/frontend/src/components/DatabaseBackup.vue` na aba Sistema
- [x] T019 [US3] Validar e reforçar a precedência estrita do tema `e-ink` (desativação de saturação e física) e conformidade com `prefers-reduced-motion` em `caderno-leitura-0.1/frontend/src/components/AppearanceControls.vue`

**Checkpoint**: As três User Stories estão 100% implementadas e integradas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testes automatizados, verificação de build e conformidade de acessibilidade

- [x] T020 [P] Implementar suíte completa de testes automatizados em `caderno-leitura-0.1/frontend/tests/settings-central.test.mjs` validando abas, diagnóstico de storage, health check e reset de fábrica
- [x] T021 Executar suíte completa de testes com `npm test` garantindo 100% de aprovação
- [x] T022 Executar compilação com `npm run build` garantindo zero erros de tipagem TypeScript e empacotamento Vite
- [x] T023 Validar roteiro de cenários manuais conforme `caderno-leitura-0.1/specs/014-central-ajustes-preview/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA as histórias de usuário.
- **User Stories (Phases 3 a 5)**: Dependem da Phase 2 concluída.
  - US1 (Aparência, Leitura, Sistema em abas): Depende da Phase 2.
  - US2 (Preview sticky 2 colunas e dinâmica): Depende de US1.
  - US3 (Central de Diagnóstico e Reset): Depende de US1 e US2.
- **Polish (Phase 6)**: Depende de todas as histórias implementadas.

### Parallel Opportunities

- T002 e T005 podem rodar em paralelo com tarefas de infraestrutura.
- T008 e T010 (estilos CSS) podem ser desenvolvidos em paralelo com componentes Vue.
- T015 (utilitário de storage) pode ser desenvolvido em paralelo com T016 (health check).
- T020 (testes unitários) pode ser incrementado paralelamente ao desenvolvimento dos componentes.

---

## Implementation Strategy (MVP First)

1. **Fase 1 e 2**: Preparar tipagem, reset de fábrica e purga de chaves em `appearance-bootstrap.js`.
2. **Fase 3 (MVP - US1)**: Entregar a navegação segmentada em 3 abas em `SettingsView.vue` e `AppearanceControls.vue`. Testar e validar isoladamente.
3. **Fase 4 (US2)**: Adicionar o layout de 2 colunas com preview sticky e cartão adaptativo (grade/lista) em `AppearancePreview.vue`.
4. **Fase 5 (US3)**: Implementar a Central Completa de Diagnóstico na aba Sistema com medição de storage, health check, modal de reset e backup.
5. **Fase 6 (Finalização)**: Executar testes automatizados (`npm test`) e build de produção (`npm run build`).
