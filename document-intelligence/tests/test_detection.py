"""Testes das métricas de detecção com valores calculados à mão."""

import pytest

from leitorum_di.metrics.detection import (
    average_precision,
    detection_counts,
    match_detections,
    mean_average_precision,
    precision_recall_f1,
)

A = [0, 0, 10, 10]
B = [20, 0, 30, 10]
A_SHIFT_2 = [2, 0, 12, 10]  # IoU com A = 80 / 120 = 2/3
A_SHIFT_5 = [5, 0, 15, 10]  # IoU com A = 50 / 150 = 1/3


def test_perfect_match():
    assert match_detections([A, B], [B, A]) == [(0, 1, 1.0), (1, 0, 1.0)]
    assert precision_recall_f1(detection_counts([A, B], [A, B])) == {
        "tp": 2, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0, "mean_iou": 1.0,
    }  # fmt: skip


def test_threshold_and_partial_overlap():
    counts = detection_counts([A, B], [A_SHIFT_2, A_SHIFT_5], threshold=0.5)
    result = precision_recall_f1(counts)
    assert (result["tp"], result["fp"], result["fn"]) == (1, 1, 1)
    assert result["precision"] == result["recall"] == result["f1"] == 0.5
    assert result["mean_iou"] == pytest.approx(2 / 3)
    assert detection_counts([A], [A_SHIFT_5], threshold=0.3)["tp"] == 1


def test_greedy_matching_is_one_to_one():
    # Duas predições sobre a mesma verdade: só a de maior IoU casa.
    assert match_detections([A], [A_SHIFT_5, A_SHIFT_2]) == [(0, 1, pytest.approx(2 / 3))]


def test_empty_cases():
    assert precision_recall_f1(detection_counts([], [])) == {
        "tp": 0, "fp": 0, "fn": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0, "mean_iou": 0.0,
    }  # fmt: skip
    only_fp = precision_recall_f1(detection_counts([], [A]))
    assert only_fp["precision"] == 0.0 and only_fp["recall"] == 1.0 and only_fp["f1"] == 0.0
    only_fn = precision_recall_f1(detection_counts([A], []))
    assert only_fn["precision"] == 0.0 and only_fn["recall"] == 0.0


def test_custom_iou_function():
    always = lambda a, b: 0.9  # noqa: E731
    assert detection_counts([A, B], [A], iou=always)["tp"] == 1


def test_average_precision_perfect_and_undefined():
    assert average_precision([([A, B], [(A, 0.9), (B, 0.8)])]) == pytest.approx(1.0)
    assert average_precision([([], [(A, 0.9)])]) is None


def test_average_precision_known_value():
    # 2 verdades; ranking: acerto (0.9), erro (0.8), acerto (0.7).
    # Precisões: 1, 1/2, 2/3; revocações: 0.5, 0.5, 1.0. Envelope: 1, 2/3, 2/3.
    # 101 pontos: recall 0–0.5 (51 pontos) → 1; recall 0.51–1.0 (50 pontos) → 2/3.
    images = [([A, B], [(A, 0.9), ([50, 50, 60, 60], 0.8), (B, 0.7)])]
    assert average_precision(images) == pytest.approx((51 * 1 + 50 * 2 / 3) / 101)


def test_average_precision_across_images_and_missed_truth():
    images = [([A], [(A, 0.9)]), ([B], [])]
    # 1 acerto de 2 verdades: precisão 1 até recall 0.5 → 51 pontos de 101.
    assert average_precision(images) == pytest.approx(51 / 101)


def test_mean_average_precision_ignores_undefined():
    assert mean_average_precision({"a": 1.0, "b": 0.5, "c": None}) == 0.75
    assert mean_average_precision({"a": None}) is None
