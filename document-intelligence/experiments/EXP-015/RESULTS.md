# EXP-015: Relatório de Resultados — Pipeline com Leitura Direta e Margem

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-22)
* **Executor:** Claude Code
* **Decisão:** incorporado ao [ADR-008](../../docs/adr/ADR-008-pipeline-de-referencia.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Pipeline só com componentes `VERIFIED` (Apache-2.0; léxico CC-BY-SA 4.0), conforme declarado; **o
> modelo de leitura é o original, sem o ajuste do EXP-014** — nada aqui depende do BRESSAY para funcionar. A
> medição em português usa o BRESSAY (`NEEDS VALIDATION`). Nenhum texto aparece neste relatório.

---

## 1. Resposta

**Sim.** Trocar só a forma de ler a linha — ONNX Runtime direto, com 640 px de margem à direita, no lugar do
reconhecedor do `rapidocr` — reduz o erro de caractere das redações de **35,9 % para 27,5 %** de ponta a ponta,
com o mesmo modelo e sem treino. Nas fotos em inglês, fica igual (27,4 %). O custo sobe: 7,4 s por página nas
redações.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — redações: CER de página cai ≥ 5 pontos | **Confirmada** | 35,9 % → 27,5 % (−8,4) |
| H2 — fotos: não piora mais de 1 ponto | **Confirmada** | 27,3 % → 27,4 % |
| H3 — ≤ 6 s por página e 100 % LDF válido | **Refutada em parte** | LDF 357 / 357; tempo 7,4 s (redações) e 3,1 s (fotos) |

## 2. Resultados

Benchmark: [`BENCHMARK-20261022-exp-015-pipeline-direct-reader.json`](../../evaluation/benchmarks/BENCHMARK-20261022-exp-015-pipeline-direct-reader.json),
commit `239b711`, árvore limpa. Escala automática com alvo de 80 px (EXP-013).

| Conjunto (teste) | CER de página | WER | Mediana do CER por página | s por página (mediana / p95) | LDF 2.0 válido |
| :--- | ---: | ---: | ---: | :--- | ---: |
| BRESSAY, escala original (português, com correção lexical) | **27,5 %** | 63,0 % | 25,6 % | 7,4 / 8,7 | 185 / 185 |
| GNHK, fotos (inglês) | 27,4 % | 55,5 % | 17,8 % | 3,1 / 5,2 | 172 / 172 |

Comparação de ponta a ponta nas redações: EXP-012 sem ampliar 45,8 % → EXP-013 com escala automática 35,9 % →
EXP-015 com leitura direta **27,5 %**.

## 3. Limitações

* O custo passou de 6 s nas redações: a margem de 640 px aumenta a largura lida em cada linha. Uma margem menor
  (320 px custou só 0,8 ponto a mais na validação do EXP-014) ou a leitura em lote reduziriam o tempo; não foi
  medido aqui.
* Nas fotos em inglês a margem não ajudou; o ganho é específico das linhas longas e baixas das redações.
* Mesmos limites de dados dos anteriores.

## 4. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-015/harness/read.py --set test-bressay --target 80
uv run --frozen --project $h python experiments/EXP-015/harness/read.py --set test-gnhk --target 80
uv run --frozen --project $h python experiments/EXP-015/harness/score.py --mode test --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-22`
