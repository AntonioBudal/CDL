# Plano técnico: Fechamento do contrato LDF (LDF 2.0)

* **Feature:** `001-contrato-ldf`
* **Especificação:** [`spec.md`](./spec.md) (`APPROVED` em 2026-10-12)
* **Status:** `APPROVED` (aprovado pelo usuário em 2026-10-12, com `jsonschema` autorizado como dependência)
* **Próximo artefato:** [`tasks.md`](./tasks.md)

---

## 1. Resumo

Publicar o **LDF 2.0.0** com o JSON Schema como fonte normativa, um conjunto de regras que o schema não consegue
expressar (integridade referencial, coerência entre etapas, geometria), um modelo Python conferido contra o schema,
a aplicação de correções humanas por identificador e um conversor de referência. O schema 1.0 e os diretórios dos
experimentos aceitos não são tocados.

## 2. Contexto técnico

| Item | Valor |
| :--- | :--- |
| Linguagem | Python ≥ 3.11 (ambiente principal em 3.14.3), `uv` |
| Dependências atuais | `pydantic` ≥ 2.7 |
| **Dependência nova** | `jsonschema` (MIT, Python puro mais `rpds-py`; já usado nos ambientes dos EXP-002/003). Autorizada pelo usuário em 2026-10-12 — ver §9 |
| Testes | `pytest`, `ruff`; só dados fictícios |
| Rede, modelos, datasets | nenhum |
| Disco | desprezível (texto) |

## 3. Conferência com a Constituição

* **Local-first:** sem rede, sem serviço.
* **Sem modelos prematuros:** nenhuma biblioteca de OCR/HTR; `jsonschema` é validação de dados.
* **Experimentos antes de features:** o contrato só passa a representar o que os EXP-002/003 já produzem; semântica
  e diagramas detalhados ficam para depois dos EXP-004/005.
* **LDF como contrato:** é o objeto da feature; a mudança é registrada no ADR-004.
* **Human-in-the-loop:** correções continuam sendo operações RFC 6902.
* **Escopo:** tudo dentro de `document-intelligence/`.

## 4. Desenho do LDF 2.0

As três camadas do formato (`recognition`, `structure`, `semantics`) são mantidas. O que muda:

```text
ldf_version            "2.0.x"
document_id, created_at
source_image           { filename, width, height, dpi?, sha256 }
coordinate_space       { frame: "source_image", unit: "pixel",
                         rectification?: { method, source_quad, output_size, homography } }
pipeline.stages        layout | reading_order | recognition | semantics | diagrams →
                         { status: completed | not_run | failed,
                           component?: { name, version, revision?, license, license_status },
                           elapsed_ms?, error? }
recognition.lines[]    { id, bbox, polygon?, detection_confidence?,
                         text?, confidence?, is_handwritten? }
structure.regions[]    { id, type: title | paragraph | margin_note | graphic,
                         bbox, polygon?, line_ids, confidence? }
structure.reading_order  [ id de região, … ]
structure.diagrams[]   { id, region_id, nodes, edges }        (nós e arestas como no 1.0)
semantics              { sections, entities }                 (como no 1.0, marcada provisória)
human_corrections[]    { id, author, timestamp, reason?,
                         target: { collection, id? }, ops: [ operação RFC 6902 ] }
```

Como cada lacuna é resolvida:

| Lacuna | Solução |
| :--- | :--- |
| L1 dois contratos | Um arquivo de schema; modelo Python comparado campo a campo e por veredicto (§6) |
| L2 região de diagrama | Todo diagrama aponta para uma região do tipo `graphic`, que tem caixa |
| L3 ordem só com blocos | `blocks` vira `regions`; a ordem aceita qualquer região, inclusive `graphic` |
| L4 etapa não executada | `pipeline.stages` com estado por etapa; `text` e `confidence` da linha deixam de ser obrigatórios; `semantics` deixa de ser obrigatória |
| L5 coordenadas | Tudo na fotografia original; `rectification` guarda o quadrilátero da folha e a matriz foto → imagem retificada |
| L6 linhas inclinadas | Coordenadas aceitam decimais; polígono com 3 ou mais vértices, em sentido horário; a caixa é o envelope do polígono |
| L7 vocabulário | Quatro tipos, os que os experimentos produziram. `heading`, `text_block`, `list_item`, `table` e `diagram_region` saem; voltam por versão MINOR quando houver evidência |
| L8 integridade | Regras R1–R9 abaixo, verificadas em código e por casos de conformidade |
| L9 correções | A correção aponta para o elemento pelo `id`; os caminhos das operações são relativos a ele. A posição no vetor é resolvida na hora de aplicar. O documento guarda a saída original; a versão corrigida é calculada |
| L10 metadados | `component` com nome, versão, revisão e estado de licença (`VERIFIED`, `NEEDS VALIDATION`, `N/A`) |

### Regras além do schema

O JSON Schema confere forma e tipos. Estas regras ficam escritas em `docs/ldf.md` com código próprio, para que um
leitor em outra linguagem possa implementá-las:

| Código | Regra |
| :--- | :--- |
| R1 | Identificadores únicos em todo o documento |
| R2 | `line_ids`, `region_id`, `block_ids`, nós de arestas e `reading_order` apontam para elementos existentes |
| R3 | `reading_order` não repete região; região pode ficar fora da ordem |
| R4 | Uma linha pertence a no máximo uma região |
| R5 | Caixas com largura e altura positivas, dentro da imagem (tolerância de 1 px) |
| R6 | Havendo polígono, a caixa é o seu envelope (tolerância de 1 px) |
| R7 | Etapa `recognition` não concluída → nenhuma linha com `text`; concluída → todas com `text` e `confidence` |
| R8 | Etapa `not_run` ou `failed` → a parte correspondente do documento está vazia ou ausente; `failed` traz `error` |
| R9 | Toda correção tem alvo existente no momento da aplicação, na ordem da lista |

### Regra de versão

Um leitor aceita apenas a versão MAJOR que conhece e MINOR menor ou igual à sua. Diante de versão mais nova, recusa
com erro de "versão não suportada" em vez de ler parcialmente. Cada MINOR publica um arquivo de schema novo; os
anteriores não são editados.

## 5. Estrutura de arquivos

```text
src/leitorum_di/contracts/ldf/            (substitui o módulo ldf.py atual, que não corresponde a schema nenhum)
├── __init__.py                           API pública
├── schemas/ldf-2.0.schema.json           FONTE NORMATIVA (única cópia; empacotada com o código)
├── schema.py                             carga do schema e validação de forma
├── rules.py                              regras R1–R9
├── validate.py                           validate(doc) → lista de problemas (código, caminho, mensagem)
├── models.py                             modelo Pydantic espelhando o schema
├── corrections.py                        aplicação de correções; conversão para JSON Patch absoluto
├── geometry.py                           envelope de polígono; foto ↔ imagem retificada
└── build.py                              conversor de referência: layout + ordem → LDF 2.0

docs/ldf.md                               reescrito para o 2.0 (prosa, regras R1–R9, regra de versão)
docs/ldf-1.0.md                           texto atual, movido e marcado como congelado
docs/schemas/ldf-1.0.schema.json          INALTERADO
docs/schemas/README.md                    aponta para a fonte normativa do 2.0
docs/ldf-examples/ldf-2.0-*.json          mínimo; só layout; página retificada; com correções
docs/adr/ADR-004-contrato-ldf-2.0.md

tests/ldf/
├── conformance/valid/*.json              casos válidos
├── conformance/invalid/*.json            casos inválidos, cada um com o código esperado
├── test_schema.py  test_rules.py  test_models_parity.py
├── test_corrections.py  test_geometry.py  test_build.py
└── test_frozen.py                        hash do schema 1.0; experimentos aceitos sem alteração
```

A pasta `tests/ldf/conformance/` é o que o Leitorum poderá reutilizar no futuro para testar o seu próprio leitor.

## 6. Como a fonte única é garantida

1. **Paridade de estrutura:** um teste percorre o schema e o modelo Pydantic e compara, objeto a objeto, nomes de
   campos, obrigatoriedade e valores enumerados.
2. **Paridade de veredicto:** todo caso de `conformance/` é validado pelas duas vias; o resultado tem de coincidir.
3. **Exemplos:** todo arquivo `docs/ldf-examples/ldf-2.0-*.json` é validado nos testes.
4. **Cópia única:** um teste falha se aparecer outro arquivo `ldf-2.0.schema.json` no repositório.

## 7. Fases

| Fase | Entrega | Verificação |
| :--- | :--- | :--- |
| 1. Schema e prosa | `ldf-2.0.schema.json`, `docs/ldf.md`, `docs/ldf-1.0.md`, exemplos | exemplos válidos; schema 1.0 com o mesmo hash |
| 2. Validação | `schema.py`, `rules.py`, `validate.py`, casos de conformidade | SC-003: todo caso inválido rejeitado com o código certo |
| 3. Modelo Python | `models.py`, testes de paridade | SC-001 |
| 4. Correções | `corrections.py` | história 4: correção sobrevive à remoção de outra linha; original recuperável |
| 5. Conversor | `geometry.py`, `build.py` | SC-002: 180 páginas de teste do EXP-003 (layout verdadeiro do manifesto versionado) sem lacunas |
| 6. Fechamento | ADR-004, índice de ADRs, `CLAUDE.md`, relatório curto de verificação | SC-004, SC-005, SC-006 |

O layout **detectado** do EXP-003 não está no Git (fica em `dataset/processed/`). Se o arquivo ainda existir no
disco, a conversão dele entra como verificação adicional no relatório; se não existir, não é regenerado — exigiria
carregar os modelos, o que está fora desta feature.

## 8. Riscos

| Risco | Tratamento |
| :--- | :--- |
| Desenhar campos que nenhum experimento exercitou | Só entram campos com produtor conhecido; semântica e nós de diagrama ficam como estão, marcados provisórios |
| A retificação medida no EXP-002 não guardou a matriz | O manifesto do EXP-003 traz `page_corners`; a matriz é calculada a partir deles no conversor. O campo é opcional no formato |
| Paridade estrutural frágil com construções avançadas do schema | O schema usa só o subconjunto necessário (`$defs`, `enum`, `required`, sem `oneOf` aninhado) |
| Quebrar testes de estrutura existentes | `tests/test_structure.py` exige `docs/ldf.md`, os exemplos 1.0 e a pasta `contracts`; todos permanecem |

## 9. Decisão do usuário: `jsonschema` autorizado (2026-10-12)

**Adicionar `jsonschema` às dependências do pacote principal.** Com o JSON Schema como fonte, é a forma direta de
validar. É uma biblioteca pequena, licença MIT, sem relação com OCR. A alternativa é deixá-la só nos testes e
validar em produção apenas pelo modelo Pydantic; nesse caso a fonte normativa não seria a que valida de fato, e
recomendo não seguir por aí.

## 10. Fora do plano

Leitura do LDF pelo Leitorum, API local, migração de documentos 1.0 (não existe nenhum guardado), atualização dos
conversores dentro de `experiments/EXP-002` e `EXP-003`.
