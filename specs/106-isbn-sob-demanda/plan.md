# Implementation Plan: F0.11.04 — ISBN Sob Demanda

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-09 | **Status**: Executado em 2026-11-09

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3; `httpx` (já é dependência, usado nas capas). **Com migração** (`0036`).
Testes sem rede: `httpx.MockTransport` injetado no serviço.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK |
| Banco ativo | Não é tocado; o mesmo `upgrade head` do HANDOFF passa a aplicar 0034, 0035 e 0036 |
| Rede | Saída nova só a pedido, só do servidor, só para dois domínios fixos, com chave para desligar; landing atualizada para não prometer menos do que faz |
| Testes | Nenhum teste nem conferência no navegador vai à internet de verdade |
| Lote | 4ª feature do lote 1 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0036_book_isbn_publisher.py` (novo) | `isbn`, `publisher`, `publication_place`, índice |
| `backend/app/models/book.py`, `schemas/book.py` | campos e validação do ISBN |
| `backend/app/services/isbn_service.py` (novo) | normalização, consulta e mapeamento |
| `backend/app/routers/books.py` | `GET /books/isbn/{isbn}` (antes de `/{book_id}`) |
| `backend/app/core/config.py`, `routers/system.py` (ou o serviço do status) | `LEITORUM_ISBN_LOOKUP`; `isbn_lookup_enabled` no status |
| `backend/app/services/export_service.py` | campos na exportação |
| `frontend/src/types.ts`, `services/api.ts` | tipos e `lookupIsbn` |
| `frontend/src/components/books/IsbnLookup.vue` (novo) | campo, busca, sugestão, aplicar |
| `frontend/src/views/BooksView.vue`, `components/BookEditModal.vue`, `views/BookView.vue` | integração e exibição |
| `frontend/src/utils/citationFormatter.ts` | local e editora na referência |
| `frontend/src/components/landing/SovereigntySection.vue`, `TrustChallengeSection.vue` | textos de conexões externas |
| testes | `backend/tests/test_isbn_lookup.py`, `frontend/tests/feature-106-isbn.test.mjs`; ajustes nos que fixam textos |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Do servidor, não do navegador**: mantém a CSP `connect-src 'self'` e o Desafio F12 verdadeiro; o servidor controla
   os domínios e o tempo de espera.
2. **Sugestão, não gravação**: o leitor vê e aceita; campos preenchidos não são sobrescritos sem ele marcar.
3. **BrasilAPI primeiro**: melhor cobertura de livros brasileiros e já traz editora e cidade; Open Library completa os
   estrangeiros.
4. **Editora e local agora**: são o que falta para a referência ABNT e vêm de graça na mesma consulta.
5. **Chave para desligar** (`LEITORUM_ISBN_LOOKUP=off`): instalação sem rede ou quem não quer nenhuma saída.

## Riscos

| Risco | Mitigação |
|---|---|
| Formato das APIs mudar | Mapeamento tolerante; falha vira "não encontrado", nunca erro 500 |
| SSRF por redirecionamento | `follow_redirects=False`; URL montada só com o ISBN validado (dígitos) |
| Landing prometer menos do que o app faz | Texto e teste atualizados no mesmo commit |
