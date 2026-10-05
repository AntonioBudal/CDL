"""Retificação de perspectiva: localiza a folha, estima a homografia e desentorta a imagem.

Usa só OpenCV e NumPy e é compatível com Python 3.10 (roda também no ambiente do Doc-UFCN). A
homografia corrige perspectiva; a curvatura perto da lombada **não** é corrigida.
"""

from __future__ import annotations

import cv2
import numpy as np


def order_quad(points) -> np.ndarray:
    """Ordena 4 pontos em: sup.-esquerdo, sup.-direito, inf.-direito, inf.-esquerdo."""
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 2)
    total, diff = pts.sum(axis=1), pts[:, 0] - pts[:, 1]
    return np.array(
        [pts[total.argmin()], pts[diff.argmax()], pts[total.argmax()], pts[diff.argmin()]]
    )


def quad_from_region(points) -> np.ndarray:
    """Quadrilátero de uma região: os pontos extremos em x+y e x−y do seu fecho convexo."""
    hull = cv2.convexHull(np.asarray(points, dtype=np.float32).reshape(-1, 1, 2)).reshape(-1, 2)
    return order_quad(
        [
            hull[(hull[:, 0] + hull[:, 1]).argmin()],
            hull[(hull[:, 0] - hull[:, 1]).argmax()],
            hull[(hull[:, 0] + hull[:, 1]).argmax()],
            hull[(hull[:, 0] - hull[:, 1]).argmin()],
        ]
    )


def find_page_contour(image_bgr: np.ndarray, max_side: int = 1000):
    """Acha a folha como a maior região clara (limiar de Otsu). Devolve o quadrilátero ou None."""
    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    small = cv2.resize(
        image_bgr, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA
    )
    gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (0, 0), 3)
    if float(gray.std()) < 5.0:
        return None  # sem contraste: não há folha distinguível do fundo
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 0.25 * binary.shape[0] * binary.shape[1]:
        return None
    return quad_from_region(largest.reshape(-1, 2) / scale)


def rectify(image_bgr: np.ndarray, quad):
    """Desentorta a imagem pelo quadrilátero. Devolve ``(imagem, homografia)``."""
    quad = order_quad(quad).astype(np.float32)
    width = round(max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3])))
    height = round(max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1])))
    width, height = max(width, 8), max(height, 8)
    target = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    homography = cv2.getPerspectiveTransform(quad, target)
    warped = cv2.warpPerspective(
        image_bgr,
        homography,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return warped, homography


def map_points(points, homography) -> np.ndarray:
    """Aplica uma homografia 3×3 a pontos ``(N, 2)``."""
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(pts, np.asarray(homography, dtype=np.float64)).reshape(-1, 2)


def corner_error(quad, truth) -> float:
    """Distância euclidiana média (px) entre os 4 cantos estimados e os verdadeiros."""
    a, b = order_quad(quad), order_quad(truth)
    return float(np.linalg.norm(a - b, axis=1).mean())
