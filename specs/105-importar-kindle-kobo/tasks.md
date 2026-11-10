# Tasks — F0.11.03: Importar Destaques do Kindle e do Kobo

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Arquivos sintéticos; bancos descartáveis; sem migração.

- [x] T001 Testes que falham primeiro: `test_ereader_import.py` e `feature-105-importar-kindle-kobo.test.mjs`.
- [x] T002 Parser do Kindle (`My Clippings.txt`, inglês e português, notas, marcadores, ajustes).
- [x] T003 Parser do Kobo (`KoboReader.sqlite` somente leitura, cópia temporária, limites).
- [x] T004 Serviço: prévia (sugestão de livro, duplicatas) e importação em lote; rotas.
- [x] T005 Frontend: `EreaderImportView.vue`, rota e botão na Mesa.
- [x] T006 Testes novos e vizinhos; `npm run build`.
- [x] T007 Navegador (banco temporário, arquivos sintéticos; 1366 e 375 px; contraste nos 10 temas).
- [x] T008 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
