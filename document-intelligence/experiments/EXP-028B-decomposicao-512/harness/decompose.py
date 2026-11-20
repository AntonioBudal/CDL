"""T003 — decomposição do erro do EXP-028B (só números):

* CER de página de A (produto), B (caixas do autor, ordem dele) e C (caixas do autor, ordem do
  produto) contra a referência v3 (texto da 1ª passada do autor, linha a linha);
* partes: detecção = A − C, ordem = C − B, leitor = B;
* CER por linha em B (par exato pelo ``line_id``) e a distribuição;
* custo da resolução: A em 512 px contra a leitura do produto nas fotos originais (exportação do
  Leitorum, a mesma usada no EXP-027/028A), nas mesmas páginas e com a mesma referência.

Mesma normalização do EXP-027 (``textnorm``: marcas ``$…$``/``[?]`` retiradas, NFC, espaços
colapsados). Uso: ``python decompose.py --pages p10,p11,p14,p15 [--benchmark]``
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

DI_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(DI_ROOT / "experiments" / "EXP-027-analise-50-paginas" / "harness"))

import align  # noqa: E402
import textnorm  # noqa: E402

DATA_ROOT = Path(os.environ.get("EXP028B_DATA_ROOT") or DI_ROOT / "dataset")
READINGS = DATA_ROOT / "processed" / "exp-028b"
ANNOTATIONS = DATA_ROOT / "raw" / "anotacao"
ORIGINAL_READING = DATA_ROOT / "processed" / "exp-027" / "motor"
BUCKETS = ((0.1, "ate_10"), (0.3, "10_a_30"), (0.6, "30_a_60"), (float("inf"), "acima_60"))


def clean(text: str) -> str:
    return textnorm.page_text(textnorm.parse_ref_line(text).text)


def page_pair(reference: list[str], hypothesis: list[str]) -> tuple[int, int]:
    ref = textnorm.page_text(" ".join(clean(t) for t in reference))
    hyp = textnorm.page_text(" ".join(hypothesis))
    return align.levenshtein(ref, hyp), len(ref)


def micro(pairs: list[tuple[int, int]]) -> float | None:
    chars = sum(c for _, c in pairs)
    return round(sum(d for d, _ in pairs) / chars, 4) if chars else None


def bucket(value: float) -> str:
    return next(name for limit, name in BUCKETS if value <= limit)


def decompose(pages: dict[str, dict]) -> dict:
    """``pages[pid]`` = {"ref": {line_id: texto}, "order": [line_id…], "a": [...], "b": {line_id:
    texto}, "c": [...], "original": [...] ou None}."""
    pairs = {key: [] for key in ("a", "b", "c", "original", "a_same")}
    per_page, per_line = {}, []
    for pid, page in sorted(pages.items()):
        reference = [page["ref"][line_id] for line_id in page["order"]]
        b_texts = [page["b"][line_id] for line_id in page["order"]]
        result = {}
        for key, hyp in (("a", page["a"]), ("b", b_texts), ("c", page["c"])):
            dist, chars = page_pair(reference, hyp)
            pairs[key].append((dist, chars))
            result[key] = round(dist / chars, 4) if chars else None
        if page.get("original") is not None:
            dist, chars = page_pair(reference, page["original"])
            pairs["original"].append((dist, chars))
            pairs["a_same"].append(pairs["a"][-1])
            result["original"] = round(dist / chars, 4) if chars else None
        for line_id in page["order"]:
            ref = clean(page["ref"][line_id])
            hyp = textnorm.page_text(page["b"][line_id])
            if ref:
                per_line.append(align.levenshtein(ref, hyp) / len(ref))
        per_page[pid] = result
    a, b, c = (micro(pairs[k]) for k in ("a", "b", "c"))
    parts = None
    if None not in (a, b, c):
        parts = {
            "deteccao_pontos": round((a - c) * 100, 1),
            "ordem_pontos": round((c - b) * 100, 1),
            "leitor_pontos": round(b * 100, 1),
            "caixas_e_ordem_pontos": round((a - b) * 100, 1),
        }
    distribution = {name: 0 for _, name in BUCKETS}
    for value in per_line:
        distribution[bucket(value)] += 1
    original, a_same = micro(pairs["original"]), micro(pairs["a_same"])
    return {
        "cer": {"a_produto": a, "b_caixas_autor": b, "c_caixas_autor_ordem_produto": c},
        "parts": parts,
        "lines_b": {
            "count": len(per_line),
            "median_cer": round(sorted(per_line)[len(per_line) // 2], 4) if per_line else None,
            "distribution": distribution,
        },
        "resolution": {
            "a_512": a_same,
            "original_photos": original,
            "cost_points": round((a_same - original) * 100, 1)
            if None not in (a_same, original)
            else None,
        },
        "pages": per_page,
    }


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect(ids: list[str]) -> dict[str, dict]:
    pages = {}
    for pid in ids:
        annotation = load_json(ANNOTATIONS / f"{pid}.json")
        lines = sorted(annotation["lines"], key=lambda line: line["order"])
        original_path = ORIGINAL_READING / f"{pid}.json"
        original = None
        if original_path.is_file():
            original = [ln["text"] for ln in load_json(original_path)["lines"] if ln.get("text")]
        pages[pid] = {
            "ref": {line["line_id"]: line["pass1"]["text"] for line in lines},
            "order": [line["line_id"] for line in lines],
            "a": [ln["text"] for ln in load_json(READINGS / "a" / f"{pid}.json")["lines"]],
            "b": {ln["line_id"]: ln["text"]
                  for ln in load_json(READINGS / "b" / f"{pid}.json")["lines"]},
            "c": [ln["text"] for ln in load_json(READINGS / "c" / f"{pid}.json")["lines"]],
            "original": original,
        }
    return pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decomposição do erro do EXP-028B")
    parser.add_argument("--pages", required=True)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    ids = [p.strip() for p in args.pages.split(",") if p.strip()]
    result = {
        "schema": "exp-028b-results/1",
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "images": "512 px (low_resolution)",
        "page_ids": ids,
        **decompose(collect(ids)),
    }
    out = READINGS / "results.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.benchmark:
        stamp = datetime.now(UTC).strftime("%Y%m%d")
        bench = DI_ROOT / "evaluation" / "benchmarks" / f"BENCHMARK-{stamp}-exp-028b.json"
        bench.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("cer", "parts", "resolution")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
