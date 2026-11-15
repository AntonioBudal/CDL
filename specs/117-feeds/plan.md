# Implementation Plan: F0.12.04 — Feeds RSS, Atom e JSON

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Executado em 2026-11-15

## Technical Context

FastAPI + SQLAlchemy 2. **Sem migração.** XML com `xml.etree.ElementTree` (biblioteca padrão), JSON com `json`.
Testes em `tmp_path`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado |
| Privacidade | Feed só com o que já é público (estudos publicados e disponíveis); mesmos campos da página pública |
| Lote | 4ª feature do 0.12 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/feed_service.py` (novo) | itens, RSS, Atom, JSON Feed, ETag |
| `backend/app/routers/feeds.py` (novo), `main.py` | rotas e 304 |
| `backend/app/services/public_study_service.py` | `<link rel="alternate">` na página pública; HTML das seções reaproveitável |
| `backend/app/services/seo_service.py` | `Allow` dos feeds no `robots.txt` |
| `frontend/src/components/settings/PublishedStudiesCard.vue` | endereços dos feeds |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.4` |
| testes | `test_feeds.py`, `feature-117-feeds.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md`, `ROADMAP-0.12.md` |

## Decisões

1. **Feed da instalação**: sem expor nome de usuário nem criar identificador público novo.
2. **Gerador de XML, nunca texto concatenado**: escape garantido (inclusive `]]>`).
3. **Mesmo conteúdo da página pública**: uma função só gera o HTML das seções para a página e para os feeds.
4. **`no-cache` + `ETag`**: despublicar some na próxima leitura, e leitores economizam banda com 304.

## Riscos

| Risco | Mitigação |
|---|---|
| Feed inválido para algum leitor | Testes com os elementos obrigatórios de cada padrão; datas em RFC 822 (RSS) e RFC 3339 (Atom/JSON) |
| Vazar campo privado | Itens montados só com os campos da página pública; teste procura os campos privados |
