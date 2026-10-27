"""Associação foto → página e sorteio das páginas do EXP-022, com dados fictícios."""

import pytest
from prepare import pick
from score import assign


def test_assign_picks_lowest_cost_and_reports_margin():
    costs = {"a": {"p1": 0.2, "p2": 0.9}, "b": {"p1": 0.8, "p2": 0.3}}
    mapping, margins = assign(costs)
    assert mapping == {"a": "p1", "b": "p2"}
    assert margins["a"] == pytest.approx(0.7) and margins["b"] == pytest.approx(0.5)


def test_assign_refuses_two_photos_on_one_page():
    with pytest.raises(ValueError):
        assign({"a": {"p1": 0.2, "p2": 0.9}, "b": {"p1": 0.3, "p2": 0.8}})


def test_pick_is_stable_and_order_independent():
    ids = [f"{i:04d}-001" for i in range(50)]
    assert pick(ids, 5, "s") == pick(list(reversed(ids)), 5, "s")
    assert len(set(pick(ids, 15, "s"))) == 15
