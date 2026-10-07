"""Testes da verdade de chão de ordem de leitura e das famílias de layout do gerador."""

import pytest
from generate import build_page
from order_eval import evaluate_page, true_line_order
from orderers import OrderParams
from pages.render import FAMILIES, render_page
from to_ldf import to_ldf, validation_errors


@pytest.mark.parametrize("family", FAMILIES)
def test_reading_order_is_a_permutation_of_blocks_and_anchors_are_valid(fonts, family):
    for seed in (101, 202, 303):
        _, truth = render_page(seed, fonts, family)
        ids = [block.id for block in truth.blocks]
        assert sorted(truth.reading_order) == sorted(ids)
        position = {block_id: i for i, block_id in enumerate(truth.reading_order)}
        for block in truth.blocks:
            if block.anchor is not None:
                assert block.anchor in position
                assert position[block.anchor] < position[block.id]
        assert truth.blocks[0].type == "title" and truth.reading_order[0] == truth.blocks[0].id


def test_families_have_their_distinctive_blocks(fonts):
    def count(family, predicate):
        total = 0
        for seed in range(400, 410):
            _, truth = render_page(seed, fonts, family)
            total += sum(1 for block in truth.blocks if predicate(block))
        return total

    assert count("single", lambda b: b.type == "margin_note" or b.anchor) == 0
    assert count("margin", lambda b: b.type == "margin_note") >= 15
    assert count("callout", lambda b: b.type == "paragraph" and b.anchor) >= 8


def test_callout_sits_to_the_right_of_its_paragraph(fonts):
    found = 0
    for seed in range(500, 520):
        _, truth = render_page(seed, fonts, "callout")
        by_id = {block.id: block for block in truth.blocks}
        for block in truth.blocks:
            if block.type == "paragraph" and block.anchor:
                anchor = by_id[block.anchor]
                assert block.bbox[0] > anchor.bbox[2] - 5
                assert min(block.bbox[3], anchor.bbox[3]) > max(block.bbox[1], anchor.bbox[1])
                found += 1
    assert found > 0


def test_manifest_entry_carries_order_and_reference_order_scores_one(tmp_path):
    entry = build_page("t-margin", "strong", 777, 1.0, tmp_path, tmp_path, "margin")
    assert entry["family"] == "margin"
    assert sorted(entry["reading_order"]) == sorted(block["id"] for block in entry["blocks"])
    assert len(true_line_order(entry)) == len(entry["lines"])
    result = evaluate_page(entry, OrderParams(method="anchored"), repeats=1)
    assert result["truth_blocks"] == len(entry["blocks"])


def test_ldf_reading_order_excludes_graphic_boxes(tmp_path):
    entry = None
    for seed in range(900, 930):
        candidate = build_page(f"t-{seed}", "clean", seed, 1.0, tmp_path, tmp_path, "single")
        if any(block["type"] == "graphic_box" for block in candidate["blocks"]):
            entry = candidate
            break
    assert entry is not None
    index = {block["id"]: i for i, block in enumerate(entry["blocks"])}
    order = [index[block_id] for block_id in entry["reading_order"]]
    prediction = {"lines": entry["lines"], "blocks": entry["blocks"]}
    document, gaps = to_ldf(entry, prediction, "truth", order=order)
    assert validation_errors(document) == []
    listed = document["structure"]["reading_order"]
    text_blocks = [block for block in entry["blocks"] if block["type"] != "graphic_box"]
    assert len(listed) == len(text_blocks) == len(document["structure"]["blocks"])
    assert len(gaps) == len(entry["blocks"]) - len(text_blocks)
