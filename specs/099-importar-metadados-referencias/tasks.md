# Tasks — F0.10.06: Importar com Faixa de Metadados da Obra e Ganchos para Referências

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; 2ª feature do lote 2.

- [x] T001 Testes que falham primeiro: `frontend/tests/feature-099-importar-metadados.test.mjs` (módulo e tela).
- [x] T002 `utils/referenceScopes.ts`: localizador, escopos, contagem de referências, chamada ABNT com página.
- [x] T003 `components/import/ImportWorkMetaStrip.vue`: linha da obra, aviso, "Completar dados do livro" com
  `expected_version` e tratamento de 409, prévia dos 3 escopos; `.quiet`, tokens, 44 px.
- [x] T004 `ImportView.vue`: integrar o componente, atualizar `books`, rótulo "Página ou localização".
- [x] T005 Testes novos e vizinhos da Importar; `npm run build`.
- [x] T006 Navegador (1366, 375 e 320 px, dados fictícios): completar livro sem ano, prévia com página e posição,
  contraste nos 10 temas.
- [x] T007 `RETOMADA.md`, marcar tarefas, commit, levar ao `main` (fast-forward) e build no checkout principal.
