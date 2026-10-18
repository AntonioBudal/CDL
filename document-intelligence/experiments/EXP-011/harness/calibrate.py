"""Calibra a correção lexical só nas linhas de VALIDAÇÃO do BRESSAY (nenhum dado de teste é lido).

Grade: tamanho do léxico × distância máxima × comprimento mínimo × razão de acento. Critério: CER
micro (NFC) da validação depois da correção. Grava ``experiments/EXP-011/calibration.json``.
"""

from __future__ import annotations

import itertools
import json
import sys
import time
import unicodedata
from dataclasses import replace
from pathlib import Path

from lexicon import Corrector, LexiconParams

from leitorum_di.metrics.base import levenshtein_distance, tokenize_words

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-011"
GRID = {
    "size": (20_000, 50_000, 100_000),
    "max_distance": (0, 1, 2),
    "min_length": (1, 3),
    "accent_ratio": (None, 5.0, 20.0),
}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def micro(refs: dict[str, str], hyps: dict[str, str]) -> dict[str, float]:
    chars = char_total = words = word_total = 0
    for key, reference in refs.items():
        reference, hypothesis = nfc(reference), nfc(hyps.get(key, ""))
        chars += levenshtein_distance(reference, hypothesis)
        char_total += len(reference)
        ref_words = tokenize_words(reference)
        words += levenshtein_distance(ref_words, tokenize_words(hypothesis))
        word_total += len(ref_words)
    return {"cer": chars / char_total, "wer": words / word_total}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    words = json.loads((DATA / "lexicon-pt.json").read_text(encoding="utf-8"))["words"]
    refs = json.loads((DATA / "val-lines-refs.json").read_text(encoding="utf-8"))["refs"]
    read = json.loads((DATA / "read-val-lines.json").read_text(encoding="utf-8"))["items"]
    started = time.monotonic()
    baseline = micro(refs, read)
    print(f"sem correção: CER {baseline['cer']:.4f} WER {baseline['wer']:.4f}")
    results = []
    for size, distance in itertools.product(GRID["size"], GRID["max_distance"]):
        corrector = Corrector(words, LexiconParams(size=size, max_distance=distance))
        for min_length, ratio in itertools.product(GRID["min_length"], GRID["accent_ratio"]):
            corrector.params = replace(corrector.params, min_length=min_length, accent_ratio=ratio)
            fixed = {key: corrector.correct_line(text) for key, text in read.items()}
            score = micro(refs, fixed)
            results.append({"params": corrector.params.to_dict(), **score})
            print(corrector.params.to_dict(), f"CER {score['cer']:.4f} WER {score['wer']:.4f}")
    best = min(results, key=lambda item: item["cer"])
    out = {
        "schema": "leitorum-di-lexicon-calibration/1",
        "note": "Calibração só nas linhas de validação do BRESSAY; o teste não é lido.",
        "criterion": "CER micro (NFC) da validação",
        "lines": len(refs),
        "baseline": baseline,
        "best": best,
        "grid": {k: list(v) for k, v in GRID.items()},
        "results": results,
        "elapsed_s": round(time.monotonic() - started, 1),
    }
    (EXPERIMENT / "calibration.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print("escolhido:", best)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
