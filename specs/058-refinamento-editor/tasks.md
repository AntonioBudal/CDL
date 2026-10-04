# Tasks: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Feature Branch**: `058-refinamento-editor`  
**Date**: 2026-10-04  
**Spec**: [specs/058-refinamento-editor/spec.md](spec.md) | **Plan**: [specs/058-refinamento-editor/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de tipos TypeScript e contratos compartilhados para suporte a rascunhos de sessão e navegação por abas.

- [X] T001 Definir tipos de dados para rascunhos em sessão (`StudyEditorDraftPayload`, `StudyEditorDraft`), chaves de abas (`EditorSectionTabKey`), modo de visualização (`EditorViewMode`) e abas (`EditorSectionTab`) em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura básica de persistência volátil em `sessionStorage` e recuperação de rascunhos necessária para todas as histórias.

**⚠️ CRITICAL**: Nenhuma história de usuário deve avançar sem a base de gerenciamento de rascunho de sessão validada.

- [X] T002 Criar testes unitários para o composable de rascunhos em sessão (`useStudyDraft`) validando salvamento com debounce, isolamento por `studyId`, auto-restauração e descarte em `caderno-leitura-0.1/frontend/tests/study-draft.test.mjs`
- [X] T003 Implementar composable `useStudyDraft` para persistência em `sessionStorage` (`caderno_draft_study_<id>`), restauração automática e métodos de descarte/limpeza em `caderno-leitura-0.1/frontend/src/composables/useStudyDraft.ts`

**Checkpoint**: Base de persistência de sessão operacional. As histórias de usuário podem ser executadas.

---

## Phase 3: User Story 1 - Navegação Responsiva de Seções e Modo Focado de Escrita (Priority: P1) 🎯 MVP

**Goal**: Permitir que o leitor navegue rapidamente entre as seções analíticas (`Resumo`, `Explicação`, `Conceitos`, `Referências` e `Notas`) através de pílulas horizontais com indicador de preenchimento e alternância para o modo contínuo ("Ver todas as seções"), reduzindo em > 60% a rolagem vertical no mobile.

**Independent Test**: Abrir o formulário de edição de estudos; alternar entre abas individuais verificando que apenas a seção selecionada fica visível; acionar o toggle "Ver todas as seções" e confirmar expansão contínua de todas as seções mantendo a regra de validação `hasAnalysis` e salvamento intactos.

### Tests for User Story 1 🧪

- [X] T004 [US1] Criar testes unitários e de integração para navegação por abas, modo focado/contínuo e preservação de v-models em `caderno-leitura-0.1/frontend/tests/study-editor-fields.test.mjs`

### Implementation for User Story 1

- [X] T005 [US1] Implementar barra de pílulas de navegação horizontal com abas (`Resumo`, `Explicação`, `Conceitos`, `Referências`, `Notas`), indicadores de conteúdo preenchido, botão toggle "Ver todas as seções" e acessibilidade WAI-ARIA (`role="tablist"`, `role="tab"`) em `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`
- [X] T006 [US1] Ajustar layout responsivo e transições suaves de foco entre seções individuais e visão contínua em `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`

**Checkpoint**: User Story 1 (MVP) concluída e testável de forma independente. O editor já permite escrita focada e elimina rolagem excessiva.

---

## Phase 4: User Story 2 - Barra de Formatação Markdown Otimizada, Atalhos e Prévia Imediata (Priority: P2)

**Goal**: Fornecer alvos táteis mínimos de 44x44px na `MarkdownToolbar.vue`, atalhos universais de teclado (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`) e alternância instantânea "Editar / Prévia" in-place no cabeçalho de cada seção analítica via `markdown-it`.

**Independent Test**: Selecionar texto e aplicar formatação via atalhos de teclado e botões da barra; verificar emulando toque móvel que botões possuem $\ge 44\times 44$px sem quebra horizontal; alternar para a prévia in-place e confirmar renderização fiel do HTML Markdown.

### Tests for User Story 2 🧪

- [X] T007 [P] [US2] Estender testes automatizados para atalhos de teclado (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`), alvos táteis móveis e modo de prévia in-place em `caderno-leitura-0.1/frontend/tests/markdown-toolbar.test.mjs`

### Implementation for User Story 2

- [X] T008 [P] [US2] Otimizar `MarkdownToolbar.vue` com botões táteis de no mínimo 44x44px no mobile, rolagem horizontal suave (`overflow-x: auto`) e preservação de foco no `@mousedown.prevent` em `caderno-leitura-0.1/frontend/src/components/MarkdownToolbar.vue`
- [X] T009 [US2] Implementar botão toggle in-place "Editar / Prévia" no cabeçalho de cada seção analítica e renderização segura via `renderMarkdown` com tipografia consistente em `caderno-leitura-0.1/frontend/src/components/StudyEditorFields.vue`

**Checkpoint**: User Stories 1 e 2 integradas. Edição ágil com atalhos, pré-visualização instantânea e ergonomia tátil completa.

---

## Phase 5: User Story 3 - Correção Definitiva de Ícones de Categorias e Proteção de Rascunho em Sessão (Priority: P3)

**Goal**: Substituir SVGs inline corrompidos ou mal alinhados por `<Icon name="x" :size="12" />` em `CategoryBadge.vue` e `CategoryInput.vue` com acessibilidade plena por teclado, e integrar a restauração de rascunhos de sessão em `StudyEditView.vue` com banner discreto no topo.

**Independent Test**: Inspecionar badges e seletores de categoria confirmando ícones nítidos e perfeitamente centralizados com `aria-label`; recarregar a página com alterações não salvas e confirmar recuperação automática do rascunho com banner informativo e botão de descarte funcional.

### Tests for User Story 3 🧪

- [X] T010 [P] [US3] Atualizar suíte de testes de categorias validando renderização de ícones padronizados via `Icon.vue`, alinhamento e atributos de acessibilidade em `caderno-leitura-0.1/frontend/tests/category_input.test.mjs`
- [X] T011 [P] [US3] Estender testes de `StudyEditView` para cobrir auto-recuperação de rascunho, exibição do banner de restauração e descarte voluntário em `caderno-leitura-0.1/frontend/tests/study-edit.test.mjs`

### Implementation for User Story 3

- [X] T012 [P] [US3] Normalizar ícone de remoção e estrutura gráfica usando `<Icon name="x" :size="12" />` com alinhamento vertical flex e rótulo de acessibilidade em `caderno-leitura-0.1/frontend/src/components/CategoryBadge.vue`
- [X] T013 [P] [US3] Revisar e padronizar o seletor de categorias garantindo alinhamento de ícones e suporte robusto a teclado em `caderno-leitura-0.1/frontend/src/components/CategoryInput.vue`
- [X] T014 [US3] Integrar `useStudyDraft` na tela `StudyEditView.vue`, incluindo o banner discreto no topo para aviso de rascunho restaurado, botão de descarte e limpeza do snapshot pós-salvamento em `caderno-leitura-0.1/frontend/src/views/StudyEditView.vue`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e integradas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação global de integridade, validação dos 5 cenários do quickstart, execução das suítes de testes e checagem estrita de compilação.

- [X] T015 Executar validação manual e automatizada dos 5 cenários descritos em `specs/058-refinamento-editor/quickstart.md`
- [X] T016 Rodar suíte completa de testes de frontend via `npm test` em `caderno-leitura-0.1/frontend/`
- [X] T017 Rodar suíte completa de testes de backend via `pytest` garantindo isolamento total do banco de dados ativo
- [X] T018 Executar verificação estrita de tipagem TypeScript e compilação de produção via `npm run build` em `caderno-leitura-0.1/frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências externas. Início imediato.
- **Foundational (Phase 2)**: Depende da Phase 1 (tipos de dados). Bloqueia o início das histórias de usuário.
- **User Story 1 (Phase 3 - P1 MVP)**: Depende da Phase 2. Estabelece a estrutura de abas e foco do formulário.
- **User Story 2 (Phase 4 - P2)**: Depende da Phase 3 (pois adiciona a prévia in-place e melhora a toolbar nos campos de seções).
- **User Story 3 (Phase 5 - P3)**: As tarefas de categorias (T010, T012, T013) podem rodar em paralelo; a integração do banner em `StudyEditView.vue` (T011, T014) depende da Phase 2 e Phase 3.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- **Fase 4 (US2)**: T007 e T008 podem ser desenvolvidos em paralelo antes de T009.
- **Fase 5 (US3)**: T010, T011, T012 e T013 podem ser executados em paralelo.

---

## Parallel Example: User Story 3

```bash
# Executar paralelamente os testes e ajustes de categorias com o banner de rascunho:
Task: T010 "Atualizar suíte de testes de categorias em tests/category_input.test.mjs"
Task: T011 "Estender testes de StudyEditView para cobrir rascunho em tests/study-edit.test.mjs"
Task: T012 "Normalizar ícone de remoção em components/CategoryBadge.vue"
Task: T013 "Revisar alinhamento de ícones em components/CategoryInput.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Tipos de dados em `types.ts`).
2. Concluir Phase 2 (Composable `useStudyDraft.ts` e testes).
3. Concluir Phase 3 (Abas e modo focado em `StudyEditorFields.vue` e testes).
4. **Validar MVP**: Navegação por seções funcionando no mobile e desktop com redução de rolagem.

### Entrega Incremental

1. MVP concluído -> Adicionar US2 (Alvos 44px, atalhos universais e prévia in-place Markdown).
2. US2 concluída -> Adicionar US3 (Ícones limpos em `CategoryBadge` / `CategoryInput` e banner de rascunho em `StudyEditView`).
3. Executar Phase 6 (Validação fim a fim, `npm test`, `pytest`, `npm run build`).
4. Commit atômico: `feature — refinamento do editor de estudos e correcao de icones de categorias`.
