# Roteiro Sequencial de Experimentos — Document Intelligence

Este documento define a ordem cronológica, as dependências e o escopo planejado para os experimentos de pesquisa e validação técnica do subsistema **Document Intelligence**.

---

## 1. Regra Fundamental de Execução

> **REGRA DE OURO:**  
> **O Claude Code deve conduzir estritamente UM experimento por vez.**  
> É terminantemente vedado iniciar a implementação ou os benchmarks do `EXP-001` sem que o `EXP-000` esteja completamente homologado, auditado e com seus critérios de aceite validados.

---

## 2. Mapa do Roteiro Experimental

```text
┌─────────────────────────────────────────────────────────────┐
│ EXP-000: Ambiente, Reprodutibilidade e Fundação de Avaliação │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Apenas após aceite do EXP-000)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-001: Reconhecimento de Texto Manuscrito (HTR) em Linhas │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-002: Detecção de Layout e Segmentação de Blocos/Regiões │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-003: Reconstrução Espacial e Ordem de Leitura           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-004: Classificação Semântica de Fichamentos e Estudos    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-005: Reconhecimento de Diagramas, Nós e Fluxogramas     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ EXP-006: Pipeline Integrado Ponta a Ponta (Foto → LDF)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Escopo Detalhado dos Experimentos

### `EXP-000` — Fundação de Ambiente, Reprodutibilidade e Avaliação *(CONCLUÍDO — aceito em 2026-09-30)*
- **Objetivo**: Garantir que a máquina local do desenvolvedor esteja perfeitamente configurada, inventariar capacidades de CPU/GPU/CUDA, validar o gerenciamento por `uv`, confirmar o isolamento do diretório via testes de fronteira e preparar a infraestrutura para benchmarks científicos.
- **Artefatos**: Diretório [`experiments/EXP-000/`](../experiments/EXP-000/).
- **Entregável**: Relatório formal em `experiments/EXP-000/RESULTS.md` com status de aptidão do ambiente.

### `EXP-001` — HTR em Linhas Manuscritas *(FASE ATUAL — em especificação, ver `experiments/EXP-001/`)*
- **Objetivo**: Transformar imagens isoladas de linhas manuscritas em português em texto puro. Comparar *baseline zero-shot* contra arquiteturas com eventual adaptação/fine-tuning.
- **Métricas**: CER, WER, latência de inferência e consumo de VRAM.
- **Critério**: Não escolher modelos por popularidade; auditar candidatos (ex.: TrOCR, PyLaia, CTC/CRNN) em dataset controlado.

### `EXP-002` — Detecção de Layout e Segmentação de Blocos/Regiões
- **Objetivo**: Localizar na página fotográfica os limites das linhas, parágrafos, cabeçalhos, notas de margem e caixas gráficas.
- **Métricas**: IoU, mAP, Precision e Recall de detecção de caixas.

### `EXP-003` — Reconstrução Espacial e Ordem de Leitura
- **Objetivo**: Algoritmos topológicos para ordenar blocos e linhas em sequência lógica de leitura coerente, resolvendo colunas múltiplas, anotações marginais inseridas lateralmente e interrupções visuais.
- **Métricas**: Edit Distance da ordem de leitura (*Reading Order Accuracy*).

### `EXP-004` — Classificação Semântica
- **Objetivo**: Rotular trechos do caderno em categorias didáticas (`title`, `concept`, `summary`, `question`, `quote`, `example`) usando pistas visuais e textuais.
- **Métricas**: Macro-F1 e Matriz de Confusão.

### `EXP-005` — Diagramas, Setas e Grafos Conceituais
- **Objetivo**: Detectar caixas conceituais, nós geométricos e setas direcionais, montando o grafo de adjacência de causa, efeito e fluxo.
- **Métricas**: Node Precision/Recall, Edge Precision/Recall e Edge-F1.

### `EXP-006` — Pipeline Integrado Ponta a Ponta
- **Objetivo**: Unificação de todos os componentes experimentais em uma cadeia de inferência completa: receber fotografia bruta e emitir o documento serializado em **LDF 1.0**.
- **Métricas**: Tempo total de resposta por página, memória de pico e aderência estrita ao JSON Schema do LDF.
