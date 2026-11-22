"""EXP-043 — amostra das bases de linhas da Teklia pela API de linhas do Hugging Face (``datasets-
server``): imagem e texto por linha, sem baixar o conjunto inteiro. A licença que vale é a da
fonte original (o rótulo MIT do reempacotamento não substitui a original).

Uso: ``python sample_teklia.py [--per-set 200]``
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import urllib.parse

import common

API = "https://datasets-server.huggingface.co"
# Licença da fonte original, com a evidência consultada em 2026-11-20 (Zenodo / site oficial).
UPSTREAM = {
    "Teklia/Belfort-line": (
        "CC-BY-4.0",
        "https://zenodo.org/record/8041668",
        "APPROVED",
        "fra",
        "1790-1946",
    ),
    "Teklia/POPP-line": (
        "CC-BY-4.0",
        "https://zenodo.org/record/6581158",
        "APPROVED",
        "fra",
        "1926",
    ),
    "Teklia/HOME-Alcar-line": (
        "CC-BY-4.0",
        "https://zenodo.org/records/5600884",
        "APPROVED",
        "lat",
        "medieval",
    ),
    "Teklia/Himanis-line": (
        "CC-BY-4.0",
        "https://zenodo.org/records/5535306",
        "APPROVED",
        "lat,fra",
        "medieval",
    ),
    "Teklia/NorHand-v1-line": (
        "CC-BY-4.0",
        "https://zenodo.org/records/6542056",
        "APPROVED",
        "nob",
        "1820-1940",
    ),
    "Teklia/NorHand-v2-line": (
        "CC-BY-4.0",
        "https://zenodo.org/records/10628791",
        "APPROVED",
        "nob",
        "1820-1940",
    ),
    "Teklia/NorHand-v3-line": (
        "CC-BY-4.0 (a confirmar v3)",
        "https://zenodo.org/records/10628791",
        "PENDING_REVIEW",
        "nob",
        "1820-1940",
    ),
    "Teklia/RIMES-2011-line": (
        "CC-BY-NC-4.0",
        "https://zenodo.org/records/10812725",
        "APPROVED_NC",
        "fra",
        "contemporâneo",
    ),
    "Teklia/IAM-line": (
        "pesquisa não comercial",
        "https://fki.tic.heia-fr.ch/databases/iam-handwriting-database",
        "EXPERIMENT_ONLY",
        "eng",
        "contemporâneo",
    ),
    "Teklia/Esposalles-line": (
        "não encontrada",
        "https://huggingface.co/datasets/Teklia/Esposalles-line",
        "PENDING_REVIEW",
        "cat",
        "1600s",
    ),
}
SKIPPED = {
    "Teklia/CASIA-HWDB2-line": (
        "chinês (conjunto de caracteres incompatível com o leitor latino); licença por acordo"
    ),
    "Teklia/NewsEye-Austrian-line": "jornais impressos, não manuscrito",
}


def sample(dataset: str, per_set: int, rng: random.Random) -> dict:
    license_name, evidence_url, status, language, era = UPSTREAM[dataset]
    source = dataset.split("/")[1]
    q = urllib.parse.urlencode({"dataset": dataset})
    splits = common.fetch_json(f"{API}/splits?{q}")["splits"]
    split = next((s for s in splits if s["split"] == "train"), splits[0])
    base = {"dataset": dataset, "config": split["config"], "split": split["split"]}
    first = common.fetch_json(
        f"{API}/rows?{urllib.parse.urlencode({**base, 'offset': 0, 'length': 1})}"
    )
    total = first["num_rows_total"]
    evidence = common.save_terms(source, evidence_url)
    stats = {
        "rows_total": total,
        "sampled": 0,
        "usable": 0,
        "bytes_original": 0,
        "bytes_ours": 0,
        "bytes_ours_lossy": 0,
        "chars": 0,
        "pt_accents": 0,
        "blocked": None,
    }
    chunks = 4
    for start in sorted(rng.sample(range(max(1, total - per_set)), chunks)):
        params = {**base, "offset": start, "length": per_set // chunks}
        try:
            rows = common.fetch_json(f"{API}/rows?{urllib.parse.urlencode(params)}")["rows"]
        except common.BlockedError as error:
            stats["blocked"] = str(error)
            break
        for item in rows:
            row = item["row"]
            text = row.get("text") or ""
            try:
                image_bytes = common.fetch(row["image"]["src"])
            except common.BlockedError as error:
                stats["blocked"] = str(error)
                break
            path = common.store(source, image_bytes, ".img")
            measures = common.line_measures(image_bytes, text)
            common.record(
                source,
                {
                    "source": dataset,
                    "source_url": f"https://huggingface.co/datasets/{dataset}",
                    "row_index": item["row_idx"],
                    "split": split["split"],
                    "file": path.name,
                    "sha256": path.stem,
                    "license_repackage": "MIT",
                    "license": license_name,
                    "status": status,
                    "language": language,
                    "era": era,
                    "transcription": "line",
                    "text": text,
                    **evidence,
                    **measures,
                },
            )
            stats["sampled"] += 1
            stats["usable"] += measures["usable"]
            for key in ("bytes_original", "bytes_ours", "bytes_ours_lossy", "chars", "pt_accents"):
                stats[key] += measures[key]
    return {
        "dataset": dataset,
        "license": license_name,
        "status": status,
        "language": language,
        "era": era,
        **stats,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-set", type=int, default=200)
    parser.add_argument("--only", default="")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    rng = random.Random("exp-043")
    wanted = [d for d in UPSTREAM if not args.only or d in args.only.split(",")]
    results = []
    for dataset in wanted:
        try:
            result = sample(dataset, args.per_set, rng)
        except common.BlockedError as error:
            result = {"dataset": dataset, "blocked": str(error)}
        except Exception as error:  # noqa: BLE001 — registra e segue para o próximo conjunto
            result = {"dataset": dataset, "error": f"{type(error).__name__}: {str(error)[:120]}"}
        results.append(result)
        print(
            json.dumps(
                {
                    k: result.get(k)
                    for k in ("dataset", "rows_total", "sampled", "usable", "blocked")
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    out = common.ROOT / "resumo-teklia.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.is_file():  # nova rodada de alguns conjuntos: substitui só esses no resumo
        previous = json.loads(out.read_text(encoding="utf-8"))["results"]
        redone = {r["dataset"] for r in results}
        results = [r for r in previous if r["dataset"] not in redone] + results
    out.write_text(
        json.dumps({"results": results, "skipped": SKIPPED}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
