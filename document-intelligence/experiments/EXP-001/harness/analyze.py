"""Análise de erros do EXP-001: alinhamento por caractere, confusões e taxas por classe.

Lê um relatório completo do benchmark (com o texto das predições) e o manifesto do dataset e
produz apenas agregados — nenhum texto de linha vai para a saída.

Uso: ``python analyze.py --report <relatório completo> --manifest <manifesto> --out <json>``
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from evaluate import nfc

from leitorum_di.metrics.base import levenshtein_distance

SCHEMA = "leitorum-di-htr-error-analysis/1"
EMPTY = "∅"
TOP_CONFUSIONS = 20
CLASSES = [
    "acentuada", "cedilha", "dígito", "pontuação", "maiúscula", "minúscula", "espaço", "outro",
]  # fmt: skip
AMBIGUOUS_PAIRS = [
    ("l", "1"), ("O", "0"), ("I", "l"), ("o", "0"), ("S", "5"), ("a", "o"), ("e", "c"),
]  # fmt: skip
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:?!)\]])")
_SPACE_AFTER_OPEN = re.compile(r"([(\[])\s+")


def char_class(char: str) -> str:
    if char == " ":
        return "espaço"
    if char in "çÇ":
        return "cedilha"
    if char.isdigit():
        return "dígito"
    if unicodedata.category(char)[0] in "PS":
        return "pontuação"
    if char.isalpha():
        if unicodedata.normalize("NFD", char) != char:
            return "acentuada"
        return "maiúscula" if char.isupper() else "minúscula"
    return "outro"


def align(reference: str, hypothesis: str) -> list[tuple[str, str | None, str | None]]:
    """Alinhamento de Levenshtein: lista de ``(operação, char da referência, char da hipótese)``.

    Operações: ``eq``, ``sub``, ``del`` (faltou na hipótese) e ``ins`` (sobrou na hipótese).
    """
    m, n = len(reference), len(hypothesis)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if reference[i - 1] == hypothesis[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + cost, dp[i - 1][j] + 1, dp[i][j - 1] + 1)

    ops: list[tuple[str, str | None, str | None]] = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            same = reference[i - 1] == hypothesis[j - 1]
            if dp[i][j] == dp[i - 1][j - 1] + (0 if same else 1):
                ops.append(("eq" if same else "sub", reference[i - 1], hypothesis[j - 1]))
                i, j = i - 1, j - 1
                continue
        if i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(("del", reference[i - 1], None))
            i -= 1
        else:
            ops.append(("ins", None, hypothesis[j - 1]))
            j -= 1
    ops.reverse()
    return ops


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def glue_punctuation(text: str) -> str:
    """Remove o espaço que alguns modelos inserem antes da pontuação e depois de parênteses."""
    return _SPACE_AFTER_OPEN.sub(r"\1", _SPACE_BEFORE_PUNCT.sub(r"\1", text))


def _micro_cer(pairs: list[tuple[str, str]]) -> float:
    total = sum(len(reference) for reference, _ in pairs)
    edits = sum(levenshtein_distance(reference, hypothesis) for reference, hypothesis in pairs)
    return edits / total if total else 0.0


def analyze(pairs: list[tuple[str, str]], symbols: set[str] | None = None) -> dict[str, Any]:
    """Agrega erros sobre pares ``(referência, hipótese)`` já em NFC."""
    ref_count: Counter[str] = Counter()
    ref_errors: Counter[str] = Counter()
    insertions: Counter[str] = Counter()
    confusions: Counter[tuple[str, str]] = Counter()
    ops_total: Counter[str] = Counter()

    for reference, hypothesis in pairs:
        for op, ref_char, hyp_char in align(reference, hypothesis):
            ops_total[op] += 1
            if ref_char is not None:
                ref_count[char_class(ref_char)] += 1
            if op == "sub":
                ref_errors[char_class(ref_char)] += 1
                confusions[(ref_char, hyp_char)] += 1
            elif op == "del":
                ref_errors[char_class(ref_char)] += 1
                confusions[(ref_char, EMPTY)] += 1
            elif op == "ins":
                insertions[char_class(hyp_char)] += 1
                confusions[(EMPTY, hyp_char)] += 1

    by_class = {
        name: {
            "ref_chars": ref_count[name],
            "errors": ref_errors[name],
            "error_rate": ref_errors[name] / ref_count[name] if ref_count[name] else None,
            "insertions": insertions[name],
        }
        for name in CLASSES
    }
    result: dict[str, Any] = {
        "lines": len(pairs),
        "ref_chars": sum(ref_count.values()),
        "operations": {op: ops_total[op] for op in ("eq", "sub", "del", "ins")},
        "cer": _micro_cer(pairs),
        "cer_without_diacritics": _micro_cer(
            [(strip_diacritics(r), strip_diacritics(h)) for r, h in pairs]
        ),
        "cer_case_insensitive": _micro_cer([(r.casefold(), h.casefold()) for r, h in pairs]),
        "cer_punctuation_glued": _micro_cer([(r, glue_punctuation(h)) for r, h in pairs]),
        "by_class": by_class,
        "top_confusions": [
            {"ref": ref, "hyp": hyp, "count": count}
            for (ref, hyp), count in confusions.most_common(TOP_CONFUSIONS)
        ],
        "ambiguous_pairs": [
            {"a": a, "b": b, "count": confusions[(a, b)] + confusions[(b, a)]}
            for a, b in AMBIGUOUS_PAIRS
        ],
    }
    if symbols is not None:
        text = "".join(reference for reference, _ in pairs)
        missing = Counter(ch for ch in text if ch != " " and ch not in symbols)
        result["alphabet"] = {
            "symbols": len(symbols),
            "unreachable_ref_chars": sum(missing.values()),
            "unreachable_share": sum(missing.values()) / len(text) if text else 0.0,
            "unreachable_by_char": dict(missing.most_common()),
        }
    return result


def load_symbols(path: Path) -> set[str]:
    """Lê um ``syms.txt`` do PyLaia e devolve o conjunto de caracteres que o modelo pode emitir."""
    symbols = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            symbol = line.rsplit(maxsplit=1)[0]
            if len(symbol) == 1:
                symbols.add(symbol)
    return symbols


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Análise de erros por caractere (EXP-001)")
    parser.add_argument("--report", required=True, help="relatório completo, com textos")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--syms", default=None, help="syms.txt do PyLaia (opcional)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    run = next(run for run in report["runs"] if run["status"] == "OK")
    predicted = {p["id"]: p["text"] for p in run["predictions"]}
    pairs = [(nfc(line["text"]), nfc(predicted.get(line["id"], ""))) for line in manifest["lines"]]

    result = {
        "schema": SCHEMA,
        "candidate": report["candidate"]["id"],
        "license_status": report["license_status"],
        "dataset": report["dataset"],
        "git": report["git"],
        **analyze(pairs, load_symbols(Path(args.syms)) if args.syms else None),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Análise gravada em {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
