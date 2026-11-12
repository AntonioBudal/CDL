# Implementation Plan: F0.11.07 — Validador de Paráfrase

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-12 | **Status**: Executado em 2026-11-12

## Technical Context

FastAPI + SQLAlchemy 2, Vue 3 + TS. **Sem migração.** Cálculo no navegador; testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado; sem migração |
| Isolamento | Fontes só do dono do estudo; texto não sai do navegador para nenhum serviço externo |
| Lote | 2ª feature do lote 2 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `frontend/src/utils/paraphraseCheck.ts` (novo) | normalização, frases, trigramas, Jaccard, maior sequência comum, índice, verificação, `markAsQuote` |
| `backend/app/services/paraphrase_sources.py` (novo) | reunir capturas do livro e citações literais de outros estudos; citações do próprio estudo como declaradas |
| `backend/app/schemas/paraphrase.py` (novo) | `ParaphraseSource`, `ParaphraseSources` |
| `backend/app/routers/paraphrase.py` (novo) + `main.py` | `GET /studies/{id}/paraphrase-sources`, `GET /chapters/{id}/paraphrase-sources` |
| `frontend/src/services/api.ts`, `types.ts` | chamadas e tipos |
| `frontend/src/components/studies/ParaphrasePanel.vue` (novo) | painel, resumo, lista, "Marcar como citação" |
| `frontend/src/views/StudyEditView.vue`, `views/ImportView.vue` | uso do painel |
| testes | `backend/tests/test_paraphrase_sources.py`, `frontend/tests/feature-109-parafrase.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **No navegador**: verifica o texto ainda não salvo, sem ida ao servidor a cada tecla e sem guardar nada.
2. **Trigramas de palavras + maior sequência comum**: Jaccard de trigramas pega troca de poucas palavras; a sequência
   de 12+ palavras pega a cópia de um trecho dentro de uma frase longa, que o Jaccard sozinho dilui.
3. **Frase do leitor contra janelas de 1 a 3 frases da fonte**: o leitor costuma fundir frases da fonte, mas uma
   janela fixa de 3 diluiria a cópia de uma frase só. O índice invertido de trigramas evita comparar com todas.
4. **Limiares 0,50 e 0,25**: ponto de partida conservador, em constantes nomeadas, ajustáveis sem migração.
5. **Citação declarada nunca é sinalizada**: aspas, `>` ou destaque `quote` no próprio estudo contam como citação
   assumida; o validador incentiva citar, não punir.
6. **Fichamento fora das fontes** (decidido na execução): `source_response` é o texto que vira as seções na importação
   ou a página manuscrita na digitalização; usá-lo acusaria o texto do próprio leitor. Só entra texto do livro.

## Riscos

| Risco | Mitigação |
|---|---|
| Falso positivo em termos técnicos repetidos | Frases com menos de 6 palavras ignoradas; nível "muito próxima" é só aviso |
| Fonte enorme travar a digitação | Atraso de 400 ms; índice invertido; teste de tempo com 200 mil palavras |
| "Marcar como citação" achar a frase errada | Substitui só a primeira ocorrência exata na seção indicada; se não achar, avisa e não mexe |
