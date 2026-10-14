# EXP-009: Relatório de Resultados — Leitura de Manuscrito em Português com o Reconhecedor do PP-OCR

* **Status:** `AWAITING USER ACCEPTANCE`
* **Execução:** 2026-10-14, por delegação do usuário (spec, plano e execução sem paradas intermediárias)
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-007](../../docs/adr/ADR-007-leitura-pp-ocr-sem-portugues-suficiente.md) (`PROPOSED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md)

> **Licenças.** `rapidocr` 3.10.0 (Apache-2.0), pesos PP-OCRv6 small det e rec (Apache-2.0, conforme o
> `MODEL_LICENSES.md` do wheel e os cards oficiais), ONNX Runtime (MIT) — `LICENSE STATUS: VERIFIED`, conforme
> declarado. Dados: GNHK (CC-BY-4.0, `VERIFIED`); BRESSAY `LICENSE STATUS: NEEDS VALIDATION` — exceção
> experimental do usuário; **nada aqui apoiado só no BRESSAY embasa produto**. As transcrições foram usadas só para
> calcular métricas; nenhum texto aparece neste relatório.

---

## 1. Resposta à pergunta do experimento

**Pergunta:** o reconhecedor que já vem no pacote do PP-OCR lê manuscrito em português?

**Resposta: melhor que tudo o que foi medido antes, mas ainda não o bastante.** Nas mesmas 398 linhas do EXP-001,
o erro de caractere cai de 69,4 % (melhor candidato de então) para **38,5 %**. Em manuscrito **inglês** fotografado
com celular, o mesmo modelo erra só **14,8 %** dos caracteres. A diferença é do português: as letras acentuadas
ficam com 80 % de erro.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — CER ≤ 30 % nas linhas do EXP-001 | **Refutada** | 38,5 % (EXP-001: 69,4 %) |
| H2 — CER ≤ 12 % e WER ≤ 25 % (critério de adoção) | **Refutada** | CER 38,5 %, WER 76,1 % |
| H3 — página detectada no máximo 5 pontos pior que com as linhas verdadeiras | **Confirmada**, com ressalva | 36,7 % de ponta a ponta contra 41,4 % com as linhas verdadeiras (ver §2.3) |
| H4 — ≤ 150 ms por linha e ≤ 2 GiB | **Confirmada** | 85 ms por linha; pico de 848 MiB |
| H5 — CER ≤ 20 % em linhas manuscritas do GNHK (inglês, celular) | **Confirmada** | 14,8 % |

---

## 2. Resultados

Benchmark: [`BENCHMARK-20261014-exp-009-reading.json`](../../evaluation/benchmarks/BENCHMARK-20261014-exp-009-reading.json),
commit `e679489`, árvore limpa.

### 2.1 Leitura de linhas (linhas verdadeiras)

| Conjunto | Linhas | CER | WER | Linhas com CER < 10 % | ms por linha |
| :--- | ---: | ---: | ---: | ---: | ---: |
| BRESSAY, as 398 linhas do EXP-001 | 398 | **38,5 %** | 76,1 % | 32 (8 %) | 85 |
| BRESSAY, todas as linhas das 185 páginas | 5.496 | 41,9 % | 77,5 % | 428 (8 %) | 83 |
| GNHK, linhas manuscritas legíveis | 1.918 | **14,8 %** | 45,5 % | 926 (48 %) | 32 |

Comparação com o EXP-001, nas mesmas 398 linhas: PyLaia RIMES 94,7 %; PyLaia IAM 79,3 %; TrOCR small 69,4 %;
**PP-OCRv6 small 38,5 %**. No GNHK ficaram de fora 521 linhas com palavra impressa ou ilegível.

### 2.2 Onde erra (BRESSAY, todas as linhas)

| Classe de caractere | Caracteres | CER |
| :--- | ---: | ---: |
| Letra sem acento | 384.863 | 42,5 % |
| **Letra acentuada** | 15.676 | **80,5 %** |
| Pontuação | 18.311 | 61,6 % |
| Dígito | 449 | 47,9 % |
| Espaço | 71.239 | 22,0 % |

No GNHK, as letras ficam em 12,7 %. O modelo lê o traço manuscrito; o que falha em português é o vocabulário e os
diacríticos.

### 2.3 Página inteira (BRESSAY, 185 páginas)

| Variante | CER de página | WER | Mediana do CER por página |
| :--- | ---: | ---: | ---: |
| Linhas verdadeiras (recortes do dataset, escala nativa) | 41,4 % | 77,2 % | 33,2 % |
| **Ponta a ponta** (detecção do EXP-008 + leitura, página ampliada 3×) | **36,7 %** | 74,6 % | 29,0 % |

O ponta a ponta ficou **melhor** que a leitura das linhas verdadeiras. Isso não significa que detectar ajude: as
duas variantes não leem a mesma imagem. Os recortes do dataset estão na escala nativa (linhas de cerca de 24 px),
e os recortes do ponta a ponta saem da página ampliada 3×. A conclusão segura é a de H3 — a detecção não é o que
limita a página —; a diferença de 4,7 pontos indica que a **resolução da linha** afeta a leitura e merece medida
própria.

Custo de ponta a ponta: 5,1 s por página (mediana), pico de 848 MiB. 185 de 185 páginas gravadas em LDF 2.0 com as
etapas de layout e reconhecimento concluídas, todas válidas.

---

## 3. Critérios de sucesso

| Critério | Resultado |
| :--- | :--- |
| SC-001 — veredito de H1 a H5 | Atendido |
| SC-002 — CER comparável ao EXP-001 | Atendido: mesmas 398 linhas, mesma métrica |
| SC-003 — decomposição detecção × leitura | Atendido, com o efeito de escala declarado (§2.3) |
| SC-004 — 100 % das páginas válidas em LDF 2.0 | Atendido: 185 de 185 |
| SC-005 — nenhum texto no Git ou nos relatórios | Atendido |
| SC-006 — ADR | Atendido: ADR-007 `PROPOSED` |

## 4. Desvios

| Planejado | O que ocorreu |
| :--- | :--- |
| Ciclo com aprovação por artefato | Spec, plano e execução por delegação do usuário ("planeje as próximas e continue executando") |
| Uma execução por conjunto | A primeira leitura das páginas terminou com código 4 sem mensagem, depois de ler os três conjuntos de linhas; repetida sozinha, terminou sem falha. A causa não foi identificada |
| Teto de página na mesma escala do ponta a ponta | Os recortes do dataset só existem na escala nativa; a comparação mistura escala e detecção (§2.3) |

## 5. Limitações

* **Um modelo, uma configuração.** O pacote oferece também um reconhecedor PP-OCRv6 "medium" e reconhecedores
  latinos do PP-OCRv5, que não foram medidos (exigem download).
* **Sem nenhum ajuste para português** e sem dicionário ou modelo de linguagem.
* **BRESSAY são redações escolares**, com caligrafia e vocabulário próprios; não é caderno de estudo.
* A ordem de leitura de página é a mais simples (de cima para baixo); funciona aqui porque as redações não têm
  regiões laterais.

## 6. Manifesto de reprodutibilidade

| Item | Valor |
| :--- | :--- |
| Ambiente do modelo | `experiments/EXP-008/envs/ppocr` (Python 3.12, `rapidocr` 3.10.0, `onnxruntime` 1.31.0), sem mudança |
| Modelos | `PP-OCRv6_det_small.onnx` (`090f04ab…`), `PP-OCRv6_rec_small.onnx` (`6f327246…`), conferidos antes da carga |
| Fusão | parâmetros do `experiments/EXP-008/calibration.json` |
| Conjuntos | linhas do EXP-001 (`dataset/raw/exp-001/bressay-subset/`); GNHK e BRESSAY de teste do EXP-007 |
| Commit da medição | `e679489`, árvore limpa |

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-009/harness/prepare.py
uv run --frozen --project $h python experiments/EXP-009/harness/read.py --set lines-exp001   # e lines-gnhk, lines-bressay, pages-bressay
uv run --frozen --project $h python experiments/EXP-009/harness/run.py --out evaluation/benchmarks/bench.json
```

## 7. Homologação

- [x] Entregáveis concluídos e submetidos ao usuário.
- [ ] EXP-009 **ACEITO** — decisão do usuário.
- [ ] ADR-007 aceito, rejeitado ou ajustado — decisão do usuário.

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-14`
