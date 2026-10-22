"""Relatório do EXP-014: leitura antes e depois do ajuste fino, com e sem correção lexical.

Junta as predições gravadas por ``predict.py`` e ``probe_padding_width.py`` (fora do Git),
calcula CER/WER com o avaliador do EXP-009 e aplica a correção lexical do EXP-011 (parâmetros
calibrados lá). Grava um relatório só com números. Roda no ambiente do harness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-009" / "harness"))
sys.path.insert(0, str(ROOT / "experiments" / "EXP-011" / "harness"))
from evaluate import line_metrics  # noqa: E402
from lexicon import Corrector, LexiconParams  # noqa: E402

DATA = ROOT / "dataset" / "processed" / "exp-014"
VARIANTS = {
    "pacote (EXP-009/010)": "pred-rapidocr-padding1-{set}.json",
    "margem 640 px, sem ajuste": "pred-pad-e640-{set}.json",
    "ajustado no BRESSAY + margem 640 px": "pred-ft-{set}.json",
}


def git_state() -> dict:
    def git(*args: str) -> str | None:
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                                  check=True).stdout.strip()  # fmt: skip
        except (OSError, subprocess.CalledProcessError):
            return None

    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def summary(metrics: dict) -> dict:
    accents = metrics["cer_by_class"].get("letra acentuada", {}).get("cer")
    return {
        "lines": metrics["lines"],
        "cer": metrics["cer_micro"],
        "wer": metrics["wer_micro"],
        "accents": accents,
        "lines_with_cer_below_10pct": metrics["lines_with_cer_below_10pct"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Relatório do EXP-014")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-011" / "calibration.json").read_text("utf-8")
    )
    words = json.loads(
        (ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json").read_text("utf-8")
    )
    corrector = Corrector(words["words"], LexiconParams(**calibration["best"]["params"]))
    training = json.loads((ROOT / "experiments" / "EXP-014" / "training.json").read_text("utf-8"))
    results: dict = {}
    for name in ("test-exp001", "test-all"):
        items = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
        refs = {it["id"]: it["text"] for it in items}
        results[name] = {}
        for label, pattern in VARIANTS.items():
            path = DATA / pattern.format(set=name)
            if not path.is_file():
                continue
            predictions = json.loads(path.read_text(encoding="utf-8"))["items"]
            corrected = {k: corrector.correct_line(v) for k, v in predictions.items()}
            results[name][label] = {
                "raw": summary(line_metrics(refs, predictions)),
                "lexicon": summary(line_metrics(refs, corrected)),
                "ms_per_line": json.loads(path.read_text(encoding="utf-8")).get("ms_per_line"),
            }
    report = {
        "schema": "leitorum-di-reading-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-014",
        "git": git_state(),
        "license_status": {
            "base_model": "PP-OCRv6 small rec, Apache-2.0 (VERIFIED, conforme declarado)",
            "fine_tuned_model": "ajustado com BRESSAY (NEEDS VALIDATION): só experimento",
        },
        "training": {k: training[k] for k in ("best_val_cer", "steps", "train_lines", "args")},
        "validation_padding_choice": {"e0": 0.4149, "e160": 0.3481, "e320": 0.3287, "e640": 0.3205},
        "results": results,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8", newline="\n")  # fmt: skip
    for name, variants in results.items():
        for label, item in variants.items():
            r, lx = item["raw"], item["lexicon"]
            print(
                f"{name} | {label}: CER {r['cer']:.3f} WER {r['wer']:.3f} "
                f"acentos {r['accents']:.3f} | léxico CER {lx['cer']:.3f} WER {lx['wer']:.3f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
