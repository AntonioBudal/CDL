# Tasks: F0.6.9 — Segurança de Aplicação e Dados

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md), [contracts/security-headers-api.yaml](./contracts/security-headers-api.yaml)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura inicial, schemas Pydantic, tipagens TypeScript e configurações compartilhadas de segurança

- [x] T001 Criar schema Pydantic `SecurityErrorResponse` em `caderno-leitura-0.1/backend/app/schemas/security.py`
- [x] T002 [P] Criar tipagens TypeScript para contratos de segurança em `caderno-leitura-0.1/frontend/src/types/security.ts`
- [x] T003 [P] Configurar helpers de resolução de CORS e variáveis de ambiente em `caderno-leitura-0.1/backend/app/core/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de middleware, sanitizador base e manipulador de exceções que bloqueiam as histórias de usuário

- [x] T004 Implementar módulo de sanitização leve e estrita de HTML em `caderno-leitura-0.1/frontend/src/services/sanitizer.ts`
- [x] T005 [P] Implementar middleware HTTP para injeção de Security Headers e Content-Security-Policy em `caderno-leitura-0.1/backend/app/core/security_headers.py`
- [x] T006 [P] Configurar registro de middleware CORS controlado por `CADERNO_CORS_ORIGINS` em `caderno-leitura-0.1/backend/app/main.py`
- [x] T007 Implementar manipulador global de exceções 500 com rastreamento por `error_id` em `caderno-leitura-0.1/backend/app/errors.py`
- [x] T008 [P] Criar suíte de testes de isolamento para cabeçalhos e CSP em `caderno-leitura-0.1/backend/tests/test_security_headers_and_csp.py`

**Checkpoint**: Fundação pronta — implementação das histórias de usuário pode prosseguir de forma independente.

---

## Phase 3: User Story 1 - Imunização contra XSS e Sanitização Robusta de Conteúdo (Priority: P1) 🎯 MVP

**Goal**: Garantir que nenhum texto, nota, fichamento importado ou link malicioso execute scripts no navegador, preservando integralmente os componentes de leitura ativa.

**Independent Test**: Submeter payloads XSS clássicos e modernos (tags `<script>`, atributos `on*`, links `javascript:`) e verificar que são neutralizados na renderização sem disparar scripts e mantendo os nós de leitura ativa (`.study-occlusion`, `.study-highlight`, etc.) funcionais.

- [x] T009 [P] [US1] Criar testes automatizados de sanitização de HTML e URLs no frontend em `caderno-leitura-0.1/frontend/tests/security_xss_sanitization.test.mjs`
- [x] T010 [US1] Configurar validação estrita de links (`validateLink`) no parser Markdown em `caderno-leitura-0.1/frontend/src/services/markdown.ts`
- [x] T011 [US1] Integrar camada de sanitização antes da atribuição a `v-html` em `caderno-leitura-0.1/frontend/src/components/MarkdownContent.vue`
- [x] T012 [P] [US1] Criar testes de validação defensiva contra injeção de scripts em payloads de importação no backend em `caderno-leitura-0.1/backend/tests/test_security_xss_backend.py`

**Checkpoint**: User Story 1 (MVP) concluída — Leitorum 100% imune a injeções de script no leitor de estudos e no editor.

---

## Phase 4: User Story 2 - Cabeçalhos HTTP de Segurança e Política CORS Restrita (Priority: P2)

**Goal**: Injetar cabeçalhos de segurança consagrados em 100% das respostas HTTP do servidor (CSP em modo Enforce, nosniff, Referrer, Permissions e Frame Options) e restringir CORS para arquitetura same-origin.

**Independent Test**: Inspecionar respostas HTTP de rotas públicas e da API para certificar presença obrigatória de todos os cabeçalhos de proteção e bloqueio de requisições CORS de origens não autorizadas.

- [x] T013 [P] [US2] Implementar testes de integração para todos os Security Headers e diretivas CSP em `caderno-leitura-0.1/backend/tests/test_security_headers_and_csp.py`
- [x] T014 [US2] Integrar `SecurityHeadersMiddleware` na inicialização da aplicação FastAPI em `caderno-leitura-0.1/backend/app/main.py`
- [x] T015 [US2] Configurar diretivas CSP compatíveis com Google Identity, Google Fonts e Vue em `caderno-leitura-0.1/backend/app/core/security_headers.py`
- [x] T016 [P] [US2] Criar testes de integração validando comportamento restrito do CORS em `caderno-leitura-0.1/backend/tests/test_security_cors.py`

**Checkpoint**: User Story 2 concluída — Servidor HTTP blindado com cabeçalhos de segurança em conformidade com as diretivas OWASP.

---

## Phase 5: User Story 3 - Mascaramento de Erros do Backend, Auditoria de Queries e Blindagem de Segredos (Priority: P3)

**Goal**: Mascarar falhas 500 do backend com resposta genérica e `error_id` UUID, comprovar imunidade a injeção SQL e bloquear acesso estático a arquivos internos de infraestrutura.

**Independent Test**: Provocar uma exceção não tratada e verificar que o JSON de resposta oculta stack traces e inclui `error_id`; submeter sequências de injeção SQL e confirmar que são tratadas como literais; e requisitar arquivos como `.env` e `caderno.db` confirmando resposta 404.

- [x] T017 [P] [US3] Criar testes de integração para mascaramento de falhas 500 e correlação de logs em `caderno-leitura-0.1/backend/tests/test_security_error_masking.py`
- [x] T018 [US3] Conectar o exception handler global 500 com geração de UUID e log defensivo em `caderno-leitura-0.1/backend/app/errors.py` e `caderno-leitura-0.1/backend/app/main.py`
- [x] T019 [P] [US3] Criar suíte de testes de estresse contra injeção SQL em rotas de busca, filtros e parâmetros em `caderno-leitura-0.1/backend/tests/test_security_sql_injection.py`
- [x] T020 [US3] Implementar bloqueio estrito de arquivos sensíveis e ocultos na camada estática em `caderno-leitura-0.1/backend/app/frontend.py`
- [x] T021 [P] [US3] Criar testes de bloqueio de arquivos de infraestrutura e prevenção de path traversal em `caderno-leitura-0.1/backend/tests/test_security_static_blocking.py`
- [x] T022 [US3] Implementar auditoria defensiva de `CADERNO_SESSION_SECRET` na rotina de lifespan em `caderno-leitura-0.1/backend/app/main.py`

**Checkpoint**: Todas as três histórias de usuário implementadas e verificadas de ponta a ponta.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação holística de conformidade, execução dos cenários de teste e garantia de 100% de testes verdes

- [x] T023 [P] Executar e validar todos os cenários de segurança descritos em `specs/048-seguranca-aplicacao-dados/quickstart.md`
- [x] T024 Executar suíte completa de testes do backend (`pytest`), do frontend (`npm test`) e compilação de produção (`npm run build`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — execução imediata.
- **Foundational (Phase 2)**: Depende do Setup — bloqueia as histórias de usuário.
- **User Story 1 (Phase 3)**: Depende da Fundação (Phase 2) — foco MVP no cliente e parser.
- **User Story 2 (Phase 4)**: Depende da Fundação (Phase 2) — foco no servidor HTTP e cabeçalhos.
- **User Story 3 (Phase 5)**: Depende da Fundação (Phase 2) — foco em exceções, dados e arquivos estáticos.
- **Polish (Phase 6)**: Depende da conclusão de todas as histórias de usuário.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 — Imunização contra XSS).
3. Validar de forma independente a renderização e leitura ativa.

### Incremental Delivery
1. Setup + Foundational → Infraestrutura base pronta.
2. User Story 1 → Proteção contra XSS e sanitização no frontend.
3. User Story 2 → Proteção via cabeçalhos HTTP e CSP no backend.
4. User Story 3 → Mascaramento de erros 500, testes SQLi e bloqueio de arquivos.
5. Polish → Verificação holística e commit atômico sob governança (**1 Feature = 1 Commit**).
