# ADR-010: Organização do texto nas 4 seções do Estudo como sugestão revisável, em Python puro

* **Status:** ACCEPTED (aprovado pelo usuário em 2026-10-27; implementação no Leitorum pela feature 089)
* **Data:** 2026-10-27
* **Decisores:** Usuário; Claude Code (proposta e execução do EXP-023)
* **Experimento de suporte:** [EXP-023](../../experiments/EXP-023/RESULTS.md)
* **Status de licença:**
  - código e pesos sob MIT, ajustados só em dados fictícios do projeto;
  - nenhum corpus, modelo ou serviço externo;
  - o ruído de treino usa só contagens de erro do EXP-015.

## 1. Contexto

Leitores escrevem no caderno sem os cabeçalhos que o parser de importação do Leitorum exige. O pedido é um botão
que distribua o texto lido entre Resumo, Explicação, Conceitos e Referências. As restrições:
- sem IA de terceiros e sem LLM;
- em CPU, com menos de 200 ms;
- auditável.

## 2. Decisão

1. **Adotar a pipeline do EXP-023 como sugestão sob demanda**, nunca como distribuição automática:
   - **segmentação:** linhas → blocos → sentenças, com geometria quando houver;
   - **vetor de cada unidade:** pistas estruturais e discursivas, mais o léxico de n-gramas de caracteres;
   - **classificador:** regressão logística calibrada;
   - **decisão:** Viterbi com custo de troca de seção ponderado pela coesão entre vizinhos.
2. **Simplificar a matriz relacional ao que a validação sustentou:**
   - a transição $T$ e a propagação de rótulos ficam desligadas ($\tau = \omega = \alpha = 0$);
   - o acoplamento $S$ entra só no custo de troca.
3. **Rodar no backend em Python puro, sem dependência nova**, com os pesos em `organizer-v1.json`. O texto nunca é
   reescrito: só trechos movidos, com a origem preservada.
4. **Calibração com os estudos do usuário desligada** até medir ganho com N suficiente (decisão 3 da spec).

## 3. Evidência

| Conjunto | Macro-F1 (V4) | Observação |
| :--- | ---: | :--- |
| D-sintético, digitado, sem geometria | 0,908 | portão ≥ 0,70 |
| D-sintético, CER 25 %, com geometria | 0,825 | portão ≥ 0,60 |
| **Estudos reais do usuário (N = 3)** | **0,497** | lacuna de domínio; Referências 0,29 |

- **Latência:** p95 de 8 ms por página fictícia e 42 ms num estudo real longo.
- **Calibração:** ECE ≤ 0,045.

## 4. Consequências

- **O botão vale como ponto de partida, não como resposta.** A interface precisa da lista "Seções para conferir"
  e do "Voltar para texto único".
- **Qualidade em texto real não está demonstrada.** Antes de tratar como recurso maduro:
  - repetir a medida nos estudos do usuário com N ≥ 30;
  - ampliar as pistas de Referências para os formatos reais;
  - medir em páginas de caderno.
- **Para calibrar com os estudos do usuário,** a montagem dos centróides precisa de cache incremental. Hoje, a
  montagem a frio está estimada em ~6 s para 500 estudos.
