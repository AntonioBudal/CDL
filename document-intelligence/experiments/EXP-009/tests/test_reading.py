"""Recorte, ordem de leitura e métricas do EXP-009, só com dados fictícios."""

import numpy as np
import pytest
from crop import crop_line, line_quad, reading_order
from evaluate import align_errors, char_class, line_metrics, page_metrics, page_text


def test_line_quad_orders_corners_for_reading():
    quad = line_quad([[300, 160], [100, 100], [110, 70], [310, 130]])
    assert quad[0][0] < quad[1][0] and quad[3][0] < quad[2][0]
    assert quad[0][1] < quad[3][1] and quad[1][1] < quad[2][1]


def test_crop_of_a_tilted_line_is_horizontal():
    image = np.full((400, 600, 3), 255, np.uint8)
    polygon = [[100, 200], [500, 100], [510, 140], [110, 240]]
    crop = crop_line(image, polygon)
    assert crop.shape[1] > 3 * crop.shape[0]
    assert crop.shape[2] == 3


def test_reading_order_rows_then_left_to_right():
    lines = [
        {"bbox": [400, 100, 600, 140]},
        {"bbox": [100, 300, 500, 340]},
        {"bbox": [100, 104, 380, 142]},
    ]
    assert reading_order(lines) == [2, 0, 1]
    assert reading_order([]) == []


@pytest.mark.parametrize(
    ("char", "kind"),
    [
        ("a", "letra"),
        ("ç", "letra acentuada"),
        ("Ã", "letra acentuada"),
        ("7", "dígito"),
        (",", "pontuação"),
        (" ", "espaço"),
        ("+", "outro"),
    ],  # fmt: skip
)
def test_char_classes(char, kind):
    assert char_class(char) == kind


def test_alignment_attributes_errors_to_the_reference_class():
    totals, errors, insertions = align_errors("ação", "acao!")
    assert totals == {"letra": 2, "letra acentuada": 2}
    assert errors == {"letra acentuada": 2}
    assert insertions == 1


def test_line_metrics_match_the_exp001_definition():
    refs = {"a": "casa amarela", "b": "pão"}
    preds = {"a": "casa amarela", "b": "pao"}
    result = line_metrics(refs, preds)
    assert result["cer_micro"] == pytest.approx(1 / 15)
    assert result["wer_micro"] == pytest.approx(1 / 3)
    assert result["lines_with_cer_below_10pct"] == 1
    assert result["cer_by_class"]["letra acentuada"]["cer"] == 1.0
    assert line_metrics({"a": "abc"}, {})["cer_micro"] == 1.0


def test_page_normalization_and_metrics():
    assert page_text("Uma  linha\n-- outra @@ linha  ") == "Uma linha outra linha"
    result = page_metrics({"p": "Uma linha\noutra linha"}, {"p": "Uma linha outra linha"})
    assert result["cer_micro"] == 0.0
    assert page_metrics({"p": "abcd"}, {})["cer_micro"] == 1.0
