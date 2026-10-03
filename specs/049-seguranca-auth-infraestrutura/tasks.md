# Tasks: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/auth-security-api.yaml](./contracts/auth-security-api.yaml)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estruturas básicas de schema, tipagens e parâmetros de configuração para rate limiting e segurança

- [x] T001 Criar schema Pydantic `RateLimitExceededResponse` em `caderno-leitura-0.1/backend/app/schemas/security.py`
- [x] T002 [P] Configurar constantes e variáveis de ambiente de rate limit em `caderno-leitura-0.1/backend/app/core/config.py` (`CADERNO_AUTH_MAX_ATTEMPTS_PER_MINUTE`, `CADERNO_AUTH_MAX_CONSECUTIVE_FAILURES`, `CADERNO_AUTH_FAILURE_LOCKOUT_SECONDS`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de identificação segura de IP do cliente e rastreamento de falhas que bloqueiam as histórias de usuário

- [x] T003 Implementar extração e sanitização robusta de IP do cliente com suporte a `CF-Connecting-IP`, `X-Forwarded-For` e validação sintática em `caderno-leitura-0.1/backend/app/core/rate_limiter.py`
- [x] T004 [P] Implementar rastreador em memória de falhas consecutivas de autenticação `AuthFailureTracker` em `caderno-leitura-0.1/backend/app/core/rate_limiter.py`
- [x] T005 [P] Criar testes de integração e validação sintática para extração de IP de proxies em `caderno-leitura-0.1/backend/tests/test_security_proxy_ip_extraction.py`

**Checkpoint**: Fundação pronta — implementação das histórias de usuário pode prosseguir de forma independente.

---

## Phase 3: User Story 1 - Mitigação de Força Bruta e Proteção contra Abuso via Rate Limiting (Priority: P1) 🎯 MVP

**Goal**: Bloquear por 60 segundos IPs com 5 falhas consecutivas de login em 1 minuto e aplicar teto global de 30 req/min nas rotas de autenticação, emitindo HTTP 429 e `Retry-After: 60`, sem impactar a leitura legítima.

**Independent Test**: Submeter 5 tentativas com senha inválida a partir do mesmo IP e constatar que a 5ª tentativa retorna status 429 com cabeçalho `Retry-After: 60`, enquanto requisições de leitura em `/api/studies` ou `/api/books` continuam respondendo 200 normalmente.

- [x] T006 [P] [US1] Criar suíte de testes de integração para rate limiting, bloqueio escalonado e `Retry-After` em `caderno-leitura-0.1/backend/tests/test_security_rate_limiting.py`
- [x] T007 [US1] Integrar registro de falha (`record_auth_failure`) e reset de sucesso (`reset_auth_failures`) no fluxo de login em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [x] T008 [US1] Aplicar dependência de rate limit nos endpoints de registro (`/api/auth/register`), autenticação Google (`/api/auth/google`) e reativação em `caderno-leitura-0.1/backend/app/routers/auth.py`
- [x] T009 [P] [US1] Implementar interceptor defensivo para respostas HTTP 429 no cliente HTTP do frontend em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: User Story 1 (MVP) concluída — Sistema imune a força bruta de credenciais e flooding em rotas de autenticação.

---

## Phase 4: User Story 2 - Blindagem de Sessões, Cookies Seguros e Invalidação Efetiva (Priority: P2)

**Goal**: Garantir que cookies de sessão possuam atributos `HttpOnly`, `SameSite=Lax`, diretiva `Secure` adaptativa e invalidação definitiva no servidor após o logout.

**Independent Test**: Realizar login e verificar presença de `HttpOnly`, `SameSite=Lax` e `Secure` (quando em HTTPS/`X-Forwarded-Proto`). Executar logout e verificar que a sessão no SQLite é deletada e o token antigo recebe 401 em chamadas subsequentes.

- [x] T010 [P] [US2] Criar suíte de testes de integração para governança de cookies e ciclo de vida de sessão em `caderno-leitura-0.1/backend/tests/test_security_cookies_and_sessions.py`
- [x] T011 [US2] Aprimorar helper adaptativo `resolve_cookie_secure` com suporte a `CF-Visitor` e `X-Forwarded-Proto` em `caderno-leitura-0.1/backend/app/services/session_service.py`
- [x] T012 [US2] Reforçar remoção atômica de sessão no banco e instruções de exclusão de cookie no logout em `caderno-leitura-0.1/backend/app/services/session_service.py` e `caderno-leitura-0.1/backend/app/routers/auth.py`
- [x] T013 [US2] Validar geração de novo token opaco em cada login bem-sucedido para prevenção de fixação de sessão em `caderno-leitura-0.1/backend/app/routers/auth.py`

**Checkpoint**: User Story 2 concluída — Gerenciamento de sessão inviolável e conforme as diretrizes OWASP.

---

## Phase 5: User Story 3 - Integridade da Fronteira com Proxy Reverso e Proteção de Recursos Privados (Priority: P3)

**Goal**: Proteger recursos restritos e backups contra acesso não autorizado e assegurar que o isolamento multiusuário seja estritamente aplicado.

**Independent Test**: Submeter requisições para `/api/backups` sem credenciais e com credenciais de usuário comum, confirmando retorno de status 401 e 403 respectivamente, permitindo acesso apenas para `admin`.

- [x] T014 [P] [US3] Criar testes de controle de acesso para endpoints privilegiados e recursos de infraestrutura em `caderno-leitura-0.1/backend/tests/test_security_privileged_access.py`
- [x] T015 [US3] Auditar e reforçar validação de permissões administrativas no router de backups em `caderno-leitura-0.1/backend/app/routers/backups.py`
- [x] T016 [US3] Verificar e blindar isolamento de propriedade de usuário em downloads e exportações de dados em `caderno-leitura-0.1/backend/app/routers/account.py`

**Checkpoint**: Todas as três histórias de usuário implementadas e verificadas de ponta a ponta.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação holística de conformidade, execução dos cenários de teste e garantia de 100% de testes verdes

- [x] T017 [P] Executar e validar todos os cenários de segurança descritos em `specs/049-seguranca-auth-infraestrutura/quickstart.md`
- [x] T018 Executar suíte completa de testes do backend (`pytest`), do frontend (`npm test`) e compilação de produção (`npm run build`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende da Fundação (Phase 2) — foco MVP no rate limit e proteção de força bruta.
- **User Story 2 (Phase 4)**: Depende da Fundação (Phase 2) — foco nos cookies e ciclo de vida de sessão.
- **User Story 3 (Phase 5)**: Depende da Fundação (Phase 2) — foco na blindagem de recursos privilegiados (RBAC).
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 — Rate Limiting e Mitigação de Força Bruta).
3. Validar de forma independente a resposta 429 e o cabeçalho `Retry-After: 60`.

### Incremental Delivery
1. Setup + Foundational → Infraestrutura base e extração confiável de IP de proxy.
2. User Story 1 → Rate limiting volumétrico e mitigação de força bruta.
3. User Story 2 → Governança de cookies de sessão adaptativos e revogação no logout.
4. User Story 3 → Proteção de recursos privilegiados e auditoria de RBAC.
5. Polish → Verificação holística e commit atômico sob governança (**1 Feature = 1 Commit**).
