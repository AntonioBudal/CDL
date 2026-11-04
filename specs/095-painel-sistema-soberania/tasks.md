# Tasks — F0.10.03: Painel de Sistema, Segurança, Backups e Soberania dos Dados

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos e `.git` em `tmp_path`; banco ativo
nunca escrito; build antes do commit (4ª feature do lote de 5).

- [x] T001 Testes que falham primeiro: `backend/tests/test_system_status.py` (commit por variável, ref solta,
  `packed-refs` e sem `.git`; revisão atual e esperada; status com e sem admin; integridade ok, corrompida e 403) e
  `frontend/tests/feature-095-painel-sistema.test.mjs`.
- [x] T002 `core/build_info.py`: `get_build_commit()` e `get_expected_schema_revision()`.
- [x] T003 `services/maintenance.py`: `auto_backup_status()`.
- [x] T004 `schemas/system.py` e `routers/system.py`; registro em `main.py`.
- [x] T005 `vite.config.ts`: `__BUILD_COMMIT__`; declaração de tipo.
- [x] T006 `api.ts` e `types.ts`: `getSystemStatus`, `runIntegrityCheck`.
- [x] T007 `components/settings/SystemSovereigntyCard.vue` (US1 a US4).
- [x] T008 `SettingsView.vue`: card na aba Sistema, commit no card de conexão, `DatabaseBackup` só para admin.
- [x] T009 Testes novos e vizinhos (`settings`, `health`, `backups`) e `npm run build`.
- [x] T010 Navegador (1366 e 375 px): painel, aviso de divergência com `LEITORUM_BUILD_COMMIT` forçado,
  verificação de integridade, contraste nos 10 temas.
- [x] T011 `RETOMADA.md`, marcar tarefas, commit e relatório.
