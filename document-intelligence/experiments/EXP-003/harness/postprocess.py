"""Ponto de operação dos blocos detectados: limiar de confiança e supressão de duplicatas.

O detector de layout devolve muitas caixas de baixa confiança e sobrepostas (úteis para calcular AP,
como no EXP-002, mas não para montar um documento). Antes de ordenar, ficam só as caixas com
confiança ≥ ``min_score`` e, entre caixas muito sobrepostas, a de maior confiança (NMS sem olhar o
tipo). Também é descartada a caixa quase toda contida em outra de maior confiança.

Os parâmetros são calibrados **só** no conjunto ``dev`` (``calibrate_blocks.py``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from leitorum_di.metrics.base import calculate_iou


@dataclass(frozen=True)
class BlockFilter:
    min_score: float = 0.5
    nms_iou: float = 0.5
    containment: float = 0.8  # fração da área de uma caixa dentro de outra para ser descartada

    def to_dict(self) -> dict:
        return asdict(self)


def _contained(inner, outer) -> float:
    ix = max(0, min(inner[2], outer[2]) - max(inner[0], outer[0]))
    iy = max(0, min(inner[3], outer[3]) - max(inner[1], outer[1]))
    area = max(1, (inner[2] - inner[0]) * (inner[3] - inner[1]))
    return ix * iy / area


def filter_blocks(blocks: list[dict], params: BlockFilter) -> list[dict]:
    """Aplica limiar, NMS e supressão por contenção; devolve os blocos mantidos."""
    ranked = sorted(
        (b for b in blocks if float(b.get("score", 1.0)) >= params.min_score),
        key=lambda b: -float(b.get("score", 1.0)),
    )
    kept: list[dict] = []
    for block in ranked:
        box = block["bbox"]
        duplicate = any(
            calculate_iou(box, other["bbox"]) >= params.nms_iou
            or _contained(box, other["bbox"]) >= params.containment
            for other in kept
        )
        if not duplicate:
            kept.append(block)
    return kept
