# Tasks: F0.3.5 — Tela Placeholder do Document Intelligence (Digitalizar Caderno)

**Branch**: `069-document-intelligence-placeholder` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup & Shared Types

**Purpose**: Estruturas de dados em TypeScript e constantes canônicas de apresentação da funcionalidade

- [x] T001 [P] Criar tipagens e constantes de apresentação `DOCUMENT_INTELLIGENCE_STAGES` e `DIGITIZE_EXIT_SHORTCUTS` em `caderno-leitura-0.1/frontend/src/types/digitize.ts`
- [x] T002 [P] Reexportar os novos tipos de digitalização em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational Routing (Roteamento de Base)

**Purpose**: Registro da rota dedicada no frontend para possibilitar navegação

- [x] T003 Registrar a rota `/digitalizar` com alias `/scan` e metadados de autenticação em `caderno-leitura-0.1/frontend/src/router/index.ts`

---

## Phase 3: User Story 1 - Acesso à Proposta e Compromisso de Privacidade Local (Priority: P1) [MVP]

**Goal**: Apresentar cabeçalho editorial, explicação da conversão de cadernos manuscritos em estudos e garantia estrita de privacidade 100% local

**Independent Test**: Navegar para `/digitalizar` e conferir título, subtítulo e manifesto de privacidade destacando que nenhuma imagem sai do computador

- [x] T004 [US1] Criar o componente de visualização base `DigitizeNotebookView.vue` com cabeçalho editorial e manifesto de privacidade local soberana em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`
- [x] T005 [US1] Adicionar texto explicativo em linguagem de leitor sobre a proposta de estudos estruturados e aviso explícito de status "em pesquisa" sem prazos em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`

---

## Phase 4: User Story 2 - Consulta ao Indicador de Maturidade por Etapas (Priority: P1) [MVP]

**Goal**: Exibir matriz honesta de maturidade com as 4 etapas técnicas estáticas e ilustração conceitual rotulada

**Independent Test**: Inspecionar a seção de maturidade em `/digitalizar`, confirmando os 4 marcos textuais e a rotulagem da ilustração conceitual

- [x] T006 [US2] Implementar a Matriz Didática de Maturidade com os 4 marcos canônicos e notas técnicas transparentes em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`
- [x] T007 [US2] Adicionar bloco visual vetorial rotulado como "Ilustração Conceitual" exemplificando blocos delimitadores com dados fictícios em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`

---

## Phase 5: User Story 3 - Caminhos de Saída Úteis para Fluxos em Operação (Priority: P2)

**Goal**: Oferecer atalhos de saída imediatos para `/importar` e `/inbox` e integrar card de convite no Hub de Importação

**Independent Test**: Clicar nos atalhos de saída em `/digitalizar` verificando redirecionamento para `/importar` e `/inbox`, e acessar `/importar` confirmando o card editorial de convite

- [x] T008 [US3] Implementar seção de caminhos de ação imediata com atalhos de navegação fluida para `/importar` e `/inbox` em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`
- [x] T009 [US3] Integrar card editorial "Caderno Manuscrito (Em Pesquisa)" no Ateliê de Importação com link para `/digitalizar` em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

---

## Phase 6: User Story 4 - Respeito aos Temas Visuais, Acessibilidade & Resiliência Offline (Priority: P3)

**Goal**: Garantir imunidade cromática nos 10 temas, acessibilidade WAI-ARIA, touch targets $\ge 44$px e resiliência offline total

**Independent Test**: Alternar temas visuais, testar navegação por teclado, redimensionar para tela móvel e verificar ausência de requisições de rede

- [x] T010 [US4] Estilizar `DigitizeNotebookView.vue` consumindo exclusivamente variáveis CSS semânticas dos 10 temas visuais e touch targets $\ge 44 \times 44$px em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`
- [x] T011 [US4] Assegurar semântica WAI-ARIA, hierarquia de títulos, foco visual acessível, ausência absoluta de emojis e banimento de `<input type="file">` ou APIs de mídia em `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`

---

## Phase 7: Testes Automatizados, Validação & Polimento

**Purpose**: Verificação completa de requisitos, contratos de UI e garantia de não-regressão

- [x] T012 [P] Criar suíte de testes unitários para rota, metadados, 4 etapas de maturidade, texto de privacidade, atalhos e acessibilidade em `caderno-leitura-0.1/frontend/tests/feature-069-document-intelligence-placeholder.test.mjs`
- [x] T013 Executar validação global de suítes (`npm test`, `npm run build`) e cenários do `quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Foundational (Phases 1 & 2)**: Sem dependências externas — iniciam imediatamente.
- **User Story 1 (Phase 3 - P1 [MVP])**: Depende das Fases 1 e 2.
- **User Story 2 (Phase 4 - P1 [MVP])**: Depende da view criada na US1.
- **User Story 3 (Phase 5 - P2)**: Depende da view criada na US1 e conecta com `ImportView.vue`.
- **User Story 4 (Phase 6 - P3)**: Refinamento de temas e acessibilidade sobre US1, US2 e US3.
- **Testes & Validação (Phase 7)**: Executada para assegurar não-regressão e conformidade.

### Parallel Opportunities

- T001 e T002 podem ser preparados em paralelo.
- T012 (testes) pode ser preparado em paralelo com T010 e T011.

---

## Implementation Strategy

### MVP Scope (Phases 1, 2, 3 e 4)
1. Concluir Setup e Roteamento (T001 a T003).
2. Entregar a Proposta Editorial e Manifesto de Privacidade Local (T004 e T005).
3. Entregar a Matriz de Maturidade das 4 Etapas e Ilustração Conceitual (T006 e T007).
4. **Validação do MVP**: Acessar `/digitalizar` e verificar a comunicação honesta e estática.

### Incremental Delivery
- **Incremento 1**: Tipos, Rota e View Base com Manifesto Local (US1).
- **Incremento 2**: Matriz de Maturidade de 4 Etapas e Ilustração (US2).
- **Incremento 3**: Caminhos de Saída e Card no Hub de Importação (US3).
- **Incremento 4**: Polimento de Temas, Ergonomia Mobile e Acessibilidade (US4).
- **Validação Global**: Suíte automatizada com `npm test` e `npm run build`.
