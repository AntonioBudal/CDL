# EXP-022: Relatório de Resultados — Páginas do BRESSAY Impressas e Fotografadas

* **Status:** `ACCEPTED` / `CONCLUÍDO` com ressalva (executado e aceito por delegação permanente do usuário,
  2026-10-27)
* **Executor:** Claude Code
* **Decisão:** nenhuma mudança de pipeline nem de ADR; a pergunta sobre a câmera crua **continua aberta**
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Páginas do BRESSAY (`NEEDS VALIDATION`) impressas e fotografadas pelo usuário só para teste
> local; leitor ajustado só experimental. Imagens fora do Git; nenhum texto aparece neste relatório.

---

## 1. Resposta

Nas 15 imagens entregues, a IA lê **como na digitalização**: leitor ajustado 11,0 % de CER de página (mesmas
páginas digitalizadas: 10,7 %), leitor original 24,3 % (digitalizadas: 24,1 %). Saída 100 % LDF 2.0 válida,
~7 s por página, pico de 796 MiB.

**Ressalva principal:** as imagens não guardam sinal de câmera. Chegaram depois de um conversor (PDF → PPTX) e
de recorte: PNG em tons de cinza, todas com 1653 × 2339 px (A4 a 200 dpi), fundo branco puro, sem metadados.
A checagem objetiva confirma: a inclinação das linhas detectadas é a mesma da digitalização (mediana 0,12° contra
0,11°; 90 % abaixo de 0,29° contra 0,30°), enquanto a foto leve sintética tem 0,95° e 2,8°. Ou seja, a geometria
de foto (perspectiva, inclinação) não está nas imagens. O resultado mede **página limpa e endireitada por
software**, não a foto crua do celular.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — fotos entre a digitalização e a foto leve sintética | **Confirmada no limite inferior** | 10,7 % ≤ **11,0 %** ≤ 22,9 % |
| H2 — roda sem erro, ≤ 1 GiB, 100 % LDF válido | **Confirmada** | 15/15, 796 MiB, 15/15 válidos |

## 2. Resultados

Benchmark: [`BENCHMARK-20261027-exp-022-printed-photos.json`](../../evaluation/benchmarks/BENCHMARK-20261027-exp-022-printed-photos.json),
commit `1cb8ad4`, árvore limpa. Pipeline do EXP-019 (ADR-008) sem mudança.

| Condição (as mesmas 15 páginas) | Leitor original | Leitor ajustado | Mediana por página (ajustado) | Linhas detectadas | Inclinação mediana / p90 |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Digitalizada (EXP-015/017) | 24,1 % | 10,7 % | 7,7 % | 454 | 0,11° / 0,30° |
| **Imagens entregues (EXP-022)** | **24,3 %** | **11,0 %** | 7,0 % | 458 | 0,12° / 0,29° |
| Foto leve sintética (EXP-019) | 38,2 % | 22,9 % | 14,0 % | 436 | 0,95° / 2,8° |
| Foto forte sintética (EXP-019) | 73,6 % | 63,7 % | 69,8 % | 281 | 1,9° / — |

* **Associação foto → página** pelo menor CER: um-a-um, com folga grande (diferença mínima de 50 pontos de CER
  entre a página certa e a segunda melhor).
* **Escala automática:** 8 páginas em 1×, 7 em 2× (as linhas chegam maiores que na digitalização original).

## 3. O que isso diz

* Se a imagem chega **recortada, endireitada e com fundo limpo** (o que um aplicativo de digitalização de
  documentos faz), o pipeline lê como se fosse digitalização, inclusive a partir de uma impressão com resolução
  de origem baixa. Isso sugere que uma etapa de "limpeza de documento" antes da leitura pode valer a pena, mas
  não foi medida aqui com uma câmera.
* A pergunta do experimento, quanto a câmera crua custa, **segue sem resposta**. Para respondê-la, as fotos
  precisam chegar como o celular as grava (JPG ou HEIC, sem conversão nem recorte).

## 4. Limitações

* Imagens processadas por software antes do teste (ver §1); não há como separar o efeito da câmera do efeito
  do conversor.
* 15 páginas; fonte impressa de baixa resolução (~524 × 573 px ampliada 4×); leitor ajustado só experimental.

## 5. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-022/harness/prepare.py
# usuário: imprimir dataset/processed/exp-022/imprimir.pdf, fotografar, salvar em dataset/raw/exp-022/fotos/
foreach ($r in "ft", "original") { uv run --frozen --project $h python experiments/EXP-022/harness/read.py --reader $r }
uv run --frozen --project $h python experiments/EXP-022/harness/score.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-27`
