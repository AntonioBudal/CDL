# Tasks — F0.12.07: Círculos de leitura com trava anti-spoiler

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; migração `0042`; 2ª feature do lote 2.

- [x] T001 Testes que falham primeiro: `test_reading_circles.py`, `feature-120-circulos.test.mjs`.
- [x] T002 Migração `0042` e modelos; subir e descer em banco descartável.
- [x] T003 `reading_circle_service.py`: criar, convidar, aceitar/recusar, progresso, partes, mensagens com a trava,
  bloqueio, sair/remover/apagar, exemplar.
- [x] T004 `routers/reading_circles.py` e registro; contratos de rota.
- [x] T005 `CirclesView.vue` e `CircleView.vue`; rotas; menu "Mais" com contador; "Criar círculo deste livro".
- [x] T006 Testes novos e vizinhos; build; navegador com dois leitores fictícios (desktop, 375 px, 10 temas).
- [x] T007 Versão `0.12.0-alpha.7` e linha do tempo; `ROADMAP-0.12.md`, `RETOMADA.md`, `HANDOFF.md`; commit; levar ao
  `main`; build no checkout principal.
