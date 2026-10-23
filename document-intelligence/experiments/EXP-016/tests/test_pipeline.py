"""Regra de ampliação de linha do pipeline (EXP-016), com imagens fictícias."""

import numpy as np
from pipeline import (
    MIN_HEIGHT,
    batch_input,
    ctc_greedy,
    median_height,
    normalize_line,
    prepare_line,
    rec_input,
    scale_factor,
    to_original,
)


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


def test_rec_input_keeps_ratio_and_adds_right_margin():
    tensor = rec_input(np.full((24, 240, 3), 255, np.uint8), extra=640)
    assert tensor.shape[2] == 48
    assert tensor.shape[3] == 1120  # 480 de texto + 640 de margem, múltiplo de 32
    assert float(tensor[0, 0, 0, 479]) == 1.0 and float(tensor[0, 0, 0, 480]) == 0.0


def test_ctc_greedy_collapses_repeats_and_blanks():
    chars = ["blank", "a", "b", " "]
    probs = np.zeros((6, 4), np.float32)
    for position, token in enumerate([1, 1, 0, 1, 3, 2]):
        probs[position, token] = 0.9
    text, confidence = ctc_greedy(probs, chars)
    assert text == "aa b"
    assert abs(confidence - 0.9) < 1e-6


def test_batch_input_pads_every_line_to_the_widest_plus_margin():
    short = normalize_line(np.full((48, 100, 3), 255, np.uint8))
    long = normalize_line(np.full((48, 300, 3), 255, np.uint8))
    tensor = batch_input([short, long], extra=640)
    assert tensor.shape == (2, 3, 48, 960)  # 300 + 640, múltiplo de 32
    assert float(tensor[0, 0, 0, 99]) == 1.0 and float(tensor[0, 0, 0, 100]) == 0.0
    assert float(tensor[1, 0, 0, 299]) == 1.0 and float(tensor[1, 0, 0, 300]) == 0.0


def test_single_line_input_matches_exp015():
    image = np.random.default_rng(0).integers(0, 255, (30, 200, 3), dtype=np.uint8)
    tensor = rec_input(image)
    assert tensor.shape == (1, 3, 48, 960)  # ceil(48 * 200 / 30) = 320; 320 + 640
    assert np.allclose(tensor[0, :, :, :320], normalize_line(image))
