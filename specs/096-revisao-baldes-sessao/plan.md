# Implementation Plan: F0.10.04 — Revisão: Baldes, Sessões de 5/10/15 e Gaveta de Contexto

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-03 | **Status**: Executado em 2026-11-03

## Technical Context

FastAPI + SQLAlchemy 2 (backend) e Vue 3 (frontend). Sem migração, sem dependência nova. Testes em `tmp_path`;
conferência no servidor de validação com highlights fictícios do tipo pergunta e trecho oculto.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só dados fictícios nos testes e no navegador |
| Banco ativo intocado, sem migração | OK: baldes derivados de `last_rating` |
| Lote de 5 | 5ª feature: suítes completas no fim, `pytest` sozinho (sem build em paralelo) |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/schemas/review.py` | `ReviewBucket = Literal["new","hard","medium","easy"]`; `ReviewBucketCounts`; `ReviewStatsResponse.buckets` |
| `backend/app/services/review_service.py` | `_bucket_filter(bucket)` (`new` = `last_rating IS NULL`; os outros = `last_rating == bucket`); `get_review_stats(..., book_id, chapter_id, kind)` calcula os baldes com os mesmos filtros de `get_review_items`; `get_review_items(..., bucket)` |
| `backend/app/routers/review.py` | query params `bucket` (itens) e `book_id`, `chapter_id`, `kind` (stats) |
| `backend/app/schemas/study_session.py`, `routers/study_sessions.py` e o serviço da sessão | `bucket` opcional repassado à seleção dos itens |
| `frontend/src/types*.ts`, `services/api.ts` (ou o serviço de revisão em uso) | tipos e parâmetros novos |
| `frontend/src/components/review/ReviewStatsHeader.vue` | linha de baldes (`radiogroup`) e seletor de tamanho; emite `update:bucket` e `update:size` |
| `frontend/src/views/ReviewHubView.vue` | estado `bucket` e `sessionSize` (`localStorage`), repassados às três entradas; recarrega as contagens ao mudar o filtro |
| `frontend/src/components/review/StudyContextDrawer.vue` (novo) | carrega `api.getStudy(studyId)` ao abrir; mostra as 4 partes com `MarkdownContent`; estado de erro "não está mais disponível" |
| `frontend/src/components/review/ReviewCard.vue` e `views/StudySessionView.vue` | botão "Ver o estudo" com `v-if` da resposta revelada; abre a gaveta |
| testes | `backend/tests/test_review_buckets.py`, `frontend/tests/feature-096-revisao-baldes.test.mjs` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **Baldes = `last_rating`**: dado que já existe e já guia a ordem; "Novos" são os nunca avaliados. Sem coluna nova.
2. **Contagens dos baldes seguem o filtro atual**, mas os números da faixa de prontidão continuam globais, para não
   mudar o significado do que já aparece hoje.
3. **Gaveta só depois de revelar**: preserva a recuperação ativa; a consulta serve para entender o erro ou o acerto.
4. **Tamanho da sessão no navegador**: preferência pessoal, sem valor para o servidor; padrão 10, como hoje.
5. **Sem mexer na ordenação**: o balde só filtra; dentro dele vale a ordem atual (mais antigos primeiro).

## Riscos

| Risco | Mitigação |
|---|---|
| Teste antigo que fixa `limit: 10` no hub | Atualizar a asserção para o tamanho escolhido, com o padrão 10 |
| Gaveta sobre o cartão no celular atrapalhar a avaliação | Fecha com Esc, botão e fundo; foco volta ao botão "Ver o estudo" |
| Suítes completas acusarem falha de features anteriores (lote sem `pytest` completo desde a F0.10.01) | Corrigir em commit próprio, como combinado |
