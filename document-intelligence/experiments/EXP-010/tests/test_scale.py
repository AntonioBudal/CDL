"""Ampliação do recorte (EXP-010), com imagem fictícia."""

import numpy as np
from adapters.ppocr_rec import scaled


def test_scale_one_keeps_the_image():
    image = np.zeros((20, 100, 3), np.uint8)
    assert scaled(image, 1) is image


def test_scale_multiplies_both_sides():
    image = np.zeros((20, 100, 3), np.uint8)
    assert scaled(image, 3).shape == (60, 300, 3)
    assert scaled(image, 2).shape == (40, 200, 3)
