# EXP-020: Relatório de Resultados — Escala Automática Medida na Linha Inclinada

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-26)
* **Executor:** Claude Code
* **Decisão:** **não adotado**; a regra de escala do ADR-008 (altura pela caixa) fica. Corrige o diagnóstico do
  [EXP-019](../EXP-019/RESULTS.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Páginas do BRESSAY (`NEEDS VALIDATION`), leitor ajustado só experimental. Nenhum texto aparece
> neste relatório.

---

## 1. Resposta

**Não.** Medir a altura no quadrilátero faz a escala subir como previsto (na foto leve, as páginas em 4× passam
de 2 para 58), mas o erro não muda na foto leve (21,6 % → 21,6 %) e **piora** na forte (70,6 % → 74,1 %), com
menos linhas detectadas. A perda em condições de foto **não vem da escala**: o diagnóstico do EXP-019 estava errado.
Ela vem da própria degradação sobre o detector e o leitor.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — leve: CER cai ≥ 2 pontos | **Refutada** | 21,60 % → 21,57 % |
| H2 — forte: não piora | **Refutada** | 70,6 % → 74,1 % (+3,5) |
| H3 — digitalizada: até 0,3 ponto | **Confirmada** | 11,82 % → 11,80 % |
| H4 — 100 % LDF válido | **Confirmada** | 555 / 555 |

## 2. Resultados

Benchmark: [`BENCHMARK-20261026-exp-020-tilted-scale.json`](../../evaluation/benchmarks/BENCHMARK-20261026-exp-020-tilted-scale.json),
commit `b22510b`, árvore limpa. Leitor ajustado (só experimento); única mudança: altura da linha no quadrilátero.

| Condição | Escala pela caixa (EXP-017/019) | Escala no quadrilátero | Linhas detectadas (antes → agora) | Páginas em 4× (antes → agora) | s por página |
| :--- | ---: | ---: | :--- | :--- | ---: |
| Digitalizada | 11,8 % | 11,8 % | 5 623 → 5 622 | 83 → 94 | 7,2 |
| Foto leve | 21,6 % | 21,6 % | 5 406 → 5 389 | 2 → 58 | 6,6 |
| Foto forte | 70,6 % | **74,1 %** | 2 848 → 2 303 | 0 → 4 | 4,1 |

## 3. O que isso diz

* A inclinação de fato engana a medida da altura (EXP-019, §3), mas, nesta faixa de tamanhos, ampliar mais a
  página não ajuda o detector nem o leitor: na foto leve, a escala menor já bastava.
* Na foto forte, ampliar mais **amplia o ruído e o desfoque**, e o detector perde ainda mais linhas.
* Como na foto leve só 4 % das linhas deixam de ser detectadas (5 406 contra 5 623) e o erro quase dobra, o
  principal ponto de perda é o **leitor** diante de letras borradas e com ruído. O caminho provável é treinar o
  leitor com degradações de foto (aumento de dados), não mexer na escala.

## 4. Limitações

* Mesmas do EXP-019: páginas de baixa resolução (~520 × 570 px), degradação sintética, leitor experimental.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
foreach ($s in "clean", "light", "strong") {
  uv run --frozen --project $h python experiments/EXP-020/harness/read.py --set test-bressay-$s --reader ft }
uv run --frozen --project $h python experiments/EXP-020/harness/score.py --out evaluation/benchmarks/bench.json `
  --before-light 0.21602581722301967 --before-strong 0.706145842877358
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-26`
