"""Regras do LDF 2.0 que o JSON Schema não expressa (R1–R8). Pressupõem forma válida.

R9 (correções humanas) fica em ``validate.py``, porque depende de aplicar as correções e
revalidar o resultado.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from leitorum_di.contracts.ldf.geometry import envelope, signed_area
from leitorum_di.contracts.ldf.issues import Issue

TOLERANCE = 1.0
STAGES = ("layout", "reading_order", "recognition", "semantics", "diagrams")


def _identified(document: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    """Percorre todos os elementos que têm ``id``, com o caminho de cada um."""
    for i, line in enumerate(document["recognition"]["lines"]):
        yield f"/recognition/lines/{i}", line
    structure = document["structure"]
    for i, region in enumerate(structure["regions"]):
        yield f"/structure/regions/{i}", region
    for i, diagram in enumerate(structure["diagrams"]):
        yield f"/structure/diagrams/{i}", diagram
        for kind in ("nodes", "edges"):
            for j, item in enumerate(diagram[kind]):
                yield f"/structure/diagrams/{i}/{kind}/{j}", item
    semantics = document.get("semantics") or {}
    for kind in ("sections", "entities"):
        for i, item in enumerate(semantics.get(kind, [])):
            yield f"/semantics/{kind}/{i}", item
    for i, correction in enumerate(document["human_corrections"]):
        yield f"/human_corrections/{i}", correction


def _unique_ids(document: dict[str, Any]) -> list[Issue]:
    seen: dict[str, str] = {}
    issues = []
    for path, item in _identified(document):
        ident = item["id"]
        if ident in seen:
            issues.append(
                Issue("R1", f"{path}/id", f"identificador repetido: {ident} ({seen[ident]})")
            )
        else:
            seen[ident] = path
    return issues


def _references(document: dict[str, Any]) -> list[Issue]:
    issues = []
    line_ids = {line["id"] for line in document["recognition"]["lines"]}
    structure = document["structure"]
    regions = {region["id"]: region for region in structure["regions"]}

    def missing(path: str, ids, known, what: str) -> None:
        for k, ref in enumerate(ids):
            if ref not in known:
                issues.append(Issue("R2", f"{path}/{k}", f"{what} inexistente: {ref}"))

    for i, region in enumerate(structure["regions"]):
        missing(f"/structure/regions/{i}/line_ids", region["line_ids"], line_ids, "linha")
    missing("/structure/reading_order", structure["reading_order"], regions, "região")
    for i, diagram in enumerate(structure["diagrams"]):
        base = f"/structure/diagrams/{i}"
        region = regions.get(diagram["region_id"])
        if region is None:
            issues.append(
                Issue("R2", f"{base}/region_id", f"região inexistente: {diagram['region_id']}")
            )
        elif region["type"] != "graphic":
            issues.append(
                Issue("R2", f"{base}/region_id", "o diagrama deve apontar para região graphic")
            )
        node_ids = {node["id"] for node in diagram["nodes"]}
        for j, node in enumerate(diagram["nodes"]):
            missing(f"{base}/nodes/{j}/line_ids", node.get("line_ids", []), line_ids, "linha")
        for j, edge in enumerate(diagram["edges"]):
            for end in ("source", "target"):
                if edge[end] not in node_ids:
                    issues.append(
                        Issue("R2", f"{base}/edges/{j}/{end}", f"nó inexistente: {edge[end]}")
                    )
    semantics = document.get("semantics") or {}
    for kind in ("sections", "entities"):
        for i, item in enumerate(semantics.get(kind, [])):
            missing(f"/semantics/{kind}/{i}/region_ids", item["region_ids"], regions, "região")
    return issues


def _reading_order(document: dict[str, Any]) -> list[Issue]:
    seen: set[str] = set()
    issues = []
    for k, ref in enumerate(document["structure"]["reading_order"]):
        if ref in seen:
            issues.append(Issue("R3", f"/structure/reading_order/{k}", f"região repetida: {ref}"))
        seen.add(ref)
    return issues


def _line_ownership(document: dict[str, Any]) -> list[Issue]:
    owner: dict[str, str] = {}
    issues = []
    for i, region in enumerate(document["structure"]["regions"]):
        for k, ref in enumerate(region["line_ids"]):
            if ref in owner:
                issues.append(
                    Issue(
                        "R4",
                        f"/structure/regions/{i}/line_ids/{k}",
                        f"linha {ref} já pertence à região {owner[ref]}",
                    )
                )
            else:
                owner[ref] = region["id"]
    return issues


def _geometry(document: dict[str, Any]) -> list[Issue]:
    width = document["source_image"]["width"]
    height = document["source_image"]["height"]
    issues = []
    for path, item in _identified(document):
        if "bbox" not in item or path.startswith("/human_corrections"):
            continue
        x0, y0, x1, y1 = item["bbox"]
        if x1 <= x0 or y1 <= y0:
            issues.append(Issue("R5", f"{path}/bbox", "caixa com largura ou altura não positiva"))
        elif (
            x0 < -TOLERANCE or y0 < -TOLERANCE or x1 > width + TOLERANCE or y1 > height + TOLERANCE
        ):
            issues.append(Issue("R5", f"{path}/bbox", "caixa fora dos limites da imagem"))
        polygon = item.get("polygon")
        if polygon is None:
            continue
        if signed_area(polygon) <= 0:
            issues.append(
                Issue("R6", f"{path}/polygon", "vértices fora do sentido horário ou área nula")
            )
        elif any(
            abs(a - b) > TOLERANCE for a, b in zip(envelope(polygon), item["bbox"], strict=True)
        ):
            issues.append(Issue("R6", f"{path}/bbox", "a caixa não é o envelope do polígono"))
    return issues


def _recognition_stage(document: dict[str, Any]) -> list[Issue]:
    completed = document["pipeline"]["stages"]["recognition"]["status"] == "completed"
    issues = []
    for i, line in enumerate(document["recognition"]["lines"]):
        path = f"/recognition/lines/{i}"
        has = [key for key in ("text", "confidence") if key in line]
        if completed and len(has) < 2:
            issues.append(
                Issue("R7", path, "reconhecimento concluído: a linha precisa de text e confidence")
            )
        elif not completed and has:
            issues.append(
                Issue("R7", f"{path}/{has[0]}", "reconhecimento não concluído: linha com resultado")
            )
    return issues


def _stage_coherence(document: dict[str, Any]) -> list[Issue]:
    stages = document["pipeline"]["stages"]
    structure = document["structure"]
    semantics = document.get("semantics") or {}
    content = {
        "layout": [
            ("/recognition/lines", document["recognition"]["lines"]),
            ("/structure/regions", structure["regions"]),
        ],
        "reading_order": [("/structure/reading_order", structure["reading_order"])],
        "diagrams": [("/structure/diagrams", structure["diagrams"])],
        "semantics": [
            ("/semantics/sections", semantics.get("sections", [])),
            ("/semantics/entities", semantics.get("entities", [])),
        ],
    }
    issues = []
    for name in STAGES:
        stage = stages[name]
        path = f"/pipeline/stages/{name}"
        status = stage["status"]
        if status == "failed" and "error" not in stage:
            issues.append(Issue("R8", path, "etapa que falhou precisa do campo error"))
        if status != "failed" and "error" in stage:
            issues.append(Issue("R8", f"{path}/error", "campo error só cabe em etapa que falhou"))
        if status == "completed" and "component" not in stage:
            issues.append(Issue("R8", path, "etapa concluída precisa do campo component"))
        if status != "completed":
            for where, items in content.get(name, []):
                if items:
                    issues.append(
                        Issue("R8", where, f"etapa {name} não concluída, mas há conteúdo")
                    )
    return issues


ALWAYS = (_unique_ids, _references, _reading_order, _line_ownership, _geometry)
ORIGINAL_ONLY = (_recognition_stage, _stage_coherence)


def check_rules(document: dict[str, Any], *, stage_rules: bool = True) -> list[Issue]:
    """Aplica R1–R6 e, com ``stage_rules``, também R7–R8 (que valem só para a saída original)."""
    checks = ALWAYS + (ORIGINAL_ONLY if stage_rules else ())
    return [issue for check in checks for issue in check(document)]
