# Tasks: F0.6.2 — Seleção e Ações Contextuais

**Branch**: `041-selecao-acoes-contextuais` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Definição de contratos de dados, interfaces TypeScript e schemas Pydantic.

- [x] T001 [P] Definir tipos TypeScript `StudyHighlight`, `HighlightColor`, `HighlightKind` e `TextSelectionContext` em `caderno-leitura-0.1/frontend/src/types.ts`
- [x] T002 [P] Criar schemas Pydantic v2 `StudyHighlightCreate`, `StudyHighlightUpdate` e `StudyHighlightRead` em `caderno-leitura-0.1/backend/app/schemas/study_highlight.py`

---

## Phase 2: Foundational (Pré-requisitos Bloqueantes)

**Purpose**: Estrutura central de persistência e endpoints que bloqueiam a implementação das histórias de usuário.

- [x] T003 Criar modelo SQLAlchemy `StudyHighlight` com constraints de validação em `caderno-leitura-0.1/backend/app/models/study_highlight.py` e registrar em `caderno-leitura-0.1/backend/app/models/__init__.py`
- [x] T004 Criar script de migração Alembic `0020_add_study_highlights.py` em `caderno-leitura-0.1/backend/migrations/versions/0020_add_study_highlights.py`
- [x] T005 Implementar serviço `study_highlight_service.py` com regras de isolamento, CRUD e cascata em `caderno-leitura-0.1/backend/app/services/study_highlight_service.py`
- [x] T006 Implementar router FastAPI de destaques e registrar na aplicação em `caderno-leitura-0.1/backend/app/routers/study_highlights.py` e `caderno-leitura-0.1/backend/app/main.py`
- [x] T007 Implementar métodos de API de destaques no frontend (`listHighlights`, `createHighlight`, `updateHighlight`, `deleteHighlight`) em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: Camada de persistência, API e client prontos — desenvolvimento das histórias de usuário pode prosseguir.

---

## Phase 3: User Story 1 - Seleção Textual Fluida e Barra Flutuante Contextual (Priority: P1)

**Goal**: Permitir seleção de texto no leitor de estudos e exibir barra contextual flutuante no Desktop e barra ancorada na base no Mobile.

**Independent Test**: Selecionar um trecho de texto em qualquer seção do estudo na tela `StudyView.vue` e verificar o surgimento imediato da barra com as ações, posicionada de forma estável e fechando ao desselecionar ou pressionar `Escape`.

### Tests for User Story 1
- [x] T008 [P] [US1] Criar testes unitários para o composable de seleção em `caderno-leitura-0.1/frontend/test/useTextSelection.spec.ts`
- [x] T009 [P] [US1] Criar testes de renderização e posicionamento adaptativo da barra contextual em `caderno-leitura-0.1/frontend/test/FloatingActionsToolbar.spec.ts`

### Implementation for User Story 1
- [x] T010 [US1] Implementar composable `useTextSelection.ts` para captura de Selection API, Range API, offsets e bounding rect em `caderno-leitura-0.1/frontend/src/composables/useTextSelection.ts`
- [x] T011 [US1] Implementar componente `FloatingActionsToolbar.vue` com posicionamento inteligente (clamp no viewport no Desktop e bottom sheet fixo no Mobile) em `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue`
- [x] T012 [US1] Integrar captura de seleção e barra flutuante em `caderno-leitura-0.1/frontend/src/components/StudyTabs.vue` e `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Barra flutuante e seleção contextual funcionando perfeitamente em telas Desktop e Mobile.

---

## Phase 4: User Story 2 - Destacar Trechos (Marca-Texto) com Persistência Confiável (Priority: P1) 🎯 MVP

**Goal**: Permitir destacar passagens do estudo com marca-texto suave, salvar no SQLite, restaurar ao recarregar e permitir remoção/edição rápida.

**Independent Test**: Selecionar uma frase, clicar em "Destacar", verificar marcação visual colorida, recarregar a página conferindo persistência e clicar no destaque para remover.

### Tests for User Story 2
- [x] T013 [P] [US2] Criar testes de backend para persistência, validações e isolamento de destaques em `caderno-leitura-0.1/backend/tests/test_study_highlights.py`
- [x] T014 [P] [US2] Criar testes unitários para ancoragem e renderização não destrutiva no DOM em `caderno-leitura-0.1/frontend/test/highlightRenderer.spec.ts`

### Implementation for User Story 2
- [x] T015 [US2] Implementar composable `useStudyHighlights.ts` para carregar, criar, atualizar e remover destaques em `caderno-leitura-0.1/frontend/src/composables/useStudyHighlights.ts`
- [x] T016 [US2] Implementar utilitário `highlightRenderer.ts` para localização via TreeWalker e sobreposição de `<mark>` sem corromper nós Markdown em `caderno-leitura-0.1/frontend/src/utils/highlightRenderer.ts`
- [x] T017 [US2] Atualizar `MarkdownContent.vue` para aplicar sobreposição de destaques sobre o HTML renderizado em `caderno-leitura-0.1/frontend/src/components/MarkdownContent.vue`
- [x] T018 [US2] Implementar componente `HighlightActionPopover.vue` para gerenciar cor e exclusão ao clicar em um destaque existente em `caderno-leitura-0.1/frontend/src/components/HighlightActionPopover.vue`
- [x] T019 [US2] Integrar a ação "Destacar" da barra flutuante e popover de gestão na visualização do estudo em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: Marca-texto e persistência no SQLite 100% operacionais (MVP alcançado).

---

## Phase 5: User Story 3 - Criar Anotação ou Citação Conectada ao Trecho (Priority: P2)

**Goal**: Vincular notas explicativas aos trechos com indicador visual lateral e possibilitar cópia formatada como citação com metadados da obra.

**Independent Test**: Selecionar trecho, escolher "Anotar", digitar reflexão e verificar indicador visual que exibe a nota; selecionar outro trecho, clicar em "Copiar citação" e conferir formato colado na área de transferência.

### Implementation for User Story 3
- [x] T020 [US3] Implementar modal/popover de entrada de anotação na barra flutuante e exibição de indicador de nota em `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue` e `caderno-leitura-0.1/frontend/src/utils/highlightRenderer.ts`
- [x] T021 [US3] Implementar ação de cópia formatada de citação com metadados do estudo e toast de confirmação em `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue` e `caderno-leitura-0.1/frontend/src/views/StudyView.vue`
- [x] T022 [US3] Adicionar testes unitários de cópia de citação e notas vinculadas em `caderno-leitura-0.1/frontend/test/FloatingActionsToolbar.spec.ts`

**Checkpoint**: Anotações vinculadas e cópia de citações funcionando de forma integrada.

---

## Phase 6: User Story 4 - Leitura Ativa: Ocultar Trecho e Transformar em Pergunta (Priority: P2)

**Goal**: Transformar a leitura em estudo ativo permitindo ocultar trechos (oclusão com revelação sob demanda) e transformá-los em perguntas interativas.

**Independent Test**: Selecionar trecho, acionar "Ocultar" e verificar máscara visual com botão `[Revelar]`; selecionar trecho, acionar "Pergunta", digitar pergunta e verificar caixa interativa com botão `[Ver resposta]`.

### Implementation for User Story 4
- [x] T023 [US4] Implementar ação e renderização de oclusão de trechos (`kind = 'hidden'`) com toggle interativo de revelação em `caderno-leitura-0.1/frontend/src/utils/highlightRenderer.ts` e `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue`
- [x] T024 [US4] Implementar ação "Transformar em pergunta" (`kind = 'question'`) com prompt de pergunta e revelação da resposta em `caderno-leitura-0.1/frontend/src/utils/highlightRenderer.ts` e `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue`
- [x] T025 [US4] Adicionar testes de interação e revelação de oclusão/perguntas em `caderno-leitura-0.1/frontend/test/highlightRenderer.spec.ts`

**Checkpoint**: Todas as 5 ações contextuais operacionais no editor de estudos.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Estilização temática, acessibilidade e validação completa do sistema.

- [x] T026 [P] Ajustar paleta de destaques e blocos de oclusão para compatibilidade com os 10 temas visuais em `caderno-leitura-0.1/frontend/src/styles/themes.css`
- [x] T027 [P] Garantir acessibilidade física (alvos de toque >= 44x44px no mobile, navegação por teclado e `aria-*`) em `caderno-leitura-0.1/frontend/src/components/FloatingActionsToolbar.vue`
- [x] T028 Executar testes automatizados no backend (`pytest backend/tests/test_study_highlights.py`) e frontend (`npm test`), validando build limpo (`npm run build`)
- [x] T029 Executar roteiro de validação manual completo conforme `specs/041-selecao-acoes-contextuais/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA a execução de todas as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende da conclusão da Phase 2 (Foundational).
- **User Story 2 (Phase 4)**: Depende da Phase 3 (US1 - Captura de seleção e barra flutuante).
- **User Story 3 (Phase 5)**: Depende da Phase 4 (US2 - Infraestrutura de persistência e renderização).
- **User Story 4 (Phase 6)**: Depende da Phase 4 (US2 - Infraestrutura de sobreposição e renderização).
- **Polish (Phase 7)**: Depende da conclusão de todas as histórias de usuário.

---

## Parallel Opportunities

- **Phase 1**: T001 (Frontend types) e T002 (Backend schemas) podem rodar em paralelo.
- **Phase 3**: T008 (Testes seleção) e T009 (Testes toolbar) podem rodar em paralelo.
- **Phase 4**: T013 (Testes backend) e T014 (Testes renderizador) podem rodar em paralelo.
- **Phase 7**: T026 (Temas CSS) e T027 (Acessibilidade) podem rodar em paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)
1. Completar Setup (Phase 1) e Foundational (Phase 2).
2. Implementar seleção e barra flutuante (Phase 3 - US1).
3. Implementar marca-texto e persistência SQLite (Phase 4 - US2).
4. **STOP and VALIDATE**: Testar marca-texto, recarregamento e remoção de destaque.

### Incremental Delivery
1. Foundation pronta (Phase 1 + 2)
2. US1 + US2 entregam o marca-texto funcional no Desktop e Mobile (MVP).
3. US3 adiciona anotações reflexivas vinculadas e cópia de citações com metadados.
4. US4 adiciona Leitura Ativa (oclusão e perguntas para retenção).
5. Phase 7 refina acessibilidade, temas e executa validações do quickstart.
