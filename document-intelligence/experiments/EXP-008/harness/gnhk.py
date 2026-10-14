"""Verdade de chão de linhas do GNHK a partir das palavras anotadas.

Cada palavra do GNHK traz ``polygon`` (quatro cantos), ``line_idx``, ``type`` (``H`` manuscrito,
``P`` impresso) e ``text``. Uma linha é o conjunto de palavras com o mesmo ``line_idx``; seu
contorno
é o retângulo mínimo (possivelmente inclinado) que envolve os polígonos dessas palavras.

Linhas sem nenhuma palavra manuscrita legível (só impressas, ou só com marcas especiais como
``%NA%``, ``%SC%`` e ``%math%``) viram regiões "ignorar": detecções sobre elas não contam como
acerto
nem como erro.

O campo ``text`` só é consultado para reconhecer as marcas especiais. Nenhum texto é devolvido.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import cv2
import numpy as np

CORNERS = (("x0", "y0"), ("x1", "y1"), ("x2", "y2"), ("x3", "y3"))


def is_special(text: str) -> bool:
    """Marca especial do GNHK (``%NA%``, ``%SC%``, ``%math%``, ``%``): não é texto legível."""
    return len(text) >= 1 and text.startswith("%") and text.endswith("%")


def word_points(word: dict[str, Any], scale: float = 1.0) -> list[list[float]]:
    polygon = word["polygon"]
    return [[polygon[x] * scale, polygon[y] * scale] for x, y in CORNERS]


def _clockwise(points: np.ndarray) -> list[list[float]]:
    area = 0.0
    for index, (x0, y0) in enumerate(points):
        x1, y1 = points[(index + 1) % len(points)]
        area += x0 * y1 - x1 * y0
    ordered = points if area >= 0 else points[::-1]
    return [[round(float(x), 1), round(float(y), 1)] for x, y in ordered]


def lines_from_words(
    words: list[dict[str, Any]], scale: float = 1.0
) -> tuple[list[dict[str, Any]], list[list[int]]]:
    """Devolve ``(linhas, regiões a ignorar)`` de uma foto.

    Cada linha: ``{"id", "bbox", "polygon", "words"}``, com a geometria multiplicada por ``scale``.
    """
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for word in words:
        groups[int(word["line_idx"])].append(word)

    lines: list[dict[str, Any]] = []
    ignore: list[list[int]] = []
    for line_idx in sorted(groups):
        group = groups[line_idx]
        points = np.array([p for word in group for p in word_points(word, scale)], dtype=np.float32)
        x0, y0 = np.floor(points.min(axis=0))
        x1, y1 = np.ceil(points.max(axis=0))
        bbox = [int(x0), int(y0), int(x1), int(y1)]
        if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
            continue
        readable = [w for w in group if w.get("type") == "H" and not is_special(w.get("text", ""))]
        if not readable:
            ignore.append(bbox)
            continue
        box = cv2.boxPoints(cv2.minAreaRect(points))
        lines.append(
            {
                "id": f"l{line_idx:03d}",
                "bbox": bbox,
                "polygon": _clockwise(box),
                "words": len(group),
            }
        )
    return lines, ignore
