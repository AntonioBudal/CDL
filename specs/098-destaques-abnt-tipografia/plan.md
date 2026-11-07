# Implementation Plan: F0.10.05 — Destaques: Cópia ABNT e Tipografia Citação × Anotação

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-07 | **Status**: Executado em 2026-11-07

## Technical Context

FastAPI + SQLAlchemy 2 e Vue 3. Sem migração, sem dependência nova. Testes de backend em `tmp_path`; frontend com
`node:test`. Conferência no servidor de validação (`serve.py` recriado no scratchpad, banco temporário, dados fictícios).

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: auditoria só de código; testes e navegador com dados fictícios |
| Banco ativo intocado, sem migração | OK: usa `kind = quote` e colunas que já existem em `books` |
| Lote | 1ª feature do lote 2: build e testes novos; suítes completas no fecho do lote |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/schemas/study_highlight.py` | `book_year`, `book_subtitle` em `HighlightLibraryItemRead` |
| `backend/app/services/study_highlight_service.py` | seleciona `Book.year` e `Book.subtitle` e repassa |
| `frontend/src/types.ts` | campos novos em `HighlightLibraryItem` |
| `frontend/src/utils/citationFormatter.ts` | chamada de autoria ABNT 2023, citação direta e indireta, referência NBR 6023 (texto e HTML), Markdown com ano |
| `frontend/src/utils/clipboard.ts` (novo) | `copyRich(text, html?)`: `ClipboardItem` com `text/html` quando houver; senão `writeText`; senão `textarea` |
| `frontend/src/components/highlights/HighlightCard.vue` | `isLiteral`; rótulo de origem; trecho literal × texto do leitor; controle "Citação literal"; menu com Esc, clique fora e foco; `aria-live`; `.quiet` |
| `HighlightCard.vue` (CSS do componente) | texto do leitor (sans, sem aspas) e rótulo de origem, com tokens; ficou no componente em vez do `style.css` global para não criar mais classes globais |
| `frontend/src/views/HighlightsLibraryView.vue` | `handleToggleLiteral` com `updateStudyHighlight(studyId, id, { kind })`, atualização otimista e reversão |
| testes | `backend/tests/test_highlight_library_book_meta.py`, `frontend/tests/feature-098-destaques-abnt.test.mjs`; ajustar `citation_formatter.test.mjs` e vizinhos que fixam o formato antigo |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **Citação literal é escolha do leitor**, não inferida da seção: as Referências podem ter paráfrase e o Resumo pode
   ter transcrição. Padrão = texto do leitor (o caso mais comum, e o mais seguro contra plágio involuntário).
2. **NBR 10520:2023** para a chamada (sobrenome em maiúsculas e minúsculas dentro dos parênteses); **NBR 6023** para
   a referência (SOBRENOME em caixa alta). Se preferir a chamada antiga, `(MANGUEL, 1997)`, basta dizer na aprovação.
3. **Sem página**: melhor uma chamada sem `p.` do que um número inventado.
4. **Voltar de `quote`** usa `note` se houver nota, senão `highlight` (o tipo original não fica guardado).
5. **HTML na área de transferência** só para o itálico do título na referência; o resto é texto puro.

## Riscos

| Risco | Mitigação |
|---|---|
| Testes antigos fixam o formato `(ALBERTO MANGUEL, Título, cap. …)` | Atualizar as asserções para o formato novo |
| `ClipboardItem` ausente (navegador antigo, HTTP sem TLS na rede local) | Queda para `writeText` e depois `textarea` |
| Classes novas colidirem com globais | Procurar no CSS global antes de nomear |
