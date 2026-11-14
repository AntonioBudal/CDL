# Implementation Plan: F0.11.11 — Cadernos de Síntese com Transclusão

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-14 | **Status**: Executado em 2026-11-14

## Technical Context

FastAPI + SQLAlchemy 2 + Alembic, Vue 3 + TS. **Migração `0039`** (tabela nova). Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado; a `0039` fica pendente com `0034`–`0038` |
| Isolamento | Cadernos e trechos resolvidos só do próprio leitor; origem alheia ou na lixeira não vaza |
| Portabilidade | Pacote da conta inclui as sínteses (LGPD) |
| Lote | 1ª feature do lote 3 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/migrations/versions/0039_synthesis_notebooks.py`, `models/synthesis_notebook.py`, `models/__init__.py` | tabela e modelo |
| `backend/app/services/synthesis_service.py` (novo) | CRUD, lixeira, analisador, resolução, exportação |
| `backend/app/schemas/synthesis.py` (novo), `routers/syntheses.py` (novo), `main.py` | API |
| `backend/app/services/export_service.py` | `sinteses/` no pacote da conta |
| `frontend/src/utils/synthesisEmbeds.ts` (novo) | analisador e divisão do texto |
| `frontend/src/views/SynthesesView.vue`, `views/SynthesisView.vue` (novos), `router/index.ts`, menus | telas e rotas |
| `frontend/src/components/synthesis/EmbedBlock.vue`, `InsertEmbedDialog.vue` (novos) | bloco e inserção |
| `frontend/src/services/api.ts`, `types.ts` | chamadas e tipos |
| `specs/076-…`, `specs/081-…` | rotas `syntheses` e `synthesis` |
| testes | `test_synthesis.py`, `test_migration_0039.py`, `feature-113-sinteses.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Marca em linha própria** (`![[…]]`, sintaxe próxima de Obsidian): fácil de ler no texto cru, de exportar e de
   dividir sem ambiguidade com as menções `[[…]]`.
2. **Resolução no servidor**, numa chamada só por caderno: o navegador não precisa abrir cada estudo, e o
   isolamento fica num lugar.
3. **Lixeira própria** dentro de Sínteses: não mexe na Lixeira geral (livros e estudos), que tem regras de
   hierarquia; mesma janela de 30 dias.
4. **Sem backlinks nesta fatia**: a tabela de menções é de estudo para estudo; fica para depois.

## Riscos

| Risco | Mitigação |
|---|---|
| Caderno grande com muitos trechos | Uma consulta por tipo (estudos, destaques) com `IN`; limite de 200 trechos |
| Vazamento de conteúdo alheio por id | Resolução filtra por `user_id` e lixeira; bloco "indisponível" igual para todos os casos |
| Rotas novas sem contrato de responsividade | Registrar nos contratos 076/081 |
