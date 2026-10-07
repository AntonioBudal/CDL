"""Testes das métricas de ordem de leitura com valores calculados à mão."""

import pytest

from leitorum_di.metrics.ordering import (
    kendall_tau,
    order_accuracy,
    order_edit_counts,
    out_of_order,
)

TRUTH = ["a", "b", "c", "d"]


def test_identical_and_empty():
    assert order_accuracy(TRUTH, TRUTH) == 1.0
    assert order_accuracy([], []) == 1.0
    assert kendall_tau(TRUTH, TRUTH) == 1.0
    assert out_of_order(TRUTH, TRUTH) == []


def test_swap_of_neighbours():
    predicted = ["a", "c", "b", "d"]
    # troca de vizinhos = 2 substituições em 4 posições
    assert order_edit_counts(predicted, TRUTH) == (2, 4)
    assert order_accuracy(predicted, TRUTH) == 0.5
    # 6 pares, 1 discordante: (5 − 1) / 6
    assert kendall_tau(predicted, TRUTH) == pytest.approx(4 / 6)
    assert len(out_of_order(predicted, TRUTH)) == 1


def test_one_element_moved_to_the_end():
    predicted = ["b", "c", "d", "a"]
    # remover "a" do início e inserir no fim: 2 edições
    assert order_accuracy(predicted, TRUTH) == 0.5
    assert kendall_tau(predicted, TRUTH) == pytest.approx(0.0)
    assert out_of_order(predicted, TRUTH) == ["a"]


def test_reversed_order():
    predicted = list(reversed(TRUTH))
    assert kendall_tau(predicted, TRUTH) == -1.0
    assert order_accuracy(predicted, TRUTH) == 0.0


def test_missing_and_extra_elements():
    assert order_accuracy(["a", "b", "c"], TRUTH) == 0.75  # falta 1 de 4
    assert order_accuracy(["a", "x", "b", "c", "d"], TRUTH) == pytest.approx(0.8)  # sobra 1 em 5
    assert order_accuracy([], TRUTH) == 0.0
    assert kendall_tau(["a", "x", "b"], TRUTH) == 1.0  # só os elementos em comum contam
    assert kendall_tau(["a"], TRUTH) is None
    assert out_of_order(["a", "b", "c"], TRUTH) == ["d"]
