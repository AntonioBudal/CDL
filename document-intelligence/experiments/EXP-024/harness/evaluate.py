"""EXP-024 (F04): curvas de aprendizado, ablações, estresse, 1 clique e custo.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \\
        experiments/EXP-024/harness/evaluate.py --split test \
        --out evaluation/benchmarks/<arquivo>.json

Os parâmetros vêm de ``artifacts/thresholds.json``, congelado na validação antes de abrir o teste.
Só dados fictícios; a saída tem só números e nomes fixos.
"""

from __future__ import annotations

import argparse
import difflib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import adaptive_ocr_corrector as aoc  # noqa: E402
import adaptive_organizer as ao  # noqa: E402
import metrics  # noqa: E402  (EXP-023)
import simulator as sim  # noqa: E402
import state as st  # noqa: E402
import streams  # noqa: E402

THRESHOLDS = HERE.parent / "artifacts" / "thresholds.json"
CHECKPOINTS = (1, 5, 10, 20, 40)
ACCENTED = set("áàâãéêíóôõúüç")
LABEL = {"summary": 0, "explanation": 1, "concepts": 2, "references": 3}

# escada cumulativa (spec §8.4); cada degrau liga o que o anterior tinha mais um componente
LADDER = {
    "E1_diff": {
        "learn_weights": True,
        "learn_centroids": False,
        "use_book": False,
        "use_extra_cues": False,
        "use_gating": False,
        "unreviewed_factor": 1.0,
        "use_T": False,
        "shadow": False,
        "replay": False,
    },
    "E2_contexto": {
        "learn_weights": True,
        "learn_centroids": True,
        "use_book": True,
        "use_extra_cues": True,
        "use_gating": False,
        "unreviewed_factor": 1.0,
        "use_T": False,
        "shadow": False,
        "replay": False,
    },
    "E3_E6_gating": {
        "learn_weights": True,
        "learn_centroids": True,
        "use_book": True,
        "use_extra_cues": True,
        "use_gating": True,
        "use_T": False,
        "shadow": False,
        "replay": False,
    },
    "E5_completo": {},
}
LEAVE_ONE_OUT = {
    "sem_pistas_novas": {"use_extra_cues": False},
    "sem_centroides": {"learn_centroids": False},
    "sem_livro": {"use_book": False},
    "sem_gating": {"use_gating": False, "unreviewed_factor": 1.0},
    "sem_T_user": {"use_T": False},
    "sem_portao_sombra": {"shadow": False},
    "sem_replay": {"replay": False},
    "sem_travas": {"shadow": False, "replay": False, "delta_max": 1e9},
}


def load_thresholds() -> dict:
    if THRESHOLDS.exists():
        return json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    return {"organizer": {}, "reader": {}}


# --- medidas no holdout --------------------------------------------------------------------------


def holdout_organizer(
    engine, user: str, stream: dict, adaptive: bool = True, cer: float = 0.0, reader=None
):
    """Macro-F1 por caractere (régua do EXP-023) nas páginas holdout, sem aprender com elas."""
    scores = metrics.Scores()
    for book, pages in stream["holdout"].items():
        for page in pages:
            if cer > 0:
                lines = sim.read_page(page, cer, "holdout")
                shown = [ln["text"] for ln in lines]
                if reader is not None:
                    shown = reader.correct_lines(user, book, shown)
                text = "\n".join(shown)
                gold = []
                for k, (ln, t) in enumerate(zip(lines, shown, strict=False)):
                    if k:
                        gold.append(gold[-1] if gold else "e")
                    gold.extend(sim.transfer_labels(ln["truth"], ln["truth_labels"], t))
                units = [0] * len(text)
                layout = [
                    {"text": t, "bbox": ln["bbox"], "confidence": ln["confidence"]}
                    for ln, t in zip(lines, shown, strict=False)
                ]
            else:
                text, gold, units = streams.page_text(page)
                layout = streams.layout(page)
            result = engine.organize(user, text, layout, book, adaptive=adaptive)
            scores.add(text, gold, units, result)
    report = scores.report()
    return {
        "macro_f1": report["macro_f1_chars"],
        "f1_references": report["per_section_chars"]["references"]["f1"],
        "per_section_f1": {s: report["per_section_chars"][s]["f1"] for s in streams.SECTIONS},
        "windowdiff": report["windowdiff"],
        "chars_to_move": report["char_error_effort"],
    }


def _accent_errors(truth: str, text: str) -> tuple[int, int]:
    total = sum(ch in ACCENTED for ch in truth)
    wrong = 0
    for op, i1, i2, _j1, _j2 in difflib.SequenceMatcher(
        None, truth, text, autojunk=False
    ).get_opcodes():
        if op != "equal":
            wrong += sum(ch in ACCENTED for ch in truth[i1:i2])
    return wrong, total


def holdout_reader(reader, user: str, stream: dict, cer: float = 0.25) -> dict:
    """CER, WER, erro em acentos e palavras certas preservadas, antes e depois da pós-correção."""
    acc = {"chars": 0, "raw_err": 0, "fix_err": 0, "words": 0, "raw_wrong": 0, "fix_wrong": 0}
    acc.update({"acc_total": 0, "acc_raw": 0, "acc_fix": 0, "right": 0, "damaged": 0})
    for book, pages in stream["holdout"].items():
        for page in pages:
            lines = sim.read_page(page, cer, "holdout")
            fixed = (
                reader.correct_lines(user, book, [ln["text"] for ln in lines])
                if reader
                else [ln["text"] for ln in lines]
            )
            for ln, f in zip(lines, fixed, strict=False):
                truth = ln["truth"]
                acc["chars"] += len(truth)
                acc["raw_err"] += sim.levenshtein(truth, ln["text"])
                acc["fix_err"] += sim.levenshtein(truth, f)
                tw, rw, fw = truth.split(), ln["text"].split(), f.split()
                acc["words"] += len(tw)
                acc["raw_wrong"] += _word_errors(tw, rw)
                acc["fix_wrong"] += _word_errors(tw, fw)
                w1, total = _accent_errors(truth, ln["text"])
                w2, _ = _accent_errors(truth, f)
                acc["acc_total"] += total
                acc["acc_raw"] += w1
                acc["acc_fix"] += w2
                if len(rw) == len(fw):
                    for r, x in zip(rw, fw, strict=False):
                        if r in tw:
                            acc["right"] += 1
                            acc["damaged"] += x != r
    return {
        "cer_raw": round(acc["raw_err"] / acc["chars"], 4),
        "cer": round(acc["fix_err"] / acc["chars"], 4),
        "wer_raw": round(acc["raw_wrong"] / acc["words"], 4),
        "wer": round(acc["fix_wrong"] / acc["words"], 4),
        "accent_error_raw": round(acc["acc_raw"] / max(1, acc["acc_total"]), 4),
        "accent_error": round(acc["acc_fix"] / max(1, acc["acc_total"]), 4),
        "correct_words_preserved": round(1 - acc["damaged"] / max(1, acc["right"]), 4),
    }


def _word_errors(truth: list[str], hyp: list[str]) -> int:
    matcher = difflib.SequenceMatcher(None, truth, hyp, autojunk=False)
    return len(truth) - sum(block.size for block in matcher.get_matching_blocks())


# --- um fluxo -------------------------------------------------------------------------------------


def run_stream(
    profile: str,
    split: str,
    regime: str,
    org_params: dict,
    reader_params: dict,
    checkpoints=CHECKPOINTS,
    use_reader: bool = True,
    measure_reader: bool = True,
    cer: float = 0.25,
) -> dict:
    stream = streams.stream(profile, split)
    engine = ao.AdaptiveOrganizer(org_params)
    reader = aoc.AdaptiveReader(engine.state_for, reader_params)
    user = f"u-{profile}-{split}"
    plan = sim.noisy_plan(stream["adapt"], regime)
    out = {"organizer": {}, "reader": {}}
    out["organizer"][0] = holdout_organizer(engine, user, stream, adaptive=False)
    if measure_reader:
        out["reader"][0] = holdout_reader(reader, user, stream, cer)
    org_ms, read_ms, rejected, gated, curated, curated_ok = [], [], 0, 0, 0, 0
    for page in stream["adapt"]:

        def organize(text, layout, book):
            return engine.organize(user, text, layout, book)

        def read(lines, book):
            return reader.correct_lines(user, book, [ln["text"] for ln in lines])

        feedback, truth = sim.session(
            page,
            regime,
            organize,
            read if use_reader else None,
            cer=cer,
            noisy=plan.get(page["id"]),
        )
        t0 = time.perf_counter()
        report = engine.learn(feedback)
        org_ms.append((time.perf_counter() - t0) * 1000)
        rejected += not report.get("accepted", True)
        gated += bool(report.get("gated"))
        reader_gate = report.get("reason") == "low_rating_without_corrections"
        t0 = time.perf_counter()
        rep = reader.learn(feedback, gated=reader_gate)
        read_ms.append((time.perf_counter() - t0) * 1000)
        for item in rep["curated"]:
            curated += 1
            curated_ok += any(
                item["text"] == c or (len(item["text"]) >= 5 and item["text"] in c)
                for c in truth["clean_lines"]
            )
        if page["t"] in checkpoints:
            out["organizer"][page["t"]] = holdout_organizer(engine, user, stream)
            if measure_reader:
                out["reader"][page["t"]] = holdout_reader(reader, user, stream, cer)
    out["costs"] = {
        "organizer_update_ms_p50": round(statistics.median(org_ms), 2),
        "organizer_update_ms_p95": round(sorted(org_ms)[int(0.95 * len(org_ms)) - 1], 2),
        "reader_update_ms_p50": round(statistics.median(read_ms), 2),
        "reader_update_ms_p95": round(sorted(read_ms)[int(0.95 * len(read_ms)) - 1], 2),
        "state_kb": round(st.size_bytes(engine.state_for(user)) / 1024, 1),
    }
    out["updates"] = {"rejected": rejected, "gated": gated, "pages": len(stream["adapt"])}
    out["curation"] = {
        "pairs": curated,
        "precision": round(curated_ok / curated, 4) if curated else None,
    }
    out["_engine"], out["_reader"], out["_user"] = engine, reader, user
    return out


def strip(run: dict) -> dict:
    return {k: v for k, v in run.items() if not k.startswith("_")}


# --- E4: um clique --------------------------------------------------------------------------


def clicks(engine, user: str, stream: dict, k_max: int = 3, adaptive: bool = True) -> dict:
    """Macro-F1 depois de k cliques; o leitor corrige, na ordem mostrada, os itens errados."""
    strategies = {
        "margem_sem_redecodificar": ("margin_order", False, False),
        "entropia_x_acoplamento_redecodifica": ("review_order", True, False),
        "entropia_x_acoplamento_passo_local": ("review_order", True, True),
    }
    out = {}
    for name, (order_key, redecode, local) in strategies.items():
        per_k = [metrics.Scores() for _ in range(k_max + 1)]
        fixed_chars = [0] * (k_max + 1)
        for book, pages in stream["holdout"].items():
            for page in pages:
                text, gold, units = streams.page_text(page)
                result = engine.organize(user, text, streams.layout(page), book, adaptive=adaptive)
                truth = [
                    max(
                        streams.SECTIONS,
                        key=lambda s, seg=seg: sum(
                            metrics.CODE[g] == s for g in gold[seg["start"] : seg["end"]]
                        ),
                    )
                    for seg in result["segments"]
                ]
                per_k[0].add(text, gold, units, result)
                current = result
                wrong_order = [
                    i for i in result[order_key] if result["segments"][i]["section"] != truth[i]
                ]
                done = 0
                for k in range(1, k_max + 1):
                    remaining = [
                        i for i in wrong_order if current["segments"][i]["section"] != truth[i]
                    ]
                    if remaining:
                        i = remaining[0]
                        if redecode:
                            current = engine.click(current, i, truth[i], local=local)
                        else:
                            segments = [dict(s) for s in current["segments"]]
                            segments[i]["section"] = truth[i]
                            current = {**current, "segments": segments}
                        done += 1
                    per_k[k].add(text, gold, units, current)
                    fixed_chars[k] = fixed_chars[k]
        out[name] = [per_k[k].report()["macro_f1_chars"] for k in range(k_max + 1)]
    out["gain_first_click"] = {
        name: round(v[1] - v[0], 4) for name, v in out.items() if isinstance(v, list)
    }
    return out


# --- custo de reconstruir o estado por replay -----------------------------------------------


def replay_cost(org_params: dict, n_studies: int = 500) -> dict:
    """Reconstrói o estado com 500 estudos fictícios (16 livros); mede tempo e tamanho."""
    pages = [
        p
        for split in streams.SPLITS
        for s in streams.all_streams(split).values()
        for p in s["adapt"]
    ]
    pages += [
        p
        for split in streams.SPLITS
        for s in streams.all_streams(split).values()
        for hp in s["holdout"].values()
        for p in hp
    ]
    engine = ao.AdaptiveOrganizer(org_params)
    t0 = time.perf_counter()
    for page in pages[:n_studies]:
        columns = {
            s: "\n".join(u["text"] for u in page["source_units"] if streams.CODE[s] == u["section"])
            for s in streams.SECTIONS
        }
        engine.learn_study("u-replay", page["book_id"], columns)
    seconds = time.perf_counter() - t0
    state = engine.state_for("u-replay")
    return {
        "studies": min(n_studies, len(pages)),
        "books": len(state["organizer"]["books"]),
        "seconds": round(seconds, 2),
        "state_kb": round(st.size_bytes(state) / 1024, 1),
    }


def organize_overhead(org_params: dict, profile: str = "P4") -> dict:
    """Acréscimo de latência da organização adaptativa sobre o V4 (mesmas páginas)."""
    run = run_stream(
        profile,
        "test",
        "R1",
        org_params,
        {},
        checkpoints=(),
        use_reader=False,
        measure_reader=False,
    )
    engine, user, stream = run["_engine"], run["_user"], streams.stream(profile, "test")
    static_ms, adaptive_ms = [], []
    for book, pages in stream["holdout"].items():
        for page in pages:
            text, _g, _u = streams.page_text(page)
            layout = streams.layout(page)
            for adaptive, bucket in ((False, static_ms), (True, adaptive_ms)):
                t0 = time.perf_counter()
                engine.organize(user, text, layout, book, adaptive=adaptive)
                bucket.append((time.perf_counter() - t0) * 1000)

    def p95(xs):
        return round(sorted(xs)[int(0.95 * len(xs)) - 1], 2)

    return {
        "static_ms_p95": p95(static_ms),
        "adaptive_ms_p95": p95(adaptive_ms),
        "overhead_ms_p95": round(p95(adaptive_ms) - p95(static_ms), 2),
    }


# --- execução ------------------------------------------------------------------------------------


def git_state() -> dict:
    root = HERE.parents[2]
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", "."], cwd=root, capture_output=True, text=True
    ).stdout.strip()
    return {"commit": head, "clean": not dirty}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=streams.SPLITS, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    thresholds = load_thresholds()
    org_p, read_p = thresholds.get("organizer", {}), thresholds.get("reader", {})
    profiles = sorted(streams.load()["profiles"])
    bench = {
        "experiment": "EXP-024",
        "split": args.split,
        "git": git_state(),
        "thresholds_sha256": None,
    }
    if THRESHOLDS.exists():
        import hashlib

        bench["thresholds_sha256"] = hashlib.sha256(
            THRESHOLDS.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
    started = time.perf_counter()
    full = {}
    for regime in sim.REGIMES:
        full[regime] = {}
        for p in profiles:
            run = run_stream(p, args.split, regime, org_p, read_p)
            full[regime][p] = strip(run)
            if regime == "R1":
                full[regime][p]["clicks_t0"] = clicks(
                    run["_engine"], run["_user"], streams.stream(p, args.split), adaptive=False
                )
                full[regime][p]["clicks_t40"] = clicks(
                    run["_engine"], run["_user"], streams.stream(p, args.split)
                )
            print(
                f"{regime} {p}: F1 {full[regime][p]['organizer'][0]['macro_f1']}"
                f" -> {full[regime][p]['organizer'][40]['macro_f1']}",
                flush=True,
            )
    bench["full"] = full
    bench["ladder_R1"] = {}
    for name, overrides in LADDER.items():
        params = {**org_p, **overrides}
        bench["ladder_R1"][name] = {
            p: strip(run_stream(p, args.split, "R1", params, read_p, measure_reader=False))
            for p in profiles
        }
        print(f"escada {name}", flush=True)
    bench["leave_one_out_R1"] = {}
    for name, overrides in LEAVE_ONE_OUT.items():
        params = {**org_p, **overrides}
        bench["leave_one_out_R1"][name] = {
            p: strip(run_stream(p, args.split, "R1", params, read_p, measure_reader=False))
            for p in profiles
        }
        print(f"sem {name}", flush=True)
    bench["stress_R3_without_locks"] = {
        p: strip(
            run_stream(
                p,
                args.split,
                "R3",
                {
                    **org_p,
                    **LEAVE_ONE_OUT["sem_travas"],
                    "use_gating": False,
                    "unreviewed_factor": 1.0,
                },
                {**read_p, "use_filter": False},
            )
        )
        for p in profiles
    }
    reader_ablation = {}
    for name, overrides in {
        "sem_correcao": {"use_lexicon": False},
        "so_lexico": {"use_confusions": False},
        "so_lexico_sem_livro": {"use_confusions": False, "use_book": False},
        "lexico_e_confusoes": {},
    }.items():
        reader_ablation[name] = {
            p: strip(
                run_stream(
                    p,
                    args.split,
                    "R1",
                    org_p,
                    {**read_p, **overrides},
                    checkpoints=(40,),
                    use_reader=False,
                )
            )["reader"]
            for p in profiles
        }
    bench["reader_ablation_R1"] = reader_ablation
    bench["reader_cer10_R1"] = {
        p: strip(run_stream(p, args.split, "R1", org_p, read_p, checkpoints=(40,), cer=0.10))[
            "reader"
        ]
        for p in profiles
    }
    bench["costs"] = {"replay_500": replay_cost(org_p), "organize": organize_overhead(org_p)}
    bench["elapsed_s"] = round(time.perf_counter() - started, 1)
    Path(args.out).write_text(
        json.dumps(bench, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print(f"gravado em {args.out} ({bench['elapsed_s']} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
