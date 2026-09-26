# Tasks: F06 — Sistema de Amizades

**Branch**: `033-sistema-de-amizades`  
**Feature Spec**: [spec.md](spec.md)  
**Implementation Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup & Foundational (Prerequisitos Bloqueantes)

**Purpose**: Criação do modelo relacional, migração de banco de dados, contratos Pydantic e tipagens base que desbloqueiam todas as histórias de usuário.

- [x] T001 [P] Criar o modelo relacional `Friendship` com par ordenado normalizado `(user_id_a < user_id_b)`, constraints `UNIQUE` e `CHECK` anti-autoamizade em `backend/app/models/friendship.py`
- [x] T002 [P] Registrar o modelo `Friendship` em `backend/app/db/base.py` e configurar os relacionamentos bidirecionais em `backend/app/models/user.py`
- [x] T003 Criar migração incremental do Alembic `0016_add_friendships_table.py` com índices compostos e rollback seguro em `backend/migrations/versions/`
- [x] T004 [P] Criar schemas Pydantic v2 de entrada, saída, listagens e enumerações de amizade em `backend/app/schemas/friendship.py`
- [x] T005 [P] Criar interfaces TypeScript e enums de estado de amizade em `frontend/src/types.ts`

**Checkpoint**: Fundação relacional e tipagens prontas — implementação das histórias de usuário desbloqueada.

---

## Phase 2: User Story 1 - Solicitação, Aceite e Recusa de Amizade (Priority: P1) 🌟 MVP

**Goal**: Permitir que usuários autenticados enviem solicitações de amizade por `@username`, aceitem solicitações pendentes e recusem solicitações (retornando a relação ao estado neutro), resolvendo automaticamente solicitações cruzadas simultâneas.

**Independent Test**: Executar teste de ponta a ponta criando dois usuários sintéticos em banco efêmero (`tmp_path`). O usuário A solicita amizade a B; B recebe a solicitação e a aceita; ambos passam a constar mutuamente como amigos. Em outro teste, B recusa a solicitação de A; a pendência é eliminada e ambos retornam ao estado "sem vínculo".

### Testes da User Story 1
- [x] T006 [P] [US1] Criar suíte de testes de integração para fluxo de solicitação, auto-solicitação proibida, aceite, recusa e solicitações cruzadas em `backend/tests/test_friendships.py`

### Implementação da User Story 1
- [x] T007 [US1] Implementar serviço de domínio `friendship_service.py` com métodos `send_friend_request`, `accept_friend_request` e `reject_friend_request` em `backend/app/services/friendship_service.py`
- [x] T008 [US1] Implementar rotas `POST /api/friends/request/{username}`, `POST /api/friends/accept/{request_id}` e `POST /api/friends/reject/{request_id}` com `commit_changes(session)` em `backend/app/routers/friends.py`
- [x] T009 [US1] Registrar o router `friends.py` na aplicação FastAPI em `backend/app/main.py`
- [x] T010 [P] [US1] Implementar métodos HTTP de solicitação, aceite e recusa no cliente de API do frontend em `frontend/src/services/api.ts`

**Checkpoint**: MVP do fluxo de amizades operacional e testável de ponta a ponta no backend e frontend.

---

## Phase 3: User Story 2 - Cancelamento e Desfazimento de Amizade (Priority: P2)

**Goal**: Permitir que o autor de uma solicitação a cancele antes de ser respondida e que qualquer um dos membros de uma amizade ativa possa desfazê-la a qualquer momento de forma soberana.

**Independent Test**: O usuário A envia solicitação a B e a cancela; o registro é removido e B não vê mais pendências. Os usuários A e B são amigos; A clica em "Desfazer amizade"; o registro é dissolvido e ambos deixam de ser listados como amigos.

### Testes da User Story 2
- [x] T011 [P] [US2] Adicionar testes automatizados para cancelamento de solicitação pendente pelo remetente e desfazimento de amizade aceita em `backend/tests/test_friendships.py`

### Implementação da User Story 2
- [x] T012 [US2] Implementar métodos `cancel_friend_request` e `remove_friendship` com exclusão física atômica em `backend/app/services/friendship_service.py`
- [x] T013 [US2] Implementar endpoints `DELETE /api/friends/cancel/{request_id}` e `DELETE /api/friends/{username}` com `commit_changes(session)` em `backend/app/routers/friends.py`
- [x] T014 [P] [US2] Adicionar métodos `cancelFriendRequest` e `removeFriend` no cliente de API em `frontend/src/services/api.ts`

**Checkpoint**: Ciclo de vida de criação e encerramento voluntário de amizades 100% completo.

---

## Phase 4: User Story 3 - Bloqueio, Desbloqueio e Blindagem Bilateral (Priority: P3)

**Goal**: Fornecer mecanismo de bloqueio unilateral a partir de qualquer estado (estranhos, pendentes ou amigos), com blindagem anti-enumeração (HTTP 404) em perfis e exclusão imediata de buscas de descobríveis em ambas as direções.

**Independent Test**: O usuário A bloqueia B; ao buscar por A, B não encontra resultados; ao tentar acessar `/@username_a`, B recebe 404 Not Found; A consegue desbloquear B a qualquer momento a partir de sua lista de bloqueados, retornando ao estado neutro.

### Testes da User Story 3
- [x] T015 [P] [US3] Adicionar testes automatizados para bloqueio a partir de qualquer estado, bloqueio mútuo, blindagem de perfil público (404) e exclusão nas buscas em `backend/tests/test_friendships.py`

### Implementação da User Story 3
- [x] T016 [US3] Implementar métodos `block_user`, `unblock_user`, `get_blocked_users` e `check_is_blocked` em `backend/app/services/friendship_service.py`
- [x] T017 [US3] Implementar endpoints `POST /api/friends/block/{username}`, `POST /api/friends/unblock/{username}` e `GET /api/friends/blocked` em `backend/app/routers/friends.py`
- [x] T018 [US3] Integrar verificação de bloqueio em `backend/app/routers/users.py` (`get_user_public_profile` e `search_users` excluindo usuários bloqueados em qualquer direção)
- [x] T019 [P] [US3] Adicionar métodos `blockUser`, `unblockUser` e `getBlockedUsers` no cliente de API em `frontend/src/services/api.ts`

**Checkpoint**: Proteção e blindagem de segurança pessoal ativas no servidor e refletidas na API.

---

## Phase 5: User Story 4 - Hub Social `/amigos`, Listagens e Descoberta de Leitores (Priority: P4)

**Goal**: Disponibilizar o painel social centralizado em `/amigos` com abas para "Meus Amigos", "Solicitações", "Bloqueados" e "Descobrir Leitores", crachás numéricos de pendências no cabeçalho e contagem de amigos no perfil público.

**Independent Test**: O usuário navega para a rota `/amigos` pelo cabeçalho superior; visualiza contadores consolidados e alterna entre as 4 abas acessíveis; interage com botões contextuais ("Conectar", "Responder", "Amigos", "Bloquear") que atualizam a interface de forma reativa; visita o perfil público e constata a contagem de amigos sem vazamento da lista nominal.

### Testes da User Story 4
- [x] T020 [P] [US4] Adicionar testes automatizados para listagem de amigos, resumo consolidado de contadores e status relacional pontual em `backend/tests/test_friendships.py`

### Implementação da User Story 4
- [x] T021 [US4] Implementar métodos `get_user_friends`, `get_friend_requests`, `get_friends_summary` e `get_relation_status` em `backend/app/services/friendship_service.py`
- [x] T022 [US4] Implementar endpoints `GET /api/friends`, `GET /api/friends/requests`, `GET /api/friends/summary` e `GET /api/friends/status/{username}` em `backend/app/routers/friends.py`
- [x] T023 [US4] Adicionar campo `friends_count` no schema de perfil público `UserProfilePublicRead` em `backend/app/schemas/profile.py` e calcular contagem em `backend/app/routers/users.py`
- [x] T024 [P] [US4] Criar composable reativo `frontend/src/composables/useFriends.ts` com gerenciamento de estado das abas, contadores de pendências e ações sociais
- [x] T025 [P] [US4] Criar componente reutilizável `frontend/src/components/FriendActionButtons.vue` com variantes contextuais de botões, alvos táteis de 44px e atributos WAI-ARIA
- [x] T026 [US4] Criar visualização principal `frontend/src/views/FriendsView.vue` com nó raiz único, abas acessíveis ("Meus Amigos", "Solicitações", "Bloqueados", "Descobrir Leitores") e estados vazios acolhedores
- [x] T027 [US4] Registrar rota `/amigos` em `frontend/src/router/index.ts` e adicionar atalho de navegação com ícone SVG vetorial e crachá de pendências no cabeçalho em `frontend/src/App.vue`
- [x] T028 [US4] Integrar `FriendActionButtons.vue` e exibição de contagem de amigos no perfil público em `frontend/src/views/UserProfileView.vue` e `frontend/src/components/UserProfileCard.vue`

**Checkpoint**: Experiência visual completa, acessível e integrada em toda a interface do Caderno de Leitura.

---

## Phase 6: Polish, Validação End-to-End e Verificação de Quickstart

**Purpose**: Verificação cruzada, testes automatizados e conformidade com os critérios de aceite do Roadmap 0.5.

- [x] T029 [P] Criar suíte de testes de unidade e renderização no frontend para o hub de amigos e composable em `frontend/tests/friends.test.mjs`
- [x] T030 Executar todos os 5 cenários do `specs/033-sistema-de-amizades/quickstart.md` e a suíte completa de regressão do backend com `pytest backend/tests`
- [x] T031 Executar a validação completa do frontend com `npm test` e compilação de produção com `npm run build`
- [x] T032 [P] Elaborar o documento arquitetural consolidado da feature em `caderno-leitura-0.1/docs/contexto/SISTEMA-DE-AMIZADES.md`

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Phase 1 (Setup & Foundational)**: Executa primeiro sem dependências externas; desbloqueia todas as fases seguintes.
2. **Phase 2 (User Story 1 - MVP)**: Depende da Phase 1 concluída; estabelece a espinha dorsal de solicitações e aceite.
3. **Phase 3 (User Story 2)**: Depende da Phase 2; reutiliza a infraestrutura de amizades para cancelamento e remoção.
4. **Phase 4 (User Story 3)**: Depende da Phase 2; estende a máquina de estados para bloqueio e integra com o router de usuários.
5. **Phase 5 (User Story 4)**: Depende das fases 2, 3 e 4; conecta todas as rotas do backend ao Hub Social no frontend.
6. **Phase 6 (Polish & Validação)**: Executa após a conclusão de todas as histórias de usuário.

### Parallel Opportunities
- Em cada fase, todas as tarefas marcadas com `[P]` atuam em arquivos independentes e podem ser executadas em paralelo.
- Testes unitários/contrato (`backend/tests/test_friendships.py`) podem ser estruturados em paralelo aos schemas e tipagens.
- Os componentes do frontend (`FriendActionButtons.vue`, `FriendsView.vue`) e composables (`useFriends.ts`) podem ser desenvolvidos em paralelo aos endpoints correspondentes.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Phase 1 (Modelos, migração, schemas e tipos).
2. Concluir Phase 2 (Testes e implementação de solicitação, aceite e recusa).
3. **Validar MVP**: Comprovar que dois usuários conseguem se conectar como amigos via API.

### Entrega Incremental
1. Adicionar cancelamento e desfazimento (Phase 3).
2. Adicionar bloqueio bilateral e blindagem anti-enumeração (Phase 4).
3. Entregar o Hub Social `/amigos` e componentes visuais (Phase 5).
4. Homologar com regressão completa (Phase 6).
