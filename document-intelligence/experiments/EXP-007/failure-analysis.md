# EXP-007: Análise de Falhas

Fonte: [`ANALYSIS-20261013-exp-007-real-images.json`](../../evaluation/benchmarks/ANALYSIS-20261013-exp-007-real-images.json),
gerado por `harness/analyze.py` sobre o benchmark do commit `8bf4e5f`. Só números e nomes de arquivo; nenhuma
imagem ou transcrição foi inspecionada.

> `LICENSE STATUS: NEEDS VALIDATION` para tudo o que depende do BRESSAY (uso experimental local autorizado pelo
> usuário; não pode embasar produto). GNHK: CC-BY-4.0, conforme declarado.

---

## 1. Linhas: o detector acha o texto, mas não a linha

Em todos os conjuntos o padrão é o mesmo: **quase nenhuma linha passa despercebida, e cerca de metade não é
reconhecida como uma linha inteira.**

| Conjunto | Linhas verdadeiras | Não casadas | Partidas em fragmentos | Desalinhadas | Fundidas com a vizinha | Não vistas |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| GNHK, foto original | 2.189 | 1.068 (49 %) | 416 | 467 | 115 | 70 |
| GNHK, retificada | 2.189 | 1.326 (61 %) | 591 | 426 | 75 | 234 |
| BRESSAY 3× | 5.496 | 2.813 (51 %) | 1.844 | 881 | 1 | 87 |
| BRESSAY nativa | 5.496 | 2.870 (52 %) | 1.924 | 863 | 0 | 83 |

* **Não vistas** são só 3 % das falhas no BRESSAY e 7 % no GNHK: o Doc-UFCN `norhand` marca tinta onde há texto.
* **Partidas** é a falha dominante: o detector devolve em mediana **1,5 caixa por linha verdadeira** (1,9 no GNHK
  retificado). Com caligrafia real, o espaço entre palavras quebra a linha em pedaços; nas páginas sintéticas,
  escritas com fonte, isso não acontecia.
* **Precisão baixa** (0,26 no GNHK, 0,30 no BRESSAY) é o outro lado do mesmo problema: cada fragmento que não casa
  conta como detecção errada.
* **A escala não é a causa.** BRESSAY ampliado 3× e nativo dão o mesmo resultado (F1 0,372 e 0,359): o modelo
  redimensiona a entrada internamente.

### Quanto uma fusão de fragmentos recuperaria

Unindo, com ajuda da verdade de chão, as detecções que caem dentro da mesma linha verdadeira (um **teto**, não um
resultado do pipeline):

| Conjunto | F1 medido | F1 com fusão ideal | Referência sintética |
| :--- | ---: | ---: | ---: |
| GNHK, foto original | 0,345 | 0,535 | 0,784 |
| GNHK, retificada | 0,239 | 0,500 | 0,845 |
| BRESSAY 3× | 0,372 | 0,712 | 0,928 |
| BRESSAY nativa | 0,359 | 0,715 | 0,928 |

Mesmo a fusão perfeita fica 0,2 abaixo do sintético. Juntar fragmentos ajudaria, mas não fecha a diferença: sobram
as linhas desalinhadas (caixa com altura ou extensão errada) e, no GNHK, 1.536 detecções fora de qualquer linha
anotada.

### Critério mais exigente

Com IoU ≥ 0,75 o F1 cai para 0,07 (GNHK) e 0,03 (BRESSAY). Pelo contorno, em vez da caixa, 0,16 e 0,06. As
caixas que casam têm IoU médio de 0,62 a 0,66: casam por pouco.

### Por origem da foto (GNHK, foto original)

| Região | Fotos | Precisão | Revocação | F1 | F1 retificada |
| :--- | ---: | ---: | ---: | ---: | ---: |
| AS | 25 | 0,430 | 0,591 | 0,498 | 0,379 |
| AF | 29 | 0,259 | 0,530 | 0,348 | 0,211 |
| NA | 36 | 0,246 | 0,490 | 0,328 | 0,232 |
| EU | 82 | 0,202 | 0,469 | 0,282 | 0,192 |

A variação entre regiões é grande (0,28 a 0,50), mas nenhuma chega perto do sintético. Em 106 das 172 fotos o F1
da página fica abaixo de 0,5; em 20, nenhuma linha casa.

## 2. Retificação: acha uma "folha" em toda foto e piora o resultado

O retificador por contorno devolveu um quadrilátero em **172 de 172 fotos**. Isso não é um acerto: ele aceita a
maior região clara da imagem, e em fotos tiradas de perto essa região é parte da folha, não a folha.

| Fração da foto ocupada pelo quadrilátero | Fotos | F1 sem retificar | F1 retificado |
| :--- | ---: | ---: | ---: |
| ≥ 90 % (quase não muda a imagem) | 60 | 0,294 | 0,280 |
| 60 % a 90 % | 84 | 0,365 | 0,237 |
| < 60 % (recorta muito) | 28 | 0,382 | 0,159 |

Quanto mais o retificador altera a imagem, mais ele prejudica. As linhas "não vistas" sobem de 70 para 234: o
recorte deixa texto de fora. No sintético a folha sempre aparecia inteira sobre fundo escuro, o caso em que o
método funciona; nas fotos reais esse caso é minoria.

## 3. Blocos: o detector vê o texto como um bloco só

| Conjunto | Parágrafos verdadeiros | Não casados | Dos não casados, dentro de um bloco detectado maior |
| :--- | ---: | ---: | ---: |
| BRESSAY 3× | 771 | 566 | 562 (99 %) |
| BRESSAY nativa | 771 | 573 | 568 (99 %) |

Em 109 das 185 páginas o Heron devolveu **um único bloco** para o texto inteiro. Ele não errou a localização (os
blocos que casam têm IoU médio de 0,90); ele não separa parágrafos que só se distinguem pelo recuo da primeira
linha. É uma diferença de granularidade: a verdade de chão do BRESSAY é por parágrafo, e o detector foi treinado
em documentos impressos, onde parágrafos têm espaço entre si.

Consequência: este conjunto **não permite concluir** se o Heron separa título, parágrafo, nota de margem e caixa
gráfica em caderno real. Mostra só que, em texto corrido manuscrito, ele entrega o bloco de texto e nada mais fino.

## 4. Ordem de leitura: perfeita com os parágrafos certos, perdida com os detectados

* Com os parágrafos verdadeiros: 1,000 (os dois ordenadores). Como previsto no plano, o resultado é trivial:
  parágrafos empilhados de cima para baixo.
* Com os blocos detectados: 0,24. Restrita aos blocos casados: 1,000.

Toda a perda vem dos blocos (566 parágrafos sem par, 182 blocos sobrando). O ordenador não erra nada. É o mesmo
diagnóstico do EXP-003, mais forte.

## 5. O que não falhou

* **Nenhuma falha de execução:** 0 páginas com erro em 5 execuções de modelo e 1 de retificação.
* **LDF 2.0:** 542 de 542 documentos válidos, com 23.321 linhas e 1.741 regiões, sem nenhuma descartada.
* **Custo:** mesma faixa do sintético (§ custo em `RESULTS.md`).

## 6. Ressalvas sobre a medição

* **A verdade de chão de linha do GNHK é derivada** do índice de linha das palavras. Se uma foto tiver texto não
  anotado, as detecções sobre ele contam como erro. Isso pode inflar as detecções erradas do GNHK; não afeta o
  BRESSAY, onde a verdade de chão é exata e o resultado é igual.
* **IoU ≥ 0,5 com a linha inteira** é um critério que pune fragmentos. Um reconhecedor de texto que aceitasse
  fragmentos poderia aproveitar parte dessas detecções; não há reconhecedor para medir isso (ADR-001).
* O GNHK é em inglês e não é caderno de estudo; o BRESSAY não é foto de celular. Nenhum dos dois é o caso de uso.
* A classificação das falhas usa só caixas alinhadas aos eixos.
