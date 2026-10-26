# EXP-018: Relatório de Resultados — Curva de Aprendizado do Ajuste Fino

* **Status:** `ACCEPTED` / `CONCLUÍDO` (executado e aceito por delegação permanente do usuário, 2026-10-26)
* **Executor:** Claude Code
* **Decisão:** evidência e recomendação de quantidade de dados acrescentadas ao
  [ADR-009](../../docs/adr/ADR-009-margem-de-leitura-e-ajuste-fino.md)
* **Artefato do ciclo:** [spec.md](./spec.md)

> **Licenças.** Treinos com páginas do BRESSAY (`NEEDS VALIDATION`): pesos em `models/exp-018/`, fora do Git, **só
> experimento**. Nenhum texto aparece neste relatório. Conjuntos de teste não usados.

---

## 1. Resposta

Poucas páginas bastam para a maior parte do ganho. Com o mesmo orçamento de treino do EXP-014, **50 páginas**
(~1 500 linhas) dão 88 % do ganho (CER de validação 32,0 % → 15,8 %) e **150 páginas** (~4 500 linhas) chegam ao
mesmo resultado do treino com as 647 páginas (13,7 % contra 13,5 %). Com 16 páginas o ganho para cedo, em 19,6 %:
o modelo vê as mesmas ~500 linhas treze vezes.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — 50 páginas: CER ≤ 18 % | **Confirmada** | 15,8 % |
| H2 — 16 páginas: CER < 25 % | **Confirmada** | 19,6 % |
| H3 — 150 páginas: até 1 ponto do EXP-014 (13,5 %) | **Confirmada** | 13,7 % (0,2 ponto do EXP-014) |

## 2. Curva

Mesmo orçamento em todos os pontos: 392 passos de 16 linhas (~6,3 mil linhas vistas), taxa 5e-5, margem de 640 px,
semente 1234; páginas sorteadas encaixadas (as 16 estão nas 50, que estão nas 150). CER no subconjunto de validação
do EXP-014 (1 537 linhas, autores fora do treino), **no último passo**. Registros em [`runs/`](./runs/).

| Páginas de treino | Linhas | Vezes que cada linha foi vista | CER no último passo | Parte do ganho do EXP-014 |
| ---: | ---: | ---: | ---: | ---: |
| 0 (modelo original) | 0 | — | 32,0 % | 0 % |
| 16 | 487 | ~13 | 19,6 % | 67 % |
| 50 | 1 496 | ~4 | 15,8 % | 88 % |
| 150 | 4 500 | ~1,4 | 13,7 % | 99 % |
| 647 (EXP-014, sorteio de linhas) | ~6 270 vistas de 19 565 | 1 | 13,5 % | 100 % |

Evolução da validação (passos 98 / 196 / 294 / 392):

* 16 páginas: 19,0 % / 19,8 % / 19,6 % / 19,6 % — para de melhorar cedo; poucas linhas distintas.
* 50 páginas: 17,5 % / 16,8 % / 15,5 % / 15,8 %.
* 150 páginas: 17,0 % / 14,8 % / 14,8 % / 13,7 % — ainda melhorando no fim. (Uma primeira execução caiu com falha
  de segmentação entre os passos 250 e 294, com a máquina sem memória livre; a repetição, retomável, deu exatamente os
  mesmos 17,0 % e 14,8 % nos passos 98 e 196 e terminou sem queda.)

## 3. Recomendação de dados para o produto

Para repetir o ajuste com dados que possam ir para o produto, o pedido mínimo útil é de **cerca de 50 páginas
transcritas** (88 % do ganho medido aqui) e o alvo é de **cerca de 150 páginas** (o mesmo resultado que todo o
treino do BRESSAY, neste orçamento de CPU). Uma página de redação tem ~30 linhas; uma página de caderno costuma ter
um número parecido.

Ressalvas para o pedido:

* **Quem escreve importa.** Aqui cada página é de um autor diferente e a validação é de autores fora do treino. Se o
  objetivo for ler a letra de **uma pessoa** (o caso do caderno pessoal do Leitorum), páginas dessa pessoa devem
  render mais por página do que este número indica; se for ler qualquer leitor do produto, é preciso variedade de
  autores, e o número de páginas é um mínimo.
* **Fotos, não digitalizações.** O EXP-019 mostrou que a foto custa muito mais que a leitura; as páginas pedidas
  devem ser fotos de celular, como as que o produto vai receber.
* **Transcrição linha a linha**, fiel (com acentos e pontuação), é o que o treino usa.

## 4. Limitações

* Um sorteio e uma semente por ponto; a variação entre sorteios não foi medida (estimativa de ±1 ponto, pela
  oscilação entre passos).
* Mesmo acervo do treino e da validação (redações digitalizadas); fotos de caderno devem ser mais difíceis, e o
  número de páginas necessário pode ser maior.
* Orçamento fixo de 392 passos (~2,5–3 h em CPU). Com mais passos, os pontos com mais páginas tendem a ganhar mais
  que os com menos.

## 5. Reprodução

```powershell
cd experiments/EXP-014/envs/ft
foreach ($n in 16, 50, 150) { uv run --frozen python -u -I ../../../EXP-018/harness/train.py --pages $n }
```

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-26`
