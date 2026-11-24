"""EXP-044 — alinhamento forçado de um texto fixo (a carta da BFL) às linhas detectadas numa página.

As leituras das linhas são concatenadas e alinhadas ao texto da carta por distância de edição
(caractere a caractere, sem caixa). O caminho de alinhamento diz em que ponto da carta cada linha
começa e termina; esses pontos são levados ao limite de palavra mais próximo. Trechos da carta que
nenhuma linha leu (palavra pulada, linha não detectada) ficam sem dono.
"""

from __future__ import annotations

MAX_CER = 0.45
MIN_WORDS = 3
PAGE_LINES = (8, 25)
SPLIT_SLACK = 1


def levenshtein(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            current[j] = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb))
        previous = current
    return previous[-1]


def cer(hyp: str, ref: str) -> float:
    if not ref:
        return 0.0 if not hyp else 1.0
    return levenshtein(hyp, ref) / len(ref)


def _path_bounds(hyp: str, ref: str) -> tuple[list[int], list[int]]:
    """Para cada posição i da hipótese: a menor e a maior posição j da referência por onde o caminho
    ótimo de alinhamento passa na linha i da matriz."""
    n, m = len(hyp), len(ref)
    table = [list(range(m + 1))]
    for i in range(1, n + 1):
        prev, row, ch = table[-1], [i] + [0] * m, hyp[i - 1]
        for j in range(1, m + 1):
            row[j] = min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + (ch != ref[j - 1]))
        table.append(row)
    low, high = [m] * (n + 1), [0] * (n + 1)
    i, j = n, m
    while True:
        low[i], high[i] = min(low[i], j), max(high[i], j)
        if i == 0 and j == 0:
            break
        here = table[i][j]
        if i and j and here == table[i - 1][j - 1] + (hyp[i - 1] != ref[j - 1]):
            i, j = i - 1, j - 1
        elif j and here == table[i][j - 1] + 1:
            j -= 1
        else:
            i -= 1
    return low, high


def _snap(position: int, cuts: list[int]) -> int:
    return min(cuts, key=lambda c: (abs(c - position), c))


def align_detail(reference: str, hyps: list[str]) -> list[tuple[str, bool]]:
    """Trecho da referência atribuído a cada leitura de linha (vazio se não leu nada dela) e se a
    linha parte uma palavra: a fronteira bruta do alinhamento cai a mais de ``SPLIT_SLACK``
    caracteres de um espaço (palavra com hífen no fim da linha); nesse caso o trecho, levado ao
    limite de palavra, ganha ou perde um pedaço que não está na imagem."""
    ref = " ".join(reference.split())
    starts, joined = [], []
    position = 0
    for hyp in hyps:
        hyp = " ".join(hyp.split())
        starts.append(position)
        joined.append(hyp)
        position += len(hyp) + 1
    hyp_all = " ".join(joined)
    low, high = _path_bounds(hyp_all.lower(), ref.lower())
    cuts = [0, len(ref)] + [k for k, c in enumerate(ref) if c == " "]
    out = []
    for start, hyp in zip(starts, joined, strict=True):
        raw_begin, raw_end = high[start], low[start + len(hyp)]
        begin, end = _snap(raw_begin, cuts), _snap(raw_end, cuts)
        split = abs(raw_begin - begin) > SPLIT_SLACK or abs(raw_end - end) > SPLIT_SLACK
        out.append((ref[begin:end].strip() if end > begin else "", split))
    return out


def align(reference: str, hyps: list[str]) -> list[str]:
    """Trecho da referência atribuído a cada leitura de linha (vazio se não leu nada dela)."""
    return [part for part, _ in align_detail(reference, hyps)]


def accept(hyp: str, ref: str, max_cer: float = MAX_CER, min_words: int = MIN_WORDS) -> bool:
    """Sem caixa: muita gente escreve em maiúsculas, e o filtro não deve descartar essas pessoas."""
    return len(ref.split()) >= min_words and cer(hyp.lower(), ref.lower()) <= max_cer


UPPER_SHARE = 0.7


def label(hyp: str, ref: str, upper_share: float = UPPER_SHARE) -> str:
    """Rótulo da linha: o trecho da carta, em maiúsculas quando a leitura sai quase toda em
    maiúsculas (a pessoa escreveu em letra de forma maiúscula); senão, como na carta."""
    letters = [c for c in hyp if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) >= upper_share:
        return ref.upper()
    return ref


def page_ok(lines: int, bounds: tuple[int, int] = PAGE_LINES) -> bool:
    return bounds[0] <= lines <= bounds[1]
