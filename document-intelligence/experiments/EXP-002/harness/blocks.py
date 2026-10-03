"""Montagem de blocos por regras geométricas sobre as linhas detectadas (mesmas regras para todos).

* ``margin_note``: linhas que terminam à esquerda da borda principal do texto (ou são verticais).
* ``title``: a primeira linha do texto principal, se for mais alta que a mediana ou isolada abaixo.
* ``paragraph``: linhas restantes agrupadas por espaçamento vertical.
* ``graphic_box``: tinta grande que não pertence a nenhuma linha (caixas, setas, rótulos).

Os limiares são calibrados **só** no conjunto ``dev`` (``calibrate_classic.py``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class BlockParams:
    margin_gap: float = 0.5  # nota: termina ao menos isso × altura mediana antes da borda principal
    title_height: float = 1.08  # título: altura ≥ isso × mediana
    title_gap: float = 1.6  # ou separação abaixo ≥ isso × espaçamento típico
    paragraph_gap: float = (
        1.55  # nova parágrafo quando o salto vertical ≥ isso × espaçamento típico
    )
    graphic_min_area: float = (
        6.0  # área mínima (em alturas medianas ao quadrado) da tinta não-linha
    )
    graphic_join: float = 1.5  # dilatação para unir partes do diagrama, em alturas medianas

    def to_dict(self) -> dict:
        return asdict(self)


def _union(boxes) -> list[int]:
    return [
        int(min(b[0] for b in boxes)),
        int(min(b[1] for b in boxes)),
        int(max(b[2] for b in boxes)),
        int(max(b[3] for b in boxes)),
    ]


def _height(line) -> float:
    """Altura "própria" da linha: lado menor do retângulo rotacionado (ou da bbox)."""
    polygon = line.get("polygon")
    if polygon and len(polygon) >= 4:
        (_, _), (w, h), _ = cv2.minAreaRect(np.asarray(polygon, np.float32))
        return float(min(w, h))
    x0, y0, x1, y1 = line["bbox"]
    return float(min(x1 - x0, y1 - y0))


def _is_vertical(line) -> bool:
    x0, y0, x1, y1 = line["bbox"]
    return (y1 - y0) > 2.5 * (x1 - x0)


def assemble_blocks(lines: list[dict], ink: np.ndarray | None, params: BlockParams) -> list[dict]:
    """Agrupa linhas em blocos; ``ink`` (máscara 255 = tinta, mesma escala da imagem) é opcional."""
    if not lines:
        return []
    heights = np.array([_height(line) for line in lines])
    median_h = float(np.median(heights))
    horizontal = [i for i, line in enumerate(lines) if not _is_vertical(line)]
    lefts = np.array([lines[i]["bbox"][0] for i in horizontal]) if horizontal else np.array([0])
    widths = (
        np.array([lines[i]["bbox"][2] - lines[i]["bbox"][0] for i in horizontal])
        if horizontal
        else np.array([1])
    )
    wide = lefts[widths >= np.percentile(widths, 50)] if len(widths) else lefts
    main_left = float(np.percentile(wide, 20)) if len(wide) else 0.0

    margin, main = [], []
    for i, line in enumerate(lines):
        if _is_vertical(line) or line["bbox"][2] < main_left - params.margin_gap * median_h:
            margin.append(i)
        else:
            main.append(i)

    blocks: list[dict] = []
    main.sort(key=lambda i: (lines[i]["bbox"][1] + lines[i]["bbox"][3]) / 2)
    centers = [(lines[i]["bbox"][1] + lines[i]["bbox"][3]) / 2 for i in main]
    steps = np.diff(centers) if len(centers) > 1 else np.array([median_h * 1.2])
    spacing = float(np.median(steps)) if len(steps) else median_h * 1.2
    start = 0
    if main:
        first = main[0]
        below = steps[0] if len(steps) else 0.0
        if heights[first] >= params.title_height * median_h or below >= params.title_gap * spacing:
            blocks.append(
                {
                    "type": "title",
                    "bbox": _union([lines[first]["bbox"]]),
                    "score": 1.0,
                    "members": [first],
                }
            )
            start = 1
    group: list[int] = []
    for k in range(start, len(main)):
        if group and centers[k] - centers[k - 1] >= params.paragraph_gap * spacing:
            blocks.append(
                {
                    "type": "paragraph",
                    "bbox": _union([lines[i]["bbox"] for i in group]),
                    "score": 1.0,
                    "members": group,
                }
            )
            group = []
        group.append(main[k])
    if group:
        blocks.append(
            {
                "type": "paragraph",
                "bbox": _union([lines[i]["bbox"] for i in group]),
                "score": 1.0,
                "members": group,
            }
        )

    margin.sort(key=lambda i: lines[i]["bbox"][1])
    note: list[int] = []
    for i in margin:
        if note and lines[i]["bbox"][1] - lines[note[-1]]["bbox"][3] > 1.2 * median_h:
            blocks.append(
                {
                    "type": "margin_note",
                    "bbox": _union([lines[j]["bbox"] for j in note]),
                    "score": 1.0,
                    "members": note,
                }
            )
            note = []
        note.append(i)
    if note:
        blocks.append(
            {
                "type": "margin_note",
                "bbox": _union([lines[j]["bbox"] for j in note]),
                "score": 1.0,
                "members": note,
            }
        )

    if ink is not None:
        blocks.extend(_graphic_boxes(lines, ink, median_h, params))
    for block in blocks:
        block.pop("members", None)
    return blocks


def _graphic_boxes(lines, ink: np.ndarray, median_h: float, params: BlockParams) -> list[dict]:
    remaining = ink.copy()
    pad = max(2, round(0.25 * median_h))
    for line in lines:
        x0, y0, x1, y1 = line["bbox"]
        remaining[max(0, y0 - pad) : y1 + pad, max(0, x0 - pad) : x1 + pad] = 0
    size = max(3, round(params.graphic_join * median_h))
    joined = cv2.dilate(remaining, np.ones((size, size), np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    boxes = []
    for label in range(1, count):
        x, y, w, h, _ = stats[label]
        ink_pixels = int(np.count_nonzero(remaining[y : y + h, x : x + w]))
        if (
            w * h >= params.graphic_min_area * median_h**2
            and h >= 1.5 * median_h
            and ink_pixels > 50
        ):
            shrink = size // 2
            boxes.append(
                {
                    "type": "graphic_box",
                    "bbox": [
                        int(x + shrink),
                        int(y + shrink),
                        int(x + w - shrink),
                        int(y + h - shrink),
                    ],
                    "score": 1.0,
                }
            )
    return boxes


def assemble_for_image(
    image_path: str, lines: list[dict], params: BlockParams, classic_params
) -> list[dict]:
    """Monta blocos para uma página a partir das linhas preditas e da tinta da própria imagem."""
    from classic import ink_mask

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = image.shape[:2]
    scale = min(1.0, classic_params.max_side / max(h, w))
    if scale < 1.0:
        image = cv2.resize(
            image, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA
        )
    mask = ink_mask(image, classic_params)

    def scaled(points, factor):
        return [[round(x * factor), round(y * factor)] for x, y in points]

    local = [
        {
            "bbox": [round(v * scale) for v in line["bbox"]],
            "polygon": scaled(line["polygon"], scale) if line.get("polygon") else None,
        }
        for line in lines
    ]
    blocks = assemble_blocks(local, mask, params)
    for block in blocks:
        block["bbox"] = [round(v / scale) for v in block["bbox"]]
    return blocks
