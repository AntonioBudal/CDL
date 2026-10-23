# EXP-017: Relatório de Resultados — Teto de Ponta a Ponta com o Leitor Ajustado

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-22)
* **Executor:** Claude Code
* **Decisão:** evidência acrescentada ao [ADR-009](../../docs/adr/ADR-009-margem-de-leitura-e-ajuste-fino.md); o
  pipeline de referência do ADR-008 **não** muda (o modelo ajustado não pode ir para o produto)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** O leitor medido aqui foi ajustado no BRESSAY (`NEEDS VALIDATION`): **só experimento, nunca
> produto**. O arquivo `models/exp-017/rec-ft-bressay.onnx` fica fora do Git. Nenhum texto aparece neste relatório.

---

## 1. Resposta

Quase todo o ganho de linha do ajuste fino chega à página. Com detecção, fusão, recorte e correção lexical reais, o
erro de caractere das redações cai de **27,5 % para 11,8 %** (WER 63,0 % → 33,6 %), abaixo do critério de adoção de
12 % do ADR-008. O custo é a especialização: nas fotos em inglês o erro sobe de 27,4 % para 33,4 %.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — redações: CER de página ≤ 20 % | **Confirmada** | 27,5 % → 11,8 % |
| H2 — inglês: não piora mais de 3 pontos | **Refutada** | 27,4 % → 33,4 % (+6,0) |
| H3 — exportação fiel, 100 % LDF válido, mesmo custo | **Confirmada** | diferença ≤ 1,1e-5; LDF 357 / 357; 7,2 s e 3,0 s por página |

## 2. Resultados

Benchmark: [`BENCHMARK-20261022-exp-017-fine-tuned-pipeline.json`](../../evaluation/benchmarks/BENCHMARK-20261022-exp-017-fine-tuned-pipeline.json),
commit `d3d5224`, árvore limpa. Mesmo pipeline do EXP-015 (escala automática com alvo de 80 px, margem de 640 px);
só o arquivo do modelo de leitura muda.

| Conjunto (teste) | Leitor | CER de página | WER | Mediana do CER por página | s por página (mediana / p95) | LDF 2.0 válido |
| :--- | :--- | ---: | ---: | ---: | :--- | ---: |
| BRESSAY (português, com correção lexical) | original (EXP-015) | 27,5 % | 63,0 % | 25,6 % | 7,4 / 8,7 | 185 / 185 |
| BRESSAY (português, com correção lexical) | **ajustado** | **11,8 %** | **33,6 %** | **10,0 %** | 7,2 / 8,4 | 185 / 185 |
| GNHK, fotos (inglês) | original (EXP-015) | 27,4 % | 55,5 % | 17,8 % | 3,1 / 5,2 | 172 / 172 |
| GNHK, fotos (inglês) | ajustado | 33,4 % | 66,9 % | 25,1 % | 3,0 / 4,9 | 172 / 172 |

**Exportação** ([`export.json`](./export.json)): `best.pt` do EXP-014 → ONNX com lote e largura dinâmicos; diferença
máxima para o PyTorch de 1,4e-6 a 1,1e-5 em larguras de 320 a 2240 px. A leitura volta a custar o mesmo que o
modelo original (o EXP-014 media 280 ms por linha no PyTorch).

Comparação de ponta a ponta nas redações: EXP-012 45,8 % → EXP-013 35,9 % → EXP-015 27,5 % → **EXP-017 11,8 %**.

## 3. Limitações

* **É um teto dentro do mesmo acervo.** A divisão oficial de teste do BRESSAY separa autores, mas o tipo de texto
  (redação), o papel e a digitalização são os mesmos do treino. Em fotos de caderno, com outro papel, luz e
  assuntos, o número deve ser pior; não foi medido.
* O ajuste em português piora o inglês. Um ajuste para o produto deveria misturar dados das duas línguas, ou
  manter o modelo original como alternativa para texto que não seja português.
* O custo continua em 7,2 s por página nas redações (ver EXP-016).
* Mesmos limites de dados dos anteriores.

## 4. Consequências

* O ajuste fino é o caminho que leva o português abaixo do critério de adoção, agora medido de ponta a ponta.
  Falta só o dado com licença para produto; o procedimento (EXP-014) e a exportação (aqui) estão prontos para
  repetir.
* **Quanto dado pedir:** o EXP-014 usou cerca de 19 mil linhas de treino em menos de uma época. Uma estimativa do
  mínimo útil exigiria uma curva de aprendizado (treinar com frações do treino), que é um experimento possível
  sem dados novos.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project experiments/EXP-014/envs/ft python -I experiments/EXP-017/harness/export.py
uv run --frozen --project $h python experiments/EXP-017/harness/read.py --set test-bressay --target 80
uv run --frozen --project $h python experiments/EXP-017/harness/read.py --set test-gnhk --target 80
uv run --frozen --project $h python experiments/EXP-017/harness/score.py --mode test --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-22`
