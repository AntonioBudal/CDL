# Guia rápido: LDF 2.0

Tudo a partir de `document-intelligence/`. Nada aqui usa rede, modelos ou dados reais.

## 1. Conferir o contrato

```powershell
uv sync
uv run pytest tests/ldf -q
```

Esperado: todos os testes passam (201 em 2026-10-12).

## 2. Validar um documento

```python
import json
from leitorum_di.contracts.ldf import validate

documento = json.load(open("docs/ldf-examples/ldf-2.0-layout-only.json", encoding="utf-8"))
for problema in validate(documento):
    print(problema.code, problema.path, problema.message)   # nada impresso = válido
```

Códigos: `V1` versão não suportada, `S1` forma (JSON Schema), `R1`–`R9` regras de [`docs/ldf.md`](../../docs/ldf.md) §5.
Para ver uma recusa, valide qualquer arquivo de `tests/ldf/conformance/invalid/`; o código esperado de cada um está
em `tests/ldf/conformance/index.json`.

## 3. Aplicar correções humanas

```python
from leitorum_di.contracts.ldf import apply_corrections, to_json_patch

documento = json.load(open("docs/ldf-examples/ldf-2.0-with-corrections.json", encoding="utf-8"))
corrigido = apply_corrections(documento)   # visão corrigida; `documento` não muda
patch = to_json_patch(documento)           # o mesmo, como JSON Patch RFC 6902 de caminhos absolutos
```

## 4. Converter a saída de um detector

```python
from leitorum_di.contracts.ldf import build_document, component

documento = build_document(
    image={"filename": "pagina.png", "width": 1200, "height": 1600, "sha256": "…64 hex…"},
    lines=[{"bbox": [100, 100, 700, 150], "score": 0.97}],
    regions=[{"type": "title", "bbox": [90, 90, 710, 160]},
             {"type": "graphic_box", "bbox": [150, 500, 900, 900]}],
    reading_order=[0, 1],
    stages={"layout": {"component": component("detector", "0.1.0", license="MIT", license_status="VERIFIED")},
            "reading_order": {"component": component("ordenador", "0.1.0")}},
)
```

O resultado já sai validado; entrada que viole o contrato levanta `LDFValidationError`. Para geometria medida na
imagem retificada, passe `rectification=rectification_from_corners(cantos, tamanho, método)` e
`input_frame="rectified"`: as coordenadas voltam para a fotografia original.

## 5. Mudar o contrato

1. Edite `src/leitorum_di/contracts/ldf/schemas/ldf-2.0.schema.json` (só enquanto o ADR-004 estiver `PROPOSED`;
   depois do aceite, mudança entra como arquivo de versão nova).
2. Ajuste `models.py` até `tests/ldf/test_models_parity.py` passar.
3. Acrescente casos em `tests/ldf/make_conformance.py` e rode `uv run python tests/ldf/make_conformance.py`.
4. Atualize `docs/ldf.md`.

## 6. Critérios de sucesso — resultado medido em 2026-10-12

| Critério | Resultado |
| :--- | :--- |
| SC-001 — mesmo veredicto pelas duas vias | **Atendido.** 59 casos (12 válidos, 47 inválidos): schema e modelo Pydantic concordam em todos; estrutura idêntica campo a campo |
| SC-002 — 180 páginas do EXP-003 sem lacunas | **Atendido.** 180 de 180 com o layout verdadeiro; zero regiões descartadas; 102 caixas gráficas na ordem de leitura. Verificação extra com o layout detectado (arquivo no disco, fora do Git): 180 de 180, 3 561 regiões e 3 777 linhas, zero problemas |
| SC-003 — inválidos rejeitados com o código certo | **Atendido.** 47 de 47, cada um apenas com o código declarado; ao menos dois casos por código (`V1`, `S1`, `R1`–`R9`) |
| SC-004 — experimentos aceitos intactos | **Atendido.** Schema 1.0 com o mesmo hash; árvores Git dos EXP-001 a EXP-003 iguais às de antes da feature; testes dos harness dos EXP-002 e EXP-003 passam nos ambientes deles (33 e 46), rodados com `--frozen` |
| SC-005 — lacunas resolvidas ou adiadas | **Atendido.** L1–L10 resolvidas, com uma limitação declarada em L9; semântica e nós de diagrama adiados (ADR-004 §4) |
| SC-006 — nada fora da pasta | **Atendido.** |

## 7. Limitações conhecidas

* Validar uma página com contornos densos (média de 174 vértices por linha, como devolve o Doc-UFCN) custa cerca
  de 0,13 s; com contornos de 4 a 9 vértices, cerca de 8 ms.
* O modelo Pydantic é estrito com tipos: recusa `1200.0` onde o schema pede inteiro, embora o JSON Schema aceite.
* Para rodar testes ou medições dos EXP-001 e EXP-002 nos ambientes deles, use `uv run --frozen --project …`. Sem
  `--frozen`, o `uv` reescreve o `uv.lock` do ambiente por causa da dependência nova do pacote principal
  (ADR-004 §6).
* `semantics` e os nós e arestas de diagramas são provisórios.
* O formato só foi exercitado com páginas sintéticas.
