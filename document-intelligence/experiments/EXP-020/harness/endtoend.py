"""Benchmark do EXP-012: pipeline integrado foto → texto → LDF 2.0, de ponta a ponta.

Para cada variante: CER/WER de página antes e depois da correção lexical (só português), custo e
validade das páginas em LDF 2.0 (com o texto final nas linhas). Relatório só com números.
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
from evaluate import page_metrics
from lexicon import Corrector, LexiconParams

from leitorum_di.contracts.ldf import LDFValidationError, build_document, component, validate
from leitorum_di.reproducibility import environment_snapshot

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-012"
EXP007 = ROOT / "dataset" / "processed" / "exp-007"
LEXICON = ROOT / "dataset" / "processed" / "exp-011" / "lexicon-pt.json"
VARIANTS = {
    "bressay-native": ("pt", "bressay-native-manifest.json"),
    "bressay-x3": ("pt", "bressay-x3-manifest.json"),
    "gnhk": ("en", "gnhk-manifest.json"),
}
EXP009_END_TO_END = 0.367


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


def ordered_lines(lines: list[dict]) -> list[dict]:
    return [lines[i] for i in reading_order(lines)]


def ldf_pages(
    manifest: dict, items: dict, texts: dict[str, list[str]], fine_tuned: bool = True
) -> dict[str, Any]:
    layout = component("PP-OCRv6 small det + fusão (EXP-008)", "rapidocr 3.10.0",
                       license="Apache-2.0", license_status="VERIFIED")  # fmt: skip
    recognition = component("PP-OCRv6 small rec + correção lexical (EXP-011)", "PP-OCRv6 small",
                            license="Apache-2.0", license_status="VERIFIED")  # fmt: skip
    if fine_tuned:
        recognition = component("PP-OCRv6 small rec ajustado (BRESSAY, EXP-014) + correção lexical",
                                "rec-ft-bressay.onnx (EXP-017)", license="Apache-2.0 + BRESSAY",
                                license_status="NEEDS VALIDATION")  # fmt: skip
    counts = {"documents": 0, "valid": 0, "not_representable": 0, "lines": 0}
    for page in manifest["pages"]:
        lines = ordered_lines(items.get(page["id"], []))
        counts["documents"] += 1
        try:
            document = build_document(
                image={k: page[k] for k in ("width", "height", "sha256")}
                | {"filename": Path(page["image"]).name},
                lines=[
                    {
                        "bbox": ln["bbox"],
                        "polygon": ln.get("polygon"),
                        "score": ln.get("score"),
                        "text": text,
                        "confidence": ln.get("rec_score", 0.0),
                        "is_handwritten": True,
                    }
                    for ln, text in zip(lines, texts[page["id"]], strict=True)
                ],
                regions=[],
                stages={"layout": {"component": layout}, "recognition": {"component": recognition}},
                created_at="2026-10-18T00:00:00Z",
            )
        except (LDFValidationError, ValueError):
            counts["not_representable"] += 1
            continue
        counts["valid"] += not validate(document)
        counts["lines"] += len(document["recognition"]["lines"])
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark do EXP-012")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    calibration = json.loads(
        (ROOT / "experiments" / "EXP-011" / "calibration.json").read_text(encoding="utf-8")
    )
    words = json.loads(LEXICON.read_text(encoding="utf-8"))["words"]
    corrector = Corrector(words, LexiconParams(**calibration["best"]["params"]))
    results: dict[str, Any] = {}
    for variant, (language, manifest_name) in VARIANTS.items():
        manifest = json.loads((EXP007 / manifest_name).read_text(encoding="utf-8"))
        refs = json.loads((DATA / f"{variant}-refs.json").read_text(encoding="utf-8"))["refs"]
        read = json.loads((DATA / f"read-{variant}.json").read_text(encoding="utf-8"))
        raw = {
            pid: [ln["text"] for ln in ordered_lines(lines)] for pid, lines in read["items"].items()
        }
        final = raw
        if language == "pt":
            final = {pid: [corrector.correct_line(t) for t in texts] for pid, texts in raw.items()}
        upscaled = sum(
            ln.get("upscaled", 1) == 2 for lines in read["items"].values() for ln in lines
        )
        total = sum(len(lines) for lines in read["items"].values())
        results[variant] = {
            "language": language,
            "pages": len(read["items"]),
            "lines": total,
            "lines_upscaled": upscaled,
            "before_lexicon": page_metrics(refs, {k: "\n".join(v) for k, v in raw.items()}),
            "final": page_metrics(refs, {k: "\n".join(v) for k, v in final.items()}),
            "cost": read["summary"],
            "ldf2": ldf_pages(manifest, read["items"], final),
        }
    big, native, gnhk = results["bressay-x3"], results["bressay-native"], results["gnhk"]
    verdicts = {
        "h1_x3_with_lexicon": {
            "cer": big["final"]["cer_micro"],
            "target": EXP009_END_TO_END - 0.01,
            "met": big["final"]["cer_micro"] <= EXP009_END_TO_END - 0.01,
        },
        "h2_native_close_to_x3": {
            "native": native["final"]["cer_micro"],
            "x3": big["final"]["cer_micro"],
            "met": native["final"]["cer_micro"] - big["final"]["cer_micro"] <= 0.03,
        },
        "h3_gnhk_photos": {
            "cer": gnhk["final"]["cer_micro"],
            "target": 0.25,
            "met": gnhk["final"]["cer_micro"] <= 0.25,
        },
        "h4_cost": {
            "median_ms": {k: v["cost"]["median_ms"] for k, v in results.items()},
            "met": all(
                v["cost"]["median_ms"] <= 6000 and (v["cost"]["peak_rss_bytes"] or 0) <= 2 * 1024**3
                for v in results.values()
            ),
        },
        "h5_ldf": {
            "met": all(v["ldf2"]["valid"] == v["ldf2"]["documents"] for v in results.values()),
        },
    }
    report = {
        "schema": "leitorum-di-pipeline-benchmark/1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "experiment": "EXP-012",
        "git": git_state(),
        "environment": environment_snapshot(),
        "license_status": {
            "pipeline": "VERIFIED (Apache-2.0; léxico CC-BY-SA 4.0), conforme declarado",
            "gnhk": "VERIFIED (CC-BY-4.0)",
            "bressay": "NEEDS VALIDATION (exceção experimental; não embasa produto)",
        },
        "lexicon_params": calibration["best"]["params"],
        "results": results,
        "verdicts": verdicts,
    }
    Path(args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    for variant, item in results.items():
        b, f = item["before_lexicon"], item["final"]
        print(
            f"{variant}: CER {b['cer_micro']:.3f} → {f['cer_micro']:.3f}; "
            f"WER {b['wer_micro']:.3f} → {f['wer_micro']:.3f}; "
            f"{item['cost']['median_ms']:.0f} ms/página; LDF {item['ldf2']}"
        )
    for name, verdict in verdicts.items():
        print(name, "→", verdict["met"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
