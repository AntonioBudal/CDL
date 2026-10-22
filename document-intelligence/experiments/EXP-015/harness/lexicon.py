"""Correção lexical de texto lido em português, sem modelo.

Para cada palavra (pontuação de borda e caixa preservadas):

1. palavra no léxico → mantém, salvo se ``accent_ratio`` estiver ligado e a forma acentuada da
   mesma palavra for pelo menos ``accent_ratio`` vezes mais frequente (o léxico, vindo de texto da
   internet, tem formas sem acento como "nao");
2. a mesma palavra sem acentos coincide com uma palavra do léxico → forma acentuada mais frequente;
3. senão, candidatos a distância de edição ≤ ``max_distance`` → o mais frequente de menor distância;
   sem candidato, mantém.

Candidatos vêm de um índice de deleções (estilo SymSpell): até 1 deleção no léxico e até
``max_distance`` na palavra lida; a distância verdadeira é conferida depois. Com
``max_distance = 2`` o índice não acha os pares que exigem duas deleções do lado do léxico
(aproximação declarada, para caber em memória).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from itertools import combinations

from leitorum_di.metrics.base import levenshtein_distance

TOKEN = re.compile(r"^(\W*)(.*?)(\W*)$", re.UNICODE)
SPACES = re.compile(r"(\s+)")


@dataclass(frozen=True)
class LexiconParams:
    size: int = 50_000
    max_distance: int = 1
    min_length: int = 3
    accent_ratio: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def strip_accents(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word)
    return unicodedata.normalize(
        "NFC", "".join(c for c in decomposed if not unicodedata.combining(c))
    )


def recase(word: str, model: str) -> str:
    """Aplica a caixa de ``model`` a ``word``."""
    if len(model) > 1 and model.isupper():
        return word.upper()
    if model[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def _deletes(word: str, depth: int) -> set[str]:
    out = set()
    for count in range(1, depth + 1):
        if count >= len(word):
            break
        for positions in combinations(range(len(word)), count):
            out.add("".join(c for i, c in enumerate(word) if i not in positions))
    return out


class Corrector:
    def __init__(self, words: list[list], params: LexiconParams) -> None:
        self.params = params
        self.freq: dict[str, float] = {}
        for word, frequency in words[: params.size]:
            word = unicodedata.normalize("NFC", word)
            if word.isalpha() and word not in self.freq:
                self.freq[word] = float(frequency)
        self.by_stripped: dict[str, str] = {}
        for word, frequency in self.freq.items():
            key = strip_accents(word)
            best = self.by_stripped.get(key)
            if best is None or frequency > self.freq[best]:
                self.by_stripped[key] = word
        self.index: dict[str, list[str]] = {}
        if params.max_distance >= 1:
            for word in self.freq:
                for variant in {word} | _deletes(word, 1):
                    self.index.setdefault(variant, []).append(word)

    def correct_word(self, token: str) -> str:
        low = token.lower()
        if not low.isalpha() or len(low) < self.params.min_length:
            return token
        accented = self.by_stripped.get(strip_accents(low))
        if low in self.freq:
            ratio = self.params.accent_ratio
            if ratio and accented and accented != low:
                if self.freq[accented] >= ratio * self.freq[low]:
                    return recase(accented, token)
            return token
        if accented is not None:
            return recase(accented, token)
        if self.params.max_distance == 0:
            return token
        candidates: set[str] = set()
        for variant in {low} | _deletes(low, self.params.max_distance):
            candidates.update(self.index.get(variant, ()))
        best = None
        for word in candidates:
            distance = levenshtein_distance(low, word)
            if distance <= self.params.max_distance:
                key = (distance, -self.freq[word])
                if best is None or key < best[0]:
                    best = (key, word)
        return recase(best[1], token) if best else token

    def correct_line(self, text: str) -> str:
        out = []
        for part in SPACES.split(text):
            if not part or part.isspace():
                out.append(part)
                continue
            lead, core, tail = TOKEN.match(part).groups()
            out.append(lead + (self.correct_word(core) if core else "") + tail)
        return "".join(out)
