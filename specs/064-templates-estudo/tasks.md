# Tasks: F0.7.15 — Templates Estruturados de Estudo

**Feature**: F0.7.15 — Templates Estruturados de Estudo  
**Branch**: `064-templates-estudo` | **Date**: 2026-10-10  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Inicialização das constantes do catálogo, tipos compartilhados e contratos de dados.

- [X] T001 Criar catálogo canônico dos 5 templates estruturados em `frontend/src/constants/studyTemplates.ts`
- [X] T002 [P] Declarar tipos TypeScript para templates de estudo (`StudyTemplateId`, `StudyTemplateDefinition`, etc.) em `frontend/src/types.ts`
- [X] T003 [P] Atualizar schemas Pydantic de entrada e saída com suporte a `template_id` em `backend/app/schemas/study.py`

---

## Phase 2: Foundational (Pré-requisitos Bloqueantes)

**Purpose**: Infraestrutura de banco de dados e backend necessária antes de qualquer fluxo de usuário.

**CRITICAL**: Nenhuma interface pode ser implementada antes da conclusão desta fase.

- [X] T004 Criar migração Alembic `0029_add_template_id_to_studies.py` adicionando a coluna `template_id` na tabela `studies` com `server_default='classico'` e índice
- [X] T005 [P] Atualizar mapeamento SQLAlchemy `Study` com coluna `template_id` em `backend/app/models/study.py`
- [X] T006 [P] Atualizar rotas de criação e atualização em `backend/app/routers/studies.py` para receber e persistir `template_id`
- [X] T007 Criar suíte de testes de integração do backend em `backend/tests/test_study_templates.py` com banco efêmero `tmp_path`

**Checkpoint**: Fundação de dados e contratos pronta para implementação das histórias de usuário.

---

## Phase 3: User Story 1 - Seleção de Template na Criação e Prévia de Roteiro (Priority: P1) [MVP]

**Goal**: Permitir ao leitor escolher entre os 5 templates canônicos no momento da criação/edição e visualizar a prévia do roteiro com injeção automática dos esqueletos Markdown nas 4 seções analíticas.

**Independent Test**: Criar um novo estudo selecionando "Estudo de Conceito", verificar a injeção do esqueleto Markdown e confirmar a persistência de `template_id = 'conceito'`.

### Implementação para User Story 1

- [X] T008 [US1] Criar componente `TemplateSelectorModal.vue` em `frontend/src/components/studies/TemplateSelectorModal.vue` com prévias explicativas e navegação acessível
- [X] T009 [US1] Integrar gatilho e seletor de template no topo do editor de estudos em `frontend/src/components/StudyEditorFields.vue`
- [X] T010 [US1] Implementar injeção reativa dos esqueletos analíticos Markdown nas seções correspondentes ao confirmar um template em `frontend/src/components/StudyEditorFields.vue`
- [X] T011 [US1] Atualizar `useImportDraft.ts` e `ImportView.vue` para persistir `template_id` na criação do estudo via importação/promoção
- [X] T012 [P] [US1] Adicionar testes automatizados de backend para criação de estudo com template em `backend/tests/test_study_templates.py`

**Checkpoint**: User Story 1 funcional de ponta a ponta (MVP entregue).

---

## Phase 4: User Story 2 - Troca Segura de Template com Proteção de Conteúdo Existente (Priority: P2)

**Goal**: Permitir alternar o template em um estudo já existente salvaguardando o trabalho do leitor com diálogo de confirmação deliberado entre "Substituir Conteúdo" e "Anexar ao Final" (Q1: A).

**Independent Test**: Preencher uma seção com texto, tentar trocar o template e verificar se o modal de confirmação protege contra perda acidental de dados, testando tanto a substituição quanto a anexação sem deleção.

### Implementação para User Story 2

- [X] T013 [US2] Implementar detecção de conteúdo pré-existente e diálogo modal de confirmação no seletor de template com as opções "Substituir Conteúdo" e "Anexar ao Final" em `frontend/src/components/StudyEditorFields.vue`
- [X] T014 [US2] Implementar lógica de concatenação limpa ("Anexar ao Final") preservando 100% das anotações existentes do usuário em `frontend/src/components/StudyEditorFields.vue`
- [X] T015 [US2] Integrar `template_id` no ciclo de vida e rascunhos de edição em `frontend/src/composables/useStudyEdit.ts` e `frontend/src/views/StudyEditView.vue`
- [X] T016 [P] [US2] Adicionar testes automatizados de backend para atualização de `template_id` via `PUT /api/studies/{id}` em `backend/tests/test_study_templates.py`

**Checkpoint**: User Stories 1 e 2 funcionais conjuntamente.

---

## Phase 5: User Story 3 - Visualização Contextual e Persistência Retrocompatível (Priority: P3)

**Goal**: Exibir identificador discreto do modelo analítico empregado no cabeçalho da leitura do estudo e garantir retrocompatibilidade absoluta para todo o acervo legado.

**Independent Test**: Abrir um estudo antigo sem template e verificar que opera normalmente com padrão clássico; visualizar um estudo novo com template e verificar a presença do badge semântico.

### Implementação para User Story 3

- [X] T017 [US3] Atualizar `StudyView.vue` para exibir badge discreto e semântico com o nome do template quando o estudo for estruturado por modelo diferente de `'classico'`
- [X] T018 [US3] Implementar fallback visual e funcional para `'classico'` em estudos com `template_id` ausente ou nulo em `StudyView.vue` e `StudyEditorFields.vue`
- [X] T019 [P] [US3] Adicionar testes de regressão no backend garantindo fallback transparente para `'classico'` em estudos legados em `backend/tests/test_study_templates.py`

**Checkpoint**: Todas as 3 histórias de usuário implementadas e integradas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de conformidade visual, acessibilidade, estabilidade e suítes completas de testes.

- [X] T020 [P] Criar suíte de testes de frontend em `frontend/tests/study_templates.test.mjs` validando contratos do catálogo, ausência de emojis e acessibilidade
- [X] T021 Auditar alvos táteis mínimos ($\ge 44 \times 44$px) e conformidade visual sem emojis em `TemplateSelectorModal.vue` e `StudyEditorFields.vue`
- [X] T022 Executar validação completa do quickstart e rodar `npm test`, `pytest` e `npm run build`

---

## Dependencies & Execution Order

### Dependência entre Fases

1. **Setup (Phase 1)**: Sem dependências — execução imediata.
2. **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA todas as histórias de usuário.
3. **User Stories (Phases 3 a 5)**: Dependem da conclusão da Phase 2.
   - US1 (P1): MVP principal de seleção e injeção de template.
   - US2 (P2): Depende do fluxo de US1 para implementar a proteção de troca.
   - US3 (P3): Depende da persistência do modelo em US1 e US2 para exibição na leitura.
4. **Polish (Phase 6)**: Executada ao término das histórias de usuário.

---

## Implementation Strategy

### MVP First (User Story 1)

1. Concluir Setup e Foundational (migração Alembic `0029`, modelo `Study`, schemas Pydantic).
2. Concluir User Story 1 (catálogo de templates, modal de seleção, injeção no editor).
3. **Validar US1**: Criar estudo de teste com template "Estudo de Conceito".
4. Concluir User Story 2 (diálogo de salvaguarda "Substituir" vs "Anexar").
5. Concluir User Story 3 (badge discreto no leitor e fallback para acervo legado).
6. Rodar testes de regressão completos (`npm test`, `pytest`, `npm run build`).
