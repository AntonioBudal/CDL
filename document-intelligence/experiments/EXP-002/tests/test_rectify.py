"""Testes da retificação: ordenação de cantos, homografia e ida e volta de coordenadas."""

import cv2
import numpy as np
from rectify import (
    corner_error,
    find_page_contour,
    map_points,
    order_quad,
    quad_from_region,
    rectify,
)


def test_order_quad_and_corner_error():
    quad = [[90, 100], [10, 110], [100, 10], [0, 0]]
    ordered = order_quad(quad)
    assert ordered.tolist() == [[0, 0], [100, 10], [90, 100], [10, 110]]
    assert corner_error(quad, ordered) == 0.0
    assert (
        corner_error([[0, 0], [10, 0], [10, 10], [0, 10]], [[3, 4], [13, 4], [13, 14], [3, 14]])
        == 5.0
    )


def test_quad_from_region_picks_extreme_points():
    region = [[5, 5], [95, 8], [50, 50], [90, 97], [8, 92], [40, 20]]
    assert quad_from_region(region).tolist() == [[5, 5], [95, 8], [90, 97], [8, 92]]


def test_find_page_and_rectify_roundtrip():
    image = np.full((600, 500, 3), 60, np.uint8)
    truth = np.array([[80, 60], [430, 90], [410, 540], [60, 500]], dtype=np.float64)
    cv2.fillPoly(image, [truth.astype(np.int32)], (245, 245, 240))
    quad = find_page_contour(image)
    assert quad is not None and corner_error(quad, truth) < 6
    warped, homography = rectify(image, quad)
    assert warped.mean() > 220  # só papel na imagem retificada
    mapped = map_points(truth, homography)
    height, width = warped.shape[:2]
    assert np.abs(mapped - [[0, 0], [width, 0], [width, height], [0, height]]).max() < 8
    back = map_points(mapped, np.linalg.inv(homography))
    assert np.abs(back - truth).max() < 1e-6


def test_find_page_returns_none_without_page():
    assert find_page_contour(np.full((300, 300, 3), 40, np.uint8)) is None
