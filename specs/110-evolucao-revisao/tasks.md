# Tasks — F0.11.08: Evolução da Revisão

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; migração `0037` (não aplicada ao banco ativo);
3ª feature do lote 2 do 0.11.

- [x] T001 Testes que falham primeiro: pesos, cartões de conceito, frágeis, Memória do Dia, migração, frontend.
- [x] T002 Migração `0037` e modelos; `test_migration_matches_models`.
- [x] T003 `review_weights.py`; peso ao avaliar; fila nova em `get_review_items`.
- [x] T004 Cartões de conceito: serviço, `kind=concept`, avaliação; conceitos frágeis; `fragile` no léxico.
- [x] T005 Memória do Dia: serviço e rota.
- [x] T006 Frontend: filtro "Conceitos", verso, gravação, `FragileConceptsPanel`, etiqueta "Frágil", `DailyMemoryCard`.
- [x] T007 Testes novos e vizinhos; `npm run build`; navegador (1366 e 375 px; 10 temas).
- [x] T008 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
