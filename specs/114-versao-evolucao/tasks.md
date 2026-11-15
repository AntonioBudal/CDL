# Tasks — F0.12.01: Versão no Rodapé e "Evolução das Versões"

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Sem migração; 1ª feature do lote 1 do 0.12.

- [x] T001 Testes que falham primeiro: `test_app_version.py` e `feature-114-versoes.test.mjs`.
- [x] T002 `VERSION`; backend lê o arquivo; `vite.config.ts` (`__APP_VERSION__`); `package.json`.
- [x] T003 `appVersion.ts`; rodapé com a versão e a dica; Painel de Sistema.
- [x] T004 `versionHistory.ts` (0.1 a 0.12, a partir dos documentos do projeto).
- [x] T005 `VersionsView.vue`, rota `versions`, botão no fim do Sobre; contratos 076/081.
- [x] T006 Testes novos e vizinhos; `npm run build`; navegador (375 e 1366 px; 10 temas).
- [x] T007 Regra de versão no HANDOFF §2; `ROADMAP-0.12.md` e `RETOMADA.md`; commit; levar ao `main`; build no checkout
  principal.
