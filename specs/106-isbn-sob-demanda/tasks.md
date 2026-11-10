# Tasks — F0.11.04: ISBN Sob Demanda

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Sem rede real nos testes; bancos descartáveis.

- [x] T001 Testes que falham primeiro: `test_isbn_lookup.py` e `feature-106-isbn.test.mjs`.
- [x] T002 Migração `0036_book_isbn_publisher`, modelo e schemas (ISBN normalizado).
- [x] T003 `isbn_service.py` (BrasilAPI → Open Library, limites) e rota; chave `LEITORUM_ISBN_LOOKUP`; status.
- [x] T004 Exportação com ISBN, editora e local.
- [x] T005 Frontend: `IsbnLookup.vue` no cadastro e na edição; exibição na página do livro.
- [x] T006 Referência ABNT com local e editora.
- [x] T007 Landing e Desafio F12: textos de conexões externas.
- [x] T008 Testes novos e vizinhos; `npm run build`; navegador com busca simulada (1366 e 375 px; 10 temas).
- [x] T009 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
