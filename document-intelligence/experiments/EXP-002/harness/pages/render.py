"""Renderização de uma página de caderno limpa, com verdade de chão de linhas e blocos.

A geometria de cada linha vem da própria máscara de tinta renderizada: a bbox é a caixa justa
e o polígono é o retângulo rotacionado mínimo. Texto dentro de diagramas não é linha anotada;
a região do
diagrama vira bloco ``graphic_box`` e região "ignorar".
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pages import content

PAGE_WIDTH = 1240
PAGE_HEIGHT = 1754
RIGHT_MARGIN = 70
BOTTOM_MARGIN = 70
ALPHA_THRESHOLD = 90  # 0–255: pixel conta como tinta da linha
RULE_COLOR = (172, 192, 228)
MARGIN_COLOR = (222, 120, 120)
INK_COLORS = [(25, 35, 110), (22, 22, 28), (40, 45, 140), (30, 60, 120)]


@dataclass
class Line:
    id: str
    block_id: str
    text: str
    bbox: list[int]
    polygon: list[list[int]]


@dataclass
class Block:
    id: str
    type: str  # title | paragraph | margin_note | graphic_box
    bbox: list[int]
    line_ids: list[str] = field(default_factory=list)


@dataclass
class PageTruth:
    width: int
    height: int
    font: str
    lines: list[Line] = field(default_factory=list)
    blocks: list[Block] = field(default_factory=list)
    ignore: list[list[int]] = field(default_factory=list)


def font_size_for(font_path: Path, target_height: float) -> int:
    """Tamanho de fonte cuja altura de "Ágjy" fica próxima de ``target_height`` pixels."""
    probe = ImageFont.truetype(str(font_path), 100)
    _, top, _, bottom = probe.getbbox("Ágjy")
    return max(8, round(100 * target_height / max(1, bottom - top)))


def _union(boxes: list[list[int]]) -> list[int]:
    return [
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    ]


class _Canvas:
    def __init__(self, rng: random.Random, np_rng: np.random.Generator) -> None:
        base = np.array(
            [rng.randint(240, 252), rng.randint(238, 250), rng.randint(228, 244)], dtype=np.float32
        )
        noise = np_rng.normal(0.0, 2.2, (PAGE_HEIGHT, PAGE_WIDTH, 1)).astype(np.float32)
        self.pixels = np.clip(base + noise, 0, 255)

    def draw_rgb(self, draw_fn) -> None:
        image = Image.fromarray(self.pixels.astype(np.uint8))
        draw_fn(ImageDraw.Draw(image))
        self.pixels = np.asarray(image, dtype=np.float32).copy()

    def composite(self, alpha: np.ndarray, x0: int, y0: int, color: tuple[int, int, int]) -> None:
        """Mistura tinta de cor ``color`` com opacidade ``alpha`` (0–255) na posição dada."""
        h, w = alpha.shape
        x1, y1 = min(PAGE_WIDTH, x0 + w), min(PAGE_HEIGHT, y0 + h)
        ax0, ay0 = max(0, -x0), max(0, -y0)
        x0, y0 = max(0, x0), max(0, y0)
        if x1 <= x0 or y1 <= y0:
            return
        a = alpha[ay0 : ay0 + (y1 - y0), ax0 : ax0 + (x1 - x0)].astype(np.float32)[..., None] / 255
        region = self.pixels[y0:y1, x0:x1]
        self.pixels[y0:y1, x0:x1] = region * (1 - a) + np.array(color, np.float32) * a


def _render_words(
    words: list[str],
    font: ImageFont.FreeTypeFont,
    angle: float,
    rng: random.Random,
    stroke: int,
) -> tuple[np.ndarray, tuple[float, float]]:
    """Desenha uma linha palavra a palavra e gira em torno do início da linha de base.

    Devolve a máscara alfa e a posição, nela, do ponto de ancoragem (início da linha de base).
    """
    ascent, descent = font.getmetrics()
    space = font.getlength(" ")
    width = int(sum(font.getlength(word) for word in words) + space * 1.6 * len(words)) + 40
    pad = 12
    layer = Image.new("L", (width + 2 * pad, ascent + descent + 2 * pad + 8), 0)
    draw = ImageDraw.Draw(layer)
    x = float(pad)
    anchor_y = pad + ascent + 4
    for word in words:
        jitter = rng.uniform(-1.5, 1.5)
        draw.text(
            (x, anchor_y + jitter),
            word,
            font=font,
            fill=255,
            anchor="ls",
            stroke_width=stroke,
            stroke_fill=255,
        )
        x += font.getlength(word) + space * rng.uniform(0.85, 1.35)
    mask = np.asarray(layer)
    anchor = (float(pad), float(anchor_y))

    h, w = mask.shape
    matrix = cv2.getRotationMatrix2D(anchor, angle, 1.0)
    corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], dtype=np.float64)
    rotated = corners @ matrix.T
    min_xy = rotated.min(axis=0)
    size = np.ceil(rotated.max(axis=0) - min_xy).astype(int) + 1
    matrix[:, 2] -= min_xy
    out = cv2.warpAffine(mask, matrix, (int(size[0]), int(size[1])), flags=cv2.INTER_LINEAR)
    new_anchor = matrix @ np.array([anchor[0], anchor[1], 1.0])
    return out, (float(new_anchor[0]), float(new_anchor[1]))


def _ink_geometry(alpha: np.ndarray, x0: int, y0: int) -> tuple[list[int], list[list[int]]] | None:
    ys, xs = np.nonzero(alpha >= ALPHA_THRESHOLD)
    if xs.size == 0:
        return None
    xs = np.clip(xs + x0, 0, PAGE_WIDTH - 1)
    ys = np.clip(ys + y0, 0, PAGE_HEIGHT - 1)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    points = np.stack([xs, ys], axis=1).astype(np.float32)
    box = cv2.boxPoints(cv2.minAreaRect(points))
    polygon = [[round(float(px)), round(float(py))] for px, py in box]
    return bbox, polygon


class _PageBuilder:
    def __init__(self, seed: int, fonts: list[Path]) -> None:
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)
        rng = self.rng
        self.font_path = rng.choice(fonts)
        self.spacing = rng.randint(44, 56)
        self.top = rng.randint(150, 190)
        self.margin_x = rng.randint(130, 160)
        self.ink = rng.choice(INK_COLORS)
        self.stroke = rng.choice([0, 0, 1])
        self.body_size = font_size_for(self.font_path, self.spacing * rng.uniform(0.78, 0.9))
        self.font = ImageFont.truetype(str(self.font_path), self.body_size)
        self.canvas = _Canvas(rng, self.np_rng)
        self.truth = PageTruth(PAGE_WIDTH, PAGE_HEIGHT, self.font_path.name)
        self.rows = (PAGE_HEIGHT - BOTTOM_MARGIN - self.top) // self.spacing
        self.counter = 0

    def baseline(self, row: int) -> int:
        return self.top + row * self.spacing

    def _next_id(self, prefix: str) -> str:
        self.counter += 1
        return f"{prefix}{self.counter:03d}"

    def draw_rules(self) -> None:
        def draw(d: ImageDraw.ImageDraw) -> None:
            for row in range(self.rows + 1):
                y = self.baseline(row)
                d.line([(0, y), (PAGE_WIDTH, y)], fill=RULE_COLOR, width=1)
            d.line([(self.margin_x, 0), (self.margin_x, PAGE_HEIGHT)], fill=MARGIN_COLOR, width=2)

        self.canvas.draw_rgb(draw)

    def place_line(self, words, font, x, y, angle, block_id) -> Line | None:
        alpha, anchor = _render_words(words, font, angle, self.rng, self.stroke)
        x0, y0 = round(x - anchor[0]), round(y - anchor[1])
        self.canvas.composite(alpha, x0, y0, self.ink)
        geometry = _ink_geometry(alpha, x0, y0)
        if geometry is None:
            return None
        line = Line(self._next_id("l"), block_id, " ".join(words), geometry[0], geometry[1])
        self.truth.lines.append(line)
        return line

    def wrap(self, words: list[str], font, width: float) -> list[list[str]]:
        lines, current = [], []
        space = font.getlength(" ") * 1.1
        for word in words:
            candidate = current + [word]
            if current and sum(font.getlength(w) for w in candidate) + space * len(current) > width:
                lines.append(current)
                current = [word]
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines

    def add_title(self, row: int) -> None:
        rng = self.rng
        text = content.title(rng)
        if rng.random() < 0.4:
            text = text.upper()
        font = ImageFont.truetype(
            str(self.font_path), round(self.body_size * rng.uniform(1.15, 1.35))
        )
        block_id = self._next_id("b")
        x = self.margin_x + rng.randint(20, 120)
        available = PAGE_WIDTH - RIGHT_MARGIN - x
        words = self.wrap(text.split(), font, available)[0]
        line = self.place_line(words, font, x, self.baseline(row), rng.uniform(-1.5, 1.5), block_id)
        if line is None:
            return
        if rng.random() < 0.5:
            y = line.bbox[3] + 4
            self.canvas.draw_rgb(
                lambda d: d.line([(line.bbox[0], y), (line.bbox[2], y)], fill=self.ink, width=2)
            )
        self.truth.blocks.append(Block(block_id, "title", list(line.bbox), [line.id]))

    def add_paragraph(self, row: int, max_lines: int) -> int:
        rng = self.rng
        block_id = self._next_id("b")
        x_start = self.margin_x + rng.randint(15, 30)
        width = PAGE_WIDTH - RIGHT_MARGIN - x_start
        wrapped = self.wrap(content.paragraph_words(rng, rng.randint(2, 4)), self.font, width)
        wrapped = wrapped[: rng.randint(2, max(2, max_lines))][:max_lines]
        placed = []
        for index, words in enumerate(wrapped):
            indent = rng.choice([0, 40]) if index == 0 else 0
            y = self.baseline(row + index) + rng.randint(-3, 2)
            line = self.place_line(
                words, self.font, x_start + indent, y, rng.uniform(-2.0, 2.0), block_id
            )
            if line is not None:
                placed.append(line)
        if placed:
            self.truth.blocks.append(
                Block(
                    block_id,
                    "paragraph",
                    _union([ln.bbox for ln in placed]),
                    [ln.id for ln in placed],
                )
            )
        return len(wrapped)

    def add_margin_note(self, row: int, rows_available: int) -> None:
        rng = self.rng
        block_id = self._next_id("b")
        text = content.margin_note(rng)
        placed = []
        if rng.random() < 0.5:
            font = ImageFont.truetype(str(self.font_path), round(self.body_size * 0.7))
            length = font.getlength(text)
            if length > rows_available * self.spacing:
                return
            x = self.margin_x / 2 + font.getmetrics()[0] / 2
            y = self.baseline(row) + length
            line = self.place_line(text.split(), font, x, y, 90 + rng.uniform(-3, 3), block_id)
            if line is not None:
                placed.append(line)
        else:
            size = round(self.body_size * 0.6)
            font = ImageFont.truetype(str(self.font_path), size)
            while size > 10 and max(font.getlength(w) for w in text.split()) > self.margin_x - 24:
                size -= 2
                font = ImageFont.truetype(str(self.font_path), size)
            lines = self.wrap(text.split(), font, self.margin_x - 24)[:3]
            for index, words in enumerate(lines):
                y = self.baseline(row) + index * round(size * 1.15)
                line = self.place_line(words, font, 12, y, rng.uniform(-3, 3), block_id)
                if line is not None:
                    placed.append(line)
        if placed:
            self.truth.blocks.append(
                Block(
                    block_id,
                    "margin_note",
                    _union([ln.bbox for ln in placed]),
                    [ln.id for ln in placed],
                )
            )

    def add_diagram(self, row: int, rows: int) -> None:
        rng = self.rng
        count = rng.randint(2, 3)
        labels = content.diagram_labels(rng, count)
        font = ImageFont.truetype(str(self.font_path), round(self.body_size * 0.85))
        top = self.baseline(row) - self.spacing // 2
        height = rows * self.spacing
        left = self.margin_x + 40
        slot = (PAGE_WIDTH - RIGHT_MARGIN - left) / count
        layer = Image.new("L", (PAGE_WIDTH, PAGE_HEIGHT), 0)
        draw = ImageDraw.Draw(layer)
        centers = []
        for index, label in enumerate(labels):
            w = font.getlength(label) + 40
            h = font.getmetrics()[0] + font.getmetrics()[1] + 30
            cx = left + slot * (index + 0.5) + rng.uniform(-20, 20)
            cy = top + height / 2 + rng.uniform(-height / 5, height / 5)
            box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
            if rng.random() < 0.5:
                draw.rectangle(box, outline=255, width=3)
            else:
                draw.ellipse(
                    [box[0] - 12, box[1] - 8, box[2] + 12, box[3] + 8], outline=255, width=3
                )
            draw.text((cx, cy), label, font=font, fill=255, anchor="mm")
            centers.append((cx, cy, w / 2 + 14))
        for (x1, y1, r1), (x2, y2, r2) in zip(centers, centers[1:], strict=False):
            angle = math.atan2(y2 - y1, x2 - x1)
            start = (x1 + r1 * math.cos(angle), y1 + r1 * math.sin(angle))
            end = (x2 - r2 * math.cos(angle), y2 - r2 * math.sin(angle))
            draw.line([start, end], fill=255, width=3)
            for side in (-0.45, 0.45):
                head = (end[0] - 18 * math.cos(angle + side), end[1] - 18 * math.sin(angle + side))
                draw.line([end, head], fill=255, width=3)
        alpha = np.asarray(layer)
        self.canvas.composite(alpha, 0, 0, self.ink)
        geometry = _ink_geometry(alpha, 0, 0)
        if geometry is None:
            return
        bbox = geometry[0]
        self.truth.blocks.append(Block(self._next_id("b"), "graphic_box", list(bbox), []))
        self.truth.ignore.append(list(bbox))

    def build(self) -> tuple[Image.Image, PageTruth]:
        rng = self.rng
        self.draw_rules()
        row = 0
        self.add_title(row)
        row += 2
        diagram_done = rng.random() >= 0.6
        notes_left = rng.choice([0, 1, 1, 2])
        while row < self.rows - 1:
            remaining = self.rows - row
            if not diagram_done and remaining >= 6 and rng.random() < 0.35:
                rows = rng.randint(4, 6)
                self.add_diagram(row, rows)
                diagram_done = True
                row += rows + 1
                continue
            if notes_left and rng.random() < 0.4:
                self.add_margin_note(row, min(remaining, 6))
                notes_left -= 1
            used = self.add_paragraph(row, min(7, remaining))
            row += used + 1
        image = Image.fromarray(np.clip(self.canvas.pixels, 0, 255).astype(np.uint8), "RGB")
        return image, self.truth


def render_page(seed: int, fonts: list[Path]) -> tuple[Image.Image, PageTruth]:
    """Renderiza a página limpa determinada por ``seed`` e devolve imagem e verdade de chão."""
    return _PageBuilder(seed, sorted(fonts)).build()
