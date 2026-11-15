# Implementation Plan: F0.12.02 — Estudos Publicados na Web

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-14 | **Status**: Aguardando aprovação

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TS. **Migração `0040`** (coluna sem chave estrangeira). Sem dependência nova:
renderizador de Markdown restrito escrito no projeto. Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado; a `0040` fica pendente para o usuário aplicar |
| Privacidade | Publicação só por escolha explícita do dono; só as 4 seções, referência e nome de exibição; menções a estudos não publicados viram texto |
| Segurança | HTML gerado com escape primeiro; links só `http(s)`; CSP sem script; 404 igual para todos os casos |
| Lote | 2ª feature do lote 1 do 0.12 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0040_study_published_at.py`, `models/study.py` | coluna e índice |
| `backend/app/services/public_markdown.py` (novo) | renderizador restrito e resumo |
| `backend/app/services/public_study_service.py` (novo) | publicar, despublicar, listar, disponibilidade, página |
| `backend/app/routers/public_studies.py` (novo), `main.py` | API e `GET /compartilhado/{id}` |
| `backend/app/services/seo_service.py` | robots e sitemap pelos publicados |
| `backend/app/schemas/study.py` | `published_at` na leitura do estudo |
| `frontend/src/components/sharing/PublishToWebCard.vue`, `components/settings/PublishedStudiesCard.vue` (novos) | publicar e gerenciar |
| `frontend/src/views/StudyView.vue` (painel de compartilhamento), `views/SettingsView.vue` | uso dos cartões |
| `frontend/src/services/api.ts`, `types.ts` | chamadas e tipos |
| testes | `test_public_markdown.py`, `test_public_studies.py`, `test_migration_0040.py`, `feature-115-publicar.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` (fecha a pendência do §5) |

## Decisões

1. **Opção separada da visibilidade**: "público" continua sendo da instalação; "publicado na web" é outra chave, para
   nada sair sem pedido.
2. **HTML do servidor**: indexável e legível sem JavaScript; não carrega a interface inteira para um visitante.
3. **Renderizador próprio, escape primeiro**: evita dependência nova e garante que nada do texto vire HTML ativo.
4. **Mesmo endereço ao republicar**: o id do estudo; despublicar só esconde.

## Riscos

| Risco | Mitigação |
|---|---|
| Vazar dado privado na página | Lista fechada de campos; testes que procuram notas, fichamento, destaques, e-mail e usuário no HTML |
| Injeção de HTML pelo Markdown | Escape antes de qualquer marcação; testes com `<script>`, atributos e `javascript:` |
| Usuário achar que "publicado" já está na internet | Aviso sobre `APP_BASE_URL` e exposição da rede no painel |
