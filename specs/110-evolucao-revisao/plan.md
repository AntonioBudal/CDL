# Implementation Plan: F0.11.08 — Evolução da Revisão

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-12 | **Status**: Executado em 2026-11-12

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TS. **Migração `0037`** (coluna nova sem chave estrangeira + tabela nova).
Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado; a `0037` fica pendente junto com `0034`–`0036`, para o usuário aplicar com o procedimento do HANDOFF |
| Isolamento | Pesos, cartões e memória só do próprio leitor; lixeira fora |
| Lote | 3ª feature do lote 2 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0037_review_difficulty_concepts.py` (novo) | coluna, preenchimento, tabela `concept_reviews` |
| `backend/app/models/study_highlight.py`, `models/concept_review.py` (novo), `models/__init__.py` | modelos |
| `backend/app/services/review_weights.py` (novo) | peso, intervalo, vencimento, chave da fila |
| `backend/app/services/review_service.py` | peso ao avaliar; fila nova |
| `backend/app/services/concept_review_service.py` (novo) | cartões, avaliação, conceitos frágeis |
| `backend/app/services/daily_memory.py` (novo) | Memória do Dia |
| `backend/app/schemas/review.py`, `schemas/concept.py`, `schemas/dashboard.py` | campos e respostas novas |
| `backend/app/routers/review.py`, `routers/concepts.py`, `routers/dashboard.py` | rotas |
| `frontend/src/types.ts`, `services/api.ts` (ou o `reviewApi`) | tipos e chamadas |
| `frontend/src/components/review/ReviewStatsHeader.vue`, `ReviewCard.vue`, `composables/useReviewSession.ts`, `views/ReviewHubView.vue` | filtro "Conceitos", verso com definições, gravação, bloco de frágeis |
| `frontend/src/components/review/FragileConceptsPanel.vue` (novo) | conceitos frágeis |
| `frontend/src/components/dashboard/DailyMemoryCard.vue` (novo), `views/DashboardView.vue` | Memória do dia |
| `frontend/src/views/LexiconView.vue`, `views/ConceptView.vue` | etiqueta "Frágil" |
| testes | `test_review_weights.py`, `test_concept_reviews.py`, `test_daily_memory.py`, `test_migration_0037.py`, `feature-110-revisao.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Média móvel em vez de SM-2/FSRS**: o peso guarda o histórico com uma conta que cabe numa frase e se explica na
   tela; o intervalo sai do peso na hora, sem data de vencimento guardada (nada a migrar se a regra mudar).
2. **Fila calculada em Python** sobre os itens do filtro: com SQLite e acervo pessoal (milhares de itens), é simples e
   rápido; os baldes continuam em SQL.
3. **Tabela própria para cartões de conceito**: o conceito é derivado (F0.11.06) e não tem linha no banco; a tabela
   guarda só a avaliação, pela chave normalizada.
4. **Fragilidade derivada**: nada guardado; vem dos pesos do cartão e das perguntas dos estudos que definem o conceito.
5. **Memória determinística**: semente "leitor + data" para a escolha do dia não mudar ao recarregar.
6. **Peso de reserva** (execução): item avaliado e ainda sem peso (antes da `0037`) usa o equivalente da última nota
   (`effective_weight`), igual ao preenchimento da migração; assim a fila não muda para quem já revisava.

## Riscos

| Risco | Mitigação |
|---|---|
| Migração em banco grande | Uma coluna nula + `UPDATE` por `last_rating` + tabela vazia; snapshot automático e validado |
| `test_migration_matches_models` | Nomes de restrição pela convenção; tabela criada com `op.create_table` e restrições nomeadas |
| Fila mudar a experiência de quem já revisa | Nunca revisados continuam primeiro; os baldes e "Praticar agora" não mudam de lugar |
| Léxico recalculado a cada pedido de cartões | Mesmo custo do Léxico (já paginado); limite de itens por sessão |
