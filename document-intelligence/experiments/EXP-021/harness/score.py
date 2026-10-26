"""Pontuação do EXP-021: leitor treinado com degradações, nas três condições.

``--out <arquivo>``: lê as três rodadas (digitalizada, leve, forte) e grava o relatório, comparando
com o leitor ajustado sem degradações (EXP-017 e EXP-019) e com a validade em LDF 2.0.
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
from read import EXPORT

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-021"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
SETS = ("test-bressay-clean", "test-bressay-light", "test-bressay-strong")
# Leitor ajustado sem degradações: EXP-017 (digitalizada) e EXP-019 (leve e forte), mesmas páginas.
BEFORE = {
    "test-bressay-clean": 0.11816469677997332,
    "test-bressay-light": 0.21602581722301967,
    "test-bressay-strong": 0.706145842877358,
}


def corrector() -> Corrector:
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-011" / "calibration.json").read_text(encoding="utf-8")
    )
    words = json.loads(LEXICON.read_text(encoding="utf-8"))["words"]
    return Corrector(words, LexiconParams(**calibration["best"]["params"]))


def score(name: str, reader: str, fix: Corrector) -> tuple[dict, dict, dict]:
    refs = json.loads((DATA / f"{name}-refs.json").read_text(encoding="utf-8"))["refs"]
    read = json.loads((DATA / f"read-{name}-{reader}.json").read_text(encoding="utf-8"))
    texts = {
        pid: [fix.correct_line(ln["text"]) for ln in ordered_lines(lines)]
        for pid, lines in read["items"].items()
    }
    metrics = page_metrics(refs, {pid: "\n".join(lines) for pid, lines in texts.items()})
    metrics["scales"] = dict(Counter(str(v) for v in read["scales"].values()))
    metrics["cost"] = read["summary"]
    return metrics, read, texts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pontuação do EXP-021")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    fix = corrector()
    results = {}
    for name in SETS:
        manifest = json.loads((DATA / f"{name}-worker.json").read_text(encoding="utf-8"))
        metrics, read, texts = score(name, "aug", fix)
        metrics["ldf2"] = ldf_pages(manifest, read["items"], texts, fine_tuned=True)
        metrics["before"] = BEFORE[name]
        results[name] = metrics
    delta = {name: results[name]["cer_micro"] - BEFORE[name] for name in SETS}
    verdicts = {
        "h1_light_gain": {
            "delta": delta["test-bressay-light"],
            "met": delta["test-bressay-light"] <= -0.03,
        },  # fmt: skip
        "h2_clean_not_worse": {
            "delta": delta["test-bressay-clean"],
            "met": delta["test-bressay-clean"] <= 0.01,
        },  # fmt: skip
        "h3_strong_gain": {
            "delta": delta["test-bressay-strong"],
            "met": delta["test-bressay-strong"] < 0,
        },  # fmt: skip
        "h4_ldf_valid": {
            "met": all(
                item["ldf2"]["valid"] == item["ldf2"]["documents"] for item in results.values()
            )
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-021",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": 80,
        "before": BEFORE,
        "reader_model": {
            "file": "models/exp-021/rec-aug-bressay.onnx",
            "sha256": json.loads(EXPORT.read_text(encoding="utf-8"))["onnx_sha256"],
        },
        "license_status": {
            "reader": "NEEDS VALIDATION — ajustado no BRESSAY (EXP-021); nunca produto",
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
