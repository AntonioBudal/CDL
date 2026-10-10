# Tasks: F0.8.05 — Ateliê de Fichamento e Parser Estruturado

**Branch**: `066-importar-atelie-parser` | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/066-importar-atelie-parser/spec.md) | **Plan**: [plan.md](file:///c:/Users/User/caderno/specs/066-importar-atelie-parser/plan.md)

## Phase 1: Setup & Shared Utilities

**Purpose**: Fundações utilitárias e estilos base para o ateliê de fichamento

- [x] T001 Adicionar ação de formatação de tabela (`table`) em `caderno-leitura-0.1/frontend/src/utils/markdownFormatter.ts`
- [x] T002 Definir regras de layout Two-Pane Studio, grid responsivo e animação de pulso luminoso (`section-pulse`) em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational Components (Componentes Reutilizáveis)

**Purpose**: Componentes de interface compartilhados e isolados do ateliê

- [x] T003 Criar componente de alternância de modos de visualização `StudioViewModeToggle.vue` em `caderno-leitura-0.1/frontend/src/components/studies/StudioViewModeToggle.vue`
- [x] T004 Criar componente de barra flutuante contextual `FloatingMarkdownToolbar.vue` em `caderno-leitura-0.1/frontend/src/components/studies/FloatingMarkdownToolbar.vue`

---

## Phase 3: User Story 1 - Ateliê Two-Pane Studio e Faixa Superior Compacta (Priority: P1) [MVP]

**Goal**: Transformar a tela `/importar` em duas colunas sincronizadas com faixa superior compacta de metadados

- [x] T005 [US1] Refatorar cabeçalho de metadados em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` para faixa horizontal compacta (Livro, Capítulo, Localização, Título e botão de ação)
- [x] T006 [US1] Implementar contêiner mestre com dois painéis lado a lado (Editor à esquerda, Prévia estruturada à direita) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T007 [US1] Adicionar contadores de palavras e caracteres e botão manual de análise no rodapé do editor em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T008 [US1] Renderizar os 4 cartões de seções estruturadas (Resumo, Explicação, Conceitos, Referências) e o bloco de Conteúdo Não Classificado com botões de 1 clique em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T009 [US1] Preservar tela de salvamento concluído (`saved-panel`) com rotas de leitura e novo estudo em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

---

## Phase 4: User Story 2 - Barra de Ferramentas Flutuante e Modos de Foco (Priority: P1) [MVP]

**Goal**: Permitir formatação flutuante sobre texto selecionado e alternância fluida entre modos 50/50, 100% Fonte e 100% Prévia

- [x] T010 [US2] Conectar `FloatingMarkdownToolbar.vue` ao textarea da fonte em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`, ativando na seleção e ocultando no clique fora / Esc
- [x] T011 [US2] Integrar `StudioViewModeToggle.vue` no topo do ateliê em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` e aplicar classes dinâmicas de largura (`studio-split`, `studio-source-only`, `studio-preview-only`)
- [x] T012 [US2] Adicionar fallback acessível com atalhos de formatação no rodapé do editor para operação independente de seleção com mouse em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

---

## Phase 5: User Story 3 - Pulso de Detecção Estrutural, Tratamento Térmico e Debounce (Priority: P2)

**Goal**: Garantir experiência tátil com pulso luminoso de detecção e digitação a 60 FPS com textos extensos

- [x] T013 [US3] Disparar efeito visual de pulso luminoso nos cartões de seção do painel de prévia ao detectar seções estruturadas em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T014 [US3] Implementar debounce de 300ms na digitação para cálculo e atualização da prévia sem causar jank em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T015 [US3] Adicionar regras de `prefers-reduced-motion: reduce` suprimindo o pulso luminoso e as transições de expansão em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 6: User Story 4 - Promoção do Inbox, Responsividade e Acessibilidade (Priority: P3)

**Goal**: Preservar integração de promoção de capturas, fornecer abas segmentadas para viewports < 1024px e manter acessibilidade total

- [x] T016 [US4] Preservar carregamento e banner de promoção de capturas do Inbox (`promote_inbox_id`) com vínculo no salvamento em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T017 [US4] Implementar abas segmentadas responsivas para viewports menores que 1024px (`Texto da Fonte` vs `Prévia Estruturada`) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T018 [US4] Garantir anéis de foco (`:focus-visible`), touch targets >= 44px e ausência absoluta de emojis em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` e novos componentes

---

## Phase 7: Testes Automatizados e Validação

**Purpose**: Verificação completa de requisitos, contratos de UI e não-regressão

- [x] T019 Criar suíte de testes unitários `caderno-leitura-0.1/frontend/tests/feature-066-importar-atelie-parser.test.mjs`
- [x] T020 Executar `npm test`, `npm run build` e validações de integridade
