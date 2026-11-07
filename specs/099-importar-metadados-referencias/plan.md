# Implementation Plan: F0.10.06 — Importar: Faixa de Metadados da Obra e Ganchos para Referências

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-07 | **Status**: Executado em 2026-11-07

## Technical Context

Vue 3 + TypeScript; backend sem mudança (usa `PATCH /api/books/{id}`). Testes com `node:test`. Conferência no
servidor de validação (`serve.py` no scratchpad, banco temporário, dados fictícios).

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: auditoria só de código; dados fictícios |
| Banco ativo intocado, sem migração | OK: nenhuma mudança de banco ou de backend |
| Lote | 2ª feature do lote 2: build e testes novos |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/utils/referenceScopes.ts` (novo) | `parseLocator`, `buildReferenceScopes`, `abntCallWithLocator`, `countReferenceLines` |
| `frontend/src/components/import/ImportWorkMetaStrip.vue` (novo) | linha da obra, aviso, formulário "Completar dados do livro", prévia dos 3 escopos; emite `book-updated` |
| `frontend/src/views/ImportView.vue` | usa o componente com `selectedBook`, `selectedChapter`, `state.location` e `state.sections.references`; troca o livro atualizado em `books`; rótulo "Página ou localização" |
| testes | `frontend/tests/feature-099-importar-metadados.test.mjs`; ajustar vizinhos que fixem o rótulo "Localização" |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **3 escopos = obra, trecho, obras citadas**: é onde os dados já moram (livro; capítulo e localização do estudo;
   seção Referências). O 0.11 transforma esses escopos em CSL-JSON, BibTeX e ABNT/APA sem mudar a tela.
2. **Completar na própria faixa**: é o momento em que a falta importa; sem levar o leitor para outra página e sem
   perder o rascunho (o rascunho da importação não depende do livro).
3. **Página com meia-risca**: `p. 32–34` (normaliza `-` para `–` nos intervalos), como na ABNT.
4. **Sem tocar o backend**: o `PATCH` já valida ano e versão; o 409 vira mensagem.

## Riscos

| Risco | Mitigação |
|---|---|
| A faixa já é larga e quebra linha no celular | Segunda linha própria, com `flex-wrap`; conferir em 320 e 375 px |
| `version` ausente em livros antigos | Enviar `expected_version` só quando existir |
| Classes novas colidirem com globais | Prefixo `work-meta-` e busca no CSS global antes |
