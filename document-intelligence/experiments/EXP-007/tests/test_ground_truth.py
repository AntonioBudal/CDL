"""Verdade de chão do GNHK e do BRESSAY, só com anotações e imagens fictícias."""

import numpy as np
import pytest
from bressay import locate, page_truth, scale_truth
from gnhk import is_special, lines_from_words


def word(line, x0, y0, x1, y1, kind="H", text="palavra"):
    polygon = {"x0": x0, "y0": y0, "x1": x1, "y1": y0, "x2": x1, "y2": y1, "x3": x0, "y3": y1}
    return {"text": text, "polygon": polygon, "line_idx": line, "type": kind}


def test_words_are_grouped_by_line_index():
    words = [word(0, 10, 10, 60, 30), word(1, 10, 50, 80, 70), word(0, 70, 12, 150, 32)]
    lines, ignore = lines_from_words(words)
    assert [line["id"] for line in lines] == ["l000", "l001"]
    assert lines[0]["bbox"] == [10, 10, 150, 32]
    assert lines[0]["words"] == 2
    assert ignore == []
    assert "text" not in lines[0]


def test_tilted_line_gets_a_tight_rotated_outline():
    words = []
    for step in range(5):
        x, y = 100 + step * 100, 100 + step * 50
        polygon = {"x0": x, "y0": y, "x1": x + 80, "y1": y + 40, "x2": x + 70, "y2": y + 60,
                   "x3": x - 10, "y3": y + 20}  # fmt: skip
        words.append({"text": "a", "polygon": polygon, "line_idx": 3, "type": "H"})
    (line,), _ = lines_from_words(words)
    xs = [p[0] for p in line["polygon"]]
    ys = [p[1] for p in line["polygon"]]
    box_area = (line["bbox"][2] - line["bbox"][0]) * (line["bbox"][3] - line["bbox"][1])
    area = 0.5 * abs(sum(xs[i] * ys[(i + 1) % 4] - xs[(i + 1) % 4] * ys[i] for i in range(4)))
    assert len(line["polygon"]) == 4
    assert area < 0.3 * box_area  # o contorno acompanha a inclinação; a caixa não
    signed = sum(xs[i] * ys[(i + 1) % 4] - xs[(i + 1) % 4] * ys[i] for i in range(4))
    assert signed > 0  # sentido horário, como pede o LDF 2.0


def test_printed_or_special_only_lines_become_ignore_regions():
    words = [
        word(0, 10, 10, 60, 30, kind="P"),
        word(1, 10, 50, 80, 70, text="%NA%"),
        word(2, 10, 90, 80, 110, text="%math%"),
        word(3, 10, 130, 80, 150),
        word(3, 90, 130, 150, 150, kind="P"),
    ]
    lines, ignore = lines_from_words(words)
    assert [line["id"] for line in lines] == ["l003"]
    assert lines[0]["bbox"] == [10, 130, 150, 150]  # a linha mista mantém a extensão inteira
    assert ignore == [[10, 10, 60, 30], [10, 50, 80, 70], [10, 90, 80, 110]]


def test_photo_without_usable_lines_and_scaling():
    assert lines_from_words([]) == ([], [])
    lines, _ = lines_from_words([word(0, 100, 200, 300, 260)], scale=0.5)
    assert lines[0]["bbox"] == [50, 100, 150, 130]


@pytest.mark.parametrize(
    ("text", "expected"),
    [("%NA%", True), ("%SC%", True), ("%math%", True), ("%", True), ("50%", False), ("a", False)],
)
def test_special_marks(text, expected):
    assert is_special(text) is expected


@pytest.fixture
def essay():
    """Página fictícia com ruído (para a correlação ser única) e recortes exatos."""
    rng = np.random.default_rng(7)
    page = rng.integers(0, 255, size=(300, 400), dtype=np.uint8)
    paragraphs = {"p-01": page[0:120, 5:395].copy(), "p-02": page[130:290, 5:395].copy()}
    lines = {
        "p-01-01": page[0:40, 30:395].copy(),
        "p-01-02": page[42:80, 5:395].copy(),
        "p-01-03": page[82:120, 5:200].copy(),
        "p-02-01": page[130:170, 30:395].copy(),
    }
    return page, paragraphs, lines


def test_crops_are_located_exactly(essay):
    page, paragraphs, lines = essay
    truth = page_truth(page, paragraphs, lines)
    assert truth["missing"] == []
    assert [b["bbox"] for b in truth["blocks"]] == [[5, 0, 395, 120], [5, 130, 395, 290]]
    assert [ln["bbox"] for ln in truth["lines"]] == [
        [30, 0, 395, 40],
        [5, 42, 395, 80],
        [5, 82, 200, 120],
        [30, 130, 395, 170],
    ]
    assert truth["blocks"][0]["line_ids"] == ["l001", "l002", "l003"]
    assert [ln["block_id"] for ln in truth["lines"]] == ["b001", "b001", "b001", "b002"]
    assert truth["reading_order"] == ["b001", "b002"]
    assert all(b["type"] == "paragraph" for b in truth["blocks"])


def test_crop_that_is_not_in_the_page_is_reported(essay):
    page, paragraphs, lines = essay
    rng = np.random.default_rng(99)
    lines["p-01-04"] = rng.integers(0, 255, size=(30, 100), dtype=np.uint8)
    paragraphs["p-03"] = rng.integers(0, 255, size=(50, 100), dtype=np.uint8)
    lines["p-09-01"] = page[200:230, 5:100].copy()  # linha de parágrafo que não existe
    truth = page_truth(page, paragraphs, lines)
    assert truth["missing"] == ["p-01-04", "p-03", "p-09-01"]
    assert len(truth["blocks"]) == 2


def test_uniform_or_oversized_crop_is_not_located(essay):
    page, _, _ = essay
    assert locate(page, np.full((20, 50), 255, np.uint8)) is None
    assert locate(page, np.zeros((500, 500), np.uint8)) is None


def test_repeated_line_is_found_inside_its_own_paragraph():
    rng = np.random.default_rng(3)
    page = rng.integers(0, 255, size=(300, 200), dtype=np.uint8)
    page[200:230, 10:150] = page[20:50, 10:150]  # a mesma "linha" em dois parágrafos
    paragraphs = {"p-01": page[0:100, 0:200].copy(), "p-02": page[150:300, 0:200].copy()}
    lines = {"p-02-01": page[200:230, 10:150].copy()}
    truth = page_truth(page, paragraphs, lines)
    assert truth["lines"][0]["bbox"] == [10, 200, 150, 230]
    assert truth["lines"][0]["block_id"] == "b002"


def test_single_line_paragraph_and_scaling(essay):
    page, paragraphs, lines = essay
    truth = page_truth(page, paragraphs, lines)
    assert truth["blocks"][1]["line_ids"] == ["l004"]
    big = scale_truth(truth, 3)
    assert big["blocks"][0]["bbox"] == [15, 0, 1185, 360]
    assert big["lines"][0]["bbox"] == [90, 0, 1185, 120]
    assert big["lines"][0]["polygon"][2] == [1185, 120]
    assert big["reading_order"] == truth["reading_order"]
    assert truth["lines"][0]["bbox"] == [30, 0, 395, 40]  # o original não muda
