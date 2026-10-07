# ADR-003: Ordem de leitura por ancoragem de regiões laterais; a detecção de blocos é o gargalo

* **Status:** PROPOSED
* **Data:** 2026-10-07
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-003](../../experiments/EXP-003/RESULTS.md)
* **Status de Licença:** N/A para os ordenadores (algoritmos próprios, sem pesos). O layout detectado usa os componentes do ADR-002, `LICENSE STATUS: VERIFIED`.

---

## 1. Contexto e Declaração do Problema

Depois de localizar linhas e blocos (ADR-002), o pipeline precisa colocá-los na ordem em que seriam lidos, para
preencher `structure.reading_order` do LDF. Em cadernos, o caso difícil não são colunas, e sim regiões laterais:
notas de margem e destaques ao lado do texto. O EXP-003 mediu três métodos algorítmicos sobre o layout verdadeiro
e sobre o layout produzido pelos detectores do ADR-002, em 180 páginas sintéticas.

Como os anteriores, este ADR define direção de trabalho; não promove nada a produto.

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** Local-first e custo zero.
* **Driver 2:** Acurácia de ordem de blocos — ≥ 0,95 com layout verdadeiro, ≥ 0,85 com layout detectado.
* **Driver 3:** Custo ≤ 50 ms por página, sem modelo.
* **Driver 4:** Licença — sem novas dependências.
* **Driver 5:** Saída compatível com o LDF.

---

## 3. Opções Consideradas

### Opção A: Ordenação ingênua (de cima para baixo, esquerda para a direita)
* **Pontos Positivos (+):** trivial; 1,4 ms; 0,954 com layout verdadeiro; a melhor de ponta a ponta (0,777).
* **Pontos Negativos (-):** 0,898 na família com destaque lateral — falha a meta por família.

### Opção B: Corte XY recursivo
* **Pontos Positivos (+):** método clássico, sem parâmetros de domínio.
* **Pontos Negativos (-):** 0,816 com layout verdadeiro; 0,602 com notas de margem — lê a nota antes do parágrafo
  que ela comenta.

### Opção C: Ancoragem de regiões laterais (`anchored`)
* **Pontos Positivos (+):** 0,983 com layout verdadeiro e ≥ 0,971 em todas as famílias; 2,2 ms por página.
* **Pontos Negativos (-):** limiares calibrados no mesmo gerador de páginas; de ponta a ponta fica em 0,773,
  empatada com a ingênua; não testada com notas em altura arbitrária, setas ou duas colunas.

---

## 4. Decisão Escolhida

Propõe-se a **Opção C** como método de referência de ordem de leitura, com estas condições:

1. `anchored` (sem endireitamento das caixas) é o ordenador de referência; `naive` fica como alternativa de
   comparação; o corte XY é descartado para páginas de caderno.
2. **A prioridade deixa de ser o ordenador.** A meta de ponta a ponta (0,85) não foi atingida, e 84 % da perda vem
   de blocos faltando ou sobrando na detecção. O próximo ganho está em melhorar a detecção de blocos — em especial
   notas de margem — e não em refinar a ordenação.
3. Todo detector de layout usado no pipeline precisa de um **ponto de operação explícito** (limiar de confiança e
   supressão de duplicatas) calibrado em dados separados; a saída bruta com limiar baixo serve para AP, não para
   montar documento.
4. `reading_order` do LDF 1.0 não comporta caixas gráficas; essa lacuna se soma às do EXP-002 e precisa de decisão
   de contrato antes de qualquer integração.
5. Nada entra em `src/leitorum_di/` além das métricas genéricas de ordem.

---

## 5. Evidência Empírica do Experimento

* **Experimento:** [EXP-003](../../experiments/EXP-003/RESULTS.md)
* **Layout verdadeiro (acurácia de ordem de blocos):** `anchored` 0,983; `naive` 0,954; `xycut` 0,816.
* **Layout detectado:** `naive` 0,777; `anchored` 0,773; `xycut` 0,698; restrito aos blocos casados, 0,950–0,953
  para os dois primeiros.
* **Decomposição (`anchored`):** 0,983 → 0,950 (−0,033 por geometria imprecisa) → 0,773 (−0,178 por blocos
  faltando ou sobrando: 203 de 1.785 sem par e 188 a mais).
* **Custo:** mediana de 1,4–6,8 ms por página; pico de alocação de 11 MB.
* **Limitações Observadas:** páginas sintéticas com notas sempre alinhadas ao início do parágrafo; sem duas
  colunas; o Heron rodou sem retificação; casamento de blocos sem olhar o tipo.

---

## 6. Consequências

### Consequências Positivas
* Fica definido um método de ordem barato, sem modelo e sem dependências.
* O gargalo do pipeline está identificado e quantificado: detecção de blocos, não ordenação.
* O harness mede qualquer melhoria futura na detecção diretamente em acurácia de ordem de ponta a ponta.

### Consequências Negativas / Trade-offs
* A ordem de leitura de ponta a ponta ainda não é confiável (77 %; só 32 % das páginas saem perfeitas).
* A regra de ancoragem pode não se sustentar em cadernos reais; precisa de validação com fotos reais.
* Somando ADR-001 e ADR-002: o pipeline segue sem reconhecedor de texto e com detecção de blocos abaixo do
  necessário para notas de margem.

### Conformidade com a Constituição
* [x] Princípio 1: Local-first garantido.
* [x] Princípio 2: Evidência antes de decisão — baseada nas medições do EXP-003.
* [x] Princípio 3: Reprodutibilidade — manifesto em `RESULTS.md` §6.
* [x] Princípio 6: Medição antes de otimização nativa — algoritmos em Python puro.
* [x] Princípio 8: LDF como fronteira contratual preservado — lacuna registrada, contrato intocado.
