"""Testes das regras de blocos e do baseline clássico."""

import numpy as np
from blocks import BlockParams, assemble_blocks
from classic import ClassicParams, _line_kernel, detect_lines
from pages.render import render_page

from leitorum_di.metrics.detection import detection_counts, precision_recall_f1


def _line(x0, y0, x1, y1):
    return {"bbox": [x0, y0, x1, y1], "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}


def test_blocks_from_simple_layout():
    lines = [
        _line(300, 100, 900, 160),  # título (mais alto)
        _line(200, 250, 1100, 290),
        _line(200, 300, 1100, 340),
        _line(200, 450, 1100, 490),  # salto grande: novo parágrafo
        _line(200, 500, 900, 540),
        _line(20, 300, 120, 330),  # nota de margem
    ]
    ink = np.zeros((1200, 1240), np.uint8)
    ink[700:900, 300:700] = 255  # tinta fora das linhas: caixa gráfica
    blocks = assemble_blocks(lines, ink, BlockParams())
    types = sorted(b["type"] for b in blocks)
    assert types == ["graphic_box", "margin_note", "paragraph", "paragraph", "title"]
    paragraphs = sorted((b for b in blocks if b["type"] == "paragraph"), key=lambda b: b["bbox"][1])
    assert paragraphs[0]["bbox"] == [200, 250, 1100, 340]
    assert paragraphs[1]["bbox"] == [200, 450, 1100, 540]
    graphic = next(b for b in blocks if b["type"] == "graphic_box")
    gx0, gy0, gx1, gy1 = graphic["bbox"]
    assert gx0 <= 310 and gy0 <= 710 and gx1 >= 690 and gy1 >= 890


def test_blocks_empty_and_vertical_note():
    assert assemble_blocks([], None, BlockParams()) == []
    lines = [_line(200, 200, 1000, 240), _line(200, 250, 1000, 290), _line(40, 200, 80, 500)]
    types = sorted(b["type"] for b in assemble_blocks(lines, None, BlockParams()))
    assert "margin_note" in types


def test_line_kernel_is_a_segment():
    kernel = _line_kernel(21, 0.0)
    assert kernel.sum() == 21 and kernel.shape[0] == kernel.shape[1]
    assert _line_kernel(21, 90.0).sum() == 21


def test_classic_detects_most_lines_on_clean_page(fonts):
    image, truth = render_page(555, fonts)
    bgr = np.asarray(image)[:, :, ::-1].copy()
    lines, mask, scale = detect_lines(bgr, ClassicParams(offset=30))
    assert scale == 1.0 and mask.shape == bgr.shape[:2]
    result = precision_recall_f1(
        detection_counts([ln.bbox for ln in truth.lines], [ln["bbox"] for ln in lines])
    )
    assert result["recall"] >= 0.6
