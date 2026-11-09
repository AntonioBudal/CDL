# Implementation Plan: F0.11.01 — Estados de Leitura do Livro

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-09 | **Status**: Executado em 2026-11-09

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3. **Com migração** (`0034`). Sem dependência nova. Testes em `tmp_path`; o
servidor de validação usa banco temporário (`serve.py` roda `upgrade head`).

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: auditoria só de código; testes e navegador com dados fictícios |
| Banco ativo | **Não é tocado nesta conversa.** A migração só vale no banco ativo quando você rodar o script (ou pedir que eu rode), com backup verificado antes |
| Migração | Aditiva (colunas nulas), reversível, sem preencher nada por suposição |
| Lote | 1ª feature do lote 1 do 0.11: build e testes novos; suítes completas no fecho do lote |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0034_book_reading_state.py` (novo) | colunas (`ADD COLUMN`), `CHECK` na coluna, índice; `downgrade` com `DROP COLUMN` |
| `backend/app/models/book.py` | três colunas |
| `backend/app/schemas/book.py` | `BookReadingState = Literal[...]`; campos em `BookPatch` e `BookRead` |
| `backend/app/routers/books.py` (ou serviço de livros) | datas automáticas, validação fim ≥ início, ocultar para não dono |
| `backend/app/services/export_service.py` | campos no JSON e no Markdown |
| ~~`scripts/migrar_com_backup.py`~~ | não criado: o snapshot pré-migração do `migrations/env.py` já cobre (ver spec, US4) |
| `frontend/src/types.ts`, `services/api.ts` | tipos e payload |
| `frontend/src/components/books/BookReadingState.vue` (novo) | seletor + datas |
| `frontend/src/views/BookView.vue` | usa o componente (só dono) |
| `frontend/src/views/BooksView.vue`, `components/library/*`, `components/LibraryToolbar.vue`, `composables/useLibraryFilter.ts` | selo e filtro |
| testes | `backend/tests/test_book_reading_state.py`, `frontend/tests/feature-103-estados-leitura.test.mjs` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md`, `docs/contexto/HANDOFF.md` | registro e procedimento de implantação |

## Decisões

1. **Estado no livro, não no estudo**: o `reading_status` do estudo é o andamento do fichamento; misturar os dois
   confundiria os filtros que já existem.
2. **Nulo como padrão**: livros antigos ficam "sem estado"; nada de deduzir "Lido" de estudos concluídos.
3. **Datas automáticas só quando vazias**: ajuda sem sobrescrever o que o leitor escreveu.
4. **Estado privado** na API para terceiros: evita vazar hábitos de leitura por compartilhamento de livro.
5. **Script de migração com backup** em vez de mudar o `instalar.py`: o instalador continua igual para instalações
   novas; o script é o caminho seguro para bancos com dados (este e as próximas migrações do 0.11).
6. **Serviço parado** antes de migrar: evita o servidor gravar durante a cópia e a migração.

## Riscos

| Risco | Mitigação |
|---|---|
| Serviço não sobe depois do push até migrar | Procedimento claro no relatório e no HANDOFF; script único |
| Migração falhar no meio | Backup verificado antes; SQLite faz a migração numa transação; o script mostra o caminho do backup para restaurar |
| Testes antigos de livros fixarem o conjunto exato de campos do `BookRead` | Ajustar as asserções no mesmo commit |
| Sincronização (`sync_service`) comparar campos de livro | Conferir e incluir os novos campos se a sincronização serializar livros |
