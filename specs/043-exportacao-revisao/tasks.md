# Tasks: F0.6.4 — Exportação com Destaques e Caderno de Revisão

**Feature Branch**: `043-exportacao-revisao` | **Date**: 2026-09-27 | **Spec**: [specs/043-exportacao-revisao/spec.md](spec.md) | **Plan**: [specs/043-exportacao-revisao/plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extensão dos esquemas de dados, tipos TypeScript e rotinas de consulta de exportação compartilhados.

- [X] T001 Estender modelos Pydantic ExportOptions, ExportFormat e ExportType em caderno-leitura-0.1/backend/app/schemas/export.py
- [X] T002 [P] Atualizar tipagens TypeScript ExportType e ExportConfig em caderno-leitura-0.1/frontend/src/types.ts
- [X] T003 [P] Atualizar construtor de parâmetros buildExportQuery em caderno-leitura-0.1/frontend/src/services/api.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de processamento de texto e parametrização de endpoints bloqueante para as histórias de usuário.

**CRITICAL**: Nenhuma história de usuário pode ser finalizada antes da conclusão desta fase.

- [X] T004 Implementar algoritmo de injeção reversa de destaques e ancoragem de rodapé em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T005 [P] Atualizar parâmetros de rota GET /api/books/{id}/export e GET /api/studies/{id}/export em caderno-leitura-0.1/backend/app/routers/books.py e caderno-leitura-0.1/backend/app/routers/studies.py
- [X] T006 Adicionar fixtures e utilitários de estudo sintético com destaques para testes em caderno-leitura-0.1/backend/tests/test_export.py

**Checkpoint**: Fundação pronta — os serviços e rotas aceitam os novos parâmetros e possuem suporte ao algoritmo de injeção reversa.

---

## Phase 3: User Story 1 - Exportação de Estudo com Destaques e Anotações (Priority: P1) 🎯 MVP

**Goal**: Permitir que leitores exportem estudos individuais ou livros completos em Markdown e Texto Puro preservando os grifos visuais e notas de rodapé sem deslocamento de índices.

**Independent Test**: Criar um estudo com 3 destaques e notas de rodapé; acionar a exportação com `include_highlights=true`; verificar que o arquivo Markdown gerado contém a sintaxe `==trecho==[^N]` com as notas compiladas no fim da seção, e a exportação em texto contém `«trecho» [N]`.

### Tests for User Story 1
- [X] T007 [P] [US1] Adicionar testes unitários para injeção de destaques em Markdown e Texto Puro em caderno-leitura-0.1/backend/tests/test_export.py
- [X] T008 [P] [US1] Adicionar testes unitários para buildExportQuery com destaques ativos em caderno-leitura-0.1/frontend/tests/export.test.mjs

### Implementation for User Story 1
- [X] T009 [US1] Implementar injeção de destaques e notas de rodapé em format_study_markdown e format_study_text em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T010 [US1] Implementar injeção de destaques em format_book_markdown e format_book_text em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T011 [US1] Integrar busca de StudyHighlight do estudo e do livro em generate_study_export e generate_book_export em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T012 [US1] Adicionar controle de inclusão de destaques e anotações no modal em caderno-leitura-0.1/frontend/src/components/ExportModal.vue

**Checkpoint**: MVP concluído — exportações em Markdown e Texto Puro integram perfeitamente os grifos e notas da leitura ativa.

---

## Phase 4: User Story 2 - Geração do Caderno de Revisão (Digest) (Priority: P1)

**Goal**: Gerar documento compilado contendo exclusivamente as perguntas ativas, termos ocluídos, notas e citações em nível de estudo ou livro consolidado.

**Independent Test**: Solicitar a exportação no modo `export_type=digest`; verificar que o documento omite o texto integral e compila as perguntas, termos ocluídos e notas agrupados por capítulo e estudo com sumário e estatísticas no cabeçalho.

### Tests for User Story 2
- [X] T013 [P] [US2] Adicionar testes automatizados para geração de Caderno de Revisão de estudo e de livro em caderno-leitura-0.1/backend/tests/test_export.py
- [X] T014 [P] [US2] Adicionar testes para caso de borda de estudo ou livro sem destaques cadastrados em caderno-leitura-0.1/backend/tests/test_export.py

### Implementation for User Story 2
- [X] T015 [US2] Implementar geradores de Caderno de Revisão format_study_digest_markdown e format_study_digest_text em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T016 [US2] Implementar geradores de Caderno de Revisão format_book_digest_markdown e format_book_digest_text com sumário em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T017 [US2] Atualizar generate_study_export e generate_book_export para rotear modalidade digest em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T018 [US2] Adicionar seletor de modalidade (Documento Completo vs Caderno de Revisão) em caderno-leitura-0.1/frontend/src/components/ExportModal.vue

**Checkpoint**: Histórias 1 e 2 funcionais — usuários podem exportar o estudo integral com destaques ou o Caderno de Revisão sintetizado.

---

## Phase 5: User Story 3 - Configuração de Formatação e Modo de Revisão (Priority: P2)

**Goal**: Permitir que o leitor escolha entre Modo Exercício (respostas e oclusões suprimidas com linhas de preenchimento `_______` e Gabarito Final) e Modo Estudo (respostas expostas inline).

**Independent Test**: Exportar o Caderno de Revisão com `exercise_mode=true` e confirmar que as respostas das perguntas viram `_______` no corpo e aparecem na seção final de Gabarito de Revisão.

### Tests for User Story 3
- [X] T019 [P] [US3] Adicionar testes para validação do Modo Exercício e geração do Gabarito de Revisão em caderno-leitura-0.1/backend/tests/test_export.py
- [X] T020 [P] [US3] Adicionar testes de regressão de parâmetros em caderno-leitura-0.1/frontend/tests/export.test.mjs

### Implementation for User Story 3
- [X] T021 [US3] Implementar formatação condicional de Modo Exercício e apêndice de Gabarito de Revisão em caderno-leitura-0.1/backend/app/services/export_service.py
- [X] T022 [US3] Adicionar controle de alternância para Modo Exercício na interface de caderno-leitura-0.1/frontend/src/components/ExportModal.vue

**Checkpoint**: Histórias 1, 2 e 3 completas — flexibilidade total entre revisão autoavaliativa impressa ou estudo corrido.

---

## Phase 6: User Story 4 - Exportação Confiável em Estudos Compartilhados (Priority: P3)

**Goal**: Garantir que leitores convidados com permissão somente leitura consigam exportar com destaques e gerar o Caderno de Revisão autorizado com atribuição de autoria correta.

**Independent Test**: Autenticar usuário convidado sem permissão de escrita e exportar o estudo com destaques e o Caderno de Revisão, validando sucesso HTTP 200 e metadados com autor original.

### Tests for User Story 4
- [X] T023 [P] [US4] Adicionar teste de integração para exportação de estudo compartilhado em modo somente leitura em caderno-leitura-0.1/backend/tests/test_export.py

### Implementation for User Story 4
- [X] T024 [US4] Garantir resolução segura de permissões de leitura e atribuição de autor em caderno-leitura-0.1/backend/app/services/export_service.py

**Checkpoint**: Todas as 4 histórias de usuário implementadas e validadas funcionalmente.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de integridade global, validação das suítes de teste, conformidade de estilo e auditoria constitucional.

- [X] T025 [P] Executar suíte de testes do backend com pytest em caderno-leitura-0.1/backend/tests/test_export.py
- [X] T026 [P] Executar testes do frontend e build de produção com npm test e npm run build em caderno-leitura-0.1/frontend
- [X] T027 Executar auditoria de acessibilidade WCAG AA e integridade do banco sem emojis em specs/043-exportacao-revisao/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode ser iniciado imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão da Phase 1 — BLOQUEIA a implementação das histórias de usuário.
- **User Stories (Phase 3 a Phase 6)**:
  - Todas dependem da conclusão da Phase 2 (Foundational).
  - Sequência recomendada: US1 (P1 - MVP) → US2 (P1) → US3 (P2) → US4 (P3).
- **Polish (Phase 7)**: Depende da conclusão de todas as histórias de usuário.

### User Story Dependencies

- **US1 (P1)**: Independente — foca na injeção de destaques no fluxo do estudo completo.
- **US2 (P1)**: Constrói a nova modalidade Caderno de Revisão reutilizando as consultas a `StudyHighlight`.
- **US3 (P2)**: Depende da estrutura do Caderno de Revisão da US2 para introduzir a máscara de exercício e o gabarito.
- **US4 (P3)**: Depende dos fluxos de exportação da US1 e US2 para validar a camada de autorização e metadados.

---

## Parallel Opportunities

- As tarefas T002 e T003 do Setup podem ser executadas em paralelo com a T001.
- Na Phase 2, a tarefa T005 pode ser desenvolvida em paralelo com a T004.
- As tarefas de teste unitário T007 e T008 (US1) podem ser preparadas em paralelo antes da implementação dos serviços.
- As tarefas T013 e T014 (US2) podem rodar em paralelo.
- As suítes de teste finais T025 e T026 podem ser validadas em paralelo.

---

## Parallel Example: User Story 1

```bash
# Execução paralela dos testes de US1:
Task: "Adicionar testes unitários para injeção de destaques em Markdown e Texto Puro em caderno-leitura-0.1/backend/tests/test_export.py"
Task: "Adicionar testes unitários para buildExportQuery com destaques ativos em caderno-leitura-0.1/frontend/tests/export.test.mjs"

# Execução da implementação dos formatadores em paralelo:
Task: "Implementar injeção de destaques e notas de rodapé em format_study_markdown e format_study_text"
Task: "Adicionar controle de inclusão de destaques e anotações no modal ExportModal.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Setup de Schemas e Tipos) e Phase 2 (Foundational - Algoritmo Reverso).
2. Concluir Phase 3 (User Story 1).
3. **VALIDAR MVP**: Testar a exportação de estudo e livro completo com destaques e notas de rodapé.

### Entrega Incremental
1. Setup + Foundational concluídos.
2. Adicionar US1 → Exportação integral com grifos ativa.
3. Adicionar US2 → Caderno de Revisão (Digest) gerado.
4. Adicionar US3 → Modo Exercício com gabarito final.
5. Adicionar US4 → Suporte auditado a estudos compartilhados.
6. Polish → Validação completa das suítes e checklist constitucional.
