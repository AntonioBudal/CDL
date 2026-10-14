"""Recorte de linhas para leitura: desentorta o retângulo mínimo da linha por perspectiva.

Compatível com Python 3.10+ (roda no ambiente do PP-OCR e no do harness).
"""

from __future__ import annotations

import cv2
import numpy as np


def line_quad(points) -> np.ndarray:
    """Quatro cantos do retângulo mínimo da linha, ordenados para leitura.

    Ordem: superior esquerdo, superior direito, inferior direito, inferior esquerdo (y para baixo).
    """
    box = cv2.boxPoints(cv2.minAreaRect(np.asarray(points, dtype=np.float32).reshape(-1, 2)))
    by_x = box[np.argsort(box[:, 0])]
    left = by_x[:2][np.argsort(by_x[:2, 1])]
    right = by_x[2:][np.argsort(by_x[2:, 1])]
    return np.float32([left[0], right[0], right[1], left[1]])


def crop_line(image: np.ndarray, points, pad: int = 2) -> np.ndarray:
    """Imagem da linha, horizontal, a partir do contorno (ou dos cantos da caixa)."""
    quad = line_quad(points)
    width = int(round(max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3]))))
    height = int(round(max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1]))))
    width, height = max(width, 4) + 2 * pad, max(height, 4) + 2 * pad
    target = np.float32(
        [[pad, pad], [width - pad, pad], [width - pad, height - pad], [pad, height - pad]]
    )
    matrix = cv2.getPerspectiveTransform(quad, target)
    return cv2.warpPerspective(
        image, matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
    )


def box_points(bbox) -> list[list[float]]:
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def reading_order(lines: list[dict]) -> list[int]:
    """Índices das linhas de cima para baixo; linhas na mesma faixa, da esquerda para a direita."""
    if not lines:
        return []
    heights = sorted(max(1, ln["bbox"][3] - ln["bbox"][1]) for ln in lines)
    tolerance = heights[len(heights) // 2] / 2
    centers = [((ln["bbox"][1] + ln["bbox"][3]) / 2, ln["bbox"][0]) for ln in lines]
    order = sorted(range(len(lines)), key=lambda i: centers[i][0])
    rows: list[list[int]] = []
    for index in order:
        if rows and abs(centers[index][0] - centers[rows[-1][0]][0]) <= tolerance:
            rows[-1].append(index)
        else:
            rows.append([index])
    return [i for row in rows for i in sorted(row, key=lambda k: centers[k][1])]
