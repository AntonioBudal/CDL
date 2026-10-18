# EXP-013: Relatório de Resultados — Escala Automática da Página

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-18)
* **Executor:** Claude Code
* **Decisão:** regra incorporada ao [ADR-008](../../docs/adr/ADR-008-pipeline-de-referencia.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** As do pipeline do ADR-008 (Apache-2.0; léxico CC-BY-SA 4.0), `VERIFIED` conforme declarado. GNHK:
> CC-BY-4.0. BRESSAY: `LICENSE STATUS: NEEDS VALIDATION`, não embasa produto. Nenhum texto aparece neste relatório.

---

## 1. Resposta

**Sim.** Medir a altura das linhas na própria página e ampliá-la até as linhas terem cerca de 80 px recupera todo o
ganho da ampliação fixa, sem saber de onde veio a imagem: a redação na escala original passa de 45,8 % para
**35,9 %** de erro de caractere (ampliação fixa 3×: 36,2 %), e as fotos de celular, que quase nunca precisam de
ampliação, ficam iguais (27,3 % contra 27,5 %).

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — BRESSAY original + regra: no máximo 1 ponto pior que 3× fixo | **Confirmada** | 35,9 % contra 36,2 % (e 45,8 % sem ampliar) |
| H2 — GNHK não piora mais de 1 ponto | **Confirmada** | 27,3 % contra 27,5 % |
| H3 — ≤ 6 s por página na mediana | **Confirmada** | 5,6 s (BRESSAY) e 2,8 s (GNHK); p95 6,9 s e 4,5 s |

## 2. Resultados

Benchmark: [`BENCHMARK-20261018-exp-013-auto-scale.json`](../../evaluation/benchmarks/BENCHMARK-20261018-exp-013-auto-scale.json),
commit `56fa23e`, árvore limpa. Alvo escolhido na calibração: 80 px.

| Conjunto (teste) | CER de página | WER | Mediana do CER por página | Fatores escolhidos (páginas) | s por página | LDF 2.0 válido |
| :--- | ---: | ---: | ---: | :--- | ---: | ---: |
| BRESSAY, escala original | **35,9 %** | 67,7 % | 28,1 % | 1×: 19 · 2×: 50 · 3×: 33 · 4×: 83 | 5,6 | 185 / 185 |
| GNHK, fotos de celular | **27,3 %** | 53,5 % | 17,6 % | 1×: 165 · 2×: 5 · 3×: 2 | 2,8 | 172 / 172 |

### Calibração (só calibração: validação do BRESSAY e treino do GNHK)

| Alvo | BRESSAY validação | GNHK treino | Média | s por página (BRESSAY) |
| ---: | ---: | ---: | ---: | ---: |
| 48 px | 42,3 % | 28,3 % | 35,3 % | 3,9 |
| 64 px | 40,2 % | 28,3 % | 34,3 % | 5,3 |
| **80 px** | **39,7 %** | 28,6 % | **34,1 %** | 6,2 |

O alvo de 80 px ficou na borda da grade; a melhora entre 64 e 80 px já é pequena (0,2 ponto na média) e o custo
sobe. Um alvo maior não foi medido.

## 3. Limitações

* A altura das linhas vem de uma primeira detecção na imagem original; quando a página é muito pequena, essa
  primeira detecção pode errar a altura (19 páginas do BRESSAY ficaram em 1×).
* Duas detecções por página quando há ampliação: o custo cresce com o fator (até 6,9 s no p95).
* Mesmos limites de dados dos anteriores: não é caderno; português só em redações com licença em validação.

## 4. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-013/harness/prepare.py
uv run --frozen --project $h python experiments/EXP-013/harness/read.py --set cal-bressay --target 80   # etc.
uv run --frozen --project $h python experiments/EXP-013/harness/score.py --mode calibrate
uv run --frozen --project $h python experiments/EXP-013/harness/score.py --mode test --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-18`
