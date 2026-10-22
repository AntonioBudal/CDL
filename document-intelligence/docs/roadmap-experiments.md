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

### `EXP-001` — HTR em Linhas Manuscritas *(CONCLUÍDO — aceito em 2026-10-02; decisão no ADR-001)*
- **Objetivo**: Transformar imagens isoladas de linhas manuscritas em português em texto puro. Comparar *baseline zero-shot* contra arquiteturas com eventual adaptação/fine-tuning.
- **Métricas**: CER, WER, latência de inferência e consumo de VRAM.
- **Critério**: Não escolher modelos por popularidade; auditar candidatos (ex.: TrOCR, PyLaia, CTC/CRNN) em dataset controlado.

### `EXP-002` — Detecção de Layout e Segmentação de Blocos/Regiões *(CONCLUÍDO — aceito em 2026-10-05; direção no ADR-002)*
- **Objetivo**: Localizar na página fotográfica os limites das linhas, parágrafos, cabeçalhos, notas de margem e caixas gráficas.
- **Métricas**: IoU, mAP, Precision e Recall de detecção de caixas.

### `EXP-003` — Reconstrução Espacial e Ordem de Leitura *(CONCLUÍDO — aceito em 2026-10-12; decisão no ADR-003)*
- **Objetivo**: Algoritmos topológicos para ordenar blocos e linhas em sequência lógica de leitura coerente, resolvendo colunas múltiplas, anotações marginais inseridas lateralmente e interrupções visuais.
- **Métricas**: Edit Distance da ordem de leitura (*Reading Order Accuracy*).

### `EXP-007` — Validação em Imagens Reais *(CONCLUÍDO — aceito em 2026-10-13; decisão no ADR-005)*
- **Objetivo**: Medir o pipeline dos ADR-002 e ADR-003, sem ajustes, em fotos de celular (GNHK) e em caligrafia portuguesa (BRESSAY). Executado depois do EXP-003 e antes do EXP-004.
- **Resultado**: o F1 de linhas cai de 0,78–0,93 (sintético) para 0,35–0,37; a retificação por contorno piora; os blocos saem como texto único. Decisão no ADR-005. Próximo: `EXP-008` (detecção de linhas em manuscrito real).

### `EXP-008` — Detecção de Linhas em Manuscrito Real *(CONCLUÍDO — aceito por delegação em 2026-10-18)*
- **Resultado**: PP-OCRv6 small det + fusão de fragmentos: F1 0,812 (GNHK) e 0,982 (BRESSAY), contra 0,428 e 0,675 do Doc-UFCN. Proposta no ADR-006.

### `EXP-009` — Leitura de Manuscrito com o PP-OCR *(CONCLUÍDO — aceito por delegação em 2026-10-18)*
- **Resultado**: CER 38,5 % nas linhas do EXP-001 (antes: 69,4 %); 14,8 % em inglês fotografado; letras acentuadas com 80 % de erro. ADR-001 mantido (ADR-007).

### `EXP-010` — Outros Reconhecedores e Escala da Linha *(CONCLUÍDO — aceito por delegação em 2026-10-18)*
- **Resultado**: melhor leitura em português: PP-OCRv6 small com recorte ampliado 2×, CER 34,4 %; medium e latino não superam. Evidência no ADR-007.

### `EXP-011` — Correção Lexical *(CONCLUÍDO — aceito por delegação em 2026-10-18)*
- **Resultado**: WER −7,1 e CER −0,6 pontos com dicionário do português; ajuda pouco. Evidência no ADR-007.

### `EXP-012` — Pipeline Integrado Foto → LDF 2.0 *(CONCLUÍDO — aceito por delegação em 2026-10-18; cumpre o objetivo do EXP-006 com os componentes validados)*
- **Resultado**: CER de página 27,5 % (fotos, inglês), 36,2 % (português, página 3×), 45,8 % (português, nativa); 2,7–5,2 s por página; 100 % LDF 2.0 válido. Decisão no ADR-008.

### `EXP-013` — Escala Automática da Página *(CONCLUÍDO — aceito por delegação em 2026-10-18)*
- **Resultado**: ampliar a página até linhas de ~80 px: redação original 45,8 % → 35,9 % de CER; fotos sem mudança (27,3 %). Incorporado ao ADR-008.

### `EXP-014` — Ajuste Fino do Reconhecedor *(CONCLUÍDO — aceito por delegação em 2026-10-22)*
- **Resultado**: leitura direta com margem de 640 px: CER 41,9 % → 29,7 % sem treino; ajuste fino experimental (BRESSAY, < 1 época): 13,6 % (12,4 % com correção lexical). Decisão no ADR-009.

### `EXP-004` — Classificação Semântica
- **Objetivo**: Rotular trechos do caderno em categorias didáticas (`title`, `concept`, `summary`, `question`, `quote`, `example`) usando pistas visuais e textuais.
- **Métricas**: Macro-F1 e Matriz de Confusão.

### `EXP-005` — Diagramas, Setas e Grafos Conceituais
- **Objetivo**: Detectar caixas conceituais, nós geométricos e setas direcionais, montando o grafo de adjacência de causa, efeito e fluxo.
- **Métricas**: Node Precision/Recall, Edge Precision/Recall e Edge-F1.

### `EXP-006` — Pipeline Integrado Ponta a Ponta
- **Objetivo**: Unificação de todos os componentes experimentais em uma cadeia de inferência completa: receber fotografia bruta e emitir o documento serializado em **LDF 2.0** (contrato fechado em 2026-10-12, ADR-004).
- **Métricas**: Tempo total de resposta por página, memória de pico e aderência estrita ao JSON Schema do LDF.
