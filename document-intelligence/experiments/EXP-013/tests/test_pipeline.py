"""Regra de ampliação de linha do pipeline (EXP-013), com imagens fictícias."""

import numpy as np
from pipeline import MIN_HEIGHT, median_height, prepare_line, scale_factor, to_original


def test_short_lines_are_upscaled_twice():
    crop, factor = prepare_line(np.zeros((24, 200, 3), np.uint8))
    assert factor == 2 and crop.shape == (48, 400, 3)


def test_tall_lines_are_kept():
    image = np.zeros((MIN_HEIGHT, 200, 3), np.uint8)
    crop, factor = prepare_line(image)
    assert factor == 1 and crop is image


def test_scale_factor_rounds_and_clamps():
    assert scale_factor(24, 64) == 3
    assert scale_factor(60, 64) == 1
    assert scale_factor(10, 64) == 4
    assert scale_factor(None, 64) == 1
    assert scale_factor(24, None) == 1


def test_median_height_and_coordinates_back_to_the_original():
    lines = [{"bbox": [0, 0, 10, h]} for h in (20, 24, 30)]
    assert median_height(lines) == 24
    assert median_height([]) is None
    line = {"bbox": [30, 60, 90, 120], "polygon": [[30, 60], [90, 60], [90, 120], [30, 120]]}
    back = to_original(line, 3)
    assert back["bbox"] == [10, 20, 30, 40]
    assert back["polygon"][2] == [30.0, 40.0]
    assert to_original(line, 1) == line
