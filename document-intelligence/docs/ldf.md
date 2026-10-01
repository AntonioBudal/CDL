# Leitorum Document Format (LDF) — Versão 1.0.0

O **Leitorum Document Format (LDF)** é a especificação do contrato de dados que conecta o subsistema **Document Intelligence** ao ecossistema da aplicação **Leitorum**. Ele padroniza a representação digital de cadernos físicos e anotações manuscritas digitalizadas.

---

## 1. Princípios Arquiteturais do Formato

1. **Separação Trilateral de Responsabilidades**:
   - O LDF divide estritamente a representação da página em três camadas desacopladas:
     - **`recognition`**: Dados brutos de OCR/HTR (texto fiel, transcrição de linhas, caixas delimitadoras físicas e pontuações de confiança dos modelos).
     - **`structure`**: Organização espacial e geométrica (blocos de texto, parágrafos, nós visuais, caixas de diagramas, setas direcionais, conectores e ordem natural de leitura).
     - **`semantics`**: Interpretação de significado orientada ao estudo (classificação dos elementos como títulos, conceitos, resumos, citações, perguntas, exemplos e anotações marginais).
2. **Local-First & Imutabilidade de Origem**:
   - O documento reflete fielmente o artefato físico digitalizado. O texto original reconhecido nunca é reescrito silenciosamente pela camada semântica.
3. **Evolução Versionada (SemVer)**:
   - A especificação adota *Semantic Versioning*:
     - **MAJOR**: Alterações estruturais que quebrem compatibilidade com leitores do LDF existente.
     - **MINOR**: Adição de novos tipos semânticos, novos atributos ou metadados retrocompatíveis.
     - **PATCH**: Correções de schemas, esclarecimentos de documentação ou validações mais estritas.
4. **Human-in-the-Loop via RFC 6902 JSON Patch**:
   - Correções manuais feitas pelo usuário no Leitorum (ex.: correção de uma palavra manuscrita, ajuste de um polígono delimitador ou reclassificação de um conceito) são persistidas como operações padronizadas de **JSON Patch (RFC 6902)** aplicadas sobre o documento base, garantindo rastreabilidade e reversibilidade.

---

## 2. Estrutura Canônica do Documento LDF 1.0

A raiz do documento LDF é composta por:

```json
{
  "ldf_version": "1.0.0",
  "document_id": "018f3a90-8b1e-723a-bc4e-123456789abc",
  "created_at": "2026-09-30T20:30:00Z",
  "source_image": {
    "filename": "caderno_fisica_pag_042.jpg",
    "width": 2480,
    "height": 3508,
    "dpi": 300,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  "pipeline_metadata": {
    "model_versions": {
      "detector": "layout-detector-v0",
      "htr": "htr-pt-baseline-v0",
      "semantic": "classifier-v0"
    },
    "processing_time_ms": 420
  },
  "recognition": {
    "lines": [
      {
        "id": "line_01",
        "bbox": [120, 240, 980, 310],
        "polygon": [[120, 240], [980, 240], [980, 310], [120, 310]],
        "text": "Primeira Lei da Termodinâmica",
        "confidence": 0.94,
        "is_handwritten": true
      }
    ]
  },
  "structure": {
    "reading_order": ["block_01", "block_02"],
    "blocks": [
      {
        "id": "block_01",
        "type": "text_block",
        "bbox": [120, 230, 1000, 480],
        "line_ids": ["line_01"],
        "confidence": 0.92
      }
    ],
    "diagrams": [
      {
        "id": "diag_01",
        "nodes": [
          { "id": "node_heat", "label": "Calor (Q)", "bbox": [150, 600, 350, 720] },
          { "id": "node_work", "label": "Trabalho (W)", "bbox": [550, 600, 750, 720] }
        ],
        "edges": [
          { "id": "edge_01", "source": "node_heat", "target": "node_work", "type": "arrow", "label": "Conversão" }
        ]
      }
    ]
  },
  "semantics": {
    "sections": [
      {
        "id": "sec_01",
        "role": "title",
        "block_ids": ["block_01"],
        "label": "Título Principal",
        "confidence": 0.96
      }
    ],
    "entities": [
      {
        "id": "ent_01",
        "type": "concept",
        "text_reference": "Primeira Lei da Termodinâmica",
        "block_ids": ["block_01"],
        "confidence": 0.90
      }
    ]
  },
  "human_corrections": []
}
```

---

## 3. Especificação dos Componentes

### 3.1 Camada `recognition`
- Contém a transcrição direta realizada pelos motores de HTR/OCR.
- Elemento central: `lines` e `words` opcionais.
- Cada elemento possui:
  - `id`: Identificador estável único na página.
  - `bbox`: Coordenadas `[x_min, y_min, x_max, y_max]` em pixels relativos à imagem original.
  - `polygon`: Opcional, lista de vértices `[[x, y], ...]` para textos inclinados ou polígonos curvos.
  - `text`: Texto literal reconhecido em UTF-8.
  - `confidence`: Valor em ponto flutuante `[0.0, 1.0]`.
  - `is_handwritten`: Booleano diferenciando manuscrito de impresso.

### 3.2 Camada `structure`
- Define como as linhas se agrupam no espaço físico do papel.
- Elementos:
  - `blocks`: Parágrafos, cabeçalhos, colunas ou listas agrupando linhas físicas (`line_ids`).
  - `reading_order`: Lista ordenada de identificadores de blocos representando a sequência lógica de leitura sugerida pelo modelo.
  - `diagrams`: Grafos visuais contendo nós (`nodes`) e arestas direcionadas (`edges`) com seus respectivos rótulos e caixas delimitadoras.

### 3.3 Camada `semantics`
- Projeta o significado didático das seções sobre a estrutura.
- Papéis canônicos suportados:
  - `title`: Título de assunto ou subtema;
  - `summary`: Resumo ou síntese;
  - `concept`: Definição de conceito central ou lei científica;
  - `question`: Questão, dúvida ou exercício anotado;
  - `quote`: Citação de obra, livro ou autor;
  - `example`: Exemplo prático ilustrativo;
  - `margin_note`: Observação rápida ou nota de rodapé manuscrita.

### 3.4 Camada `human_corrections`
- Lista de operações RFC 6902 representando mutações aplicadas sobre o documento base:
  ```json
  [
    {
      "op": "replace",
      "path": "/recognition/lines/0/text",
      "value": "Primeira Lei da Termodinâmica (Corrigido)",
      "author": "user",
      "timestamp": "2026-09-30T21:00:00Z"
    }
  ]
  ```

---

## 4. Exemplos e Schemas
- Consulte os exemplos conceituais em [`docs/ldf-examples/`](./ldf-examples/).
- Consulte o JSON Schema formal de validação em [`docs/schemas/ldf-1.0.schema.json`](./schemas/ldf-1.0.schema.json).
