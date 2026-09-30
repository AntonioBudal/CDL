# Tasks: F0.6.6 — Apoie o Leitorum

**Branch**: `045-apoie-o-leitorum`  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estrutura inicial e definições de contratos de tipos e esquemas compartilhados

- [X] T001 Definir interfaces TypeScript para configurações e dados de apoio em `caderno-leitura-0.1/frontend/src/types.ts`
- [X] T002 [P] Criar esquemas Pydantic para respostas pública, administrativa e payload de atualização em `caderno-leitura-0.1/backend/app/schemas/support_setting.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de persistência, modelo relacional e serviços base que bloqueiam todas as histórias de usuário

- [X] T003 Criar modelo SQLAlchemy `SupportSetting` em `caderno-leitura-0.1/backend/app/models/support_setting.py` e registrar em `caderno-leitura-0.1/backend/app/models/__init__.py`
- [X] T004 Criar migração Alembic para a tabela `support_settings` em `caderno-leitura-0.1/backend/migrations/versions/0022_add_support_settings.py`
- [X] T005 Criar serviço de apoio `SupportService` com fallback híbrido (banco de dados e `.env`) em `caderno-leitura-0.1/backend/app/services/support_service.py`
- [X] T006 [P] Criar métodos de consumo HTTP para consulta pública e gestão administrativa em `caderno-leitura-0.1/frontend/src/services/api.ts`

**Checkpoint**: Fundação pronta — implementação das histórias de usuário pode iniciar de forma independente.

---

## Phase 3: User Story 1 - Consulta da Página de Apoio e Contribuição via PIX (Priority: P1) [MVP]

**Goal**: Disponibilizar rota pública `/apoie` com apresentação institucional, dados de PIX e botão de cópia de chave com feedback imediato.

**Independent Test**: Acessar `/apoie` no navegador; visualizar chave PIX, titular e QR Code; clicar em "Copiar Chave PIX"; constatar que o texto foi para a área de transferência e o feedback visual foi exibido.

### Tests for User Story 1
- [X] T007 [P] [US1] Criar testes de integração para o endpoint público `GET /api/support` e fallback de ambiente em `caderno-leitura-0.1/backend/tests/test_support_settings.py`

### Implementation for User Story 1
- [X] T008 [US1] Implementar endpoint público `GET /api/support` em `caderno-leitura-0.1/backend/app/routers/support.py` e registrar em `caderno-leitura-0.1/backend/app/main.py`
- [X] T009 [P] [US1] Criar view pública `SupportView.vue` em `caderno-leitura-0.1/frontend/src/views/SupportView.vue` com apresentação de PIX, QR Code, botão de cópia de um clique e alvos de toque de 44px
- [X] T010 [US1] Registrar rota canônica `/apoie` e alias `/apoiar` com `meta: { public: true }` em `caderno-leitura-0.1/frontend/src/router/index.ts`

**Checkpoint**: MVP entregue — qualquer visitante pode consultar a página de apoio e copiar a chave PIX voluntariamente.

---

## Phase 4: User Story 2 - Acesso Discreto e Elegante via Rodapé da Aplicação (Priority: P2)

**Goal**: Garantir que o link para a página de apoio seja acessível exclusivamente pelo rodapé das páginas e pelo menu móvel, preservando a imersão e o foco do estudo.

**Independent Test**: Navegar pelo Dashboard e Acervo; verificar ausência de abas de doação no menu superior; rolar até o rodapé e acionar o link "Apoie o Leitorum" para acessar `/apoie`.

### Tests for User Story 2
- [X] T011 [P] [US2] Criar teste automatizado verificando a presença do link de apoio no rodapé em `caderno-leitura-0.1/frontend/test/footer-support.test.js`

### Implementation for User Story 2
- [X] T012 [US2] Integrar link discreto "Apoie o Leitorum" no componente `<footer class="app-footer">` em `caderno-leitura-0.1/frontend/src/App.vue`
- [X] T013 [US2] Adicionar link "Apoie o Leitorum" na gaveta de navegação secundária em `caderno-leitura-0.1/frontend/src/components/navigation/MobileMoreMenu.vue`

**Checkpoint**: Navegação discreta e harmoniosa integrada em toda a aplicação sem poluição visual.

---

## Phase 5: User Story 3 - Suporte a Link Alternativo e Gestão Administrativa (Priority: P3)

**Goal**: Permitir que administradores gerenciem os dados de apoio diretamente pelo painel `/admin`, com suporte a links externos (Google Pay) e rastreabilidade por logs de auditoria.

**Independent Test**: Fazer login como administrador; acessar `/admin`; abrir aba "Apoio e Doações"; preencher nova chave PIX e link Google Pay; salvar; conferir que o endpoint público reflete imediatamente os dados alterados.

### Tests for User Story 3
- [X] T014 [P] [US3] Criar testes automatizados para endpoints `GET /api/admin/support` e `PUT /api/admin/support` validando autorização RBAC e auditoria em `caderno-leitura-0.1/backend/tests/test_support_settings.py`

### Implementation for User Story 3
- [X] T015 [US3] Implementar endpoints `GET /api/admin/support` e `PUT /api/admin/support` com verificação de perfil `AdminUser` e registro em `audit_logs` em `caderno-leitura-0.1/backend/app/routers/admin.py`
- [X] T016 [P] [US3] Implementar botão de pagamento alternativo (Google Pay/Link externo) com abertura segura em nova janela em `caderno-leitura-0.1/frontend/src/views/SupportView.vue`
- [X] T017 [US3] Criar aba de configuração de apoio no painel de controle em `caderno-leitura-0.1/frontend/src/views/AdminView.vue`

**Checkpoint**: Ciclo completo de gestão administrativa e opções multimeios de apoio concluído.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Acessibilidade, ergonomia móvel, conformidade estrita sem emojis e validação completa

- [X] T018 [P] Garantir conformidade com ausência total de emojis no código e na interface visual em `SupportView.vue`, `AdminView.vue` e `App.vue`
- [X] T019 [P] Garantir alvos de toque mínimos de 44x44px, contraste WCAG AA e navegação por teclado em `SupportView.vue`
- [X] T020 Executar suite completa de testes automatizados (`pytest tests/test_support_settings.py`, `npm test` e `npm run build`)
- [X] T021 Executar verificação dos cenários de validação descritos em `specs/045-apoie-o-leitorum/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — inicia imediatamente.
- **Foundational (Phase 2)**: Depende da conclusão do Setup — BLOQUEIA as histórias de usuário.
- **User Stories (Phase 3+)**: Dependem da Fase 2 (Foundational).
  - Ordem sequencial: US1 (MVP) → US2 (Navegação no Rodapé) → US3 (Gestão Admin e Meio Alternativo).
- **Polish (Phase 6)**: Depende da conclusão das histórias.

### Parallel Opportunities

- `T001` (Typescript) e `T002` (Pydantic) podem rodar em paralelo no Setup.
- `T007` (Testes backend US1) e `T009` (Componente visual US1) podem ser desenvolvidos em paralelo.
- `T014` (Testes backend admin) e `T016` (Botão alternativo no frontend) podem ser desenvolvidos em paralelo.
- `T018` e `T019` podem ser validados em paralelo durante o Polish.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Phase 1 (Setup) e Phase 2 (Foundational).
2. Concluir Phase 3 (User Story 1 - Rota `/apoie`, consulta pública e cópia de chave PIX).
3. **VALIDAR**: Acessar `/apoie`, verificar chave PIX e testar botão de cópia.

### Incremental Delivery

1. Setup + Foundational → Base pronta.
2. User Story 1 → Página pública `/apoie` com PIX e cópia (MVP).
3. User Story 2 → Links de acesso discretos no rodapé e menu móvel.
4. User Story 3 → Aba de gestão no painel `/admin`, link Google Pay e auditoria.
5. Polish → Verificação de acessibilidade, zero emojis e build limpo.
