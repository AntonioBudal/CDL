# EXP-000: Manifesto de Avaliação de Fundação

* **Status:** `ACTIVE SPECIFICATION`
* **Versão:** 1.0.0
* **Data:** 2026-09-30

---

## 1. Escopo e Propósito

Este manifesto define os dados sintéticos, algoritmos de teste e protocolo determinístico de avaliação que devem ser validados durante o **EXP-000**, estabelecendo o alicerce para todos os benchmarks subsequentes (EXP-001 a EXP-006).

---

## 2. Fixtures Sintéticas Obrigatórias de Teste

Para o EXP-000, nenhuma imagem real ou dado sensível é utilizado. Apenas dados sintéticos gerados e mockados em formato JSON compõem o conjunto de validação:

* `dataset/fixtures/synthetic-line-sample.json`:
  - Contém pares de ground truth e predições mockadas simulando:
    1. Transcrição perfeita (`CER = 0.0`, `WER = 0.0`).
    2. Substituição simples de caractere.
    3. Inserção e deleção de caracteres acentuados típicos da língua portuguesa (`ç`, `ã`, `é`, `õ`).
    4. Variação de caixa alta/baixa.
    5. Caixas delimitadoras com sobreposição conhecida para validação de `IoU`.

---

## 3. Protocolo de Verificação das Métricas

O Claude Code deve assegurar que os cálculos de métricas respeitem as seguintes definições matemáticas:

### 3.1. Distância de Levenshtein e CER
$$\text{CER} = \frac{S + D + I}{N}$$
Onde:
* $S$: Substituições
* $D$: Deleções
* $I$: Inserções
* $N$: Número total de caracteres na referência de ground truth.

### 3.2. WER em Nível de Palavra
Calculado sobre tokens delimitados por espaços em branco após normalização básica de pontuação (preservando acentuação gráfica do português).

### 3.3. IoU (Intersection over Union)
$$\text{IoU}(A, B) = \frac{\text{Área}(A \cap B)}{\text{Área}(A \cup B)}$$
Para retângulos de caixas delimitadoras $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$.

---

## 4. Auditoria de Desempenho e Recursos

Durante o EXP-000, o framework de teste deve monitorar:
* Tempo decorrido de execução por amostra (ms).
* Alocação de memória RAM (RSS) antes e após a execução.
* Registro de seeds para reprodutibilidade estrita.
