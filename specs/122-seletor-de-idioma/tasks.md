# Tasks — F0.12.09: Seletor de idioma (só a fundação)

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Migração `0043`; 4ª feature do lote 2.

- [x] T001 Testes que falham primeiro: `feature-122-idioma.test.mjs`, `test_user_locale.py`.
- [x] T002 `vue-i18n`; `src/i18n/` (instância, `pt-BR`, `en`, formatos, idioma inicial); instalar no `main.ts`.
- [x] T003 Migração `0043` e API de preferências com `locale`.
- [x] T004 Menus, cabeçalho, rodapé, títulos das abas, avisos gerais e atalhos por chave; tradução em inglês.
- [x] T005 Datas e números pela função comum nas 31 telas; seletor em Ajustes; `<html lang>`; `localStorage`.
- [x] T006 Testes novos e vizinhos; build; navegador (troca sem recarregar, recarga, tela de entrada, console sem
  erro de CSP, 375 px).
- [x] T007 Versão `0.12.0-alpha.9` e linha do tempo; `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md`; commit; levar ao
  `main`; build no checkout principal.
