"""Gera os casos de conformidade do LDF 2.0 e os exemplos de ``docs/ldf-examples``.

Uso (a partir de ``document-intelligence/``): ``uv run python tests/ldf/make_conformance.py``.

Os arquivos gerados são versionados; ``test_conformance_is_current`` falha se este script e os
arquivos divergirem. Todo o conteúdo é fictício.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CONFORMANCE = HERE / "conformance"
EXAMPLES = HERE.parents[1] / "docs" / "ldf-examples"

COMPONENTS = {
    "layout": {
        "name": "detector-ficticio",
        "version": "0.1.0",
        "revision": "abc1234",
        "license": "MIT",
        "license_status": "VERIFIED",
    },
    "reading_order": {
        "name": "ordenador-ficticio",
        "version": "0.1.0",
        "license": "N/A",
        "license_status": "N/A",
    },
    "recognition": {
        "name": "htr-ficticio",
        "version": "0.1.0",
        "license": "não declarada",
        "license_status": "NEEDS VALIDATION",
    },
    "semantics": {
        "name": "classificador-ficticio",
        "version": "0.1.0",
        "license": "N/A",
        "license_status": "N/A",
    },
    "diagrams": {
        "name": "grafos-ficticio",
        "version": "0.1.0",
        "license": "N/A",
        "license_status": "N/A",
    },
}


def done(name: str) -> dict[str, Any]:
    return {"status": "completed", "component": copy.deepcopy(COMPONENTS[name]), "elapsed_ms": 12.5}


def skeleton() -> dict[str, Any]:
    """Página vazia: nenhuma etapa executada."""
    return {
        "ldf_version": "2.0.0",
        "document_id": "00000000-0000-0000-0000-000000000002",
        "created_at": "2026-10-12T20:00:00Z",
        "source_image": {
            "filename": "pagina_ficticia.jpg",
            "width": 1200,
            "height": 1600,
            "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
        },
        "coordinate_space": {"frame": "source_image", "unit": "pixel"},
        "pipeline": {
            "stages": {
                name: {"status": "not_run"}
                for name in ("layout", "reading_order", "recognition", "semantics", "diagrams")
            }
        },
        "recognition": {"lines": []},
        "structure": {"regions": [], "reading_order": [], "diagrams": []},
        "human_corrections": [],
    }


def layout_only() -> dict[str, Any]:
    """Layout e ordem de leitura, sem texto reconhecido."""
    doc = skeleton()
    doc["pipeline"]["stages"]["layout"] = done("layout")
    doc["pipeline"]["stages"]["reading_order"] = done("reading_order")
    doc["recognition"]["lines"] = [
        {"id": "line_001", "bbox": [100, 100, 700, 150], "detection_confidence": 0.97},
        {"id": "line_002", "bbox": [100, 220, 800, 270], "detection_confidence": 0.95},
        {"id": "line_003", "bbox": [100, 280, 760, 330], "detection_confidence": 0.93},
        {"id": "line_004", "bbox": [880, 220, 1120, 262], "detection_confidence": 0.81},
    ]
    doc["structure"]["regions"] = [
        {"id": "region_001", "type": "title", "bbox": [90, 90, 710, 160], "line_ids": ["line_001"]},
        {
            "id": "region_002",
            "type": "paragraph",
            "bbox": [90, 210, 810, 340],
            "line_ids": ["line_002", "line_003"],
            "confidence": 0.9,
        },
        {
            "id": "region_003",
            "type": "margin_note",
            "bbox": [870, 210, 1130, 270],
            "line_ids": ["line_004"],
        },
        {"id": "region_004", "type": "graphic", "bbox": [150, 500, 900, 900], "line_ids": []},
    ]
    doc["structure"]["reading_order"] = ["region_001", "region_002", "region_003", "region_004"]
    return doc


TEXTS = [
    "Fichamento de teste",
    "Primeira linha de um parágrafo fictício",
    "segunda linha do mesmo parágrafo",
    "nota de margem",
]


def full() -> dict[str, Any]:
    """Todas as etapas concluídas."""
    doc = layout_only()
    for name in ("recognition", "semantics", "diagrams"):
        doc["pipeline"]["stages"][name] = done(name)
    for line, text in zip(doc["recognition"]["lines"], TEXTS, strict=True):
        line.update(text=text, confidence=0.9, is_handwritten=True)
    doc["structure"]["diagrams"] = [
        {
            "id": "diagram_001",
            "region_id": "region_004",
            "nodes": [
                {"id": "node_001", "label": "Causa", "bbox": [180, 560, 420, 700]},
                {"id": "node_002", "label": "Efeito", "bbox": [620, 560, 860, 700]},
            ],
            "edges": [
                {"id": "edge_001", "source": "node_001", "target": "node_002", "type": "arrow"}
            ],
        }
    ]
    doc["semantics"] = {
        "sections": [
            {"id": "section_001", "role": "title", "region_ids": ["region_001"], "confidence": 0.9}
        ],
        "entities": [
            {
                "id": "entity_001",
                "type": "concept",
                "text_reference": "parágrafo fictício",
                "region_ids": ["region_002"],
            }
        ],
    }
    return doc


def minimal() -> dict[str, Any]:
    """Uma linha lida, uma região."""
    doc = skeleton()
    for name in ("layout", "reading_order", "recognition"):
        doc["pipeline"]["stages"][name] = done(name)
    doc["recognition"]["lines"] = [
        {
            "id": "line_001",
            "bbox": [100, 150, 600, 200],
            "text": "Anotação de teste em linha única",
            "confidence": 0.98,
            "is_handwritten": True,
        }
    ]
    doc["structure"]["regions"] = [
        {
            "id": "region_001",
            "type": "paragraph",
            "bbox": [100, 140, 600, 210],
            "line_ids": ["line_001"],
        }
    ]
    doc["structure"]["reading_order"] = ["region_001"]
    return doc


def rectified() -> dict[str, Any]:
    """Página fotografada em ângulo: polígonos na foto original e metadado de retificação."""
    doc = skeleton()
    doc["pipeline"]["stages"]["layout"] = done("layout")
    doc["pipeline"]["stages"]["reading_order"] = done("reading_order")
    doc["coordinate_space"]["rectification"] = {
        "method": "contorno-ficticio",
        "source_quad": [[100, 100], [1100, 100], [1100, 1500], [100, 1500]],
        "output_size": [1000, 1400],
        "homography": [[1, 0, -100], [0, 1, -100], [0, 0, 1]],
    }
    doc["recognition"]["lines"] = [
        {
            "id": "line_001",
            "bbox": [200, 300, 800, 380],
            "polygon": [[200, 320], [800, 300], [800, 360], [200, 380]],
        }
    ]
    doc["structure"]["regions"] = [
        {
            "id": "region_001",
            "type": "paragraph",
            "bbox": [190, 290, 810, 390],
            "polygon": [[190, 310], [810, 290], [810, 370], [190, 390]],
            "line_ids": ["line_001"],
        }
    ]
    doc["structure"]["reading_order"] = ["region_001"]
    return doc


def correction(ident: str, target: dict[str, Any], ops: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": ident,
        "author": "leitor-ficticio",
        "timestamp": "2026-10-12T21:00:00Z",
        "target": target,
        "ops": ops,
    }


def with_corrections() -> dict[str, Any]:
    """Saída original mais correções: texto, remoção de linha, nova ordem e novo tipo."""
    doc = full()
    doc["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines", "id": "line_003"},
            [{"op": "replace", "path": "/text", "value": "segunda linha, corrigida"}],
        ),
        correction(
            "correction_002",
            {"collection": "structure.regions", "id": "region_003"},
            [{"op": "replace", "path": "/line_ids", "value": []}],
        ),
        correction(
            "correction_003",
            {"collection": "recognition.lines", "id": "line_004"},
            [{"op": "remove", "path": ""}],
        ),
        correction(
            "correction_004",
            {"collection": "structure.reading_order"},
            [
                {
                    "op": "replace",
                    "path": "",
                    "value": ["region_001", "region_003", "region_002", "region_004"],
                }
            ],
        ),
    ]
    doc["human_corrections"][0]["reason"] = "palavra lida errado"
    return doc


def valid_cases() -> dict[str, dict[str, Any]]:
    cases = {
        "empty-page": skeleton(),
        "minimal": minimal(),
        "layout-only": layout_only(),
        "full": full(),
        "rectified": rectified(),
        "with-corrections": with_corrections(),
    }

    doc = layout_only()
    doc["structure"]["regions"][2]["line_ids"] = []
    cases["line-without-region"] = doc

    doc = layout_only()
    doc["structure"]["reading_order"].remove("region_003")
    cases["region-outside-reading-order"] = doc

    doc = full()
    doc["structure"]["diagrams"][0].update(nodes=[], edges=[])
    cases["diagram-without-nodes"] = doc

    doc = layout_only()
    doc["pipeline"]["stages"]["recognition"] = {"status": "failed", "error": "memória insuficiente"}
    cases["failed-stage"] = doc

    doc = layout_only()
    doc["recognition"]["lines"][0]["bbox"] = [100.5, 100.25, 700.75, 150]
    cases["decimal-coordinates"] = doc

    doc = with_corrections()
    doc["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines"},
            [
                {
                    "op": "add",
                    "path": "/-",
                    "value": {"id": "line_005", "bbox": [100, 400, 500, 450]},
                }
            ],
        ),
        correction(
            "correction_002",
            {"collection": "structure.regions", "id": "region_002"},
            [{"op": "add", "path": "/line_ids/-", "value": "line_005"}],
        ),
    ]
    cases["correction-adds-line"] = doc
    return cases


def invalid_cases() -> dict[str, tuple[str, dict[str, Any]]]:
    cases: dict[str, tuple[str, dict[str, Any]]] = {}

    def case(name: str, code: str, base: dict[str, Any]) -> dict[str, Any]:
        cases[name] = (code, base)
        return base

    case("v1-major-3", "V1", minimal())["ldf_version"] = "3.0.0"
    case("v1-minor-newer", "V1", minimal())["ldf_version"] = "2.1.0"
    case("v1-ldf-1", "V1", minimal())["ldf_version"] = "1.0.0"

    case("s1-unknown-field", "S1", minimal())["extra"] = True
    case("s1-unknown-region-type", "S1", minimal())["structure"]["regions"][0]["type"] = "heading"
    case("s1-null-optional", "S1", minimal())["source_image"]["dpi"] = None
    del case("s1-missing-pipeline", "S1", minimal())["pipeline"]
    case("s1-text-not-string", "S1", minimal())["recognition"]["lines"][0]["text"] = 42
    case("s1-bad-timestamp", "S1", minimal())["created_at"] = "12/10/2026 20:00"
    case("s1-malformed-version", "S1", minimal())["ldf_version"] = "2.0"
    case("s1-bbox-three-values", "S1", minimal())["recognition"]["lines"][0]["bbox"] = [1, 2, 3]
    case("s1-rectified-frame", "S1", minimal())["coordinate_space"]["frame"] = "rectified"
    case("s1-confidence-above-one", "S1", minimal())["recognition"]["lines"][0]["confidence"] = 1.5
    del case("s1-component-without-license", "S1", minimal())["pipeline"]["stages"]["layout"][
        "component"
    ]["license_status"]

    case("r1-duplicate-line-id", "R1", layout_only())["recognition"]["lines"].append(
        {"id": "line_001", "bbox": [100, 1000, 700, 1050]}
    )
    doc = case("r1-region-reuses-line-id", "R1", layout_only())
    doc["structure"]["regions"][3]["id"] = "line_001"
    doc["structure"]["reading_order"][3] = "line_001"

    case("r2-missing-line", "R2", layout_only())["structure"]["regions"][0]["line_ids"] = [
        "line_099"
    ]
    case("r2-missing-region-in-order", "R2", layout_only())["structure"]["reading_order"].append(
        "region_099"
    )
    case("r2-diagram-on-text-region", "R2", full())["structure"]["diagrams"][0]["region_id"] = (
        "region_002"
    )
    case("r2-edge-without-node", "R2", full())["structure"]["diagrams"][0]["edges"][0]["target"] = (
        "node_099"
    )
    case("r2-section-missing-region", "R2", full())["semantics"]["sections"][0]["region_ids"] = [
        "region_099"
    ]

    case("r3-repeated-adjacent", "R3", layout_only())["structure"]["reading_order"].insert(
        1, "region_001"
    )
    case("r3-repeated-at-end", "R3", layout_only())["structure"]["reading_order"].append(
        "region_002"
    )

    case("r4-line-in-two-regions", "R4", layout_only())["structure"]["regions"][0][
        "line_ids"
    ].append("line_002")
    case("r4-line-twice-in-region", "R4", layout_only())["structure"]["regions"][1][
        "line_ids"
    ].append("line_002")

    case("r5-degenerate-box", "R5", layout_only())["recognition"]["lines"][0]["bbox"] = [
        100,
        100,
        100,
        150,
    ]
    case("r5-outside-image", "R5", layout_only())["structure"]["regions"][3]["bbox"] = [
        150,
        500,
        1300,
        900,
    ]
    case("r5-inverted-box", "R5", layout_only())["structure"]["regions"][0]["bbox"] = [
        710,
        160,
        90,
        90,
    ]

    doc = case("r6-counterclockwise", "R6", rectified())
    doc["recognition"]["lines"][0]["polygon"].reverse()
    case("r6-box-not-envelope", "R6", rectified())["recognition"]["lines"][0]["bbox"] = [
        200,
        300,
        700,
        380,
    ]
    case("r6-flat-polygon", "R6", rectified())["recognition"]["lines"][0]["polygon"] = [
        [200, 300],
        [500, 340],
        [800, 380],
    ]

    case("r7-text-without-recognition", "R7", layout_only())["recognition"]["lines"][0]["text"] = ""
    del case("r7-line-without-text", "R7", minimal())["recognition"]["lines"][0]["text"]
    del case("r7-line-without-confidence", "R7", full())["recognition"]["lines"][2]["confidence"]

    del case("r8-failed-without-error", "R8", layout_only())["pipeline"]["stages"]["layout"][
        "component"
    ]
    cases["r8-failed-without-error"][1]["pipeline"]["stages"]["layout"] = {"status": "failed"}
    cases["r8-failed-without-error"][1]["pipeline"]["stages"]["reading_order"] = {
        "status": "not_run"
    }
    cases["r8-failed-without-error"][1]["recognition"]["lines"] = []
    cases["r8-failed-without-error"][1]["structure"].update(regions=[], reading_order=[])

    case("r8-content-without-layout", "R8", layout_only())["pipeline"]["stages"]["layout"] = {
        "status": "not_run"
    }
    del case("r8-completed-without-component", "R8", layout_only())["pipeline"]["stages"][
        "reading_order"
    ]["component"]
    case("r8-error-on-completed", "R8", layout_only())["pipeline"]["stages"]["layout"]["error"] = (
        "não deveria estar aqui"
    )
    case("r8-semantics-without-stage", "R8", full())["pipeline"]["stages"]["semantics"] = {
        "status": "not_run"
    }
    case("r8-order-without-stage", "R8", layout_only())["pipeline"]["stages"]["reading_order"] = {
        "status": "not_run"
    }

    case("r9-missing-target", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines", "id": "line_099"},
            [{"op": "replace", "path": "/text", "value": "x"}],
        )
    ]
    case("r9-missing-field", "R9", layout_only())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines", "id": "line_001"},
            [{"op": "replace", "path": "/text", "value": "x"}],
        )
    ]
    case("r9-add-without-value", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines", "id": "line_001"},
            [{"op": "add", "path": "/text"}],
        )
    ]
    case("r9-dangling-reference", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "recognition.lines", "id": "line_004"},
            [{"op": "remove", "path": ""}],
        )
    ]
    case("r9-id-on-reading-order", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "structure.reading_order", "id": "region_001"},
            [{"op": "remove", "path": ""}],
        )
    ]
    case("r9-breaks-shape", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "structure.regions", "id": "region_001"},
            [{"op": "replace", "path": "/type", "value": "heading"}],
        )
    ]
    case("r9-target-removed-earlier", "R9", full())["human_corrections"] = [
        correction(
            "correction_001",
            {"collection": "semantics.entities", "id": "entity_001"},
            [{"op": "remove", "path": ""}],
        ),
        correction(
            "correction_002",
            {"collection": "semantics.entities", "id": "entity_001"},
            [{"op": "replace", "path": "/type", "value": "question"}],
        ),
    ]
    return cases


EXAMPLE_FILES = {
    "ldf-2.0-minimal.json": minimal,
    "ldf-2.0-layout-only.json": layout_only,
    "ldf-2.0-rectified.json": rectified,
    "ldf-2.0-with-corrections.json": with_corrections,
}


def files() -> dict[Path, Any]:
    """Todos os arquivos gerados, com o conteúdo esperado."""
    out: dict[Path, Any] = {}
    index: dict[str, Any] = {"valid": [], "invalid": {}}
    for name, doc in sorted(valid_cases().items()):
        out[CONFORMANCE / "valid" / f"{name}.json"] = doc
        index["valid"].append(f"{name}.json")
    for name, (code, doc) in sorted(invalid_cases().items()):
        out[CONFORMANCE / "invalid" / f"{name}.json"] = doc
        index["invalid"][f"{name}.json"] = code
    out[CONFORMANCE / "index.json"] = index
    for filename, factory in EXAMPLE_FILES.items():
        out[EXAMPLES / filename] = factory()
    return out


def render(content: Any) -> str:
    return json.dumps(content, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    for path, content in files().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(content), encoding="utf-8", newline="\n")
    print(f"{len(files())} arquivos gravados")


if __name__ == "__main__":
    main()
