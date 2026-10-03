"""Métricas de detecção sobre caixas: casamento por IoU, Precision/Recall/F1 e AP.

Funções puras, sem dependências externas. A função de IoU é injetável, para que o mesmo casamento
sirva a caixas alinhadas aos eixos (padrão) ou a polígonos.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from leitorum_di.metrics.base import calculate_iou

Box = Sequence[float]
IoUFunction = Callable[[Any, Any], float]


def match_detections(
    truths: Sequence[Any],
    predictions: Sequence[Any],
    threshold: float = 0.5,
    iou: IoUFunction = calculate_iou,
) -> list[tuple[int, int, float]]:
    """Casamento guloso um-para-um por IoU decrescente.

    Devolve ``(índice da verdade, índice da predição, IoU)`` para os pares com IoU ≥ ``threshold``.
    """
    candidates = []
    for ti, truth in enumerate(truths):
        for pi, prediction in enumerate(predictions):
            value = iou(truth, prediction)
            if value >= threshold and value > 0:
                candidates.append((value, ti, pi))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    used_truth: set[int] = set()
    used_prediction: set[int] = set()
    matches = []
    for value, ti, pi in candidates:
        if ti in used_truth or pi in used_prediction:
            continue
        used_truth.add(ti)
        used_prediction.add(pi)
        matches.append((ti, pi, value))
    return matches


def detection_counts(
    truths: Sequence[Any],
    predictions: Sequence[Any],
    threshold: float = 0.5,
    iou: IoUFunction = calculate_iou,
) -> dict[str, float]:
    """TP, FP, FN e soma dos IoU casados para uma imagem."""
    matches = match_detections(truths, predictions, threshold, iou)
    return {
        "tp": len(matches),
        "fp": len(predictions) - len(matches),
        "fn": len(truths) - len(matches),
        "iou_sum": sum(value for _, _, value in matches),
    }


def precision_recall_f1(counts: dict[str, float]) -> dict[str, float]:
    """Agrega contagens (somadas sobre várias imagens) em Precision, Recall, F1 e IoU médio."""
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if tp + fp else (1.0 if fn == 0 else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_iou": counts["iou_sum"] / tp if tp else 0.0,
    }


def average_precision(
    images: Sequence[tuple[Sequence[Box], Sequence[tuple[Box, float]]]],
    threshold: float = 0.5,
    iou: IoUFunction = calculate_iou,
) -> float | None:
    """AP de uma classe sobre várias imagens, com interpolação de 101 pontos (estilo COCO).

    ``images`` é uma lista de ``(caixas verdadeiras, [(caixa predita, confiança), ...])``.
    Devolve ``None`` se não houver nenhuma caixa verdadeira (AP indefinida).
    """
    total_truths = sum(len(truths) for truths, _ in images)
    if total_truths == 0:
        return None
    ranked = sorted(
        (
            (score, image_index, prediction_index)
            for image_index, (_, predictions) in enumerate(images)
            for prediction_index, (_, score) in enumerate(predictions)
        ),
        key=lambda item: (-item[0], item[1], item[2]),
    )
    matched: dict[int, set[int]] = {}
    tp_flags = []
    for _, image_index, prediction_index in ranked:
        truths, predictions = images[image_index]
        box = predictions[prediction_index][0]
        used = matched.setdefault(image_index, set())
        best, best_iou = None, threshold
        for ti, truth in enumerate(truths):
            if ti in used:
                continue
            value = iou(truth, box)
            if value >= best_iou and value > 0:
                best, best_iou = ti, value
        if best is None:
            tp_flags.append(0)
        else:
            used.add(best)
            tp_flags.append(1)

    precisions, recalls = [], []
    tp = fp = 0
    for flag in tp_flags:
        tp += flag
        fp += 1 - flag
        precisions.append(tp / (tp + fp))
        recalls.append(tp / total_truths)
    # Envelope monotônico da precisão.
    for i in range(len(precisions) - 2, -1, -1):
        precisions[i] = max(precisions[i], precisions[i + 1])
    total = 0.0
    for step in range(101):
        level = step / 100
        total += next((p for p, r in zip(precisions, recalls, strict=True) if r >= level), 0.0)
    return total / 101


def mean_average_precision(per_class: dict[str, float | None]) -> float | None:
    """Média das AP definidas (classes sem nenhuma verdade são ignoradas)."""
    values = [value for value in per_class.values() if value is not None]
    return sum(values) / len(values) if values else None
