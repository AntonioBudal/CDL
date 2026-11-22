"""Operações de imagem do catálogo: formato padrão de linha, dimensões e hash perceptivo de
página."""

from __future__ import annotations

import io

from PIL import Image

LINE_HEIGHT = 64  # altura padrão da linha
# Formato da linha: PNG em cinza (1 canal). Medido em 2026-11-22 com 80 linhas reais: 2,7 ms e
# ~35 KB por linha, contra 164 ms e ~31 KB do WebP sem perda (method=6) — 60× mais rápido.
LINE_FORMAT = "png"
PHASH_NEAR = 6  # distância de Hamming máxima (de 64 bits) para "quase a mesma página"


def to_line_format(data: bytes) -> tuple[bytes, int, int]:
    """Linha em cinza (1 canal), altura padrão, PNG. Devolve (bytes, largura, altura)."""
    with Image.open(io.BytesIO(data)) as image:
        gray = image.convert("L")
        width = max(1, round(gray.width * LINE_HEIGHT / max(1, gray.height)))
        small = gray.resize((width, LINE_HEIGHT), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    small.save(out, "PNG")
    return out.getvalue(), width, LINE_HEIGHT


def describe(data: bytes) -> tuple[str, int, int]:
    """Formato, largura e altura do arquivo original."""
    with Image.open(io.BytesIO(data)) as image:
        return (image.format or "bin").lower(), image.width, image.height


def dhash(data: bytes, size: int = 8) -> str:
    """Hash de diferença (64 bits, em hexadecimal): igual para a mesma página em formatos
    diferentes."""
    with Image.open(io.BytesIO(data)) as image:
        small = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
        pixels = list(small.tobytes())
    bits = 0
    for row in range(size):
        for col in range(size):
            left = pixels[row * (size + 1) + col]
            right = pixels[row * (size + 1) + col + 1]
            bits = (bits << 1) | (left > right)
    return f"{bits:016x}"


def hamming(a: str, b: str) -> int:
    return bin(int(a, 16) ^ int(b, 16)).count("1")
