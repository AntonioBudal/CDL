"""Testes do avaliador: CER/WER agregados, NFC, casos de borda e latência."""

import unicodedata

import pytest
from evaluate import evaluate, latency_stats, percentile, verdicts


def _manifest(*texts):
    return {"lines": [{"id": f"l{i}", "text": text} for i, text in enumerate(texts)]}


def _preds(*texts, ms=10.0):
    return [{"id": f"l{i}", "text": text, "elapsed_ms": ms} for i, text in enumerate(texts)]


def test_perfect_predictions_score_zero():
    texts = ("Olá, mundo!", "açúcar é doce")
    result = evaluate(_manifest(*texts), _preds(*texts))
    assert result["cer_micro"] == result["wer_micro"] == 0.0
    assert result["cer_macro"] == result["wer_macro"] == 0.0
    assert result["missing"] == []


def test_known_errors_micro_and_macro():
    # linha 0: 2 substituições em 32 caracteres, 1 palavra errada de 4; linha 1: perfeita (4 chars).
    manifest = _manifest("definição e conceitos essenciais", "dois")
    result = evaluate(manifest, _preds("definicao e conceitos essenciais", "dois"))
    assert result["char_edits"] == 2 and result["ref_chars"] == 36
    assert result["cer_micro"] == pytest.approx(2 / 36)
    assert result["cer_macro"] == pytest.approx((2 / 32 + 0) / 2)
    assert result["wer_micro"] == pytest.approx(1 / 5)
    assert result["wer_macro"] == pytest.approx((1 / 4 + 0) / 2)


def test_nfd_prediction_equals_nfc_reference():
    reference = "ação à tarde"
    result = evaluate(_manifest(reference), _preds(unicodedata.normalize("NFD", reference)))
    assert result["cer_micro"] == 0.0


def test_punctuation_counts_for_cer_but_not_for_wer():
    result = evaluate(_manifest("Olá, mundo! Tudo bem?"), _preds("Olá mundo Tudo bem"))
    assert result["cer_micro"] == pytest.approx(3 / 21)
    assert result["wer_micro"] == 0.0


def test_missing_prediction_counts_as_empty_hypothesis():
    result = evaluate(_manifest("abc", "de"), _preds("abc"))
    assert result["missing"] == ["l1"]
    assert result["per_line"][1]["cer"] == 1.0
    assert result["cer_micro"] == pytest.approx(2 / 5)


def test_empty_reference_edge_cases():
    result = evaluate(_manifest("", ""), _preds("", "x"))
    assert result["per_line"][0]["cer"] == 0.0
    assert result["per_line"][1]["cer"] == 1.0
    assert result["cer_micro"] == 0.0  # sem caracteres de referência: agregado micro indefinido → 0


def test_percentile_and_latency_stats():
    assert percentile([], 0.95) is None
    assert percentile([5.0], 0.95) == 5.0
    values = [float(v) for v in range(1, 101)]
    assert percentile(values, 0.95) == 95.0
    stats = latency_stats([{"elapsed_ms": v} for v in values])
    assert stats["median_ms"] == 50.5 and stats["p95_ms"] == 95.0 and stats["max_ms"] == 100.0
    assert latency_stats([])["median_ms"] is None


def test_verdicts_against_hypotheses():
    good = {"cer_micro": 0.10, "wer_micro": 0.20}
    bad = {"cer_micro": 0.30, "wer_micro": 0.20}
    fast, slow = {"median_ms": 100.0}, {"median_ms": 900.0}
    assert verdicts(good, fast, 10**9) == {"h1_quality": True, "h2_cost": True}
    assert verdicts(bad, slow, 10**9) == {"h1_quality": False, "h2_cost": False}
    assert verdicts(good, fast, 3 * 1024**3)["h2_cost"] is False
    assert verdicts(good, {"median_ms": None}, None)["h2_cost"] is None
