# Tasks: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Feature**: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global  
**Branch**: `065-livros-header` | **Date**: 2026-10-10  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup & Shared Infrastructure

**Purpose**: Estrutura dos componentes desacoplados e tokens base

- [x] T001 Criar componente `Drawer.vue` acessível e acelerado por GPU em `frontend/src/components/ui/Drawer.vue` (420px desktop / 100% mobile, foco gerenciado, tecla `Esc`, backdrop e `prefers-reduced-motion`)
- [x] T002 Criar componente `UserDropdown.vue` em `frontend/src/components/layout/UserDropdown.vue` com avatar/iniciais, nome do usuário, link de perfil e ação "Sair" com confirmação
- [x] T003 Criar componente `NavigationTabs.vue` em `frontend/src/components/layout/NavigationTabs.vue` com as 4 abas primárias (`Livros`, `Destaques`, `Revisão`, `Inbox`), badges dinâmicos e menu retrátil "Mais ▾"

---

## Phase 2: Foundational (Header Centralization, Clean Icons & UI Harmony)

**Purpose**: Resolução da fragmentação visual do cabeçalho, centralização matemática e hierarquia intencional

- [x] T004 [US1] Refatorar layout de `.header-inner` em `frontend/src/components/layout/GlobalHeader.vue` para CSS Grid (`1fr auto 1fr`), garantindo centralização horizontal matemática da barra de navegação central
- [x] T005 [US1] Remover badge textual `Ctrl K` do botão de busca (`search-trigger-btn`) em `frontend/src/components/layout/GlobalHeader.vue`, mantendo pílula translúcida suave e acessível
- [x] T006 [US1] Refatorar botão de captura (`quick-capture-trigger-btn`) em `frontend/src/components/layout/GlobalHeader.vue` para exibir **apenas o `+`** com formato circular/arredondado de destaque primário e tooltip explicativo
- [x] T007 [US1] Simplificar `frontend/src/components/sync/SyncStatusBadge.vue` para exibir **estritamente um ícone pequeno** discreto com cor semântica e tooltip informativo, sem caixas escuras ou texto
- [x] T008 [US1] Padronizar visualmente o gatilho `Mais ▾` em `frontend/src/components/layout/NavigationTabs.vue` para seguir a mesma tipografia e estado de hover das abas principais
- [x] T009 [US1] Garantir encapsulamento seguro de `Sair da conta` dentro do `UserDropdown.vue`

---

## Phase 3: User Story 2 - Biblioteca Ativa em Largura Total e Drawer Deslizante (Priority: P1) [MVP]

**Goal**: Exibir a estante em largura total sem formulário lateral fixo e prover cadastro focado via gaveta lateral

- [x] T010 [US2] Remover a coluna estática lateral de formulário `aside.panel.form-panel` em `frontend/src/views/BooksView.vue` para expansão em largura total
- [x] T011 [US2] Adicionar botão `+ Adicionar Livro` no topo da estante disparando o `Drawer.vue`
- [x] T012 [US2] Integrar o formulário de cadastro de livros no `Drawer.vue` com foco retido no primeiro campo e tecla `Esc` ativa

---

## Phase 4: User Story 3 - Hero "Lendo Agora" e Estante Fluida Editorial (Priority: P2)

**Goal**: Destacar a leitura ativa no topo e fornecer estante fluida com acabamento editorial

- [x] T013 [US3] Implementar componente `BookHeroCard.vue` e integrá-lo no topo da página de Livros destacando a leitura ativa ("Lendo Agora")
- [x] T014 [US3] Reorganizar o grid da biblioteca em largura total com elevação sutil no hover das capas (`translateY(-4px)` em 150ms)

---

## Phase 5: Verification & Automated Tests

**Purpose**: Verificação completa de requisitos, contratos de UI e não-regressão

- [x] T015 Atualizar e expandir testes unitários em `frontend/tests/feature-065-livros-header.test.mjs` validando centralização via Grid, ausência de `Ctrl K` visual, botão `+` de captura, e ícone discreto de sync
- [x] T016 Executar suite completa de testes (`npm test` e `npm run build`) garantindo conformidade com os 10 temas nativos e zero emojis
