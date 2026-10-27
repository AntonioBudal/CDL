# Tasks: Autorização Antes da Geração de Backup

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: Obrigatórios (FR-006, SC-001, SC-003); escritos antes da correção.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência).
- **[Story]**: US1 (anônimo), US2 (usuário comum), US3 (administrador).
- Caminhos relativos a `caderno-leitura-0.1/backend/`.
- Python: `C:\Users\User\caderno\caderno-leitura-0.1\backend\.venv\Scripts\python.exe`, executado a partir de `caderno-leitura-0.1/backend` do worktree.

---

## Phase 1: Setup — linha de base

- [x] T001 Confirmar que `app.__file__` resolve para o worktree (`python -c "import app; print(app.__file__)"`).
- [x] T002 Rodar `python -m pytest -q -p no:cacheprovider` e registrar a linha de base; a única falha aceita é `test_iniciar_rejects_relative_database_path`.

**Checkpoint**: ambiente aponta para o worktree; linha de base conhecida.

---

## Phase 2: Testes primeiro (US1, US2, US3)

- [x] T003 [US1][US2][US3] Em `tests/test_security_privileged_access.py`, adicionar a fixture `backup_calls(monkeypatch)`, que substitui `app.routers.backups.create_database_backup` e `app.routers.backups.create_backup_bundle` por registradores. Cada registrador anota `(tipo, path)` e grava bytes fictícios em `path`.
- [x] T004 [US1][US2] No mesmo arquivo, adicionar `test_unauthorized_backup_requests_never_generate_backup`, parametrizado em `/api/backup` e `/api/backup/bundle` × {anônimo → 401, usuário comum → 403}. O teste confere o status e `backup_calls == []`.
- [x] T005 [US2] No mesmo arquivo, adicionar o caso de usuário comum com cabeçalho `Range: bytes=0-` nas duas rotas: 403 e `backup_calls == []`.
- [x] T006 [US3] No mesmo arquivo, adicionar `test_admin_backup_request_reaches_generation`, parametrizado nas duas rotas: 200 e exatamente uma chamada do tipo esperado.
- [x] T007 Rodar só esses testes contra o código atual. Esperado: T004 e T005 falham porque há chamadas registradas; T006 passa. Registrar o resultado como evidência de SC-003.

**Checkpoint**: o defeito está demonstrado por teste.

---

## Phase 3: Correção

- [x] T008 [US1][US2] Em `app/routers/backups.py`, acrescentar `_admin: AdminUser` como primeiro parâmetro de `temporary_backup` e de `temporary_backup_bundle`, sem mudar o corpo (FR-001, FR-002, FR-003).
- [x] T009 [US3] No mesmo arquivo, mover `_admin: AdminUser` para o primeiro parâmetro de `download_backup` e de `download_backup_bundle_endpoint` (FR-004, FR-005).

**Checkpoint**: a geração depende estruturalmente da autorização.

---

## Phase 4: Validação

- [x] T010 Rodar os testes de T003 a T006: todos verdes (SC-001, SC-003).
- [x] T011 Rodar `python -m pytest -q -p no:cacheprovider` completo. Esperado: verde, salvo `test_iniciar_rejects_relative_database_path` (SC-002, NFR-003).
- [x] T012 Conferir `git diff` e confirmar que só mudaram `app/routers/backups.py`, `tests/test_security_privileged_access.py` e `specs/087-*` (NFR-002).

---

## Phase 5: Registro

- [x] T013 Marcar as tarefas concluídas neste arquivo e mudar o status da spec.
- [x] T014 Depois do aceite do usuário, fazer um único commit em português, por exemplo `feature — autorização antes de gerar backup` (NFR-004).

---

## Registro de execução (2026-10-27)

- **T001**: `app.__file__` resolve para `.claude/worktrees/vigilant-swartz-c1e0ef/caderno-leitura-0.1/backend/app/__init__.py`.
- **T002**: linha de base com 4 falhas, e não 1. Além de `test_iniciar_rejects_relative_database_path`, falharam os três testes de backup de `test_security_privileged_access.py` com 503 ("O arquivo do banco está vazio"). A causa é que este branch não contém o commit `f4713b4` da 086 (`teste — isola o banco ativo da suíte do backend`, branch `claude/intelligent-perlman-c530cd`). Sem ele, `rbac_client` não define `CADERNO_DATABASE_PATH`, e as rotas copiam o `data/caderno.db` padrão do worktree, que é um arquivo vazio. O banco ativo do checkout principal não foi tocado, porque `BACKEND_DIR` aponta para o worktree.
- **Ajuste adicional em T003**: a fixture `rbac_client` recebeu a mesma linha de `f4713b4` (`monkeypatch.setenv("CADERNO_DATABASE_PATH", str(db_file))`, com o mesmo comentário). Assim o teste de administrador existente volta a passar, e esta suíte não copia o banco padrão quando rodada no checkout principal. A mudança é textualmente idêntica à da 086 e deve mesclar sem conflito.
- **T007**: contra o código antigo, os 4 casos de T004 e os 2 de T005 falharam porque havia chamadas registradas (`[('db', …)]`, `[('bundle', …)]`); os casos de T006 passaram.
- **T010**: `test_security_privileged_access.py`, `test_backup_bundle.py` e `test_admin_and_rbac.py`: 24 passed.
- **T011**: suíte completa com `1 failed, 490 passed, 5 skipped`. A única falha é a ambiental conhecida `test_iniciar_rejects_relative_database_path` (falta `frontend/dist` no worktree). Na linha de base foram `4 failed, 479 passed`.
- **T012**: `git status` mostra só `app/routers/backups.py`, `tests/test_security_privileged_access.py` e `specs/087-backup-autorizacao-antes-da-geracao/`.

---

## Dependencies & Execution Order

- Fases sequenciais: 1 → 2 → 3 → 4 → 5.
- T003 a T006 editam o mesmo arquivo e por isso não são paralelas; T008 e T009 também editam o mesmo arquivo.
- T014 depende do aceite explícito do usuário.

## Cobertura (requisito → tarefas)

| Requisito | Tarefas |
| --- | --- |
| FR-001 | T004, T008 |
| FR-002 | T004, T008 |
| FR-003 | T008 |
| FR-004 | T004, T005, T009 |
| FR-005 | T006, T009, T011 |
| FR-006 | T003, T004 |
| NFR-001 | T003 (fixture `rbac_client` em `tmp_path`) |
| NFR-002 | T012 |
| NFR-003 | T011 |
| NFR-004 | T014 |
| SC-001 | T004, T010 |
| SC-002 | T011 |
| SC-003 | T007, T010 |
