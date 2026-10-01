# ADR-NNN: [Título Curto da Decisão Arquitetural]

* **Status:** [PROPOSED | ACCEPTED | REJECTED | DEPRECATED | SUPERSEDED por ADR-MMM]
* **Data:** [AAAA-MM-DD]
* **Decisores:** [Claude Code | Usuário | Time]
* **Experimento de Suporte:** [EXP-xxx (link relativo)](../experiments/EXP-xxx/README.md)
* **Status de Licença:** [LICENSE STATUS: VERIFIED | LICENSE STATUS: NEEDS VALIDATION | N/A]

---

## 1. Contexto e Declaração do Problema

Descreva o contexto técnico e a necessidade de produto que motivou esta decisão.
Qual problema concreto estamos resolvendo no pipeline de Document Intelligence?

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** Local-first e custo zero (sem chamadas a APIs pagas por imagem/token).
* **Driver 2:** Desempenho e acurácia empírica (CER/WER, IoU, F1).
* **Driver 3:** Reprodutibilidade e simplicidade de manutenção no ambiente Windows / uv.
* **Driver 4:** Licença comercial permissiva de código e pesos.
* **Driver 5:** Preservação da fronteira com o produto principal Leitorum.

---

## 3. Opções Consideradas

### Opção A: [Nome da Opção A]
* **Descrição:** [Breve explicação]
* **Pontos Positivos (+):**
  * Ponto positivo 1
  * Ponto positivo 2
* **Pontos Negativos (-):**
  * Ponto negativo 1
  * Ponto negativo 2

### Opção B: [Nome da Opção B]
* **Descrição:** [Breve explicação]
* **Pontos Positivos (+):**
  * Ponto positivo 1
* **Pontos Negativos (-):**
  * Ponto negativo 1

---

## 4. Decisão Escolhida

Aprovamos a **Opção [A/B]** porque [justificativa clara conectando aos drivers e aos resultados empíricos do experimento].

---

## 5. Evidência Empírica do Experimento

* **Experimento:** [EXP-xxx](../experiments/EXP-xxx/README.md)
* **Métrica Aferida:**
  * Baseline anterior: `X%`
  * Resultado obtido: `Y%`
  * Impacto de latência / throughput: `Z ms por página`
* **Limitações Observadas:** [Condições em que a opção escolhida degrada ou falha]

---

## 6. Consequências

### Consequências Positivas
* [Benefício direto para o produto ou arquitetura]

### Consequências Negativas / Trade-offs
* [Custos adicionais de manutenção, dependências introduzidas, etc.]

### Conformidade com a Constituição
* [x] Princípio 1: Local-first garantido?
* [x] Princípio 2: Evidência antes de decisão comprovada?
* [x] Princípio 3: Reprodutibilidade verificada?
* [x] Princípio 6: Medição antes de otimização nativa?
* [x] Princípio 8: LDF como fronteira contratual preservado?
