# Tasks — F0.12.02: Estudos Publicados na Web

**Input**: [spec.md](spec.md) e [plan.md](plan.md). Dados fictícios; migração `0040` (não aplicada ao banco ativo);
2ª feature do lote 1 do Roadmap 0.12.

- [ ] T001 Testes que falham primeiro: renderizador, API, página pública, SEO, migração, frontend.
- [ ] T002 Migração `0040` e modelo; `test_migration_matches_models`.
- [ ] T003 `public_markdown.py`: escape, blocos, inline, links seguros, menções.
- [ ] T004 `public_study_service.py` e rotas (API + `GET /compartilhado/{id}`); `seo_service` pelos publicados.
- [ ] T005 Frontend: `PublishToWebCard` no estudo, `PublishedStudiesCard` em Ajustes, API e tipos.
- [ ] T006 Testes novos e vizinhos; `npm run build`; navegador (375 e 1366 px; 10 temas nos cartões).
- [ ] T007 `RETOMADA.md` e `HANDOFF.md`; commit; levar ao `main`; build no checkout principal.
