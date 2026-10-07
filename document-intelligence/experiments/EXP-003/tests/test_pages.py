"""Testes do gerador de páginas: geometria da verdade de chão e degradações que a acompanham."""

import io
import random

import numpy as np
import pytest
from generate import build_page
from pages import content
from pages.degrade import PARAMS, degrade, densify, make_transform, transform_polygon
from pages.render import ALPHA_THRESHOLD, render_page
from PIL import Image


def test_content_is_deterministic_and_covers_portuguese_alphabet():
    rng_a, rng_b = random.Random(7), random.Random(7)
    assert [content.sentence(rng_a) for _ in range(20)] == [
        content.sentence(rng_b) for _ in range(20)
    ]
    rng = random.Random(1)
    text = " ".join(
        content.title(rng).upper() + " " + content.sentence(rng) + " " + content.margin_note(rng)
        for _ in range(600)
    )
    assert not set(content.REQUIRED_CHARS) - set(text)


def test_render_is_deterministic(fonts):
    image_a, truth_a = render_page(123, fonts)
    image_b, truth_b = render_page(123, fonts)
    assert np.array_equal(np.asarray(image_a), np.asarray(image_b))
    assert truth_a == truth_b


def test_line_boxes_contain_ink_and_blocks_reference_lines(fonts):
    image, truth = render_page(321, fonts)
    pixels = np.asarray(image.convert("L"), dtype=np.int16)
    assert len(truth.lines) >= 8
    types = {block.type for block in truth.blocks}
    assert {"title", "paragraph"} <= types
    line_ids = {line.id for line in truth.lines}
    for block in truth.blocks:
        assert set(block.line_ids) <= line_ids
    for line in truth.lines:
        x0, y0, x1, y1 = line.bbox
        assert x1 > x0 and y1 > y0
        crop = pixels[y0:y1, x0:x1]
        assert crop.min() < 255 - ALPHA_THRESHOLD, f"linha {line.id} sem tinta dentro da bbox"


def test_degrade_geometry_follows_image():
    """Marcadores pretos em posições conhecidas devem cair onde a transformação dos pontos diz."""
    page = Image.new("RGB", (1240, 1754), (250, 250, 250))
    points = np.array([[150, 150], [1100, 200], [600, 900], [200, 1600], [1080, 1650]], dtype=float)
    pixels = np.asarray(page).copy()
    for x, y in points.astype(int):
        pixels[y - 6 : y + 7, x - 6 : x + 7] = 0
    page = Image.fromarray(pixels)
    result = degrade(page, "strong", seed=99)
    output = np.asarray(Image.open(io.BytesIO(result.image_bytes)).convert("L"))
    expected = result.transform.apply_points(points)
    for ex, ey in expected:
        window = output[int(ey) - 20 : int(ey) + 21, int(ex) - 20 : int(ex) + 21]
        ys, xs = np.nonzero(window < 90)
        assert xs.size > 0, "marcador não encontrado perto da posição esperada"
        cx, cy = xs.mean() + int(ex) - 20, ys.mean() + int(ey) - 20
        assert abs(cx - ex) < 3 and abs(cy - ey) < 3


def test_clean_level_is_identity_and_transform_polygon():
    page = Image.new("RGB", (100, 80), (255, 255, 255))
    result = degrade(page, "clean", seed=1)
    assert result.transform is None and result.extension == ".png"
    bbox, polygon = transform_polygon([[10, 10], [50, 10], [50, 30], [10, 30]], None)
    assert bbox == [10, 10, 50, 30] and polygon == [[10, 10], [50, 10], [50, 30], [10, 30]]


def test_densify_keeps_vertices_and_adds_points():
    square = np.array([[0, 0], [16, 0], [16, 16], [0, 16]], dtype=float)
    dense = densify(square, step=8)
    assert len(dense) == 8
    assert {tuple(p) for p in square} <= {tuple(p) for p in dense}


def test_transform_is_seeded():
    a = make_transform((1240, 1754), PARAMS["light"], random.Random(5))
    b = make_transform((1240, 1754), PARAMS["light"], random.Random(5))
    assert a == b


@pytest.mark.parametrize("level", ["clean", "strong"])
def test_build_page_manifest_entry(tmp_path, level):
    entry = build_page(f"t-{level}", level, 4242, 1.0, tmp_path, tmp_path)
    assert (tmp_path / entry["image"]).is_file()
    assert entry["lines"] and entry["blocks"]
    for line in entry["lines"]:
        x0, y0, x1, y1 = line["bbox"]
        assert 0 <= x0 < x1 <= entry["width"] + 2 and 0 <= y0 < y1 <= entry["height"] + 2
        assert len(line["polygon"]) >= 4
    assert len(entry["page_corners"]) == 4
