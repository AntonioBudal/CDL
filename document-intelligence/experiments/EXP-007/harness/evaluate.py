"""Avaliador do EXP-002: detecção de linhas (caixa e polígono), blocos (AP) e regiões "ignorar".

Formato de predição por página::

    {"lines": [{"bbox": [x0, y0, x1, y1], "polygon": [[x, y], ...] | None, "score": float}],
     "blocks": [{"type": "title|paragraph|margin_note|graphic_box", "bbox": [...], "score": float}]}
"""

from __future__ import annotations

import statistics
from typing import Any

import cv2
import numpy as np

from leitorum_di.metrics.detection import (
    average_precision,
    detection_counts,
    mean_average_precision,
    precision_recall_f1,
)

BLOCK_TYPES = ("title", "paragraph", "margin_note", "graphic_box")
THRESHOLDS = (0.5, 0.75)
IGNORE_OVERLAP = 0.5
LEVELS = ("clean", "light", "strong")

# Critérios de avaliação aprovados (spec §1).
H1_F1_CLEAN = 0.90
H1_F1_DEGRADED = 0.80
H2_MAP = 0.70
H3_MAX_MEDIAN_MS = 2000.0
H3_MAX_PEAK_BYTES = 2 * 1024**3


def _box_polygon(bbox) -> list[list[float]]:
    x0, y0, x1, y1 = bbox
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def polygon_iou(a, b) -> float:
    """IoU de dois polígonos por rasterização (pixels inteiros)."""
    pa = np.asarray(a, dtype=np.float64).reshape(-1, 2)
    pb = np.asarray(b, dtype=np.float64).reshape(-1, 2)
    if len(pa) < 3 or len(pb) < 3:
        return 0.0
    both = np.vstack([pa, pb])
    x0, y0 = np.floor(both.min(axis=0)).astype(int)
    x1, y1 = np.ceil(both.max(axis=0)).astype(int)
    if (x1 - x0) * (y1 - y0) > 40_000_000:
        return 0.0
    shape = (y1 - y0 + 1, x1 - x0 + 1)
    mask_a = np.zeros(shape, np.uint8)
    mask_b = np.zeros(shape, np.uint8)
    cv2.fillPoly(mask_a, [np.round(pa - (x0, y0)).astype(np.int32)], 1)
    cv2.fillPoly(mask_b, [np.round(pb - (x0, y0)).astype(np.int32)], 1)
    union = np.count_nonzero(mask_a | mask_b)
    return float(np.count_nonzero(mask_a & mask_b) / union) if union else 0.0


def _bbox_iou(a, b) -> float:
    from leitorum_di.metrics.base import calculate_iou

    return calculate_iou(a["bbox"], b["bbox"])


def _poly_iou(a, b) -> float:
    return polygon_iou(
        a.get("polygon") or _box_polygon(a["bbox"]), b.get("polygon") or _box_polygon(b["bbox"])
    )


def _ignored(bbox, regions) -> bool:
    area = max(0, bbox[2] - bbox[0]) * max(0, bbox[3] - bbox[1])
    if area == 0:
        return True
    for region in regions:
        ix = max(0, min(bbox[2], region[2]) - max(bbox[0], region[0]))
        iy = max(0, min(bbox[3], region[3]) - max(bbox[1], region[1]))
        if ix * iy / area >= IGNORE_OVERLAP:
            return True
    return False


def _empty_counts() -> dict[str, float]:
    return {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0}


def _add(total: dict[str, float], counts: dict[str, float]) -> None:
    for key in total:
        total[key] += counts[key]


def evaluate_pages(
    manifest: dict[str, Any], predictions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Avalia predições (por id de página) contra o manifesto.

    Páginas sem predição contam como vazias.
    """
    kinds = {"bbox": _bbox_iou, "polygon": _poly_iou}
    totals = {kind: {t: _empty_counts() for t in THRESHOLDS} for kind in kinds}
    by_level: dict[str, dict[str, float]] = {}
    per_page = []
    block_images: dict[str, list] = {name: [] for name in BLOCK_TYPES}
    missing = []

    for page in manifest["pages"]:
        prediction = predictions.get(page["id"])
        if prediction is None:
            missing.append(page["id"])
            prediction = {"lines": [], "blocks": []}
        regions = page.get("ignore", [])
        predicted_lines = [
            ln for ln in prediction.get("lines", []) if not _ignored(ln["bbox"], regions)
        ]
        truth_lines = page["lines"]
        page_counts = {}
        for kind, iou in kinds.items():
            for threshold in THRESHOLDS:
                counts = detection_counts(truth_lines, predicted_lines, threshold, iou)
                _add(totals[kind][threshold], counts)
                if kind == "bbox" and threshold == 0.5:
                    page_counts = counts
                    _add(by_level.setdefault(page["level"], _empty_counts()), counts)
        per_page.append(
            {"id": page["id"], "level": page["level"], **precision_recall_f1(page_counts)}
        )

        for name in BLOCK_TYPES:
            truths = [b["bbox"] for b in page["blocks"] if b["type"] == name]
            preds = [
                (b["bbox"], float(b.get("score", 1.0)))
                for b in prediction.get("blocks", [])
                if b["type"] == name
            ]
            block_images[name].append((truths, preds))

    ap = {name: average_precision(images, 0.5) for name, images in block_images.items()}
    any_blocks = any(prediction.get("blocks") for prediction in predictions.values())
    return {
        "pages": len(manifest["pages"]),
        "missing": missing,
        "lines": {
            kind: {str(t): precision_recall_f1(totals[kind][t]) for t in THRESHOLDS}
            for kind in kinds
        },
        "lines_by_level": {level: precision_recall_f1(c) for level, c in sorted(by_level.items())},
        "blocks": {"ap50": ap, "map50": mean_average_precision(ap)} if any_blocks else None,
        "per_page": per_page,
    }


def latency_stats(elapsed_ms: list[float]) -> dict[str, float | int | None]:
    if not elapsed_ms:
        return {"pages": 0, "median_ms": None, "p95_ms": None, "max_ms": None}
    ordered = sorted(elapsed_ms)
    p95 = ordered[max(1, int(np.ceil(0.95 * len(ordered)))) - 1]
    return {
        "pages": len(ordered),
        "median_ms": statistics.median(ordered),
        "p95_ms": p95,
        "max_ms": ordered[-1],
    }


def verdicts(metrics: dict[str, Any], latency: dict[str, Any], peak_rss_bytes: int | None) -> dict:
    """Veredito contra os critérios de avaliação. ``None`` = não mensurável nesta execução."""
    levels = metrics["lines_by_level"]
    clean = levels.get("clean", {}).get("f1")
    degraded = [levels[name]["f1"] for name in ("light", "strong") if name in levels]
    blocks = metrics.get("blocks")
    median = latency.get("median_ms")
    return {
        "h1_lines_clean": None if clean is None else clean >= H1_F1_CLEAN,
        "h1_lines_degraded": None if not degraded else min(degraded) >= H1_F1_DEGRADED,
        "h2_blocks": None if not blocks or blocks["map50"] is None else blocks["map50"] >= H2_MAP,
        "h3_cost": None
        if median is None or peak_rss_bytes is None
        else median <= H3_MAX_MEDIAN_MS and peak_rss_bytes <= H3_MAX_PEAK_BYTES,
    }
