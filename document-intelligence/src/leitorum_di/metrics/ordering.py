"""Métricas de ordem de leitura: acurácia por distância de edição e tau de Kendall.

Funções puras sobre sequências de identificadores, sem dependências externas.
"""

from __future__ import annotations

from collections.abc import Hashable, Sequence

from leitorum_di.metrics.base import levenshtein_distance


def order_edit_counts(predicted: Sequence[Hashable], truth: Sequence[Hashable]) -> tuple[int, int]:
    """Devolve ``(distância de edição, denominador)``; o denominador é o maior comprimento."""
    return levenshtein_distance(list(truth), list(predicted)), max(len(predicted), len(truth))


def order_accuracy(predicted: Sequence[Hashable], truth: Sequence[Hashable]) -> float:
    """Acurácia de ordem = 1 − distância de edição / maior comprimento (1,0 se ambas vazias)."""
    distance, denominator = order_edit_counts(predicted, truth)
    return 1.0 if denominator == 0 else 1.0 - distance / denominator


def kendall_tau(predicted: Sequence[Hashable], truth: Sequence[Hashable]) -> float | None:
    """Tau de Kendall sobre os elementos presentes nas duas sequências (``None`` se menos de 2).

    Ignora faltas e sobras: mede só se os elementos em comum estão na mesma ordem relativa.
    """
    position = {item: index for index, item in enumerate(truth)}
    common = [position[item] for item in predicted if item in position]
    n = len(common)
    if n < 2:
        return None
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            if common[i] < common[j]:
                concordant += 1
            elif common[i] > common[j]:
                discordant += 1
    pairs = n * (n - 1) / 2
    return (concordant - discordant) / pairs


def out_of_order(predicted: Sequence[Hashable], truth: Sequence[Hashable]) -> list[Hashable]:
    """Elementos da verdade fora da maior subsequência comum (deslocados ou ausentes)."""
    a, b = list(truth), list(predicted)
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if a[i] == b[j]:
                table[i][j] = table[i + 1][j + 1] + 1
            else:
                table[i][j] = max(table[i + 1][j], table[i][j + 1])
    kept = set()
    i = j = 0
    while i < m and j < n:
        if a[i] == b[j]:
            kept.add(i)
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            i += 1
        else:
            j += 1
    return [item for index, item in enumerate(a) if index not in kept]
