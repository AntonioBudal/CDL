# Tasks — F0.11.11: Cadernos de Síntese com Transclusão

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; migração `0039` (não aplicada ao banco ativo);
1ª feature do lote 3 do 0.11.

- [x] T001 Testes que falham primeiro: analisador (backend e frontend), API, migração.
- [x] T002 Migração `0039` e modelo; `test_migration_matches_models`.
- [x] T003 `synthesis_service.py`: CRUD com versão, lixeira, analisador, resolução, exportação.
- [x] T004 Schemas, rotas, `main.py`; pacote da conta com `sinteses/`.
- [x] T005 Frontend: `synthesisEmbeds.ts`, `SynthesesView`, `SynthesisView`, `EmbedBlock`, `InsertEmbedDialog`, API, rotas,
  menus, contratos 076/081.
- [x] T006 Testes novos e vizinhos; `npm run build`; navegador (1366 e 375 px; 10 temas).
- [x] T007 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
