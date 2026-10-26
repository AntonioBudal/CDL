# EXP-019 — Leitura em Condições de Foto (especificação, plano e tarefas)

**Created**: 2026-10-26 · **Status**: `ACCEPTED` / `CONCLUÍDO` (por delegação, 2026-10-26; resultados em [RESULTS.md](./RESULTS.md))

**Input**: EXP-017 (redações BRESSAY digitalizadas: CER de página 27,5 % com o leitor original, 11,8 % com o
ajustado). A principal limitação registrada é que o número vem de **digitalizações**; o produto vai receber
**fotos de caderno**, que o usuário não vai fornecer agora.

## Pergunta e hipóteses

Quanto a leitura piora quando a mesma página chega como foto (fundo de mesa, perspectiva, curvatura perto da
lombada, luz irregular, sombra, desfoque, ruído, JPEG), e o ganho do ajuste fino se mantém?

- **H1:** com degradação **leve**, o leitor ajustado fica ≤ 15 % de CER de página.
- **H2:** com degradação **forte**, o leitor ajustado continua pelo menos 10 pontos melhor que o original.
- **H3:** 100 % LDF 2.0 válido nos dois níveis.

## Método

* Páginas: as 185 do teste do BRESSAY (EXP-007/015/017), mesma referência de texto.
* Degradação: `experiments/EXP-002/harness/pages/degrade.py` **sem alteração** (níveis `light` e `strong` do
  EXP-002), semente fixa por página. Imagens em `dataset/processed/exp-019/` (fora do Git).
* Pipeline: o do EXP-017 sem mudança — escala automática (alvo 80 px), fusão, margem de 640 px, correção lexical —
  com o leitor original (PP-OCRv6 small) e com o ajustado (`models/exp-017/rec-ft-bressay.onnx`, só experimento).
* Medida: CER e WER de página, como no EXP-015/017. Nenhum parâmetro novo; o nível "limpo" é o do EXP-017.
* Custo esperado: 4 rodadas × 185 páginas × ~8 s ≈ 1,7 h de CPU, depois do EXP-018.

## Tarefas

- [x] **T001** Gerar as páginas degradadas e os manifestos; harness (cópia do EXP-017) com a escolha do leitor;
  testes.
- [x] **T002** Rodar as quatro combinações; pontuar; relatório; registrar no ADR-009.
