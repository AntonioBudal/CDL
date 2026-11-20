"""T008 — medidas H1–H4 do EXP-028A (só números; nenhum texto na saída).

* **H1** CER(Gemini → v3): referência v3 contra o texto do Gemini, em nível de página, com e sem a
  simplificação de LaTeX do EXP-027 (``delatex``).
* **H2** piso de ruído humano: 1ª passada contra a 2ª passada cega, linha a linha (mesmo
  ``line_id``), nas páginas de ``second-pass.json``.
* **H3** CER/WER de página da leitura do produto (texto do motor sobre as fotos originais, guardado
  pelo EXP-027) contra a v3 — a mesma conta do EXP-027 com a régua nova — e, como a v3 tem linhas, a
  decomposição de linhas do ``align.score_page`` (heurística, só texto).
* **H4** quebras de linha: fração das quebras da v3 que a referência do Gemini também tem, na
  posição alinhada.

Grava ``processed/exp-028a/results.json``; com ``--benchmark``, uma cópia versionada em
``evaluation/benchmarks/``. Uso: ``python measure.py [--benchmark]``
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime

import align
import common
import textnorm
from delatex import delatex_ref
from seed_drafts import align_words

EXP027_PAGE_CER_TEST = 0.5634  # benchmark 2026-11-16, modo de página, referência v2


def ref_lines(content: str) -> list[textnorm.RefLine]:
    return textnorm.text_lines(textnorm.parse_reference(content))


def page_ref(lines: list[textnorm.RefLine]) -> textnorm.RefLine:
    return align.merge_ref(lines, list(range(len(lines))))


def plain(line: textnorm.RefLine) -> str:
    return delatex_ref(line.text, line.formula)[0]


def micro(pairs: list[tuple[int, int]]) -> float | None:
    chars = sum(c for _, c in pairs)
    return round(sum(d for d, _ in pairs) / chars, 4) if chars else None


def h1(v3: dict[str, list], gemini: dict[str, list]) -> dict:
    pairs, pairs_plain, per_page = [], [], {}
    for pid in sorted(v3):
        if pid not in gemini:
            continue
        ref, hyp = page_ref(v3[pid]), page_ref(gemini[pid])
        ref_text, hyp_text = textnorm.page_text(ref.text), textnorm.page_text(hyp.text)
        dist = align.levenshtein(ref_text, hyp_text)
        ref_plain, hyp_plain = textnorm.page_text(plain(ref)), textnorm.page_text(plain(hyp))
        dist_plain = align.levenshtein(ref_plain, hyp_plain)
        pairs.append((dist, len(ref_text)))
        pairs_plain.append((dist_plain, len(ref_plain)))
        per_page[pid] = {
            "cer": round(dist / len(ref_text), 4) if ref_text else None,
            "cer_plain": round(dist_plain / len(ref_plain), 4) if ref_plain else None,
            "wer": round(align.wer(ref_text, hyp_text), 4) if ref_text else None,
        }
    return {"cer_micro": micro(pairs), "cer_plain_micro": micro(pairs_plain), "pages": per_page}


def h2(docs: dict[str, dict], second_pass: list[str]) -> dict:
    pairs, per_page, lines_equal, lines_total = [], {}, 0, 0
    for pid in second_pass:
        doc = docs.get(pid)
        if not doc:
            continue
        both = [line for line in doc["lines"] if line["pass1"] and line["pass2"]]
        page_pairs = []
        for line in both:
            first = textnorm.page_text(textnorm.parse_ref_line(line["pass1"]["text"]).text)
            second = textnorm.page_text(textnorm.parse_ref_line(line["pass2"]["text"]).text)
            page_pairs.append((align.levenshtein(first, second), len(first)))
            lines_equal += first == second
        lines_total += len(both)
        pairs.extend(page_pairs)
        modes = sorted({line["pass2"]["mode"] for line in both})
        per_page[pid] = {"lines": len(both), "cer": micro(page_pairs), "modes": modes}
    return {
        "cer_micro": micro(pairs),
        "lines": lines_total,
        "lines_identical": lines_equal,
        "pages": per_page,
    }


def h3(v3: dict[str, list], readings: dict[str, list[str]]) -> dict:
    page_pairs, words, per_page = [], [], {}
    totals = {"missing": 0, "spurious": 0, "merged": 0, "split": 0, "one_to_one": 0, "ref": 0}
    origins = {"order": 0, "missing": 0, "spurious": 0, "recognition": 0, "residual": 0}
    for pid in sorted(v3):
        hyp = readings.get(pid)
        if hyp is None:
            continue
        lines = v3[pid]
        page = align.score_page([page_ref(lines)], [" ".join(hyp)], single=True)
        line_level = align.score_page(lines, hyp)
        page_pairs.append((page.distance_total, page.ref_chars))
        ref_text = textnorm.page_text(" ".join(line.text for line in lines))
        words.append(align.wer(ref_text, " ".join(hyp)))
        m = line_level.matching
        totals["missing"] += len(m.missing)
        totals["spurious"] += len(m.spurious)
        totals["merged"] += m.merged
        totals["split"] += m.split
        totals["one_to_one"] += m.one_to_one
        totals["ref"] += len(lines)
        origins["order"] += line_level.order
        origins["missing"] += line_level.missing_chars
        origins["spurious"] += line_level.spurious_chars
        origins["recognition"] += line_level.recognition
        origins["residual"] += line_level.residual
        per_page[pid] = {
            "cer": round(page.cer_total, 4),
            "wer": round(words[-1], 4),
            "ref_lines": len(lines),
            "read_lines": len(hyp),
            "missing_lines": len(m.missing),
        }
    error = sum(origins.values()) or 1
    cer = micro(page_pairs)
    return {
        "cer_micro": cer,
        "wer_page_mean": round(sum(words) / len(words), 4) if words else None,
        "exp027_cer_v2": EXP027_PAGE_CER_TEST,
        "delta_points": round((cer - EXP027_PAGE_CER_TEST) * 100, 1) if cer is not None else None,
        "lines": totals,
        "origins_share": {k: round(v / error, 3) for k, v in origins.items()},
        "pages": per_page,
    }


def breaks(lines: list[str]) -> tuple[list[str], set[int]]:
    """Palavras da página e os índices das palavras que terminam uma linha (menos a última)."""
    words, ends = [], set()
    for line in lines:
        tokens = textnorm.tokenize_words(line)
        if not tokens:
            continue
        words.extend(tokens)
        ends.add(len(words) - 1)
    if words:
        ends.discard(len(words) - 1)
    return words, ends


def h4(v3_raw: dict[str, list[str]], gemini_raw: dict[str, list[str]]) -> dict:
    found = total = 0
    v3_lines = gemini_lines = 0
    per_page = {}
    for pid in sorted(v3_raw):
        if pid not in gemini_raw:
            continue
        words_v3, ends_v3 = breaks(v3_raw[pid])
        words_g, ends_g = breaks(gemini_raw[pid])
        mapping = align_words(words_v3, words_g)
        page_found = sum(1 for i in ends_v3 if mapping[i] is not None and mapping[i] in ends_g)
        found += page_found
        total += len(ends_v3)
        v3_lines += len(v3_raw[pid])
        gemini_lines += len(gemini_raw[pid])
        per_page[pid] = {
            "v3_lines": len(v3_raw[pid]),
            "gemini_lines": len(gemini_raw[pid]),
            "breaks_kept": round(page_found / len(ends_v3), 3) if ends_v3 else None,
        }
    return {
        "v3_lines": v3_lines,
        "gemini_lines": gemini_lines,
        "breaks_v3": total,
        "breaks_kept_share": round(found / total, 3) if total else None,
        "breaks_lost_share": round(1 - found / total, 3) if total else None,
        "pages": per_page,
    }


def load_texts(folder, ids) -> dict[str, str]:
    out = {}
    for pid in ids:
        path = folder / f"{pid}.txt"
        if path.is_file():
            out[pid] = path.read_text(encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Medidas do EXP-028A")
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    manifest = json.loads((common.SPLITS / "test-manifest-v3.json").read_text(encoding="utf-8"))
    ids = sorted(manifest["pages"])
    v3_text = load_texts(common.REFERENCE_V3, ids)
    gemini_text = load_texts(common.GEMINI_REFERENCE, ids)
    v3 = {pid: ref_lines(text) for pid, text in v3_text.items()}
    gemini = {pid: ref_lines(text) for pid, text in gemini_text.items()}
    readings = {}
    for pid in ids:
        path = common.PRODUCT_READING / f"{pid}.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            readings[pid] = [line["text"] for line in data["lines"] if line.get("text")]
    paths = common.anotar_paths()
    docs = {}
    for pid in ids:
        path = paths.annotations / f"{pid}.json"
        if path.is_file():
            docs[pid] = json.loads(path.read_text(encoding="utf-8"))
    second = json.loads((common.SPLITS / "second-pass.json").read_text(encoding="utf-8"))
    result = {
        "schema": "exp-028a-results/1",
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages": len(v3),
        "h1_gemini_vs_v3": h1(v3, gemini),
        "h2_human_noise": h2(docs, sorted(second["pages"])),
        "h3_product_vs_v3": h3(v3, readings),
        "h4_line_breaks": h4(
            {p: [ln for ln in t.splitlines() if ln.strip()] for p, t in v3_text.items()},
            {p: [ln for ln in t.splitlines() if ln.strip()] for p, t in gemini_text.items()},
        ),
        "seconds": {
            pid: doc["seconds"] for pid, doc in docs.items()
        },
        "draft_source": {pid: doc["draft_source"] for pid, doc in docs.items()},
    }
    common.PROCESSED.mkdir(parents=True, exist_ok=True)
    out = common.PROCESSED / "results.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.benchmark:
        stamp = datetime.now(UTC).strftime("%Y%m%d")
        bench = common.DI_ROOT / "evaluation" / "benchmarks" / f"BENCHMARK-{stamp}-exp-028a.json"
        bench.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "pages": result["pages"],
        "h1_cer": result["h1_gemini_vs_v3"]["cer_micro"],
        "h2_cer": result["h2_human_noise"]["cer_micro"],
        "h3_cer": result["h3_product_vs_v3"]["cer_micro"],
        "h4_breaks_lost": result["h4_line_breaks"]["breaks_lost_share"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
