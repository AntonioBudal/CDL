# Implementation Plan: F0.10.07 — Amigos: Leituras e Estudos em Comum

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-07 | **Status**: Executado em 2026-11-07

## Technical Context

FastAPI + SQLAlchemy 2 e Vue 3. Sem migração, sem dependência nova. Testes de backend em `tmp_path` com dois usuários
fictícios (cabeçalho `X-User-Id`, como os testes de amizade e compartilhamento); frontend com `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: auditoria só de código; dados fictícios |
| Banco ativo intocado, sem migração | OK |
| Privacidade entre leitores | Só o que o visitante já pode ler; bloqueio → 404; nada de contagens de itens privados |
| Lote | 3ª feature do lote 2: build e testes novos |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/in_common_service.py` (novo) | `normalize_title_key`, `first_author_surname_key`, `get_in_common(session, viewer_id, username)` |
| `backend/app/schemas/in_common.py` (novo) | `InCommonStudy`, `InCommonBook`, `InCommonResponse` |
| `backend/app/routers/users.py` | `GET /api/users/{username}/in-common` (antes da rota `/{username}` não conflita: caminho mais longo) |
| `frontend/src/types.ts`, `services/api.ts` | tipos e `getInCommon(username)` |
| `frontend/src/components/profile/ProfileInCommon.vue` (novo) | seção "Em comum com você" |
| `frontend/src/views/UserProfileView.vue` | usa o componente quando não é o dono |
| `frontend/src/views/BooksView.vue`, `components/library/SharedStudiesList.vue` | `?aba=compartilhados&autor=` |
| testes | `backend/tests/test_users_in_common.py`, `frontend/tests/feature-100-amigos-em-comum.test.mjs` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Algoritmo

1. Resolver o perfil; 404 se não existe, se é o próprio visitante ou se há bloqueio (mesmas funções do perfil).
2. Se não há amizade aceita → `is_friend: false`.
3. Livros do amigo legíveis: `deleted_at IS NULL` e (`visibility in ('friends','public')` ou concessão `book` em
   `resource_permissions` para o visitante). Livros do visitante: todos os não excluídos.
4. Chave = `normalize_title_key(title)`; casar pelas chaves; se os dois têm autor, exigir o mesmo
   `first_author_surname_key`. Ordenar por título; cortar em 30 (`books_truncated`).
5. Estudos do amigo nesses livros: `deleted_at IS NULL`, filtrados com `can_read_study` (o número é pequeno), até 5
   por livro, mais recentes primeiro, com o total.
6. `shared_with_me_total` = total de `get_shared_studies_for_user(author=username, limit=1)`.

## Decisões

1. **Só o legível do outro lado**, para não vazar o acervo privado do amigo (nem por contagem).
2. **Sobrenome do primeiro autor** (reaproveitando a lógica de nome da F0.10.05 no Python) em vez do nome inteiro:
   "Machado de Assis" × "Assis, Machado de" casam.
3. **Endpoint dedicado** em vez de cruzar no navegador: o navegador não tem a lista de livros do amigo e não deve ter.
4. **Deep link na Biblioteca** em vez de tela nova: a aba Compartilhados já faz o trabalho.

## Riscos

| Risco | Mitigação |
|---|---|
| Falso positivo por título igual de obras diferentes | Exigir o sobrenome quando os dois têm autor |
| Acervo grande deixar a rota lenta | Selecionar só `id, title, author` dos dois lados e casar em memória por dicionário |
| Rota `/{username}/in-common` capturada por outra | Teste de rota; `/{username}` só casa um segmento |
