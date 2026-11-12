# Implementation Plan: F0.11.06 — Léxico de Conceitos e `[[conceito:…]]`

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-12 | **Status**: Executado em 2026-11-12

## Technical Context

FastAPI + SQLAlchemy 2, Vue 3. **Sem migração** (léxico derivado). Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado; sem migração |
| Isolamento | Só estudos do próprio leitor, fora da lixeira |
| Lote | 1ª feature do lote 2 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/concept_lexicon.py` (novo) | análise da seção Conceitos, chave, menções, agregação |
| `backend/app/schemas/concept.py` (novo) | lista, detalhe, candidatos |
| `backend/app/routers/concepts.py` (novo) + `main.py` | `GET /api/concepts`, `/api/concepts/candidates`, `/api/concepts/{key}` |
| `frontend/src/services/markdown.ts`, `components/MarkdownContent.vue` | `[[conceito:…]]` |
| `frontend/src/components/StudyEditorFields.vue` | autocompletar com conceitos |
| `frontend/src/views/LexiconView.vue`, `views/ConceptView.vue` (novos), `router/index.ts` | páginas e rotas |
| menus (`MobileMoreMenu`, `UserDropdown`) | entrada "Léxico" |
| `specs/076-…/contracts`, `specs/081-…` | registrar `lexicon` e `concept` |
| testes | `backend/tests/test_concept_lexicon.py`, `frontend/tests/feature-108-lexico.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Derivado, não tabela nova**: o texto do estudo continua sendo a fonte; nada fica desatualizado e não há migração.
2. **Formatos explícitos**: só linhas com "termo + separador + definição" ou título; melhor perder um conceito mal
   formatado do que encher o léxico de lixo.
3. **Prefixo `conceito:`**: separa conceito de estudo sem ambiguidade e mantém o `[[Título]]` atual intacto.
4. **Plural simples só por fusão**: "conceitos" junta com "conceito" apenas se "conceito" existir, para não estragar
   termos que terminam em "s".

## Riscos

| Risco | Mitigação |
|---|---|
| Acervo grande deixar a lista lenta | Só as colunas `id`, `title`, `concepts`, `chapter_id` e as seções de texto para as menções; paginação |
| Formatos de seção Conceitos não previstos | Testes com variações; ajustes futuros sem migração |
| Rotas novas sem contrato de responsividade | Registrar nos contratos 076/081 (armadilha do HANDOFF) |
