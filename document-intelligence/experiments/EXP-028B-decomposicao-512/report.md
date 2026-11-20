# EXP-028B — Relatório: de onde vem o erro (imagens de 512 px)

* **Data:** 2026-11-20 · **Status:** `DONE` (4 páginas, 62 linhas; imagens de 512 px por decisão do usuário)
* **Spec:** [spec.md](./spec.md) · **Benchmark:** `evaluation/benchmarks/BENCHMARK-20261120-exp-028b.json`
* **Privacidade:** só números; nenhum texto, imagem ou recorte.

## 1. Resumo

Com as caixas desenhadas pelo autor, o mesmo leitor do produto ainda erra **50,9 %** dos caracteres. O produto
inteiro, nas mesmas imagens, erra **64,3 %**. Das duas partes, **o leitor responde por cerca de 4/5 do erro**
(50,9 pontos); achar as linhas, por 10,9 pontos, e a ordem, por 2,5. O maior ganho possível está no **leitor**
— o que confirma a ordem do roadmap (ajuste fino do leitor no 0.14) e limita o que a detecção (EXP-030A/B) pode
render: no máximo uns 13 pontos.

| # | Hipótese | Resultado | Veredito |
| :--- | :--- | :--- | :--- |
| **H1** | ≥ 10 pontos vêm das caixas e da ordem | **13,4 pontos** (detecção 10,9 + ordem 2,5) | **Confirmada** |
| **H2** | o leitor sozinho, com caixas perfeitas, erra > 40 % | **50,9 %** | **Confirmada** |
| **H3** | a imagem de 512 px piora o produto em > 5 pontos | **−5,5 pontos**: em 512 px o produto errou *menos* (64,3 %) que nas fotos originais (69,8 %) | **Refutada** (com ressalva, §3) |

## 2. Detalhes

**As três leituras** (mesmo leitor PP-OCRv6 small do produto, escala da página para linhas de ~80 px, mesmo
recorte; só muda a caixa):

| Página | A — produto | C — caixas do autor, ordem do produto | B — caixas do autor, ordem dele |
| :--- | ---: | ---: | ---: |
| p10 | 51,3 % | 46,7 % | 33,7 % |
| p11 | 68,1 % | 60,5 % | 58,4 % |
| p14 | 72,1 % | 49,0 % | 48,5 % |
| p15 | 55,0 % | 48,6 % | 48,6 % |
| **micro** | **64,3 %** | **53,4 %** | **50,9 %** |

* A diferença entre A e C (detecção, fusão e escala do produto) varia muito por página: de 4,6 pontos (p10) a
  23,1 pontos (p14). Na p14 o produto achou as 20 linhas, mas cortou ou juntou mal.
* A ordem pesa pouco: a regra do produto trocou 2 linhas de lugar em 3 das 4 páginas.
* As duas rodadas de leitura deram resultados idênticos (ONNX em CPU, leitura gulosa).

**O leitor linha a linha (B, 62 linhas, par exato pelo `line_id`):** mediana de **45,7 %** de erro por linha.

| Erro na linha | Linhas |
| :--- | ---: |
| até 10 % | 1 |
| 10–30 % | 10 |
| 30–60 % | 36 |
| acima de 60 % | 15 |

Só 1 linha em 62 sai quase certa. Não é um problema de algumas linhas ruins: o leitor erra de forma
espalhada, o que indica falta de adaptação à letra (o que o ajuste fino ataca), e não um defeito pontual.

## 3. A surpresa da resolução (H3)

O esperado era que as imagens pequenas piorassem a leitura. Aconteceu o contrário: 64,3 % em 512 px contra
69,8 % na leitura que o produto fez das fotos originais (texto da exportação do Leitorum, o mesmo do EXP-027).
Contando caracteres (sem ler o texto), a leitura das originais tem **muito menos texto** que a de 512 px — por
exemplo, 182 caracteres contra 329 numa página cuja referência tem 383 —, ou seja, o erro dela vem sobretudo de
**texto que ficou de fora**.

O que isso permite dizer, e o que não:

* **Permite:** o resultado "o leitor domina" não é um efeito das imagens pequenas — em 512 px o produto leu
  mais, não menos.
* **Não permite:** saber por que a leitura das originais perdeu tanto texto. Sem as fotos, não dá para
  repetir a leitura; as hipóteses são a escala automática agir diferente numa foto grande, a versão do motor da
  época ou algum filtro na exportação. Fica registrado como pergunta aberta para quando houver fotos novas
  (que, se chegarem, devem ser lidas pelo motor atual nos dois tamanhos).

## 4. Limitações

* **4 páginas, 62 linhas**, todas do teste congelado (só medida; nada foi ajustado aqui).
* **Imagens de 512 px** e caixas desenhadas nelas; a parte "detecção" mede o detector **nesta resolução**.
* A decomposição é um caminho (A → C → B): as partes somam o erro total, mas não são atribuições
  independentes (trocar a ordem antes das caixas daria números um pouco diferentes).

## 5. O que isto muda no plano

1. **Prioridade confirmada:** o leitor é ~4/5 do erro. O ajuste fino (EXP-033A) é o passo de maior impacto.
2. **Detecção vale até ~11 pontos e varia por página** (5 a 23): o EXP-030A/B continua útil, mas não é a
   alavanca principal.
3. **A ordem de leitura pode esperar** (2,5 pontos): o EXP-038 do 0.15 fica onde está.
4. **Antes do primeiro treino:** a F-DI-13.02 (trava de hashes entre treino e teste), como aprovado. E o treino
   precisa de páginas de desenvolvimento transcritas linha a linha (Dados-13.1), que hoje não têm imagem.
