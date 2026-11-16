r"""Simplificação aproximada do LaTeX da referência, para a variante "fórmulas simplificadas" do
CER:
``\frac{a}{b}`` vira ``a/b``, ``\cdot`` vira ``.``, chaves, ``^`` e ``_`` somem. Um leitor de texto
comum nunca escreveria LaTeX; sem isto, todo o erro de fórmula seria creditado à marcação. É uma
aproximação, declarada como tal no relatório."""

from __future__ import annotations

import re

_RULES = [
    (re.compile(r"\\frac\{([^{}]*)\}\{([^{}]*)\}"), r"\1/\2"),
    (re.compile(r"\\(?:text|mathrm|mbox)\{([^{}]*)\}"), r"\1"),
    (re.compile(r"\\(?:left|right)"), ""),
    (re.compile(r"\\(?:cdot|times)"), "."),
    (re.compile(r"\\(?:quad|qquad|,|;)"), " "),
    (re.compile(r"\\Rightarrow|\\rightarrow|\\to"), "=>"),
    (re.compile(r"\\(?:cong|approx)"), "~"),
    (re.compile(r"\\(?:leq|le)\b"), "<="),
    (re.compile(r"\\(?:geq|ge)\b"), ">="),
    (re.compile(r"\\sqrt"), "V"),
    (re.compile(r"\\(log|ln|sin|cos|tan)\b"), r"\1"),
    (re.compile(r"\\%"), "%"),
    (re.compile(r"[{}^_]"), ""),
]


def delatex(text: str, mask: list[bool] | None = None) -> str:
    """Com ``mask`` (um booleano por caractere), simplifica só os trechos de fórmula."""
    if mask is None:
        out = text
        for pattern, repl in _RULES:
            out = pattern.sub(repl, out)
        return " ".join(out.split())
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = start
        while end < len(text) and mask[end] == mask[start]:
            end += 1
        segment = text[start:end]
        pieces.append(delatex(segment) if mask[start] else segment)
        start = end
    return " ".join("".join(pieces).split())


def delatex_ref(text: str, mask: list[bool]) -> tuple[str, list[bool]]:
    """Versão com máscara de saída: os trechos de fórmula simplificados continuam marcados."""
    out_text: list[str] = []
    out_mask: list[bool] = []
    start = 0
    while start < len(text):
        end = start
        while end < len(text) and mask[end] == mask[start]:
            end += 1
        segment = text[start:end]
        if mask[start]:
            segment = delatex(segment)
        out_text.append(segment)
        out_mask.extend([mask[start]] * len(segment))
        start = end
    joined = "".join(out_text)
    # colapsa espaços mantendo a máscara
    text2: list[str] = []
    mask2: list[bool] = []
    previous_space = True
    for char, flag in zip(joined, out_mask, strict=True):
        if char.isspace():
            if previous_space:
                continue
            previous_space = True
            text2.append(" ")
            mask2.append(flag)
        else:
            previous_space = False
            text2.append(char)
            mask2.append(flag)
    if text2 and text2[-1] == " ":
        text2.pop()
        mask2.pop()
    return "".join(text2), mask2
