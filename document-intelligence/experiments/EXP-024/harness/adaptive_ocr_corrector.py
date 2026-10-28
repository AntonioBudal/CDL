"""EXP-024 (E2, E5, E6): pós-correção pessoal da leitura e curadoria de pares para o ajuste fino.

- **Léxico de 1ª parte:** palavras dos textos que o próprio leitor salvou, por livro e no acervo,
  mais uma semente MIT (protótipos e listas de pistas do EXP-023). Cada palavra guarda as grafias
  vistas sob a mesma forma sem acento, o que permite restaurar acentos.
- **Confusões pessoais:** operações de 1–2 caracteres (lido → certo) tiradas das correções de
  leitura, com suporte mínimo e prior de Dirichlet no modelo global do EXP-015.
- **Correção por canal ruidoso:** ``log P_lex(c) + log P(lido | c)``; troca só com margem θ.
- **Limiar de ``low_confidence``:** logístico de P(linha editada | confiança), com teto de 25 %
  marcadas.
- **Curadoria:** pares (linha, texto revisado) só de correções de leitura confiáveis, cujas palavras
  todas já eram conhecidas no léxico antes da página (um erro que sobrou costuma ser uma
  não-palavra).

Só biblioteca padrão. Nada aqui grava ou registra texto.
"""

from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP023 = HERE.parent.parent / "EXP-023"
for path in (HERE, EXP023 / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import diff_signal  # noqa: E402

DI = HERE.parents[2]
NOISE_MODEL = DI / "dataset" / "processed" / "exp-023" / "noise-model.json"
PROTOTYPES = EXP023 / "data" / "semente" / "prototipos.json"
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

DEFAULTS = {
    "theta": 2.0,  # margem (log) para trocar uma palavra
    "candidate_min": 2.0,  # contagem ponderada mínima de um candidato do léxico
    "protect_min": 3.0,  # grafia lida já vista tantas vezes, e majoritária, fica protegida
    "weight_book": 3.0,
    "weight_user": 1.0,
    "weight_seed": 0.5,
    "alpha_channel": 20.0,  # força do prior global nas confusões
    "support_min": 2,  # confusão pessoal só vale com essa contagem, em >= 2 linhas
    "curate_max_distance": 0.3,
    "curate_min_length": 5,
    "curate_known_min": 2.0,  # toda palavra da linha curada já vista tantas vezes antes da página
    "low_conf_max_share": 0.25,
    "low_conf_lr": 0.5,
    "use_lexicon": True,
    "use_confusions": True,
    "use_book": True,
    "use_filter": True,
}


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def deletes(word: str, depth: int) -> set[str]:
    out, frontier = {word}, {word}
    for _ in range(depth):
        frontier = {w[:i] + w[i + 1 :] for w in frontier for i in range(len(w))}
        out |= frontier
    return out


def recase(model: str, word: str) -> str:
    if model.isupper() and len(model) > 1:
        return word.upper()
    if model[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


class AdaptiveReader:
    def __init__(self, state_for, params: dict | None = None) -> None:
        self.state_for = state_for
        self.params = {**DEFAULTS, **(params or {})}
        self.noise = json.loads(NOISE_MODEL.read_text(encoding="utf-8"))
        self.seed = self._seed_lexicon()
        self._index_cache: dict = {}

    # léxico ---------------------------------------------------------------------------------------

    @staticmethod
    def _seed_lexicon() -> dict[str, dict[str, float]]:
        import organizer as org

        texts = []
        data = json.loads(PROTOTYPES.read_text(encoding="utf-8"))
        for section in ("summary", "explanation", "concepts", "references"):
            texts.extend(data[section])
        for words in org.CUES.values():
            texts.extend(words)
        lexicon: dict[str, dict[str, float]] = {}
        for text in texts:
            for word in WORD.findall(text):
                surface = word.lower()
                key = fold(surface)
                lexicon.setdefault(key, {})
                lexicon[key][surface] = lexicon[key].get(surface, 0.0) + 1.0
        return lexicon

    def _scopes(self, state: dict, book_id: str | None) -> list[tuple[dict, float]]:
        p = self.params
        lex = state["reading"]["lexicon"]
        scopes = [(self.seed, p["weight_seed"]), (lex["user"], p["weight_user"])]
        if p["use_book"] and book_id and book_id in lex["books"]:
            scopes.append((lex["books"][book_id], p["weight_book"]))
        return scopes

    def _surfaces(self, scopes, key: str) -> dict[str, float]:
        out: dict[str, float] = {}
        for table, weight in scopes:
            for surface, count in table.get(key, {}).items():
                out[surface] = out.get(surface, 0.0) + weight * count
        return out

    def _index(self, state: dict, book_id: str | None) -> dict[str, set[str]]:
        """Índice de apagamentos (distância ≤ 2) das formas sem acento do léxico; em memória."""
        lex = state["reading"]["lexicon"]
        sizes = (len(lex["user"]), len(lex["books"].get(book_id, {})) if book_id else 0)
        key = (state["user_id"], book_id, sizes)
        if key in self._index_cache:
            return self._index_cache[key]
        index: dict[str, set[str]] = {}
        for table, _w in self._scopes(state, book_id):
            for word in table:
                for d in deletes(word, 2 if len(word) >= 6 else 1):
                    index.setdefault(d, set()).add(word)
        if len(self._index_cache) > 64:
            self._index_cache.clear()
        self._index_cache[key] = index
        return index

    # canal ruidoso --------------------------------------------------------------------------------

    def _p_global(self, read: str, true: str) -> float:
        n = self.noise
        if len(read) == 1 and len(true) == 1:
            targets = n["substitute_to"].get(true, {})
            total = sum(targets.values()) or 1.0
            return max(1e-5, n["p_substitute"].get(true, 0.0) * targets.get(read, 0.0) / total)
        if read == "" and len(true) == 1:
            return max(1e-5, n["p_delete"].get(true, 0.0))
        if true == "" and len(read) == 1:
            total = sum(n["insert_chars"].values()) or 1.0
            return max(1e-6, n["p_insert"] * n["insert_chars"].get(read, 0.0) / total)
        return 1e-6

    def channel(self, state: dict, read: str, true: str) -> float:
        """log P(lido | certo), por operação de caractere."""
        if read == true:
            return sum(
                math.log(
                    max(
                        0.5,
                        1
                        - self.noise["p_substitute"].get(c, 0.0)
                        - self.noise["p_delete"].get(c, 0.0),
                    )
                )
                for c in true
            )
        _dist, ops = diff_signal.levenshtein_ops(read, true)
        matched = len(true) - sum(len(t) for _r, t in ops)
        logp = matched * math.log(0.9)
        if sum(len(r) + len(t) for r, t in ops) < max(1, abs(len(read) - len(true))):
            return -50.0  # trecho longo diferente: não é erro de leitura
        conf = state["reading"]["confusions"] if self.params["use_confusions"] else {}
        totals = state["reading"].get("char_totals", {})
        alpha = self.params["alpha_channel"]
        for r, t in ops:
            count, lines = conf.get(f"{r}>{t}", (0, 0))
            if count < self.params["support_min"] or lines < 2:
                count = 0
            if count == 0 and len(r) == len(t) == 2:
                # duas trocas vizinhas sem confusão pessoal: soma as trocas de 1 caractere
                pieces = [(r[0], t[0]), (r[1], t[1])]
            else:
                pieces = [(r, t)]
            for pr, pt in pieces:
                prior = self._p_global(pr, pt)
                c = count if (pr, pt) == (r, t) else 0
                denominator = totals.get(pt[:1], 0) if pt else sum(totals.values())
                logp += math.log((c + alpha * prior) / (denominator + alpha))
        return logp

    # correção -------------------------------------------------------------------------------------

    def _context(self, state: dict, book_id: str | None) -> dict:
        scopes = self._scopes(state, book_id)
        total = sum(w * sum(sum(v.values()) for v in table.values()) for table, w in scopes) or 1.0
        return {"scopes": scopes, "total": total, "index": self._index(state, book_id)}

    def correct_word(
        self, state: dict, book_id: str | None, word: str, ctx: dict | None = None
    ) -> str:
        p = self.params
        key = fold(word)
        if len(key) < 3 or not p["use_lexicon"]:
            return word
        ctx = ctx or self._context(state, book_id)
        scopes, total, index = ctx["scopes"], ctx["total"], ctx["index"]
        own = self._surfaces(scopes, key)
        lower = word.lower()
        if own and own.get(lower, 0.0) >= p["protect_min"] and own[lower] == max(own.values()):
            return word
        candidates: set[str] = set()
        for d in deletes(key, 2 if len(key) >= 6 else 1):
            candidates |= index.get(d, set())
        keep_count = own.get(lower, 0.0)
        best, best_score = (
            word,
            math.log((keep_count + 0.1) / total) + self.channel(state, lower, lower),
        )
        keep_score = best_score
        for cand_key in candidates:
            surfaces = self._surfaces(scopes, cand_key)
            if not surfaces:
                continue
            surface, count = max(surfaces.items(), key=lambda kv: (kv[1], kv[0]))
            if count < p["candidate_min"] or surface == lower:
                continue
            score = math.log((count + 0.1) / total) + self.channel(state, lower, surface)
            if score > best_score:
                best, best_score = surface, score
        if best != word and best_score - keep_score > p["theta"]:
            return recase(word, best)
        return word

    def correct_line(self, user_id: str, book_id: str | None, text: str) -> str:
        state = self.state_for(user_id)
        ctx = self._context(state, book_id)
        return WORD.sub(lambda m: self.correct_word(state, book_id, m.group(0), ctx), text)

    def correct_lines(self, user_id: str, book_id: str | None, lines: list[str]) -> list[str]:
        state = self.state_for(user_id)
        ctx = self._context(state, book_id)
        return [
            WORD.sub(lambda m: self.correct_word(state, book_id, m.group(0), ctx), line)
            for line in lines
        ]

    # aprendizado ----------------------------------------------------------------------------------

    def learn(self, feedback: dict, gated: bool = False) -> dict:
        """Léxico, confusões e limiar a partir de uma página salva; devolve os pares curados."""
        state = self.state_for(feedback["user_id"])
        reading = state["reading"]
        reading.setdefault("char_totals", {})
        book_id = feedback.get("book_id")
        source = feedback["reading"]["source_lines"]
        edits = diff_signal.align_reading(source, feedback["saved"])
        any_edit = any(e.kind != "same" for e in edits)
        report = {"edits": len(edits), "ocr_lines": 0, "curated": [], "gated": gated}
        if gated or not any_edit:
            # página rejeitada, ou salva sem nenhuma correção: o texto pode ter erros de leitura
            report["gated"] = True
            return report
        # curadoria para o ajuste fino em lote (EXP-018), com o léxico de ANTES desta página
        p = self.params
        ctx = self._context(state, book_id)
        for edit in edits:
            if edit.kind != "ocr" or edit.distance > p["curate_max_distance"]:
                continue
            if len(edit.revised) < p["curate_min_length"]:
                continue
            words = [w.lower() for w in WORD.findall(edit.revised) if len(w) >= 3]
            known = all(
                self._surfaces(ctx["scopes"], fold(w)).get(w, 0.0) >= p["curate_known_min"]
                for w in words
            )
            if words and known:
                report["curated"].append(
                    {"page_id": feedback["page_id"], "line": edit.line, "text": edit.revised}
                )
        # léxico: palavras do texto salvo, nas linhas revisadas ou intocadas
        kinds_ok = (
            ("ocr", "same")
            if self.params["use_filter"]
            else ("ocr", "same", "ambiguous", "rewrite")
        )
        lex = reading["lexicon"]
        tables = [lex["user"]]
        if book_id:
            tables.append(lex["books"].setdefault(book_id, {}))
        for edit in edits:
            if edit.kind not in kinds_ok:
                continue
            for word in WORD.findall(edit.revised):
                surface = word.lower()
                key = fold(surface)
                for table in tables:
                    table.setdefault(key, {})
                    table[key][surface] = table[key].get(surface, 0.0) + 1.0
            for ch in edit.revised:
                reading["char_totals"][ch] = reading["char_totals"].get(ch, 0) + 1
        # confusões pessoais: só correções de leitura
        for edit in edits:
            if edit.kind != "ocr" and self.params["use_filter"]:
                continue
            report["ocr_lines"] += edit.kind == "ocr"
            seen = set()
            ops = (
                edit.ops
                if edit.kind == "ocr"
                else diff_signal.levenshtein_ops(edit.read, edit.revised)[1]
            )
            for r, t in ops:
                name = f"{r}>{t}"
                count, lines = reading["confusions"].get(name, (0, 0))
                reading["confusions"][name] = (count + 1, lines + (name not in seen))
                seen.add(name)
        # limiar de baixa confiança
        confidences = feedback["reading"].get("line_confidence") or []
        edited_lines = {e.line for e in edits if e.kind != "same"}
        lc = reading["low_confidence"]
        for k, conf in enumerate(confidences):
            y = 1.0 if k in edited_lines else 0.0
            z = lc["a"] + lc["b"] * conf
            prob = 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))
            lr = self.params["low_conf_lr"] / math.sqrt(1 + lc["n"] / 50)
            lc["a"] -= lr * (prob - y)
            lc["b"] -= lr * (prob - y) * conf
            lc["n"] += 1
            lc["hist"][min(19, int(conf * 20))] += 1
        lc["threshold"] = self.threshold(state)
        return report

    def threshold(self, state: dict) -> float | None:
        lc = state["reading"]["low_confidence"]
        if lc["n"] < 30 or lc["b"] >= 0:
            return None
        logistic = -lc["a"] / lc["b"]
        total, acc, cap = sum(lc["hist"]), 0, 1.0
        for k, count in enumerate(lc["hist"]):
            if acc + count > self.params["low_conf_max_share"] * total:
                cap = k / 20
                break
            acc += count
        return round(max(0.3, min(0.95, logistic, cap)), 4)
