# Tasks: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Feature**: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global  
**Branch**: `065-livros-header` | **Date**: 2026-10-10  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup (Componentes Base e Estrutura)

**Purpose**: Criação dos componentes isolados de gaveta lateral deslizante e subcomponentes desacoplados de navegação e conta.

- [X] T001 Criar componente `Drawer.vue` acessível e acelerado por GPU em `frontend/src/components/ui/Drawer.vue` com largura de 420px desktop / 100% mobile, foco gerenciado, tecla `Esc`, backdrop e suporte a `prefers-reduced-motion`
- [X] T002 [P] Criar componente `UserDropdown.vue` em `frontend/src/components/layout/UserDropdown.vue` com avatar/iniciais, nome do usuário, link de perfil e botão "Sair" integrado com confirmação
- [X] T003 [P] Criar componente `NavigationTabs.vue` em `frontend/src/components/layout/NavigationTabs.vue` com as 4 abas primárias (`Livros`, `Destaques`, `Revisão`, `Inbox`), badges dinâmicos e menu retrátil "Mais ▾" (`Importar`, `Amigos`, `Ajustes`, `Lixeira`, `Admin`)

---

## Phase 2: Foundational (App Shell e Header Global)

**Purpose**: Estruturação do novo App Shell em 3 zonas operacionais substituindo o cabeçalho monolítico.

**CRITICAL**: O novo cabeçalho mestre deve ser integrado antes das alterações específicas da biblioteca.

- [X] T004 Criar componente `GlobalHeader.vue` em `frontend/src/components/layout/GlobalHeader.vue` organizando os 3 blocos semânticos (Marca à esquerda, `NavigationTabs` ao centro, e Ferramentas / `UserDropdown` à direita)
- [X] T005 Integrar `GlobalHeader.vue` em `frontend/src/App.vue`, eliminando o cabeçalho monolítico antigo e removendo o botão solto "Sair" do plano superior
- [X] T006 Ajustar regras CSS em `frontend/src/style.css` para suporte à arquitetura em 3 blocos do Header com imunidade cromática estrita aos 10 temas nativos

**Checkpoint**: Header Global em 3 blocos ativo e operando em todas as rotas do sistema.

---

## Phase 3: User Story 1 - Header Global em 3 Zonas Operacionais (Priority: P1) [MVP]

**Goal**: Entregar o cabeçalho unificado com as 4 abas primárias, menu "Mais ▾", ferramentas à direita e ação de logout encapsulada exclusivamente no dropdown do usuário.

**Independent Test**: Navegar pelas rotas autenticadas confirmando a disposição em 3 blocos, funcionamento do menu "Mais ▾", badges reativos de pendências e encerramento de sessão pelo menu do usuário.

### Implementação para User Story 1

- [X] T007 [US1] Implementar controle acessível de abertura/fechamento do menu "Mais ▾" com navegação por teclado (`Tab`, `Esc`, `Enter`), `aria-expanded` e fechamento ao clicar fora em `frontend/src/components/layout/NavigationTabs.vue`
- [X] T008 [US1] Implementar controle acessível do dropdown do usuário em `frontend/src/components/layout/UserDropdown.vue` com confirmação e redirecionamento de logout
- [X] T009 [US1] Ajustar adaptação responsiva do Header para telas intermediárias (1024px–1280px) e mobile (< 768px), integrando `MobileMoreMenu.vue` sem estouro horizontal

**Checkpoint**: User Story 1 funcional e testável de ponta a ponta.

---

## Phase 4: User Story 2 - Biblioteca Ativa em Largura Total e Drawer Deslizante de Cadastro (Priority: P1) [MVP]

**Goal**: Eliminar a coluna estática lateral de formulário em `/livros`, expandir o acervo para largura total e prover cadastro focado via gaveta lateral deslizante (`Drawer`).

**Independent Test**: Acessar `/livros`, confirmar largura total do acervo sem painel lateral estático, acionar `+ Adicionar Livro`, testar abertura em 220ms, preenchimento e criação do livro via API sem erros.

### Implementação para User Story 2

- [X] T010 [US2] Remover a coluna estática lateral de formulário `aside.panel.form-panel` em `frontend/src/views/BooksView.vue` e converter o layout da biblioteca para largura total (`full-width`)
- [X] T011 [US2] Adicionar botão de ação primária `+ Adicionar Livro` na barra de ações da biblioteca em `frontend/src/components/LibraryToolbar.vue` e no cabeçalho do acervo em `frontend/src/views/BooksView.vue`
- [X] T012 [US2] Integrar o componente `Drawer.vue` em `frontend/src/views/BooksView.vue` encapsulando o formulário de cadastro (Título, Autor opcional, Categorias opcionais via `CategoryInput.vue`) com retenção de foco e tecla `Esc`
- [X] T013 [US2] Conectar a submissão do formulário no Drawer ao método `api.createBook`, com tratamento de erros, estado de carregamento e proteção contra perda de dados não salvos

**Checkpoint**: User Story 2 funcional; a biblioteca agora opera em largura total com fluxo de Drawer limpo e focado.

---

## Phase 5: User Story 3 - Hero de Leitura Ativa ("Em Andamento") e Estante Fluida (Priority: P2)

**Goal**: Destacar a obra em andamento no topo da biblioteca através de um Hero Card editorial e aprimorar a grade fluida com proporções de livros e elevação tátil.

**Independent Test**: Carregar a biblioteca com livros cadastrados, confirmar a renderização do Hero Card com atalho direto de leitura e testar a elevação suave no hover dos livros da estante.

### Implementação para User Story 3

- [X] T014 [US3] Criar componente `BookHeroCard.vue` em `frontend/src/components/library/BookHeroCard.vue` destacando a obra mais recente com capa proporcional, título, autor, metadados e atalho "Continuar leitura"
- [X] T015 [US3] Integrar o `BookHeroCard.vue` na seção superior de `frontend/src/views/BooksView.vue` (suprimindo a seção de forma elegante caso o acervo esteja vazio)
- [X] T016 [US3] Refinar estilos da grade curatorial em `frontend/src/views/BooksView.vue` e `frontend/src/style.css`, aplicando proporções realistas de capa e elevação sutil no hover (`transform: translateY(-4px)`, 150ms)
- [X] T017 [US3] Assegurar transição suave e contínua entre os modos Grade e Lista sem recarga da página

**Checkpoint**: User Stories 1, 2 e 3 integradas com composição editorial completa.

---

## Phase 6: User Story 4 - Responsividade e Acessibilidade (Mobile, Teclado, Reduced Motion) (Priority: P3)

**Goal**: Garantir excelência ergonômica em todas as resoluções, alvos de toque $\ge 44 \times 44$px e neutralização de movimento para preferências de acessibilidade.

**Independent Test**: Auditar alvos táteis em viewport de 375px, validar foco por teclado em toda a navegação e verificar execução instantânea das animações sob `prefers-reduced-motion`.

### Implementação para User Story 4

- [X] T018 [US4] Assegurar alvos táteis mínimos de $44 \times 44$px em todos os botões, links de abas e controles do Drawer em resoluções móveis
- [X] T019 [US4] Aplicar e verificar regra de `prefers-reduced-motion` no `Drawer.vue` e nos cartões de livro para garantir transição imediata (0.01ms)
- [X] T020 [US4] Validar conformidade de contraste e imunidade cromática nos 10 temas nativos sem valores hexadecimais literais arbitrários

**Checkpoint**: Todas as 4 histórias de usuário plenamente acessíveis e responsivas.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de conformidade visual, ausência absoluta de emojis e validação completa das suítes de testes.

- [X] T021 [P] Criar suíte de testes unitários de frontend em `frontend/tests/feature-065-livros-header.test.mjs` validando o Header em 3 blocos, menu do usuário com logout, Drawer acessível e ausência de emojis
- [X] T022 Auditar código-fonte dos novos componentes para garantir estrita ausência de emojis e uso exclusivo do catálogo `Icon.vue`
- [X] T023 Executar testes completos (`npm test`, `pytest`) e build de produção (`npm run build`)

---

## Dependencies & Execution Order

### Dependência entre Fases

1. **Setup (Phase 1)**: Sem dependências — criação dos blocos base (`Drawer.vue`, `UserDropdown.vue`, `NavigationTabs.vue`).
2. **Foundational (Phase 2)**: Depende da Phase 1 — criação do `GlobalHeader.vue` e integração no `App.vue`.
3. **User Story 1 (Phase 3)**: Depende da Phase 2 — refinamento do Header, menu "Mais ▾" e responsividade.
4. **User Story 2 (Phase 4)**: Depende da Phase 1 e 2 — remoção da coluna estática de `BooksView.vue` e integração do `Drawer.vue`.
5. **User Story 3 (Phase 5)**: Depende da Phase 4 — Hero Card "Em Andamento" e estante fluida.
6. **User Story 4 (Phase 6)**: Depende das fases anteriores — acessibilidade fina, alvos táteis e `prefers-reduced-motion`.
7. **Polish (Phase 7)**: Depende de todas as fases implementadas.
