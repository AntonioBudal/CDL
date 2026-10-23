# EXP-016 — Leitura em Lote no Pipeline (especificação, plano e tarefas)

**Created**: 2026-10-22 · **Status**: `ACCEPTED` / `CONCLUÍDO` (por delegação, 2026-10-22; resultados em [RESULTS.md](./RESULTS.md))

**Input**: EXP-015 (pipeline do ADR-008 com leitura direta e 640 px de margem): redações 27,5 % de CER de página,
fotos 27,4 %, mas **7,4 s por página** nas redações, acima da meta de 6 s.

## Pergunta e hipóteses

Ler as linhas de cada página em lotes, em vez de uma chamada do ONNX Runtime por linha, baixa o custo para a meta
sem piorar o texto?

- **H1:** redações (BRESSAY, escala original, escala automática): mediana ≤ 6 s por página.
- **H2:** CER de página não piora mais de 0,5 ponto em nenhum dos dois conjuntos (27,5 % e 27,4 %).
- **H3:** 100 % LDF 2.0 válido.

## Método

O pipeline do EXP-015 sem mudança na detecção, fusão, escala e recorte. Na leitura, os recortes da página são
ordenados pela largura depois de redimensionados a 48 px de altura e lidos em lotes de **8** (valor fixado antes
de rodar; não é ajustado no teste). Cada lote é preenchido com zeros até a largura da maior linha + 640 px, em
múltiplo de 32; linhas mais curtas recebem margem maior que 640 px, o que na validação do EXP-014 nunca piorou a
leitura (0 → 160 → 320 → 640 px só melhoraram). A decodificação gulosa é feita por linha, e o resultado volta à
ordem original. Conjuntos de teste do EXP-015, uma vez.

## Tarefas

- [x] **T001** Harness (cópia do EXP-015) com a leitura em lote e testes (lote igual à leitura individual no
  modelo real, em linhas sintéticas).
- [~] **T002** ~~Rodar os dois conjuntos de teste~~ — cancelada: as sondas (linhas fictícias e calibração) já
  mostraram a leitura em lote mais lenta; relatório e ADR-008 atualizados.
