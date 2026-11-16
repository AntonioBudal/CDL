"""Alinhamento referência ↔ leitura e quebra do erro por origem (Python puro, sem texto na saída).

Origens do erro de página, medidas nesta ordem:

1. **ordem de leitura** — diferença entre a distância da página na ordem do motor e na ordem da
   referência (linhas correspondidas reordenadas);
2. **detecção** — linhas da referência sem correspondência (``missing``), linhas lidas sem
   referência (``spurious``), e grupos de linhas unidas (``merged``) ou partidas (``split``);
3. **reconhecimento** — distância dentro das linhas correspondidas, separada em caracteres de
   fórmula e de texto comum;
4. o que sobra é folga de alinhamento (``residual``).

A correspondência de linhas é heurística (custo normalizado com limiar, depois tentativas de união
e partição entre vizinhas); o relatório registra isso como limitação.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from textnorm import RefLine, page_text, tokenize_words

# ----------------------------------------------------------------------------- distâncias


def levenshtein(a: str | list[str], b: str | list[str]) -> int:
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    previous = list(range(m + 1))
    for i in range(1, n + 1):
        current = [i] + [0] * m
        ai = a[i - 1]
        for j in range(1, m + 1):
            cost = 0 if ai == b[j - 1] else 1
            current[j] = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
        previous = current
    return previous[m]


def normalized(a: str, b: str) -> float:
    """Distância dividida pelo comprimento maior: 0 (iguais) a 1 (nada em comum)."""
    longest = max(len(a), len(b))
    return levenshtein(a, b) / longest if longest else 0.0


def cer(reference: str, hypothesis: str) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein(reference, hypothesis) / len(reference)


def wer(reference: str, hypothesis: str) -> float:
    ref, hyp = tokenize_words(reference), tokenize_words(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein(ref, hyp) / len(ref)


def edit_ops(ref: str | list[str], hyp: str | list[str]) -> list[tuple[str, int, int]]:
    """Caminho de edição: ``(op, i, j)`` com ``op`` em ``eq``, ``sub``, ``del`` (ref[i] some) e
    ``ins`` (hyp[j] entra; ``i`` é o índice do caractere de referência anterior, ou -1)."""
    n, m = len(ref), len(hyp)
    rows = [list(range(m + 1))]
    for i in range(1, n + 1):
        current = [i] + [0] * m
        previous = rows[-1]
        for j in range(1, m + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            current[j] = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
        rows.append(current)
    ops: list[tuple[str, int, int]] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            if rows[i][j] == rows[i - 1][j - 1] + cost:
                ops.append(("eq" if cost == 0 else "sub", i - 1, j - 1))
                i, j = i - 1, j - 1
                continue
        if i > 0 and rows[i][j] == rows[i - 1][j] + 1:
            ops.append(("del", i - 1, j - 1))
            i -= 1
            continue
        ops.append(("ins", i - 1, j - 1))
        j -= 1
    ops.reverse()
    return ops


# ----------------------------------------------------------------------------- correspondência


@dataclass
class Matching:
    """Resultado da correspondência de linhas de uma página."""

    groups: list[tuple[list[int], list[int]]] = field(default_factory=list)  # (refs, hyps)
    missing: list[int] = field(default_factory=list)
    spurious: list[int] = field(default_factory=list)

    @property
    def one_to_one(self) -> int:
        return sum(1 for refs, hyps in self.groups if len(refs) == 1 and len(hyps) == 1)

    @property
    def merged(self) -> int:
        return sum(1 for refs, hyps in self.groups if len(refs) > 1)

    @property
    def split(self) -> int:
        return sum(1 for refs, hyps in self.groups if len(hyps) > 1)


def _join(lines: list[str], idx: list[int]) -> str:
    return " ".join(lines[i] for i in idx)


def match_lines(
    refs: list[str], hyps: list[str], threshold: float = 0.5, margin: float = 0.05
) -> Matching:
    """Correspondência heurística um-a-um com união/partição entre vizinhas.

    1. pares (ref, hyp) por custo normalizado crescente, aceitos se ambos livres e custo ≤ limiar;
    2. **união**: uma ref livre vizinha (±2) de uma ref correspondida entra no grupo se a
       concatenação reduz o custo em pelo menos ``margin``; ou duas/três refs livres consecutivas
       cujo texto junto casa com uma hyp livre;
    3. **partição**: o simétrico, com hyps livres vizinhas;
    4. refs restantes = ``missing``; hyps restantes = ``spurious``.
    """
    n, m = len(refs), len(hyps)
    cost = [[normalized(refs[i], hyps[j]) for j in range(m)] for i in range(n)]
    pairs = sorted((cost[i][j], i, j) for i in range(n) for j in range(m))
    ref_of_hyp: dict[int, list[int]] = {}
    hyp_of_ref: dict[int, list[int]] = {}
    groups: list[tuple[list[int], list[int]]] = []
    for c, i, j in pairs:
        if c > threshold:
            break
        if i in hyp_of_ref or j in ref_of_hyp:
            continue
        groups.append(([i], [j]))
        hyp_of_ref[i] = [j]
        ref_of_hyp[j] = [i]

    def free_refs() -> list[int]:
        return [i for i in range(n) if i not in hyp_of_ref]

    def free_hyps() -> list[int]:
        return [j for j in range(m) if j not in ref_of_hyp]

    # 2a. união: ref livre entra no grupo de uma vizinha correspondida
    changed = True
    while changed:
        changed = False
        for i in free_refs():
            best = None
            for refs_g, hyps_g in groups:
                if len(hyps_g) != 1 or len(refs_g) >= 3:
                    continue
                if min(abs(i - r) for r in refs_g) > 2:
                    continue
                candidate = sorted([*refs_g, i])
                before = normalized(_join(refs, refs_g), _join(hyps, hyps_g))
                after = normalized(_join(refs, candidate), _join(hyps, hyps_g))
                if after + margin <= before and (best is None or after < best[0]):
                    best = (after, refs_g, candidate)
            if best is not None:
                _, refs_g, candidate = best
                refs_g[:] = candidate
                hyp_of_ref[i] = list(groups[[g[0] for g in groups].index(refs_g)][1])
                changed = True
                break
    # 2b. união de refs livres consecutivas numa hyp livre
    for j in free_hyps():
        free = free_refs()
        best = None
        for size in (2, 3):
            for start in range(len(free) - size + 1):
                block = free[start : start + size]
                if block[-1] - block[0] != size - 1:
                    continue
                c = normalized(_join(refs, block), hyps[j])
                if c <= threshold and (best is None or c < best[0]):
                    best = (c, block)
        if best is not None:
            groups.append((best[1], [j]))
            for i in best[1]:
                hyp_of_ref[i] = [j]
            ref_of_hyp[j] = best[1]
    # 3a. partição: hyp livre entra no grupo de uma vizinha correspondida
    changed = True
    while changed:
        changed = False
        for j in free_hyps():
            best = None
            for refs_g, hyps_g in groups:
                if len(refs_g) != 1 or len(hyps_g) >= 3:
                    continue
                if min(abs(j - h) for h in hyps_g) > 2:
                    continue
                candidate = sorted([*hyps_g, j])
                before = normalized(_join(refs, refs_g), _join(hyps, hyps_g))
                after = normalized(_join(refs, refs_g), _join(hyps, candidate))
                if after + margin <= before and (best is None or after < best[0]):
                    best = (after, hyps_g, candidate)
            if best is not None:
                _, hyps_g, candidate = best
                hyps_g[:] = candidate
                ref_of_hyp[j] = list(groups[[g[1] for g in groups].index(hyps_g)][0])
                changed = True
                break
    # 3b. partição de hyps livres consecutivas numa ref livre
    for i in free_refs():
        free = free_hyps()
        best = None
        for size in (2, 3):
            for start in range(len(free) - size + 1):
                block = free[start : start + size]
                if block[-1] - block[0] != size - 1:
                    continue
                c = normalized(refs[i], _join(hyps, block))
                if c <= threshold and (best is None or c < best[0]):
                    best = (c, block)
        if best is not None:
            groups.append(([i], best[1]))
            hyp_of_ref[i] = best[1]
            for j in best[1]:
                ref_of_hyp[j] = [i]
    groups.sort(key=lambda g: g[0][0])
    return Matching(groups=groups, missing=free_refs(), spurious=free_hyps())


# ----------------------------------------------------------------------------- quebra do erro


def inversions(sequence: list[int]) -> int:
    """Pares fora de ordem (distância de Kendall) — 0 quando a sequência é crescente."""
    return sum(
        1
        for a in range(len(sequence))
        for b in range(a + 1, len(sequence))
        if sequence[a] > sequence[b]
    )


def recognition_breakdown(ref: RefLine, hyp: str) -> Counter:
    """Erros por classe do caractere de referência (fórmula / texto) e inserções atribuídas ao
    caractere de referência vizinho. Também conta os totais de cada classe."""
    out: Counter = Counter()
    mask = ref.formula or [False] * len(ref.text)
    out["chars_formula"] = sum(mask)
    out["chars_text"] = len(ref.text) - out["chars_formula"]
    for op, i, _ in edit_ops(ref.text, hyp):
        if op == "eq":
            continue
        klass = "formula" if 0 <= i < len(mask) and mask[i] else "text"
        out[f"errors_{klass}"] += 1
    return out


def word_near_misses(ref: str, hyp: str) -> tuple[Counter, list[tuple[str, str, int]]]:
    """Substituições de palavra por distância (1, 2, 3+), mais omissões e inserções.

    Devolve também os pares (ref, hyp, distância) para o léxico; os pares nunca saem em relatório.
    """
    ref_w, hyp_w = tokenize_words(ref), tokenize_words(hyp)
    out: Counter = Counter({"words_ref": len(ref_w)})
    pairs = []
    for op, i, j in edit_ops(ref_w, hyp_w):
        if op == "eq":
            out["words_ok"] += 1
        elif op == "sub":
            distance = levenshtein(ref_w[i], hyp_w[j])
            bucket = "d1" if distance == 1 else "d2" if distance == 2 else "d3plus"
            out[f"sub_{bucket}"] += 1
            pairs.append((ref_w[i], hyp_w[j], distance))
        elif op == "del":
            out["words_deleted"] += 1
        else:
            out["words_inserted"] += 1
    return out, pairs


def merge_ref(lines: list[RefLine], idx: list[int]) -> RefLine:
    """Junta linhas de referência de um grupo (espaço entre elas, fora de fórmula)."""
    text, mask = [], []
    for k, i in enumerate(idx):
        if k:
            text.append(" ")
            mask.append(False)
        text.append(lines[i].text)
        mask.extend(lines[i].formula or [False] * len(lines[i].text))
    return RefLine(text="".join(text), formula=mask)


@dataclass
class PageScore:
    ref_chars: int
    distance_total: int
    distance_reordered: int
    order: int
    missing_chars: int
    spurious_chars: int
    recognition: int
    residual: int
    matching: Matching
    inversions: int
    recognition_detail: Counter
    words: Counter
    word_pairs: list[tuple[str, str, int]]

    @property
    def cer_total(self) -> float:
        return self.distance_total / self.ref_chars if self.ref_chars else 0.0

    def weights(self) -> dict[str, float]:
        """Parte do erro total atribuída a cada origem (soma 1 quando há erro)."""
        total = self.distance_total or 1
        return {
            "order": self.order / total,
            "missing": self.missing_chars / total,
            "spurious": self.spurious_chars / total,
            "recognition": self.recognition / total,
            "residual": self.residual / total,
        }


def score_page(ref_lines: list[RefLine], hyp_lines: list[str]) -> PageScore:
    refs = [line.text for line in ref_lines]
    hyps = [page_text(h) for h in hyp_lines]
    matching = match_lines(refs, hyps)
    ref_page = page_text(" ".join(refs))
    hyp_page = page_text(" ".join(hyps))
    distance_total = levenshtein(ref_page, hyp_page)

    # ordem: linhas lidas reordenadas pela referência (grupos pela primeira ref), espúrias no fim
    ordered_hyps = []
    for _, hyps_g in matching.groups:
        ordered_hyps.extend(hyps_g)
    ordered_hyps.extend(matching.spurious)
    reordered_page = page_text(" ".join(hyps[j] for j in ordered_hyps))
    distance_reordered = levenshtein(ref_page, reordered_page)
    order = max(distance_total - distance_reordered, 0)
    motor_positions = [min(hyps_g) for _, hyps_g in matching.groups]

    missing_chars = sum(len(refs[i]) for i in matching.missing)
    spurious_chars = sum(len(hyps[j]) for j in matching.spurious)
    recognition = 0
    detail: Counter = Counter()
    words: Counter = Counter()
    word_pairs: list[tuple[str, str, int]] = []
    for refs_g, hyps_g in matching.groups:
        ref_group = merge_ref(ref_lines, refs_g)
        hyp_group = _join(hyps, hyps_g)
        recognition += levenshtein(ref_group.text, hyp_group)
        detail += recognition_breakdown(ref_group, hyp_group)
        w, pairs = word_near_misses(ref_group.text, hyp_group)
        words += w
        word_pairs.extend(pairs)
    words["words_missing_lines"] = sum(len(tokenize_words(refs[i])) for i in matching.missing)
    residual = distance_reordered - missing_chars - spurious_chars - recognition
    return PageScore(
        ref_chars=len(ref_page),
        distance_total=distance_total,
        distance_reordered=distance_reordered,
        order=order,
        missing_chars=missing_chars,
        spurious_chars=spurious_chars,
        recognition=recognition,
        residual=residual,
        matching=matching,
        inversions=inversions(motor_positions),
        recognition_detail=detail,
        words=words,
        word_pairs=word_pairs,
    )
