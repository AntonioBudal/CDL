"""Avaliador do EXP-001: CER/WER por linha e agregados, e estatísticas de latência.

Usa só ``leitorum_di.metrics``. Referência e predição são comparadas em Unicode NFC; nenhuma
outra normalização é aplicada antes do CER (Princípio 4: a saída bruta é preservada).
"""

from __future__ import annotations

import math
import statistics
import unicodedata
from typing import Any

from leitorum_di.metrics.base import (
    calculate_cer,
    calculate_wer,
    levenshtein_distance,
    tokenize_words,
)

H1_MAX_CER = 0.12
H1_MAX_WER = 0.25
H2_MAX_MEDIAN_MS = 150.0
H2_MAX_PEAK_BYTES = 2 * 1024**3


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def percentile(values: list[float], fraction: float) -> float | None:
    """Percentil pelo método do posto mais próximo (nearest-rank)."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(fraction * len(ordered)))
    return ordered[rank - 1]


def latency_stats(predictions: list[dict[str, Any]]) -> dict[str, float | int | None]:
    times = [float(p["elapsed_ms"]) for p in predictions]
    return {
        "lines": len(times),
        "median_ms": statistics.median(times) if times else None,
        "p95_ms": percentile(times, 0.95),
        "mean_ms": statistics.fmean(times) if times else None,
        "max_ms": max(times) if times else None,
    }


def evaluate(manifest: dict[str, Any], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    """Compara predições com as referências do manifesto.

    Linhas sem predição contam como hipótese vazia e são listadas em ``missing``. Os agregados
    "micro" ponderam pelo tamanho da referência (total de edições / total de unidades).
    """
    by_id = {p["id"]: p for p in predictions}
    per_line = []
    missing = []
    char_edits = char_total = word_edits = word_total = 0

    for line in manifest["lines"]:
        reference = nfc(line["text"])
        prediction = by_id.get(line["id"])
        if prediction is None:
            missing.append(line["id"])
        hypothesis = nfc(prediction["text"]) if prediction is not None else ""

        ref_words, hyp_words = tokenize_words(reference), tokenize_words(hypothesis)
        char_edits += levenshtein_distance(reference, hypothesis)
        char_total += len(reference)
        word_edits += levenshtein_distance(ref_words, hyp_words)
        word_total += len(ref_words)
        per_line.append(
            {
                "id": line["id"],
                "cer": calculate_cer(reference, hypothesis),
                "wer": calculate_wer(reference, hypothesis),
                "ref_chars": len(reference),
                "ref_words": len(ref_words),
            }
        )

    count = len(per_line)
    return {
        "lines": count,
        "missing": missing,
        "cer_micro": char_edits / char_total if char_total else 0.0,
        "wer_micro": word_edits / word_total if word_total else 0.0,
        "cer_macro": sum(item["cer"] for item in per_line) / count if count else 0.0,
        "wer_macro": sum(item["wer"] for item in per_line) / count if count else 0.0,
        "char_edits": char_edits,
        "ref_chars": char_total,
        "word_edits": word_edits,
        "ref_words": word_total,
        "per_line": per_line,
    }


def verdicts(
    metrics: dict[str, Any], latency: dict[str, Any], peak_rss_bytes: int | None
) -> dict[str, bool | None]:
    """Veredito contra as hipóteses da spec. ``None`` = não mensurável nesta execução."""
    median = latency.get("median_ms")
    h2 = None
    if median is not None and peak_rss_bytes is not None:
        h2 = median <= H2_MAX_MEDIAN_MS and peak_rss_bytes <= H2_MAX_PEAK_BYTES
    return {
        "h1_quality": metrics["cer_micro"] <= H1_MAX_CER and metrics["wer_micro"] <= H1_MAX_WER,
        "h2_cost": h2,
    }
