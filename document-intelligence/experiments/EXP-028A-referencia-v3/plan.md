# Plano: EXP-028A — Referência v3 linha a linha e piso de ruído humano

**Spec:** [spec.md](./spec.md) · **Data:** 2026-11-20 · **Status:** `APPROVED`

## Contexto técnico

* Python puro do subprojeto (`uv`); reaproveita o harness do EXP-027 (`align.py`, `textnorm.py`, `split.py`,
  `score.py`) por importação a partir de `experiments/EXP-028A-referencia-v3/harness/`, sem copiar código.
* Reaproveita a ferramenta F-DI-13.01 (`tools/anotar/`): o rascunho por alinhamento grava `draft` e
  `draft_source: "importado:gemini-alinhado"` nos arquivos `di-annotation/1` pelo próprio `store.save_page`
  (mesma validação e hash).
* Sem modelo, sem download, sem GPU. Dados em `dataset/raw/anotacao/`, `dataset/raw/exp-028a/` (fora do Git).

## Verificação das regras

| Regra | Situação |
| :--- | :--- |
| Teste congelado só para medir | OK: v3 é a régua; nenhuma saída alimenta treino; sorteios gravados antes das medidas |
| Privacidade | OK: scripts imprimem só contagens e métricas; texto fica em `dataset/` |
| Experimento ≠ feature | OK: o rascunho por alinhamento fica no experimento; só vira ferramenta por spec própria |
| Escopo | OK: só `document-intelligence/` |

## Estrutura

```text
experiments/EXP-028A-referencia-v3/
├── spec.md, plan.md, tasks.md, report.md (no fim)
├── harness/
│   ├── paths.py         # raízes; importa o harness do EXP-027
│   ├── draws.py         # sorteio da 2ª passada (5/20) e do dev-val (10/31), semente "exp-028a"
│   ├── seed_drafts.py   # rascunho por alinhamento Gemini ↔ caixas do motor
│   ├── export_v3.py     # di-annotation → referencia-v3/pNN.txt + manifestos (hashes)
│   └── measure.py       # H1–H4 → results.json (só números)
├── splits/              # dev-val-manifest.json, second-pass.json (versionados; só ids e hashes)
└── tests/test_exp028a.py  # páginas fictícias
```

## Decisões

1. **Rascunho por alinhamento de palavras.** Concatena as palavras do motor por caixa (na ordem), alinha com as
   palavras do Gemini por programação dinâmica de palavras (troca custa a distância de caracteres normalizada,
   sem acentos; uma fórmula `$…$` é um token só) e atribui cada palavra do Gemini à caixa da palavra do motor
   com que alinhou; as que não alinham ficam com a caixa da palavra anterior. Pior caso
   (alinhamento ruim): a palavra vai para a caixa vizinha, e o autor move ao corrigir. Testado com página
   fictícia de quebra conhecida.
2. **Sorteios antes de medir**, com `split.allocate` (estratos escrita × fórmulas), semente fixa e hash do
   resultado no manifesto.
3. **H3 com as mesmas funções do EXP-027** (`align.score_page`, modo de página e de linhas), chamadas pelo
   `measure.py`: o `score.py` grava por cima do resultado do EXP-027, então não é rodado de novo.
4. **Normalização** de texto igual à do EXP-027 (`textnorm`; WER sem pontuação de borda, acentos e caixa
   preservados — regra aprovada).
5. **2ª passada cega com intervalo** de pelo menos 2 dias depois da 1ª da mesma página (data conferida pelo
   `at` das linhas), para reduzir memória.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Rascunho por alinhamento desalinhado em páginas com muito erro do motor | sobras visíveis; critério de abandono de 15 min/página nas 5 primeiras |
| Ancoragem no Gemini subestima H1 | controles: p14 (rascunho do motor) e 2ª passada cega |
| Cansaço do autor | sessões curtas; a ferramenta grava a cada linha |
| Sem originais para o EXP-028B | pedido explícito ao usuário (Folhas originais do Leitorum) |
