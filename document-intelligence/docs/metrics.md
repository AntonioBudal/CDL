# Protocolo de Métricas e Critérios de Avaliação

Este documento especifica as métricas matemáticas e operacionais adotadas para quantificar a eficácia dos modelos e algoritmos no **Document Intelligence**.

---

## 1. Métricas por Camada Funcional

### 1.1 Reconhecimento de Texto e Transcrição (HTR e OCR)
- **CER (*Character Error Rate*)**:
  $$\text{CER} = \frac{S + D + I}{N}$$
  Onde $S$ é o número de substituições, $D$ de deleções, $I$ de inserções e $N$ o total de caracteres no texto de referência (Distância de Levenshtein no nível de caractere).
- **WER (*Word Error Rate*)**:
  Métrica correspondente calculada no nível de palavras delimitadas por espaços.

### 1.2 Detecção de Layout e Segmentação Estrutural
- **IoU (*Intersection over Union*)**:
  Razão entre a área de sobreposição e a área de união entre a caixa delimitadora/polígono predito e o gabarito anotado.
- **Precision, Recall e F1-Score por Categoria Estrutural**:
  Avaliado para classes de blocos (`heading`, `paragraph`, `list_item`, `margin_note`, `diagram_box`) sob limiar de sobreposição $\tau$ (ex.: $\text{IoU} \ge 0.50$).

### 1.3 Relações Espaciais, Grafos e Diagramas
- **Edge Precision**:
  Proporção de arestas (setas e conexões direcionais) corretamente detectadas entre nós válidos.
- **Edge Recall**:
  Proporção de arestas reais do caderno anotado que foram recuperadas pelo pipeline.
- **Edge F1-Score**:
  Média harmônica entre Edge Precision e Edge Recall.

### 1.4 Classificação Semântica de Fichamentos
- **Accuracy Global**:
  Proporção total de seções classificadas com o papel correto.
- **Precision, Recall e Macro-F1**:
  Calculados para cada papel semântico (`title`, `concept`, `summary`, `question`, `quote`, `example`).
- **Matriz de Confusão (*Confusion Matrix*)**:
  Identificação explícita de padrões de ambiguidade (ex.: confusão entre `concept` e `example`).

---

## 2. Hipóteses Internas Iniciais de Desempenho

> **IMPORTANTE — HIPÓTESES INTERNAS INICIAIS:**  
> Os limiares numéricos abaixo representam **metas de aspiração inicial da equipe**, e **NÃO** dogmas universais ou fatos consolidados da literatura de HTR em português.  
> O Claude Code deverá registrar o *baseline* empírico no **EXP-001** e calibrar formalmente estes limiares durante o ciclo de clarificação (`speckit.clarify`).

| Camada | Métrica | Hipótese Inicial Almejada | Justificativa / Contexto |
| :--- | :--- | :---: | :--- |
| **HTR (Linhas Manuscritas)** | **CER** | $\le 8.0\%$ | Nível aceitável para leitura confortável com poucos reparos humanos. |
| **HTR (Texto Impresso)** | **CER** | $\le 1.5\%$ | Texto impresso nítido deve ser quase perfeito. |
| **Segmentação de Linhas** | **IoU ($\tau$)** | $\ge 0.85$ | Alinhamento geométrico fidedigno para recortar a linha sem cortar descendentes (p, q, g). |
| **Diagramas e Setas** | **Edge-F1** | $\ge 0.75$ | Grafos de estudo devem reconstruir a lógica conceitual central sem excesso de falsos positivos. |
| **Classificação Semântica**| **Macro-F1** | $\ge 0.80$ | Distinção estável entre conceitos e anotações explicativas. |

---

## 3. Protocolo de Medição

1. **Avaliação Automatizada**: Scripts em `evaluation/` devem computar as métricas sem intervenção manual a partir de predições e anotações de gabarito.
2. **Registro de Tempos e Recursos**: Juntamente com a precisão, todo relatório deve registrar a latência por página (em milissegundos) e o pico de consumo de memória RAM e VRAM na inferência.

---

## 4. Definições Operacionais (EXP-000)

- **WER**: tokens separados por espaço em branco; pontuação nas **bordas** de cada token é removida
  (categorias Unicode `P*`); tokens que ficam vazios são descartados. Acentuação, caixa e pontuação
  interna (ex.: hífen) são preservadas. **CER** não normaliza nada (pontuação, acento e caixa contam como erro).
- **Reprodutibilidade**: `leitorum_di.reproducibility.freeze_seeds()` (seed padrão 1234).
- **Benchmark de fundação**: `uv run python -m leitorum_di.benchmark [--out evaluation/benchmark-exp000.json]`
  registra tempo por amostra (ms), RSS antes/depois, pico de alocação Python e seeds (`leitorum-di-benchmark/1`).
