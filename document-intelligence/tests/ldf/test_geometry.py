"""Geometria do LDF: envelope, sentido dos vértices, recorte e homografia."""

import pytest

from leitorum_di.contracts.ldf import geometry as g

SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]


def test_envelope_of_a_tilted_polygon():
    assert g.envelope([[2, 5], [8, 1], [9, 4], [3, 8]]) == [2, 1, 9, 8]


def test_clockwise_has_positive_area_with_y_down():
    assert g.signed_area(SQUARE) == 100
    assert g.signed_area(SQUARE[::-1]) == -100
    assert g.clockwise(SQUARE[::-1]) == [[float(x), float(y)] for x, y in SQUARE]


def test_bbox_polygon_is_clockwise_and_has_the_same_envelope():
    polygon = g.bbox_polygon([1, 2, 5, 9])
    assert g.signed_area(polygon) > 0
    assert g.envelope(polygon) == [1, 2, 5, 9]


def test_clip_keeps_inner_polygon_and_cuts_the_outer_part():
    assert g.clip_polygon(SQUARE, 100, 100) == [[float(x), float(y)] for x, y in SQUARE]
    clipped = g.clip_polygon([[-5, 2], [5, 2], [5, 8], [-5, 8]], 100, 100)
    assert g.envelope(clipped) == [0, 2, 5, 8]
    assert g.signed_area(clipped) == 30


def test_clip_of_polygon_outside_the_image_is_empty():
    assert g.clip_polygon([[200, 200], [210, 200], [210, 210]], 100, 100) == []


def test_homography_maps_the_four_corners():
    source = [[51.8, 94.2], [1319.8, 14.1], [1341.9, 1993.3], [184.8, 1845.6]]
    target = [[0, 0], [1240, 0], [1240, 1754], [0, 1754]]
    matrix = g.homography_from_quads(source, target)
    for point, expected in zip(source, target, strict=True):
        assert g.apply_homography(matrix, point) == pytest.approx(expected, abs=1e-6)


def test_round_trip_between_photo_and_rectified_image():
    rectification = {
        "homography": g.homography_from_quads(
            [[40, 60], [900, 20], [950, 1300], [10, 1250]],
            [[0, 0], [800, 0], [800, 1200], [0, 1200]],
        )
    }
    for point in ([100, 200], [500.5, 640.25], [880, 1200]):
        there = g.to_rectified(rectification, point)
        assert g.to_source(rectification, there) == pytest.approx(point, abs=1e-6)


def test_identity_and_singular_cases():
    identity = g.homography_from_quads(SQUARE, SQUARE)
    assert g.apply_homography(identity, [3, 4]) == pytest.approx([3, 4])
    with pytest.raises(ValueError):
        g.homography_from_quads([[0, 0], [1, 1], [2, 2], [3, 3]], SQUARE)
    with pytest.raises(ValueError):
        g.invert([[1, 2, 3], [2, 4, 6], [0, 0, 1]])
    with pytest.raises(ValueError):
        g.homography_from_quads(SQUARE[:3], SQUARE[:3])
