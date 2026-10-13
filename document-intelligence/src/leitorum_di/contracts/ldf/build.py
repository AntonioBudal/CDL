"""Conversor de referência: saída de layout e ordem de leitura → documento LDF 2.0 validado.

Recebe estruturas simples (dicionários com ``bbox``, ``polygon`` e ``score``), como as produzidas
pelos detectores dos experimentos, e devolve um documento que já passou por ``validate``. Não lê
imagens nem carrega modelos.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from leitorum_di.contracts.ldf.geometry import (
    apply_homography,
    bbox_polygon,
    clip_polygon,
    clockwise,
    envelope,
    homography_from_quads,
    invert,
    signed_area,
)
from leitorum_di.contracts.ldf.rules import STAGES
from leitorum_di.contracts.ldf.validate import ensure_valid

LDF_VERSION = "2.0.0"
NAMESPACE = uuid.UUID("3d0c8e0a-6a55-4b1c-9c0e-5b2f4d7a1e20")
REGION_TYPES = {
    "title": "title",
    "paragraph": "paragraph",
    "margin_note": "margin_note",
    "graphic": "graphic",
    "graphic_box": "graphic",
}


def _num(value: float) -> float | int:
    rounded = round(float(value), 2)
    return int(rounded) if rounded.is_integer() else rounded


def _unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def component(
    name: str,
    version: str,
    *,
    license: str = "N/A",  # noqa: A002 - nome do campo no contrato
    license_status: str = "N/A",
    revision: str | None = None,
) -> dict[str, str]:
    """Descrição de um componente do pipeline para ``pipeline.stages``."""
    item = {"name": name, "version": version, "license": license, "license_status": license_status}
    if revision:
        item["revision"] = revision
    return item


def rectification_from_corners(
    corners: Sequence[Sequence[float]], output_size: Sequence[int], method: str
) -> dict[str, Any]:
    """Metadado de retificação a partir dos cantos da folha na fotografia.

    ``corners`` na ordem superior esquerdo, superior direito, inferior direito, inferior esquerdo.
    """
    width, height = int(output_size[0]), int(output_size[1])
    target = [[0, 0], [width, 0], [width, height], [0, height]]
    return {
        "method": method,
        "source_quad": [[_num(x), _num(y)] for x, y in corners],
        "output_size": [width, height],
        "homography": homography_from_quads(corners, target),
    }


def _stage(spec: Mapping[str, Any] | None) -> dict[str, Any]:
    if spec is None:
        return {"status": "not_run"}
    stage: dict[str, Any] = {"status": "failed" if "error" in spec else "completed"}
    for key in ("component", "error"):
        if key in spec:
            stage[key] = spec[key]
    if spec.get("elapsed_ms") is not None:
        stage["elapsed_ms"] = round(max(0.0, float(spec["elapsed_ms"])), 3)
    return stage


def _shape(item: Mapping[str, Any], width: int, height: int, back) -> dict[str, Any]:
    """Geometria final de um elemento: na fotografia original, recortada à imagem."""
    polygon = item.get("polygon")
    if back is not None:
        polygon = [apply_homography(back, p) for p in (polygon or bbox_polygon(item["bbox"]))]
    if not polygon:
        x0, y0, x1, y1 = item["bbox"]
        return {
            "bbox": [
                _num(max(0, x0)),
                _num(max(0, y0)),
                _num(min(width, x1)),
                _num(min(height, y1)),
            ]
        }
    clipped = clip_polygon(clockwise(polygon), width, height)
    points = [[_num(x), _num(y)] for x, y in clipped]
    if len(points) < 3 or signed_area(points) <= 0:
        raise ValueError("elemento fora da imagem ou com área nula")
    return {"bbox": [_num(v) for v in envelope(points)], "polygon": points}


def _membership(lines: list[dict[str, Any]], regions: list[dict[str, Any]]) -> list[list[str]]:
    """Atribui cada linha à menor região que contém o seu centro."""
    owned: list[list[str]] = [[] for _ in regions]

    def area(index: int) -> float:
        x0, y0, x1, y1 = regions[index]["bbox"]
        return (x1 - x0) * (y1 - y0)

    for line in lines:
        x0, y0, x1, y1 = line["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        inside = [
            index
            for index, region in enumerate(regions)
            if region["bbox"][0] <= cx <= region["bbox"][2]
            and region["bbox"][1] <= cy <= region["bbox"][3]
        ]
        if inside:
            owned[min(inside, key=area)].append(line["id"])
    return owned


def build_document(
    *,
    image: Mapping[str, Any],
    lines: Sequence[Mapping[str, Any]],
    regions: Sequence[Mapping[str, Any]],
    reading_order: Sequence[int] | None = None,
    stages: Mapping[str, Mapping[str, Any]] | None = None,
    rectification: Mapping[str, Any] | None = None,
    input_frame: str = "source_image",
    document_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Monta e valida um documento LDF 2.0.

    * ``image``: ``filename``, ``width``, ``height``, ``sha256`` e, opcionalmente, ``dpi``.
    * ``lines``: ``bbox`` e, opcionalmente, ``polygon``, ``score``, ``text``, ``confidence``,
      ``is_handwritten``.
    * ``regions``: ``type``, ``bbox`` e, opcionalmente, ``polygon``, ``score`` e ``lines``
      (índices em ``lines``). Se nenhuma região trouxer ``lines``, a associação é feita pelo
      centro de cada linha.
    * ``reading_order``: índices em ``regions``, na ordem de leitura.
    * ``stages``: por etapa, ``component`` (concluída) ou ``error`` (falhou), mais ``elapsed_ms``;
      etapa ausente fica como não executada.
    * ``input_frame``: ``"source_image"`` ou ``"rectified"``. No segundo caso a geometria é levada
      de volta à fotografia original por ``rectification``.

    Levanta ``LDFValidationError`` se o resultado violar o contrato.
    """
    stages = stages or {}
    unknown = set(stages) - set(STAGES)
    if unknown:
        raise ValueError(f"etapas desconhecidas: {sorted(unknown)}")
    if input_frame not in ("source_image", "rectified"):
        raise ValueError(f"input_frame inválido: {input_frame}")
    if input_frame == "rectified" and rectification is None:
        raise ValueError("geometria retificada exige o metadado rectification")
    width, height = int(image["width"]), int(image["height"])
    back = invert(rectification["homography"]) if input_frame == "rectified" else None

    out_lines: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        item: dict[str, Any] = {"id": f"line_{index:03d}", **_shape(line, width, height, back)}
        if line.get("score") is not None:
            item["detection_confidence"] = _unit(line["score"])
        if "text" in line:
            item["text"] = line["text"]
            item["confidence"] = _unit(line.get("confidence", 0.0))
        if "is_handwritten" in line:
            item["is_handwritten"] = bool(line["is_handwritten"])
        out_lines.append(item)

    out_regions: list[dict[str, Any]] = []
    for index, region in enumerate(regions, start=1):
        if region["type"] not in REGION_TYPES:
            raise ValueError(f"tipo de região sem correspondência no LDF: {region['type']}")
        item = {
            "id": f"region_{index:03d}",
            "type": REGION_TYPES[region["type"]],
            **_shape(region, width, height, back),
            "line_ids": [],
        }
        if region.get("score") is not None:
            item["confidence"] = _unit(region["score"])
        out_regions.append(item)

    if any("lines" in region for region in regions):
        owned = [[out_lines[i]["id"] for i in region.get("lines", [])] for region in regions]
    else:
        owned = _membership(out_lines, out_regions)
    for item, line_ids in zip(out_regions, owned, strict=True):
        item["line_ids"] = line_ids

    space: dict[str, Any] = {"frame": "source_image", "unit": "pixel"}
    if rectification is not None:
        space["rectification"] = dict(rectification)
    source = {
        key: image[key] for key in ("filename", "width", "height", "dpi", "sha256") if key in image
    }
    document = {
        "ldf_version": LDF_VERSION,
        "document_id": document_id or str(uuid.uuid5(NAMESPACE, image["sha256"])),
        "created_at": created_at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_image": source,
        "coordinate_space": space,
        "pipeline": {"stages": {name: _stage(stages.get(name)) for name in STAGES}},
        "recognition": {"lines": out_lines},
        "structure": {
            "regions": out_regions,
            "reading_order": [out_regions[i]["id"] for i in (reading_order or [])],
            "diagrams": [],
        },
        "human_corrections": [],
    }
    ensure_valid(document)
    return document
