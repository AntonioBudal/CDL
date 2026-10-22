"""Métricas de leitura do EXP-009: CER/WER de linha, CER de página e CER por classe de caractere.

Linha: Unicode NFC, como no EXP-001 (nenhuma outra normalização antes do CER). Página: NFC, marcas
de
anotação do BRESSAY removidas (``@@``, ``##``, ``$$``, ``--``) e espaços em branco colapsados, nos
dois
lados. WER com a normalização aprovada do pacote (pontuação de borda removida; acentos e caixa
preservados). Nenhum texto é devolvido: só contagens.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

from leitorum_di.metrics.base import levenshtein_distance, tokenize_words

MARKS = re.compile(r"@@|##|\$\$|--")
CLASSES = ("letra", "letra acentuada", "dígito", "pontuação", "espaço", "outro")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def page_text(text: str) -> str:
    """Normalização de página (FR-002)."""
    return " ".join(MARKS.sub(" ", nfc(text)).split())


def char_class(char: str) -> str:
    if char.isspace():
        return "espaço"
    if char.isdigit():
        return "dígito"
    if char.isalpha():
        decomposed = unicodedata.normalize("NFD", char)
        return "letra acentuada" if len(decomposed) > 1 else "letra"
    if unicodedata.category(char).startswith("P"):
        return "pontuação"
    return "outro"


def align_errors(reference: str, hypothesis: str) -> tuple[Counter, Counter, int]:
    """Por classe do caractere de referência: total e erros (troca ou omissão); e inserções."""
    n, m = len(reference), len(hypothesis)
    previous = list(range(m + 1))
    rows = [previous]
    for i in range(1, n + 1):
        current = [i] + [0] * m
        for j in range(1, m + 1):
            cost = 0 if reference[i - 1] == hypothesis[j - 1] else 1
            current[j] = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
        rows.append(current)
        previous = current
    totals, errors = Counter(char_class(c) for c in reference), Counter()
    insertions = 0
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if reference[i - 1] == hypothesis[j - 1] else 1
            if rows[i][j] == rows[i - 1][j - 1] + cost:
                if cost:
                    errors[char_class(reference[i - 1])] += 1
                i, j = i - 1, j - 1
                continue
        if i > 0 and rows[i][j] == rows[i - 1][j] + 1:
            errors[char_class(reference[i - 1])] += 1
            i -= 1
        else:
            insertions += 1
            j -= 1
    return totals, errors, insertions


def line_metrics(references: dict[str, str], predictions: dict[str, str]) -> dict[str, Any]:
    """CER e WER micro e macro, como no EXP-001; linhas sem predição contam como vazias."""
    char_edits = char_total = word_edits = word_total = 0
    per_line = []
    totals, errors = Counter(), Counter()
    insertions = 0
    for key, raw_reference in references.items():
        reference = nfc(raw_reference)
        hypothesis = nfc(predictions.get(key, ""))
        edits = levenshtein_distance(reference, hypothesis)
        ref_words, hyp_words = tokenize_words(reference), tokenize_words(hypothesis)
        word = levenshtein_distance(ref_words, hyp_words)
        char_edits += edits
        char_total += len(reference)
        word_edits += word
        word_total += len(ref_words)
        per_line.append(edits / len(reference) if reference else float(bool(hypothesis)))
        line_totals, line_errors, line_insertions = align_errors(reference, hypothesis)
        totals.update(line_totals)
        errors.update(line_errors)
        insertions += line_insertions
    count = len(per_line)
    return {
        "lines": count,
        "missing": sum(1 for key in references if key not in predictions),
        "cer_micro": char_edits / char_total if char_total else 0.0,
        "wer_micro": word_edits / word_total if word_total else 0.0,
        "cer_macro": sum(per_line) / count if count else 0.0,
        "ref_chars": char_total,
        "ref_words": word_total,
        "lines_with_cer_below_10pct": sum(1 for value in per_line if value < 0.10),
        "cer_by_class": {
            name: {"chars": totals[name], "cer": errors[name] / totals[name]}
            for name in CLASSES
            if totals[name]
        },
        "insertions": insertions,
    }


def page_metrics(references: dict[str, str], predictions: dict[str, str]) -> dict[str, Any]:
    """CER e WER de página (micro), com a normalização de página."""
    char_edits = char_total = word_edits = word_total = 0
    per_page = []
    for key, raw_reference in references.items():
        reference = page_text(raw_reference)
        hypothesis = page_text(predictions.get(key, ""))
        edits = levenshtein_distance(reference, hypothesis)
        ref_words, hyp_words = tokenize_words(reference), tokenize_words(hypothesis)
        char_edits += edits
        char_total += len(reference)
        word_edits += levenshtein_distance(ref_words, hyp_words)
        word_total += len(ref_words)
        per_page.append(edits / len(reference) if reference else 0.0)
    ordered = sorted(per_page)
    return {
        "pages": len(per_page),
        "cer_micro": char_edits / char_total if char_total else 0.0,
        "wer_micro": word_edits / word_total if word_total else 0.0,
        "page_cer_median": ordered[len(ordered) // 2] if ordered else None,
        "ref_chars": char_total,
    }
