# EXP-019: Relatório de Resultados — Leitura em Condições de Foto

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-26)
* **Executor:** Claude Code
* **Decisão:** evidência acrescentada ao [ADR-009](../../docs/adr/ADR-009-margem-de-leitura-e-ajuste-fino.md);
  abre o [EXP-020](../EXP-020/spec.md) (escala medida na linha inclinada)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Páginas do BRESSAY (`NEEDS VALIDATION`) degradadas localmente; leitor ajustado só experimental.
> Imagens em `dataset/processed/exp-019/`, fora do Git. Nenhum texto aparece neste relatório.

---

## 1. Resposta

A mesma página fotografada lê bem pior que digitalizada, e quase toda a perda vem **antes** da leitura. Com
degradação leve, o leitor ajustado vai de 11,8 % para **21,6 %** de CER de página; o ganho do ajuste sobre o
original se mantém (39,3 % → 21,6 %). Com degradação forte, a detecção perde metade das linhas e os dois leitores
passam de 70 %.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — leve, leitor ajustado ≤ 15 % | **Refutada** | 21,6 % |
| H2 — forte, ajustado ≥ 10 pontos melhor que o original | **Refutada** | 77,9 % → 70,6 % (7,3 pontos) |
| H3 — 100 % LDF 2.0 válido | **Confirmada** | 740 / 740 |

## 2. Resultados

Benchmark: [`BENCHMARK-20261026-exp-019-photo-conditions.json`](../../evaluation/benchmarks/BENCHMARK-20261026-exp-019-photo-conditions.json),
commit `60f5df6`, árvore limpa. Pipeline do EXP-017 sem mudança; degradação do EXP-002 sem mudança.

| Condição (185 páginas de teste) | Leitor | CER de página | WER | Mediana por página | Linhas detectadas | s por página |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| Digitalizada (EXP-015 / EXP-017) | original | 27,5 % | 63,0 % | 25,6 % | 5 623 | 7,4 |
| Digitalizada (EXP-015 / EXP-017) | ajustado | 11,8 % | 33,6 % | 10,0 % | 5 623 | 7,2 |
| Foto leve | original | 39,3 % | 73,6 % | 36,2 % | 5 406 | 6,4 |
| Foto leve | ajustado | **21,6 %** | 47,6 % | 16,9 % | 5 406 | 6,3 |
| Foto forte | original | 77,9 % | 92,0 % | 84,1 % | 2 848 | 3,3 |
| Foto forte | ajustado | 70,6 % | 84,9 % | 76,4 % | 2 848 | 3,4 |

**Escala automática escolhida (páginas por fator):** digitalizada 4× 83, 3× 33, 2× 50, 1× 19; leve 4× 2, 3× 67,
2× 73, 1× 43; forte 3× 9, 2× 68, 1× 108.

## 3. Diagnóstico: a escala automática erra em linhas inclinadas

Comparando, página a página, as linhas da foto leve com as da digitalização (só alturas, nenhum texto):

* a altura da **caixa alinhada aos eixos** sobe 40 % (mediana da razão);
* a altura do **quadrilátero** da linha sobe só 10 %;
* 129 de 185 páginas recebem escala **menor** que na digitalização, nenhuma maior.

A regra do EXP-013 mede a altura pela caixa; numa linha inclinada pela perspectiva, a caixa é mais alta que a
escrita, a página é menos ampliada e as letras chegam pequenas ao detector e ao leitor. Na foto forte, com 108
páginas em escala 1, a detecção perde metade das linhas. A correção (altura medida no quadrilátero, sem
parâmetro novo) é o [EXP-020](../EXP-020/spec.md).

## 4. Limitações

* **Resolução.** As páginas do BRESSAY têm ~520 × 570 px; a degradação (desfoque, ruído, JPEG) aplicada a uma
  imagem tão pequena é mais destrutiva que numa foto de celular de 12 MP, em que cada linha tem muito mais pixels.
  O nível forte deve ser lido como pior caso.
* Degradação sintética: não reproduz papel pautado, tinta azul, dobras ou reflexo.
* Mesmos limites de dados dos anteriores; o leitor ajustado é só experimental.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-019/harness/prepare.py
foreach ($s in "light", "strong") { foreach ($r in "ft", "original") {
  uv run --frozen --project $h python experiments/EXP-019/harness/read.py --set test-bressay-$s --reader $r } }
uv run --frozen --project $h python experiments/EXP-019/harness/score.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-26`
