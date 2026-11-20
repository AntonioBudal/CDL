"""T003 — rascunho por alinhamento: distribui o texto da referência do Gemini (em parágrafos) pelas
caixas de linha da página, alinhando as palavras dele com as palavras que o motor leu em cada caixa.

* Tokens: palavras separadas por espaço; um trecho ``$…$`` inteiro é um token só (a fórmula nunca
  fica partida entre duas caixas).
* Alinhamento: programação dinâmica de palavras com custo de troca igual à distância de caracteres
  normalizada (minúsculas, sem acentos), custo 1 para sobra de um lado. Cada palavra do Gemini vai
  para a caixa da palavra do motor com que alinhou; a que não alinhou acompanha a anterior (ou a
  seguinte, no começo da página).
* Grava pelo ``store.save_page`` da ferramenta (mesma validação e hash), com
  ``draft_source: "importado:gemini-alinhado"``. Só mexe em páginas **sem nenhuma linha
  confirmada** na 1ª passada.

Imprime só contagens. Uso: ``python seed_drafts.py [--only p10,p11] [--dry-run]``
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

import common
from align import levenshtein

TOKEN = re.compile(r"(?<!\\)\$[^$]*(?<!\\)\$|\S+")


def tokens(text: str) -> list[str]:
    """Palavras, com cada ``$…$`` como um token só (espaços de dentro preservados)."""
    return TOKEN.findall(" ".join(text.split()))


def _key(word: str) -> str:
    word = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in word if c.isalnum())


def _sub_cost(a: str, b: str) -> float:
    ka, kb = _key(a), _key(b)
    if not ka and not kb:
        return 0.0
    if not ka or not kb:
        return 1.0
    return min(1.0, levenshtein(ka, kb) / max(len(ka), len(kb)))


def align_words(source: list[str], target: list[str]) -> list[int | None]:
    """Para cada palavra de ``source``, o índice da palavra de ``target`` com que alinhou, ou
    None."""
    n, m = len(source), len(target)
    cost = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0] = float(i)
    for j in range(1, m + 1):
        cost[0][j] = float(j)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost[i][j] = min(
                cost[i - 1][j] + 1,
                cost[i][j - 1] + 1,
                cost[i - 1][j - 1] + _sub_cost(source[i - 1], target[j - 1]),
            )
    out: list[int | None] = [None] * n
    i, j = n, m
    while i > 0 and j > 0:
        if cost[i][j] == cost[i - 1][j - 1] + _sub_cost(source[i - 1], target[j - 1]):
            out[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif cost[i][j] == cost[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    return out


def distribute(reference: str, boxes: list[str | None]) -> tuple[list[list[str]], dict]:
    """Palavras do Gemini por caixa (na ordem das caixas) e contagens do alinhamento."""
    words = tokens(reference)
    motor_words: list[str] = []
    owner: list[int] = []
    for index, text in enumerate(boxes):
        for word in tokens(text or ""):
            motor_words.append(word)
            owner.append(index)
    assigned: list[list[str]] = [[] for _ in boxes]
    stats = {"words": len(words), "aligned": 0, "carried": 0}
    if not boxes:
        return assigned, stats
    mapping = align_words(words, motor_words) if motor_words else [None] * len(words)
    boxes_of = [owner[j] if j is not None else None for j in mapping]
    stats["aligned"] = sum(1 for b in boxes_of if b is not None)
    first = next((b for b in boxes_of if b is not None), 0)
    current = first
    for word, box in zip(words, boxes_of, strict=True):
        if box is None:
            stats["carried"] += 1
            box = current
        else:
            box = max(box, current)  # nunca volta para uma caixa anterior: preserva a ordem
        current = box
        assigned[box].append(word)
    return assigned, stats


def main(argv: list[str] | None = None) -> int:
    from tools.anotar import store

    parser = argparse.ArgumentParser(description="Rascunho do Gemini alinhado às caixas")
    parser.add_argument("--only", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    paths = common.anotar_paths()
    test = json.loads((common.SPLITS / "test-manifest.json").read_text(encoding="utf-8"))
    wanted = {p.strip() for p in args.only.split(",") if p.strip()} or set(test["pages"])
    report = {"seeded": [], "skipped_confirmed": [], "skipped_missing": [], "pages": {}}
    for pid in sorted(wanted):
        ref_path = common.GEMINI_REFERENCE / f"{pid}.txt"
        try:
            doc = store.load_page(paths, pid)
        except (store.NotFoundError, store.BlockedError):
            report["skipped_missing"].append(pid)
            continue
        if not ref_path.is_file():
            report["skipped_missing"].append(pid)
            continue
        if any(line["pass1"] for line in doc["lines"]):
            report["skipped_confirmed"].append(pid)
            continue
        lines = sorted(doc["lines"], key=lambda line: line["order"])
        assigned, stats = distribute(
            ref_path.read_text(encoding="utf-8"), [line["motor_text"] for line in lines]
        )
        for line, words in zip(lines, assigned, strict=True):
            line["draft"] = " ".join(words) or None
        doc["lines"] = lines
        doc["draft_leftover"] = []
        doc["draft_source"] = f"importado:{common.DRAFT_LABEL}"
        stats["boxes"] = len(lines)
        stats["empty_boxes"] = sum(1 for words in assigned if not words)
        report["pages"][pid] = stats
        if not args.dry_run:
            store.save_page(paths, pid, doc, expected_version=doc["version"])
        report["seeded"].append(pid)
    totals = {
        key: sum(page[key] for page in report["pages"].values())
        for key in ("words", "aligned", "carried", "boxes", "empty_boxes")
    }
    print(json.dumps({**{k: v for k, v in report.items() if k != "pages"}, "totals": totals},
                     ensure_ascii=False))
    out = common.PROCESSED / "seed-drafts.json"
    if not args.dry_run:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
