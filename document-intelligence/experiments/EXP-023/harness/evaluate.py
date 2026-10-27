"""EXP-023, F05: avaliação das linhas de base e variantes (spec §8.3) num conjunto de páginas.

``--split val``: só para registrar os limiares (``thresholds.json``) antes de abrir o teste.
``--split test``: exige ``thresholds.json``; grava o benchmark (só números) com os vereditos.

Variantes: B0 classe majoritária; B1 só cabeçalhos explícitos (o que o import_parser faz; o resto
vai para Explicação, como na importação); B2 só pistas; B3 só léxico; V1 híbrido isolado; V2 +
transições; V3 + custo de troca por S; V4 + propagação (pipeline completa). V5 (L1/L3) não roda:
nenhum corpus ou embedding com licença verificada (spec §4.2). Cada variante em 3 níveis de ruído,
com e sem geometria.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import organizer as org
from metrics import CODE, Scores
from pages import build_pages, layout, page_text, with_noise
from train import ART, CERS, NOISE, ROOT

THRESHOLDS = ART / "thresholds.json"
VARIANTS = ("B0", "B1", "B2", "B3", "V1", "V2", "V3", "V4")
INDEPENDENT = org.Options(use_T=False, use_S=False, use_propagation=False)
OPTIONS = {
    "B2": INDEPENDENT,
    "B3": INDEPENDENT,
    "V1": INDEPENDENT,
    "V2": org.Options(use_T=True, use_S=False, use_propagation=False),
    "V3": org.Options(use_T=True, use_S=True, use_propagation=False),
    "V4": org.Options(),
}


def load_model() -> tuple[org.Model, dict]:
    data = json.loads((ART / "organizer-v1.json").read_text(encoding="utf-8"))
    return org.Model.from_json(data), data


def variant_model(base: org.Model, data: dict, which: str) -> org.Model:
    model = copy.copy(base)
    model.params = dict(base.params)
    if which in data["baselines"]:
        model.weights = data["baselines"][which]["weights"]
        model.bias = data["baselines"][which]["bias"]
        model.params["beta"] = data["baselines"][which]["beta"]
    return model


def fixed_result(units, section_of) -> dict:
    return {
        "segments": [
            {
                "index": i,
                "start": u.start,
                "end": u.end,
                "section": section_of(u),
                "confidence": 1.0,
                "margin": 1.0,
                "review": False,
            }
            for i, u in enumerate(units)
        ]
    }


def git_state() -> dict:
    def git(*args):
        try:
            return subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def run(split: str) -> dict:
    noise_model = json.loads(NOISE.read_text(encoding="utf-8"))
    pages = build_pages()
    base, data = load_model()
    engines = {
        "B2": org.Organizer(variant_model(base, data, "features")),
        "B3": org.Organizer(variant_model(base, data, "lexical")),
        "full": org.Organizer(base),
    }
    majority = Counter(
        CODE[lab] for p in pages["train"] for line in p["lines"] for lab in line["labels"]
    ).most_common(1)[0][0]
    results = {}
    for cer in CERS:
        for geo in (True, False):
            key = f"cer{int(cer * 100):02d}-{'geo' if geo else 'sem-geo'}"
            scores = {v: Scores() for v in VARIANTS}
            for page in pages[split]:
                noisy = with_noise(page, noise_model, cer)
                text, labels, units_gold = page_text(noisy)
                lay = layout(noisy) if geo else None
                for v in VARIANTS:
                    if v == "B0":
                        units, _ = org.segment(text, lay)
                        result = fixed_result(units, lambda u: majority)
                    elif v == "B1":
                        units, _ = org.segment(text, lay)
                        result = fixed_result(units, lambda u: u.heading or "explanation")
                    else:
                        engine = engines["B2" if v == "B2" else "B3" if v == "B3" else "full"]
                        started = time.perf_counter()
                        result = engine.organize(text, lay, copy.copy(OPTIONS[v]))
                        elapsed = (time.perf_counter() - started) * 1000
                    scores[v].add(text, labels, units_gold, result, elapsed if v == "V4" else None)
            results[key] = {v: s.report() for v, s in scores.items()}
            v4 = results[key]["V4"]
            print(
                f"{split} {key}: "
                + " ".join(f"{v}={results[key][v]['macro_f1_chars']:.3f}" for v in VARIANTS)
                + f" | V4 WD={v4['windowdiff']:.3f} p95={v4['latency_ms_p95']} ms"
            )
    return results


def verdicts(results: dict, thresholds: dict) -> dict:
    out = {}
    for cond in ("cer00-geo", "cer25-geo"):
        r = results[cond]
        best_part = max(r["B2"]["macro_f1_chars"], r["B3"]["macro_f1_chars"])
        out[f"h1_{cond}"] = {
            "v1": r["V1"]["macro_f1_chars"],
            "best_component": best_part,
            "met": r["V1"]["macro_f1_chars"] - best_part >= thresholds["h1_min_gain"],
        }
    wd_gain, f1_drop = [], []
    for r in results.values():
        wd_gain.append(1 - r["V4"]["windowdiff"] / max(1e-9, r["V1"]["windowdiff"]))
        f1_drop.append(r["V1"]["macro_f1_chars"] - r["V4"]["macro_f1_chars"])
    out["h2"] = {
        "windowdiff_relative_reduction_mean": round(sum(wd_gain) / len(wd_gain), 4),
        "max_macro_f1_drop": round(max(f1_drop), 4),
        "met": sum(wd_gain) / len(wd_gain) >= thresholds["h2_min_wd_reduction"]
        and max(f1_drop) <= thresholds["h2_max_f1_drop"],
    }
    p95 = max(r["V4"]["latency_ms_p95"] for r in results.values())
    out["h3"] = {"latency_ms_p95_worst": p95, "met": p95 <= thresholds["h3_max_p95_ms"]}
    gate_clean = results["cer00-sem-geo"]["V4"]["macro_f1_chars"]
    gate_noisy = results["cer25-geo"]["V4"]["macro_f1_chars"]
    out["product_gate"] = {
        "clean_typed_v4": gate_clean,
        "cer25_photo_v4": gate_noisy,
        "met": gate_clean >= thresholds["gate_clean"] and gate_noisy >= thresholds["gate_noisy"],
    }
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Avaliação do EXP-023")
    parser.add_argument("--split", choices=("val", "test"), required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.split == "test" and not THRESHOLDS.is_file():
        raise SystemExit(
            "registre os limiares (thresholds.json) na validação antes de abrir o teste"
        )
    results = run(args.split)
    if args.split == "val":
        (ART / "val-results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
        return 0
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    report = {
        "schema": "leitorum-di-organizer-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-023",
        "git": git_state(),
        "split": "test",
        "data": (
            "D-sintético (fictício, MIT): 4 temas de teste x 6 páginas;"
            " ruído do EXP-015 (só estatísticas)"
        ),
        "artifact_sha256": (ART / "organizer-v1.sha256").read_text(encoding="utf-8").strip(),
        "thresholds": thresholds,
        "results": results,
        "verdicts": verdicts(results, thresholds),
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    for name, verdict in report["verdicts"].items():
        print(name, "→", verdict["met"], {k: v for k, v in verdict.items() if k != "met"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
