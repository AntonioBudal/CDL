# Tasks — F0.11.01: Estados de Leitura do Livro

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos descartáveis; banco ativo intocado.

- [x] T001 Testes que falham primeiro: `test_book_reading_state.py`,
  `feature-103-estados-leitura.test.mjs`.
- [x] T002 Migração `0034_book_reading_state` e modelo; subir e descer em banco descartável.
- [x] T003 Schemas e `PATCH`: estados, datas automáticas, fim ≥ início, ocultar para terceiros.
- [x] T004 Exportação JSON e Markdown; conferir `sync_service`.
- [x] T005 ~~`scripts/migrar_com_backup.py`~~ Substituída: o `alembic upgrade` já faz o snapshot validado e aborta se
  falhar (`migrations/env.py`); teste novo cobre a 0034.
- [x] T006 Frontend: tipos, `BookReadingState.vue` na `BookView`.
- [x] T007 Frontend: selo e filtro na biblioteca, com `localStorage`.
- [x] T008 Testes novos e vizinhos; `npm run build`.
- [x] T009 Navegador (banco temporário migrado; 1366, 375 e 320 px; contraste nos 10 temas).
- [x] T010 `RETOMADA.md` e `HANDOFF.md` (procedimento de implantação); commit; levar ao `main`; build no checkout principal.
