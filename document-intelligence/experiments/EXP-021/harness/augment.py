"""Degradação de foto aplicada a uma linha recortada (EXP-021).

Faixas fixadas a partir dos níveis ``light`` e ``strong`` do EXP-002 (``pages/degrade.py``), antes
de qualquer treino: um nível ``t`` em [0, 1] interpola de leve a forte. Inclui uma inclinação
pequena, gradiente de luz, desfoque gaussiano, ruído e compressão JPEG.
"""

from __future__ import annotations

import cv2
import numpy as np

MAX_ANGLE = 3.0  # graus
LIGHT_MIN = (0.82, 0.55)  # brilho mínimo do gradiente, leve → forte
BLUR = (0.5, 1.1)
NOISE = (2.0, 5.0)
JPEG = (88, 65)


def _lerp(pair: tuple[float, float], t: float) -> float:
    return pair[0] + (pair[1] - pair[0]) * t


def degrade_line(image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Linha BGR ``uint8`` → linha degradada do mesmo tamanho."""
    h, w = image.shape[:2]
    t = float(rng.uniform(0, 1))
    angle = float(rng.uniform(-MAX_ANGLE, MAX_ANGLE))
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    out = cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    theta = float(rng.uniform(0, 2 * np.pi))
    xs, ys = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    ramp = xs * np.cos(theta) + ys * np.sin(theta)
    ramp = (ramp - ramp.min()) / max(1e-6, float(ramp.max() - ramp.min()))
    out *= (1 - (1 - _lerp(LIGHT_MIN, t)) * ramp)[..., None].astype(np.float32)
    out = cv2.GaussianBlur(out, (0, 0), sigmaX=_lerp(BLUR, t))
    out += rng.normal(0, _lerp(NOISE, t), out.shape).astype(np.float32)
    out = np.clip(out, 0, 255).astype(np.uint8)
    quality = round(_lerp(JPEG, t))
    ok, encoded = cv2.imencode(".jpg", out, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return cv2.imdecode(encoded, cv2.IMREAD_COLOR) if ok else out
