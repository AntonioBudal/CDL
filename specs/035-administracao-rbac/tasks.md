# Tasks: F08 — Administração e RBAC

**Feature**: F08 — Administração e RBAC
**Branch**: `035-administracao-rbac`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup & Foundational (Shared Infrastructure & RBAC Core)

**Purpose**: Estruturar schemas Pydantic, dependência `require_admin`, serviços base e router `/api/admin/*`.

**CRITICAL**: Nenhuma User Story pode ser iniciada antes da conclusão desta fase fundacional.

- [x] T001 [P] Criar schemas Pydantic de administração em backend/app/schemas/admin.py
- [x] T002 Criar dependência require_admin em backend/app/dependencies.py validando role == 'admin' com 403 Forbidden
- [x] T003 Implementar função revoke_user_all_sessions em backend/app/services/session_service.py
- [x] T004 Implementar funções base de estatísticas e contadores em backend/app/services/admin_service.py
- [x] T005 Criar router backend/app/routers/admin.py com require_admin e registrá-lo em backend/app/main.py

**Checkpoint**: Fundação pronta — infraestrutura de autorização por papel ativa no backend.

---

## Phase 2: User Story 1 - Painel de Gestão de Contas e Visualização Administrativa (Priority: P1) 🎯 MVP

**Goal**: Permitir ao administrador visualizar e filtrar todas as contas de usuários com métricas consolidadas, garantindo blindagem 403 contra acessos não autorizados.

**Independent Test**: Criar admin e usuário comum. Admin acessa `/admin` e lista todas as contas com busca/filtros; usuário comum recebe 403 na API e é redirecionado no frontend.

- [x] T006 [P] [US1] Criar testes automatizados para listagem administrativa, filtros e blindagem 403 em backend/tests/test_admin_and_rbac.py
- [x] T007 [US1] Implementar consulta list_users com paginação, busca e filtros (status, role) em backend/app/services/admin_service.py
- [x] T008 [US1] Implementar endpoints GET /api/admin/users e GET /api/admin/stats em backend/app/routers/admin.py
- [x] T009 [P] [US1] Criar tipos TypeScript em frontend/src/types/admin.ts e cliente adminApi em frontend/src/api/admin.ts, integrando em frontend/src/services/api.ts
- [x] T010 [US1] Implementar componente de tabela AdminUsersTable.vue em frontend/src/components/admin/AdminUsersTable.vue
- [x] T011 [US1] Implementar tela principal AdminView.vue em frontend/src/views/AdminView.vue com cards de indicadores e filtros rápidos
- [x] T012 [US1] Configurar rota /admin no Vue Router em frontend/src/router/index.ts com Navigation Guard para administradores
- [x] T013 [US1] Integrar link "Administração" na barra de navegação superior em frontend/src/App.vue visível apenas para admins

**Checkpoint**: MVP Completo — Painel administrativo operacional com visualização de contas e blindagem de segurança.

---

## Phase 3: User Story 2 - Moderação de Contas: Suspensão, Reativação e Revogação de Sessões (Priority: P2)

**Goal**: Permitir ao administrador suspender contas temporariamente (invalidando imediatamente todas as sessões ativas), reativá-las e desconectar dispositivos forçadamente.

**Independent Test**: Admin suspende conta de usuário com sessão aberta; sessão é revogada na hora e requisições subsequentes falham com 401/403. Ao reativar, usuário volta a logar normalmente.

- [x] T014 [P] [US2] Criar testes automatizados de suspensão com revogação atômica de sessões e reativação em backend/tests/test_admin_and_rbac.py
- [x] T015 [US2] Implementar funções suspend_user e reactivate_user em backend/app/services/admin_service.py
- [x] T016 [US2] Implementar função revoke_all_sessions_for_user em backend/app/services/admin_service.py
- [x] T017 [US2] Implementar endpoints POST /api/admin/users/{id}/suspend, POST /api/admin/users/{id}/reactivate e POST /api/admin/users/{id}/sessions/revoke-all em backend/app/routers/admin.py
- [x] T018 [US2] Implementar componente modal acessível AdminConfirmModal.vue em frontend/src/components/admin/AdminConfirmModal.vue
- [x] T019 [US2] Integrar ações de suspensão, reativação e revogação de sessões em AdminUsersTable.vue e AdminView.vue

**Checkpoint**: Moderação completa — Suspensão atômica com desconexão imediata e reativação funcionando de ponta a ponta.

---

## Phase 4: User Story 3 - Gestão de Papéis e Proteção contra Auto-Bloqueio (Priority: P3)

**Goal**: Permitir promoção e rebaixamento de papéis (`user` ↔ `admin`) com proteção inviolável contra auto-suspensão e garantia de que o sistema nunca fique sem administradores ativos.

**Independent Test**: Admin promove usuário a admin e rebaixa de volta. Tenta suspender a si próprio ou rebaixar o único admin ativo; o sistema bloqueia com 400 Bad Request.

- [x] T020 [P] [US3] Criar testes automatizados para proteção contra auto-bloqueio e despromoção do único admin em backend/tests/test_admin_and_rbac.py
- [x] T021 [US3] Implementar função update_user_role com verificação de contagem mínima de administradores ativos em backend/app/services/admin_service.py
- [x] T022 [US3] Aplicar salvaguarda anti-auto-suspensão e proteção do último admin no suspend_user em backend/app/services/admin_service.py
- [x] T023 [US3] Implementar endpoint PUT /api/admin/users/{id}/role em backend/app/routers/admin.py
- [x] T024 [US3] Integrar ação de alteração de papel com confirmação em AdminUsersTable.vue e AdminView.vue

**Checkpoint**: RBAC dinâmico seguro — Governança de papéis com blindagem anti-lockout.

---

## Phase 5: User Story 4 - Provisionamento e Inicialização Segura do Administrador Inicial (Priority: P4)

**Goal**: Disponibilizar utilitário CLI em terminal para criação ou promoção interativa e segura do primeiro administrador local.

**Independent Test**: Rodar o script no terminal criando um admin com senha forte; autenticar na interface com a conta criada e acessar o painel administrativo.

- [x] T025 [P] [US4] Criar testes automatizados para o utilitário CLI de provisionamento em backend/tests/test_admin_and_rbac.py
- [x] T026 [US4] Implementar script CLI executável backend/scripts/create_admin.py com suporte a prompts interativos com getpass e flags de linha de comando
- [x] T027 [US4] Implementar detecção de usuário existente e promoção determinística para admin no backend/scripts/create_admin.py

**Checkpoint**: Provisionamento seguro — Primeiro administrador pode ser configurado via terminal sem tocar manualmente no banco.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testes integrados de ponta a ponta, acessibilidade visual WAI-ARIA, integridade das diretrizes editoriais e documentação técnica.

- [x] T028 [P] Implementar suíte de testes de frontend em frontend/tests/admin.test.mjs com contratos de API, acessibilidade e alvos táteis mínimos de 44px
- [x] T029 Executar e validar suíte completa de testes (pytest backend/tests, npm test e npm run build) com 100% de aprovação
- [x] T030 Criar documentação técnica da arquitetura em docs/contexto/ADMINISTRACAO-RBAC.md

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup & Foundational)**: Sem dependências externas — inicia imediatamente e BLOQUEIA todas as histórias de usuário.
- **Phase 2 (User Story 1 - MVP)**: Depende da Phase 1 — Estabelece o painel, a rota `/admin` e a listagem.
- **Phase 3 (User Story 2 - Moderação)**: Depende da Phase 2 — Estende o painel e os serviços com ações de suspensão e revogação.
- **Phase 4 (User Story 3 - RBAC & Anti-Lockout)**: Depende da Phase 2 e Phase 3 — Adiciona governança de papéis e salvaguardas.
- **Phase 5 (User Story 4 - CLI Admin)**: Depende da Phase 1 (reutiliza hashing e modelos).
- **Phase 6 (Polish)**: Depende da conclusão de todas as histórias de usuário.

---

## Parallel Example: User Story 1

```bash
# Executar testes e tipos em paralelo:
Task: "T006 [P] [US1] Criar testes automatizados para listagem administrativa em backend/tests/test_admin_and_rbac.py"
Task: "T009 [P] [US1] Criar tipos TypeScript em frontend/src/types/admin.ts"

# Executar backend e componentes de frontend:
Task: "T007 [US1] Implementar consulta list_users em backend/app/services/admin_service.py"
Task: "T010 [US1] Implementar componente AdminUsersTable.vue em frontend/src/components/admin/AdminUsersTable.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Schemas, dependência `require_admin`, router base).
2. Concluir Phase 2 (Listagem de usuários, estatísticas, tela `AdminView.vue` e navigation guard).
3. **Validar MVP**: Testar acesso de admin vs bloqueio 403 de leitor comum.

### Entrega Incremental
1. MVP entregue com sucesso (Listagem + Estatísticas + Proteção 403).
2. Moderação atômica com revogação de sessões (User Story 2).
3. Gestão de papéis e salvaguardas anti-lockout (User Story 3).
4. Utilitário CLI para criação/promoção via terminal (User Story 4).
5. Polish final, acessibilidade e documentação técnica (Phase 6).
