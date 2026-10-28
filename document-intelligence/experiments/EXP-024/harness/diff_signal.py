"""EXP-024 (E1): sinais implícitos tirados da diferença entre o rascunho e o que o leitor salvou.

- ``align_units``: para cada trecho sugerido pelo Organizador, se foi mantido, movido, editado ou
  apagado, e em que seção ficou;
- ``align_reading``: cada linha lida pela máquina contra o texto revisado, com as operações de
  caractere e a classificação da edição (``ocr``, ``rewrite`` ou ``ambiguous``);
- ``to_ldf_corrections`` e ``to_organizer_patch``: as mesmas mudanças como RFC 6902.

Só biblioteca padrão. Nenhuma função grava ou registra texto.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass

SECTIONS = ("summary", "explanation", "concepts", "references")
WORD = re.compile(r"\w+", re.UNICODE)

DEFAULTS = {
    "unit_min_ratio": 0.6,  # cobertura mínima para um trecho editado ainda contar como achado
    "ocr_max_distance": 0.35,  # distância normalizada máxima de uma correção de leitura
    "rewrite_min_distance": 0.6,  # acima disso, reescrita autoral
    "rewrite_new_words": 2,  # palavras novas sem par no lido que indicam reescrita
}


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


# --- Organizador: trecho sugerido x seções salvas -----------------------------------------------


@dataclass
class UnitOutcome:
    index: int
    suggested: str
    final: str | None
    outcome: str  # kept | moved | edited | deleted
    ratio: float


def _coverage(needle: str, haystack: str) -> float:
    if not needle or not haystack:
        return 0.0
    matcher = difflib.SequenceMatcher(None, needle, haystack, autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks()) / len(needle)


def align_units(
    text: str, segments: list[dict], saved: dict[str, str], params: dict | None = None
) -> list[UnitOutcome]:
    """Onde cada trecho sugerido foi parar no estudo salvo."""
    params = {**DEFAULTS, **(params or {})}
    sections = {s: normalize(saved.get(s, "")) for s in SECTIONS}
    used = dict.fromkeys(SECTIONS, 0)  # posição já consumida em cada seção (trechos repetidos)
    out = []
    for seg in segments:
        piece = normalize(text[seg["start"] : seg["end"]])
        found = None
        for section in [seg["section"], *[s for s in SECTIONS if s != seg["section"]]]:
            pos = sections[section].find(piece, used[section]) if piece else -1
            if pos < 0 and piece:
                pos = sections[section].find(piece)
            if pos >= 0:
                found = section
                used[section] = pos + len(piece)
                break
        if found is not None:
            outcome = "kept" if found == seg["section"] else "moved"
            out.append(UnitOutcome(seg["index"], seg["section"], found, outcome, 1.0))
            continue
        best, best_ratio = None, 0.0
        for section in SECTIONS:
            ratio = _coverage(piece, sections[section])
            if ratio > best_ratio:
                best, best_ratio = section, ratio
        if best is not None and best_ratio >= params["unit_min_ratio"]:
            out.append(
                UnitOutcome(seg["index"], seg["section"], best, "edited", round(best_ratio, 4))
            )
        else:
            out.append(
                UnitOutcome(seg["index"], seg["section"], None, "deleted", round(best_ratio, 4))
            )
    return out


# --- Leitura: linha lida x texto revisado --------------------------------------------------------


def levenshtein_ops(a: str, b: str) -> tuple[int, list[tuple[str, str]]]:
    """Distância e operações agrupadas (trecho lido, trecho certo), de até 2 caracteres."""
    n, m = len(a), len(b)
    dist = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dist[i][0] = i
    for j in range(m + 1):
        dist[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist[i][j] = min(
                dist[i - 1][j] + 1, dist[i][j - 1] + 1, dist[i - 1][j - 1] + (a[i - 1] != b[j - 1])
            )
    i, j, ops, run_a, run_b = n, m, [], [], []

    def flush():
        if run_a or run_b:
            ops.append(("".join(reversed(run_a)), "".join(reversed(run_b))))
            run_a.clear()
            run_b.clear()

    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and dist[i][j] == dist[i - 1][j - 1]:
            flush()
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dist[i][j] == dist[i - 1][j - 1] + 1:
            run_a.append(a[i - 1])
            run_b.append(b[j - 1])
            i, j = i - 1, j - 1
        elif i > 0 and dist[i][j] == dist[i - 1][j] + 1:
            run_a.append(a[i - 1])
            i -= 1
        else:
            run_b.append(b[j - 1])
            j -= 1
    flush()
    ops.reverse()
    return dist[n][m], [(x, y) for x, y in ops if len(x) <= 2 and len(y) <= 2]


@dataclass
class LineEdit:
    line: int
    read: str
    revised: str
    distance: float
    kind: str  # same | ocr | rewrite | ambiguous
    ops: list[tuple[str, str]]
    word_pairs: list[tuple[str, str]]


def classify_edit(read: str, revised: str, params: dict | None = None) -> tuple[str, float]:
    params = {**DEFAULTS, **(params or {})}
    if read == revised:
        return "same", 0.0
    raw, _ = levenshtein_ops(read, revised)
    distance = raw / max(1, len(read), len(revised))
    read_words = [fold(w) for w in WORD.findall(read)]
    new_words = 0
    for word in WORD.findall(revised):
        folded = fold(word)
        best = max(
            (difflib.SequenceMatcher(None, folded, r, autojunk=False).ratio() for r in read_words),
            default=0.0,
        )
        new_words += best < 0.5 and len(folded) > 2
    if distance > params["rewrite_min_distance"] or new_words >= params["rewrite_new_words"]:
        return "rewrite", distance
    if distance <= params["ocr_max_distance"]:
        return "ocr", distance
    return "ambiguous", distance


def word_pairs(read: str, revised: str) -> list[tuple[str, str]]:
    """Pares (palavra lida, palavra certa) alinhados por posição de palavra."""
    a, b = WORD.findall(read), WORD.findall(revised)
    pairs = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            pairs.extend((w, w) for w in a[i1:i2])
        elif op == "replace" and i2 - i1 == j2 - j1:
            pairs.extend(zip(a[i1:i2], b[j1:j2], strict=False))
    return pairs


def _fragments(saved: dict[str, str]) -> list[str]:
    return [line for s in SECTIONS for line in saved.get(s, "").split("\n") if line.strip()]


def align_reading(
    source_lines: list[str], saved: dict[str, str], params: dict | None = None
) -> list[LineEdit]:
    """Casa cada linha lida com o trecho salvo mais parecido e classifica a edição."""
    fragments = _fragments(saved)
    out = []
    for k, read in enumerate(source_lines):
        if not read.strip():
            continue
        best, best_ratio = None, 0.0
        for frag in fragments:
            ratio = difflib.SequenceMatcher(None, read, frag, autojunk=False).ratio()
            if ratio > best_ratio:
                best, best_ratio = frag, ratio
        if best is None or best_ratio < 0.3:
            out.append(LineEdit(k, read, "", 1.0, "rewrite", [], []))
            continue
        kind, distance = classify_edit(read, best, params)
        ops = levenshtein_ops(read, best)[1] if kind == "ocr" else []
        pairs = word_pairs(read, best) if kind in ("ocr", "same") else []
        out.append(LineEdit(k, read, best, round(distance, 4), kind, ops, pairs))
    return out


# --- RFC 6902 ---------------------------------------------------------------------------------


def to_ldf_corrections(
    line_ids: list[str], edits: list[LineEdit], author: str, timestamp: str
) -> list[dict]:
    """Correções de leitura como ``human_corrections`` do LDF 2.0 (só as do tipo ``ocr``)."""
    out = []
    for edit in edits:
        if edit.kind != "ocr":
            continue
        out.append(
            {
                "id": f"corr-{line_ids[edit.line]}",
                "author": author,
                "timestamp": timestamp,
                "reason": "ocr-fix",
                "target": {"collection": "recognition.lines", "id": line_ids[edit.line]},
                "ops": [{"op": "replace", "path": "/text", "value": edit.revised}],
            }
        )
    return out


def to_organizer_patch(outcomes: list[UnitOutcome]) -> list[dict]:
    """Movimentos de seção como RFC 6902 sobre o documento ``organizer-result/1``."""
    return [
        {"op": "replace", "path": f"/segments/{o.index}/section", "value": o.final}
        for o in outcomes
        if o.outcome == "moved"
    ]
