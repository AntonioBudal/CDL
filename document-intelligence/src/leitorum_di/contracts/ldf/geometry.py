"""Geometria do LDF: envelope e sentido de polígonos, recorte e homografia (Python puro)."""

from __future__ import annotations

from collections.abc import Sequence

Point = Sequence[float]
Matrix = list[list[float]]


def envelope(polygon: Sequence[Point]) -> list[float]:
    """Caixa alinhada aos eixos ``[x_min, y_min, x_max, y_max]`` que contém o polígono."""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def signed_area(polygon: Sequence[Point]) -> float:
    """Área com sinal; positiva quando os vértices estão em sentido horário (eixo y para baixo)."""
    total = 0.0
    for index, (x0, y0) in enumerate(polygon):
        x1, y1 = polygon[(index + 1) % len(polygon)]
        total += x0 * y1 - x1 * y0
    return total / 2


def clockwise(polygon: Sequence[Point]) -> list[list[float]]:
    """Devolve o polígono com os vértices em sentido horário."""
    points = [[float(p[0]), float(p[1])] for p in polygon]
    return points if signed_area(points) >= 0 else points[::-1]


def bbox_polygon(bbox: Sequence[float]) -> list[list[float]]:
    """Os quatro cantos de uma caixa, em sentido horário a partir do superior esquerdo."""
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _clip_edge(
    points: list[list[float]], axis: int, limit: float, keep_greater: bool
) -> list[list[float]]:
    def inside(p: list[float]) -> bool:
        return p[axis] >= limit if keep_greater else p[axis] <= limit

    clipped: list[list[float]] = []
    for index, current in enumerate(points):
        previous = points[index - 1]
        if inside(current) != inside(previous):
            ratio = (limit - previous[axis]) / (current[axis] - previous[axis])
            crossing = [
                previous[0] + ratio * (current[0] - previous[0]),
                previous[1] + ratio * (current[1] - previous[1]),
            ]
            crossing[axis] = limit
            clipped.append(crossing)
        if inside(current):
            clipped.append(current)
    return clipped


def clip_polygon(polygon: Sequence[Point], width: float, height: float) -> list[list[float]]:
    """Recorta o polígono ao retângulo da imagem (Sutherland–Hodgman)."""
    points = [[float(p[0]), float(p[1])] for p in polygon]
    for axis, limit, keep_greater in (
        (0, 0.0, True),
        (0, float(width), False),
        (1, 0.0, True),
        (1, float(height), False),
    ):
        if not points:
            break
        points = _clip_edge(points, axis, limit, keep_greater)
    return points


def _solve(matrix: list[list[float]], values: list[float]) -> list[float]:
    """Resolve um sistema linear por eliminação de Gauss com pivoteamento parcial."""
    size = len(values)
    rows = [[float(v) for v in matrix[i]] + [float(values[i])] for i in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(rows[r][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ValueError("sistema singular: os pontos não definem uma homografia")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(size):
            if r != col:
                factor = rows[r][col] / rows[col][col]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[col], strict=True)]
    return [rows[i][size] / rows[i][i] for i in range(size)]


def homography_from_quads(source: Sequence[Point], target: Sequence[Point]) -> Matrix:
    """Homografia 3×3 que leva os quatro pontos de ``source`` aos de ``target``."""
    if len(source) != 4 or len(target) != 4:
        raise ValueError("são necessários exatamente quatro pares de pontos")
    matrix, values = [], []
    for (x, y), (u, v) in zip(source, target, strict=True):
        matrix.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        values.append(u)
        matrix.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        values.append(v)
    h = _solve(matrix, values)
    return [[h[0], h[1], h[2]], [h[3], h[4], h[5]], [h[6], h[7], 1.0]]


def invert(matrix: Matrix) -> Matrix:
    """Inversa de uma matriz 3×3."""
    (a, b, c), (d, e, f), (g, h, i) = matrix
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        raise ValueError("homografia singular")
    return [
        [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
        [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
        [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
    ]


def apply_homography(matrix: Matrix, point: Point) -> list[float]:
    """Aplica a homografia a um ponto."""
    x, y = point
    w = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]
    return [
        (matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]) / w,
        (matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]) / w,
    ]


def to_rectified(rectification: dict, point: Point) -> list[float]:
    """Leva um ponto da fotografia original para a imagem retificada."""
    return apply_homography(rectification["homography"], point)


def to_source(rectification: dict, point: Point) -> list[float]:
    """Leva um ponto da imagem retificada de volta para a fotografia original."""
    return apply_homography(invert(rectification["homography"]), point)
