"""Calibração e teste do EXP-013: CER de página por conjunto e alvo de escala.

``--mode calibrate``: lê só os conjuntos de calibração, escolhe o alvo pela média do CER de página
(BRESSAY com correção lexical; GNHK sem) e grava ``experiments/EXP-013/calibration.json``.

``--mode test --out <arquivo>``: lê os conjuntos de teste com o alvo escolhido e grava o relatório,
com a comparação com as escalas fixas do EXP-012 e a validade em LDF 2.0.
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

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-013"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
TARGETS = (48, 64, 80)
LANGUAGE = {"cal-bressay": "pt", "cal-gnhk": "en", "test-bressay": "pt", "test-gnhk": "en"}
EXP012 = {"test-bressay": {"native": 0.458, "x3": 0.362}, "test-gnhk": {"fixed": 0.275}}


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
    parser = argparse.ArgumentParser(description="Calibração e teste (EXP-013)")
    parser.add_argument("--mode", required=True, choices=("calibrate", "test"))
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    fix = corrector()

    if args.mode == "calibrate":
        results = {}
        for target in TARGETS:
            per_set = {name: score(name, target, fix)[0] for name in ("cal-bressay", "cal-gnhk")}
            mean = sum(m["cer_micro"] for m in per_set.values()) / len(per_set)
            results[str(target)] = {"mean_cer": mean, **per_set}
            print(target, {k: round(v["cer_micro"], 4) for k, v in per_set.items()}, round(mean, 4))
        best = min(results, key=lambda k: results[k]["mean_cer"])
        out = {"note": "Só conjuntos de calibração.", "best_target": int(best), "results": results}
        (EXPERIMENT / "calibration.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
        )
        print("alvo escolhido:", best)
        return 0

    target = json.loads((EXPERIMENT / "calibration.json").read_text(encoding="utf-8"))[
        "best_target"
    ]
    results = {}
    for name in ("test-bressay", "test-gnhk"):
        metrics, read, texts = score(name, target, fix)
        manifest = json.loads((DATA / f"{name}-worker.json").read_text(encoding="utf-8"))
        metrics["ldf2"] = ldf_pages(manifest, read["items"], texts)
        results[name] = metrics
    bressay, gnhk = results["test-bressay"], results["test-gnhk"]
    verdicts = {
        "h1_bressay_close_to_fixed_x3": {
            "auto": bressay["cer_micro"],
            "fixed_x3": EXP012["test-bressay"]["x3"],
            "native": EXP012["test-bressay"]["native"],
            "met": bressay["cer_micro"] - EXP012["test-bressay"]["x3"] <= 0.01,
        },
        "h2_gnhk_not_worse": {
            "auto": gnhk["cer_micro"],
            "fixed": EXP012["test-gnhk"]["fixed"],
            "met": gnhk["cer_micro"] - EXP012["test-gnhk"]["fixed"] <= 0.01,
        },
        "h3_cost": {
            "median_ms": {k: v["cost"]["median_ms"] for k, v in results.items()},
            "met": all(v["cost"]["median_ms"] <= 6000 for v in results.values()),
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-013",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": target,
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
