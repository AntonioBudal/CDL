"""Teste do EXP-017: CER de página com o leitor ajustado do EXP-014, comparado com o EXP-015.

``--mode test --out <arquivo>``: lê os conjuntos de teste (alvo de escala do EXP-013) e grava o
relatório, com a comparação com o leitor original (EXP-015) e a validade em LDF 2.0.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from endtoend import git_state, ldf_pages, ordered_lines
from evaluate import page_metrics
from lexicon import Corrector, LexiconParams
from read import FT_SHA256

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-017"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
LANGUAGE = {"test-bressay": "pt", "test-gnhk": "en"}
# Referência: EXP-015 (leitor original), BENCHMARK-20261022-exp-015-pipeline-direct-reader.json.
EXP015 = {
    "test-bressay": {"cer": 0.2752567978906433, "wer": 0.6295836004238563, "median_ms": 7413.5618},
    "test-gnhk": {"cer": 0.27378697898472115, "wer": 0.5553885787891799, "median_ms": 3143.94315},
}


def corrector() -> Corrector:
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-011" / "calibration.json").read_text(encoding="utf-8")
    )
    words = json.loads(LEXICON.read_text(encoding="utf-8"))["words"]
    return Corrector(words, LexiconParams(**calibration["best"]["params"]))


def score(name: str, target: int, fix: Corrector) -> tuple[dict, dict, dict]:
    refs = json.loads((DATA / f"{name}-refs.json").read_text(encoding="utf-8"))["refs"]
    read = json.loads((DATA / f"read-{name}-t{target}.json").read_text(encoding="utf-8"))
    texts = {
        pid: [ln["text"] for ln in ordered_lines(lines)] for pid, lines in read["items"].items()
    }
    if LANGUAGE[name] == "pt":
        texts = {pid: [fix.correct_line(t) for t in lines] for pid, lines in texts.items()}
    metrics = page_metrics(refs, {pid: "\n".join(lines) for pid, lines in texts.items()})
    metrics["scales"] = dict(Counter(str(v) for v in read["scales"].values()))
    metrics["cost"] = read["summary"]
    return metrics, read, texts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Teste do EXP-017")
    parser.add_argument("--mode", required=True, choices=("test",))
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    fix = corrector()
    target = json.loads(
        (ROOT / "experiments" / "EXP-013" / "calibration.json").read_text(encoding="utf-8")
    )["best_target"]
    results = {}
    for name in ("test-bressay", "test-gnhk"):
        metrics, read, texts = score(name, target, fix)
        manifest = json.loads((DATA / f"{name}-worker.json").read_text(encoding="utf-8"))
        metrics["ldf2"] = ldf_pages(manifest, read["items"], texts)
        metrics["exp015"] = EXP015[name]
        results[name] = metrics
    bressay, gnhk = results["test-bressay"], results["test-gnhk"]
    verdicts = {
        "h1_bressay_page_cer": {"cer": bressay["cer_micro"], "met": bressay["cer_micro"] <= 0.20},
        "h2_gnhk_not_much_worse": {
            "delta": gnhk["cer_micro"] - EXP015["test-gnhk"]["cer"],
            "met": gnhk["cer_micro"] - EXP015["test-gnhk"]["cer"] <= 0.03,
        },
        "h3_ldf_valid": {
            "met": all(
                item["ldf2"]["valid"] == item["ldf2"]["documents"] for item in results.values()
            )
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-017",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": target,
        "reader_model": {"file": "models/exp-017/rec-ft-bressay.onnx", "sha256": FT_SHA256},
        "license_status": {
            "reader": "NEEDS VALIDATION — ajustado no BRESSAY (EXP-014); nunca produto",
            "gnhk": "VERIFIED (CC-BY-4.0)",
            "bressay": "NEEDS VALIDATION (exceção experimental; não embasa produto)",
        },
        "results": results,
        "verdicts": verdicts,
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for name, item in results.items():
        print(name, round(item["cer_micro"], 4), round(item["wer_micro"], 4), item["scales"],
              round(item["cost"]["median_ms"]), item["ldf2"])  # fmt: skip
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
