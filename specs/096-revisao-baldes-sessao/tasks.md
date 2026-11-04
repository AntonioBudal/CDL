# Tasks — F0.10.04: Revisão com Baldes, Sessões de 5/10/15 e Gaveta de Contexto

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos descartáveis; 5ª feature do lote:
fecha com `npm test`, `pytest` completo (sozinho) e build.

- [x] T001 Testes que falham primeiro: `backend/tests/test_review_buckets.py` (contagens com e sem filtros, `bucket`
  nos itens e na sessão estruturada, 422 para valor inválido) e `frontend/tests/feature-096-revisao-baldes.test.mjs`.
- [x] T002 Backend: schemas, `review_service` (baldes e filtro), router de revisão.
- [x] T003 ~~Backend: `bucket` na criação da sessão estruturada.~~ Retirada na execução: exigiria migração (ver
  spec, US1). No lugar, aviso na tela quando há balde escolhido.
- [x] T004 Frontend: tipos e chamadas de API com `bucket`, filtros dos baldes e `limit`.
- [x] T005 `ReviewStatsHeader.vue`: linha de baldes e seletor 5/10/15.
- [x] T006 `ReviewHubView.vue`: estado e repasse às três entradas; `localStorage` do tamanho.
- [x] T007 `StudyContextDrawer.vue` e botão "Ver o estudo" no `ReviewCard` e na `StudySessionView`.
- [x] T008 Testes novos e vizinhos da revisão; `npm run build`.
- [x] T009 Navegador (1366 e 375 px): baldes, sessão de 5 do balde "Difícil", gaveta após revelar, contraste nos
  10 temas.
- [x] T010 Fecho do lote: `npm test`, `pytest` completo e build; falhas de features anteriores em commit próprio.
- [x] T011 `RETOMADA.md`, marcar tarefas, commit e relatório.
