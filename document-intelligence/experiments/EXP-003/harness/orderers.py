"""Ordenadores de leitura algorítmicos (sem modelos) para blocos e linhas de uma página.

Entrada: blocos ``{"type", "bbox"}`` e linhas ``{"bbox", "polygon", "block"?}``. Saída: índices dos
blocos na ordem de leitura. Parâmetros calibrados **só** no conjunto ``dev`` (``calibrate.py``).

* ``naive``: de cima para baixo e, em empate, da esquerda para a direita.
* ``xycut``: corte XY recursivo (faixas horizontais vazias, depois verticais).
* ``anchored``: separa o fluxo principal das regiões laterais (margem, destaque) e insere cada
  região lateral logo depois do bloco principal ao lado do qual está.

``deskew=True`` gira as caixas pelo ângulo mediano das linhas antes de ordenar.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class OrderParams:
    method: str = "anchored"  # naive | xycut | anchored
    deskew: bool = True
    tie: float = 0.5  # naive: tolerância de empate vertical, em alturas medianas de bloco
    min_gap: float = 0.15  # xycut: faixa vazia mínima, em alturas medianas de linha
    shrink: float = 0.1  # xycut: encolhimento das caixas antes de projetar
    lateral_offset: float = 0.08  # anchored: desvio da borda principal, em larguras do texto
    side_overlap: float = 0.3  # anchored: sobreposição vertical mínima com o vizinho lateral

    def to_dict(self) -> dict:
        return asdict(self)


def line_angle(line: dict) -> float:
    """Ângulo (graus) do lado maior do polígono da linha, em (−90, 90]."""
    polygon = line.get("polygon")
    if not polygon or len(polygon) < 3:
        return 0.0
    pts = np.asarray(polygon, dtype=np.float32)
    (_, _), (w, h), angle = cv2.minAreaRect(pts)
    if w < h:
        angle += 90.0
    while angle > 90:
        angle -= 180
    while angle <= -90:
        angle += 180
    return float(angle)


def page_skew(lines: list[dict]) -> float:
    """Inclinação da página: ângulo mediano das linhas quase horizontais (0 se não houver)."""
    angles = [a for a in (line_angle(line) for line in lines) if abs(a) < 30]
    return float(np.median(angles)) if angles else 0.0


def _rotated_boxes(boxes: list[list[float]], angle: float) -> list[list[float]]:
    if abs(angle) < 0.2 or not boxes:
        return [list(map(float, b)) for b in boxes]
    arr = np.asarray(boxes, dtype=np.float64)
    cx, cy = (arr[:, 0].min() + arr[:, 2].max()) / 2, (arr[:, 1].min() + arr[:, 3].max()) / 2
    radians = math.radians(-angle)
    cos, sin = math.cos(radians), math.sin(radians)
    out = []
    for x0, y0, x1, y1 in arr:
        corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]) - (cx, cy)
        rx = corners[:, 0] * cos - corners[:, 1] * sin
        ry = corners[:, 0] * sin + corners[:, 1] * cos
        # Caixa alinhada aos eixos de um retângulo w×h girado: W = w·c + h·s e H = w·s + h·c.
        # Invertendo, recupera-se o retângulo já endireitado.
        width, height = x1 - x0, y1 - y0
        mx, my = rx.mean(), ry.mean()
        c, sn = abs(cos), abs(sin)
        det = max(1e-6, c * c - sn * sn)
        w = max(1.0, (width * c - height * sn) / det)
        h = max(1.0, (height * c - width * sn) / det)
        out.append([mx - w / 2, my - h / 2, mx + w / 2, my + h / 2])
    return out


def _median_height(boxes) -> float:
    return float(np.median([b[3] - b[1] for b in boxes])) if boxes else 1.0


def _naive(boxes, params: OrderParams) -> list[int]:
    tolerance = max(1.0, params.tie * _median_height(boxes))
    order = sorted(range(len(boxes)), key=lambda i: (boxes[i][1], boxes[i][0]))
    rows: list[list[int]] = []
    for index in order:
        if rows and boxes[index][1] - boxes[rows[-1][0]][1] <= tolerance:
            rows[-1].append(index)
        else:
            rows.append([index])
    return [i for row in rows for i in sorted(row, key=lambda i: boxes[i][0])]


def _xycut(boxes, params: OrderParams, line_height: float) -> list[int]:
    gap = max(1.0, params.min_gap * line_height)

    def shrunk(i):
        x0, y0, x1, y1 = boxes[i]
        dx, dy = (x1 - x0) * params.shrink / 2, (y1 - y0) * params.shrink / 2
        return x0 + dx, y0 + dy, x1 - dx, y1 - dy

    def split(indices, axis):
        spans = sorted((shrunk(i)[axis], shrunk(i)[axis + 2], i) for i in indices)
        groups, end = [[spans[0][2]]], spans[0][1]
        for start, stop, i in spans[1:]:
            if start - end >= gap:
                groups.append([i])
            else:
                groups[-1].append(i)
            end = max(end, stop)
        return groups

    def recurse(indices):
        if len(indices) <= 1:
            return list(indices)
        for axis in (1, 0):  # primeiro faixas horizontais (corte em y), depois verticais
            groups = split(indices, axis)
            if len(groups) > 1:
                return [i for group in groups for i in recurse(group)]
        return sorted(indices, key=lambda i: (boxes[i][1], boxes[i][0]))

    return recurse(list(range(len(boxes))))


def _anchored(boxes, params: OrderParams) -> list[int]:
    n = len(boxes)
    widths = np.array([b[2] - b[0] for b in boxes])
    wide = [i for i in range(n) if widths[i] >= 0.6 * widths.max()]
    main_left = float(np.median([boxes[i][0] for i in wide]))
    text_width = float(np.median([widths[i] for i in wide]))

    def vertical_overlap(i, j):
        top, bottom = max(boxes[i][1], boxes[j][1]), min(boxes[i][3], boxes[j][3])
        return max(0.0, bottom - top) / max(1.0, boxes[i][3] - boxes[i][1])

    def beside(i, j):
        overlap = min(boxes[i][2], boxes[j][2]) - max(boxes[i][0], boxes[j][0])
        return overlap <= 0.1 * min(widths[i], widths[j])

    lateral = []
    for i in range(n):
        off_axis = abs(boxes[i][0] - main_left) > params.lateral_offset * text_width
        neighbours = [
            j
            for j in range(n)
            if j != i and beside(i, j) and vertical_overlap(i, j) >= params.side_overlap
        ]
        if off_axis and neighbours and widths[i] < 0.7 * text_width:
            lateral.append(i)
    main = sorted(
        (i for i in range(n) if i not in lateral), key=lambda i: (boxes[i][1], boxes[i][0])
    )
    if not main:
        return sorted(range(n), key=lambda i: (boxes[i][1], boxes[i][0]))

    attached: dict[int, list[int]] = {i: [] for i in main}
    for i in lateral:
        best = max(main, key=lambda j: (vertical_overlap(i, j), -abs(boxes[i][1] - boxes[j][1])))
        attached[best].append(i)
    order = []
    for i in main:
        order.append(i)
        order.extend(sorted(attached[i], key=lambda k: (boxes[k][1], boxes[k][0])))
    return order


def order_blocks(blocks: list[dict], lines: list[dict], params: OrderParams) -> list[int]:
    """Índices dos blocos na ordem de leitura."""
    if not blocks:
        return []
    boxes = [list(map(float, block["bbox"])) for block in blocks]
    if params.deskew:
        boxes = _rotated_boxes(boxes, page_skew(lines))
    if params.method == "naive":
        return _naive(boxes, params)
    if params.method == "xycut":
        heights = [min(b[2] - b[0], b[3] - b[1]) for b in (line["bbox"] for line in lines)]
        line_height = float(np.median(heights)) if heights else _median_height(boxes) / 2
        return _xycut(boxes, params, line_height)
    if params.method == "anchored":
        return _anchored(boxes, params)
    raise ValueError(f"método desconhecido: {params.method}")


def order_lines(lines: list[dict]) -> list[int]:
    """Ordem das linhas de um bloco: projeção dos centros na direção perpendicular às linhas."""
    if len(lines) <= 1:
        return list(range(len(lines)))
    angle = math.radians(float(np.median([line_angle(line) for line in lines])))
    # Vetor perpendicular à linha de base, apontando "para baixo" no sentido da leitura.
    px, py = -math.sin(angle), math.cos(angle)

    def key(index):
        x0, y0, x1, y1 = lines[index]["bbox"]
        return ((x0 + x1) / 2) * px + ((y0 + y1) / 2) * py

    return sorted(range(len(lines)), key=key)


def assign_lines(blocks: list[dict], lines: list[dict]) -> list[int | None]:
    """Bloco de cada linha: o menor bloco que contém o centro da linha (``None`` se nenhum)."""
    result: list[int | None] = []
    for line in lines:
        if line.get("block") is not None:
            result.append(line["block"])
            continue
        x0, y0, x1, y1 = line["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        best, best_area = None, None
        for index, block in enumerate(blocks):
            bx0, by0, bx1, by1 = block["bbox"]
            if bx0 <= cx <= bx1 and by0 <= cy <= by1:
                area = (bx1 - bx0) * (by1 - by0)
                if best_area is None or area < best_area:
                    best, best_area = index, area
        result.append(best)
    return result
