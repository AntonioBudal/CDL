"""Normalização de texto e leitura dos arquivos de referência do EXP-027 (Python puro).

Formato da referência (``pNN.txt``): uma linha por linha física do caderno, na ordem de leitura;
fórmulas entre ``$…$`` (LaTeX simples); ``[figura]`` para desenho ou diagrama; ``[?]`` para trecho
ilegível. Esta camada tira as marcas e guarda, por caractere, se ele está dentro de uma fórmula.
Nenhuma função devolve texto que não tenha vindo do chamador.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

FIGURE = "[figura]"
ILLEGIBLE = "[?]"
_SPACES = re.compile(r"\s+")


@dataclass
class RefLine:
    """Uma linha de referência já sem marcas."""

    text: str
    formula: list[bool] = field(default_factory=list)  # um booleano por caractere de ``text``
    figure: bool = False  # a linha inteira é ``[figura]``
    illegible: bool = False  # havia ``[?]`` na linha

    @property
    def formula_chars(self) -> int:
        return sum(self.formula)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def page_text(text: str) -> str:
    """Normalização de página: NFC e espaços em branco colapsados (como no EXP-022)."""
    return " ".join(nfc(text).split())


def parse_ref_line(raw: str) -> RefLine:
    """Tira ``$…$``, ``[figura]`` e ``[?]`` e marca os caracteres de fórmula."""
    line = nfc(raw.strip())
    if line == FIGURE:
        return RefLine(text="", figure=True)
    illegible = ILLEGIBLE in line
    line = line.replace(ILLEGIBLE, "")
    out: list[str] = []
    mask: list[bool] = []
    inside = False
    for char in line:
        if char == "$":
            inside = not inside
            continue
        out.append(char)
        mask.append(inside)
    text = "".join(out)
    # colapsa espaços mantendo a máscara alinhada
    collapsed: list[str] = []
    collapsed_mask: list[bool] = []
    previous_space = True
    for char, is_formula in zip(text, mask, strict=True):
        if char.isspace():
            if previous_space:
                continue
            previous_space = True
            collapsed.append(" ")
            collapsed_mask.append(is_formula)
        else:
            previous_space = False
            collapsed.append(char)
            collapsed_mask.append(is_formula)
    if collapsed and collapsed[-1] == " ":
        collapsed.pop()
        collapsed_mask.pop()
    return RefLine(text="".join(collapsed), formula=collapsed_mask, illegible=illegible)


def parse_reference(content: str) -> list[RefLine]:
    """Linhas de um ``pNN.txt``; linhas em branco são ignoradas."""
    return [parse_ref_line(raw) for raw in content.splitlines() if raw.strip()]


def text_lines(lines: list[RefLine]) -> list[RefLine]:
    """Só as linhas com texto (sem as que são apenas ``[figura]``)."""
    return [line for line in lines if not line.figure and line.text]


def tokenize_words(text: str) -> list[str]:
    """Tokens de palavra do WER aprovado: pontuação de borda removida, acentos e caixa mantidos."""
    words = []
    for token in text.split():
        start, end = 0, len(token)
        while start < end and unicodedata.category(token[start]).startswith("P"):
            start += 1
        while end > start and unicodedata.category(token[end - 1]).startswith("P"):
            end -= 1
        if start < end:
            words.append(token[start:end])
    return words
