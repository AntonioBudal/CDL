"""Testes dos ordenadores e da avaliação de ordem em layouts pequenos construídos à mão."""

import pytest
from order_eval import evaluate_page, summarize
from orderers import OrderParams, assign_lines, order_blocks, order_lines, page_skew


def _block(bid, kind, bbox, anchor=None):
    return {"id": bid, "type": kind, "bbox": bbox, "line_ids": [f"{bid}-l1"], "anchor": anchor}


def _page(blocks, order, family="single"):
    lines = []
    for block in blocks:
        x0, y0, x1, y1 = block["bbox"]
        lines.append(
            {
                "id": block["line_ids"][0],
                "block_id": block["id"],
                "bbox": [x0, y0, x1, y1],
                "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
            }
        )
    return {"id": "p", "level": "clean", "family": family, "blocks": blocks, "lines": lines,
            "reading_order": order}  # fmt: skip


SINGLE = _page(
    [
        _block("t", "title", [250, 100, 900, 150]),
        _block("p1", "paragraph", [200, 220, 1100, 400]),
        _block("p2", "paragraph", [200, 460, 1100, 640]),
    ],
    ["t", "p1", "p2"],
)
MARGIN = _page(
    [
        _block("t", "title", [250, 100, 900, 150]),
        _block("n1", "margin_note", [20, 230, 130, 270], anchor="p1"),
        _block("p1", "paragraph", [200, 220, 1100, 400]),
        _block("p2", "paragraph", [200, 460, 1100, 640]),
    ],
    ["t", "p1", "n1", "p2"],
    "margin",
)
CALLOUT = _page(
    [
        _block("t", "title", [250, 100, 900, 150]),
        _block("p1", "paragraph", [200, 220, 700, 400]),
        _block("c1", "paragraph", [780, 225, 1100, 380], anchor="p1"),
        _block("p2", "paragraph", [200, 460, 1100, 640]),
    ],
    ["t", "p1", "c1", "p2"],
    "callout",
)


def _accuracy(page, method, **kwargs):
    result = evaluate_page(page, OrderParams(method=method, **kwargs), repeats=1)
    distance, total = result["blocks_full"]
    return 1 - distance / total


@pytest.mark.parametrize("method", ["naive", "xycut", "anchored"])
def test_all_methods_solve_single_column(method):
    assert _accuracy(SINGLE, method) == 1.0


def test_margin_note_goes_after_its_paragraph_only_with_anchored():
    assert _accuracy(MARGIN, "anchored") == 1.0
    assert _accuracy(MARGIN, "xycut") < 1.0  # o corte XY lê a nota (à esquerda) antes do parágrafo
    assert _accuracy(MARGIN, "naive") < 1.0  # a nota começa um pouco abaixo do topo do parágrafo


def test_callout_beside_paragraph():
    assert _accuracy(CALLOUT, "anchored") == 1.0
    assert _accuracy(CALLOUT, "xycut") == 1.0


def test_line_order_and_assignment():
    lines = [
        {"bbox": [0, 100, 300, 130], "polygon": [[0, 100], [300, 100], [300, 130], [0, 130]]},
        {"bbox": [0, 20, 300, 50], "polygon": [[0, 20], [300, 20], [300, 50], [0, 50]]},
        {"bbox": [0, 60, 300, 90], "polygon": [[0, 60], [300, 60], [300, 90], [0, 90]]},
    ]
    assert order_lines(lines) == [1, 2, 0]
    blocks = [
        {"type": "paragraph", "bbox": [0, 0, 400, 95]},
        {"type": "paragraph", "bbox": [0, 96, 400, 200]},
    ]
    assert assign_lines(blocks, lines) == [1, 0, 0]
    assert assign_lines(blocks, [{"bbox": [900, 900, 950, 950]}]) == [None]
    assert page_skew(lines) == 0.0


def test_detected_layout_with_missing_and_extra_blocks():
    detected = {
        "blocks": [
            {"type": "title", "bbox": [250, 100, 900, 150]},
            {"type": "paragraph", "bbox": [200, 460, 1100, 640]},
            {"type": "paragraph", "bbox": [10, 900, 60, 950]},  # sobra
        ],
        "lines": [{"bbox": ln["bbox"], "polygon": ln["polygon"]} for ln in SINGLE["lines"]],
    }
    result = evaluate_page(SINGLE, OrderParams(method="naive"), detected, repeats=1)
    # verdade: t, p1, p2; previsto: t, p2, x2 → faltou p1 e sobrou um bloco: 2 edições em 3
    assert result["blocks_full"] == (2, 3)
    assert result["blocks_matched"] == (0, 2)  # entre os casados, a ordem está certa
    assert result["unmatched_predicted"] == 1 and result["unmatched_truth"] == 1
    summary = summarize([result])
    assert summary["blocks_accuracy"] == pytest.approx(1 / 3)
    assert summary["blocks_accuracy_matched"] == 1.0


def test_empty_blocks():
    assert order_blocks([], [], OrderParams()) == []
