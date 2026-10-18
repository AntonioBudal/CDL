# EXP-012: Relatório de Resultados — Pipeline Integrado de Ponta a Ponta (Foto → LDF 2.0)

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-18)
* **Executor:** Claude Code
* **Decisão:** [ADR-008](../../docs/adr/ADR-008-pipeline-de-referencia.md) (`ACCEPTED` por delegação)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** PP-OCRv6 small det e rec via `rapidocr` (Apache-2.0), léxico `wordfreq` (dados CC-BY-SA 4.0) —
> `LICENSE STATUS: VERIFIED`, conforme declarado. GNHK: CC-BY-4.0. BRESSAY: `LICENSE STATUS: NEEDS VALIDATION`,
> não embasa produto. Nenhum texto de referência ou lido aparece neste relatório.

---

## 1. Resposta

**O pipeline funciona de ponta a ponta, localmente, e sempre entrega LDF 2.0 válido — mas a qualidade do texto
depende muito da resolução da página.** Em fotos de celular (inglês), recupera o texto com 27,5 % de erro de
caractere (mediana por página 17,6 %). Em redações em português, 36,2 % com a página ampliada 3× e 45,8 % na
escala original: a regra de ampliar só a linha não substitui ampliar a página.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — BRESSAY 3× com correção: CER ≤ 35,7 % | **Refutada, por pouco** | 36,2 % (EXP-009: 36,7 %) |
| H2 — BRESSAY nativo no máximo 3 pontos pior que 3× | **Refutada** | 45,8 % contra 36,2 % (+9,6) |
| H3 — fotos do GNHK: CER de página ≤ 25 % | **Refutada, por pouco** | 27,5 % (mediana por página 17,6 %) |
| H4 — ≤ 6 s por página e ≤ 2 GiB | **Confirmada** | 2,7–5,2 s na mediana; pico de 881 MiB |
| H5 — 100 % LDF 2.0 válido | **Confirmada** | 542 de 542 páginas, com texto e confiança em 13.618 linhas |

## 2. Resultados

Benchmark: [`BENCHMARK-20261018-exp-012-pipeline.json`](../../evaluation/benchmarks/BENCHMARK-20261018-exp-012-pipeline.json),
commit `7a852cf`, árvore limpa.

| Variante | Páginas | CER sem → com correção | WER sem → com correção | Mediana do CER por página | s por página (mediana / p95) | Pico |
| :--- | ---: | :--- | :--- | ---: | :--- | ---: |
| BRESSAY 3× | 185 | 36,7 % → **36,2 %** | 74,6 % → **67,9 %** | 28,7 % | 5,2 / 6,5 | 881 MiB |
| BRESSAY nativa | 185 | 46,1 % → **45,8 %** | 79,0 % → **73,8 %** | 34,9 % | 2,8 / 5,3 | 644 MiB |
| GNHK (inglês, celular) | 172 | 27,5 % (sem correção) | 54,0 % | 17,6 % | 2,7 / 3,6 | 783 MiB |

* Na página nativa do BRESSAY, 3.162 das 5.532 linhas detectadas tinham menos de 32 px e foram ampliadas 2× —
  ainda assim o resultado ficou 9,6 pontos pior que ampliar a página inteira. A diferença vem também da
  **detecção**, que trabalha melhor com a página ampliada (o EXP-008 calibrou e mediu a fusão na escala 3×).
* No GNHK, só 55 de 2.461 linhas precisaram de ampliação: as fotos, com 2.048 px no lado maior, já têm linhas
  altas o bastante.
* A correção lexical tira 5 a 7 pontos de WER no português e quase nada de CER, como no EXP-011.

## 3. O que isso significa para o produto

* A cadeia inteira — foto, linhas, leitura, correção, LDF 2.0 — roda local, em CPU, em menos de 6 s por página,
  sem nenhum serviço externo. É o primeiro artefato que poderia alimentar uma prévia no site.
* **A resolução de entrada é parte do contrato:** as linhas precisam chegar ao detector com algo como 50 a 70 px
  de altura. Fotos de celular atuais satisfazem isso; digitalizações pequenas precisam ser ampliadas antes.
* O texto em português ainda tem um terço dos caracteres errado. Para um primeiro teste, faz sentido mostrar o
  texto lido **como rascunho editável**, com a correção humana gravada como JSON Patch no LDF (ADR-004), e não
  como texto final.

## 4. Desvios e limitações

* Executado por delegação, sem aprovação intermediária.
* Nenhuma das variantes é caderno de estudo brasileiro fotografado; GNHK é em inglês; BRESSAY, licença em
  validação.
* A ordem de leitura é de cima para baixo; serve para estes conjuntos (sem regiões laterais), não para cadernos com
  notas de margem.
* A referência de página do GNHK é derivada das palavras anotadas (ordem por índice de linha); diferenças de ordem
  entre o que o pipeline lê e a anotação contam como erro.
* Uma execução por variante.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-012/harness/prepare.py
uv run --frozen --project $h python experiments/EXP-012/harness/read.py --set bressay-x3   # e bressay-native, gnhk
uv run --frozen --project $h python experiments/EXP-012/harness/run.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-18`
