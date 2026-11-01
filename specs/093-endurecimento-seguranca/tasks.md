# Tasks — F0.10.02: Endurecimento de Segurança e Privacidade Verificável

**Input**: [spec.md](spec.md) (US1 a US6, FR-001 a FR-011, SC-001 a SC-005) e [plan.md](plan.md) (decisões 1 a 7).

**Status**: Concluídas em 2026-11-01.

Caminhos relativos a `C:\Users\User\caderno`; `B/` = `caderno-leitura-0.1/backend/`; `F/` =
`caderno-leitura-0.1/frontend/`.

**Regras em todas as tarefas**:
- **Dados:** só fictícios; sentinela `SENTINELA-093-FICTICIO`; bancos em `tmp_path`; navegador no servidor de
  validação (porta 8010).
- **Banco ativo:** nunca tocado; nenhum `alembic`.
- **Testes (diretiva de 2026-11-01):** esta é a 2ª feature do lote; valida com `npm run build` e os testes novos.
  Os testes de backend tocados (`test_security_headers_and_csp.py`, `test_seo_and_public_presence.py` e os novos)
  rodam isolados com `pytest -k`, porque cobrem diretamente o que muda. A suíte completa fica para o marco da 5ª
  feature.
- **Build:** nunca junto com o `pytest`.
- `[P]` = paralelizável com as outras `[P]` da mesma fase.

---

## Phase 1: Testes primeiro

- [x] T001 [P] `B/tests/test_security_hardening.py`: CSP com e sem Google, `Referrer-Policy`, rotas públicas do
  `X-Robots-Tag`, os 7 casos de origem do plano e o `security.txt`. Rodar e ver falhar.
- [x] T002 [P] `B/tests/test_secure_delete.py`: pragma `secure_delete` = 1 em conexão nova; sentinela some do `.db`
  e do `-wal` depois de exclusão permanente de estudo, de esvaziar a lixeira e de excluir a conta; controle sem o
  pragma mostra o sentinela. Rodar e ver falhar.
- [x] T003 [P] `F/tests/feature-093-bootstrap-externo.test.mjs`: em modo build, o marcador vira
  `<script src="/appearance-bootstrap.js"></script>` e nenhum `<script>` inline executável sobra; em modo dev,
  segue inline; o asset emitido contém `cadernoFontCatalog`. Rodar e ver falhar.

## Phase 2: Cabeçalhos (US1, US3)

- [x] T004 `B/app/core/security_headers.py`: `build_csp(google_enabled)` com a política da FR-001/FR-002;
  `Referrer-Policy: same-origin`; `X-Robots-Tag` por lista de rotas públicas (decisão 3).
- [x] T005 `B/tests/test_security_headers_and_csp.py`: atualizar as asserções de `Referrer-Policy` e dos domínios
  de fontes para os valores novos, com comentário citando a F0.10.02.

## Phase 3: Sem script inline (US2)

- [x] T006 `F/vite.config.ts`: plugin com modo dev (inline) e modo build (`<script src>` mais `generateBundle`
  emitindo `appearance-bootstrap.js`). Conferir `dist/index.html` e `dist/appearance-bootstrap.js` depois de
  `npm run build`.

## Phase 4: Origem dos pedidos (US4)

- [x] T007 `B/app/core/config.py`: `get_trusted_origins()` (`LEITORUM_TRUSTED_ORIGINS`) e `get_security_contact()`.
- [x] T008 `B/app/core/origin_guard.py`: `OriginGuardMiddleware` (decisão 4), com log sem corpo nem cookies.
- [x] T009 `B/app/main.py`: registrar o middleware depois do `SecurityHeadersMiddleware`.

## Phase 5: Contato de segurança (US5)

- [x] T010 `B/app/routers/seo.py`: `GET /.well-known/security.txt` (decisão 5).

## Phase 6: Apagar de verdade (US6)

- [x] T011 `B/app/db/session.py`: `PRAGMA secure_delete=ON` em `_configure_connection`, com conferência de leitura
  como já é feito para `foreign_keys`.
- [x] T012 `B/app/services/persistence.py`: `checkpoint_after_purge(session)` (decisão 6).
- [x] T013 `B/app/services/trash_service.py` e `account_service.py`: chamar o checkpoint depois do commit em
  `permanent_delete_book`, `permanent_delete_study`, `empty_trash`, `purge_expired_trash` e
  `delete_account_permanently`.

## Phase 7: Validação

- [x] T014 `pytest -k "security or secure_delete or seo or trash or account"` com banco descartável: T001, T002 e
  os testes vizinhos passam. Depois, sozinho, `npm run build` e `node --test tests/feature-093-bootstrap-externo.test.mjs`.
- [x] T015 Navegador (servidor de validação): aba Rede de `/` e `/livros` só com `localhost:8010`; console sem
  violação de CSP; tema escuro salvo aplicado sem piscar; salvar um estudo, mandar para a lixeira e restaurar;
  `/.well-known/security.txt` legível; cabeçalhos conferidos com `fetch(...).headers`.

## Phase 8: Fechamento

- [x] T016 `caderno-leitura-0.1/docs/contexto/RETOMADA.md`: seção da F0.10.02, com as decisões, o achado do
  `/compartilhado` e a pendência do `Referrer-Policy` com o login do Google no ambiente real.
- [x] T017 Marcar as tarefas e o status da spec; commit logo após o build (`feature — endurecimento de segurança e
  privacidade verificável`), sem `query`, `stop` e `.claude/`; reportar ao usuário.

---

## Dependências

- T001, T002, T003 (paralelas) → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 →
  T015 → T016 → T017.
- T006 é independente do backend e pode ser feita a qualquer momento depois da T003.
