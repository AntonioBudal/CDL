# Tasks — F0.12.04: Feeds RSS, Atom e JSON

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; sem migração; 4ª feature do 0.12.

- [x] T001 Testes que falham primeiro: `test_feeds.py`, `feature-117-feeds.test.mjs`.
- [x] T002 `feed_service.py`: itens, RSS 2.0, Atom 1.0, JSON Feed 1.1, ETag; HTML das seções compartilhado com a página.
- [x] T003 `routers/feeds.py` (GET/HEAD, 304); `<link rel="alternate">` na página pública; `robots.txt`.
- [x] T004 Endereços dos feeds em Ajustes → "Publicados na web".
- [x] T005 Testes novos e vizinhos; `npm run build`; navegador.
- [x] T006 Versão `0.12.0-alpha.4` e linha do tempo; `RETOMADA.md`, `HANDOFF.md`, `ROADMAP-0.12.md`; commit; levar ao
  `main`; build no checkout principal.
