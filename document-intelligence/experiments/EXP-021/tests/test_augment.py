"""Degradação de linha do EXP-021, com uma linha fictícia."""

import cv2
import numpy as np
from augment import degrade_line


def fake_line() -> np.ndarray:
    image = np.full((40, 300, 3), 255, np.uint8)
    cv2.putText(image, "Livro de Teste", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 30, 30), 2)
    return image


def test_keeps_shape_and_type():
    out = degrade_line(fake_line(), np.random.default_rng(0))
    assert out.shape == (40, 300, 3) and out.dtype == np.uint8


def test_is_reproducible_and_changes_the_image():
    line = fake_line()
    a = degrade_line(line, np.random.default_rng(5))
    b = degrade_line(line, np.random.default_rng(5))
    c = degrade_line(line, np.random.default_rng(6))
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    assert np.abs(a.astype(int) - line.astype(int)).mean() > 1


def test_text_stays_darker_than_background():
    out = degrade_line(fake_line(), np.random.default_rng(1)).astype(float)
    assert out[:, :, 0].min() < out[:, :, 0].mean() - 40
