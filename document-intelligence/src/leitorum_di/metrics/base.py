"""Funções puras e determinísticas para cálculo de métricas em Document Intelligence."""

import unicodedata
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def levenshtein_distance(seq1: Sequence[T], seq2: Sequence[T]) -> int:
    """Calcula a distância de edição de Levenshtein entre duas sequências."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # Deleção
                    dp[i][j - 1],      # Inserção
                    dp[i - 1][j - 1],  # Substituição
                )

    return dp[m][n]


def calculate_cer(reference: str, hypothesis: str) -> float:
    """Calcula a taxa de erro de caracteres (Character Error Rate - CER).

    CER = Levenshtein(reference, hypothesis) / len(reference)
    Retorna 0.0 se ambas as strings forem vazias.
    """
    if not reference:
        return 0.0 if not hypothesis else 1.0

    distance = levenshtein_distance(reference, hypothesis)
    return distance / len(reference)


def _normalize_words(text: str) -> list[str]:
    """Tokeniza por espaços e remove pontuação das bordas de cada token.

    Preserva acentuação e caixa; pontuação interna (ex.: hífen em "guarda-chuva") é mantida.
    Tokens que ficam vazios (ex.: "-" isolado) são descartados.
    """
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


def tokenize_words(text: str) -> list[str]:
    """Tokens de palavra usados pelo WER (pontuação de borda removida, acentos e caixa mantidos)."""
    return _normalize_words(text)


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calcula a taxa de erro de palavras (Word Error Rate - WER).

    WER = Levenshtein(words_ref, words_hyp) / len(words_ref)
    Tokens delimitados por espaços, com pontuação de borda normalizada
    (acentos e caixa preservados).
    """
    ref_words = _normalize_words(reference)
    hyp_words = _normalize_words(hypothesis)

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    distance = levenshtein_distance(ref_words, hyp_words)
    return distance / len(ref_words)


def calculate_iou(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """Calcula a interseção sobre união (IoU) entre duas caixas [x1, y1, x2, y2]."""
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    intersection_area = max(0.0, x_b - x_a) * max(0.0, y_b - y_a)

    area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
    area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])

    union_area = area_a + area_b - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area
