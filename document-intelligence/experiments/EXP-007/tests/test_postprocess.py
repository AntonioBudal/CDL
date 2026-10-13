"""Testes do ponto de operação dos blocos detectados."""

from postprocess import BlockFilter, filter_blocks


def _block(bbox, score, kind="paragraph"):
    return {"type": kind, "bbox": bbox, "score": score}


def test_threshold_nms_and_containment():
    blocks = [
        _block([0, 0, 100, 100], 0.9),
        _block([5, 5, 105, 105], 0.8),  # duplicata por IoU alto
        _block([10, 10, 40, 40], 0.7),  # contida na primeira
        _block([200, 0, 300, 100], 0.6),
        _block([400, 0, 500, 100], 0.2),  # abaixo do limiar
    ]
    kept = filter_blocks(blocks, BlockFilter(min_score=0.5, nms_iou=0.5, containment=0.8))
    assert [b["bbox"] for b in kept] == [[0, 0, 100, 100], [200, 0, 300, 100]]


def test_containment_can_be_disabled_and_scores_default_to_one():
    blocks = [_block([0, 0, 100, 100], 0.9), _block([10, 10, 40, 40], 0.7)]
    assert len(filter_blocks(blocks, BlockFilter(0.5, 0.5, 1.01))) == 2
    assert filter_blocks([{"type": "title", "bbox": [0, 0, 5, 5]}], BlockFilter()) != []
    assert filter_blocks([], BlockFilter()) == []
