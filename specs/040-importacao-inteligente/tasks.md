# Tasks: F0.6.1 — Importação Inteligente

**Feature**: `040-importacao-inteligente`  
**Date**: 2026-09-27  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificação e alinhamento da estrutura da feature

- [X] T001 Verificar contratos e documentação da feature em `specs/040-importacao-inteligente/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extensões de modelos e tipos compartilhados necessários para as histórias de usuário

- [X] T002 [P] Expandir dicionário de sinônimos e normalização léxica em `caderno-leitura-0.1/backend/app/services/import_parser.py`
- [X] T003 [P] Atualizar schemas Pydantic de prévia e avisos em `caderno-leitura-0.1/backend/app/schemas/imports.py`
- [X] T004 [P] Atualizar definições de tipos TypeScript de importação em `caderno-leitura-0.1/frontend/src/types.ts`

**Checkpoint**: Base compartilhada pronta — implementação das histórias de usuário pode prosseguir

---

## Phase 3: User Story 2 - Reconhecimento Tolerante a Variações Lexicais e Formatações (Priority: P1)

**Goal**: Permitir que o parser do backend reconheça variações de títulos (visão geral, síntese, aprofundamento, termos-chave, fontes), diferentes marcações Markdown (`#`, `##`, `###`, `**negrito**`), numerações ordinais e mantenha o isolamento rigoroso de cercas de código (` ``` `).

**Independent Test**: Submeter textos com sinônimos e formatações flexíveis em `tests/unit/test_import_parser.py` e verificar a correta divisão nas 4 seções com 100% de sucesso.

### Tests for User Story 2
- [X] T005 [P] [US2] Criar suíte de testes unitários cobrindo sinônimos, formatações Markdown, numerações ordinais e code fences em `caderno-leitura-0.1/backend/tests/unit/test_import_parser.py`

### Implementation for User Story 2
- [X] T006 [US2] Implementar regex tolerante a níveis de títulos Markdown (`#` a `####`), negrito e prefixos numéricos em `caderno-leitura-0.1/backend/app/services/import_parser.py`
- [X] T007 [US2] Integrar mapeamento semântico de sinônimos normalizados em `caderno-leitura-0.1/backend/app/services/import_parser.py`
- [X] T008 [US2] Garantir que linhas de código delimitadas por cercas (` ``` ` e `~~~`) nunca sejam interpretadas como divisores de seção em `caderno-leitura-0.1/backend/app/services/import_parser.py`

**Checkpoint**: O parser de importação identifica com precisão sinônimos e formatações variadas de forma determinística e testada.

---

## Phase 4: User Story 1 - Importação em Fluxo Contínuo e Direto (Priority: P1) 🎯 MVP

**Goal**: Permitir ao leitor colar o texto em um único campo, obter a prévia estruturada instantaneamente (sem rolagem obrigatória nem cliques intermediários) e salvar o estudo de imediato no padrão `Colar → Leitorum entende → Usuário confere → Salvar`.

**Independent Test**: Acessar `ImportView.vue`, colar um texto de estudo, constatar a geração imediata da prévia em cards legíveis e concluir o salvamento com persistência íntegra de `source_response`.

### Tests for User Story 1
- [X] T009 [P] [US1] Adicionar testes unitários para disparo no evento de colagem e fluxo de prévia em `caderno-leitura-0.1/frontend/tests/import-draft.test.mjs`

### Implementation for User Story 1
- [X] T010 [US1] Implementar no composable o auto-disparo de prévia na colagem (`onPaste`) e o controle de estado `stale` em `caderno-leitura-0.1/frontend/src/composables/useImportDraft.ts`
- [X] T011 [US1] Configurar na view o campo de texto unificado com manipulador de evento `@paste` e botão visível "Atualizar prévia" em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [X] T012 [US1] Criar visualização estruturada em cards legíveis para as seções da prévia em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [X] T013 [US1] Posicionar barra de ações com botão "Salvar Estudo" diretamente acessível após a prévia em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

**Checkpoint**: MVP do novo fluxo de importação completo e funcional de ponta a ponta.

---

## Phase 5: User Story 3 - Tratamento e Atribuição de Conteúdo Não Classificado (Priority: P2)

**Goal**: Sinalizar trechos não reconhecidos com avisos claros, permitir atribuição rápida para qualquer seção com 1 clique e anexar automaticamente conteúdo residual à Explicação ao salvar sem reatribuição (garantia de zero perda de dados).

**Independent Test**: Colar texto com introdução genérica do chatbot, verificar a exibição da caixa de "Conteúdo Não Classificado", testar botão de atribuição rápida e certificar que o conteúdo residual é incorporado sem perda.

### Tests for User Story 3
- [X] T014 [P] [US3] Adicionar testes unitários para a ação de mover texto não atribuído e política de fallback ao salvar em `caderno-leitura-0.1/frontend/tests/import-draft.test.mjs`

### Implementation for User Story 3
- [X] T015 [US3] Implementar função `assignUnassignedToSection(sectionKey)` e regra de salvamento com anexação residual na seção de Explicação em `caderno-leitura-0.1/frontend/src/composables/useImportDraft.ts`
- [X] T016 [US3] Construir interface de alerta visual de conteúdo não classificado com botões rápidos de 1 clique ("Mover para Resumo", "Mover para Explicação", etc.) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`

**Checkpoint**: Zero risco de perda de texto em textos atípicos ou conversacionais de IA.

---

## Phase 6: User Story 4 - Conferência e Edição Rápida Pré-Salvamento (Priority: P3)

**Goal**: Disponibilizar painel colapsável ("Ajuste manual detalhado") para os 4 campos manuais legados, recolhido por padrão, preservando a interface limpa e dando controle refinado para usuários avançados.

**Independent Test**: Abrir o painel colapsável na tela de importação, editar o conteúdo de um dos campos manuais e constatar que a alteração é salva no estudo sem afetar o texto original de `source_response`.

### Implementation for User Story 4
- [X] T017 [P] [US4] Envolver o componente de campos manuais em um bloco colapsável `<details class="manual-adjustment-panel">` recolhido por padrão em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [X] T018 [US4] Garantir que alterações nos campos manuais permaneçam sincronizadas bidirecionalmente com o estado de salvamento em `caderno-leitura-0.1/frontend/src/composables/useImportDraft.ts`

**Checkpoint**: Ajustes manuais finos disponíveis sob demanda sem sobrecarregar a experiência padrão.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Acessibilidade, robustez, validação de tipos e verificação dos critérios de aceite

- [X] T019 [P] Aprimorar acessibilidade visual e suporte a leitores de tela (ARIA labels, contraste e anúncio de status) em `caderno-leitura-0.1/frontend/src/views/ImportView.vue`
- [X] T020 Executar suíte completa de testes de regressão do backend via `pytest` em `caderno-leitura-0.1/backend`
- [X] T021 Executar suíte de testes e verificação de tipagem TypeScript via `npm test` e `npm run build` em `caderno-leitura-0.1/frontend`
- [X] T022 Validar os cenários manuais de ponta a ponta descritos em `specs/040-importacao-inteligente/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências, inicia de imediato.
- **Foundational (Phase 2)**: Depende do Setup; bloqueia as histórias de usuário.
- **User Story 2 (Phase 3)**: Motor de backend para suporte a sinônimos e marcações. Pode iniciar após Foundational.
- **User Story 1 (Phase 4)**: Interface e fluxo principal MVP (`Colar → Entender → Salvar`). Depende da Phase 2 e se beneficia dos testes da Phase 3.
- **User Story 3 (Phase 5)**: Tratamento de texto não classificado e ações de 1 clique. Depende da Phase 4.
- **User Story 4 (Phase 6)**: Accordion colapsável para campos manuais detalhados. Depende da Phase 4.
- **Polish (Phase 7)**: Depende da conclusão de todas as histórias desejadas.

### Parallel Opportunities

- `T002`, `T003` e `T004` podem ser desenvolvidos em paralelo (backend e frontend isolados).
- `T005` (testes do parser) pode ser escrito paralelamente a `T009` (testes do composable).
- `T014` e `T017` operam em arquivos distintos e podem ser implementados concorrentemente.

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (Parser de sinônimos no Backend).
3. Concluir Phase 4 (Fluxo de colagem e prévia no Frontend).
4. **Validar MVP**: Colar texto com sinônimos → Conferir prévia → Salvar.

### Entrega Incremental
1. Adicionar Phase 5 (Tratamento de não classificado + botões de 1 clique).
2. Adicionar Phase 6 (Painel colapsável para campos manuais).
3. Concluir Phase 7 (Acessibilidade, testes completos e build de produção).
