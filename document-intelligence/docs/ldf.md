# Leitorum Document Format (LDF) — Versão 2.0.0

O **LDF** é o contrato de dados entre o **Document Intelligence** e o **Leitorum**: a representação de uma página
de caderno fotografada, com o que o pipeline encontrou nela.

* **Fonte normativa:** [`src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json`](../src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json)
  (JSON Schema, draft 2020-12). Em caso de divergência entre este texto e o schema, vale o schema.
* **Regras além do schema:** R1–R9, na §5. Fazem parte do contrato.
* **Casos de conformidade:** [`tests/ldf/conformance/`](../tests/ldf/conformance/) — documentos válidos e inválidos,
  cada inválido com o código de erro esperado em `index.json`. Servem para testar um leitor em qualquer linguagem.
* **Decisão:** [ADR-004](./adr/ADR-004-contrato-ldf-2.0.md). **Versão anterior:** [LDF 1.0](./ldf-1.0.md), congelada.

O formato descreve o que os experimentos aceitos já produzem (layout e ordem de leitura). A camada `semantics` e o
detalhe de nós e arestas dos diagramas são **provisórios** até os EXP-004 e EXP-005.

---

## 1. Princípios

1. **Três camadas.** `recognition` (linhas e texto lido), `structure` (regiões, ordem de leitura, diagramas) e
   `semantics` (interpretação). O texto reconhecido nunca é reescrito por outra camada.
2. **Uma página por documento.**
3. **Coordenadas na fotografia original**, em pixels. É a imagem que o leitor fotografou e vê na tela.
4. **Etapa não executada é dita, não inferida.** Cada etapa do pipeline tem estado próprio.
5. **A saída original é intocável.** Correções humanas ficam numa lista à parte; a versão corrigida é calculada.
6. **Nada de campo desconhecido.** Todo objeto recusa propriedades que o schema não define.

## 2. Estrutura

```json
{
  "ldf_version": "2.0.0",
  "document_id": "00000000-0000-0000-0000-000000000002",
  "created_at": "2026-10-12T20:00:00Z",
  "source_image": { "filename": "pagina_ficticia.jpg", "width": 1200, "height": 1600, "sha256": "…" },
  "coordinate_space": { "frame": "source_image", "unit": "pixel" },
  "pipeline": {
    "stages": {
      "layout":        { "status": "completed", "component": { "name": "…", "version": "…", "license": "MIT", "license_status": "VERIFIED" }, "elapsed_ms": 12.5 },
      "reading_order": { "status": "completed", "component": { "name": "…", "version": "…", "license": "N/A", "license_status": "N/A" } },
      "recognition":   { "status": "not_run" },
      "semantics":     { "status": "not_run" },
      "diagrams":      { "status": "not_run" }
    }
  },
  "recognition": {
    "lines": [ { "id": "line_001", "bbox": [100, 100, 700, 150], "detection_confidence": 0.97 } ]
  },
  "structure": {
    "regions": [
      { "id": "region_001", "type": "title",   "bbox": [90, 90, 710, 160],   "line_ids": ["line_001"] },
      { "id": "region_002", "type": "graphic", "bbox": [150, 500, 900, 900], "line_ids": [] }
    ],
    "reading_order": ["region_001", "region_002"],
    "diagrams": []
  },
  "human_corrections": []
}
```

Exemplos completos em [`docs/ldf-examples/`](./ldf-examples/): `ldf-2.0-minimal.json`, `ldf-2.0-layout-only.json`,
`ldf-2.0-rectified.json` e `ldf-2.0-with-corrections.json`.

## 3. Componentes

### 3.1 Identificadores

Todo elemento tem `id`: letras, dígitos, `_`, `.`, `:` e `-`, começando por letra ou dígito. Os identificadores são
**únicos no documento inteiro** (R1), não só dentro da sua lista. É por eles que as correções encontram o alvo.

### 3.2 Geometria e coordenadas

* `bbox`: `[x_min, y_min, x_max, y_max]`, em pixels da fotografia original. Aceita decimais.
* `polygon` (opcional): três ou mais vértices `[x, y]`, **em sentido horário** com o eixo y para baixo. Use para
  linhas e regiões inclinadas. Quando existe, a `bbox` é o seu envelope (R6).
* `coordinate_space.rectification` (opcional): presente quando o pipeline endireitou a folha antes de analisar.
  * `source_quad`: os quatro cantos da folha na fotografia — superior esquerdo, superior direito, inferior
    direito, inferior esquerdo.
  * `output_size`: `[largura, altura]` da imagem retificada.
  * `homography`: matriz 3×3 que leva um ponto da fotografia para a imagem retificada. A inversa faz o caminho de
    volta.
  * `method`: nome do método de retificação.

  A geometria do documento **continua na fotografia original**; a retificação é só metadado para quem precisar
  reproduzir a imagem em que os modelos trabalharam.

### 3.3 `pipeline.stages`

Cinco etapas, todas obrigatórias: `layout`, `reading_order`, `recognition`, `semantics`, `diagrams`.

| Campo | Significado |
| :--- | :--- |
| `status` | `completed`, `not_run` ou `failed` |
| `component` | quem executou: `name`, `version`, `revision` (opcional), `license`, `license_status` (`VERIFIED`, `NEEDS VALIDATION` ou `N/A`) |
| `elapsed_ms` | tempo da etapa |
| `error` | motivo, só quando `failed` |

`license_status` segue a política de [`models-and-licensing.md`](./models-and-licensing.md). Um documento produzido
com componente `NEEDS VALIDATION` carrega essa marca consigo.

### 3.4 `recognition.lines`

| Campo | Obrigatório | Significado |
| :--- | :---: | :--- |
| `id`, `bbox` | sim | identidade e localização |
| `polygon` | não | contorno da linha |
| `detection_confidence` | não | confiança de que há uma linha ali |
| `text`, `confidence` | ver R7 | texto lido e confiança da leitura; só existem se a etapa `recognition` foi concluída |
| `is_handwritten` | não | manuscrito ou impresso |

### 3.5 `structure`

* `regions`: áreas da página. `type` é um de `title`, `paragraph`, `margin_note`, `graphic`. `line_ids` lista as
  linhas da região, na ordem em que são lidas dentro dela. Uma linha pertence a no máximo uma região (R4); pode
  não pertencer a nenhuma.
* `reading_order`: identificadores de regiões, na ordem de leitura. Qualquer tipo de região pode entrar, inclusive
  `graphic`. Uma região pode ficar fora da ordem; nenhuma entra duas vezes (R3).
* `diagrams`: cada diagrama aponta, por `region_id`, para uma região `graphic`, que é quem guarda a sua localização.
  `nodes` e `edges` seguem como no LDF 1.0 e são provisórios.

Os tipos `heading`, `text_block`, `list_item`, `table` e `diagram_region`, que existiam em rascunhos anteriores,
não fazem parte do 2.0: nenhum experimento os produziu.

### 3.6 `semantics` (provisória)

Opcional. `sections` (com `role`) e `entities`, ambos referindo regiões por `region_ids`. O vocabulário será revisto
depois do EXP-004; não construa sobre ele.

## 4. Correções humanas

Cada item de `human_corrections` é:

```json
{
  "id": "correction_001",
  "author": "leitor-ficticio",
  "timestamp": "2026-10-12T21:00:00Z",
  "reason": "palavra lida errado",
  "target": { "collection": "recognition.lines", "id": "line_003" },
  "ops": [ { "op": "replace", "path": "/text", "value": "segunda linha, corrigida" } ]
}
```

* `target.collection` é uma de `recognition.lines`, `structure.regions`, `structure.reading_order`,
  `structure.diagrams`, `semantics.sections`, `semantics.entities`.
* Com `target.id`, as operações são **relativas ao elemento**: `/text` é o texto daquela linha, esteja ela onde
  estiver no vetor. Caminho vazio (`""`) é o elemento inteiro, e só aceita `remove`, `replace` e `test`.
* Sem `target.id`, as operações são relativas à coleção: `{"op": "add", "path": "/-", "value": {…}}` acrescenta um
  elemento. `structure.reading_order` nunca leva `id`; para reordenar, substitua a lista (`replace` em `""`).
* `ops` são operações **RFC 6902** (`add`, `remove`, `replace`, `move`, `copy`, `test`) com caminhos RFC 6901.
* As correções são aplicadas **na ordem da lista**. O alvo é localizado no momento da aplicação, de modo que uma
  correção continua válida depois que outra insere ou remove elementos.
* Para remover uma linha, retire-a antes de `line_ids` da região que a contém; caso contrário o resultado viola R2.

**O que é guardado.** O documento guarda a saída original do pipeline mais a lista de correções. A versão corrigida
é uma visão calculada (`apply_corrections`) e não deve ser gravada como documento LDF. Quem precisar de um JSON
Patch comum, de caminhos absolutos, obtém-no com `to_json_patch`.

## 5. Regras além do schema

Um documento só é válido se passar no schema **e** nestas regras. Os códigos são estáveis.

| Código | Regra |
| :--- | :--- |
| V1 | `ldf_version` é de uma versão que o leitor suporta (§6) |
| S1 | O documento tem a forma definida pelo JSON Schema |
| R1 | Identificadores únicos no documento inteiro |
| R2 | Toda referência aponta para elemento existente: `line_ids`, `reading_order`, `region_ids`, `region_id` do diagrama (que deve ser região `graphic`) e as pontas das arestas (nós do mesmo diagrama) |
| R3 | `reading_order` não repete região |
| R4 | Uma linha aparece em no máximo uma região, e uma vez só |
| R5 | Toda `bbox` tem largura e altura positivas e está dentro da imagem, com tolerância de 1 px |
| R6 | Havendo `polygon`, ele tem área positiva em sentido horário e a `bbox` é o seu envelope, com tolerância de 1 px |
| R7 | Etapa `recognition` concluída: toda linha tem `text` e `confidence`. Não concluída: nenhuma linha tem |
| R8 | Etapa `failed` tem `error`, e só ela. Etapa `completed` tem `component`. Etapa não concluída não tem conteúdo: `layout` → sem linhas nem regiões; `reading_order` → ordem vazia; `diagrams` → sem diagramas; `semantics` → sem seções nem entidades |
| R9 | Todas as correções se aplicam, em ordem, e a visão corrigida respeita o schema e R1–R6 |

R7 e R8 valem para a saída original. A visão corrigida não está sujeita a elas: o leitor pode digitar o texto de
uma linha numa página em que o reconhecimento não rodou.

## 6. Versões

O LDF usa SemVer. **MAJOR** quebra leitores; **MINOR** acrescenta campos ou valores; **PATCH** só esclarece.

* Um leitor aceita a versão MAJOR que conhece e MINOR menor ou igual à sua.
* Diante de versão mais nova, **recusa** com erro de versão não suportada (V1), em vez de ler pela metade.
* Cada versão MINOR publica um arquivo de schema novo. Os anteriores não são editados.
* O LDF 1.0 nunca foi lido por nenhum sistema; não há migração de 1.0 para 2.0.

## 7. Uso em Python

```python
from leitorum_di.contracts.ldf import validate, apply_corrections, build_document, LDFDocument

problemas = validate(documento)          # lista vazia = válido; cada item tem code, path, message
corrigido = apply_corrections(documento) # visão corrigida; o original não muda
tipado = LDFDocument.model_validate(documento)  # acesso tipado; não aplica R1–R9
```

Guia passo a passo em [`specs/001-contrato-ldf/quickstart.md`](../specs/001-contrato-ldf/quickstart.md).
