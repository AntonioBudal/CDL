# Tasks: F10 — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  
**Input**: Design artifacts from `specs/039-seguranca-auditoria-conta/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configurações de ambiente, infraestrutura de taxa e schemas base

- [X] T001 [P] Configurar parâmetros de Google OAuth 2.0 e Rate Limiting em `caderno-leitura-0.1/backend/app/core/config.py`
- [X] T002 [P] Definir tipos e contratos TypeScript para ciclo de vida, exportação e auditoria em `caderno-leitura-0.1/frontend/src/types/auth.ts`
- [X] T003 [P] Criar cliente de API para rotas de ciclo de vida e exportação em `caderno-leitura-0.1/frontend/src/api/account.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estruturas de banco de dados, migração Alembic, modelos de dados e serviços centrais que bloqueiam as User Stories

**CRITICAL**: Nenhuma User Story pode ser iniciada antes da conclusão desta fase.

- [X] T004 Criar modelo relacional `AuditLog` com campos de evento, timestamp, usuário e detalhes em `caderno-leitura-0.1/backend/app/models/audit_log.py`
- [X] T005 [P] Atualizar modelo relacional `User` com campos `status`, `deactivated_at`, `deleted_at`, `failed_login_attempts` e `locked_until` em `caderno-leitura-0.1/backend/app/models/user.py`
- [X] T006 Registrar modelo `AuditLog` e relacionamentos em `caderno-leitura-0.1/backend/app/models/__init__.py`
- [X] T007 Criar migração Alembic `0019_add_audit_logs_and_user_lifecycle.py` em `caderno-leitura-0.1/backend/migrations/versions/0019_add_audit_logs_and_user_lifecycle.py`
- [X] T008 [P] Implementar gerenciador em memória de Rate Limiting com janela deslizante e cabeçalho Retry-After em `caderno-leitura-0.1/backend/app/core/rate_limiter.py`
- [X] T009 Implementar serviço central de auditoria com filtro de sanitização e eliminação de segredos em `caderno-leitura-0.1/backend/app/services/audit_service.py`

**Checkpoint**: Fundação pronta - banco, migrações, rate limiter e serviço de auditoria operacionais.

---

## Phase 3: User Story 1 - Proteção contra Força Bruta e Enumeração (Priority: P1) [MVP]

**Goal**: Proteger endpoints de autenticação com limite de 5 tentativas a cada 5 minutos, respondendo com HTTP 429 e padronizar mensagens contra enumeração de contas (OWASP).

**Independent Test**: Executar requisições inválidas em série e verificar disparo de HTTP 429 com cabeçalho Retry-After; validar que erros de login retornam mensagem idêntica "Credenciais inválidas" (`HTTP 401`) tanto para usuários existentes quanto inexistentes.

### Tests for User Story 1
- [X] T010 [P] [US1] Criar testes automatizados de rate limiting e bloqueio temporário em `caderno-leitura-0.1/backend/tests/test_rate_limit.py`
- [X] T011 [P] [US1] Criar testes de proteção contra enumeração de contas em `caderno-leitura-0.1/backend/tests/test_auth_anti_enumeration.py`

### Implementation for User Story 1
- [X] T012 [US1] Integrar dependência de rate limiting nas rotas `/api/auth/login`, `/api/auth/register` e `/api/auth/google` em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [X] T013 [US1] Implementar controle de tentativas incorretas e bloqueio temporário por conta (`failed_login_attempts` e `locked_until`) em `caderno-leitura-0.1/backend/app/services/auth_service.py`
- [X] T014 [US1] Padronizar mensagens de erro unificadas contra enumeração de contas no fluxo de login e recuperação em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [X] T015 [US1] Adicionar tratamento defensivo e mensagens de feedback amigáveis para erro 429 no cliente de autenticação em `caderno-leitura-0.1/frontend/src/stores/auth.ts`

**Checkpoint**: User Story 1 completa e testável de forma independente (MVP de segurança ativo).

---

## Phase 4: User Story 2 - Autenticação Prática com Google OAuth 2.0 (Priority: P1)

**Goal**: Permitir login e cadastro com um clique via Google OAuth 2.0 na tela inicial/login sem necessidade de senha local, suportando tanto fluxo web redirect quanto GIS com auto-associação segura.

**Independent Test**: Simular autorização do Google com nova conta (gera usuário e sessão sem pedir senha) e com e-mail já existente (auto-vincula e loga com sucesso).

### Tests for User Story 2
- [X] T016 [P] [US2] Criar testes de integração do fluxo Google OAuth 2.0 (redirecionamento, callback e auto-associação) em `caderno-leitura-0.1/backend/tests/test_google_oauth_web.py`

### Implementation for User Story 2
- [X] T017 [US2] Implementar métodos de geração de URL de autorização e troca de código OAuth 2.0 em `caderno-leitura-0.1/backend/app/services/google_auth_service.py`
- [X] T018 [US2] Criar endpoints `GET /api/auth/google/login` e `GET /api/auth/google/callback` em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [X] T019 [US2] Aprimorar provisionamento implícito de novos leitores Google sem senha e auto-vínculo de e-mail em `caderno-leitura-0.1/backend/app/services/auth_service.py`
- [X] T020 [US2] Refinar componente de botão "Entrar com o Google" com suporte a feedback de carregamento em `caderno-leitura-0.1/frontend/src/components/auth/GoogleSignInButton.vue`
- [X] T021 [US2] Integrar botão de login com Google com destaque na tela de login em `caderno-leitura-0.1/frontend/src/views/LoginView.vue`
- [X] T022 [US2] Integrar botão de login com Google na tela de cadastro em `caderno-leitura-0.1/frontend/src/views/RegisterView.vue`

**Checkpoint**: User Stories 1 e 2 funcionais; login tradicional e Google OAuth protegidos por rate limit.

---

## Phase 5: User Story 3 - Trilha de Auditoria Estruturada e Sem Segredos (Priority: P2)

**Goal**: Registrar imutavelmente eventos críticos de segurança (logins, alterações de permissão e exclusões) em `AuditLog`, garantindo sanitização total de segredos e consulta administrativa paginada.

**Independent Test**: Disparar eventos de segurança e verificar gravação no banco; certificar ausência de tokens e senhas no campo `details`; validar que usuários não-admin recebem HTTP 403 ao consultar a trilha.

### Tests for User Story 3
- [X] T023 [P] [US3] Criar testes de registro e sanitização de eventos de auditoria em `caderno-leitura-0.1/backend/tests/test_audit_log.py`

### Implementation for User Story 3
- [X] T024 [P] [US3] Criar schemas Pydantic para listagem de auditoria em `caderno-leitura-0.1/backend/app/schemas/audit_log.py`
- [X] T025 [US3] Integrar chamadas `audit_service.log_event` nos fluxos de login local e Google em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [X] T026 [US3] Integrar chamadas de auditoria nos fluxos de promoção de papéis e suspensão em `caderno-leitura-0.1/backend/app/routers/admin.py`
- [X] T027 [US3] Criar endpoint administrativo `GET /api/admin/audit-logs` com paginação e filtros em `caderno-leitura-0.1/backend/app/routers/admin.py`

**Checkpoint**: Trilha de auditoria ativa em todos os subsistemas de identidade e administração.

---

## Phase 6: User Story 4 - Ciclo de Vida da Conta: Desativação Temporária e Exclusão Definitiva (Priority: P3)

**Goal**: Permitir ao titular desativar sua conta (com reativação explícita no login mediante confirmação - Opção B) ou excluí-la definitivamente em cascata física transacional no SQLite (Opção A).

**Independent Test**: Desativar conta e validar revogação de sessões e status desativado; testar login que dispara modal de reativação explícita; solicitar exclusão definitiva com senha e validar eliminação física total sem quebra de integridade referencial (`PRAGMA foreign_key_check`).

### Tests for User Story 4
- [X] T028 [P] [US4] Criar testes de desativação, reativação explícita e exclusão em cascata em `caderno-leitura-0.1/backend/tests/test_account_lifecycle.py`

### Implementation for User Story 4
- [X] T029 [P] [US4] Criar schemas Pydantic para desativação, reativação e exclusão em `caderno-leitura-0.1/backend/app/schemas/account.py`
- [X] T030 [US4] Implementar serviço de ciclo de vida da conta com desativação, reativação e purga física em cascata em `caderno-leitura-0.1/backend/app/services/account_service.py`
- [X] T031 [US4] Criar endpoints `POST /api/account/deactivate`, `POST /api/account/reactivate` e `DELETE /api/account` em `caderno-leitura-0.1/backend/app/routers/account.py`
- [X] T032 [US4] Registrar router de conta em `caderno-leitura-0.1/backend/app/main.py`
- [X] T033 [US4] Criar modal de confirmação explícita de reativação de conta em `caderno-leitura-0.1/frontend/src/components/settings/ReactivateAccountModal.vue`
- [X] T034 [US4] Integrar tratamento de conta desativada e abertura de modal de reativação em `caderno-leitura-0.1/frontend/src/views/LoginView.vue`
- [X] T035 [US4] Implementar seção de gerenciamento de conta com botões e modais de desativação e exclusão em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`

**Checkpoint**: Ciclo de vida completo implementado com garantia dos direitos do titular (LGPD).

---

## Phase 7: User Story 5 - Portabilidade e Exportação Completa de Dados do Titular (Priority: P4)

**Goal**: Permitir ao leitor baixar pacote ZIP completo com acervo organizado em pastas Markdown (`[Livro]/[Capítulo]/[Estudo].md`) e arquivo `dados_acervo.json` consolidado (Opção A).

**Independent Test**: Chamar endpoint de exportação para um usuário com acervo populado e certificar que o arquivo ZIP gerado contém a árvore de pastas esperada e JSON válido.

### Tests for User Story 5
- [X] T036 [P] [US5] Criar testes de compilação e integridade do pacote ZIP de exportação em `caderno-leitura-0.1/backend/tests/test_account_export.py`

### Implementation for User Story 5
- [X] T037 [US5] Estender serviço de exportação para empacotar pastas Markdown e `dados_acervo.json` em `caderno-leitura-0.1/backend/app/services/export_service.py`
- [X] T038 [US5] Criar endpoint de download de portabilidade `GET /api/account/export` com streaming em `caderno-leitura-0.1/backend/app/routers/account.py`
- [X] T039 [US5] Adicionar botão de download do acervo completo (ZIP) com estado de progresso em `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`

**Checkpoint**: Todas as 5 User Stories da Feature 10 implementadas e independentemente testáveis.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Testes integrados, auditoria de integridade, documentação e conformidade

- [X] T040 [P] Criar testes de interface para fluxos de reativação, desativação e botão Google em `caderno-leitura-0.1/frontend/tests/security_lifecycle.test.mjs`
- [X] T041 Executar suíte de testes de backend (`pytest backend/tests`) garantindo 100% de aprovação sem banco ativo
- [X] T042 Executar testes de frontend (`npm test`) e compilação TypeScript/Vite (`npm run build`)
- [X] T043 Atualizar registro histórico de sessão em `docs/contexto/RETOMADA.md` e `caderno-leitura-0.1/docs/contexto/RETOMADA.md`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA todas as User Stories.
- **User Story 1 (Phase 3)**: Depende de Phase 2 — MVP de segurança.
- **User Story 2 (Phase 4)**: Depende de Phase 2 — Google OAuth 2.0.
- **User Story 3 (Phase 5)**: Depende de Phase 2 — Trilha de Auditoria.
- **User Story 4 (Phase 6)**: Depende de Phase 2 — Ciclo de Vida da Conta.
- **User Story 5 (Phase 7)**: Depende de Phase 2 — Portabilidade e Exportação.
- **Polish (Phase 8)**: Depende de todas as User Stories concluídas.

### Parallel Opportunities
- T001, T002 e T003 podem ser executados em paralelo na Fase 1.
- T005, T008 podem ser desenvolvidos em paralelo na Fase 2.
- Testes T010 e T011 podem rodar em paralelo na Fase 3.
- Testes T016, T023, T028 e T036 podem ser desenvolvidos em paralelo aos seus respectivos serviços.

---

## Implementation Strategy

### MVP First (User Story 1)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 - Rate Limiting e Prevenção de Força Bruta).
3. Validar via `pytest backend/tests/test_rate_limit.py` e `test_auth_anti_enumeration.py`.

### Incremental Delivery
1. Setup + Foundation $\rightarrow$ Infraestrutura pronta.
2. User Story 1 $\rightarrow$ Rate Limiting e OWASP ativo (MVP).
3. User Story 2 $\rightarrow$ Login com Google instantâneo.
4. User Story 3 $\rightarrow$ Auditoria sem segredos.
5. User Story 4 $\rightarrow$ Desativação e exclusão física definitiva.
6. User Story 5 $\rightarrow$ Portabilidade e exportação ZIP.
7. Polish $\rightarrow$ Validação de suítes completas e documentação de retomada.
