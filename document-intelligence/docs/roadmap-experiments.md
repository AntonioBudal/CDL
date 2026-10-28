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

### `EXP-015` — Pipeline com Leitura Direta *(CONCLUÍDO — aceito por delegação em 2026-10-22)*
- **Resultado**: redações 35,9 % → 27,5 % de CER de página de ponta a ponta, sem treino; fotos iguais (27,4 %); 7,4 s por página. Incorporado ao ADR-008.

### `EXP-016` — Leitura em Lote *(CONCLUÍDO — aceito por delegação em 2026-10-22)*
- **Resultado**: lote de 8 dá o mesmo texto e não acelera (leitura 4,6 → 5,0 s por página na calibração); o custo é meio detecção ampliada, meio margem. Pipeline mantido; testes não usados.

### `EXP-017` — Teto de Ponta a Ponta com o Leitor Ajustado *(CONCLUÍDO — aceito por delegação em 2026-10-22)*
- **Resultado**: leitor do EXP-014 exportado para ONNX no pipeline do ADR-008: redações 27,5 % → 11,8 % de CER de página; inglês 27,4 % → 33,4 %. Modelo só experimental (BRESSAY). Registrado no ADR-009.

### `EXP-018` — Curva de Aprendizado do Ajuste Fino *(CONCLUÍDO — aceito por delegação em 2026-10-26)*
- **Resultado**: 16 / 50 / 150 páginas dão 19,6 % / 15,8 % / 13,7 % de CER de validação (647 páginas: 13,5 %). Pedido de dados recomendado: mínimo ~50 páginas, alvo ~150.

### `EXP-019` — Leitura em Condições de Foto *(CONCLUÍDO — aceito por delegação em 2026-10-26)*
- **Resultado**: leitor ajustado 11,8 % (digitalizada) → 21,6 % (foto leve) → 70,6 % (foto forte). A escala automática erra em linhas inclinadas (129 de 185 páginas com escala menor). Abre o EXP-020.

### `EXP-020` — Escala Medida na Linha Inclinada *(CONCLUÍDO — não adotado, por delegação em 2026-10-26)*
- **Resultado**: a escala sobe, mas o erro não muda na foto leve (21,6 %) e piora na forte (70,6 % → 74,1 %). A perda em foto vem do leitor e do detector, não da escala; regra do ADR-008 mantida.

### `EXP-021` — Ajuste Fino com Degradações de Foto *(CONCLUÍDO — não adotado, por delegação em 2026-10-26)*
- **Resultado**: metade das linhas de treino degradadas como foto: digitalizada 11,8 % → 12,1 %, foto leve 21,6 % → 21,4 %, forte 70,6 % → 69,9 %. O aumento não fecha a perda em foto; as páginas pedidas para o produto devem ser fotos.

### `EXP-022` — Páginas do BRESSAY Impressas e Fotografadas *(CONCLUÍDO com ressalva — por delegação em 2026-10-27)*
- **Resultado**: 15 páginas impressas e fotografadas pelo usuário, entregues depois de conversor e recorte: leitor ajustado 11,0 % (as mesmas digitalizadas: 10,7 %), original 24,3 % (24,1 %). As imagens não têm inclinação de câmera (0,12° contra 0,11° na digitalização); medem página limpa por software, não a foto crua. O custo da câmera crua segue sem medida.

### Promoção ao Leitorum — feature 086 *(2026-10-27, decisão do usuário)*
- **Resultado**: pipeline do ADR-008 com o leitor original levado ao Leitorum (`caderno-leitura-0.1/motor/`, tela `/digitalizar`), texto como rascunho a revisar e salvo como Estudo. Validação com foto crua de celular dispensada pelo usuário. Paridade com o EXP-019: 458/458 linhas idênticas nas páginas do EXP-022. Ver ADR-008 §5.

### `EXP-023` — Organização nas 4 Seções do Estudo *(CONCLUÍDO em 2026-10-27; ADR-010 aceito pelo usuário)*
- **Resultado**: pipeline em Python puro (pistas + n-gramas de caracteres + Viterbi com custo de troca por coesão), < 10 ms por página. Páginas fictícias: Macro-F1 0,93 (limpo) e 0,82 (CER 25 %, com geometria); portão de produto atingido. Estudos reais do usuário (N = 3, só números): 0,50, lacuna de domínio. H1 e H2 refutadas (léxico e matriz relacional ajudam pouco); transição e propagação desligadas pela validação.

### `EXP-004` — Classificação Semântica
- **Objetivo**: Rotular trechos do caderno em categorias didáticas (`title`, `concept`, `summary`, `question`, `quote`, `example`) usando pistas visuais e textuais.
- **Métricas**: Macro-F1 e Matriz de Confusão.

### `EXP-005` — Diagramas, Setas e Grafos Conceituais
- **Objetivo**: Detectar caixas conceituais, nós geométricos e setas direcionais, montando o grafo de adjacência de causa, efeito e fluxo.
- **Métricas**: Node Precision/Recall, Edge Precision/Recall e Edge-F1.

### `EXP-006` — Pipeline Integrado Ponta a Ponta
- **Objetivo**: Unificação de todos os componentes experimentais em uma cadeia de inferência completa: receber fotografia bruta e emitir o documento serializado em **LDF 2.0** (contrato fechado em 2026-10-12, ADR-004).
- **Métricas**: Tempo total de resposta por página, memória de pico e aderência estrita ao JSON Schema do LDF.
