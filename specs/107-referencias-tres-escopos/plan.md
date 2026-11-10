# Implementation Plan: F0.11.05 — Referências em 3 Escopos

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-09 | **Status**: Executado em 2026-11-09

## Technical Context

Vue 3 + TypeScript, só frontend; reaproveita `citationFormatter.ts` (nomes, ABNT), `referenceScopes.ts` (escopos,
localizador) e `utils/clipboard.ts` (`copyRich`). Sem backend, sem migração, sem dependência nova.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: testes e navegador com dados fictícios |
| Banco ativo | Não é tocado |
| Nada inventado | Campos ausentes não aparecem; obras citadas exportadas como escritas |
| Lote | 5ª feature do lote 1 do 0.11: suítes completas no fecho |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/utils/referenceFormats.ts` (novo) | dados normalizados, ABNT/APA/BibTeX/CSL, trecho, chamadas, bibliografia |
| `frontend/src/components/references/ReferencePanel.vue` (novo) | painel com abas, copiar, baixar, avisos, obras citadas |
| `frontend/src/views/BookView.vue` | item "Referência" no menu e no cabeçalho; painel (obra) |
| `frontend/src/views/StudyView.vue` | item "Referência" no menu; painel (obra + trecho + obras citadas) |
| `frontend/src/views/BooksView.vue` | "Baixar bibliografia" com o formato |
| testes | `frontend/tests/feature-107-referencias.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` (fecho do lote) |

## Decisões

1. **No navegador**: os dados já estão carregados; nenhuma rota nova, nenhum risco no servidor.
2. **APA 7ª edição** e **NBR 6023** como padrões; BibTeX `@book` (compatível com BibLaTeX); CSL-JSON `type: book`
   (o formato que Zotero e Pandoc leem).
3. **Obras citadas só em texto**: estruturar linhas livres geraria referências erradas com cara de certas.
4. **Bibliografia sobre os livros filtrados**: o leitor escolhe o recorte com os filtros que já existem.

## Riscos

| Risco | Mitigação |
|---|---|
| Regras finas de APA/ABNT (muitos autores, sem data) | Casos cobertos em teste; o resto fica como está documentado no spec |
| BibTeX com caracteres especiais quebrando o LaTeX | Escapes e testes |
| Fecho do lote achar falhas antigas | Commit próprio, como combinado |
