# Tasks: F0.8.05 — Ateliê de Fichamento e Parser Estruturado

**Branch**: `066-importar-atelie-parser` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup & Shared Utilities

**Purpose**: Fundações utilitárias e estilos base para o ateliê de fichamento

- [x] T001 [P] Adicionar ação de formatação de tabela (`table`) em `caderno-leitura-0.1/frontend/src/utils/markdownFormatter.ts`
- [x] T002 [P] Definir regras de layout Two-Pane Studio, grid responsivo e keyframes de pulso luminoso (`section-pulse`) em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational Components (Componentes Reutilizáveis)

**Purpose**: Componentes de interface compartilhados e isolados do ateliê

- [x] T003 [P] Implementar componente de alternância de modos de visualização `StudioViewModeToggle.vue` em `caderno-leitura-0.1/frontend/src/components/studies/StudioViewModeToggle.vue`
- [x] T004 [P] Implementar componente de barra flutuante contextual `FloatingMarkdownToolbar.vue` em `caderno-leitura-0.1/frontend/src/components/studies/FloatingMarkdownToolbar.vue`

---

## Phase 3: User Story 1 - Ateliê Two-Pane Studio e Faixa Superior Compacta (Priority: P1) [MVP]

**Goal**: Transformar a tela `/importar` em duas colunas sincronizadas com faixa superior compacta de metadados

**Independent Test**: Acessar `/importar`, selecionar livro e capítulo na barra superior compacta, colar texto no editor esquerdo, verificar a prévia estruturada imediata das 4 seções no painel direito e salvar o estudo com sucesso.

- [x] T005 [US1] Refatorar cabeçalho de metadados em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` para faixa horizontal compacta (Livro, Capítulo, Localização, Título e botão de ação)
- [x] T006 [US1] Implementar contêiner mestre com dois painéis lado a lado (Editor à esquerda, Prévia estruturada à direita) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T007 [US1] Adicionar contadores de palavras e caracteres e botão manual de análise no rodapé do editor em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T008 [US1] Renderizar os 4 cartões de seções estruturadas (Resumo, Explicação, Conceitos, Referências) e o bloco de Conteúdo Não Classificado com botões de 1 clique em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T009 [US1] Preservar tela de salvamento concluído (`saved-panel`) com rotas de leitura e novo estudo em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

---

## Phase 4: User Story 2 - Barra de Ferramentas Flutuante e Modos de Foco (Priority: P1) [MVP]

**Goal**: Permitir formatação flutuante sobre texto selecionado e alternância fluida entre modos 50/50, 100% Fonte e 100% Prévia

**Independent Test**: Selecionar um trecho no editor da fonte, verificar a exibição da barra flutuante, aplicar negrito/link, alternar para o modo 'Apenas Fonte' e 'Apenas Prévia' e constatar a animação em $\le 180$ms e a persistência do conteúdo.

- [x] T010 [US2] Conectar `FloatingMarkdownToolbar.vue` ao textarea da fonte em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`, ativando na seleção e ocultando no clique fora ou `Esc`
- [x] T011 [US2] Integrar `StudioViewModeToggle.vue` no topo do ateliê em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` e aplicar classes dinâmicas de largura (`studio-split`, `studio-source-only`, `studio-preview-only`)
- [x] T012 [US2] Adicionar fallback acessível com atalhos de formatação no rodapé do editor para operação independente de seleção com mouse em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

---

## Phase 5: User Story 3 - Pulso de Detecção Estrutural, Tratamento Térmico e Debounce (Priority: P2)

**Goal**: Garantir experiência tátil com pulso luminoso de detecção e digitação a 60 FPS com textos extensos

**Independent Test**: Colar um texto de 2.500 palavras com títulos variados, verificar a ausência de quedas de frames ou travamento de digitação, e conferir o pulso sutil nos cartões do preview quando a análise é concluída.

- [x] T013 [US3] Disparar efeito visual de pulso luminoso nos cartões de seção do painel de prévia ao detectar seções estruturadas em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T014 [US3] Implementar debounce de 300ms na digitação para cálculo e atualização da prévia sem causar jank em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T015 [US3] Adicionar regras de `prefers-reduced-motion: reduce` suprimindo o pulso luminoso e as transições cinéticas em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 6: User Story 4 - Promoção do Inbox, Responsividade e Acessibilidade (Priority: P3)

**Goal**: Preservar integração de promoção de capturas, fornecer abas segmentadas para viewports < 1024px e manter acessibilidade total

**Independent Test**: Abrir `/importar?promote_inbox_id=...`, verificar banner de promoção, redimensionar a janela para 800px e 375px conferindo as abas responsivas, navegar exclusivamente com teclado e salvar.

- [x] T016 [US4] Preservar carregamento e banner de promoção de capturas do Inbox (`promote_inbox_id`) com vínculo no salvamento em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T017 [US4] Implementar abas segmentadas responsivas para viewports menores que 1024px (`Texto da Fonte` vs `Prévia Estruturada`) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [x] T018 [US4] Garantir anéis de foco (`:focus-visible`), touch targets $\ge 44 \times 44$px e ausência absoluta de emojis em `caderno-leitura-0.1/frontend/src/views/ImportView.vue` e novos componentes

---

## Phase 7: Testes Automatizados, Validação & Polimento

**Purpose**: Verificação completa de requisitos, contratos de UI e não-regressão

- [x] T019 [P] Criar suíte de testes unitários `caderno-leitura-0.1/frontend/tests/feature-066-importar-atelie-parser.test.mjs` validando layout Two-Pane, toolbar flutuante, modos de foco, debounce e acessibilidade
- [x] T020 Executar suite completa de validações (`npm test`, `npm run build` e `python -m pytest`) e cenários do `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as User Stories que consom os novos componentes.
- **User Story 1 (Phase 3)**: Depende de Phase 1 e Phase 2 — implementa a arquitetura Two-Pane Studio e faixa compacta (MVP).
- **User Story 2 (Phase 4)**: Depende de US1 — adiciona barra flutuante e alternância de modos de foco.
- **User Story 3 (Phase 5)**: Depende de US1 — adiciona pulso luminoso de detecção e debounce para fontes densas.
- **User Story 4 (Phase 6)**: Depende de US1 — garante adaptação responsiva (< 1024px) e fluxo do Inbox.
- **Verification (Phase 7)**: Depende da conclusão das fases anteriores.

### Parallel Opportunities

- `T001` e `T002` (Phase 1) podem rodar em paralelo.
- `T003` e `T004` (Phase 2) podem rodar em paralelo.
- `T019` (Phase 7) pode ser preparado em paralelo com as fases finais.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Concluir Setup (T001, T002) e Componentes (T003, T004).
2. Implementar User Story 1 (T005..T009) — Two-Pane Studio funcional com faixa superior compacta.
3. Implementar User Story 2 (T010..T012) — Barra flutuante e modos de foco.
4. Validar MVP independentemente na rota `/importar`.
5. Acrescentar refinamentos táteis de US3 (T013..T015) e responsividade de US4 (T016..T018).
6. Rodar suíte de testes e fechar ciclo com commit atômico individual.
