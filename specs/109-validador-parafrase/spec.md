# Feature Specification: F0.11.07 — Validador de Paráfrase

**Feature Branch**: `109-validador-parafrase`

**Created**: 2026-11-12

**Status**: Concluída em 2026-11-12

**Input**: Item "validador de paráfrase (Jaccard)" do Roadmap 0.11 no HANDOFF. Segunda feature do lote 2 do 0.11.
**Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-12, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Fichamento (`source_response`) | Na importação é o texto colado **que vira as próprias seções**; na digitalização é a **página manuscrita do leitor**. Não é texto do livro (correção da auditoria, feita na execução: compará-lo acusaria o texto do próprio leitor) | `models/study.py`, `composables/useImportDraft.ts`, `useDigitizeDraft.ts` |
| Citações literais | Destaques com `kind = "quote"` (F0.10.05) marcam trechos que o leitor declarou serem citação direta | `models/study_highlight.py`, `HighlightCard.vue` |
| Capturas do livro | Capturas da Mesa com livro (e capítulo, F0.11.02), inclusive as vindas do Kindle/Kobo (F0.11.03), costumam ser texto literal do livro | `models/inbox_capture.py` |
| Texto do leitor | Resumo, Explicação, Conceitos e Referências, editados em `StudyEditorFields` (tela de edição e de importação) | `views/StudyEditView.vue`, `views/ImportView.vue` |
| Verificação de paráfrase | **Não existe.** Nada avisa quando o "resumo" é, na prática, uma cópia da fonte sem aspas nem citação | — |

**Decisão de dados:** sem migração e sem guardar resultado. A verificação é feita **no navegador**, sobre o texto que
está no editor (inclusive o que ainda não foi salvo). O servidor só entrega as fontes: **texto do livro** guardado pelo
leitor (capturas do mesmo livro e citações literais de outros estudos do mesmo livro) e as citações literais marcadas
no próprio estudo, que valem como citação declarada. O fichamento fica de fora.

---

## 2. User Stories

### US1 — Saber se o texto está perto demais da fonte (P1)

**Acceptance**:
1. Na edição do estudo e na importação, um painel **"Verificar paráfrase"** (fechado por padrão, abre com um botão
   `.quiet`) compara as seções **Resumo, Explicação e Conceitos** com o texto do livro.
2. A comparação é por frase do leitor contra cada trecho da fonte, usando **Jaccard de trigramas de palavras**
   (sem acento, caixa e pontuação; frases com menos de 6 palavras são ignoradas). Para cada frase vale a maior
   semelhança encontrada.
3. Cada frase recebe um nível:
   - **Cópia** (≥ 0,50 ou uma sequência de 12+ palavras idênticas à fonte): "Está igual ao texto do livro. Use aspas
     e cite a página, ou reescreva com suas palavras."
   - **Muito próxima** (0,25 a 0,49): "Ainda segue a fonte de perto. Tente mudar a estrutura, não só trocar palavras."
   - Abaixo de 0,25 não aparece.
4. O painel mostra um resumo ("3 frases para revisar em 24; 1 cópia") e a lista das frases sinalizadas, cada uma com a
   seção, o nível (texto + ícone, nunca só cor), a porcentagem e o trecho da fonte mais parecido, com as palavras em
   comum marcadas.
5. Sem nenhuma frase sinalizada: "Nenhuma frase muito próxima da fonte."

### US2 — Citação declarada não é acusada (P1)

**Acceptance**:
1. Frase entre aspas (`"…"`, `“…”`, `«…»`) ou em bloco de citação Markdown (`> …`) **não** é sinalizada: é citação
   direta assumida. Frase que contém um trecho marcado como **citação literal** neste estudo (destaque `quote`, 3+
   palavras, na mesma seção) também fica de fora.
2. Se a frase sinalizada não tem aspas, o painel oferece **"Marcar como citação"**: envolve a frase em aspas no editor
   e acrescenta a chamada ABNT com o livro e o ano já conhecidos (`(SOBRENOME, ano, p. )`), deixando a página para o
   leitor preencher.
3. Ao reescrever, o painel se atualiza sozinho (com atraso de 400 ms após parar de digitar).

### US3 — Fontes usadas (P2)

**Acceptance**:
1. O painel diz quais fontes entraram ("N citações literais de outros estudos · N capturas do livro") e cada frase
   sinalizada diz de onde veio o trecho ("Captura deste capítulo", "Captura deste livro", "Citação literal em «…»").
2. Sem nenhuma fonte, o painel aberto explica: "Ainda não há texto deste livro para comparar. Capture trechos na Mesa ou
   importe os destaques do Kindle ou do Kobo."
3. Na importação, as fontes são as do livro do capítulo escolhido (o texto colado não é fonte).

### Edge Cases

- Fonte muito grande: o índice invertido de trigramas leva só às frases da fonte com trigramas em comum, e a frase do
  leitor é comparada com janelas de 1 a 3 frases consecutivas dessas candidatas (teste com 200 mil palavras: índice
  em menos de 3 s, verificação em menos de 300 ms).
- Texto com Markdown (negrito, listas, links, `[[menções]]`): limpo antes da comparação.
- Seção Referências não é verificada (é onde ficam citações e obras).
- Estudo de outro leitor ou na lixeira: a rota de fontes responde 404; estudos na lixeira não são fonte.
- Celular: painel em uma coluna, alvos de 44 px.

---

## 3. Requirements

- **FR-001**: `frontend/src/utils/paraphraseCheck.ts` (puro): `normalizeWords`, `stripMarkdown`, `splitSentences`,
  `withoutDeclaredQuotes`, `trigrams`, `jaccard`, `longestCommonRun`, `buildSourceIndex(sources)`,
  `checkParaphrase(sections, index, declaredQuotes)` → `{ flagged: [{ section, sentence, level, score, run,
  sourceLabel, sentenceParts, sourceParts }], total, copies }`; `abntQuoteCall`, `markAsQuote`.
- **FR-002**: `GET /api/studies/{id}/paraphrase-sources` → `{ sources: [{ kind: "quote" | "capture", label, text }],
  declared_quotes: [{ section, text }] }`, só para o dono do estudo, fora da lixeira.
  `GET /api/chapters/{id}/paraphrase-sources` para a importação (fontes do livro do capítulo, sem citações declaradas).
- **FR-003**: `components/studies/ParaphrasePanel.vue` usado em `StudyEditView` e `ImportView`; "Marcar como citação"
  altera a seção pelo mesmo `v-model:sections`.
- **FR-004**: Só tokens existentes, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas; `aria-live="polite"` no resumo.

## 4. Success Criteria

- **SC-001**: Testes de frontend do utilitário: cópia literal (score ≥ 0,5), troca de poucas palavras (muito próxima),
  paráfrase real (não sinalizada), frase entre aspas e em `>` ignorada, frase curta ignorada, sequência de 12 palavras
  vira cópia, Markdown limpo, fonte grande em tempo razoável (< 300 ms em 200 mil palavras no teste), "Marcar como
  citação" gera aspas e chamada ABNT.
- **SC-002**: Testes de backend: fontes do dono (capturas do livro, citações de outros estudos; fichamento fora),
  citações do próprio estudo como declaradas, outro leitor 404, lixeira 404 e fora das fontes, sem fonte → listas
  vazias.
- **SC-003**: Navegador (dados fictícios): edição e importação, sinalização, atualização ao reescrever, "Marcar como
  citação"; 1366 e 375 px; contraste nos 10 temas.
- **SC-004**: Build e testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- Comparar com textos de fora do acervo (internet, outros leitores) ou com outros estudos do próprio leitor.
- Sinônimos, lematização ou modelos de linguagem: a medida é lexical, de propósito, e o painel diz isso.
- Bloquear o salvamento: o validador só avisa.
