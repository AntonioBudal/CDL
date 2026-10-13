"""Verdade de chão de linhas, parágrafos e ordem do BRESSAY pela localização dos recortes.

O BRESSAY distribui a imagem de cada página e, à parte, os recortes de cada parágrafo e de cada
linha, sem coordenadas. Os recortes são subimagens exatas da página; aqui cada um é localizado por
correlação normalizada. Nomes: ``<página>-<parágrafo>.png`` e ``<página>-<parágrafo>-<linha>.png``.

A ordem de leitura é a numeração dos parágrafos; dentro do parágrafo, a numeração das linhas.
Nenhuma
transcrição é lida.
"""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

MIN_SCORE = 0.99
MARGIN = 4


def locate(page: np.ndarray, crop: np.ndarray, window: list[int] | None = None):
    """Posição ``(x, y, escore)`` do recorte na página, ou ``None`` se não couber ou não casar.

    ``window`` = ``[x0, y0, x1, y1]`` restringe a busca (por exemplo, ao parágrafo da linha).
    """
    x_off = y_off = 0
    area = page
    if window is not None:
        x0, y0 = max(0, window[0] - MARGIN), max(0, window[1] - MARGIN)
        x1, y1 = min(page.shape[1], window[2] + MARGIN), min(page.shape[0], window[3] + MARGIN)
        area, x_off, y_off = page[y0:y1, x0:x1], x0, y0
    if crop.shape[0] > area.shape[0] or crop.shape[1] > area.shape[1]:
        return None
    if float(crop.std()) < 1e-6:
        return None  # recorte uniforme: a correlação normalizada não é definida
    result = cv2.matchTemplate(area, crop, cv2.TM_CCOEFF_NORMED)
    _, score, _, where = cv2.minMaxLoc(result)
    if not np.isfinite(score) or score < MIN_SCORE:
        return None
    return where[0] + x_off, where[1] + y_off, float(score)


def _box(x: int, y: int, crop: np.ndarray) -> list[int]:
    return [x, y, x + crop.shape[1], y + crop.shape[0]]


def _rectangle(box: list[int]) -> list[list[int]]:
    x0, y0, x1, y1 = box
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def page_truth(
    page: np.ndarray,
    paragraphs: dict[str, np.ndarray],
    lines: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Linhas, blocos e ordem de uma página a partir dos recortes.

    ``paragraphs`` e ``lines`` mapeiam o nome do recorte (sem extensão) para a imagem em tons de
    cinza. Devolve também ``missing``: os recortes que não foram localizados.
    """
    blocks: list[dict[str, Any]] = []
    out_lines: list[dict[str, Any]] = []
    missing: list[str] = []
    for name in sorted(paragraphs):
        found = locate(page, paragraphs[name])
        if found is None:
            missing.append(name)
            continue
        box = _box(found[0], found[1], paragraphs[name])
        block_id = f"b{len(blocks) + 1:03d}"
        line_ids = []
        for line_name in sorted(n for n in lines if n.startswith(name + "-")):
            crop = lines[line_name]
            hit = locate(page, crop, box) or locate(page, crop)
            if hit is None:
                missing.append(line_name)
                continue
            line_box = _box(hit[0], hit[1], crop)
            line_id = f"l{len(out_lines) + 1:03d}"
            out_lines.append(
                {
                    "id": line_id,
                    "block_id": block_id,
                    "bbox": line_box,
                    "polygon": _rectangle(line_box),
                }
            )
            line_ids.append(line_id)
        blocks.append(
            {"id": block_id, "type": "paragraph", "bbox": box, "line_ids": line_ids, "anchor": None}
        )
    orphans = [n for n in lines if not any(n.startswith(p + "-") for p in paragraphs)]
    missing.extend(sorted(orphans))
    return {
        "lines": out_lines,
        "blocks": blocks,
        "reading_order": [block["id"] for block in blocks],
        "missing": missing,
    }


def scale_truth(truth: dict[str, Any], factor: int) -> dict[str, Any]:
    """A mesma verdade de chão para a página ampliada ``factor`` vezes."""

    def box(values):
        return [v * factor for v in values]

    return {
        "lines": [
            {
                **line,
                "bbox": box(line["bbox"]),
                "polygon": [[x * factor, y * factor] for x, y in line["polygon"]],
            }
            for line in truth["lines"]
        ],
        "blocks": [{**block, "bbox": box(block["bbox"])} for block in truth["blocks"]],
        "reading_order": list(truth["reading_order"]),
        "missing": list(truth["missing"]),
    }
