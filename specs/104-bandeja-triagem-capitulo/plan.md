# Implementation Plan: F0.11.02 — Bandeja de Triagem por Capítulo

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-09 | **Status**: Executado em 2026-11-09

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3. **Com migração** (`0035`, aditiva). Sem dependência nova. Testes em
`tmp_path`; servidor de validação com banco temporário.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado. Implantação pelo procedimento do HANDOFF (aplica 0034 e 0035 juntas) |
| Migração | Aditiva, reversível, sem preencher nada |
| Lote | 2ª feature do lote 1 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0035_inbox_capture_chapter.py` (novo) | coluna com FK `SET NULL`, índice; `downgrade` com `DROP COLUMN` |
| `backend/app/models/inbox_capture.py` | `chapter_id` + relação |
| `backend/app/schemas/inbox_capture.py` | `chapter_id` em criar/editar/ler, `chapter_name`; `InboxBookTrayResponse` |
| `backend/app/services/inbox_service.py` (ou o serviço atual) | validação dono/coerência, livro a partir do capítulo, limpar capítulo ao trocar livro, filtro e contagens |
| `backend/app/routers/inbox.py` | `chapter_id` na listagem; `GET /book-tray` |
| `frontend/src/types.ts`, `services/api.ts` | tipos e chamadas |
| `frontend/src/components/inbox/QuickCaptureModal.vue` | seletor de capítulo; padrão vindo da página do livro |
| `frontend/src/components/books/ChapterTray.vue` (novo) | bandeja do capítulo |
| `frontend/src/views/BookView.vue` | bandeja, contagens nos capítulos, linha "sem capítulo" |
| `frontend/src/views/ImportView.vue` | capítulo da captura promovida |
| `frontend/src/components/inbox/CaptureItemCard.vue`, `views/InboxView.vue` | capítulo no cartão e na edição; `?livro=` |
| testes | `backend/tests/test_inbox_chapter_tray.py`, `frontend/tests/feature-104-bandeja-capitulo.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Capítulo na captura, não uma tabela nova**: a bandeja é só uma vista das capturas pendentes por capítulo; a Mesa
   continua sendo o lugar central.
2. **Livro derivado do capítulo**: evita captura com livro A e capítulo de B.
3. **Contagens num endpoint só** (`book-tray`): uma chamada por página de livro, não uma por capítulo.
4. **"Virar estudo" reaproveita a promoção** existente (Importar com `promote_inbox_id`), agora com o capítulo.

## Riscos

| Risco | Mitigação |
|---|---|
| Banco ativo ainda sem a 0034 | O mesmo `upgrade head` aplica as duas, com um snapshot antes |
| Página do livro ficar pesada | Bandeja recolhível; lista só do capítulo escolhido; contagens agregadas no servidor |
| Testes antigos da Inbox fixarem o formato do cartão ou do payload | Ajustar no mesmo commit |
