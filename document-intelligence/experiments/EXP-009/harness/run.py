"""Benchmark do EXP-009: leitura de manuscrito com o PP-OCRv6, por linha e por página.

Lê as transcrições (``*-refs.json``) e as leituras (``read-*.json``), ambas fora do Git, e grava
um relatório só com números e identificadores. As páginas lidas de ponta a ponta vão para LDF 2.0
(etapas de layout e de reconhecimento concluídas) e validadas.

Uso (árvore limpa): ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-009/harness/run.py --out evaluation/benchmarks/<arquivo>.json``
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from crop import reading_order
from evaluate import line_metrics, page_metrics

from leitorum_di.contracts.ldf import LDFValidationError, build_document, component, validate
from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-009"
EXP007 = ROOT / "dataset" / "processed" / "exp-007"
EXP001_BEST = {"candidate": "trocr-small-handwritten", "cer": 0.694, "wer": 1.029}
H1_CER = 0.30
H2_CER, H2_WER = 0.12, 0.25
H3_GAP = 0.05
H4_MS, H4_PEAK = 150.0, 2 * 1024**3
H5_CER = 0.20


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


def load(name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    refs = json.loads((DATA / f"{name}-refs.json").read_text(encoding="utf-8"))
    read = json.loads((DATA / f"read-{name}.json").read_text(encoding="utf-8"))
    if read.get("limit"):
        raise SystemExit(f"{name}: leitura de ensaio (--limit)")
    return refs, read


def cost(read: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in read["summary"].items() if k != "describe"}


def line_texts(read: dict[str, Any]) -> dict[str, str]:
    return {key: lines[0]["text"] if lines else "" for key, lines in read["items"].items()}


def page_documents(read: dict[str, Any]) -> dict[str, Any]:
    """Grava cada página lida em LDF 2.0 e conta os documentos válidos."""
    manifest = json.loads((EXP007 / "bressay-x3-manifest.json").read_text(encoding="utf-8"))
    layout = component("PP-OCRv6 small det + fusão (EXP-008)", "rapidocr 3.10.0",
                       license="Apache-2.0", license_status="VERIFIED")  # fmt: skip
    recognition = component("PP-OCRv6 small rec", "rapidocr 3.10.0",
                            license="Apache-2.0", license_status="VERIFIED")  # fmt: skip
    counts = {"documents": 0, "valid": 0, "not_representable": 0, "lines": 0}
    for page in manifest["pages"]:
        lines = read["items"].get(page["id"], [])
        counts["documents"] += 1
        try:
            document = build_document(
                image={
                    "filename": Path(page["image"]).name,
                    "width": page["width"],
                    "height": page["height"],
                    "sha256": page["sha256"],
                },
                lines=[
                    {
                        "bbox": ln["bbox"],
                        "polygon": ln.get("polygon"),
                        "score": ln.get("score"),
                        "text": ln["text"],
                        "confidence": ln.get("rec_score", 0.0),
                        "is_handwritten": True,
                    }
                    for ln in lines
                ],
                regions=[],
                stages={"layout": {"component": layout}, "recognition": {"component": recognition}},
                created_at="2026-10-14T00:00:00Z",
            )
        except (LDFValidationError, ValueError):
            counts["not_representable"] += 1
            continue
        counts["valid"] += not validate(document)
        counts["lines"] += len(document["recognition"]["lines"])
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de leitura (EXP-009)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    seed_record = freeze_seeds(DEFAULT_SEED)

    results: dict[str, Any] = {}
    for name in ("lines-exp001", "lines-gnhk", "lines-bressay"):
        refs, read = load(name)
        results[name] = {
            **line_metrics(refs["refs"], line_texts(read)),
            "cost": cost(read),
        }
        if "skipped_lines" in refs:
            results[name]["skipped_lines"] = refs["skipped_lines"]

    # Página: teto (linhas verdadeiras na ordem do dataset) e ponta a ponta (linhas detectadas).
    page_refs, page_read = load("pages-bressay")
    line_refs, line_read = load("lines-bressay")
    line_text = line_texts(line_read)
    oracle = {
        pid: "\n".join(line_text.get(key, "") for key in keys)
        for pid, keys in line_refs["page_lines"].items()
    }
    end_to_end = {}
    for pid, lines in page_read["items"].items():
        order = reading_order(lines)
        end_to_end[pid] = "\n".join(lines[i]["text"] for i in order)
    results["pages-oracle-lines"] = page_metrics(page_refs["refs"], oracle)
    results["pages-end-to-end"] = {
        **page_metrics(page_refs["refs"], end_to_end),
        "cost": cost(page_read),
        "ldf2": page_documents(page_read),
    }

    exp001 = results["lines-exp001"]
    gap = results["pages-end-to-end"]["cer_micro"] - results["pages-oracle-lines"]["cer_micro"]
    verdicts = {
        "h1_better_than_exp001": {
            "cer": exp001["cer_micro"],
            "target": H1_CER,
            "exp001_best": EXP001_BEST,
            "met": exp001["cer_micro"] <= H1_CER,
        },
        "h2_adoption_criterion": {
            "cer": exp001["cer_micro"],
            "wer": exp001["wer_micro"],
            "target": {"cer": H2_CER, "wer": H2_WER},
            "met": exp001["cer_micro"] <= H2_CER and exp001["wer_micro"] <= H2_WER,
        },
        "h3_detection_costs_little": {
            "page_cer_oracle": results["pages-oracle-lines"]["cer_micro"],
            "page_cer_end_to_end": results["pages-end-to-end"]["cer_micro"],
            "gap": gap,
            "target_gap": H3_GAP,
            "met": gap <= H3_GAP,
        },
        "h4_cost": {
            "median_ms_per_line": exp001["cost"]["median_ms"],
            "peak_rss_bytes": max(
                (r["cost"]["peak_rss_bytes"] or 0) for r in results.values() if "cost" in r
            ),
            "met": exp001["cost"]["median_ms"] <= H4_MS
            and all(
                (r["cost"]["peak_rss_bytes"] or 0) <= H4_PEAK
                for r in results.values()
                if "cost" in r
            ),  # fmt: skip
        },
        "h5_phone_photos_english": {
            "cer": results["lines-gnhk"]["cer_micro"],
            "target": H5_CER,
            "met": results["lines-gnhk"]["cer_micro"] <= H5_CER,
        },
    }
    report = {
        "schema": "leitorum-di-reading-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-009",
        "git": git_state(),
        "environment": environment_snapshot(),
        "seed": seed_record,
        "license_status": {
            "ppocr": "VERIFIED (Apache-2.0, conforme declarado)",
            "gnhk": "VERIFIED (CC-BY-4.0, conforme declarado)",
            "bressay": "NEEDS VALIDATION (exceção experimental do usuário; não embasa produto)",
        },
        "results": results,
        "verdicts": verdicts,
    }
    out = Path(args.out)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
                   newline="\n")  # fmt: skip
    for name, item in results.items():
        wer = item.get("wer_micro")
        print(
            f"{name:22s} CER {item['cer_micro']:.3f}"
            + (f" WER {wer:.3f}" if wer is not None else "")
        )
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
