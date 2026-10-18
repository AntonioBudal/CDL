"""Regra de ampliação de linha do pipeline (EXP-012), com imagens fictícias."""

import numpy as np
from pipeline import MIN_HEIGHT, prepare_line


def test_short_lines_are_upscaled_twice():
    crop, factor = prepare_line(np.zeros((24, 200, 3), np.uint8))
    assert factor == 2 and crop.shape == (48, 400, 3)


def test_tall_lines_are_kept():
    image = np.zeros((MIN_HEIGHT, 200, 3), np.uint8)
    crop, factor = prepare_line(image)
    assert factor == 1 and crop is image
