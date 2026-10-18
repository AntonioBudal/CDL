# EXP-010: Relatório de Resultados — Outros Reconhecedores do PP-OCR e Escala da Linha

* **Status:** `ACCEPTED` / `CONCLUÍDO` (aceito por delegação do usuário em 2026-10-18)
* **Execução:** 2026-10-14, por delegação do usuário
* **Executor:** Claude Code
* **Decisão:** evidência acrescentada ao [ADR-007](../../docs/adr/ADR-007-leitura-pp-ocr-sem-portugues-suficiente.md) (`ACCEPTED`); nenhum ADR novo
* **Artefato do ciclo:** [spec.md](./spec.md) (especificação, plano e tarefas)

> **Licenças.** PP-OCRv6 small, PP-OCRv6 medium e PP-OCRv5 latino mobile: Apache-2.0 nos cards oficiais da
> PaddlePaddle — `LICENSE STATUS: VERIFIED`, conforme declarado. Os dois modelos novos foram baixados do repositório
> do projeto `rapidocr` (ModelScope, `RapidAI/RapidOCR` 3.10.0), com o SHA-256 publicado no pacote conferido, e
> ficam em `models/exp-010/`, fora do Git. BRESSAY: `LICENSE STATUS: NEEDS VALIDATION`; nada aqui embasa produto.
> Nenhum texto de referência ou lido aparece neste relatório.

---

## 1. Resposta

**Nenhum reconhecedor pronto do ecossistema chega perto do critério de adoção.** O melhor resultado em português
continua sendo o PP-OCRv6 **small**, agora com o recorte ampliado 2×: **CER 34,4 %** nas 398 linhas do EXP-001
(38,5 % sem ampliar). O modelo **medium**, maior, lê pior o português (58,7 %), embora seja o melhor em palavras no
inglês. O modelo **latino** erra menos os acentos (66 % contra 80 %), mas mais o resto.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — algum alternativo ≤ 33,5 % (5 pontos melhor) na escala 1× | **Refutada** | latino 42,8 %; medium 58,7 % (small: 38,5 %) |
| H2 — ampliar o recorte melhora ≥ 2 pontos | **Confirmada** | small −4,1; latino −3,8; medium −8,6 pontos |
| H3 — algum atinge CER ≤ 12 % e WER ≤ 25 % | **Refutada** | melhor: small 2×, CER 34,4 %, WER 74,1 % |
| H4 — o melhor custa ≤ 150 ms por linha e ≤ 2 GiB | **Confirmada** | small 2×: 105 ms; pico de 177 MiB |

## 2. Resultados

Benchmark: [`BENCHMARK-20261014-exp-010-recognizers.json`](../../evaluation/benchmarks/BENCHMARK-20261014-exp-010-recognizers.json),
commit `e62c005`, árvore limpa.

### 2.1 Linhas do EXP-001 (BRESSAY, 398 linhas, português)

| Reconhecedor | Escala | CER | WER | Letras acentuadas | Linhas com CER < 10 % | ms por linha |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| PP-OCRv6 small | 1× | 38,5 % | 76,1 % | 81,6 % | 32 | 88 |
| **PP-OCRv6 small** | **2×** | **34,4 %** | 74,1 % | 79,7 % | 34 | 105 |
| PP-OCRv6 small | 3× | 34,7 % | 73,7 % | 79,2 % | 37 | 100 |
| PP-OCRv5 latino | 1× | 42,8 % | 80,0 % | 69,8 % | 19 | 107 |
| PP-OCRv5 latino | 2× | 39,0 % | 78,7 % | **65,7 %** | 25 | 133 |
| PP-OCRv5 latino | 3× | 39,3 % | 78,5 % | 66,4 % | 21 | 133 |
| PP-OCRv6 medium | 1× | 58,7 % | 82,0 % | 89,9 % | 25 | 2.150 |
| PP-OCRv6 medium | 2× | 51,9 % | 78,7 % | 88,6 % | 35 | 2.270 |
| PP-OCRv6 medium | 3× | 50,1 % | 77,7 % | 87,3 % | 37 | 2.311 |

Referência do EXP-001 nas mesmas linhas: TrOCR small 69,4 %; PyLaia IAM 79,3 %; PyLaia RIMES 94,7 %.

### 2.2 Linhas do GNHK (1.918 linhas, inglês, foto de celular, escala 1×)

| Reconhecedor | CER | WER | Linhas com CER < 10 % | ms por linha |
| :--- | ---: | ---: | ---: | ---: |
| PP-OCRv6 small | **14,8 %** | 45,5 % | 926 | 31 |
| PP-OCRv6 medium | 16,5 % | **41,5 %** | 1.099 | 664 |
| PP-OCRv5 latino | 23,3 % | 62,1 % | 496 | 28 |

## 3. Leitura dos resultados

* **A escala importa, e de forma estável:** ampliar 2× melhora os três modelos; 3× não acrescenta nada além de 2×.
  Isso também explica o resultado de página do EXP-009 (a página ampliada leu melhor que os recortes nativos).
* **Modelo maior não é melhor em português:** o medium perde para o small por 17 pontos no BRESSAY e quase empata
  no inglês. O que limita é o que o modelo viu no treino, não o tamanho.
* **O modelo latino ajuda só nos acentos:** a única classe em que ele ganha é a das letras acentuadas. Combinar os
  dois modelos não foi testado.
* **O traço não é o problema:** os mesmos modelos leem inglês manuscrito fotografado com 15 % a 17 % de erro. A
  diferença é de língua e de caligrafia (redações escolares brasileiras).

## 4. Desvios

* Ciclo escrito e executado por delegação, sem aprovação intermediária.
* Os modelos foram baixados diretamente das URLs publicadas no `rapidocr` (o download automático da biblioteca
  não foi acionado pela configuração passada), com o mesmo SHA-256 que ela confere.
* O primeiro relatório foi gravado por um script com uma chave de veredito errada (a impressão final falhou); o
  script foi corrigido e o relatório refeito a partir de árvore limpa. Os números não mudaram.

## 5. Limitações

* Só leitura de linhas verdadeiras; o ponta a ponta com escala 2× não foi refeito.
* Uma execução; sem combinação de modelos; sem modelo de linguagem ou dicionário de português.
* BRESSAY (redações) ainda não é caderno; licença em validação.

## 6. Reprodução

```powershell
$h = "experiments/EXP-002/envs/harness"
# requer os conjuntos preparados pelo EXP-009 e os modelos em models/exp-010/
uv run --frozen --project $h python experiments/EXP-010/harness/read.py --model small --scale 2 --set lines-exp001
uv run --frozen --project $h python experiments/EXP-010/harness/run.py --out evaluation/benchmarks/bench.json
```

**Verificação final (2026-10-14):** suíte principal e testes do harness passando; `ruff` limpo; nada fora de
`document-intelligence/`; modelos e dados fora do Git.

## 7. Homologação

- [x] Entregáveis concluídos e submetidos ao usuário.
- [x] EXP-010 **ACEITO** (aceito por delegação do usuário em 2026-10-18).

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-14`
