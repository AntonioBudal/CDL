# Tasks — F0.11.09: Receptor KOReader/Readest

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; migração `0038` (não aplicada ao banco ativo);
4ª feature do lote 2 do 0.11.

- [x] T001 Testes que falham primeiro: token, receptor, JSON do KOReader, migração, frontend.
- [x] T002 Migração `0038`, modelo; `test_migration_matches_models`.
- [x] T003 `receiver_tokens.py` e rotas da conta.
- [x] T004 Parsers `koreader.py` e `readwise.py`; detecção de formato; gravação automática na Mesa.
- [x] T005 Receptor (`auth/`, `highlights/`), isenção de origem, limites, logs sem conteúdo.
- [x] T006 Frontend: `ReceiverTokenCard`, Configurações, tela "Importar de leitor digital".
- [x] T007 Testes novos e vizinhos; `npm run build`; navegador (1366 e 375 px; 10 temas).
- [x] T008 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
