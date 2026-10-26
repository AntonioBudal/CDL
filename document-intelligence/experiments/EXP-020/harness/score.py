"""Pontuação do EXP-020: escala medida no quadrilátero, leitor ajustado, três condições.

``--out <arquivo>``: lê as três rodadas (digitalizada, leve, forte) e grava o relatório, com as
referências do EXP-017 (digitalizada) e do EXP-019 (leve e forte) e a validade em LDF 2.0.
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
DATA = ROOT / "dataset" / "processed" / "exp-020"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
SETS = ("test-bressay-clean", "test-bressay-light", "test-bressay-strong")
# Leitor ajustado com a escala pela caixa: EXP-017 (digitalizada); leve e forte vêm do EXP-019.
CLEAN_BEFORE = 0.11816469677997332


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
    parser = argparse.ArgumentParser(description="Pontuação do EXP-020")
    parser.add_argument("--out", required=True)
    parser.add_argument("--before-light", type=float, required=True, help="CER do EXP-019")
    parser.add_argument("--before-strong", type=float, required=True, help="CER do EXP-019")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    before = {
        "test-bressay-clean": CLEAN_BEFORE,
        "test-bressay-light": args.before_light,
        "test-bressay-strong": args.before_strong,
    }
    fix = corrector()
    results = {}
    for name in SETS:
        manifest = json.loads((DATA / f"{name}-worker.json").read_text(encoding="utf-8"))
        metrics, read, texts = score(name, "ft", fix)
        metrics["ldf2"] = ldf_pages(manifest, read["items"], texts, fine_tuned=True)
        metrics["before"] = before[name]
        results[name] = metrics
    cer = {name: item["cer_micro"] for name, item in results.items()}
    delta = {name: cer[name] - before[name] for name in SETS}
    verdicts = {
        "h1_light_gain": {
            "delta": delta["test-bressay-light"],
            "met": delta["test-bressay-light"] <= -0.02,
        },
        "h2_strong_not_worse": {
            "delta": delta["test-bressay-strong"],
            "met": delta["test-bressay-strong"] <= 0,
        },
        "h3_clean_unchanged": {
            "delta": delta["test-bressay-clean"],
            "met": abs(delta["test-bressay-clean"]) <= 0.003,
        },
        "h4_ldf_valid": {
            "met": all(
                item["ldf2"]["valid"] == item["ldf2"]["documents"] for item in results.values()
            )
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-020",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": 80,
        "before": before,
        "change": "altura da linha no quadrilátero detectado (média dos lados curtos)",
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
