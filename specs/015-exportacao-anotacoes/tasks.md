# Tasks: Exportação de Anotações em TXT e Markdown

**Feature Branch**: `015-exportacao-anotacoes`  
**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/export-api-contract.md](./contracts/export-api-contract.md), [quickstart.md](./quickstart.md)  
**Status**: Ready for Implementation  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Definição de schemas Pydantic, tipagens TypeScript e estruturas base

- [X] T001 Criar schemas Pydantic de formato e opções de exportação em `caderno-leitura-0.1/backend/app/schemas/export.py`
- [X] T002 [P] Configurar tipos e interfaces TypeScript para exportação em `caderno-leitura-0.1/frontend/src/types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lógica central de montagem de documentos Markdown/TXT e sanitização de nomes de arquivos

- [X] T003 Implementar utilitário de sanitização de nomes de arquivo para Windows em `caderno-leitura-0.1/backend/app/services/export_service.py`
- [X] T004 [P] Implementar geradores de texto Markdown (com YAML Frontmatter e títulos hierárquicos) e Texto Puro (com divisores ASCII) em `caderno-leitura-0.1/backend/app/services/export_service.py`
- [X] T005 [P] Criar testes unitários para o sanitizador e formatador de texto em `caderno-leitura-0.1/backend/tests/test_export.py`

---

## Phase 3: User Story 1 - Exportação Completa de Anotações de um Livro (Priority: P1) 🎯 MVP

**Goal**: Permitir exportar todo o conteúdo de um livro (capítulos e estudos ativos) em arquivo `.md` ou `.txt` a partir da tela do livro.

**Independent Test**: Acessar `/livros/:id`, clicar em "Exportar anotações", selecionar o formato e verificar o download do arquivo contendo todos os capítulos e estudos ordenados, com acentos preservados e sem itens da lixeira.

### Implementation for User Story 1

- [X] T006 [US1] Implementar serviço de consulta e montagem do documento consolidado do livro (excluindo lixeira) em `caderno-leitura-0.1/backend/app/services/export_service.py`
- [X] T007 [US1] Implementar endpoint `GET /api/books/{book_id}/export` com streaming UTF-8 em `caderno-leitura-0.1/backend/app/routers/books.py`
- [X] T008 [P] [US1] Adicionar testes de integração para `GET /api/books/{book_id}/export` (Markdown e TXT) em `caderno-leitura-0.1/backend/tests/test_export.py`
- [X] T009 [US1] Adicionar método `exportBook` com suporte a query params e download de blob em `caderno-leitura-0.1/frontend/src/services/api.ts`
- [X] T010 [US1] Adicionar ação de exportar anotações no cabeçalho do livro em `caderno-leitura-0.1/frontend/src/views/BookView.vue`

**Checkpoint**: User Story 1 completa e testável como MVP independente.

---

## Phase 4: User Story 2 - Exportação Granular de Estudo Individual (Priority: P2)

**Goal**: Permitir exportar pontualmente um único estudo ativo a partir da tela do leitor de estudos.

**Independent Test**: Acessar `/estudos/:id`, clicar em "Exportar estudo", escolher o formato e verificar o download do arquivo contendo exclusivamente os dados daquele estudo.

### Implementation for User Story 2

- [X] T011 [US2] Implementar serviço de consulta e montagem do documento de estudo individual em `caderno-leitura-0.1/backend/app/services/export_service.py`
- [X] T012 [US2] Implementar endpoint `GET /api/studies/{study_id}/export` com streaming UTF-8 em `caderno-leitura-0.1/backend/app/routers/studies.py`
- [X] T013 [P] [US2] Adicionar testes de integração para `GET /api/studies/{study_id}/export` em `caderno-leitura-0.1/backend/tests/test_export.py`
- [X] T014 [US2] Adicionar método `exportStudy` no cliente HTTP em `caderno-leitura-0.1/frontend/src/services/api.ts`
- [X] T015 [US2] Adicionar ação de exportar estudo no cabeçalho da visualização em `caderno-leitura-0.1/frontend/src/views/StudyView.vue`

**Checkpoint**: User Story 2 completa. Ambos os níveis de exportação (Livro e Estudo) funcionais.

---

## Phase 5: User Story 3 - Configuração de Conteúdo e Interoperabilidade (Priority: P3)

**Goal**: Fornecer modal acessível (`ExportModal.vue`) para configurar o formato e selecionar quais blocos de conteúdo incluir na exportação.

**Independent Test**: Abrir o modal de exportação, desmarcar seções de análise ou marcar resposta original, baixar o arquivo e verificar que o conteúdo corresponde exatamente à seleção feita.

### Implementation for User Story 3

- [X] T016 [US3] Criar componente modal acessível `caderno-leitura-0.1/frontend/src/components/ExportModal.vue` com opções de formato, seleção de seções por checkbox e armadilha de foco
- [X] T017 [US3] Conectar `ExportModal.vue` na visualização `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- [X] T018 [US3] Conectar `ExportModal.vue` na visualização `caderno-leitura-0.1/frontend/src/views/StudyView.vue`
- [X] T019 [P] [US3] Criar testes automatizados para o modal e opções de exportação em `caderno-leitura-0.1/frontend/tests/export.test.mjs`

**Checkpoint**: As três histórias estão 100% integradas e funcionais.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testes de regressão, conformidade UTF-8 e integridade da lixeira

- [X] T020 [P] Validar exclusão rigorosa de itens da lixeira (`deleted_at IS NOT NULL`) em testes de exportação em `caderno-leitura-0.1/backend/tests/test_export.py`
- [X] T021 Executar suíte completa de testes do backend com pytest
- [X] T022 Executar suíte completa de testes do frontend com `npm test`
- [X] T023 Executar compilação com `npm run build` garantindo zero erros de tipagem TypeScript
- [X] T024 Validar roteiro de cenários manuais conforme `caderno-leitura-0.1/specs/015-exportacao-anotacoes/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende da Phase 1 — BLOQUEIA as histórias de usuário.
- **User Stories (Phases 3 a 5)**:
  - US1 (Livro completo - MVP): Depende da Phase 2.
  - US2 (Estudo individual): Depende da Phase 2; pode ser executada em paralelo a US1.
  - US3 (Modal de configuração): Depende dos métodos criados em US1 e US2.
- **Polish (Phase 6)**: Depende de todas as histórias concluídas.

### Parallel Opportunities

- T001 e T002 podem rodar em paralelo.
- T004 e T005 podem ser implementados paralelamente.
- T008 e T013 (testes de integração) podem rodar em paralelo.
- T019 (testes frontend) pode ser construído paralelamente ao desenvolvimento dos componentes.

---

## Implementation Strategy (MVP First)

1. **Fase 1 e 2**: Schemas, formatador Markdown/TXT e sanitizador de nomes de arquivo.
2. **Fase 3 (MVP - US1)**: Rota de exportação do livro completo e ação básica de download em `BookView.vue`.
3. **Fase 4 (US2)**: Rota de exportação de estudo individual e ação em `StudyView.vue`.
4. **Fase 5 (US3)**: Modal `ExportModal.vue` refinado com seleção de seções para ambas as visualizações.
5. **Fase 6 (Finalização)**: Bateria de testes de regressão backend/frontend e validação de build.
