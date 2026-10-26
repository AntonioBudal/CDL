"""Pontuação do EXP-019: CER de página em condições de foto, leitor original e ajustado.

``--out <arquivo>``: lê as quatro rodadas (níveis ``light`` e ``strong`` × leitores) e grava o
relatório, com as referências limpas do EXP-015/017 e a validade em LDF 2.0.
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
DATA = ROOT / "dataset" / "processed" / "exp-019"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
SETS = ("test-bressay-light", "test-bressay-strong")
READERS = ("original", "ft")
# Página digitalizada ("limpa"): EXP-015 (original) e EXP-017 (ajustado), mesmas 185 páginas.
CLEAN = {
    "original": {"cer": 0.2752567978906433, "wer": 0.6295836004238563},
    "ft": {"cer": 0.11816469677997332, "wer": 0.33639015711463743},
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
    parser = argparse.ArgumentParser(description="Pontuação do EXP-019")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    fix = corrector()
    results = {}
    for name in SETS:
        manifest = json.loads((DATA / f"{name}-worker.json").read_text(encoding="utf-8"))
        for reader in READERS:
            metrics, read, texts = score(name, reader, fix)
            metrics["ldf2"] = ldf_pages(manifest, read["items"], texts, fine_tuned=reader == "ft")
            results[f"{name}/{reader}"] = metrics
    light, strong = "test-bressay-light", "test-bressay-strong"
    gap = results[f"{strong}/original"]["cer_micro"] - results[f"{strong}/ft"]["cer_micro"]
    verdicts = {
        "h1_light_ft": {
            "cer": results[f"{light}/ft"]["cer_micro"],
            "met": results[f"{light}/ft"]["cer_micro"] <= 0.15,
        },
        "h2_strong_gap": {"gap": gap, "met": gap >= 0.10},
        "h3_ldf_valid": {
            "met": all(
                item["ldf2"]["valid"] == item["ldf2"]["documents"] for item in results.values()
            )
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-019",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": 80,
        "clean_reference": CLEAN,
        "degradation": "experiments/EXP-002/harness/pages/degrade.py (níveis light e strong)",
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
