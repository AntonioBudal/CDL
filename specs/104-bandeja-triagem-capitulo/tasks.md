# Tasks — F0.11.02: Bandeja de Triagem por Capítulo

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos descartáveis; banco ativo intocado.

- [x] T001 Testes que falham primeiro: `test_inbox_chapter_tray.py` e `feature-104-bandeja-capitulo.test.mjs`.
- [x] T002 Migração `0035_inbox_capture_chapter` e modelo; subir e descer em banco descartável.
- [x] T003 Schemas, serviço e rotas: `chapter_id`, validação, livro pelo capítulo, filtro, `book-tray`.
- [x] T004 `QuickCaptureModal`: capítulo e padrão vindo da página do livro.
- [x] T005 `ChapterTray.vue` e integração na `BookView` (bandeja, contagens, linha sem capítulo).
- [x] T006 Importar com o capítulo da captura; `CaptureItemCard` e `InboxView` (`?livro=`).
- [x] T007 Testes novos e vizinhos; `npm run build`.
- [x] T008 Navegador (banco temporário; 1366, 375 e 320 px; contraste nos 10 temas).
- [x] T009 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
