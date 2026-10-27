"""Pontuação do EXP-022: fotos de páginas do BRESSAY impressas, contra as mesmas digitalizadas.

Cada foto é associada à página sorteada (``paginas.json``) cuja referência dá o menor CER com o
leitor ajustado; a associação precisa ser um-a-um, senão a pontuação para. A mesma associação vale
para o leitor original. Compara com as mesmas 15 páginas na digitalização (EXP-015/017) e na foto
sintética leve e forte (EXP-019). ``--out <arquivo>`` grava o relatório (só números).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from endtoend import git_state, ldf_pages, ordered_lines
from evaluate import levenshtein_distance, page_metrics, page_text
from lexicon import Corrector, LexiconParams
from read import FT_SHA256

from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "dataset" / "processed"
DATA = PROCESSED / "exp-022"
LEXICON = PROCESSED / "exp-011" / "lexicon-pt.json"
READERS = ("original", "ft")
# Mesmas páginas em outras condições: leitura já feita nos experimentos anteriores.
BASELINES = {
    "digitalizada": {
        "original": PROCESSED / "exp-015" / "read-test-bressay-t80.json",
        "ft": PROCESSED / "exp-017" / "read-test-bressay-t80.json",
    },
    "foto leve sintética": {
        "original": PROCESSED / "exp-019" / "read-test-bressay-light-original.json",
        "ft": PROCESSED / "exp-019" / "read-test-bressay-light-ft.json",
    },
    "foto forte sintética": {
        "original": PROCESSED / "exp-019" / "read-test-bressay-strong-original.json",
        "ft": PROCESSED / "exp-019" / "read-test-bressay-strong-ft.json",
    },
}


def corrector() -> Corrector:
    calibration = json.loads(
        (ROOT / "experiments" / "EXP-011" / "calibration.json").read_text(encoding="utf-8")
    )
    words = json.loads(LEXICON.read_text(encoding="utf-8"))["words"]
    return Corrector(words, LexiconParams(**calibration["best"]["params"]))


def corrected(items: dict, fix: Corrector, keep: set[str] | None = None) -> dict[str, list[str]]:
    return {
        pid: [fix.correct_line(line["text"]) for line in ordered_lines(lines)]
        for pid, lines in items.items()
        if keep is None or pid in keep
    }


def assign(costs: dict[str, dict[str, float]]) -> tuple[dict[str, str], dict[str, float]]:
    """Melhor página de cada foto; exige que seja um-a-um. Devolve também a margem até a segunda."""
    mapping, margins = {}, {}
    for photo, row in costs.items():
        ranked = sorted(row, key=row.get)
        mapping[photo] = ranked[0]
        margins[photo] = row[ranked[1]] - row[ranked[0]] if len(ranked) > 1 else math.inf
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("associação foto → página não é um-a-um")
    return mapping, margins


def tilt(items: dict) -> dict[str, float]:
    """Inclinação das linhas detectadas (graus, borda superior do quadrilátero)."""
    angles = []
    for lines in items.values():
        for line in lines:
            (x0, y0), (x1, y1) = line["polygon"][0], line["polygon"][1]
            angles.append(abs(math.degrees(math.atan2(y1 - y0, x1 - x0))))
    return {
        "median_abs_deg": float(np.median(angles)),
        "p90_abs_deg": float(np.percentile(angles, 90)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pontuação do EXP-022")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    fix = corrector()
    chosen = json.loads((DATA / "paginas.json").read_text(encoding="utf-8"))["pages"]
    all_refs = json.loads(
        (PROCESSED / "exp-017" / "test-bressay-refs.json").read_text(encoding="utf-8")
    )["refs"]
    refs = {pid: all_refs[pid] for pid in chosen}
    manifest = json.loads((DATA / "fotos-worker.json").read_text(encoding="utf-8"))
    reads = {
        r: json.loads((DATA / f"read-fotos-{r}.json").read_text(encoding="utf-8")) for r in READERS
    }
    texts = {r: corrected(reads[r]["items"], fix) for r in READERS}

    costs = {}
    for photo, lines in texts["ft"].items():
        hypothesis = page_text("\n".join(lines))
        costs[photo] = {
            pid: levenshtein_distance(page_text(ref), hypothesis) / len(page_text(ref))
            for pid, ref in refs.items()
        }
    mapping, margins = assign(costs)

    results = {}
    for r in READERS:
        by_page = {mapping[p]: "\n".join(lines) for p, lines in texts[r].items()}
        metrics = page_metrics(refs, by_page)
        metrics["cost"] = reads[r]["summary"]
        metrics["scales"] = {str(v): list(reads[r]["scales"].values()).count(v)
                             for v in set(reads[r]["scales"].values())}  # fmt: skip
        metrics["lines"] = sum(len(v) for v in reads[r]["items"].values())
        metrics["tilt"] = tilt(reads[r]["items"])
        metrics["ldf2"] = ldf_pages(manifest, reads[r]["items"], texts[r], fine_tuned=r == "ft")
        results[r] = metrics
    baselines = {}
    for condition, paths in BASELINES.items():
        baselines[condition] = {}
        for r, path in paths.items():
            read = json.loads(path.read_text(encoding="utf-8"))
            items = {pid: read["items"][pid] for pid in chosen}
            page = {pid: "\n".join(lines) for pid, lines in corrected(items, fix).items()}
            metrics = page_metrics(refs, page)
            metrics["lines"] = sum(len(v) for v in items.values())
            metrics["tilt"] = tilt(items)
            baselines[condition][r] = metrics

    photo_ft = results["ft"]["cer_micro"]
    verdicts = {
        "h1_between_scan_and_light": {
            "scan": baselines["digitalizada"]["ft"]["cer_micro"],
            "photo": photo_ft,
            "light": baselines["foto leve sintética"]["ft"]["cer_micro"],
            "met": baselines["digitalizada"]["ft"]["cer_micro"]
            <= photo_ft
            <= baselines["foto leve sintética"]["ft"]["cer_micro"],
        },
        "h2_runs_within_budget": {
            "met": all(
                not item["cost"]["failed"]
                and (item["cost"]["peak_rss_bytes"] or 0) <= 2**30
                and item["ldf2"]["valid"] == item["ldf2"]["documents"]
                for item in results.values()
            )
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-022",
        "git": git_state(),
        "environment": environment_snapshot(),
        "target": 80,
        "photos": {
            "files": len(manifest["pages"]),
            "sizes": sorted({f"{p['width']}x{p['height']}" for p in manifest["pages"]}),
            "assignment_margin_min": min(margins.values()),
            "assignment_margin_median": float(np.median(list(margins.values()))),
        },
        "pages": chosen,
        "reader_model": {"file": "models/exp-017/rec-ft-bressay.onnx", "sha256": FT_SHA256},
        "license_status": {
            "reader": "NEEDS VALIDATION — ajustado no BRESSAY (EXP-014); nunca produto",
            "bressay": "NEEDS VALIDATION (exceção experimental; não embasa produto)",
        },
        "results": results,
        "baselines_same_pages": baselines,
        "verdicts": verdicts,
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print("associação: margem mínima", round(min(margins.values()), 3))
    for r, item in results.items():
        cer, wer = round(item["cer_micro"], 4), round(item["wer_micro"], 4)
        print("fotos", r, cer, wer, item["lines"], item["scales"], item["tilt"],
              round(item["cost"]["median_ms"]), item["ldf2"])  # fmt: skip
    for condition, by_reader in baselines.items():
        for r, item in by_reader.items():
            print(condition, r, round(item["cer_micro"], 4), item["lines"], item["tilt"])
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
