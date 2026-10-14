"""Benchmark do EXP-010: três reconhecedores PP-OCR × três escalas de recorte.

Lê as transcrições preparadas no EXP-009 e as leituras do EXP-010 (fora do Git) e grava um
relatório só com números.

Uso (árvore limpa): ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-010/harness/run.py --out evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from evaluate import line_metrics

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
EXP009 = ROOT / "dataset" / "processed" / "exp-009"
DATA = ROOT / "dataset" / "processed" / "exp-010"
BASELINE = 0.385  # PP-OCRv6 small, escala 1×, linhas do EXP-001 (EXP-009)


def git_state() -> dict[str, object]:
    def git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark do EXP-010")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    refs = {
        name: json.loads((EXP009 / f"{name}-refs.json").read_text(encoding="utf-8"))["refs"]
        for name in ("lines-exp001", "lines-gnhk")
    }
    results = {}
    for path in sorted(DATA.glob("read-*.json")):
        read = json.loads(path.read_text(encoding="utf-8"))
        metrics = line_metrics(refs[read["set"]], read["items"])
        key = f"{read['model']}-x{read['scale']}-{read['set']}"
        results[key] = {
            "model": read["model"],
            "scale": read["scale"],
            "set": read["set"],
            **metrics,
            "cost": read["summary"],
        }
    exp001 = {k: v for k, v in results.items() if v["set"] == "lines-exp001"}
    best_key = min(exp001, key=lambda k: exp001[k]["cer_micro"])
    best = exp001[best_key]
    same_scale_best = {
        model: min(
            (v for v in exp001.values() if v["model"] == model), key=lambda v: v["cer_micro"]
        )
        for model in {v["model"] for v in exp001.values()}
    }
    scale_gain = {
        model: exp001[f"{model}-x1-lines-exp001"]["cer_micro"] - same_scale_best[model]["cer_micro"]
        for model in same_scale_best
    }
    one_x = {m: exp001[f"{m}-x1-lines-exp001"]["cer_micro"] for m in same_scale_best}
    verdicts = {
        "h1_alternative_model_5_points_better": {
            "cer_at_1x": one_x,
            "baseline_small_1x": BASELINE,
            "met": any(cer <= BASELINE - 0.05 for m, cer in one_x.items() if m != "small"),
        },
        "h2_upscaling_2_points_better": {
            "gain_by_model": scale_gain,
            "met": any(gain >= 0.02 for gain in scale_gain.values()),
        },
        "h3_adoption_criterion": {
            "best": best_key,
            "cer": best["cer_micro"],
            "wer": best["wer_micro"],
            "met": best["cer_micro"] <= 0.12 and best["wer_micro"] <= 0.25,
        },
        "h4_cost": {
            "median_ms": {k: v["cost"]["median_ms"] for k, v in exp001.items()},
            "met": best["cost"]["median_ms"] <= 150
            and (best["cost"]["peak_rss_bytes"] or 0) <= 2 * 1024**3,
        },
    }
    report = {
        "schema": "leitorum-di-reading-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-010",
        "git": git_state(),
        "environment": environment_snapshot(),
        "license_status": {
            "ppocr": "VERIFIED (Apache-2.0, conforme declarado)",
            "gnhk": "VERIFIED (CC-BY-4.0)",
            "bressay": "NEEDS VALIDATION (exceção experimental; não embasa produto)",
        },
        "results": results,
        "verdicts": verdicts,
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8", newline="\n")  # fmt: skip
    for key, item in results.items():
        accents = item["cer_by_class"].get("letra acentuada", {}).get("cer")
        print(f"{key:32s} CER {item['cer_micro']:.3f} WER {item['wer_micro']:.3f} "
              f"acentos {accents if accents is None else round(accents, 3)} "
              f"{item['cost']['median_ms']:.0f} ms")  # fmt: skip
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
