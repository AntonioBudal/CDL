# Tasks — F0.10.05: Destaques com Cópia ABNT e Tipografia Citação × Anotação

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; bancos descartáveis; 1ª feature do lote 2.

- [x] T001 Testes que falham primeiro: `backend/tests/test_highlight_library_book_meta.py` e
  `frontend/tests/feature-098-destaques-abnt.test.mjs` (formatador e cartão).
- [x] T002 Backend: `book_year` e `book_subtitle` no schema e no serviço da biblioteca.
- [x] T003 Frontend: tipos; `citationFormatter.ts` reescrito; `utils/clipboard.ts`.
- [x] T004 `HighlightCard.vue`: citação literal × texto do leitor (tipografia, rótulo, cópia), controle "Citação
  literal", menu acessível, `aria-live`, `.quiet`.
- [x] T005 CSS do `HighlightCard.vue` (não o `style.css` global): estilos do texto do leitor e do rótulo de origem, só com tokens.
- [x] T006 `HighlightsLibraryView.vue`: alternância otimista com reversão em erro.
- [x] T007 Atualizar testes antigos do formato de citação; rodar testes novos e vizinhos de Destaques; `npm run build`.
- [x] T008 Navegador (1366 e 375 px, dados fictícios): alternar, copiar os formatos, contraste nos 10 temas.
- [x] T009 `RETOMADA.md`, marcar tarefas, commit, levar ao `main` (fast-forward) e build no checkout principal.
