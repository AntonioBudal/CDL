# EXP-002 — Retificação e Análise de Falhas (Fases 4 e 5)

* **Data:** 2026-10-05
* **Entradas:** `evaluation/benchmarks/BENCHMARK-2026100{3,4,5}-exp-002-*.json` e `ANALYSIS-20261005-exp-002-*.json`
* **Condições:** CPU, 4 threads, 3 repetições `OK` por combinação, métricas idênticas entre repetições, árvore
  limpa, todas as saídas válidas no JSON Schema do LDF. Páginas sintéticas — ver limitações em `RESULTS.md`.

> `doctr`: `LICENSE STATUS: NEEDS VALIDATION` (uso experimental local por exceção do usuário; não promovível a produto).

---

## 1. Retificação medida isoladamente (120 páginas degradadas do `test`)

| Retificador | ms/página (mediana) | p95 | Pico de memória | Erro dos cantos — leve | Erro dos cantos — forte | Folhas achadas |
| :--- | ---: | ---: | ---: | :--- | :--- | ---: |
| `contour` (OpenCV, sem pesos) | 124–133 | 138–175 | 60 MiB | mediana 5,9 px; média 8,6; máx. 98 | mediana 30,7 px; média 73,3; máx. 381 | 120/120 |
| `docufcn-page` (Doc-UFCN, MIT) | 2.453–2.538 | 2.674–2.981 | 657 MiB | mediana 78,7 px; média 75,3; máx. 95 | mediana 75,8 px; média 74,7; máx. 162 | 120/120 |

* O `contour` é ~20× mais rápido e muito mais preciso no nível leve, mas no forte tem falhas grandes
  (sombra e fundo claro confundem o limiar).
* O `docufcn-page` erra os cantos por um deslocamento quase constante (~75 px, a máscara não chega à borda da
  folha), mas é estável: o pior caso é bem menor que o do `contour`.
* Em imagens de ~12 MP (`large`, 10 páginas): `contour` leva 524–529 ms e 122 MiB, com erro de 13,4 px.

## 2. Linhas com e sem retificação (F1, caixa, IoU ≥ 0,5)

| Detector | Retificação | Leve | Forte | Degradado (leve + forte) | Ganho | Detecção ms/página | Custo total ms/página |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `docufcn-norhand-line` | nenhuma | 0,883 | 0,784 | 0,833 | — | 2.498 | 2.498 |
| | `contour` | **0,920** | **0,845** | 0,882 | +4,9 | 2.496 | ~2.625 |
| | `docufcn-page` | 0,917 | 0,852 | 0,884 | +5,1 | 2.303 | ~4.790 |
| `docufcn-historical-line` | nenhuma | 0,863 | 0,799 | 0,831 | — | 2.458 | 2.458 |
| | `contour` | 0,900 | 0,799 | 0,850 | +1,9 | 2.454 | ~2.585 |
| | `docufcn-page` | 0,882 | **0,878** | 0,880 | +4,9 | 2.247 | ~4.735 |
| `classic` | nenhuma | 0,743 | 0,397 | 0,558 | — | 596 | 596 |
| | `contour` | 0,781 | 0,578 | 0,673 | +11,5 | 484 | ~615 |
| | `docufcn-page` | 0,783 | 0,717 | 0,749 | +19,1 | 447 | ~2.935 |
| `doctr` | nenhuma | 0,694 | 0,391 | 0,529 | — | 2.138 | 2.138 |
| | `contour` | 0,794 | 0,511 | 0,643 | +11,4 | 2.205 | ~2.335 |
| | `docufcn-page` | 0,670 | 0,662 | 0,666 | +13,7 | 2.117 | ~4.605 |

"Custo total" = mediana da retificação + mediana da detecção (medidas separadamente). Ganho em pontos de F1 na
camada degradada. Pico de memória da detecção: 83 MiB (`classic`), 728–826 MiB (Doc-UFCN), 904 MiB (`doctr`).

**Leitura:**

1. A retificação ajuda todos os detectores; ajuda mais quem é mais frágil à inclinação (`classic`, `doctr`).
2. Só o Doc-UFCN ultrapassa 0,80 nos **dois** níveis degradados, e só com retificação: `norhand` + `contour`
   (0,920 / 0,845), `norhand` + `docufcn-page` (0,917 / 0,852) e `historical` + `docufcn-page` (0,882 / 0,878).
3. O `contour` entrega quase o mesmo ganho do `docufcn-page` para o `norhand`, por 1/20 do custo.
4. Caso de 12 MP: `norhand` passa de 0,884 para 0,932 com `contour`; 2,6 s de detecção, 678 MiB — a redução
   interna da imagem mantém tempo e memória estáveis.

## 3. Onde os detectores falham (sem retificação, `test` completo)

F1 por inclinação da folha (ângulo da borda superior):

| Detector | 0–1° | 1–3° | 3–6° | ≥ 6° |
| :--- | ---: | ---: | ---: | ---: |
| `classic` | 0,757 | 0,628 | 0,466 | 0,373 |
| `doctr` | 0,794 | 0,580 | 0,473 | 0,178 |
| `docufcn-historical-line` | 0,896 | 0,844 | 0,865 | 0,677 |
| `docufcn-norhand-line` | 0,897 | 0,857 | 0,771 | 0,814 |

F1 por curvatura perto da lombada (amplitude sorteada):

| Detector | < 0,004 | 0,004–0,012 | ≥ 0,012 |
| :--- | ---: | ---: | ---: |
| `classic` | 0,844 | 0,707 | 0,403 |
| `doctr` | 0,825 | 0,681 | 0,388 |
| `docufcn-historical-line` | 0,915 | 0,857 | 0,801 |
| `docufcn-norhand-line` | 0,926 | 0,882 | 0,778 |

Curvatura alta só ocorre no nível forte, junto com perspectiva, sombra e desfoque mais fortes: a tabela mostra a
tendência, não o efeito isolado da curvatura. Sombra e desfoque não foram separados por página (o gerador não
registra se a sombra foi sorteada).

Modos de falha das linhas verdadeiras não casadas (3.548 linhas):

| Detector | Perdida | Fundida com outra | Fragmentada | Deslocada/parcial | Falsos positivos isolados |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `classic` | 405 | 279 | 197 | 75 | 1.390 (335 fora da folha) |
| `doctr` | 152 | 28 | 432 | 200 | 898 |
| `docufcn-historical-line` | 101 | 144 | 65 | 154 | 285 (65 fora da folha) |
| `docufcn-norhand-line` | 126 | 301 | 52 | 75 | 249 (29 fora da folha) |

* **`classic`**: no nível forte perde 358 linhas inteiras e gera mais de mil falsos positivos (restos de pauta e
  textura do fundo). A retificação elimina os falsos positivos fora da folha (335 → 10) e reduz as perdas.
* **`doctr`**: detecta palavras e as agrupa em caixas alinhadas aos eixos; com a folha inclinada, a linha vira
  vários pedaços (432 fragmentadas). Acima de 6° o F1 cai para 0,18.
* **Doc-UFCN `norhand`**: o erro dominante é **fundir linhas vizinhas** (301), inclusive em páginas limpas (87) —
  linhas de caderno ficam mais próximas que as dos documentos de treino.
* **Doc-UFCN `historical`**: funde menos, mas desloca mais (154), e seus polígonos são piores (F1 de polígono
  0,60 contra 0,82 do `norhand`).

## 4. Blocos

| Fonte | `title` | `paragraph` | `margin_note` | `graphic_box` | mAP@0,5 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `heron` (detector de layout) | 0,985 | 0,910 | 0,533 | 0,697 | **0,781** |
| regras sobre `doctr` | 0,864 | 0,642 | 0,246 | 0,038 | 0,447 |
| regras sobre `docufcn-historical-line` | 0,624 | 0,573 | 0,150 | 0,001 | 0,337 |
| regras sobre `docufcn-norhand-line` | 0,791 | 0,288 | 0,087 | 0,011 | 0,294 |
| regras sobre `classic` | 0,448 | 0,469 | 0,047 | 0,069 | 0,258 |
| regras sobre as linhas verdadeiras (`dev`) | | | | | 0,713 |

* As regras dependem de linhas quase perfeitas: com linhas verdadeiras chegam a 0,71; com linhas detectadas caem
  para 0,26–0,45. Linhas fundidas ou fragmentadas quebram o agrupamento por espaçamento.
* A regra de `graphic_box` (tinta que não pertence a linhas) é inviável: gerou de 309 a 4.740 caixas para 86
  verdadeiras.
* O Heron, treinado em documentos impressos, transfere bem para título e parágrafo. Seu ponto fraco é
  `margin_note` (0,53): não há classe equivalente, e a correspondência usada (notas de rodapé e
  cabeçalhos/rodapés de página) é só uma aproximação.
* Blocos não foram medidos com retificação nesta rodada.

## 5. Veredito das hipóteses

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — linhas: F1 ≥ 0,90 limpo e ≥ 0,80 degradado | **Confirmada com retificação**, só para o Doc-UFCN | limpo 0,917–0,928; degradado 0,920 / 0,845 (`norhand` + `contour`). Sem retificação nenhum candidato passa no nível forte |
| H2 — blocos: mAP@0,5 ≥ 0,70 | **Confirmada para o Heron**; refutada para as regras | 0,781 contra 0,26–0,45 |
| H3 — ≤ 2 s por página e ≤ 2 GB | **Parcial** | memória: todos abaixo de 1 GB. Tempo: `classic` (0,6 s) e Heron (1,7–1,9 s) passam; Doc-UFCN (2,3–2,5 s) e `doctr` (2,1–2,2 s) não |
| H4 — baseline clássico resolve páginas limpas e degrada com foto | **Refutada na primeira parte** | 0,847 em páginas limpas (meta 0,90); 0,743 / 0,397 nas degradadas |
| H5 — retificação: +5 pontos com custo ≤ 0,5 s | **Confirmada para `contour`** em 3 de 4 detectores | +11,5 (`classic`), +11,4 (`doctr`), +4,9 (`norhand`, no limite), +1,9 (`historical`); custo de 0,13 s. O `docufcn-page` dá ganhos iguais ou maiores, mas custa 2,5 s |

A única combinação que cumpre H1 (`docufcn-norhand-line` + `contour`) custa ~2,6 s por página — 30 % acima da
meta de tempo. Linhas e blocos juntos (retificação + Doc-UFCN + Heron, em sequência) somam cerca de 4,4 s por
página nesta máquina.
