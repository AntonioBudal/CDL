"""Léxico de português para a hipótese H3: quantas palavras "quase certas" (distância 1–2) um
dicionário resolveria sozinho. Usa o léxico do EXP-011 (``wordfreq`` pt, dados CC-BY-SA 4.0; só
experimento) quando existir em ``processed/exp-011/lexicon-pt.json``; sem ele, os contadores ficam
zerados e ``describe()`` diz que faltou.

Para cada par (ref, hyp, d ≤ 2):
- ``lex_hyp_known``: a palavra lida existe no léxico → um dicionário nem veria o erro;
- ``lex_ref_unknown``: a palavra certa não está no léxico → um dicionário não a proporia;
- ``lex_fix_d1`` / ``lex_fix_d2``: a palavra certa é o candidato mais frequente à menor distância;
- ``lex_ambiguous``: a certa está entre os candidatos, mas não é a escolhida (precisa de contexto).
Índice de deleções (SymSpell): 1 deleção do lado do léxico, até 2 do lado da palavra lida.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations

from align import levenshtein
from paths import DATA_ROOT

LEXICON_FILE = DATA_ROOT / "processed" / "exp-011" / "lexicon-pt.json"


def deletes(word: str, depth: int) -> set[str]:
    out = set()
    for count in range(1, depth + 1):
        if count >= len(word):
            break
        for positions in combinations(range(len(word)), count):
            out.add("".join(c for i, c in enumerate(word) if i not in positions))
    return out


class Lexicon:
    def __init__(self, words: list[str], source: str = "", license_text: str = "") -> None:
        self.rank = {w: i for i, w in enumerate(words)}  # menor índice = mais frequente
        self.source, self.license = source, license_text
        self.index: dict[str, list[str]] = defaultdict(list)
        for word in words:
            self.index[word].append(word)
            for key in deletes(word, 1):
                self.index[key].append(word)

    @classmethod
    def load(cls, size: int = 50_000) -> Lexicon:
        if not LEXICON_FILE.is_file():
            return cls([])
        data = json.loads(LEXICON_FILE.read_text(encoding="utf-8"))
        words = [w if isinstance(w, str) else w[0] for w in data["words"][:size]]  # [palavra, freq]
        return cls(words, data.get("source", ""), data.get("license", ""))

    @property
    def available(self) -> bool:
        return bool(self.rank)

    def describe(self) -> dict:
        return {
            "available": self.available,
            "size": len(self.rank),
            "source": self.source,
            "license": self.license,
        }

    def candidates(self, word: str, max_distance: int) -> list[tuple[int, int, str]]:
        """(distância, posição no léxico, palavra) dos candidatos a até ``max_distance``."""
        keys = {word, *deletes(word, max_distance)}
        seen = set()
        out = []
        for key in keys:
            for candidate in self.index.get(key, ()):
                if candidate in seen:
                    continue
                seen.add(candidate)
                distance = levenshtein(word, candidate)
                if distance <= max_distance:
                    out.append((distance, self.rank[candidate], candidate))
        return sorted(out)

    def judge(self, pairs: list[tuple[str, str, int]]) -> Counter:
        out: Counter = Counter()
        if not self.available:
            return out
        for ref, hyp, distance in pairs:
            if distance > 2:
                continue
            ref_l, hyp_l = ref.lower(), hyp.lower()
            if hyp_l in self.rank:
                out["lex_hyp_known"] += 1
                continue
            if ref_l not in self.rank:
                out["lex_ref_unknown"] += 1
                continue
            ranked = self.candidates(hyp_l, distance)
            if ranked and ranked[0][2] == ref_l:
                out[f"lex_fix_d{distance}"] += 1
            else:
                out["lex_ambiguous"] += 1
        return out
