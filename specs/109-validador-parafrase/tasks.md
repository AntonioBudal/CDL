# Tasks — F0.11.07: Validador de Paráfrase

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; sem migração; 2ª feature do lote 2 do 0.11.

- [x] T001 Testes que falham primeiro: `test_paraphrase_sources.py` e `feature-109-parafrase.test.mjs`.
- [x] T002 `paraphraseCheck.ts`: normalização, frases, citação declarada, trigramas, Jaccard, sequência comum, índice.
- [x] T003 `checkParaphrase` e `markAsQuote` (aspas + chamada ABNT).
- [x] T004 Backend: serviço, schemas e as duas rotas de fontes.
- [x] T005 `ParaphrasePanel.vue`; uso em `StudyEditView` e `ImportView`; API e tipos.
- [x] T006 Testes novos e vizinhos; `npm run build`; navegador (1366 e 375 px; 10 temas).
- [x] T007 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
