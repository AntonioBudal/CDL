"""Baseline clássico de detecção de linhas (sem aprendizado): OpenCV + NumPy.

Etapas: tons de cinza → binarização adaptativa → remoção da pauta e da linha de margem por abertura
morfológica → descarte de ruído → dilatação horizontal para unir letras e palavras → componentes
conexos → fusão de pedaços da mesma linha → bbox e polígono (retângulo rotacionado mínimo).

Também expõe a máscara de tinta sem pauta, usada pelas regras de blocos para achar caixas gráficas.
Os parâmetros são calibrados **só** no conjunto ``dev`` (``calibrate_classic.py``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class ClassicParams:
    block_size: int = 41  # janela da binarização adaptativa (ímpar)
    offset: int = 18  # constante subtraída da média local
    rule_kernel: int = 90  # comprimento do elemento estruturante que remove a pauta
    dilate_width: int = 21  # largura da dilatação horizontal (une letras)
    dilate_height: int = 3
    min_area: int = 120  # área mínima de um componente de linha
    max_height_factor: float = 3.0  # componentes mais altos que isso × mediana viram não-linha
    merge_gap_factor: float = 2.5  # fusão: distância horizontal máxima em alturas medianas
    max_side: int = 2500  # imagens maiores são reduzidas antes do processamento

    def to_dict(self) -> dict:
        return asdict(self)


RULE_ANGLES = (-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5, 6.0)


def _line_kernel(length: int, angle: float) -> np.ndarray:
    """Elemento estruturante: segmento de ``length`` pixels inclinado ``angle`` graus."""
    radians = np.deg2rad(angle)
    dx, dy = np.cos(radians) * (length - 1) / 2, np.sin(radians) * (length - 1) / 2
    size = int(np.ceil(max(abs(dx), abs(dy)) * 2)) + 1
    kernel = np.zeros((size, size), np.uint8)
    c = (size - 1) / 2
    cv2.line(kernel, (round(c - dx), round(c - dy)), (round(c + dx), round(c + dy)), 1, 1)
    return kernel


def ink_mask(gray: np.ndarray, params: ClassicParams) -> np.ndarray:
    """Máscara binária (255 = tinta) sem a pauta horizontal nem linhas verticais longas."""
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        params.block_size,
        params.offset,
    )
    # Pauta e margem podem estar inclinadas pela perspectiva: abertura com segmentos inclinados.
    rules = np.zeros_like(binary)
    for angle in RULE_ANGLES:
        rules = cv2.bitwise_or(
            rules, cv2.morphologyEx(binary, cv2.MORPH_OPEN, _line_kernel(params.rule_kernel, angle))
        )
        rules = cv2.bitwise_or(
            rules,
            cv2.morphologyEx(binary, cv2.MORPH_OPEN, _line_kernel(params.rule_kernel, 90 + angle)),
        )
    cleaned = cv2.subtract(binary, cv2.dilate(rules, np.ones((3, 3), np.uint8)))
    return cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))


def _overlap_ratio(a, b) -> float:
    top, bottom = max(a[1], b[1]), min(a[3], b[3])
    return max(0, bottom - top) / max(1, min(a[3] - a[1], b[3] - b[1]))


def detect_lines(
    image_bgr: np.ndarray, params: ClassicParams
) -> tuple[list[dict], np.ndarray, float]:
    """Detecta linhas; devolve ``(linhas, máscara de tinta, fator de escala aplicado)``."""
    h, w = image_bgr.shape[:2]
    scale = min(1.0, params.max_side / max(h, w))
    if scale < 1.0:
        image_bgr = cv2.resize(
            image_bgr, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA
        )
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    mask = ink_mask(gray, params)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (params.dilate_width, params.dilate_height))
    joined = cv2.dilate(mask, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)

    pieces = []
    for label in range(1, count):
        x, y, bw, bh, area = stats[label]
        if area < params.min_area or bw < bh * 0.8:
            continue
        pieces.append([int(x), int(y), int(x + bw), int(y + bh), label])
    if not pieces:
        return [], mask, scale
    median_h = float(np.median([p[3] - p[1] for p in pieces]))
    pieces = [p for p in pieces if p[3] - p[1] <= params.max_height_factor * median_h]

    # Fusão de pedaços da mesma linha (palavras separadas por espaço largo).
    pieces.sort(key=lambda p: (p[1], p[0]))
    groups: list[list[list[int]]] = []
    for piece in sorted(pieces, key=lambda p: p[0]):
        for group in groups:
            last = group[-1]
            gap = piece[0] - last[2]
            if gap <= params.merge_gap_factor * median_h and _overlap_ratio(last, piece) >= 0.5:
                group.append(piece)
                break
        else:
            groups.append([piece])

    lines = []
    for group in groups:
        member = np.isin(labels, [p[4] for p in group]) & (mask > 0)
        ys, xs = np.nonzero(member)
        if xs.size < 20:
            continue
        points = np.stack([xs, ys], axis=1).astype(np.float32)
        box = cv2.boxPoints(cv2.minAreaRect(points)) / scale
        bbox = [xs.min() / scale, ys.min() / scale, (xs.max() + 1) / scale, (ys.max() + 1) / scale]
        lines.append(
            {
                "bbox": [round(float(v)) for v in bbox],
                "polygon": [[round(float(x)), round(float(y))] for x, y in box],
                "score": 1.0,
            }
        )
    return lines, mask, scale
