# Framework de Avaliação Contínua e Benchmarks — Document Intelligence

Este diretório armazena os relatórios de benchmarks, scripts de aferição estatística e configurações de suítes de avaliação do subsistema Document Intelligence.

---

## 1. Princípios de Avaliação Confiável

Para assegurar comparações justas entre candidatos a modelos e pipelines:

1. **Suítes de Avaliação Congeladas:**
   - Cada conjunto de dados de teste (validação e teste) deve ser fixo e inalterável ao longo do ciclo de vida de um experimento.
   - Modificar o conjunto de teste invalida todas as comparações históricas.
2. **Avaliação sob Idênticas Condições de Contorno:**
   - Mesma máquina de teste ou ambiente isolado.
   - Mesma semente randômica quando envolver inicialização estocástica.
   - Mesmo conjunto de pré-processamento de imagens.
3. **Múltiplas Dimensões de Performance:**
   - Não avaliar apenas acurácia (CER/WER/IoU/F1).
   - Medir obrigatoriamente: tempo de latência de inferência por elemento (ms), throughput (páginas/minuto), consumo de pico de RAM e uso de VRAM (quando houver GPU).

---

## 2. Estrutura de Relatórios de Benchmark

Cada execução de benchmark formal pelo Claude Code deve gerar um arquivo em `evaluation/benchmarks/`:
`BENCHMARK-YYYYMMDD-[nome-do-experimento].json` e um sumário executivo em markdown contendo:
* Hash da versão do código e timestamp da execução.
* Tabela de métricas consolidadas com intervalos de confiança (ou média e desvio padrão).
* Matriz de confusão para classes semânticas ou caracteres críticos da língua portuguesa.
* Identificação clara do modelo vencedor e recomendação para ADR.
