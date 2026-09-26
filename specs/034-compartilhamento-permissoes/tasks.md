# Tasks: F07 — Compartilhamento e Permissões por Recurso (ACL)

**Feature**: F07 — Compartilhamento e Permissões por Recurso (ACL)
**Branch**: `034-compartilhamento-permissoes`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup & Data Layer (Modelos e Migrações)

**Purpose**: Estruturar as colunas de visibilidade e a tabela de ACL nominal no SQLite local com total retrocompatibilidade e integridade referencial.

- [x] T001 Criar modelo relacional ResourcePermission em backend/app/models/resource_permission.py
- [x] T002 Atualizar modelo Book em backend/app/models/book.py com campo visibility ('private', 'friends', 'public')
- [x] T003 Atualizar modelo Study em backend/app/models/study.py com campo visibility ('inherit', 'private', 'friends', 'custom', 'public')
- [x] T004 Criar migração Alembic backend/alembic/versions/0017_add_sharing_and_permissions.py com colunas de visibilidade e tabela resource_permissions
- [x] T005 [P] Criar schemas Pydantic de visibilidade e ACL em backend/app/schemas/sharing.py

---

## Phase 2: Foundational (Mecanismo de Resolução de Acesso e Blindagem)

**Purpose**: Núcleo de autorização centralizado que resolve visibilidade efetiva, herança livro-estudo e blindagem anti-enumeração com 404.

**CRITICAL**: Nenhuma User Story pode ser finalizada antes da conclusão desta fundação.

- [x] T006 Implementar serviço de resolução de permissões em backend/app/services/sharing_service.py (resolve_effective_visibility, can_read_study, can_read_book)
- [x] T007 [P] Atualizar schemas BookRead e StudyRead em backend/app/schemas/book.py e backend/app/schemas/study.py com visibility e can_edit
- [x] T008 Integrar resolução can_read_study e can_read_book com blindagem 404 nos endpoints GET de backend/app/routers/studies.py e backend/app/routers/books.py

**Checkpoint**: Fundação pronta — verificação de visibilidade e herança ativa no backend.

---

## Phase 3: User Story 1 - Modos Fundamentais de Visibilidade (Privado, Amigos, Público) (Priority: P1) 🎯 MVP

**Goal**: Permitir ao leitor proprietário alternar a visibilidade de estudos e livros entre Privado, Amigos e Público, garantindo leitura segura e somente-leitura inviolável para convidados.

**Independent Test**: Leitor A cria estudo e define visibilidade como 'friends'. Amigo B lê perfeitamente com can_edit=False e sem botões de edição; estranho C recebe 404. Ao mudar para 'public', usuário C autenticado passa a acessar via link.

- [x] T009 [P] [US1] Criar testes automatizados para visibilidade privada, amigos e pública em backend/tests/test_sharing_and_permissions.py
- [x] T010 [US1] Implementar endpoint PUT /api/studies/{id}/visibility em backend/app/routers/studies.py para alteração de visibilidade pelo proprietário
- [x] T011 [US1] Implementar endpoint PUT /api/books/{id}/visibility em backend/app/routers/books.py para alteração de visibilidade do livro
- [x] T012 [US1] Aplicar blindagem rigorosa de mutação (403 Forbidden para não-proprietários) em PATCH/DELETE e adições de nós/relações em backend/app/routers/studies.py
- [x] T013 [P] [US1] Criar cliente de API para visibilidade e compartilhamento em frontend/src/api/sharing.ts
- [x] T014 [US1] Implementar componente ShareModal.vue em frontend/src/components/sharing/ShareModal.vue com alternador de visibilidade e cópia de link
- [x] T015 [US1] Integrar botão Compartilhar e ShareModal.vue na barra de ações de frontend/src/views/StudyView.vue
- [x] T016 [US1] Exibir banner informativo de somente-leitura e ocultar botões/atalhos de mutação quando can_edit=false em frontend/src/views/StudyView.vue

**Checkpoint**: MVP Completo — Estudos e livros podem ser compartilhados com amigos e publicamente em modo somente-leitura.

---

## Phase 4: User Story 2 - Permissões Granulares Nominais / ACL Customizada (Priority: P2)

**Goal**: Permitir ao leitor conceder e revogar acesso de leitura nominal a amigos específicos via @username no modo 'custom'.

**Independent Test**: Leitor A define estudo como 'custom' e concede acesso a @amigo_b. @amigo_b lê o estudo; @amigo_c (amigo fora da ACL) recebe 404. Leitor A revoga @amigo_b; @amigo_b perde o acesso imediatamente (404).

- [x] T017 [P] [US2] Criar testes automatizados para concessão e revogação nominal de ACL em backend/tests/test_sharing_and_permissions.py
- [x] T018 [US2] Implementar funções grant_permission e revoke_permission em backend/app/services/sharing_service.py
- [x] T019 [US2] Implementar endpoints GET /api/studies/{id}/permissions, POST /api/studies/{id}/permissions e DELETE /api/studies/{id}/permissions/{user_id} em backend/app/routers/studies.py
- [x] T020 [US2] Estender ShareModal.vue em frontend/src/components/sharing/ShareModal.vue com listagem de leitores autorizados e campo de busca por @username no modo custom
- [x] T021 [US2] Implementar ação de revogação de permissão com 1 clique no ShareModal.vue em frontend/src/components/sharing/ShareModal.vue

**Checkpoint**: ACL granular nominal operacional de ponta a ponta.

---

## Phase 5: User Story 3 - Navegação e Acesso a Recursos "Compartilhados Comigo" (Priority: P3)

**Goal**: Disponibilizar aba dedicada "Compartilhados Comigo" na Biblioteca para navegação fluida em livros e estudos compartilhados por outros leitores.

**Independent Test**: Leitor B acessa a Biblioteca, clica na aba "Compartilhados Comigo" e visualiza cartões com os estudos de A aos quais tem acesso, com indicação de autor, livro e data.

- [x] T022 [P] [US3] Criar testes automatizados para listagem de recursos compartilhados em backend/tests/test_sharing_and_permissions.py
- [x] T023 [US3] Implementar consultas get_shared_studies_for_user e get_shared_books_for_user em backend/app/services/sharing_service.py
- [x] T024 [US3] Criar router backend/app/routers/sharing.py com endpoints GET /api/shared/studies e GET /api/shared/books, e registrá-lo em backend/app/main.py
- [x] T025 [P] [US3] Criar componente SharedStudiesList.vue em frontend/src/components/library/SharedStudiesList.vue com cartões e crachá do autor
- [x] T026 [US3] Implementar alternador de abas ('Meu Acervo' | 'Compartilhados Comigo') em frontend/src/views/LibraryView.vue
- [x] T027 [US3] Integrar filtros de busca por texto e por autor na aba Compartilhados Comigo em frontend/src/views/LibraryView.vue

**Checkpoint**: Central de estudos compartilhados acessível na Biblioteca com busca e filtragem.

---

## Phase 6: User Story 4 - Blindagem Rigorosa contra Bloqueios e Acessos Indevidos (Priority: P4)

**Goal**: Garantir que relações de bloqueio bilateral (F06) suprimam incondicionalmente qualquer acesso a estudos de quem bloqueou ou foi bloqueado, prevenindo invasão e enumeração.

**Independent Test**: Leitor A e Leitor B possuem relação de bloqueio ativa. B tenta acessar link de estudo público de A e recebe invariavelmente 404. Leitor A tenta adicionar B na ACL e o sistema recusa a operação.

- [x] T028 [P] [US4] Criar testes automatizados de blindagem contra bloqueios em backend/tests/test_sharing_and_permissions.py
- [x] T029 [US4] Bloquear concessão nominal para usuários bloqueados em backend/app/services/sharing_service.py
- [x] T030 [US4] Assegurar resposta 404 em todas as rotas e feeds de compartilhamento para usuários em relação de bloqueio em backend/app/services/sharing_service.py

**Checkpoint**: Blindagem total e isolamento inviolável de segurança contra bloqueados.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Testes integrados de ponta a ponta, acessibilidade visual WAI-ARIA, integridade das superclasses e validação do ecossistema.

- [x] T031 [P] Implementar suíte de testes de frontend em frontend/tests/sharing.test.mjs com alvos táteis mínimos de 44px e semântica WAI-ARIA
- [x] T032 Executar e validar suíte completa de testes (pytest backend/tests, npm test e npm run build) com 100% de aprovação
- [x] T033 Criar documentação técnica da arquitetura em docs/contexto/COMPARTILHAMENTO-ACL.md

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup & Data Layer)**: Sem dependências externas — inicia imediatamente.
- **Phase 2 (Foundational)**: Depende da Phase 1 — BLOQUEIA todas as User Stories.
- **Phase 3 (User Story 1 - MVP)**: Depende da Phase 2 — Estabelece a infraestrutura básica de visibilidade.
- **Phase 4 (User Story 2 - ACL Custom)**: Depende da Phase 3 (estende o ShareModal e endpoints de visibilidade).
- **Phase 5 (User Story 3 - Aba Compartilhados)**: Depende da Phase 3 (requer recursos compartilhados com status ativo).
- **Phase 6 (User Story 4 - Blindagem de Bloqueio)**: Depende da Phase 2 e Phase 4.
- **Phase 7 (Polish)**: Depende da conclusão das User Stories desejadas.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Modelos e Migração 0017).
2. Concluir Phase 2 (Serviço de resolução `can_read_study`).
3. Concluir Phase 3 (Endpoints de visibilidade, proteção Read-Only, `ShareModal.vue` e visualização de convidado).
4. **Validar MVP**: Testar compartilhamento com amigos e público isoladamente.

### Entrega Incremental
1. MVP entregue com sucesso (Privado, Amigos, Público).
2. Concessão nominal customizada adicionada (User Story 2).
3. Central de recursos compartilhados na Biblioteca (User Story 3).
4. Blindagem anti-bloqueio validada (User Story 4).
5. Polish, acessibilidade e documentação final (Phase 7).
