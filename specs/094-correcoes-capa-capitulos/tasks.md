# Tasks — F0.10.02.5: Correções Visuais e Gerenciamento de Capítulos

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos descartáveis; build antes do commit.

- [x] T001 Testes que falham primeiro: `backend/tests/test_chapter_delete.py` e
  `frontend/tests/feature-094-capa-capitulos.test.mjs`.
- [x] T002 `chapters.py`: `DELETE /{chapter_id}` com 409 para capítulo com estudos e renumeração.
- [x] T003 `api.ts`: `deleteChapter`.
- [x] T004 `appearance-advanced.css`: ganchos `--quiet-fg` e `--quiet-fg-disabled`; ajustar o teste da F0.10.01.
- [x] T005 `BookView.vue`: regra móvel da capa em `.book-cover-container` (US1).
- [x] T006 `BookView.vue`: cores das ferramentas na pílula selecionada (US2).
- [x] T007 `BookView.vue`: botão "Excluir capítulo" no desktop e confirmação (US3).
- [x] T008 `BookView.vue`: menu "Gerenciar capítulo" e campo de renomear no celular (US3).
- [x] T009 Testes novos e vizinhos (capítulos, livros, F0.10.01) e `npm run build`.
- [x] T010 Navegador, 1366 e 375 px: capa, contraste nos 10 temas, criar/renomear/mover/excluir com recarga.
- [x] T011 `RETOMADA.md`, marcar tarefas, commit e resumo.
