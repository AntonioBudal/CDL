# Experiment Specification: EXP-003 — Reconstrução Espacial e Ordem de Leitura

**Diretório do experimento**: `experiments/EXP-003/`

**Created**: 2026-10-05

**Status**: `APPROVED` pelo usuário em 2026-10-05 ("pode continuar"), sem ajustes: valem as propostas
recomendadas em §6. Execução concluída em 2026-10-07; resultados em [RESULTS.md](./RESULTS.md).

**Input**: `docs/roadmap-experiments.md` §3 (EXP-003), `docs/ldf.md`, resultados do EXP-002 (aceito em 2026-10-05)
e ADR-002.

**Pré-requisito**: EXP-002 `ACCEPTED`. O EXP-003 não lê texto: ordena as regiões já localizadas.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** dadas as linhas e os blocos de uma página de caderno, um método local e barato consegue
colocá-los na ordem em que uma pessoa os leria — inclusive com notas de margem, caixas gráficas e caixas de destaque laterais — e quanto dessa ordem se perde quando a entrada vem dos detectores do EXP-002 em vez da
verdade de chão?

- **H1 (ordem com layout perfeito):** com linhas e blocos verdadeiros, algum método atinge acurácia de ordem de
  blocos ≥ 0,95 em todas as famílias de layout do escopo.
- **H2 (ordem com layout detectado):** com blocos do Heron e linhas do Doc-UFCN (com retificação por contorno),
  a acurácia de ordem fica ≥ 0,85.
- **H3 (baseline ingênuo — hipótese, não premissa):** ordenar de cima para baixo e da esquerda para a direita
  basta em página de coluna única, mas falha com notas de margem e caixas de destaque laterais.
- **H4 (custo):** a ordenação custa ≤ 50 ms por página e não exige modelo.

Os limiares são critérios de avaliação dos métodos; o experimento conclui com veredito explícito para cada um.

---

## 2. Cenários Experimentais

### Cenário 1 — Verdade de chão de ordem de leitura e harness (P1)

O gerador de páginas do EXP-002 passa a registrar a ordem de leitura de blocos e de linhas, e o harness ganha
métricas de ordem validadas com casos calculados à mão.

**Aceite:** um ordenador de referência (que devolve a ordem verdadeira) dá acurácia 1,0; permutações conhecidas
dão os valores esperados.

### Cenário 2 — Métodos de ordenação sobre layout verdadeiro (P2)

Comparar, sobre linhas e blocos verdadeiros: (a) ordenação ingênua por posição; (b) corte XY recursivo;
(c) ordenação por colunas detectadas mais regra de ancoragem das notas de margem.

**Aceite:** tabela por método e por família de layout com acurácia de ordem de blocos e de linhas.

### Cenário 3 — Mesmos métodos sobre layout detectado (P2)

Entrada: blocos do Heron e linhas do Doc-UFCN `norhand` com retificação por contorno (direção do ADR-002), a
partir das predições já produzidas ou reexecutadas nas novas páginas.

**Aceite:** tabela de acurácia de ponta a ponta e a perda em relação ao Cenário 2, separando erro de ordenação de
erro herdado da detecção (blocos faltando, fundidos ou a mais).

### Cenário 4 — Linhas dentro do bloco (P3)

Ordem das linhas dentro de cada bloco, inclusive em blocos inclinados pela perspectiva.

**Aceite:** acurácia de ordem de linhas por bloco, com e sem retificação.

### Casos de borda

- Página com um único bloco; página só com diagrama.
- Nota de margem ao lado de dois parágrafos; nota vertical.
- Bloco detectado que cobre dois blocos verdadeiros, ou bloco verdadeiro partido em dois.
- Página inclinada acima de 6°.

---

## 3. Requisitos

### Funcionais

- **FR-001**: A entrada de um ordenador é a geometria de linhas e blocos (bbox, polígono, tipo); a saída é a sequência de identificadores de blocos e, dentro de cada bloco, de linhas.
- **FR-002**: Métrica principal: acurácia de ordem de blocos = 1 − distância de edição normalizada entre a sequência prevista e a verdadeira. Complementar: tau de Kendall e a mesma acurácia para linhas.
- **FR-003**: Com layout detectado, os blocos previstos são primeiro casados com os verdadeiros (IoU ≥ 0,5); blocos sem par contam como erro e são reportados à parte.
- **FR-004**: A saída é convertida para `structure.reading_order` do LDF 1.0 e validada contra o JSON Schema.
- **FR-005**: Medir ms por página e pico de memória de cada ordenador com o supervisor dos experimentos anteriores.
- **FR-006**: Métodos algorítmicos, sem pesos, são o foco. Um modelo treinado de ordem de leitura só entra se tiver licença verificada, instalar por wheels e couber no orçamento — a decidir (§6, pergunta 4).
- **FR-007**: Páginas sintéticas com texto fictício; nenhuma foto do usuário; inferência offline.
- **FR-008**: Manifesto de reprodutibilidade completo; teto de 20 GB de dados locais (uso atual: 7,5 GB).
- **FR-009**: A nota de margem entra na ordem logo depois do parágrafo ao lado do qual está.
- **FR-010**: Famílias de layout: coluna única, notas de margem ancoradas e caixa de destaque ao lado do texto. Duas colunas ficam fora desta rodada.

### Entidades

- **Página** (do EXP-002) acrescida de `reading_order` (blocos) e da ordem das linhas em cada bloco.
- **Ordenador**: identificador, parâmetros, método.
- **Execução**: ordenador × fonte do layout (verdadeiro | detectado) → sequência, métricas, tempo.

---

## 4. Métodos Candidatos

| # | Método | Tipo | Observação |
| :- | :--- | :--- | :--- |
| A | Ordenação ingênua (topo → base, esquerda → direita) | algorítmico | baseline; hipótese H3 |
| B | Corte XY recursivo | algorítmico | clássico para colunas e blocos empilhados |
| C | Colunas por agrupamento + ancoragem de notas de margem ao parágrafo vizinho | algorítmico | específico para caderno |
| ~~D~~ | ~~Modelo treinado de ordem de leitura~~ | aprendido | fora desta rodada (decisão 4) |

Nenhum é escolhido a priori.

---

## 5. Critérios de Sucesso do Experimento

- **SC-001**: Verdade de chão de ordem de leitura gerada e validada; métricas com testes de valores à mão.
- **SC-002**: Tabela de acurácia por método, por família de layout e por fonte do layout, com veredito de H1–H4.
- **SC-003**: Decomposição da perda de ponta a ponta entre ordenação e detecção.
- **SC-004**: Saídas válidas no LDF (`reading_order`).
- **SC-005**: ADR com a decisão; registros de licença atualizados se algum modelo for avaliado.
- **SC-006**: Nada alterado fora de `document-intelligence/`; testes e `ruff` verdes; teto de disco respeitado.

---

## 6. Decisões *(aprovação sem ajustes em 2026-10-05: valem as recomendações)*

1. Nota de margem: logo depois do parágrafo vizinho.
2. Famílias de layout: coluna única, notas de margem ancoradas e caixa de destaque lateral. **Duas colunas ficam
   fora** (a pergunta ficou sem resposta explícita; adotei a opção mais contida — é só avisar se quiser incluí-las).
3. Caixa gráfica avaliada na ordem pela posição vertical; a lacuna no `reading_order` do LDF é registrada à parte.
4. Só métodos algorítmicos; nenhum modelo treinado de ordem de leitura.
5. O contrato LDF não é alterado; as lacunas seguem para decisão própria.

### Perguntas originais (histórico)

1. **Onde entra a nota de margem na ordem?** Proponho: logo **depois** do parágrafo ao lado do qual ela está
   (a nota comenta o que acabou de ser lido). Alternativas: antes desse parágrafo, ou todas as notas ao final.
2. **Quais famílias de layout?** O gerador atual só faz coluna única, em que a ordem é quase trivial. Proponho
   acrescentar: (a) notas de margem ancoradas a parágrafos específicos; (b) caixa de destaque ao lado do texto;
   (c) páginas de duas colunas. Cadernos raramente têm duas colunas — quer incluí-las, ou ficar em (a) e (b)?
3. **Caixa gráfica na ordem.** No LDF 1.0, `reading_order` lista só blocos, e a caixa gráfica vai para
   `diagrams[]`. Proponho avaliar a ordem com a caixa gráfica incluída (pela posição vertical) e registrar à
   parte que ela não cabe no `reading_order` atual. Concorda?
4. **Modelo treinado.** Fico só nos métodos algorítmicos (recomendado: a entrada é geometria simples e o custo é
   mínimo), ou procuro também um modelo de ordem de leitura com licença verificada?
5. **Lacunas do LDF.** As três lacunas registradas no EXP-002 seguem sem decisão. O EXP-003 pode prosseguir sem
   mexer no contrato; prefere resolvê-las antes?

---

## 7. Fora de Escopo

- Detecção de linhas e blocos (EXP-002), reconhecimento de texto (EXP-001), classificação semântica (EXP-004),
  grafo de diagramas (EXP-005).
- Treino de modelos; GPU; fotos reais; alterações no contrato LDF; código de produto em `src/leitorum_di/` além
  de métricas genéricas de ordem.

## 8. Premissas

- Reaproveitamento do gerador de páginas, dos manifestos, do supervisor e dos ambientes do EXP-002; nenhum
  download novo é previsto se a pergunta 4 ficar em "só algorítmicos".
- Máquina-alvo e limites iguais aos dos experimentos anteriores.
- Como no EXP-002, os resultados valem para páginas sintéticas.
