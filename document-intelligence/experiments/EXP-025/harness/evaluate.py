"""EXP-025, F03: ``organizer-v1`` contra ``organizer-v2``, ambos estáticos.

- **H1:** *holdout* dos fluxos do EXP-024 (texto limpo, com geometria), por perfil.
- **H2:** páginas do EXP-023 nas 6 condições (CER 0, 10 e 25 %, com e sem geometria).
- **H4:** latência p95 por página, nas mesmas páginas, com os dois modelos.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \\
        experiments/EXP-025/harness/evaluate.py --split test --out <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (HERE, EXPS / "EXP-023" / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))

import metrics  # noqa: E402  (EXP-023)
import organizer as org  # noqa: E402
import organizer_v2 as v2  # noqa: E402
import pages  # noqa: E402  (EXP-023)
import streams  # noqa: E402  (EXP-024)

V1 = EXPS / "EXP-023" / "artifacts" / "organizer-v1.json"
NOISE = EXPS.parent / "dataset" / "processed" / "exp-023" / "noise-model.json"


def load_v1() -> org.Organizer:
    return org.Organizer(org.Model.from_json(json.loads(V1.read_text(encoding="utf-8"))))


def summary(scores: metrics.Scores) -> dict:
    r = scores.report()
    return {
        "macro_f1": r["macro_f1_chars"],
        "per_section_f1": {s: r["per_section_chars"][s]["f1"] for s in metrics.SECTIONS},
        "windowdiff": r["windowdiff"],
        "chars_to_move": r["char_error_effort"],
        "ece": r["ece"],
        "latency_ms_p95": r["latency_ms_p95"],
    }


def run(engine, items) -> dict:
    scores = metrics.Scores()
    for text, gold, units, lines in items:
        t0 = time.perf_counter()
        result = engine.organize(text, lines)
        scores.add(text, gold, units, result, (time.perf_counter() - t0) * 1000)
    return summary(scores)


def exp024_items(split: str, profile: str) -> list:
    st = streams.stream(profile, split)
    out = []
    for book_pages in st["holdout"].values():
        for page in book_pages:
            text, gold, units = streams.page_text(page)
            out.append((text, gold, units, streams.layout(page)))
    return out


def exp023_items(split: str, cer: float, geo: bool) -> list:
    noise = json.loads(NOISE.read_text(encoding="utf-8"))
    out = []
    for page in pages.build_pages()[split]:
        noisy = pages.with_noise(page, noise, cer)
        text, gold, units = pages.page_text(noisy)
        out.append((text, gold, units, pages.layout(noisy) if geo else None))
    return out


def git(*args: str) -> str:
    root = EXPS.parent
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout.strip()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("val", "test"), required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    engines = {"v1": load_v1(), "v2": v2.load()}
    bench = {
        "experiment": "EXP-025",
        "split": args.split,
        "git": {
            "commit": git("rev-parse", "--short", "HEAD"),
            "clean": not git("status", "--porcelain", "--", "."),
        },
        "artifact_sha256": hashlib.sha256(
            (HERE.parent / "artifacts" / "organizer-v2.json").read_bytes()
        ).hexdigest(),
        "exp024_holdout": {},
        "exp023": {},
    }
    for profile in sorted(streams.load()["profiles"]):
        items = exp024_items(args.split, profile)
        bench["exp024_holdout"][profile] = {name: run(e, items) for name, e in engines.items()}
    for cer in (0.0, 0.10, 0.25):
        for geo in (True, False):
            key = f"cer{int(cer * 100):02d}_{'geo' if geo else 'sem_geo'}"
            items = exp023_items(args.split, cer, geo)
            bench["exp023"][key] = {name: run(e, items) for name, e in engines.items()}
    for name in engines:
        bench[f"exp024_mean_macro_f1_{name}"] = round(
            sum(bench["exp024_holdout"][p][name]["macro_f1"] for p in bench["exp024_holdout"]) / 4,
            4,
        )
    text = json.dumps(bench, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    for p, r in bench["exp024_holdout"].items():
        print(
            p,
            "v1",
            r["v1"]["macro_f1"],
            r["v1"]["per_section_f1"]["references"],
            "| v2",
            r["v2"]["macro_f1"],
            r["v2"]["per_section_f1"]["references"],
        )
    for k, r in bench["exp023"].items():
        print(
            k,
            "v1",
            r["v1"]["macro_f1"],
            r["v1"]["latency_ms_p95"],
            "| v2",
            r["v2"]["macro_f1"],
            r["v2"]["latency_ms_p95"],
        )
    print("média EXP-024", bench["exp024_mean_macro_f1_v1"], "->", bench["exp024_mean_macro_f1_v2"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
