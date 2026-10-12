# Tasks: Correções Visuais, de Cor e de Disposição

**Feature**: `075-correcoes-visuais-disposicao`  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  
**Date**: 2026-10-11  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criação do arcabouço de teste de integridade de tokens CSS

- [X] T001 Criar suíte de teste automatizado de integridade CSS em tests/feature-075-css-tokens-integrity.test.mjs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Camada de compatibilidade de variáveis CSS que desbloqueia a adaptação de todos os temas

> **CRITICAL**: Nenhuma alteração de componente pode ser validada antes de consolidar a camada de compatibilidade de tokens.

- [X] T002 Implementar a camada de compatibilidade com os 115 apelidos de variáveis CSS legadas em caderno-leitura-0.1/frontend/src/tokens.css
- [X] T003 Executar teste de integridade em tests/feature-075-css-tokens-integrity.test.mjs validando zero variáveis indefinidas

**Checkpoint**: Camada de tokens estabelecida e validada de forma automatizada.

---

## Phase 3: User Story 1 - Toda tela legível em qualquer um dos dez temas (Priority: P1) [MVP]

**Goal**: Eliminar fundos brancos fixos, bordas destoantes e falhas de contraste em temas escuros e quentes

**Independent Test**: Executar teste de tokens e inspecionar telas de Destaques, Revisão e Biblioteca no tema Grafite e Pergaminho, verificando ausência de caixas brancas fixas e contraste $\ge 4,5:1$.

- [X] T004 [US1] Ajustar herança de estilos e remover cores de fallback fixas em caderno-leitura-0.1/frontend/src/components/ui/EmptyState.vue
- [X] T005 [P] [US1] Ajustar estilos de cartões e superfícies em caderno-leitura-0.1/frontend/src/components/HighlightCard.vue
- [X] T006 [P] [US1] Ajustar contêineres e cartões da biblioteca de destaques em caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue
- [X] T007 [P] [US1] Ajustar painéis e contêineres do hub de revisão em caderno-leitura-0.1/frontend/src/views/ReviewHubView.vue

**Checkpoint**: MVP concluído — componentes e contêineres base herdam temas perfeitamente sem caixas brancas fixas.

---

## Phase 4: User Story 2 - Navegação e organização de livros e capas (Priority: P2)

**Goal**: Alinhamento harmonioso da grade de livros, miniatura limpa sem título truncado, selos transparentes e barra despoluída

**Independent Test**: Acessar `/livros` com 1 a 3 livros, alternar entre grade e lista, inspecionar selos de categoria e botão de adicionar livro.

- [X] T008 [US2] Modificar alinhamento da grade com auto-fill e justify-content start em caderno-leitura-0.1/frontend/src/appearance-advanced.css
- [X] T009 [P] [US2] Ocultar título em miniatura de capa pequena size="sm" em caderno-leitura-0.1/frontend/src/components/BookCover.vue
- [X] T010 [P] [US2] Definir fundo transparente e cores semânticas do tema em caderno-leitura-0.1/frontend/src/components/CategoryBadge.vue
- [X] T011 [P] [US2] Remover sinal de mais duplicado no botão de adicionar livro em caderno-leitura-0.1/frontend/src/views/BooksView.vue
- [X] T012 [US2] Ajustar seletor grade/lista com espaçamento visível e cores de busca em caderno-leitura-0.1/frontend/src/components/LibraryToolbar.vue

**Checkpoint**: Tela de Livros perfeitamente alinhada e organizada em ambos os modos de exibição.

---

## Phase 5: User Story 3 - Gestão e visualização de estudos do livro (Priority: P2)

**Goal**: Acessibilidade e ergonomia visual nas visões de estudos de `/livros/:id` (Lista, Árvore e Mapa)

**Independent Test**: Acessar detalhes de um livro com estudos, inspecionar alinhamento da tabela, visibilidade de ícones da árvore e botões do mapa em tema escuro.

- [X] T013 [US3] Atualizar menu e selos com fundo transparente e indicadores semânticos acessíveis em caderno-leitura-0.1/frontend/src/components/StudyStatusBadge.vue
- [X] T014 [P] [US3] Alinhar cabeçalhos com células, adicionar ícones de ordenação e ampliar área tátil em caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue
- [X] T015 [P] [US3] Remover color: var(--color-inverse-bg) e restaurar contraste de ícones em caderno-leitura-0.1/frontend/src/components/views/StudyTreeNodeItem.vue
- [X] T016 [P] [US3] Ajustar contraste de zoom e ocultar barra mobile em telas desktop em caderno-leitura-0.1/frontend/src/components/views/StudyMapView.vue

**Checkpoint**: Visualizações de estudos em `/livros/:id` acessíveis, legíveis e com controles padronizados.

---

## Phase 6: User Story 4 - Cabeçalho, rodapé e estados vazios da aplicação (Priority: P3)

**Goal**: Despoluição do botão de perfil do usuário, equilíbrio no rodapé da aplicação e centralização de estados vazios

**Independent Test**: Inspecionar cabeçalho autenticado, rodapé em desktop/mobile e aba de bloqueados em amigos.

- [X] T017 [US4] Reestruturar alinhamento desktop e quebra responsiva sem pontuação órfã em caderno-leitura-0.1/frontend/src/components/layout/AppFooter.vue
- [X] T018 [P] [US4] Simplificar gatilho de perfil para exibir unicamente avatar de 44x44px em caderno-leitura-0.1/frontend/src/components/layout/UserDropdown.vue
- [X] T019 [P] [US4] Centralizar estado vazio de usuários bloqueados utilizando EmptyState em caderno-leitura-0.1/frontend/src/views/FriendsView.vue

**Checkpoint**: Cabeçalho, rodapé e estados vazios equilibrados e integrados ao design system.

---

## Phase 7: User Story 5 - Páginas públicas, links externos e persistência do tema da visita (Priority: P3)

**Goal**: Link oficial de código aberto, página de apoio transparente e manutenção do tema anônimo durante a navegação

**Independent Test**: Navegar deslogado entre `/`, `/sobre` e `/apoie`, verificar permanência do tema escolhido e destino do link do GitHub.

- [X] T020 [US5] Atualizar link oficial de código aberto para https://github.com/AntonioBudal/CDL em caderno-leitura-0.1/frontend/src/components/landing/PublicFooter.vue
- [X] T021 [P] [US5] Reescrever estrutura de apoio destacando colaboração técnica e comunitária em caderno-leitura-0.1/frontend/src/views/SupportView.vue
- [X] T022 [US5] Persistir tema da visita em sessionStorage sem reversão no desmonte em caderno-leitura-0.1/frontend/src/composables/useVisitorTheme.ts

**Checkpoint**: Páginas públicas e sessão da visita transparentes e estáveis.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificação completa de compilação, integridade de testes e acessibilidade

- [X] T023 Executar teste de integridade CSS via node tests/feature-075-css-tokens-integrity.test.mjs
- [X] T024 [P] Executar suíte completa de testes de frontend via npm --prefix caderno-leitura-0.1/frontend test
- [X] T025 [P] Executar build de produção via npm --prefix caderno-leitura-0.1/frontend run build
- [X] T026 Executar roteiro de validação manual do quickstart.md nos navegadores desktop e móvel

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — criação do script de teste de integridade CSS.
- **Foundational (Phase 2)**: Depende do Setup — **BLOQUEIA** a execução das histórias seguintes até que a camada de compatibilidade esteja consolidada.
- **User Story 1 (Phase 3)**: Depende de Foundational — entrega o MVP de eliminação de fundos brancos fixos.
- **User Story 2 (Phase 4)**: Depende de Foundational — pode ser executada em sequência ou em paralelo com US1.
- **User Story 3 (Phase 5)**: Depende de Foundational — pode ser executada em sequência ou em paralelo.
- **User Story 4 (Phase 6)**: Depende de Foundational.
- **User Story 5 (Phase 7)**: Depende de Foundational.
- **Polish (Phase 8)**: Depende da conclusão de todas as histórias desejadas.

---

## Parallel Opportunities

- **Phase 3 (US1)**: T005, T006 e T007 podem ser implementadas em paralelo.
- **Phase 4 (US2)**: T009, T010 e T011 podem ser implementadas em paralelo.
- **Phase 5 (US3)**: T014, T015 e T016 atuam em arquivos distintos e podem ser implementadas em paralelo.
- **Phase 6 (US4)**: T018 e T019 podem ser implementadas em paralelo.
- **Phase 7 (US5)**: T021 pode ser implementada em paralelo com T020 e T022.
- **Phase 8 (Polish)**: T024 e T025 podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Phase 1 (T001) e Phase 2 (T002, T003).
2. Completar Phase 3 (T004 a T007).
3. Validar ausência de fundos brancos fixos e integridade de variáveis nos temas escuros.

### Entrega Incremental
1. Setup + Foundational (tokens canônicos consolidados).
2. US1: Cores, superfícies e ausência de fundos brancos.
3. US2: Livros, capas e barra da biblioteca.
4. US3: Estudos do livro (`/livros/:id`), árvores e tabelas.
5. US4: Cabeçalho, rodapé e estados vazios.
6. US5: Páginas públicas, links oficiais e persistência do tema da visita.
7. Polish: Validação de testes, build e aceite visual.
