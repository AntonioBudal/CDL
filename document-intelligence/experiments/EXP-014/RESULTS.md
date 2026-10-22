# EXP-014: Relatório de Resultados — Adaptação do Reconhecedor à Caligrafia Brasileira

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-22)
* **Executor:** Claude Code
* **Decisão:** [ADR-009](../../docs/adr/ADR-009-margem-de-leitura-e-ajuste-fino.md) (`ACCEPTED` por delegação)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Modelo de partida: PP-OCRv6 small rec (Apache-2.0). Ferramentas: PyTorch (BSD-3-Clause e outras
> permissivas), `onnx` e `onnx2torch` (Apache-2.0), ONNX Runtime (MIT) — `VERIFIED`, conforme declarado. **O modelo
> ajustado foi treinado com o BRESSAY (`LICENSE STATUS: NEEDS VALIDATION`, só pesquisa não comercial): serve só
> para experimento e não pode ir para o produto.** Os pesos ficam em `models/exp-014/`, fora do Git. Nenhum texto
> de referência ou lido aparece neste relatório.

---

## 1. Resposta

**Ajustar o reconhecedor com manuscrito em português funciona, e muito.** Com menos de uma época de treino em
CPU (cerca de 6 mil linhas, 2h30), o erro de caractere nas linhas de teste cai de 29,7 % para 13,6 %, e as letras
acentuadas de 77 % para 21,5 % de erro. Com a correção lexical do EXP-011, chega a **12,4 %** (todas as linhas de
teste) e **9,5 %** (as 398 linhas do EXP-001) — abaixo do critério de adoção de caractere (12 %) nas linhas do
EXP-001, mas ainda acima do de palavra (25 %).

Antes do treino, o experimento achou uma correção de método que vale por si: **o pacote `rapidocr` lê pior do que
o modelo permite.** Ao receber uma linha baixa, ele a redimensiona arredondando os lados para múltiplos de 32 px, o
que distorce a proporção; e o modelo lê melhor com uma **margem vazia à direita**. Lendo o mesmo modelo
diretamente pelo ONNX Runtime, com 640 px de margem, o erro cai de 41,9 % para 29,7 % — sem treino nenhum.

| Hipótese | Veredito | Evidência (398 linhas do EXP-001) |
| :--- | :--- | :--- |
| H1 — CER abaixo de 20 % com o ajuste | **Confirmada** | 10,7 % (9,5 % com correção lexical) |
| H2 — o ganho vale para autores fora do treino | **Confirmada** | as divisões oficiais separam autores; 13,6 % em todas as linhas de teste |
| H3 — inferência ≤ 150 ms por linha | **Refutada nesta implementação** | 280 ms por linha no PyTorch com 640 px de margem; o ONNX Runtime sem ajuste leva ~100 ms; exportar o modelo ajustado para ONNX não foi feito |

## 2. Resultados

Benchmark: [`BENCHMARK-20261022-exp-014-fine-tune.json`](../../evaluation/benchmarks/BENCHMARK-20261022-exp-014-fine-tune.json),
commit `76f47a1`, árvore limpa.

| Leitura | Linhas do EXP-001: CER / WER | Todas as linhas de teste: CER / WER | Acentos (todas) | Com correção lexical (todas) |
| :--- | :--- | :--- | ---: | :--- |
| Pacote `rapidocr` (como nos EXP-009 a 013) | 38,5 % / 76,1 % | 41,9 % / 77,5 % | 80,5 % | 41,5 % / 71,6 % |
| ONNX Runtime + margem de 640 px, sem ajuste | 28,0 % / 71,8 % | 29,7 % / 72,0 % | 77,0 % | 28,9 % / 64,1 % |
| **Ajustado no BRESSAY + margem de 640 px** | **10,7 % / 41,3 %** | **13,6 % / 44,1 %** | **21,5 %** | **12,4 % / 34,1 %** |

### 2.1 A margem à direita (escolhida na validação)

| Margem | CER na validação (1.537 linhas) |
| ---: | ---: |
| 0 px | 41,5 % |
| 160 px | 34,8 % |
| 320 px | 32,9 % |
| **640 px** | **32,1 %** |

O efeito foi notado no teste (a conversão PyTorch, lendo em lote, ganhava ~6 pontos por causa do preenchimento
entre linhas de larguras diferentes); a escolha do valor foi feita só na validação.

### 2.2 Treino

* Modelo convertido do ONNX para PyTorch com `onnx2torch`, depois de reescrever 3 operações com preenchimento
  `SAME_UPPER` como preenchimento explícito; saída idêntica ao ONNX Runtime (diferença máxima 6×10⁻⁶).
* 2,76 milhões de parâmetros; dicionário de 18.708 caracteres, que já inclui as 24 letras acentuadas do português
  — nenhum caractere das transcrições ficou de fora.
* Perda CTC, AdamW (taxa 5×10⁻⁵), lotes de 16 linhas de largura parecida, normalização em lote congelada.
* Orçamento de 150 minutos: ~370 passos, cerca de 6 mil das 19.565 linhas de treino (menos de uma época). CER de
  validação: 32,0 % → 13,5 %. A validação intermediária (a cada 400 passos) não chegou a rodar; o modelo guardado é
  o do fim do orçamento.

## 3. O que isso significa

* **Para o produto, já:** a margem de 640 px e a leitura direta pelo ONNX Runtime não dependem do BRESSAY e
  melhoram o pipeline do ADR-008 de graça (CER de linha 41,9 % → 29,7 % em português; o inglês não foi remedido).
* **Para o produto, depois:** o ajuste fino é o caminho, e não precisa de muito: menos de uma época já reduziu o
  erro à metade. Mas o modelo ajustado aqui não pode ser usado. É preciso repetir o treino com manuscrito em
  português **com licença para produto** — por exemplo, páginas escritas para esse fim, com consentimento.
* **Mais treino provavelmente ajuda:** o modelo viu um terço das linhas de treino uma vez só.

## 4. Desvios e limitações

* PyTorch no lugar do PaddlePaddle (registrado na spec antes da execução).
* A validação intermediária não rodou (intervalo maior que o número de passos); o modelo guardado é o final.
* A inferência do modelo ajustado foi medida no PyTorch (280 ms por linha); não foi exportado de volta para ONNX.
* A primeira execução do treino foi interrompida por mim depois de poucos minutos porque a saída estava em buffer e
  não dava para acompanhar; foi reiniciada do zero com saída sem buffer.
* Mesmos limites de dados: redações, não caderno; licença em validação.

## 5. Reprodução

```powershell
$ft = "experiments/EXP-014/envs/ft/.venv/Scripts/python.exe"
& $ft experiments/EXP-014/harness/feasibility.py
uv run --frozen --project experiments/EXP-002/envs/harness python experiments/EXP-014/harness/data.py
& $ft experiments/EXP-014/harness/probe_padding_width.py val-sub e0,e160,e320,e640
& $ft -u experiments/EXP-014/harness/train.py --minutes 150 --eval-every 400
& $ft experiments/EXP-014/harness/predict.py --set test-all --checkpoint models/exp-014/best.pt --out dataset/processed/exp-014/pred-ft-test-all.json
uv run --frozen --project experiments/EXP-002/envs/harness python experiments/EXP-014/harness/run.py --out evaluation/benchmarks/bench.json
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-22`
