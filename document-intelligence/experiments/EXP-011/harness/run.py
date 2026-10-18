"""Benchmark do EXP-011: leitura do PP-OCRv6 small 2× com e sem correção lexical, no teste.

Conjuntos: as 398 linhas do EXP-001 (leitura do EXP-010) e todas as 5.496 linhas de teste (leitura
do EXP-011). Parâmetros: os de ``calibration.json`` (escolhidos na validação). Só números.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from evaluate import line_metrics, nfc
from lexicon import TOKEN, Corrector, LexiconParams

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-011"
SETS = {
    "lines-exp001": (
        ROOT / "dataset" / "processed" / "exp-009" / "lines-exp001-refs.json",
        ROOT / "dataset" / "processed" / "exp-010" / "read-small-x2-lines-exp001.json",
    ),
    "lines-bressay": (
        ROOT / "dataset" / "processed" / "exp-009" / "lines-bressay-refs.json",
        DATA / "read-lines-bressay.json",
    ),
}


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


def core(token: str) -> str:
    return TOKEN.match(token).group(2)


def harmed_words(refs: dict[str, str], before: dict[str, str], after: dict[str, str]) -> dict:
    """Palavras que estavam certas antes da correção e ficaram erradas depois (H5)."""
    correct = harmed = fixed = 0
    for key, reference in refs.items():
        ref = [core(t) for t in nfc(reference).split()]
        old = [core(t) for t in nfc(before.get(key, "")).split()]
        new = [core(t) for t in nfc(after.get(key, "")).split()]
        if len(old) != len(new):
            continue
        n, m = len(ref), len(old)
        rows = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            rows[i][0] = i
        for j in range(m + 1):
            rows[0][j] = j
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if ref[i - 1] == old[j - 1] else 1
                rows[i][j] = min(rows[i - 1][j] + 1, rows[i][j - 1] + 1, rows[i - 1][j - 1] + cost)
        i, j = n, m
        while i > 0 and j > 0:
            cost = 0 if ref[i - 1] == old[j - 1] else 1
            if rows[i][j] == rows[i - 1][j - 1] + cost:
                if cost == 0:
                    correct += 1
                    harmed += new[j - 1] != old[j - 1]
                else:
                    fixed += new[j - 1] == ref[i - 1]
                i, j = i - 1, j - 1
            elif rows[i][j] == rows[i - 1][j] + 1:
                i -= 1
            else:
                j -= 1
    return {
        "correct_before": correct,
        "harmed": harmed,
        "harmed_share": harmed / correct if correct else 0.0,
        "substitutions_fixed": fixed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark do EXP-011")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    calibration = json.loads((EXPERIMENT / "calibration.json").read_text(encoding="utf-8"))
    params = LexiconParams(**calibration["best"]["params"])
    words = json.loads((DATA / "lexicon-pt.json").read_text(encoding="utf-8"))["words"]
    corrector = Corrector(words, params)
    results = {}
    for name, (refs_path, read_path) in SETS.items():
        refs = json.loads(refs_path.read_text(encoding="utf-8"))["refs"]
        before = json.loads(read_path.read_text(encoding="utf-8"))["items"]
        started = time.perf_counter()
        after = {key: corrector.correct_line(text) for key, text in before.items()}
        per_line_ms = (time.perf_counter() - started) * 1000 / max(1, len(before))
        results[name] = {
            "before": line_metrics(refs, before),
            "after": line_metrics(refs, after),
            "harm": harmed_words(refs, before, after),
            "correction_ms_per_line": per_line_ms,
        }
    main_set = results["lines-exp001"]
    before, after = main_set["before"], main_set["after"]

    def accents(metrics):
        return metrics["cer_by_class"].get("letra acentuada", {}).get("cer", 0.0)

    verdicts = {
        "h1_wer_10_points": {
            "before": before["wer_micro"],
            "after": after["wer_micro"],
            "met": before["wer_micro"] - after["wer_micro"] >= 0.10,
        },
        "h2_cer_3_points": {
            "before": before["cer_micro"],
            "after": after["cer_micro"],
            "met": before["cer_micro"] - after["cer_micro"] >= 0.03,
        },
        "h3_accents_15_points": {
            "before": accents(before),
            "after": accents(after),
            "met": accents(before) - accents(after) >= 0.15,
        },
        "h4_cost": {
            "ms_per_line": main_set["correction_ms_per_line"],
            "met": main_set["correction_ms_per_line"] <= 20,
        },
        "h5_harm": {
            "harmed_share": main_set["harm"]["harmed_share"],
            "met": main_set["harm"]["harmed_share"] <= 0.02,
        },
    }
    report = {
        "schema": "leitorum-di-reading-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-011",
        "git": git_state(),
        "environment": environment_snapshot(),
        "license_status": {
            "lexicon": "wordfreq: código Apache-2.0, dados CC-BY-SA 4.0 (conforme declarado)",
            "bressay": "NEEDS VALIDATION (exceção experimental; não embasa produto)",
        },
        "params": params.to_dict(),
        "validation": {k: calibration[k] for k in ("baseline", "best", "lines")},
        "results": results,
        "verdicts": verdicts,
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for name, item in results.items():
        b, a = item["before"], item["after"]
        print(
            f"{name}: CER {b['cer_micro']:.3f} → {a['cer_micro']:.3f}; "
            f"WER {b['wer_micro']:.3f} → {a['wer_micro']:.3f}; "
            f"acentos {accents(b):.3f} → {accents(a):.3f}; "
            f"prejudicadas {item['harm']['harmed_share']:.3%}"
        )
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
