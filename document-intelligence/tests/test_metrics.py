"""Testes unitários para cálculo de métricas de Document Intelligence."""

import json
from pathlib import Path

from leitorum_di.metrics.base import (
    calculate_cer,
    calculate_iou,
    calculate_wer,
    levenshtein_distance,
)

FIXTURE_PATH = (
    Path(__file__).parent.parent / "dataset" / "fixtures" / "synthetic-line-sample.json"
)
TOLERANCE = 1e-9


def _load_samples() -> list[dict]:
    assert FIXTURE_PATH.exists(), "Arquivo fixture sintética não encontrado."
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data.get("samples", [])


def test_levenshtein_distance_basic():
    assert levenshtein_distance("livro", "livro") == 0
    assert levenshtein_distance("livro", "livros") == 1
    assert levenshtein_distance("livro", "livr") == 1
    assert levenshtein_distance("casa", "caso") == 1


def test_cer_calculation():
    assert calculate_cer("texto", "texto") == 0.0
    assert calculate_cer("texto", "testo") == 0.2
    assert calculate_cer("", "") == 0.0
    assert calculate_cer("", "a") == 1.0


def test_cer_accents_and_case_are_errors():
    assert abs(calculate_cer("coração", "coracao") - 2 / 7) < TOLERANCE
    assert abs(calculate_cer("Casa", "casa") - 1 / 4) < TOLERANCE


def test_wer_calculation():
    assert calculate_wer("o livro de estudos", "o livro de estudos") == 0.0
    assert calculate_wer("o livro de estudos", "o caderno de estudos") == 0.25
    assert calculate_wer("", "") == 0.0
    assert calculate_wer("", "a") == 1.0


def test_wer_ignores_edge_punctuation_but_keeps_accents_and_case():
    assert calculate_wer("Olá, mundo!", "Olá mundo") == 0.0
    assert calculate_wer("(sim) \"não\"", "sim não") == 0.0
    # hífen interno é mantido: 1 substituição + 1 inserção sobre 1 palavra de referência
    assert calculate_wer("guarda-chuva", "guarda chuva") == 2.0
    assert calculate_wer("ação", "acao") == 1.0
    assert calculate_wer("Casa", "casa") == 1.0
    assert calculate_wer("a - b", "a b") == 0.0  # token só de pontuação é descartado


def test_iou_calculation():
    # Mesma caixa: IoU = 1.0
    assert calculate_iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0

    # Caixas sem sobreposição: IoU = 0.0
    assert calculate_iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0.0

    # Sobreposição parcial: área int = 50, uni = 150 -> IoU = 1/3
    assert abs(calculate_iou([0, 0, 10, 10], [5, 0, 15, 10]) - (50 / 150)) < 1e-5

    # Caixa degenerada (área zero): sem divisão por zero
    assert calculate_iou([0, 0, 0, 0], [0, 0, 0, 0]) == 0.0


def test_synthetic_fixture_covers_manifest_cases():
    samples = _load_samples()
    assert len(samples) >= 7
    ids = [s["id"] for s in samples]
    assert len(ids) == len(set(ids)), "IDs de amostras duplicados"
    text = " ".join(s["ground_truth"] + s["prediction"] for s in samples)
    for char in "çãéõ":
        assert char in text, f"Fixture não cobre o caractere acentuado '{char}'"
    # Variação de caixa presente (mesma sequência ignorando caixa, mas diferente com caixa)
    assert any(
        s["ground_truth"] != s["prediction"]
        and s["ground_truth"].lower() == s["prediction"].lower()
        for s in samples
    )
    # Inserção e deleção (comprimentos diferentes em ambos os sentidos)
    assert any(len(s["prediction"]) > len(s["ground_truth"]) for s in samples)
    assert any(len(s["prediction"]) < len(s["ground_truth"]) for s in samples)


def test_synthetic_fixture_all_samples_match_expected_values():
    """Valida TODAS as amostras contra os valores esperados (derivados à mão na fixture)."""
    for sample in _load_samples():
        gt, pred = sample["ground_truth"], sample["prediction"]
        cer = calculate_cer(gt, pred)
        wer = calculate_wer(gt, pred)
        iou = calculate_iou(sample["bounding_box_gt"], sample["bounding_box_pred"])
        sid = sample["id"]
        assert abs(cer - sample["expected_cer"]) < TOLERANCE, f"{sid}: CER {cer}"
        assert abs(wer - sample["expected_wer"]) < TOLERANCE, f"{sid}: WER {wer}"
        assert abs(iou - sample["expected_iou"]) < TOLERANCE, f"{sid}: IoU {iou}"
