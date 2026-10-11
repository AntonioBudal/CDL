# Tasks: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Branch**: `071-amigos-salao-literario` | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/071-amigos-salao-literario/spec.md) | **Plan**: [plan.md](file:///c:/Users/User/caderno/specs/071-amigos-salao-literario/plan.md)

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Preparação de tipos e criação da suíte inicial de testes de contrato da Feature F0.8.06.

- [x] T001 [P] Declarar tipos e interfaces de navegação social (SocialActiveTab, BookplateCardProps, BookplateCardEmits, BookplateCardState) em caderno-leitura-0.1/frontend/src/types/friendship.ts
- [x] T002 [P] Criar suíte de testes de contrato e integração da Feature 071 em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs

---

## Phase 2: Foundational (Pré-Requisitos Bloqueantes)

**Purpose**: Infraestrutura de dados de perfil e resumo de amizades compartilhada entre todas as histórias de usuário.

- [x] T003 Aprimorar composables useFriends e useProfile em caderno-leitura-0.1/frontend/src/composables/useFriends.ts e caderno-leitura-0.1/frontend/src/composables/useProfile.ts para suportar atualização reativa de contadores de conexões e resolução de perfil público/privado

**Checkpoint**: Base de tipos e composables pronta — a implementação das histórias de usuário pode iniciar de forma independente.

---

## Phase 3: User Story 1 - Cartão de Identidade do Leitor (*Bookplate Card*) e Compartilhamento Ágil (Priority: P1) 🎯 MVP

**Goal**: Exibir permanentemente no topo de `/amigos` o componente `BookplateCard.vue` com avatar, nome de exibição, bio literária, `@identificador`, selo de confirmação esmaecendo em 1200ms e compartilhamento via Web Share API (`navigator.share`) com fallback para cópia rápida do link.

**Independent Test**: Acessar `/amigos`, inspecionar o Bookplate Card no topo, clicar em "Copiar" e verificar a ativação do selo esmaecendo em exatamente 1200ms com o `@identificador` copiado para a área de transferência.

### Tests for User Story 1

- [x] T004 [P] [US1] Adicionar testes de contrato para o BookplateCard (renderização permanente no topo, selo de confirmação de 1200ms, Web Share API e fallback de cópia) em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs

### Implementation for User Story 1

- [x] T005 [P] [US1] Criar componente BookplateCard.vue com avatar/iniciais, bio literária, @identificador, microinteração do selo de 1200ms (.is-stamped) e suporte à Web Share API em caderno-leitura-0.1/frontend/src/components/BookplateCard.vue
- [x] T006 [US1] Integrar BookplateCard.vue permanentemente no topo de FriendsView.vue conectando aos dados reativos de perfil e contadores em caderno-leitura-0.1/frontend/src/views/FriendsView.vue

**Checkpoint**: User Story 1 funcional de forma independente. O Ex-Líbris digital e o compartilhamento de identidade estão operacionais (MVP entregue).

---

## Phase 4: User Story 2 - Salão Literário: Cartões de Conexão e Ações Contextuais (Priority: P1) 🎯 MVP

**Goal**: Redesenhar a exibição de amigos e solicitações em cartões de conexão literária com tipografia editorial, data formatada em português, link direto para a estante pública (`/u/:username`) e ações contextuais bem distribuídas (`FriendActionButtons.vue`).

**Independent Test**: Acessar as abas "Círculo de Leitura" e "Solicitações", verificando a renderização dos cartões com data amigável, botões acessíveis e confirmações defensivas para remoção e bloqueio.

### Tests for User Story 2

- [x] T007 [P] [US2] Adicionar testes de contrato para os cartões de conexão literária (data amigável, links para /u/:username e diálogos defensivos) em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs

### Implementation for User Story 2

- [x] T008 [P] [US2] Atualizar FriendActionButtons.vue aplicando tokens semânticos, alvos táteis mínimos de 44px e diálogos defensivos acessíveis em caderno-leitura-0.1/frontend/src/components/FriendActionButtons.vue
- [x] T009 [US2] Redesenhar os cartões de amigos e solicitações com tipografia editorial, link para estante pública (/u/:username) e data amigável em caderno-leitura-0.1/frontend/src/views/FriendsView.vue

**Checkpoint**: User Stories 1 e 2 operando integradas no Salão Literário com elegância editorial e ações seguras.

---

## Phase 5: User Story 3 - Descoberta de Pares e Estados Vazios Enriquecidos (Priority: P2)

**Goal**: Substituir caixas vazias impessoais pelo estado acolhedor "Círculo em Formação" e prover campo de busca com debounce de 300ms com sugestões intelectuais na aba "Descobrir Leitores".

**Independent Test**: Visualizar o estado vazio acolhedor ao não possuir amigos cadastrados; na aba de descoberta, realizar pesquisa com debounce e constatar sugestões temáticas quando a busca estiver limpa.

### Tests for User Story 3

- [x] T010 [P] [US3] Adicionar testes para o estado vazio acolhedor Círculo em Formação e busca debounced de 300ms com sugestões intelectuais em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs

### Implementation for User Story 3

- [x] T011 [US3] Implementar estado vazio editorial acolhedor Círculo em Formação na ausência de amigos e solicitações em caderno-leitura-0.1/frontend/src/views/FriendsView.vue
- [x] T012 [US3] Implementar na aba Descobrir Leitores campo de busca debounced de 300ms e sugestões acolhedoras de temas literários e exploração intelectual quando a busca estiver vazia em caderno-leitura-0.1/frontend/src/views/FriendsView.vue

**Checkpoint**: Experiência acolhedora e inspiradora garantida tanto para novos leitores quanto para a exploração da rede.

---

## Phase 6: User Story 4 - Navegação por Abas com Contadores e Imunidade Cromática (Priority: P2)

**Goal**: Garantir navegação segmentada em 4 abas (`Círculo de Leitura`, `Solicitações`, `Descobrir Leitores`, `Bloqueados`) com contadores dinâmicos, acessibilidade WAI-ARIA (`role="tablist"` / `role="tab"`), alvos de toque $\ge 44 \times 44$px e imunidade aos 10 temas visuais.

**Independent Test**: Percorrer as abas via teclado e leitor de tela validando atributos `role="tab"` e `aria-selected`, e inspecionar a interface nos 10 temas sem degradação visual.

### Tests for User Story 4

- [x] T013 [P] [US4] Adicionar testes de acessibilidade WAI-ARIA para abas (role="tablist", role="tab", aria-selected, aria-controls) e conformidade aos 10 temas em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs

### Implementation for User Story 4

- [x] T014 [US4] Implementar navegação de abas com as 4 categorias oficiais, badges dinâmicos de contagem e atributos WAI-ARIA em caderno-leitura-0.1/frontend/src/views/FriendsView.vue

**Checkpoint**: Todas as 4 histórias de usuário estão integradas, acessíveis e operacionais.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificações finais de imunidade cromática, ergonomia móvel e validação integrada ponta a ponta.

- [x] T015 [P] Garantir imunidade cromática total aos 10 temas visuais (100% variáveis CSS semânticas, zero hexadecimais fixos e zero emojis) em caderno-leitura-0.1/frontend/src/components/BookplateCard.vue e caderno-leitura-0.1/frontend/src/views/FriendsView.vue
- [x] T016 [P] Validar alvos táteis móveis (min-height e min-width >= 44px) e anéis de foco visíveis em todos os botões e abas em caderno-leitura-0.1/frontend/src/views/FriendsView.vue e caderno-leitura-0.1/frontend/src/components/BookplateCard.vue
- [x] T017 Executar suíte completa de validação automatizada (npm test, npm run build, pytest) validando cenários de quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup (Phase 1) — BLOQUEIA as histórias de usuário.
- **User Stories (Phase 3 a Phase 6)**:
  - US1 (Phase 3 - P1): Depende da Phase 2. Não depende de outras histórias.
  - US2 (Phase 4 - P1): Depende da Phase 2 e atua sobre `FriendsView.vue` e `FriendActionButtons.vue`.
  - US3 (Phase 5 - P2): Depende de US1 e US2 para os estados de lista e busca.
  - US4 (Phase 6 - P2): Depende da Phase 2 e orquestra a navegação global por abas em `FriendsView.vue`.
- **Polish (Phase 7)**: Depende da conclusão de todas as histórias de usuário desejadas.

### User Story Dependencies

- **User Story 1 (P1)**: Pode iniciar imediatamente após Phase 2 — independente.
- **User Story 2 (P1)**: Pode iniciar após Phase 2 — independente.
- **User Story 3 (P2)**: Constrói sobre a estrutura de cartões e listas de US2.
- **User Story 4 (P2)**: Consolida a navegação e acessibilidade das 4 abas integrando US1, US2 e US3.

### Parallel Opportunities

- `T001` e `T002` em Setup podem ser executados em paralelo.
- `T004` e `T005` em User Story 1 podem ser desenvolvidos em paralelo.
- `T007` e `T008` em User Story 2 podem ser executados em paralelo.
- Tarefas de polimento `T015` e `T016` podem ser executadas em paralelo.

---

## Parallel Example: User Story 1

```bash
# Executar em paralelo testes de contrato e componente:
Task: "T004 [P] [US1] Adicionar testes de contrato para o BookplateCard em caderno-leitura-0.1/frontend/tests/feature-071-amigos-salao-literario.test.mjs"
Task: "T005 [P] [US1] Criar componente BookplateCard.vue em caderno-leitura-0.1/frontend/src/components/BookplateCard.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 & User Story 2)

1. Concluir Phase 1: Setup (tipos e suíte de testes de contrato).
2. Concluir Phase 2: Foundational (composables e estado reativo).
3. Concluir Phase 3: User Story 1 (Bookplate Card, selo de 1200ms e Web Share).
4. Concluir Phase 4: User Story 2 (Cartões de conexão e ações contextuais).
5. **PARAR e VALIDAR**: Testar User Stories 1 e 2 independentemente (MVP funcional).

### Incremental Delivery

1. Setup + Foundational $\rightarrow$ Fundação pronta.
2. US1 $\rightarrow$ Ex-Líbris digital e identificador visível e compartilhável (MVP 1).
3. US2 $\rightarrow$ Cartões editoriais de amigos e solicitações (MVP 2).
4. US3 $\rightarrow$ Estados vazios enriquecidos e busca com sugestões temáticas.
5. US4 $\rightarrow$ Navegação por 4 abas com contadores e acessibilidade WAI-ARIA.
6. Polish $\rightarrow$ Imunidade cromática aos 10 temas, alvos táteis e validação global.
