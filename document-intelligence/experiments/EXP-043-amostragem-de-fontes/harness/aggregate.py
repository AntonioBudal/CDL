"""EXP-043 — junta as medidas de todas as fontes numa tabela (só números, sem texto) e estima o
rendimento de cada uma no nosso formato. Grava ``resumo-fontes.json`` em ``D:`` e uma cópia
versionada em ``experiments/EXP-043-amostragem-de-fontes/resultados.json``.

Uso: ``python aggregate.py``
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import common

OUT_VERSIONED = Path(__file__).resolve().parents[1] / "resultados.json"


def load(name: str):
    path = common.ROOT / name
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    cer = load("resumo-cer-leitor.json") or {}
    table = []
    for manifest in sorted(common.ROOT.glob("*/manifesto.jsonl")):
        source = manifest.parent.name
        rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        if not rows:
            continue
        n = len(rows)
        usable = sum(1 for r in rows if r.get("usable"))
        chars = sum(r.get("chars", 0) for r in rows)
        sums = defaultdict(int)
        for r in rows:
            for key in ("bytes_original", "bytes_ours", "bytes_ours_lossy", "pt_accents"):
                sums[key] += r.get(key, 0)
        table.append(
            {
                "source": source,
                "status": rows[0].get("status"),
                "license": rows[0].get("license"),
                "language": rows[0].get("language"),
                "transcription": rows[0].get("transcription"),
                "sampled_lines": n,
                "usable_share": round(usable / n, 3),
                "chars_per_line": round(chars / n, 1),
                "kb_per_line_original": round(sums["bytes_original"] / n / 1024, 1),
                "kb_per_line_lossless": round(sums["bytes_ours"] / n / 1024, 1),
                "kb_per_line_lossy": round(sums["bytes_ours_lossy"] / n / 1024, 1),
                "pt_accents_per_1000_chars": round(1000 * sums["pt_accents"] / max(1, chars), 1),
                "reader_cer": (cer.get(source) or {}).get("cer_micro"),
            }
        )
    teklia = load("resumo-teklia.json") or {}
    htr = load("resumo-htr-united.json") or {}
    totals = {
        r["dataset"].split("/")[1]: r.get("rows_total")
        for r in teklia.get("results", [])
        if r.get("dataset")
    }
    for r in htr.get("results", []):
        if r.get("repo"):
            totals[f"htr-united-{r['repo'].split('/')[1]}"] = r.get("catalog_lines")
    for row in table:
        total = totals.get(row["source"])
        row["lines_available_est"] = total
        row["gb_lossy_est"] = (
            round(total * row["kb_per_line_lossy"] / 1024**2, 2) if total else None
        )
    payload = {
        "created_by": "EXP-043",
        "sources": table,
        "skipped": (teklia.get("skipped") or {}),
        "htr_united_issues": [
            {k: r.get(k) for k in ("title", "lfs_skipped", "pairs_in_repo", "blocked", "error")}
            for r in htr.get("results", [])
            if r.get("lfs_skipped") or r.get("blocked") or r.get("error") or not r.get("pages")
        ],
        "synthetic": load("resumo-sintetico.json"),
    }
    (common.ROOT / "resumo-fontes.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), "utf-8"
    )
    OUT_VERSIONED.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", "utf-8")
    for row in table:
        print(
            json.dumps(
                {
                    k: row[k]
                    for k in (
                        "source",
                        "status",
                        "sampled_lines",
                        "kb_per_line_lossy",
                        "lines_available_est",
                        "gb_lossy_est",
                        "reader_cer",
                    )
                },
                ensure_ascii=False,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
