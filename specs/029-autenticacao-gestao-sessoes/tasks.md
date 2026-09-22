# Tasks: Autenticação e Gestão de Sessões (F02)

**Feature**: `029-autenticacao-gestao-sessoes`  
**Input**: Design artifacts from `specs/029-autenticacao-gestao-sessoes/` (`spec.md`, `plan.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`)  

---

## Phase 1: Setup (Infraestrutura Criptográfica e Modelos)

**Purpose**: Instalação de bibliotecas criptográficas, utilitários centrais de segurança e estruturas declarativas ORM.

- [X] T001 Adicionar dependência argon2-cffi em backend/requirements.in e backend/requirements.txt
- [X] T002 [P] Implementar módulo de segurança criptográfica com Argon2id e hashing de tokens em backend/app/core/security.py
- [X] T003 [P] Implementar utilitário de formatação amigável de dispositivos e clientes a partir do User-Agent em backend/app/core/user_agent.py
- [X] T004 [P] Adicionar configurações de sessão, expiração de 30 dias, throttle de atividade e chave ALLOW_REGISTRATION em backend/app/core/config.py
- [X] T005 [P] Criar modelo de dados SQLAlchemy LocalCredential em backend/app/models/local_credential.py
- [X] T006 [P] Criar modelo de dados SQLAlchemy UserSession em backend/app/models/user_session.py
- [X] T007 Atualizar modelo User para incluir colunas email, role e relacionamentos com credenciais e sessões em backend/app/models/user.py
- [X] T008 Registrar novos modelos LocalCredential e UserSession na exportação em backend/app/models/__init__.py
- [X] T009 [P] Criar schemas Pydantic de autenticação, credenciais e sessões em backend/app/schemas/auth.py

---

## Phase 2: Foundational (Migração Alembic e Serviço Central de Sessões)

**Purpose**: Estruturação do banco de dados, regras de persistência de sessão e injeção de dependência via cookies.

- [X] T010 Criar migração Alembic 0012_add_credentials_and_sessions.py com batch_alter_table para users e criação de local_credentials e user_sessions com índices em backend/migrations/versions/0012_add_credentials_and_sessions.py
- [X] T011 [P] Implementar serviço central de sessões com criação de tokens opacos, hash SHA-256, cálculo de expiração e throttling de atividade em backend/app/services/session_service.py
- [X] T012 Atualizar injeção de dependência get_current_user para validar cookie caderno_session, atualizar atividade deslizante e manter fallback retrocompatível de testes em backend/app/dependencies.py
- [X] T013 [P] Criar suíte de testes unitários de hash e verificação Argon2id em backend/tests/test_password_security.py

---

## Phase 3: User Story 1 - Autenticação por Credenciais Locais e Acesso Protegido (Priority: P1) 🎯 MVP

**Goal**: Permitir que usuários autentiquem-se informando credenciais locais e recebam cookie seguro de sessão, protegendo as rotas da aplicação contra acessos não autorizados.

**Independent Test**: Tentar acessar endpoints protegidos sem cookie e receber HTTP 401; em seguida, enviar POST /api/auth/login com credenciais válidas, receber cookie caderno_session e constatar sucesso ao consultar GET /api/auth/me.

### Tests for User Story 1
- [X] T014 [P] [US1] Criar testes automatizados de autenticação local (login válido, senha incorreta, anti-fixação de sessão e bloqueio anônimo) em backend/tests/test_session_lifecycle.py

### Implementation for User Story 1
- [X] T015 [US1] Implementar endpoint POST /api/auth/login com validação de senha Argon2id, criação de sessão e emissão de cookie seguro em backend/app/routers/auth.py
- [X] T016 [P] [US1] Implementar endpoint GET /api/auth/me retornando dados do usuário e ID da sessão ativa em backend/app/routers/auth.py
- [X] T017 [P] [US1] Adicionar métodos de autenticação (login, getMe) no cliente API do frontend em frontend/src/services/api.ts
- [X] T018 [US1] Criar store reativa de autenticação (useAuthStore) gerenciando estado do usuário, sessão e métodos de autenticação em frontend/src/stores/auth.ts
- [X] T019 [US1] Criar tela de autenticação responsiva LoginView.vue com feedback de validação em frontend/src/views/LoginView.vue
- [X] T020 [US1] Configurar rota /login e guardas de navegação no Vue Router (router.beforeEach) redirecionando não autenticados em frontend/src/router/index.ts

---

## Phase 4: User Story 2 - Definição da Senha Inicial do Proprietário Canônico (Priority: P1)

**Goal**: Garantir que o usuário proprietário canônico legado, provisionado sem senha na F01, seja conduzido a um assistente obrigatório de primeiro acesso para cadastrar sua senha mestra com total segurança.

**Independent Test**: Inicializar o sistema com banco contendo a conta canônica sem senha; consultar GET /api/auth/config e verificar owner_setup_required == true; enviar POST /api/auth/setup-owner com senha válida, receber cookie de sessão e verificar bloqueio permanente de novas chamadas a este endpoint (HTTP 403).

#### Tests for User Story 2
- [X] T021 [P] [US2] Criar testes automatizados do fluxo de primeiro acesso do proprietário canônico em backend/tests/test_session_lifecycle.py

### Implementation for User Story 2
- [X] T022 [US2] Implementar endpoint GET /api/auth/config expondo flags owner_setup_required e allow_registration em backend/app/routers/auth.py
- [X] T023 [US2] Implementar endpoint POST /api/auth/setup-owner com validação de senha de no mínimo 8 caracteres e trava definitiva após primeiro uso em backend/app/routers/auth.py
- [X] T024 [P] [US2] Adicionar métodos getAuthConfig e setupOwner no cliente API do frontend em frontend/src/services/api.ts
- [X] T025 [US2] Criar tela de assistente de primeiro acesso SetupOwnerView.vue em frontend/src/views/SetupOwnerView.vue
- [X] T026 [US2] Integrar redirecionamento automático para /primeiro-acesso no guard do Vue Router quando owner_setup_required for verdadeiro em frontend/src/router/index.ts

---

## Phase 5: User Story 3 - Cadastro de Novos Usuários na Rede Local (Priority: P1)

**Goal**: Possibilitar a criação de novas contas independentes por meio de formulário de auto-registro (quando habilitado por configuração), permitindo múltiplos perfis isolados no mesmo servidor.

**Independent Test**: Com ALLOW_REGISTRATION habilitado, enviar requisição de cadastro para POST /api/auth/register e verificar que uma nova conta isolada é criada com sessão ativa iniciada; com a flag desabilitada, verificar que a requisição de cadastro é recusada.

### Tests for User Story 3
- [X] T027 [P] [US3] Criar testes automatizados de cadastro de novos usuários e bloqueio quando desativado em backend/tests/test_session_lifecycle.py

### Implementation for User Story 3
- [X] T028 [US3] Implementar endpoint POST /api/auth/register validando unicidade de username/email, criando credencial Argon2id e sessão em backend/app/routers/auth.py
- [X] T029 [P] [US3] Adicionar método register no cliente API do frontend em frontend/src/services/api.ts
- [X] T030 [US3] Criar tela de cadastro de novos leitores RegisterView.vue em frontend/src/views/RegisterView.vue
- [X] T031 [US3] Adicionar rota /registro no Vue Router e exibir link condicional de cadastro na tela de login em frontend/src/router/index.ts e frontend/src/views/LoginView.vue

---

## Phase 6: User Story 4 - Gerenciamento e Revogação de Sessões e Dispositivos Conectados (Priority: P2)

**Goal**: Permitir que o leitor visualize a lista completa de sessões conectadas à sua conta com nomes de dispositivo amigáveis e revogue o acesso de qualquer dispositivo remotamente.

**Independent Test**: Autenticar o mesmo usuário com dois User-Agents diferentes; consultar GET /api/auth/sessions e verificar as 2 sessões com is_current correto; revogar uma sessão remota via DELETE /api/auth/sessions/{id} e comprovar que requisições subsequentes com aquele cookie recebem HTTP 401.

### Tests for User Story 4
- [X] T032 [P] [US4] Criar testes automatizados de listagem de sessões, identificação de dispositivos e revogação remota anti-IDOR em backend/tests/test_device_management.py

### Implementation for User Story 4
- [X] T033 [US4] Implementar endpoint GET /api/auth/sessions listando todas as sessões ativas do usuário conectado em backend/app/routers/auth.py
- [X] T034 [US4] Implementar endpoint DELETE /api/auth/sessions/{id} com validação de propriedade e retorno HTTP 404 anti-IDOR para sessões alheias em backend/app/routers/auth.py
- [X] T035 [P] [US4] Adicionar métodos getSessions e revokeSession no cliente API do frontend em frontend/src/services/api.ts
- [X] T036 [US4] Criar painel de dispositivos conectados e sessões ativas com ação de revogação na página de Ajustes em frontend/src/views/SettingsView.vue

---

## Phase 7: User Story 5 - Encerramento Seguro de Sessão (Logout Pontual e Global) (Priority: P1)

**Goal**: Permitir o logout seguro em dispositivos compartilhados através da destruição da sessão no servidor e limpeza de cookies no navegador, além de possibilitar o encerramento em massa de outras sessões ativas.

**Independent Test**: Enviar POST /api/auth/logout e validar que o cookie caderno_session é limpo com Max-Age=0 e a sessão é removida do SQLite; testar POST /api/auth/logout-all e confirmar que todas as outras sessões são revogadas, mantendo apenas a atual.

### Tests for User Story 5
- [X] T037 [P] [US5] Criar testes automatizados de logout pontual e comando logout-all em backend/tests/test_session_lifecycle.py e backend/tests/test_device_management.py

### Implementation for User Story 5
- [X] T038 [US5] Implementar endpoint POST /api/auth/logout destruindo a sessão no banco e limpando o cookie no navegador em backend/app/routers/auth.py
- [X] T039 [US5] Implementar endpoint POST /api/auth/logout-all revogando todas as demais sessões ativas do usuário em backend/app/routers/auth.py
- [X] T040 [P] [US5] Adicionar métodos logout e logoutAll no cliente API do frontend em frontend/src/services/api.ts
- [X] T041 [US5] Atualizar cabeçalho da aplicação para exibir identificação do leitor conectado e botão de Logout em frontend/src/App.vue

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Limpeza periódica de sessões expiradas, validação completa de testes de regressão e compilação do frontend.

- [X] T042 [P] Implementar rotina de purga periódica de sessões expiradas no banco de dados em backend/app/services/session_service.py
- [X] T043 Executar suíte completa de testes do backend garantindo 100% de aprovação em backend/tests
- [X] T044 [P] Executar suíte de testes do frontend (npm test) e compilação de produção (npm run build) em frontend/
- [X] T045 Executar os cenários de validação descritos no guia quickstart.md em ambiente descartável

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências prévias — instala `argon2-cffi` e define modelos/schemas.
- **Foundational (Phase 2)**: Depende da conclusão de Setup — cria migração Alembic `0012` e serviço central de sessões. Bloqueia as User Stories.
- **User Story 1 (Phase 3 - MVP)**: Depende de Setup e Foundational. É o núcleo essencial de login com credenciais e cookies.
- **User Story 2 (Phase 4)**: Depende da Phase 3 (Login funcional). Fornece o assistente de primeiro acesso para definir a senha do proprietário.
- **User Story 3 (Phase 5)**: Depende da Phase 3 e Phase 4. Permite auto-registro de novos leitores.
- **User Story 4 (Phase 6)**: Depende da Phase 3 (sessões persistidas). Constrói o painel de dispositivos conectados nos Ajustes.
- **User Story 5 (Phase 7)**: Depende da Phase 3 e Phase 6. Implementa logout pontual e `logout-all`.
- **Polish (Phase 8)**: Depende da conclusão de todas as histórias.

### Parallel Opportunities

- Em Phase 1: `T002`, `T003`, `T004`, `T005`, `T006`, `T009` atuam em arquivos independentes e podem ser desenvolvidos em paralelo.
- Em Phase 2: `T011` e `T013` podem rodar em paralelo.
- Em Phase 3: `T014`, `T016`, `T017` podem rodar em paralelo antes da integração do frontend (`T018`, `T019`, `T020`).
- Em Phase 4: `T021` e `T024` atuam em arquivos separados.
- Em Phase 5: `T027` e `T029` atuam em arquivos separados.
- Em Phase 6: `T032` e `T035` atuam em arquivos separados.
- Em Phase 7: `T037` e `T040` atuam em arquivos separados.

---

## Implementation Strategy

### MVP First (Fases 1, 2 e 3)
1. Instalar `argon2-cffi`, modelar `LocalCredential` e `UserSession`, e aplicar migração `0012`.
2. Implementar `session_service.py` e atualizar dependência `CurrentUser` para ler cookies `HttpOnly`.
3. Implementar `POST /api/auth/login`, `GET /api/auth/me` e a tela `LoginView.vue` com guarda de navegação.

### Incremental Delivery
1. Adicionar o assistente de primeiro acesso para o proprietário legado (US2).
2. Adicionar o cadastro de novos usuários com auto-registro parametrizável (US3).
3. Adicionar o painel de sessões e revogação remota de dispositivos nos Ajustes (US4).
4. Adicionar logout pontual e comando `logout-all` (US5).
5. Executar suíte de validação completa do `quickstart.md` e compilação de produção.
