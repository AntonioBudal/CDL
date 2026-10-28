"""EXP-024 (F04): calibração SÓ nos fluxos de validação; grava ``artifacts/thresholds.json``.

Busca por coordenadas, registrada em ``artifacts/tuning-log.json``:

- **Organizador:** objetivo = média dos perfis do Macro-F1 *holdout* em t = 40 no R1, menos
  10 × a pior queda abaixo do V4 (além de 1 ponto) no R3, em t ∈ {5, 10, 20, 40}.
- **Leitura:** objetivo = queda relativa do CER *holdout* em t = 40 no R1, com as palavras certas
  preservadas ≥ 99,5 %; ``curate_known_min`` é o menor valor com precisão de curadoria ≥ 0,95.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \
        experiments/EXP-024/harness/calibrate.py
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import evaluate as ev  # noqa: E402
import streams  # noqa: E402

ARTIFACTS = HERE.parent / "artifacts"
ORGANIZER_GRID = {
    "eta0": [0.1, 0.3, 0.6],
    "unreviewed_factor": [0.05, 0.2, 0.5],
    "eps_replay": [0.0, 0.02, 0.05, 1.0],
    "mu": [0.005, 0.02, 0.08],
    "delta_max": [2.0, 4.0, 8.0],
    "eps_step": [0.03, 0.05, 0.1],
    "learn_centroids": [True, False],
    "use_T": [True, False],
}
READER_GRID = {
    "theta": [0.5, 1.0, 2.0],
    "candidate_min": [1.0, 2.0],
    "alpha_channel": [5.0, 20.0],
    "weight_book": [1.0, 3.0],
}
CURATE_KNOWN = [2.0, 3.0, 4.0, 6.0]
PROFILES = sorted(streams.load()["profiles"])


def organizer_score(params: dict, log: list) -> float:
    f1_r1, worst = [], []
    for p in PROFILES:
        r1 = ev.run_stream(
            p, "val", "R1", params, {}, checkpoints=(40,), use_reader=False, measure_reader=False
        )
        r3 = ev.run_stream(
            p,
            "val",
            "R3",
            params,
            {},
            checkpoints=(5, 10, 20, 40),
            use_reader=False,
            measure_reader=False,
        )
        base = r1["organizer"][0]["macro_f1"]
        f1_r1.append(r1["organizer"][40]["macro_f1"])
        worst.append(
            max(0.0, base - min(r3["organizer"][t]["macro_f1"] for t in (5, 10, 20, 40)) - 0.01)
        )
    score = statistics.mean(f1_r1) - 10 * statistics.mean(worst)
    log.append(
        {
            "part": "organizer",
            "params": params,
            "f1_r1_t40": [round(v, 4) for v in f1_r1],
            "r3_drop_beyond_1pt": [round(v, 4) for v in worst],
            "score": round(score, 4),
        }
    )
    print(
        f"  {json.dumps({k: params[k] for k in ORGANIZER_GRID if k in params})} -> {score:.4f}",
        flush=True,
    )
    return score


def reader_run(params: dict) -> tuple[float, float, float | None]:
    gains, preserved, precision = [], [], []
    for p in PROFILES:
        run = ev.run_stream(
            p,
            "val",
            "R1",
            {"learn_weights": False, "shadow": False, "replay": False},
            params,
            checkpoints=(40,),
            use_reader=False,
        )
        r = run["reader"][40]
        gains.append(1 - r["cer"] / r["cer_raw"])
        preserved.append(r["correct_words_preserved"])
        if run["curation"]["precision"] is not None:
            precision.append(run["curation"]["precision"])
    return (
        statistics.mean(gains),
        min(preserved),
        (statistics.mean(precision) if precision else None),
    )


def coordinate(grid: dict, start: dict, score) -> dict:
    best = dict(start)
    best_score = score(best)
    for name, values in grid.items():
        for value in values:
            if best.get(name) == value:
                continue
            trial = {**best, name: value}
            s = score(trial)
            if s > best_score + 1e-4:
                best, best_score = trial, s
    return best


def main() -> int:
    started = time.perf_counter()
    log: list = []
    print("organizador (validação)", flush=True)
    start = {k: ev.ao.DEFAULTS[k] for k in ORGANIZER_GRID}
    organizer = coordinate(ORGANIZER_GRID, start, lambda p: organizer_score(p, log))

    print("leitura (validação)", flush=True)

    def reader_score(params):
        gain, preserved, precision = reader_run(params)
        score = gain - (10 * (0.995 - preserved) if preserved < 0.995 else 0.0)
        log.append(
            {
                "part": "reader",
                "params": params,
                "cer_relative_drop": round(gain, 4),
                "preserved_min": preserved,
                "curation_precision": precision,
                "score": round(score, 4),
            }
        )
        print(f"  {json.dumps(params)} -> {score:.4f}", flush=True)
        return score

    reader = coordinate(READER_GRID, {k: ev.aoc.DEFAULTS[k] for k in READER_GRID}, reader_score)
    chosen_known = CURATE_KNOWN[-1]
    for value in CURATE_KNOWN:
        _gain, _preserved, precision = reader_run({**reader, "curate_known_min": value})
        log.append({"part": "curation", "curate_known_min": value, "precision": precision})
        print(f"  curate_known_min={value} -> precisão {precision}", flush=True)
        if precision is not None and precision >= 0.95:
            chosen_known = value
            break
    reader["curate_known_min"] = chosen_known

    thresholds = {
        "experiment": "EXP-024",
        "frozen_before_test": True,
        "split_used": "val",
        "organizer": organizer,
        "reader": reader,
        "hypotheses": {
            "H1": {"min_gain_macro_f1_mean": 0.08, "min_gain_references_profile_P1": 0.20},
            "H2": {
                "min_cer_relative_drop": 0.15,
                "min_accent_relative_drop": 0.30,
                "min_preserved": 0.995,
                "min_curation_precision": 0.95,
            },
            "H3": {"max_drop_below_v4_any_t": 0.01, "min_share_of_r1_gain": 0.70},
            "H4": {"min_ratio_first_click_gain": 2.0},
            "H5": {
                "update_ms_p95": 25.0,
                "organize_overhead_ms_p95": 5.0,
                "state_kb_500_studies": 512.0,
                "replay_500_s": 2.0,
            },
        },
        "hypotheses_note": "Limiares da spec §7 mantidos depois da validação (nenhum afrouxado).",
        "elapsed_s": round(time.perf_counter() - started, 1),
    }
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / "thresholds.json").write_text(
        json.dumps(thresholds, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    (ARTIFACTS / "tuning-log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"organizer": organizer, "reader": reader}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
