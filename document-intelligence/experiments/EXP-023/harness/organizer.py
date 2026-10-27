# ruff: noqa: N803, N806, N815 — nomes em maiúscula seguem a notação da spec (A, S, T, F, W, X)
"""EXP-023: organização de um texto de anotações nas 4 seções do Estudo, em Python puro.

Referência para o produto (spec §2–§5): só biblioteca padrão. Etapas:

1. cabeçalhos explícitos (sinônimos do ``import_parser`` do Leitorum) viram restrições rígidas;
2. segmentação: linhas físicas → blocos (pistas de texto e, se houver, geometria) → sentenças;
3. vetor de cada unidade: pistas estruturais/discursivas ``f`` + cossenos a 4 centróides de
   n-gramas de caracteres com hashing (``s``);
4. afinidade ``A = log softmax((W x + b) / beta)``;
5. coesão ``S`` entre vizinhos, propagação de rótulos e Viterbi com transição ``T`` e custo de troca
   ponderado por ``S``; forward-backward dá a confiança.

Nada é reescrito: cada unidade é um trecho ``[start, end)`` do texto recebido.
"""

from __future__ import annotations

import difflib
import math
import re
import unicodedata
import zlib
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

SECTIONS = ("summary", "explanation", "concepts", "references")
LABEL_OF = {"s": "summary", "e": "explanation", "c": "concepts", "r": "references"}
CODE_OF = {v: k for k, v in LABEL_OF.items()}
HASH_DIM = 1 << 18
NGRAMS = (3, 4, 5)
NEG_INF = float("-inf")

# --- Normalização -----------------------------------------------------------------------------


def fold(text: str) -> str:
    """Minúsculas e sem acento (o leitor erra 80 % dos acentos, EXP-009)."""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


WORD = re.compile(r"[0-9a-zç]+(?:-[0-9a-zç]+)*")


def words(folded: str) -> list[str]:
    return WORD.findall(folded)


# --- Pistas (listas escritas à mão; os pesos vêm do treino) -------------------------------------

CUES: dict[str, list[str]] = {
    "summary_marker": [
        "em suma",
        "em resumo",
        "resumindo",
        "em sintese",
        "sintese",
        "resumo",
        "de modo geral",
        "de forma geral",
        "em linhas gerais",
        "no geral",
        "ideia central",
        "ideia principal",
        "tese",
        "visao geral",
        "panorama",
    ],
    "summary_topic": [
        "o capitulo",
        "este capitulo",
        "neste capitulo",
        "o cap",
        "cap",
        "o texto",
        "o livro",
        "a obra",
        "o artigo",
        "o autor",
        "a autora",
    ],
    "summary_verb": [
        "trata",
        "apresenta",
        "aborda",
        "discute",
        "mostra",
        "defende",
        "argumenta",
        "afirma",
        "sustenta",
        "conclui",
        "examina",
        "compara",
        "propoe",
        "resume",
        "fecha",
        "termina",
        "conta",
        "explica",
    ],
    "explanation_connective": [
        "porque",
        "pois",
        "portanto",
        "logo",
        "assim",
        "por isso",
        "ja que",
        "uma vez que",
        "visto que",
        "dessa forma",
        "desse modo",
        "consequentemente",
        "ou seja",
        "isto e",
        "por exemplo",
        "no entanto",
        "contudo",
        "entretanto",
        "embora",
        "mas",
        "entao",
        "quando",
        "se",
        "como",
    ],
    "explanation_first_person": [
        "eu",
        "acho",
        "penso",
        "percebo",
        "percebi",
        "me parece",
        "concordo",
        "discordo",
        "entendi",
        "achei",
        "lembrei",
        "me pergunto",
        "nao entendi",
        "minha",
        "meu",
        "vi",
    ],
    "concept_verb": [
        "sao",
        "significa",
        "significam",
        "define-se",
        "denomina-se",
        "consiste em",
        "refere-se a",
        "entende-se por",
        "chama-se",
        "trata-se de",
        "conceito de",
        "nocao de",
        "definicao",
    ],
    "reference_marker": [
        "cf",
        "apud",
        "ver tambem",
        "fonte",
        "in",
        "disponivel em",
        "op cit",
        "ibid",
        "referencia",
        "bibliografia",
        "editora",
        "ed",
        "trad",
        "traducao",
        "org",
        "v",
        "n",
        "isbn",
    ],
}

ABBREVIATIONS = {
    "p",
    "pp",
    "cf",
    "ed",
    "org",
    "vol",
    "v",
    "n",
    "cap",
    "fig",
    "al",
    "cit",
    "ibid",
    "id",
    "sr",
    "sra",
    "dr",
    "dra",
    "prof",
    "sec",
    "art",
    "ex",
    "obs",
    "trad",
    "tab",
    "ap",
    "nº",
}

MARKER_START = re.compile(r"^\s*(?:[-–—•*·]|→|->|=>|\d{1,2}[.)]|[a-z][)])\s+")
ARROW_START = re.compile(r"^\s*(?:→|->|=>)")
LIST_START = re.compile(r"^\s*(?:[-–—•*·]|\d{1,2}[.)]|[a-z][)])\s+")
QUOTE_CHARS = '"“”«»'
QUOTED = re.compile(r"[\"“«]([^\"”»]{3,})[\"”»]")
QUOTE_LINE = re.compile(r"^\s*[\"“«][^\n]{3,}[\"”»]\s*(?:\([^)]{0,60}\))?\s*[.]?\s*$")
PAGE = re.compile(r"\bpp?\.\s*\d+(?:\s*[-–]\s*\d+)?", re.IGNORECASE)
PAGE_COMMENT = re.compile(r"^\s*pp?\.\s*\d+(?:\s*[-–]\s*\d+)?\s*[—–-]\s*\S", re.IGNORECASE)
AUTHOR_YEAR = re.compile(
    r"\(\s*[A-ZÁÂÃÉÊÍÓÔÕÚÇ][A-ZÁÂÃÉÊÍÓÔÕÚÇ'\-]+(?:\s+et al\.)?"
    r"(?:;\s*[A-ZÁÂÃÉÊÍÓÔÕÚÇ][A-ZÁÂÃÉÊÍÓÔÕÚÇ'\-]+)*,\s*\d{4}[a-z]?"
    r"(?:,\s*pp?\.\s*\d+(?:\s*[-–]\s*\d+)?)?\s*\)"
)
ABNT = re.compile(
    r"^\s*(?:ver tamb[ée]m\s+|fonte:\s*|refer[êe]ncia:\s*)?"
    r"[A-ZÁÂÃÉÊÍÓÔÕÚÇ]{2,}(?:\s+[A-ZÁÂÃÉÊÍÓÔÕÚÇ]{2,})*,\s+[A-ZÁÂÃÉÊÍÓÔÕÚÇ]"
)
YEAR = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
REF_START = re.compile(
    r"^\s*(?:cf\.?|apud|ver tamb[ée]m|fonte\s*:|in\s*:|dispon[íi]vel em|op\.\s*cit|ibid"
    r"|refer[êe]ncia\s*:)",
    re.IGNORECASE,
)
URL = re.compile(r"https?://|www\.|isbn", re.IGNORECASE)
TERM_SEP = re.compile(
    r"^\s*(?:[-–—•*·]\s+)?(?:\*\*)?([^\s:=—–]+(?:[ ]+[^\s:=—–]+){0,3}?)(?:\*\*)?"
    r"\s*(?::|=|—|–|\s-\s)\s*\S"
)
DEF_VERB_EARLY = re.compile(
    r"^\s*(?:[-–—•*·]\s+)?\S+(?:\s+\S+){0,4}?\s+(?:é|e|são|sao|significa|significam|consiste|refere-se|chama-se|denomina-se)\s",
    re.IGNORECASE,
)

# --- Cabeçalhos explícitos (mesmos sinônimos do import_parser do Leitorum) ------------------------

HEADING_SYNONYMS = {
    "summary": ("resumo", "visao geral", "visao-geral", "sintese", "ideia central", "introducao"),
    "explanation": (
        "explicacao",
        "aprofundamento",
        "desenvolvimento",
        "analise",
        "compreensao",
        "detalhamento",
    ),
    "concepts": (
        "conceitos",
        "conceitos-chave",
        "termos",
        "termos-chave",
        "vocabulario",
        "glossario",
        "glossario e termos",
        "definicoes",
    ),
    "references": (
        "referencias",
        "fontes",
        "fontes consultadas",
        "bibliografia",
        "leituras complementares",
        "obras citadas",
    ),
}
HEADING_KEYS = {syn: key for key, syns in HEADING_SYNONYMS.items() for syn in syns}
HEADING_STRIP = re.compile(r"^[#\s*_]+|[#\s*_:\-–—]+$")


def heading_section(line: str) -> str | None:
    """Seção de uma linha que é só um cabeçalho ("Resumo:", "## Conceitos"), senão ``None``."""
    candidate = HEADING_STRIP.sub("", fold(line)).strip()
    return HEADING_KEYS.get(candidate)


# --- Busca de pistas com tolerância a erro de leitura ---------------------------------------------


def _deletes(word: str) -> set[str]:
    return {word[:i] + word[i + 1 :] for i in range(len(word))}


def _within_one(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b, strict=False)) == 1
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    return any(long_[:i] + long_[i + 1 :] == short for i in range(len(long_)))


class CueIndex:
    """Frases-pista por família; palavras com 5+ letras aceitam distância de edição 1."""

    def __init__(self, cues: dict[str, list[str]]) -> None:
        self.phrases = {
            family: [tuple(words(fold(p))) for p in plist] for family, plist in cues.items()
        }
        self.by_first: dict[str, list[tuple[str, tuple[str, ...]]]] = {}
        for family, plist in self.phrases.items():
            for phrase in plist:
                if phrase:
                    self.by_first.setdefault(phrase[0], []).append((family, phrase))
        vocab = {w for plist in self.phrases.values() for p in plist for w in p}
        self.exact = vocab
        self.by_delete: dict[str, set[str]] = {}
        for w in vocab:
            if len(w) >= 5:
                for d in _deletes(w) | {w}:
                    self.by_delete.setdefault(d, set()).add(w)

    def canonical(self, token: str) -> str:
        if token in self.exact or len(token) < 4:
            return token
        candidates = set(self.by_delete.get(token, ())) | {
            c for d in _deletes(token) for c in self.by_delete.get(d, ())
        }
        for c in sorted(candidates):
            if _within_one(token, c):
                return c
        return token

    def count(self, tokens: list[str]) -> dict[str, int]:
        canon = [self.canonical(t) for t in tokens]
        out = dict.fromkeys(self.phrases, 0)
        for i, token in enumerate(canon):
            for family, phrase in self.by_first.get(token, ()):
                if tuple(canon[i : i + len(phrase)]) == phrase:
                    out[family] += 1
        return out


# --- Segmentação -------------------------------------------------------------------------------


@dataclass
class Line:
    start: int
    end: int
    text: str
    bbox: list[float] | None = None
    confidence: float | None = None


@dataclass
class Unit:
    start: int
    end: int
    text: str
    lines: list[int]
    block: int
    heading: str | None = None
    features: dict[str, float] = field(default_factory=dict)


def split_lines(text: str) -> list[Line]:
    out, pos = [], 0
    for raw in text.split("\n"):
        out.append(Line(pos, pos + len(raw), raw))
        pos += len(raw) + 1
    return out


def attach_layout(lines: list[Line], layout: list[dict[str, Any]] | None) -> None:
    """Casa as linhas atuais com as lidas (o texto pode ter sido editado) e herda a geometria."""
    if not layout:
        return
    current = [fold(ln.text).strip() for ln in lines]
    original = [fold(str(item.get("text", ""))).strip() for item in layout]
    matcher = difflib.SequenceMatcher(a=current, b=original, autojunk=False)
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            item = layout[block.b + k]
            lines[block.a + k].bbox = item.get("bbox")
            lines[block.a + k].confidence = item.get("confidence")
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace" and i2 - i1 == j2 - j1:  # linha editada no mesmo lugar: herda a posição
            for k in range(i2 - i1):
                item = layout[j1 + k]
                lines[i1 + k].bbox = item.get("bbox")
                lines[i1 + k].confidence = item.get("confidence")


def _pitch(lines: list[Line]) -> float | None:
    tops = [ln.bbox[1] for ln in lines if ln.bbox and ln.text.strip()]
    gaps = sorted(b - a for a, b in zip(tops, tops[1:], strict=False) if b > a)
    return gaps[(len(gaps) - 1) // 2] if gaps else None  # mediana inferior


def _margins(lines: list[Line]) -> tuple[float, float] | None:
    boxes = [ln.bbox for ln in lines if ln.bbox and ln.text.strip()]
    if not boxes:
        return None
    lefts = sorted(b[0] for b in boxes)
    rights = sorted(b[2] for b in boxes)
    return lefts[len(lefts) // 10], rights[(len(rights) * 9) // 10]


def is_whole_line_unit(text: str) -> bool:
    """Linha que vira unidade inteira: referência ABNT, remissão, citação em linha própria."""
    return (
        bool(ABNT.match(text) and YEAR.search(text))
        or bool(REF_START.match(text))
        or bool(QUOTE_LINE.match(text))
    )


def is_whole_block(text: str) -> bool:
    """Bloco que não se divide em sentenças: referência, remissão ou citação, mesmo quebrada."""
    flat = " ".join(text.split())
    return is_whole_line_unit(flat)


def open_reference(block_text: str) -> bool:
    """Bloco que começou como referência ABNT ou citação e não terminou (sem ano, aspas abertas)."""
    flat = " ".join(block_text.split())
    if ABNT.match(flat) and not YEAR.search(flat):
        return True
    opened = flat.count("“") + flat.count("«") - flat.count("”") - flat.count("»")
    return opened > 0 or (flat.lstrip()[:1] == '"' and flat.count('"') % 2 == 1)


def continues(
    prev: Line, nxt: Line, pitch: float | None, margins: tuple[float, float] | None, params: dict
) -> tuple[bool, float]:
    """Se ``nxt`` continua o bloco de ``prev``; devolve (continua?, intervalo em linhas)."""
    p, n = prev.text.rstrip(), nxt.text.strip()
    if not p.strip() or not n:
        return False, 2.0
    if MARKER_START.match(nxt.text) or heading_section(nxt.text) or heading_section(prev.text):
        return False, 1.0
    if PAGE_COMMENT.match(nxt.text) or re.match(r"^\s*pp?\.\s*\d", nxt.text):
        return False, 1.0  # anotação presa a uma página começa unidade própria
    if nxt.text.lstrip()[:1] in '“«"':
        return False, 1.0  # citação começa unidade própria
    if is_whole_line_unit(nxt.text) or (
        is_whole_line_unit(prev.text) and not open_reference(prev.text)
    ):
        return False, 1.0
    gap = 1.0
    score = 0.0
    if p[-1] not in ".!?;:":
        score += 1.0
    if p[-1] == ":":
        score -= 1.5
    if n[0].islower():
        score += 1.0
    elif n[0].isupper():
        score -= 0.5
    if p.endswith("-") and len(p) > 1 and p[-2].isalpha():
        score += 1.5
    if pitch and prev.bbox and nxt.bbox:
        gap = max(0.0, (nxt.bbox[1] - prev.bbox[1]) / pitch)
        if gap > params.get("gap_break", 1.6):
            score -= 2.5
        if margins:
            left, right = margins
            width = max(1.0, right - left)
            if (nxt.bbox[0] - left) / width > 0.04 and (prev.bbox[0] - left) / width < 0.03:
                score -= 1.0  # recuo de primeira linha de parágrafo
            if (right - prev.bbox[2]) / width > 0.25:
                score -= 1.0  # linha que não chega à margem: fim de parágrafo
            else:
                score += 0.5
    return score >= 0.0, gap


def _sentence_cuts(text: str) -> list[int]:
    """Posições (relativas) onde começa uma nova sentença dentro de um bloco."""
    cuts = []
    for m in re.finditer(r"[.!?…]+[\"”»)]?(\s+)(?=[\"“«(]?[A-ZÁÂÃÉÊÍÓÔÕÚÇ0-9→\-–—•])", text):
        before = text[: m.start()]
        token = re.findall(r"[\wº]+$", before)
        if token:
            t = fold(token[0])
            if t in ABBREVIATIONS or (len(token[0]) == 1 and token[0].isupper()):
                continue
        cuts.append(m.end())
    return cuts


def segment(
    text: str, layout: list[dict[str, Any]] | None = None, params: dict | None = None
) -> tuple[list[Unit], list[Line]]:
    params = params or {}
    lines = split_lines(text)
    attach_layout(lines, layout)
    pitch, margins = _pitch(lines), _margins(lines)
    # blocos de linhas
    blocks: list[list[int]] = []
    gaps_before: dict[int, float] = {}
    previous: int | None = None
    for i, ln in enumerate(lines):
        if not ln.text.strip():
            previous = None
            continue
        if previous is not None:
            joined, gap = continues(lines[previous], ln, pitch, margins, params)
            block_text = "\n".join(lines[k].text for k in blocks[-1])
            if (
                not joined
                and open_reference(block_text)
                and not MARKER_START.match(ln.text)
                and not heading_section(ln.text)
            ):
                joined = True
            gaps_before[i] = gap
            if joined:
                blocks[-1].append(i)
                previous = i
                continue
        else:
            gaps_before[i] = 2.0 if blocks else 0.0
        blocks.append([i])
        previous = i
    units: list[Unit] = []
    current_heading: str | None = None
    for b, members in enumerate(blocks):
        first, last = lines[members[0]], lines[members[-1]]
        start, end = first.start, last.end
        span = text[start:end]
        if len(members) == 1 and heading_section(span):
            current_heading = heading_section(span)
            units.append(Unit(start, end, span, members, b, heading=current_heading))
            continue
        if is_whole_block(span):
            pieces = [0]
        else:
            pieces = [0, *_sentence_cuts(span)]
        for k, rel in enumerate(pieces):
            rel_end = pieces[k + 1] if k + 1 < len(pieces) else len(span)
            piece = span[rel:rel_end]
            lead = len(piece) - len(piece.lstrip())
            piece_stripped = piece.strip()
            if not piece_stripped:
                continue
            u_start = start + rel + lead
            u_end = u_start + len(piece_stripped)
            member_lines = [i for i in members if lines[i].start < u_end and lines[i].end > u_start]
            units.append(
                Unit(u_start, u_end, text[u_start:u_end], member_lines, b, heading=current_heading)
            )
    # intervalo antes de cada unidade (para S)
    for u in units:
        u.features["_gap_before"] = gaps_before.get(u.lines[0], 0.0) if u.lines else 0.0
    return units, lines


# --- Vetor léxico L0 ---------------------------------------------------------------------------


def ngrams(text: str) -> Counter:
    out: Counter = Counter()
    for w in words(fold(text)):
        padded = f" {w} "
        for n in NGRAMS:
            for i in range(len(padded) - n + 1):
                out[zlib.crc32(padded[i : i + n].encode("utf-8")) & (HASH_DIM - 1)] += 1
    return out


def tfidf(text: str, idf: dict[int, float], default_idf: float) -> dict[int, float]:
    vec = {h: (1.0 + math.log(c)) * idf.get(h, default_idf) for h, c in ngrams(text).items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {h: v / norm for h, v in vec.items()}


def cosine(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(h, 0.0) for h, v in a.items())


def build_idf(documents: list[str]) -> tuple[dict[int, float], float]:
    df: Counter = Counter()
    for d in documents:
        df.update(set(ngrams(d)))
    n = len(documents)
    idf = {h: math.log((1 + n) / (1 + c)) + 1.0 for h, c in df.items()}
    return idf, math.log(1 + n) + 1.0


def centroid(vectors: list[dict[int, float]], keep: int = 5000) -> dict[int, float]:
    total: Counter = Counter()
    for v in vectors:
        total.update(v)
    top = dict(sorted(total.items(), key=lambda kv: -kv[1])[:keep])
    norm = math.sqrt(sum(v * v for v in top.values())) or 1.0
    return {h: v / norm for h, v in top.items()}


def blend(
    seed: dict[int, float], user_sum: dict[int, float] | None, n_user: int, kappa: float
) -> dict[int, float]:
    """c = (1 - rho) c_seed + rho c_user, rho = n / (n + kappa)."""
    if not user_sum or n_user <= 0:
        return seed
    rho = n_user / (n_user + kappa)
    user = centroid([user_sum])
    keys = set(seed) | set(user)
    mixed = {h: (1 - rho) * seed.get(h, 0.0) + rho * user.get(h, 0.0) for h in keys}
    top = dict(sorted(mixed.items(), key=lambda kv: -kv[1])[:5000])
    norm = math.sqrt(sum(v * v for v in top.values())) or 1.0
    return {h: v / norm for h, v in top.items()}


# --- Pistas estruturais f ----------------------------------------------------------------------

FEATURES = [
    "ref_quote_frac",
    "ref_quote_line",
    "ref_page",
    "ref_author_year",
    "ref_abnt",
    "ref_marker_start",
    "ref_marker_any",
    "ref_year",
    "ref_url",
    "con_term_sep",
    "con_def_verb",
    "con_e_acute",
    "con_def_early",
    "con_list",
    "con_equals",
    "con_short",
    "sum_marker",
    "sum_topic_verb",
    "sum_first",
    "sum_position",
    "exp_connective",
    "exp_first_person",
    "exp_question",
    "exp_arrow",
    "exp_page_comment",
    "exp_long",
    "shape_log_words",
    "shape_digit",
    "shape_upper",
    "shape_punct",
    "shape_colon",
    "shape_marker",
    "shape_end_period",
    "shape_indent",
    "shape_block_size",
    "shape_conf",
    "shape_conf_missing",
]


def structural_features(
    unit: Unit,
    index: int,
    total: int,
    lines: list[Line],
    block_sizes: Counter,
    cue: CueIndex,
    margins,
) -> dict[str, float]:
    t = unit.text
    f = fold(t)
    toks = words(f)
    n = max(1, len(toks))
    counts = cue.count(toks)
    quoted = sum(len(m.group(1)) for m in QUOTED.finditer(t))
    letters = [c for c in t if c.isalpha()]
    first_tokens = toks[:6]
    out = {
        "ref_quote_frac": quoted / max(1, len(t)),
        "ref_quote_line": float(bool(QUOTE_LINE.match(t))),
        "ref_page": float(len(PAGE.findall(t)) > 0),
        "ref_author_year": float(bool(AUTHOR_YEAR.search(t))),
        "ref_abnt": float(bool(ABNT.match(t) and YEAR.search(t))),
        "ref_marker_start": float(bool(REF_START.match(t))),
        "ref_marker_any": min(3, counts["reference_marker"]) / 3,
        "ref_year": float(bool(YEAR.search(t))),
        "ref_url": float(bool(URL.search(t))),
        "con_term_sep": float(bool(TERM_SEP.match(t))),
        "con_def_verb": min(3, counts["concept_verb"]) / n,
        "con_e_acute": min(2, len(re.findall(r"(?<![\w])(?:é|são)(?![\w])", t.casefold()))) / 2,
        "con_def_early": float(bool(DEF_VERB_EARLY.match(t))),
        "con_list": float(bool(LIST_START.match(t))),
        "con_equals": float("=" in t),
        "con_short": float(n <= 14),
        "sum_marker": float(counts["summary_marker"] > 0),
        "sum_topic_verb": float(
            any(
                w in ("capitulo", "cap", "texto", "livro", "obra", "artigo", "autor", "autora")
                for w in first_tokens
            )
            and counts["summary_verb"] > 0
        ),
        "sum_first": float(index == 0),
        "sum_position": 1.0 - index / max(1, total - 1),
        "exp_connective": min(4, counts["explanation_connective"]) / n,
        "exp_first_person": float(counts["explanation_first_person"] > 0),
        "exp_question": float("?" in t),
        "exp_arrow": float(bool(ARROW_START.match(t))),
        "exp_page_comment": float(bool(PAGE_COMMENT.match(t))),
        "exp_long": float(n >= 18),
        "shape_log_words": math.log1p(n) / 4,
        "shape_digit": sum(c.isdigit() for c in t) / max(1, len(t)),
        "shape_upper": sum(c.isupper() for c in letters) / max(1, len(letters)),
        "shape_punct": sum(c in '.,;:!?()"“”—–-' for c in t) / max(1, len(t)),
        "shape_colon": float(":" in t),
        "shape_marker": float(bool(MARKER_START.match(t))),
        "shape_end_period": float(t.rstrip()[-1:] in (".", "!", "?")),
        "shape_indent": 0.0,
        "shape_block_size": min(6, block_sizes[unit.block]) / 6,
        "shape_conf": 1.0,
        "shape_conf_missing": 1.0,
    }
    boxes = [lines[i].bbox for i in unit.lines if lines[i].bbox]
    if boxes and margins:
        left, right = margins
        out["shape_indent"] = max(0.0, min(1.0, (boxes[0][0] - left) / max(1.0, right - left) * 10))
    confs = [lines[i].confidence for i in unit.lines if lines[i].confidence is not None]
    if confs:
        out["shape_conf"] = sum(confs) / len(confs)
        out["shape_conf_missing"] = 0.0
    return out


# --- Modelo, matriz relacional e decodificação ----------------------------------------------------


def softmax(values: list[float]) -> list[float]:
    m = max(values)
    exps = [math.exp(v - m) for v in values]
    s = sum(exps)
    return [e / s for e in exps]


def logsumexp(values: list[float]) -> float:
    m = max(values)
    if m == NEG_INF:
        return NEG_INF
    return m + math.log(sum(math.exp(v - m) for v in values))


@dataclass
class Model:
    """Pesos e parâmetros exportados pelo treino (``organizer-v1.json``)."""

    feature_names: list[str]
    weights: list[list[float]]  # 4 x d
    bias: list[float]
    params: dict[str, float]
    seed_centroids: dict[str, dict[int, float]]
    idf: dict[int, float]
    default_idf: float

    @classmethod
    def from_json(cls, data: dict) -> Model:
        return cls(
            feature_names=data["feature_names"],
            weights=data["weights"],
            bias=data["bias"],
            params=data["params"],
            seed_centroids={
                k: {int(h): v for h, v in c.items()} for k, c in data["seed_centroids"].items()
            },
            idf={int(h): v for h, v in data["idf"].items()},
            default_idf=data["default_idf"],
        )


def vector(features: dict[str, float], sims: list[float], names: list[str]) -> list[float]:
    values = {**features, **{f"sim_{s}": v for s, v in zip(SECTIONS, sims, strict=False)}}
    return [values.get(name, 0.0) for name in names]


def affinities(xs: list[list[float]], model: Model) -> list[list[float]]:
    beta = model.params.get("beta", 1.0)
    out = []
    for x in xs:
        scores = [
            (sum(w * v for w, v in zip(row, x, strict=False)) + b) / beta
            for row, b in zip(model.weights, model.bias, strict=False)
        ]
        out.append(softmax(scores))
    return out


def coupling(
    units: list[Unit], vecs: list[dict[int, float]], params: dict, pair_sims: dict | None = None
) -> dict[tuple[int, int], float]:
    """S esparsa: proximidade vertical x bloco x similaridade, vizinhos até w posições."""
    w = int(params.get("w", 3))
    sigma = params.get("sigma_g", 1.5)
    eta = params.get("eta", 1.0)
    floor = params.get("sim_floor", 0.05)
    out = {}
    for i in range(len(units)):
        gap = 0.0
        for k in range(i + 1, min(len(units), i + w + 1)):
            gap += (
                units[k].features.get("_gap_before", 0.0)
                if units[k].block != units[k - 1].block
                else 0.0
            )
            raw = (
                pair_sims[(i, k)]
                if pair_sims is not None and (i, k) in pair_sims
                else cosine(vecs[i], vecs[k])
            )
            sim = max(floor, raw)
            value = math.exp(-gap / sigma) * (1 + eta * (units[i].block == units[k].block)) * sim
            out[(i, k)] = out[(k, i)] = value
    return out


def propagate(
    probs: list[list[float]], S: dict[tuple[int, int], float], alpha: float, iterations: int = 10
) -> list[list[float]]:
    if alpha <= 0 or not S:
        return probs
    n = len(probs)
    degree = [0.0] * n
    for (i, _), v in S.items():
        degree[i] += v
    norm = {
        (i, k): v / math.sqrt(degree[i] * degree[k])
        for (i, k), v in S.items()
        if degree[i] > 0 and degree[k] > 0
    }
    neighbours: dict[int, list[tuple[int, float]]] = {}
    for (i, k), v in norm.items():
        neighbours.setdefault(i, []).append((k, v))
    F = [row[:] for row in probs]
    for _ in range(iterations):
        new = []
        for i in range(n):
            acc = [0.0] * 4
            for k, v in neighbours.get(i, ()):
                for j in range(4):
                    acc[j] += v * F[k][j]
            new.append([alpha * acc[j] + (1 - alpha) * probs[i][j] for j in range(4)])
        F = new
    return [[v / s for v in row] if (s := sum(row)) > 0 else probs[i] for i, row in enumerate(F)]


def transition(params: dict) -> tuple[list[list[float]], list[float]]:
    tau, omega = params.get("tau", 1.0), params.get("omega", 0.25)
    order = {(0, 1), (1, 2), (2, 3), (0, 2), (1, 3)}
    T = []
    for a in range(4):
        row = [tau * (a == b) + omega * ((a, b) in order) for b in range(4)]
        z = logsumexp(row)
        T.append([v - z for v in row])
    start = [omega * (j == 0) for j in range(4)]
    z = logsumexp(start)
    return T, [v - z for v in start]


def decode(
    A: list[list[float]],
    S: dict[tuple[int, int], float],
    params: dict,
    use_T: bool = True,
    use_S: bool = True,
):
    """Viterbi exato com custo de troca ponderado por S; forward-backward para as marginais."""
    n = len(A)
    T, start = transition(params) if use_T else ([[0.0] * 4 for _ in range(4)], [0.0] * 4)
    lam = params.get("lambda", 1.0) if use_S else 0.0

    def trans(i: int, a: int, b: int) -> float:
        cost = lam * S.get((i - 1, i), 0.0) if a != b else 0.0
        return T[a][b] - cost

    score = [[start[j] + A[0][j] for j in range(4)]]
    back = []
    for i in range(1, n):
        row, ptr = [], []
        for b in range(4):
            best = max(range(4), key=lambda a: score[-1][a] + trans(i, a, b))
            row.append(score[-1][best] + trans(i, best, b) + A[i][b])
            ptr.append(best)
        score.append(row)
        back.append(ptr)
    path = [max(range(4), key=lambda j: score[-1][j])]
    for ptr in reversed(back):
        path.append(ptr[path[-1]])
    path.reverse()
    # marginais
    fwd = [[start[j] + A[0][j] for j in range(4)]]
    for i in range(1, n):
        fwd.append(
            [logsumexp([fwd[-1][a] + trans(i, a, b) for a in range(4)]) + A[i][b] for b in range(4)]
        )
    bwd = [[0.0] * 4 for _ in range(n)]
    for i in range(n - 2, -1, -1):
        bwd[i] = [
            logsumexp([trans(i + 1, a, b) + A[i + 1][b] + bwd[i + 1][b] for b in range(4)])
            for a in range(4)
        ]
    marginals = []
    for i in range(n):
        row = [fwd[i][j] + bwd[i][j] for j in range(4)]
        z = logsumexp(row)
        marginals.append([math.exp(v - z) if z != NEG_INF else 0.25 for v in row])
    return path, marginals


@dataclass
class Options:
    use_features: bool = True
    use_lexical: bool = True
    use_T: bool = True
    use_S: bool = True
    use_propagation: bool = True
    use_layout: bool = True


class Organizer:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.cue = CueIndex(CUES)

    def centroids(
        self, user: dict[str, tuple[dict[int, float], int]] | None = None
    ) -> dict[str, dict[int, float]]:
        if not user:
            return self.model.seed_centroids
        kappa = self.model.params.get("kappa", 50.0)
        return {
            s: blend(self.model.seed_centroids[s], *(user.get(s) or (None, 0)), kappa)
            for s in SECTIONS
        }

    def analyse(self, text: str, layout=None, options: Options | None = None, centroids=None):
        """Segmenta e calcula vetores; devolve tudo o que a decodificação precisa."""
        options = options or Options()
        units, lines = segment(text, layout if options.use_layout else None, self.model.params)
        margins = _margins(lines)
        block_sizes = Counter(u.block for u in units)
        cents = centroids or self.model.seed_centroids
        vecs, xs = [], []
        for i, u in enumerate(units):
            feats = structural_features(u, i, len(units), lines, block_sizes, self.cue, margins)
            vec = tfidf(u.text, self.model.idf, self.model.default_idf)
            sims = [cosine(vec, cents[s]) for s in SECTIONS]
            if not options.use_features:
                feats = dict.fromkeys(feats, 0.0)
            if not options.use_lexical:
                sims = [0.0] * 4
            u.features.update(feats)
            vecs.append(vec)
            xs.append(vector(feats, sims, self.model.feature_names))
        return units, lines, vecs, xs

    def organize(
        self, text: str, layout=None, options: Options | None = None, centroids=None
    ) -> dict:
        options = options or Options()
        units, _lines, vecs, xs = self.analyse(text, layout, options, centroids)
        if not units:
            return {
                "sections": dict.fromkeys(SECTIONS, ""),
                "segments": [],
                "explicit_headings": False,
            }
        return self.decide(units, vecs, xs, options)

    def decide(
        self,
        units,
        vecs,
        xs,
        options: Options,
        params: dict | None = None,
        probs=None,
        pair_sims=None,
    ) -> dict:
        params = {**self.model.params, **(params or {})}
        probs = probs if probs is not None else affinities(xs, self.model)
        S = (
            coupling(units, vecs, params, pair_sims)
            if (options.use_S or options.use_propagation)
            else {}
        )
        if options.use_propagation:
            probs = propagate(probs, S, params.get("alpha", 0.5))
        A = [[math.log(max(p, 1e-12)) for p in row] for row in probs]
        explicit = any(u.heading for u in units)
        for i, u in enumerate(units):
            if u.heading:
                j = SECTIONS.index(u.heading)
                A[i] = [0.0 if k == j else NEG_INF for k in range(4)]
        if options.use_T or options.use_S:
            path, marginals = decode(A, S, params, use_T=options.use_T, use_S=options.use_S)
        else:
            path = [max(range(4), key=lambda j: row[j]) for row in A]
            marginals = [[math.exp(v) if v != NEG_INF else 0.0 for v in row] for row in A]
        segments, sections = [], {s: [] for s in SECTIONS}
        review_margin = params.get("review_margin", 0.3)
        for i, (u, j) in enumerate(zip(units, path, strict=False)):
            ranked = sorted(marginals[i], reverse=True)
            margin = ranked[0] - ranked[1]
            segments.append(
                {
                    "index": i,
                    "start": u.start,
                    "end": u.end,
                    "section": SECTIONS[j],
                    "confidence": round(marginals[i][j], 4),
                    "margin": round(margin, 4),
                    "review": margin < review_margin,
                }
            )
            sections[SECTIONS[j]].append(u.text)
        return {
            "sections": {s: "\n".join(v) for s, v in sections.items()},
            "segments": segments,
            "explicit_headings": explicit,
            "marginals": marginals,
        }
