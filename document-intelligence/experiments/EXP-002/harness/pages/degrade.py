"""Degradações fotográficas aplicadas à imagem da página e, com o mesmo mapeamento, à geometria.

Ordem: página sobre fundo de mesa → curvatura perto da lombada → perspectiva (homografia) →
iluminação e sombra → desfoque → ruído → compressão JPEG. As transformações geométricas têm forma
fechada nos dois sentidos, para que pontos da verdade de chão acompanhem exatamente a imagem.
"""

from __future__ import annotations

import io
import random
from dataclasses import asdict, dataclass

import cv2
import numpy as np
from PIL import Image

LEVELS = ("clean", "light", "strong")


@dataclass(frozen=True)
class LevelParams:
    pad: float
    perspective: float  # deslocamento máximo de cada canto, fração do lado
    curvature: float  # amplitude máxima da dilatação vertical perto da lombada
    light_min: float  # brilho mínimo do gradiente de iluminação
    shadow_prob: float
    shadow_strength: float  # multiplicador dentro da sombra
    blur_sigma: float
    noise_sigma: float
    jpeg_quality: int


PARAMS = {
    "light": LevelParams(0.06, 0.03, 0.012, 0.82, 0.3, 0.85, 0.5, 2.0, 88),
    "strong": LevelParams(0.08, 0.08, 0.035, 0.55, 0.8, 0.6, 1.1, 5.0, 65),
}
BACKGROUNDS = [(96, 72, 52), (140, 112, 84), (70, 70, 74), (180, 170, 160), (120, 128, 120)]


@dataclass
class GeometricTransform:
    """Mapeia pontos da página limpa para a imagem degradada."""

    offset: tuple[float, float]
    page_size: tuple[int, int]
    spine_left: bool
    curvature: float
    homography: list[list[float]]
    output_size: tuple[int, int]

    def _k(self, x_page: np.ndarray) -> np.ndarray:
        width = self.page_size[0]
        rel = x_page if self.spine_left else width - x_page
        return self.curvature * np.clip(1 - rel / (0.35 * width), 0, None) ** 2

    def apply_points(self, points: np.ndarray) -> np.ndarray:
        """Pontos ``(N, 2)`` em coordenadas da página → coordenadas da imagem de saída."""
        pts = np.asarray(points, dtype=np.float64).reshape(-1, 2)
        k = self._k(pts[:, 0])
        cy = self.page_size[1] / 2
        canvas = np.stack(
            [pts[:, 0] + self.offset[0], cy + (pts[:, 1] - cy) * (1 + k) + self.offset[1]], axis=1
        )
        out = cv2.perspectiveTransform(canvas.reshape(-1, 1, 2), np.array(self.homography))
        return out.reshape(-1, 2)

    def apply_image(self, canvas: np.ndarray) -> np.ndarray:
        """Aplica curvatura e homografia a uma imagem já em coordenadas do canvas."""
        h, w = canvas.shape[:2]
        xs, ys = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        k = self._k(xs - self.offset[0]).astype(np.float32)
        cy = self.page_size[1] / 2 + self.offset[1]
        map_y = (cy + (ys - cy) / (1 + k)).astype(np.float32)
        curved = cv2.remap(canvas, xs, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return cv2.warpPerspective(
            curved,
            np.array(self.homography),
            self.output_size,
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        )


def make_transform(
    page_size: tuple[int, int], params: LevelParams, rng: random.Random
) -> GeometricTransform:
    width, height = page_size
    pad_x, pad_y = round(width * params.pad), round(height * params.pad)
    out_w, out_h = width + 2 * pad_x, height + 2 * pad_y
    src = np.float32([[0, 0], [out_w, 0], [out_w, out_h], [0, out_h]])
    dst = src + np.float32(
        [
            [
                rng.uniform(-1, 1) * params.perspective * out_w,
                rng.uniform(-1, 1) * params.perspective * out_h,
            ]
            for _ in range(4)
        ]
    )
    homography = cv2.getPerspectiveTransform(src, dst)
    return GeometricTransform(
        offset=(float(pad_x), float(pad_y)),
        page_size=page_size,
        spine_left=rng.random() < 0.5,
        curvature=rng.uniform(0.3, 1.0) * params.curvature,
        homography=homography.tolist(),
        output_size=(out_w, out_h),
    )


def _background(
    size: tuple[int, int], rng: random.Random, np_rng: np.random.Generator
) -> np.ndarray:
    width, height = size
    base = np.array(rng.choice(BACKGROUNDS), dtype=np.float32)
    low = cv2.resize(
        np_rng.normal(0, 12, (height // 40 + 2, width // 40 + 2)).astype(np.float32),
        (width, height),
        interpolation=cv2.INTER_CUBIC,
    )
    return np.clip(base + low[..., None], 0, 255)


def _photometric(
    image: np.ndarray, params: LevelParams, rng: random.Random, np_rng: np.random.Generator
) -> np.ndarray:
    h, w = image.shape[:2]
    out = image.astype(np.float32)
    theta = rng.uniform(0, 2 * np.pi)
    xs, ys = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    t = xs * np.cos(theta) + ys * np.sin(theta)
    t = (t - t.min()) / max(1e-6, t.max() - t.min())
    out *= (1 - (1 - params.light_min) * t)[..., None].astype(np.float32)
    if rng.random() < params.shadow_prob:
        mask = np.zeros((h, w), np.float32)
        edge = rng.choice(["left", "right", "bottom"])
        depth = rng.uniform(0.15, 0.4)
        if edge == "left":
            pts = [
                (0, rng.uniform(0, h)),
                (w * depth, rng.uniform(0, h)),
                (w * depth * 0.6, h),
                (0, h),
            ]
        elif edge == "right":
            pts = [
                (w, rng.uniform(0, h)),
                (w * (1 - depth), rng.uniform(0, h)),
                (w * (1 - depth), h),
                (w, h),
            ]
        else:
            pts = [
                (rng.uniform(0, w), h * (1 - depth)),
                (rng.uniform(0, w), h * (1 - depth * 0.5)),
                (w, h),
                (0, h),
            ]
        cv2.fillPoly(mask, [np.int32(pts)], 1.0)
        mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=max(w, h) * 0.03)
        out *= (1 - (1 - params.shadow_strength) * mask)[..., None]
    if params.blur_sigma > 0:
        out = cv2.GaussianBlur(out, (0, 0), sigmaX=params.blur_sigma)
    out += np_rng.normal(0, params.noise_sigma, out.shape).astype(np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)


@dataclass
class Degraded:
    image_bytes: bytes
    extension: str
    size: tuple[int, int]
    transform: GeometricTransform | None
    params: dict


def degrade(page: Image.Image, level: str, seed: int) -> Degraded:
    """Degrada a página limpa no nível pedido. ``clean`` devolve a página em PNG, sem alteração."""
    if level == "clean":
        buffer = io.BytesIO()
        page.save(buffer, format="PNG")
        return Degraded(buffer.getvalue(), ".png", page.size, None, {"level": "clean"})

    params = PARAMS[level]
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    transform = make_transform(page.size, params, rng)
    out_w, out_h = transform.output_size
    canvas = _background((out_w, out_h), rng, np_rng)
    ox, oy = round(transform.offset[0]), round(transform.offset[1])
    canvas[oy : oy + page.size[1], ox : ox + page.size[0]] = np.asarray(page, dtype=np.float32)
    warped = transform.apply_image(canvas.astype(np.uint8))
    final = _photometric(warped, params, rng, np_rng)
    buffer = io.BytesIO()
    Image.fromarray(final, "RGB").save(buffer, format="JPEG", quality=params.jpeg_quality)
    record = {"level": level, **asdict(params), "transform": asdict(transform)}
    return Degraded(buffer.getvalue(), ".jpg", (out_w, out_h), transform, record)


def densify(polygon: np.ndarray, step: float = 8.0) -> np.ndarray:
    """Acrescenta pontos ao longo das arestas do polígono a cada ``step`` pixels."""
    pts = np.asarray(polygon, dtype=np.float64).reshape(-1, 2)
    out = []
    for a, b in zip(pts, np.roll(pts, -1, axis=0), strict=True):
        n = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        out.extend(a + (b - a) * (i / n) for i in range(n))
    return np.array(out)


def transform_polygon(
    polygon, transform: GeometricTransform | None
) -> tuple[list[int], list[list[int]]]:
    """Transforma um polígono e devolve ``(bbox, polígono simplificado)`` em inteiros."""
    pts = np.asarray(polygon, dtype=np.float64).reshape(-1, 2)
    if transform is not None:
        pts = transform.apply_points(densify(pts))
    bbox = [
        int(np.floor(pts[:, 0].min())),
        int(np.floor(pts[:, 1].min())),
        int(np.ceil(pts[:, 0].max())),
        int(np.ceil(pts[:, 1].max())),
    ]
    if transform is None:
        return bbox, [[round(x), round(y)] for x, y in pts]
    simplified = cv2.approxPolyDP(pts.astype(np.float32).reshape(-1, 1, 2), 1.0, True).reshape(
        -1, 2
    )
    return bbox, [[round(float(x)), round(float(y))] for x, y in simplified]


def box_polygon(bbox) -> list[list[float]]:
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
