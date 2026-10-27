# EXP-021: Relatório de Resultados — Ajuste Fino com Degradações de Foto

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-26)
* **Executor:** Claude Code
* **Decisão:** **não adotado**; o leitor ajustado do EXP-014/017 continua como referência experimental. Evidência
  acrescentada ao [ADR-009](../../docs/adr/ADR-009-margem-de-leitura-e-ajuste-fino.md): as páginas pedidas para
  o produto devem ser **fotos**, não digitalizações
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Linhas e páginas do BRESSAY (`NEEDS VALIDATION`), degradadas localmente; modelo só experimental,
> em `models/exp-021/`, fora do Git. Nenhum texto aparece neste relatório.

---

## 1. Resposta

**Não.** Degradar metade das linhas de treino como foto quase não muda o erro em condições de foto: foto leve
21,6 % → 21,4 %, foto forte 70,6 % → 69,9 %. A digitalizada piora pouco (11,8 % → 12,1 %). Com este treino, o
leitor não aprende a ler fotos a partir de digitalizações degradadas artificialmente; os dados para o produto
precisam ser fotos de verdade.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — leve: CER cai ≥ 3 pontos | **Refutada** | 21,60 % → 21,38 % (−0,2) |
| H2 — digitalizada: não piora mais de 1 ponto | **Confirmada** | 11,82 % → 12,11 % (+0,3) |
| H3 — forte: CER cai | **Confirmada, sem efeito prático** | 70,61 % → 69,88 % (−0,7) |
| LDF 2.0 válido | **Confirmada** | 555 / 555 |

## 2. Resultados

Benchmark: [`BENCHMARK-20261026-exp-021-augmented-reader.json`](../../evaluation/benchmarks/BENCHMARK-20261026-exp-021-augmented-reader.json),
commit `b2df6b9`, árvore limpa. Pipeline do EXP-019 (escala pela caixa, ADR-008); única mudança: o modelo de leitura.

| Condição (185 páginas de teste) | Leitor ajustado (EXP-017/019) | Com degradações (EXP-021) | WER | Mediana por página | Linhas | s por página |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Digitalizada | 11,8 % | 12,1 % | 34,4 % | 10,5 % | 5 623 | 7,1 |
| Foto leve | 21,6 % | **21,4 %** | 47,9 % | 17,6 % | 5 406 | 6,2 |
| Foto forte | 70,6 % | 69,9 % | 84,9 % | 74,0 % | 2 848 | 3,2 |

**Treino** ([runs/aug.json](./runs/aug.json)): 647 páginas, 19 565 linhas, 392 passos de 16 (6 272 linhas vistas,
metade degradadas), 190 min em CPU, sem queda. CER de linha na validação limpa: 17,5 % → 16,1 % → 14,2 % →
**14,1 %** nos passos 98 / 196 / 294 / 392 (sem degradações, EXP-014 na mesma validação: 13,5 %). Exportação para ONNX com diferença
máxima de 7,5e-6 ([export.json](./export.json)).

## 3. O que isso diz

* Linhas detectadas e escala escolhida são idênticas às do EXP-019 (o detector não mudou); a diferença é só o
  leitor, e ela fica dentro de um ponto nas três condições.
* O aumento custou meio ponto na validação limpa e não comprou robustez. Com o mesmo orçamento de passos, metade
  das linhas degradadas é metade do treino em letra limpa.
* A degradação de linha reproduz desfoque, ruído, luz e JPEG, mas não o que a página degradada faz antes da
  leitura: perspectiva, reamostragem da página inteira e recortes imprecisos do detector. A perda em foto pode
  estar mais nesses efeitos do que nos que o aumento cobriu.
* Para o pedido de dados (EXP-018), isso decide o formato: **fotos de caderno com celular, transcritas linha a
  linha**. Digitalizações degradadas não substituem fotos.

## 4. Limitações

* Uma configuração de aumento (probabilidade 0,5, faixas do EXP-002) e um orçamento (392 passos), fixados antes
  de rodar; mais passos ou degradação na página inteira não foram testados.
* Mesmas do EXP-019: páginas de baixa resolução (~520 × 570 px), degradação sintética, leitor só experimental.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"; $ft = "experiments/EXP-014/envs/ft"
uv run --frozen --project $ft python experiments/EXP-021/harness/train.py
uv run --frozen --project $ft python experiments/EXP-021/harness/export.py
foreach ($s in "clean", "light", "strong") {
  uv run --frozen --project $h python experiments/EXP-021/harness/read.py --set test-bressay-$s }
uv run --frozen --project $h python experiments/EXP-021/harness/score.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-26`
