# Tasks: Fundação Multiusuário e CRUD Geral (F01)

**Feature**: `028-fundacao-multiusuario`  
**Input**: Design artifacts from `specs/028-fundacao-multiusuario/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`)  

---

## Phase 1: Setup (Infraestrutura e Identidade Básica)

**Purpose**: Estruturas fundamentais de modelo, schema e constantes de configuração para usuários.

- [X] T001 Definir constantes de identidade e ID canônico do proprietário inicial em backend/app/core/config.py
- [X] T002 [P] Criar modelo de dados SQLAlchemy User em backend/app/models/user.py
- [X] T003 [P] Criar schema Pydantic UserRead em backend/app/schemas/user.py
- [X] T004 Registrar o modelo User na exportação do módulo em backend/app/models/__init__.py

---

## Phase 2: Foundational (Mecanismos de Contexto e Migração)

**Purpose**: Mecanismo de resolução de usuário ativo, dependências FastAPI e preparação de colunas.

- [X] T005 Implementar utilitários de contexto de usuário e consulta determinística em backend/app/core/auth.py
- [X] T006 [P] Implementar injeção de dependência CurrentUser com suporte ao cabeçalho X-User-Id e fallback retrocompatível em backend/app/dependencies.py
- [X] T007 [P] Implementar função auxiliar get_user_resource_or_404 para proteção anti-IDOR em backend/app/services/persistence.py
- [X] T008 [P] Implementar router e endpoint GET /api/auth/me em backend/app/routers/auth.py e registrá-lo em backend/app/main.py
- [X] T009 Atualizar mapeamentos ORM existentes para incluir a coluna user_id em backend/app/models/book.py, backend/app/models/study.py, backend/app/models/category.py, backend/app/models/study_relation.py, backend/app/models/study_canvas_node.py, backend/app/models/canvas_frame.py e backend/app/models/search_history.py

---

## Phase 3: User Story 1 - Migração Transparente do Acervo Existente (Priority: P1) 🎯 MVP

**Goal**: Garantir que uma base legada existente seja migrada sem perdas para a nova fundação multiusuário, atribuindo 100% dos dados pré-existentes ao usuário soberano canônico.

**Independent Test**: Executar a migração sobre um banco SQLite temporário pré-populado com livros, estudos e relações legadas e verificar que todos os registros recebem o identificador do proprietário canônico sem perda de integridade.

### Tests for User Story 1
- [X] T010 [P] [US1] Criar teste automatizado de migração sem perdas do acervo legado em backend/tests/test_multiuser_migration.py

### Implementation for User Story 1
- [X] T011 [US1] Criar migração Alembic 0011_add_user_and_multiuser_foundation.py provisionando o proprietário canônico e adicionando user_id via batch_alter_table em backend/migrations/versions/0011_add_user_and_multiuser_foundation.py
- [X] T012 [US1] Validar execução idempotente e reversibilidade da migração Alembic em banco de dados temporário

---

## Phase 4: User Story 2 - Criação e Propriedade de Novos Recursos (Priority: P1)

**Goal**: Garantir que cada novo livro, capítulo, estudo, anotação, relação ou categoria pessoal criada receba automaticamente o identificador do usuário autenticado no servidor.

**Independent Test**: Enviar requisições de criação de livros, estudos e relações e verificar que as linhas persistidas possuem o user_id correspondente ao usuário emissor da requisição.

### Tests for User Story 2
- [X] T013 [P] [US2] Criar testes automatizados de injeção automática de propriedade em novos recursos em backend/tests/test_multiuser_creation.py

### Implementation for User Story 2
- [X] T014 [P] [US2] Atualizar endpoint POST /api/books para atribuir user_id = current_user.id em backend/app/routers/books.py
- [X] T015 [P] [US2] Atualizar router de capítulos para validar posse do livro via get_user_resource_or_404 na criação (POST) e demais operações (list, update, move) em backend/app/routers/chapters.py
- [X] T016 [P] [US2] Atualizar endpoints POST /api/studies e importação de estudos para associar user_id = current_user.id em backend/app/routers/studies.py e backend/app/routers/imports.py
- [X] T017 [P] [US2] Atualizar endpoint POST /api/study-relations para validar que ambos os estudos pertencem ao current_user.id e associar user_id em backend/app/routers/study_relations.py
- [X] T018 [P] [US2] Atualizar endpoints de salvamento de nós e quadros no canvas para associar user_id = current_user.id em backend/app/routers/canvas.py
- [X] T019 [P] [US2] Atualizar endpoint POST /api/categories para criar categoria pessoal vinculada a user_id = current_user.id em backend/app/routers/categories.py

---

## Phase 5: User Story 3 - Isolamento Estrito de Consultas e Operações (Priority: P1)

**Goal**: Assegurar que as listagens e consultas de acervo, busca global, histórico, cockpit analítico e lixeira retornem estritamente os dados do usuário autenticado.

**Independent Test**: Cadastrar dois usuários distintos ("Usuário A" e "Usuário B") com obras e estudos; verificar que as consultas do "Usuário A" retornam 0 registros do "Usuário B".

### Tests for User Story 3
- [X] T020 [P] [US3] Criar suíte de testes de isolamento de leitura e busca entre usuários distintos em backend/tests/test_multiuser_isolation.py

### Implementation for User Story 3
- [X] T021 [P] [US3] Filtrar listagem de livros por user_id == current_user.id em backend/app/routers/books.py
- [X] T022 [P] [US3] Filtrar listagem de estudos por user_id == current_user.id em backend/app/routers/studies.py
- [X] T023 [P] [US3] Implementar filtro híbrido em GET /api/categories (user_id IS NULL OR user_id == current_user.id) em backend/app/routers/categories.py
- [X] T024 [P] [US3] Filtrar relações e nós de canvas por user_id == current_user.id em backend/app/routers/study_relations.py e backend/app/routers/canvas.py
- [X] T025 [P] [US3] Filtrar busca global e histórico recente de pesquisas estritamente por user_id == current_user.id em backend/app/routers/search.py
- [X] T026 [P] [US3] Atualizar cálculo de métricas e hábitos de leitura no cockpit para filtrar por user_id == current_user.id em backend/app/routers/dashboard.py
- [X] T027 [P] [US3] Filtrar itens descartados na lixeira por user_id == current_user.id em backend/app/routers/trash.py

---

## Phase 6: User Story 4 - Autorização Rígida de Edição, Exclusão e Restauração (Priority: P1)

**Goal**: Garantir que somente o proprietário do dado tenha permissão para alterar, mover para a lixeira, restaurar ou excluir permanentemente seus registros.

**Independent Test**: O "Usuário B" tenta enviar requisição PATCH ou DELETE em um estudo pertencente ao "Usuário A"; a operação é rejeitada sem que nenhuma alteração ocorra no banco.

### Tests for User Story 4
- [X] T028 [P] [US4] Adicionar casos de teste para tentativas não autorizadas de edição, descarte e restauração em backend/tests/test_multiuser_isolation.py

### Implementation for User Story 4
- [X] T029 [P] [US4] Atualizar endpoint PATCH /api/books/{id} e controle de capas usando get_user_resource_or_404 em backend/app/routers/books.py e backend/app/routers/covers.py
- [X] T030 [P] [US4] Atualizar endpoint PATCH /api/studies/{id} e movimentação na árvore usando get_user_resource_or_404 em backend/app/routers/studies.py
- [X] T031 [P] [US4] Atualizar exclusão lógica, restauração e exclusão definitiva de livros em backend/app/services/trash_service.py e backend/app/routers/books.py
- [X] T032 [P] [US4] Atualizar exclusão lógica, restauração e exclusão definitiva de estudos em backend/app/services/trash_service.py e backend/app/routers/studies.py
- [X] T033 [P] [US4] Implementar proteção em DELETE /api/categories/{id} bloqueando exclusão de categorias globais (HTTP 403) e categorias de terceiros em backend/app/routers/categories.py

---

## Phase 7: User Story 5 - Proteção Contra Enumeração e Acesso Direto Não Autorizado (IDOR) (Priority: P2)

**Goal**: Garantir resposta uniforme com HTTP 404 Not Found para qualquer tentativa de acesso direto por identificador a recursos pertencentes a outro usuário.

**Independent Test**: Tentar acessar diretamente via GET, PATCH ou DELETE um identificador de livro ou estudo pertencente a outro leitor e validar que o retorno é idêntico a um ID inexistente (404 Not Found).

### Tests for User Story 5
- [X] T034 [P] [US5] Adicionar testes de validação anti-enumeração IDOR em backend/tests/test_multiuser_isolation.py

### Implementation for User Story 5
- [X] T035 [P] [US5] Aplicar get_user_resource_or_404 em GET /api/books/{id} e download de exportação em backend/app/routers/books.py
- [X] T036 [P] [US5] Aplicar get_user_resource_or_404 em GET /api/studies/{id} e leitura de respostas originais em backend/app/routers/studies.py
- [X] T037 [P] [US5] Aplicar get_user_resource_or_404 nos comandos de restauração POST /api/trash/books/{id}/restore e POST /api/trash/studies/{id}/restore em backend/app/routers/trash.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de não-regressão, build do frontend e validação end-to-end do quickstart.

- [X] T038 [P] Ajustar serviço de API do frontend para suportar propagação opcional do identificador de usuário em frontend/src/services/api.ts
- [X] T039 Executar suíte completa de testes do backend garantindo 100% de aprovação em backend/tests
- [X] T040 [P] Executar suíte completa de testes do frontend (npm test) e compilação de produção (npm run build) em frontend/
- [X] T041 Executar os cenários de validação descritos no guia quickstart.md em ambiente descartável

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências prévias — pode iniciar imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão do Setup — BLOQUEIA a implementação das User Stories.
- **User Story 1 (Phase 3 - MVP)**: Depende de Setup e Foundational. É o núcleo indispensável de migração de dados.
- **User Stories 2 a 5 (Phases 4 a 7)**: Dependem de Phase 1, Phase 2 e Phase 3 (banco estruturado com dados).
- **Polish (Phase 8)**: Depende da conclusão das fases funcionais.

### User Story Dependencies

- **User Story 1 (P1)**: Independente; valida a integridade do acervo na transição do schema.
- **User Story 2 (P1)**: Constrói a escrita com `user_id`; base para novas inserções.
- **User Story 3 (P1)**: Constrói a leitura filtrada com `user_id`.
- **User Story 4 (P1)**: Constrói a autorização de modificação e descarte com `user_id`.
- **User Story 5 (P2)**: Constrói o refinamento de segurança anti-enumeração (IDOR) em cima do helper `get_user_resource_or_404`.

### Parallel Opportunities

- Tarefas com a tag `[P]` atuam em arquivos independentes e podem ser implementadas em paralelo.
- Em Phase 1: `T002` (modelo) e `T003` (schema) podem rodar em paralelo.
- Em Phase 2: `T006`, `T007`, `T008` atuam em arquivos distintos.
- Em Phase 4: Os endpoints de criação de livros (`T014`), capítulos (`T015`), estudos (`T016`), relações (`T017`), canvas (`T018`) e categorias (`T019`) podem ser atualizados em paralelo.
- Em Phase 5: Os filtros de leitura (`T021` a `T027`) podem ser aplicados em paralelo nos diferentes routers.

---

## Implementation Strategy

### MVP First (Fases 1, 2 e 3)
1. Concluir Setup e Foundational (Modelos, Auth Context e dependência `CurrentUser`).
2. Implementar a Migração Alembic `0011` e testá-la em banco descartável.
3. Validar que todo o acervo legado é absorvido pelo proprietário canônico sem perda de registros.

### Incremental Delivery
1. Adicionar gravação de `user_id` em novas criações (US2).
2. Adicionar filtros de leitura privativa nas consultas (US3).
3. Adicionar autorização estrita em modificações e exclusões (US4).
4. Adicionar resposta padronizada anti-enumeração IDOR (US5).
5. Executar suíte completa de testes de regressão (Backend + Frontend).
