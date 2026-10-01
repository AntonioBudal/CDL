# EXP-001 — Análise de Erros (Fase 4)

* **Data:** 2026-10-01
* **Entradas:** relatórios `evaluation/benchmarks/BENCHMARK-*-exp-001-*.json` e agregados `ANALYSIS-20261001-exp-001-*.json`
* **Método:** alinhamento de Levenshtein por caractere em NFC (`harness/analyze.py`), sobre a saída bruta de cada modelo
* **Condições:** CPU, 4 threads, decodificação gulosa, sem modelo de linguagem; predições idênticas entre repetições

> **Licenças.** `trocr-small-handwritten`: `LICENSE STATUS: NEEDS VALIDATION` (uso experimental local autorizado; não
> promovível a produto). Dataset BRESSAY: `LICENSE STATUS: NEEDS VALIDATION` (uso experimental local autorizado em
> 2026-10-01). Imagens, transcrições e predições do BRESSAY ficam fora do Git; aqui há só agregados.
>
> BRESSAY: Neto et al., *BRESSAY: A Brazilian Portuguese Dataset for Offline Handwritten Text Recognition*, ICDAR 2024
> (DOI 10.5281/zenodo.11637681).

---

## 1. Quadro geral

| Candidato | Dataset | CER | WER | Mediana ms/linha | p95 ms | Pico de memória |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| `pylaia-rimes` | sintético (200 linhas) | 22,3 % | 68,8 % | 179 | 253–273 | 474 MiB |
| `pylaia-iam` | sintético | 24,6 % | 81,0 % | 181–186 | 251–285 | 473 MiB |
| `trocr-small-handwritten` | sintético | 17,0 % | 46,2 % | 790–798 | 969–1.049 | 573 MiB |
| `pylaia-rimes` | BRESSAY (398 linhas, 199 autores) | **94,7 %** | 99,7 % | 407–408 | 546–582 | 503 MiB |
| `pylaia-iam` | BRESSAY | **79,3 %** | 99,4 % | 402–408 | 550–605 | 499 MiB |
| `trocr-small-handwritten` | BRESSAY | **69,4 %** | 102,9 % | 705–717 | 907–922 | 585 MiB |

Metas da spec: CER ≤ 12 %, WER ≤ 25 %, ≤ 150 ms/linha, ≤ 2 GB.

* **H1 (qualidade): refutada.** Nenhum candidato lê português manuscrito real; no BRESSAY praticamente nenhuma
  palavra sai correta (WER ≈ 100 %).
* **H2 (custo): refutada na latência, confirmada na memória.** Todos ficam abaixo de 620 MiB, mas nenhum atinge
  150 ms/linha em CPU; o TrOCR fica cerca de 5× acima.
* **H0 (modelos sem treino em português falham): confirmada.**

No `pylaia-rimes` com BRESSAY a primeira das três repetições foi `SKIPPED` por RAM livre insuficiente mesmo após a
espera de 180 s; as métricas vêm das duas repetições concluídas.

---

## 2. Camada sintética: onde cada modelo erra

Taxa de erro por classe de caractere da referência (substituições + deleções):

| Classe | Caracteres | `pylaia-rimes` | `pylaia-iam` | `trocr-small` |
| :--- | ---: | ---: | ---: | ---: |
| Vogais acentuadas | 557 | 83,3 % | 100 % | 100 % |
| Cedilha | 60 | 95,0 % | 100 % | 100 % |
| Dígitos | 408 | 11,0 % | 35,5 % | 2,9 % |
| Pontuação | 464 | 41,4 % | 32,5 % | 6,2 % |
| Maiúsculas | 360 | 28,3 % | 22,8 % | 1,7 % |
| Minúsculas sem acento | 4.992 | 13,8 % | 4,7 % | 3,4 % |
| Espaços | 1.266 | 17,2 % | 40,9 % | 2,8 % |

CER recalculado para isolar cada fonte de erro:

| Variante | `pylaia-rimes` | `pylaia-iam` | `trocr-small` |
| :--- | ---: | ---: | ---: |
| CER bruto | 22,3 % | 24,6 % | 17,0 % |
| Ignorando diacríticos | 18,2 % | 18,3 % | 10,9 % |
| Ignorando caixa | 21,9 % | 24,4 % | 17,0 % |
| Sem o espaço antes da pontuação | 22,3 % | 21,7 % | 12,4 % |

Leitura:

1. **Diacríticos são um teto estrutural, não um erro ocasional.** O TrOCR e o PyLaia-IAM erram 100 % das vogais
   acentuadas e das cedilhas: o primeiro foi ajustado só em inglês; o segundo nem tem esses símbolos. O
   PyLaia-RIMES conhece `à â ç é ê ô` (do francês), mas não `á í ó ú ã õ` — 4,7 % dos caracteres da referência
   sintética são inalcançáveis para ele, e 7,6 % para o PyLaia-IAM.
2. **O TrOCR é o melhor fora dos acentos**: 3,4 % de erro em minúsculas simples e 2,9 % em dígitos. Sem diacríticos
   e sem o espaço que ele insere antes da pontuação (convenção do treino no IAM; 381 inserções de espaço), seu erro
   em linhas limpas cai para a faixa de 6–11 %.
3. **O PyLaia erra letras básicas mesmo em texto limpo** (`o→e` 112×, `o→s` 93×, `o→0` 55× no RIMES), sinal de que
   a fonte sintética já está fora do domínio de treino dele.
4. **Pares ambíguos da spec:** `o/0` aparece no PyLaia (55 e 30 ocorrências); `l/1`, `O/0`, `I/l` e `S/5`
   praticamente não ocorrem neste conjunto.

Confusões mais frequentes (referência→hipótese; `∅` = ausente; `␣` = espaço):

* `pylaia-rimes`: `o→e` 112, `␣→∅` 105, `í→i` 97, `o→s` 93, `á→a` 59, `o→0` 55, `O→∅` 44, `:→.` 33, `ç→g` 31
* `pylaia-iam`: `␣→∅` 346, `∅→␣` 204, `í→i` 97, `á→a` 83, `ã→a` 80, `:→∅` 60, `u→n` 46, `é→e` 46, `à→a` 45
* `trocr-small`: `∅→␣` 381, `í→i` 97, `ã→a` 74, `á→a` 68, `é→e` 53, `ç→g` 41, `à→a` 40, `ê→e` 37, `ó→o` 37

A lista completa das 20 principais por candidato está nos arquivos `ANALYSIS-*.json`.

---

## 3. BRESSAY: caligrafia real em português

| Operações | `pylaia-rimes` | `pylaia-iam` | `trocr-small` |
| :--- | ---: | ---: | ---: |
| Caracteres corretos | 1.851 | 7.312 | 14.571 |
| Substituições | 1.241 | 6.444 | 17.248 |
| Deleções (faltou na saída) | 31.902 | 21.238 | 3.175 |
| Inserções | 0 | 52 | 3.851 |

(34.994 caracteres de referência.)

* **O PyLaia quase não emite texto**: 91 % (RIMES) e 61 % (IAM) dos caracteres simplesmente não aparecem na saída.
* **O TrOCR emite texto do tamanho certo, mas errado**: metade dos caracteres é substituída; as confusões
  dominantes são entre vogais (`o→e` 421, `a→e` 322, `o→a` 287). Os acentos deixam de ser o problema principal:
  ignorá-los muda o CER em menos de 1 ponto.

### Resolução das imagens é um fator, mas não explica tudo

As linhas do BRESSAY são muito pequenas: altura mediana de 23 px (decis de 17 a 48 px), cerca de 7 px de largura
por caractere. O PyLaia foi treinado com altura de 128 px, então a imagem é ampliada ~5×.

| Altura da linha | Linhas | `pylaia-rimes` | `pylaia-iam` | `trocr-small` |
| :--- | ---: | ---: | ---: | ---: |
| < 20 px | 99 | 99 % | 89 % | 77 % |
| 20–29 px | 145 | 98 % | 81 % | 70 % |
| 30–44 px | 113 | 91 % | 74 % | 66 % |
| ≥ 45 px | 41 | 83 % | 65 % | 61 % |

O erro cai com a resolução, mas mesmo nas linhas maiores fica acima de 60 %.

---

## 4. Limitações

* **BRESSAY não é caderno fotografado.** São redações digitalizadas em baixa resolução, de fontes online; a
  resolução penaliza todos os modelos. O resultado mostra que os candidatos falham em manuscrito PT-BR real,
  mas não mede o desempenho em fotos de caderno feitas pelo celular.
* **Amostra:** 398 linhas (2 por página de teste, seed 1234), excluídas as linhas com marcas de anotação
  (rasuras, trechos ilegíveis, sobrescritos). O subconjunto é, portanto, um pouco mais "limpo" que o dataset.
* **Sem adaptação:** todos os modelos foram usados como publicados, com decodificação gulosa e sem modelo de
  linguagem. Nenhum ajuste de pré-processamento foi tentado (por exemplo, outra estratégia de redimensionamento).
* **Sintético ≠ manuscrito:** a fonte Caveat é regular; serve para custo e para isolar o efeito do alfabeto.
* **Latência** medida com 4 threads padrão do PyTorch e a máquina em uso normal (cerca de 1 GiB de RAM livre).
* **Sem baseline de texto impresso** nesta rodada (Tesseract e EasyOCR excluídos).

---

## 5. O que os dados sustentam (insumo para a Fase 5)

1. Nenhum dos candidatos pode ser adotado como está; a lacuna em manuscrito real é de ordem de grandeza, não de ajuste fino.
2. O alfabeto é condição necessária: qualquer caminho futuro precisa de um modelo cujo vocabulário de saída cubra `á é í ó ú â ê ô ã õ à ç`.
3. A arquitetura CNN-RNN-CTC cabe no orçamento de memória e fica perto do de latência; o Transformer testado não cabe no de latência em CPU.
4. Um experimento de adaptação (treino/ajuste em português) seria o passo seguinte natural, e depende de um dataset de treino com licença fechada — hoje o projeto não tem um.
