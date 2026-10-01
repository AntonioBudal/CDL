# Fixtures do EXP-001 — Linhas Sintéticas em PT-BR

Camada sintética do EXP-001: frases **fictícias** em português renderizadas em imagem de linha. Serve para
validar o harness e medir custo (tempo, memória). **Não** vale como métrica de HTR real
(`docs/dataset-and-evaluation.md` §3).

## Fonte de renderização

| Fonte | Origem | Licença | Status |
| :--- | :--- | :--- | :--- |
| Caveat (Regular) | <https://github.com/googlefonts/caveat> (`fonts/ttf/Caveat-Regular.ttf`) | SIL Open Font License 1.1 | `LICENSE STATUS: VERIFIED` (consulta em 2026-09-30) |

A OFL permite uso e redistribuição junto com o texto da licença, que acompanha a fonte em `fonts/OFL.txt`.

* Arquivo: `fonts/Caveat-Regular.ttf` (297.900 bytes), baixado do commit `59745e818ef7973e11e70cb1358d0e902b56c5fc`.
* SHA-256: `7af58d70e539c9195cc328617a68c9961ed804a4404b0b818989ba7c013e8776`

## Conteúdo

* `sentences.json` — 200 frases fictícias cobrindo o alfabeto exigido; geradas por
  `experiments/EXP-001/harness/build_sentences.py` (seed 1234).
* `synthetic-manifest.json` — uma entrada por linha (imagem, SHA-256, texto, dimensões), gerado por
  `experiments/EXP-001/harness/synth.py`.
* As imagens ficam em `dataset/processed/exp-001/synthetic/` (fora do Git) e são regeneráveis. Os SHA-256 do
  manifesto valem para Pillow 12.3.0; outra versão do renderizador pode produzir bytes diferentes.

Nenhum texto do acervo do usuário ou de cadernos reais entra aqui.
