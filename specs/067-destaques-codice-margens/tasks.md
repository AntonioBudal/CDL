# Tasks: F0.8.02 — Destaques: Códice e Margens Vivas

**Branch**: `067-destaques-codice-margens` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup & Shared Utilities

**Purpose**: Estruturas de dados, utilitários de citação e tokens de estilo compartilhados

- [x] T001 [P] Criar utilitário de formatação de citações `citationFormatter.ts` em `caderno-leitura-0.1/frontend/src/utils/citationFormatter.ts` suportando ABNT e Markdown
- [x] T002 [P] Adicionar tipos e constantes das categorias semânticas de grifo (`HighlightSemanticCategory`, `HIGHLIGHT_SEMANTIC_CATEGORIES`) em `caderno-leitura-0.1/frontend/src/types/index.ts`
- [x] T003 [P] Definir regras de tipografia editorial, classes de citação (`.editorial-quote`, `.reader-note`) e transições aceleradas por GPU em `caderno-leitura-0.1/frontend/src/style.css`

---

## Phase 2: Foundational Components (Componentes Compartilhados)

**Purpose**: Componentes de interface compartilhados e isolados da biblioteca

- [x] T004 [P] Implementar componente de estado de erro temático `ErrorNoticeCard.vue` com suporte a foco acessível e reintento em `caderno-leitura-0.1/frontend/src/components/ui/ErrorNoticeCard.vue`

---

## Phase 3: User Story 1 - Fichas Literárias com Tipografia Editorial Diferenciada (Priority: P1) [MVP]

**Goal**: Transformar a apresentação dos destaques em fichas literárias elegantes com tipografia serifada/humanista e separação visual clara entre citação e anotação pessoal

**Independent Test**: Acessar `/destaques`, inspecionar os cartões de citação verificando a renderização tipográfica destacada do trecho citado com aspas editoriais, contraste claro para a nota pessoal do leitor e rodapé de metadados com livro, capítulo e data.

- [x] T005 [US1] Redesenhar o layout base do cartão em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue` para a estrutura de ficha literária (*commonplace index card*)
- [x] T006 [US1] Aplicar tipografia editorial serifada (`--font-serif`), entrelinha confortável e aspas clássicas no trecho citado da obra em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T007 [US1] Estruturar o bloco subordinado da anotação do leitor com fundo suave translúcido (`--bg-subtle`), ícone `edit-3` e tipografia sans-serif em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T008 [US1] Refinar o rodapé de metadados bibliográficos (obra com link, capítulo, localização e data pt-BR) com tratamento gracioso de valores ausentes em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`

---

## Phase 4: User Story 2 - Barra Unificada de Filtros e Categorias Semânticas de Grifo (Priority: P1) [MVP]

**Goal**: Converter seletores de cores em categorias de estudo cognitivas (Ideia Central, Citação-chave, Dúvida, Refutação, Síntese) com `aria-label` acessível e contagem dinâmica

**Independent Test**: Aplicar filtros por categorias intelectuais de estudo, combinar com busca textual e alternar entre os modos "Recentes" e "Por Obra", conferindo a sincronização dos parâmetros na URL.

- [x] T009 [US2] Substituir seletores de cor circulares rígidos por pílulas de categorias intelectuais de estudo com rótulos e contadores em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`
- [x] T010 [US2] Eliminar todos os valores hexadecimais estáticos (`#eab308`, `#22c55e`, etc.) em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`, consumindo variáveis semânticas dos temas
- [x] T011 [US2] Implementar atributos de acessibilidade (`aria-label`) descritivos informando cor, categoria semântica e contagem em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`
- [x] T012 [US2] Harmonizar o campo de busca textual integrado e a alternância entre os modos "Recentes" e "Por Obra" com persistência em localStorage em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightFilterToolbar.vue`

---

## Phase 5: User Story 3 - Cópia Contextual de Citação em Múltiplos Formatos com Microfeedback (Priority: P2)

**Goal**: Permitir cópia de citações em formatos ABNT e Markdown com feedback visual imediato no botão e notificação flutuante de 1500ms

**Independent Test**: Acionar a cópia de citação em um cartão, conferir transição suave do ícone para confirmação (*check*), verificar toast flutuante exibido por 1,5s e colar o texto validando a formatação bibliográfica.

- [x] T013 [US3] Integrar ação de cópia contextual multiformato (ABNT e Markdown) no cabeçalho do cartão em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue` utilizando `citationFormatter.ts`
- [x] T014 [US3] Conectar microfeedback visual no botão de cópia com transição do ícone vetorial (`copy` -> `check`) em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T015 [US3] Disparar notificação temporária via composable `useFloatingToast.ts` com mensagem "Copiado para a área de transferência" durante exatamente 1500ms em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T016 [US3] Implementar fallback defensivo de seleção textual para navegadores com restrições na Clipboard API em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`

---

## Phase 6: User Story 4 - Expansão Suave de Contexto da Passagem e Edição Ágil (Priority: P2)

**Goal**: Truncar passagens longas com expansão suave ($\le 180$ms), permitir edição ágil da nota in-card e confirmação defensiva de exclusão

**Independent Test**: Expandir e recolher uma citação com mais de 260 caracteres validando a fluidez da animação; editar uma nota in-card e salvá-la; solicitar exclusão e validar cancelamento ou confirmação.

- [x] T017 [US4] Implementar truncamento defensivo em 260 caracteres com botão "Expandir contexto" / "Ver menos" e transição fluida ($\le 180$ms) em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T018 [US4] Refinar o fluxo de edição rápida in-card da anotação pessoal com salvamento assíncrono em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`
- [x] T019 [US4] Implementar caixa de confirmação defensiva integrada para exclusão de destaques prevenindo perda acidental em `caderno-leitura-0.1/frontend/src/components/highlights/HighlightCard.vue`

---

## Phase 7: User Story 5 - Estados de Erro e Vazio Acolhedores e Integrados aos Temas (Priority: P3)

**Goal**: Eliminar o banner vermelho estático da visualização principal, adotando estado de erro e estados vazios temáticos e acolhedores com reintento

**Independent Test**: Simular falha de rede ao consultar a biblioteca de destaques, verificar que o erro respeita a paleta do tema ativo sem faixas vermelhas rígidas e clicar em "Tentar novamente" com foco acessível.

- [x] T020 [US5] Remover o bloco `.notice-error` com cores `#fef2f2`, `#fecaca`, `#991b1b` em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [x] T021 [US5] Renderizar componente temático de estado de erro acolhedor `ErrorNoticeCard.vue` com botão acessível "Tentar novamente" conectado a `fetchHighlights` em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`
- [x] T022 [US5] Redesenhar os estados vazios (com e sem filtros ativos) integrando-os à paleta semântica dos 10 temas em `caderno-leitura-0.1/frontend/src/views/HighlightsLibraryView.vue`

---

## Phase 8: Testes Automatizados, Validação & Polimento

**Purpose**: Verificação completa de requisitos, contratos de UI e não-regressão

- [x] T023 [P] Criar suíte de testes unitários para o formatador de citações em `caderno-leitura-0.1/frontend/tests/citation_formatter.test.mjs`
- [x] T024 [P] Criar suíte de testes unitários e de integração para fichas literárias e filtros semânticos em `caderno-leitura-0.1/frontend/tests/feature-067-destaques-codice-margens.test.mjs`
- [x] T025 Executar validação global de suítes (`npm test`, `npm run build`, `pytest backend/tests`) e cenários do `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as User Stories que consom o componente compartilhado de erro.
- **User Story 1 (Phase 3)**: Depende de Phase 1 — implementa a ficha literária com tipografia editorial (MVP).
- **User Story 2 (Phase 4)**: Depende de Phase 1 — converte filtros em categorias semânticas (MVP).
- **User Story 3 (Phase 5)**: Depende de US1 e Phase 1 (`citationFormatter.ts`) — adiciona cópia multiformato e toast.
- **User Story 4 (Phase 6)**: Depende de US1 — adiciona expansão de contexto e refinamento de edição/exclusão.
- **User Story 5 (Phase 7)**: Depende de Phase 2 (`ErrorNoticeCard.vue`) — substitui o banner vermelho por estado acolhedor.
- **Verification (Phase 8)**: Depende da conclusão das fases anteriores.

### Parallel Opportunities

- `T001`, `T002` e `T003` (Phase 1) podem rodar em paralelo.
- `T004` (Phase 2) pode ser implementado em paralelo com US1.
- `T023` e `T024` (Phase 8) podem ser desenvolvidos em paralelo antes da validação final.

---

## Implementation Strategy

### MVP First (User Stories 1 e 2)

1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (US1: Ficha Literária Editorial) e Phase 4 (US2: Filtros Semânticos de Estudo).
3. **STOP and VALIDATE**: Testar o MVP da biblioteca de destaques de forma independente.
4. Prosseguir para as melhorias incrementais: cópia multiformato (US3), expansão de contexto (US4) e estado de erro temático (US5).
