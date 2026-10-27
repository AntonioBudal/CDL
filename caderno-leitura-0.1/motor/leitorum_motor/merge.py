"""Fusão de fragmentos de linha: une detecções vizinhas que pertencem à mesma linha de texto.

Promovido sem mudança de lógica de ``document-intelligence/experiments/EXP-019/harness/merge.py``
(commit ``3b695c5``); parâmetros calibrados no EXP-008.

Dois fragmentos são vizinhos quando:

* suas faixas verticais se sobrepõem em pelo menos ``v_overlap`` da altura do menor;
* a distância horizontal entre eles é de no máximo ``max_gap`` alturas medianas de linha da página;
* a diferença de inclinação é de no máximo ``max_angle`` graus.

A fusão é transitiva (componentes conexos). Os parâmetros são escolhidos só nos conjuntos de
calibração do EXP-008.
"""

from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class MergeParams:
    v_overlap: float = 0.5
    max_gap: float = 1.5
    max_angle: float = 10.0

    def to_dict(self) -> dict:
        return asdict(self)


def _points(line: dict[str, Any]) -> np.ndarray:
    polygon = line.get("polygon")
    if polygon and len(polygon) >= 3:
        return np.asarray(polygon, dtype=np.float32).reshape(-1, 2)
    x0, y0, x1, y1 = line["bbox"]
    return np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])


def angle(line: dict[str, Any]) -> float:
    """Inclinação (graus) do lado maior do fragmento, em (−90, 90]."""
    (_, _), (w, h), value = cv2.minAreaRect(_points(line))
    if w < h:
        value += 90.0
    while value > 90:
        value -= 180
    while value <= -90:
        value += 180
    return float(value)


def _neighbours(a, b, angle_a, angle_b, height: float, params: MergeParams) -> bool:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    smaller = min(ay1 - ay0, by1 - by0)
    if smaller <= 0:
        return False
    if (min(ay1, by1) - max(ay0, by0)) / smaller < params.v_overlap:
        return False
    if max(ax0, bx0) - min(ax1, bx1) > params.max_gap * height:
        return False
    difference = abs(angle_a - angle_b)
    return min(difference, 180 - difference) <= params.max_angle


def merge_lines(lines: list[dict[str, Any]], params: MergeParams) -> list[dict[str, Any]]:
    """Devolve as linhas com os fragmentos vizinhos unidos (caixa, contorno e confiança média)."""
    if len(lines) < 2:
        return [dict(line) for line in lines]
    boxes = [line["bbox"] for line in lines]
    angles = [angle(line) for line in lines]
    height = statistics.median(max(1, box[3] - box[1]) for box in boxes)
    parent = list(range(len(lines)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if _neighbours(boxes[i], boxes[j], angles[i], angles[j], height, params):
                parent[find(i)] = find(j)

    groups: dict[int, list[int]] = {}
    for index in range(len(lines)):
        groups.setdefault(find(index), []).append(index)

    merged = []
    for members in groups.values():
        if len(members) == 1:
            merged.append(dict(lines[members[0]]))
            continue
        points = np.vstack([_points(lines[i]) for i in members])
        x0, y0 = np.floor(points.min(axis=0))
        x1, y1 = np.ceil(points.max(axis=0))
        outline = cv2.boxPoints(cv2.minAreaRect(points))
        merged.append(
            {
                "bbox": [int(x0), int(y0), int(x1), int(y1)],
                "polygon": [[round(float(x), 1), round(float(y), 1)] for x, y in outline],
                "score": float(np.mean([lines[i].get("score", 1.0) for i in members])),
                "fragments": len(members),
            }
        )
    merged.sort(key=lambda line: (line["bbox"][1], line["bbox"][0]))
    return merged
