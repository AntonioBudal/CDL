"""T004 — métricas do EXP-027: CER/WER por página e no total, quebra do erro por origem, fórmulas,
palavras quase certas, correlação com as classes manuais e as medidas automáticas da foto.
Python puro. Saída só com números: ``processed/exp-027/score.json`` (completo, fora do Git) e o
benchmark versionado em ``evaluation/benchmarks/`` (agregados e por página, sem texto).

Uso: ``python score.py --system motor [--benchmark]``; ``--system`` escolhe a pasta de leituras em
``processed/exp-027/<system>/`` (``motor`` ou um VLM do T005).
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import align
import textnorm
from lexicon import Lexicon
from paths import CLASSIFICATION, DI_ROOT, MANIFEST, PROCESSED, REFERENCE, SPLITS

CLASS_KEYS = ("escrita", "formulas", "foto", "papel", "layout")


def git_state() -> dict:
    def run(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=str(DI_ROOT), capture_output=True, text=True, check=False
        ).stdout.strip()

    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain"))}


def load_system_lines(system_dir: Path, pid: str) -> list[str] | None:
    path = system_dir / f"{pid}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return [line["text"] for line in data["lines"]]


def mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 4) if values else None


def aggregate(scores: dict[str, align.PageScore], ids: list[str]) -> dict:
    """Totais sobre um conjunto de páginas (micro: soma de distâncias / soma de caracteres)."""
    chosen = [scores[p] for p in ids if p in scores]
    if not chosen:
        return {"pages": 0}
    ref_chars = sum(s.ref_chars for s in chosen)
    total = sum(s.distance_total for s in chosen)
    detail: Counter = Counter()
    words: Counter = Counter()
    for s in chosen:
        detail += s.recognition_detail
        words += s.words
    sub_total = words["sub_d1"] + words["sub_d2"] + words["sub_d3plus"]
    words_wrong = (
        sub_total + words["words_deleted"] + words["words_inserted"] + words["words_missing_lines"]
    )
    return {
        "pages": len(chosen),
        "ref_chars": ref_chars,
        "cer_micro": round(total / ref_chars, 4) if ref_chars else None,
        "cer_page_mean": mean([s.cer_total for s in chosen]),
        "cer_page_median": round(statistics.median(s.cer_total for s in chosen), 4),
        "wer_page_mean": mean([s.wer for s in chosen]),
        "origins": {
            key: round(sum(getattr(s, attr) for s in chosen) / total, 4) if total else None
            for key, attr in (
                ("order", "order"),
                ("missing_lines", "missing_chars"),
                ("spurious_lines", "spurious_chars"),
                ("recognition", "recognition"),
                ("residual", "residual"),
            )
        },
        "lines": {
            "ref": sum(len(s.matching.groups) + len(s.matching.missing) for s in chosen)
            + sum(sum(len(r) - 1 for r, _ in s.matching.groups) for s in chosen),
            "one_to_one": sum(s.matching.one_to_one for s in chosen),
            "merged_groups": sum(s.matching.merged for s in chosen),
            "split_groups": sum(s.matching.split for s in chosen),
            "missing": sum(len(s.matching.missing) for s in chosen),
            "spurious": sum(len(s.matching.spurious) for s in chosen),
            "inversions": sum(s.inversions for s in chosen),
        },
        "recognition": {
            "chars_formula": detail["chars_formula"],
            "chars_text": detail["chars_text"],
            "errors_formula": detail["errors_formula"],
            "errors_text": detail["errors_text"],
            "cer_formula": round(detail["errors_formula"] / detail["chars_formula"], 4)
            if detail["chars_formula"]
            else None,
            "cer_text": round(detail["errors_text"] / detail["chars_text"], 4)
            if detail["chars_text"]
            else None,
            "share_of_recognition_errors_in_formula": round(
                detail["errors_formula"] / (detail["errors_formula"] + detail["errors_text"]), 4
            )
            if detail["errors_formula"] + detail["errors_text"]
            else None,
            "share_of_total_distance_in_formula": round(detail["errors_formula"] / total, 4)
            if total
            else None,
        },
        "words": {
            "ref": words["words_ref"] + words["words_missing_lines"],
            "ok": words["words_ok"],
            "wrong": words_wrong,
            "sub_d1": words["sub_d1"],
            "sub_d2": words["sub_d2"],
            "sub_d3plus": words["sub_d3plus"],
            "deleted": words["words_deleted"],
            "inserted": words["words_inserted"],
            "in_missing_lines": words["words_missing_lines"],
            "near_miss_share_of_wrong": round((words["sub_d1"] + words["sub_d2"]) / words_wrong, 4)
            if words_wrong
            else None,
            "lexicon_fixable_d1": words["lex_fix_d1"],
            "lexicon_fixable_d2": words["lex_fix_d2"],
            "lexicon_ambiguous": words["lex_ambiguous"],
            "lexicon_ref_unknown": words["lex_ref_unknown"],
            "lexicon_hyp_known": words["lex_hyp_known"],
        },
    }


def by_class(scores: dict[str, align.PageScore], classes: dict[str, dict], ids: list[str]) -> dict:
    out = {}
    for key in CLASS_KEYS:
        groups: dict[str, list[str]] = defaultdict(list)
        for pid in ids:
            if pid in scores and classes.get(pid, {}).get(key):
                groups[classes[pid][key]].append(pid)
        out[key] = {
            value: {
                "pages": len(pids),
                "cer_micro": aggregate(scores, pids)["cer_micro"],
                "cer_recognition_only": round(
                    sum(scores[p].recognition for p in pids)
                    / max(1, sum(scores[p].ref_chars - scores[p].missing_chars for p in pids)),
                    4,
                ),
            }
            for value, pids in sorted(groups.items())
        }
    return out


def quality_correlation(scores: dict[str, align.PageScore], quality: dict, ids: list[str]) -> dict:
    """Correlação de Spearman entre cada medida automática da foto e o CER de página."""
    out = {}
    for measure in ("laplacian_var", "brightness_mean", "brightness_std", "shade_lr", "shade_tb"):
        pairs = [
            (quality[p][measure], scores[p].cer_total) for p in ids if p in scores and p in quality
        ]
        if len(pairs) < 4:
            continue
        out[measure] = {"pages": len(pairs), "spearman": round(spearman(pairs), 3)}
    return out


def spearman(pairs: list[tuple[float, float]]) -> float:
    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        r = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r

    xs, ys = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    n = len(pairs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    vx = sum((x - mx) ** 2 for x in xs) ** 0.5
    vy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pontuação do EXP-027")
    parser.add_argument("--system", default="motor")
    parser.add_argument("--benchmark", action="store_true", help="grava o JSON versionado")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    system_dir = PROCESSED / args.system
    quality = (
        json.loads((PROCESSED / "quality.json").read_text(encoding="utf-8"))
        if (PROCESSED / "quality.json").is_file()
        else {}
    )
    split_path = SPLITS / "test-manifest.json"
    split = json.loads(split_path.read_text(encoding="utf-8")) if split_path.is_file() else None
    lexicon = Lexicon.load()
    classes = {}
    scores: dict[str, align.PageScore] = {}
    skipped = {"no_reference": [], "no_reading": [], "empty_reference": []}
    for pid in manifest["pages"]:
        cls_path = CLASSIFICATION / f"{pid}.json"
        if cls_path.is_file():
            data = json.loads(cls_path.read_text(encoding="utf-8"))
            classes[pid] = {k: data.get(k) for k in CLASS_KEYS}
        ref_path = REFERENCE / f"{pid}.txt"
        if not ref_path.is_file():
            skipped["no_reference"].append(pid)
            continue
        ref_lines = textnorm.text_lines(
            textnorm.parse_reference(ref_path.read_text(encoding="utf-8"))
        )
        if not ref_lines:
            skipped["empty_reference"].append(pid)
            continue
        hyp_lines = load_system_lines(system_dir, pid)
        if hyp_lines is None:
            skipped["no_reading"].append(pid)
            continue
        score = align.score_page(ref_lines, hyp_lines)
        score.wer = align.wer(  # type: ignore[attr-defined]
            " ".join(line.text for line in ref_lines), " ".join(hyp_lines)
        )
        score.words += lexicon.judge(score.word_pairs)
        scores[pid] = score
    ids = sorted(scores)
    test_ids = [p for p in ids if split and p in split["pages"]]
    dev_ids = [p for p in ids if not split or p not in split["pages"]]
    per_page = {
        pid: {
            "cer": round(s.cer_total, 4),
            "wer": round(s.wer, 4),
            "ref_chars": s.ref_chars,
            "origins": {k: round(v, 3) for k, v in s.weights().items()},
            "lines": {
                "groups": len(s.matching.groups),
                "one_to_one": s.matching.one_to_one,
                "merged": s.matching.merged,
                "split": s.matching.split,
                "missing": len(s.matching.missing),
                "spurious": len(s.matching.spurious),
                "inversions": s.inversions,
            },
            "formula_chars": s.recognition_detail["chars_formula"],
            "formula_errors": s.recognition_detail["errors_formula"],
            "split": "test" if pid in test_ids else "dev",
            "classes": classes.get(pid),
            "quality": quality.get(pid),
        }
        for pid, s in scores.items()
    }
    result = {
        "schema": "exp-027-score/1",
        "created_at": datetime.now(UTC).isoformat(),
        "system": args.system,
        "git": git_state(),
        "pages_scored": len(ids),
        "skipped": skipped,
        "frozen_test": bool(split),
        "all": aggregate(scores, ids),
        "test": aggregate(scores, test_ids),
        "dev": aggregate(scores, dev_ids),
        "by_class_all": by_class(scores, classes, ids),
        "by_class_test": by_class(scores, classes, test_ids),
        "quality_correlation_all": quality_correlation(scores, quality, ids),
        "lexicon": lexicon.describe(),
        "per_page": per_page,
    }
    out = PROCESSED / f"score-{args.system}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.benchmark:
        stamp = datetime.now(UTC).strftime("%Y%m%d")
        bench = (
            DI_ROOT / "evaluation" / "benchmarks" / f"BENCHMARK-{stamp}-exp-027-{args.system}.json"
        )
        bench.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {k: result[k] for k in ("pages_scored", "skipped")}
    summary["cer_all"] = result["all"].get("cer_micro")
    summary["cer_test"] = result["test"].get("cer_micro")
    summary["origins_all"] = result["all"].get("origins")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
