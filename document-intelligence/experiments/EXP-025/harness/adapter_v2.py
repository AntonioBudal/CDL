# ruff: noqa: N806 — W e b seguem a notação da spec do EXP-024
"""EXP-025, F05: adaptador online enxuto sobre o ``organizer-v2`` (referência que o produto copia).

Só três peças do motor do EXP-024, com os mesmos parâmetros congelados (``thresholds.json``):

- **E1:** pesos online sobre o diff de revisão, somados aos do v2, com âncora L2 e projeção;
- **E2:** centróides do leitor e do livro (colunas ``usim_*`` e ``bsim_*``) e a forma de linha de
  referência aprendida (``ref_shape_user``);
- **gating:** página revertida, ou com pouca retenção e sem correções, não gera atualização.

Ficam de fora ``T_user``, *replay*, portão-sombra e pós-correção da leitura. Com o estado vazio, a
sugestão é idêntica à do v2: as 9 colunas novas entram com peso 0 e a decisão é o mesmo ``decide``.

A **guarda** (decisão C-Q3 da feature 091): antes de aprender com um registro, mede quantos
trechos o adaptador e o v2 teriam acertado contra as seções salvas; o adaptador só é usado se,
nos últimos 20 registros medidos (pelo menos 10), acertou tanto quanto o v2.

Entrada do aprendizado: o registro ``leitorum-feedback/1`` do Leitorum (``organizer`` com ``text``,
``segments``, ``outcome``, ``saved_sections`` e ``lines``; ``reading`` com ``kinds``). Só biblioteca
padrão; o estado não guarda texto.
"""

from __future__ import annotations

import math

import adapter_deps as dep

SECTIONS = ("summary", "explanation", "concepts", "references")
EXTRA_FEATURES = [
    "ref_shape_user",
    *[f"usim_{s}" for s in SECTIONS],
    *[f"bsim_{s}" for s in SECTIONS],
]
CENTROID_KEEP = 5000
GUARD_WINDOW = 20
GUARD_MIN = 10

# EXP-024: ``adaptive_organizer.DEFAULTS`` com ``artifacts/thresholds.json`` por cima
# (só o que é usado).
PARAMS = {
    "eta0": 0.1,
    "t0": 50.0,
    "mu": 0.02,
    "delta_max": 4.0,
    "eta_beta": 0.02,
    "beta_range": 1.5,
    "scope_min_units": 3.0,
    "omega_keep": 1.0,
    "keep_blind": 0.1,
    "rating_none": 0.5,
    "omega_moved": 1.0,
    "omega_edited": 0.5,
    "omega_click": 1.0,
    "unreviewed_factor": 0.05,
    "retention_min": 0.3,
    "shape_alpha": 1.0,
    "shape_scale": 3.0,
}


class AdapterV2:
    """Sugestões e aprendizado sobre o v2; o estado (um por usuário) fica com quem chama."""

    def __init__(self, base, anchor_sha256: str) -> None:
        self.base = base  # OrganizerV2 do artefato
        self.model = base.model
        self.anchor_sha256 = anchor_sha256
        self.names = list(self.model.feature_names) + EXTRA_FEATURES
        self.W0 = [list(row) + [0.0] * len(EXTRA_FEATURES) for row in self.model.weights]
        self.b0 = list(self.model.bias)
        self.beta0 = self.model.params.get("beta", 1.0)

    # estado ------------------------------------------------------------------------------------

    def new_state(self, user_id: str) -> dict:
        state = dep.new_state(user_id, self.anchor_sha256, 4, len(self.names))
        state["guard"] = {"adapter": [], "static": []}
        state["reviewed"] = 0
        return state

    def weights(self, state: dict | None) -> tuple[list[list[float]], list[float], float]:
        if state is None:
            return self.W0, self.b0, self.beta0
        o = state["organizer"]
        W = [
            [w + d for w, d in zip(r0, rd, strict=False)]
            for r0, rd in zip(self.W0, o["delta_W"], strict=False)
        ]
        b = [x + d for x, d in zip(self.b0, o["delta_b"], strict=False)]
        return W, b, self.beta0 * math.exp(o["log_beta_delta"])

    def guard_allows(self, state: dict | None) -> bool:
        if state is None:
            return False
        adapter = state["guard"]["adapter"][-GUARD_WINDOW:]
        static = state["guard"]["static"][-GUARD_WINDOW:]
        if len(adapter) < GUARD_MIN:
            return False
        return sum(adapter) >= sum(static)

    # vetor ---------------------------------------------------------------------------------------

    def _scope(self, scope: dict) -> dict[str, dict[int, float]]:
        minimum = PARAMS["scope_min_units"]
        return {
            s: dep.normalized(dep.top(scope["sums"][s], CENTROID_KEEP))
            if scope["counts"][s] >= minimum
            else {}
            for s in SECTIONS
        }

    def scope_centroids(self, state: dict | None, book_id: str | None):
        empty = {s: {} for s in SECTIONS}
        if state is None:
            return empty, empty
        o = state["organizer"]
        book = o["books"].get(book_id) if book_id is not None else None
        return self._scope(o["user"]), self._scope(book) if book else empty

    def shape_score(self, state: dict | None, book_id: str | None, text: str) -> float:
        if state is None:
            return 0.0
        shapes = state["organizer"]["ref_shapes"]
        tables = [shapes["user"]]
        if book_id is not None and book_id in shapes["books"]:
            tables.append(shapes["books"][book_id])
        sig = dep.line_shape(text)
        c_ref = c_oth = tot_ref = tot_oth = 0.0
        for table in tables:
            r, o = table.get(sig, (0.0, 0.0))
            c_ref, c_oth = c_ref + r, c_oth + o
            tr, to = table.get("__total__", (0.0, 0.0))
            tot_ref, tot_oth = tot_ref + tr, tot_oth + to
        if c_ref + c_oth == 0:
            return 0.0
        a = PARAMS["shape_alpha"]
        prior = (tot_ref + 1) / (tot_ref + tot_oth + 2)
        lo = math.log((c_ref + a * prior) / (c_oth + a * (1 - prior))) - math.log(
            prior / (1 - prior)
        )
        return math.tanh(lo / PARAMS["shape_scale"])

    def analyse(self, state: dict | None, text: str, lines, book_id: str | None):
        units, _lines, vecs, xs = self.base.analyse(text, lines or None, dep.Options())
        user_c, book_c = self.scope_centroids(state, book_id)
        out = []
        for x, u, v in zip(xs, units, vecs, strict=False):
            usims = [dep.cosine(v, user_c[s]) if user_c[s] else 0.0 for s in SECTIONS]
            bsims = [dep.cosine(v, book_c[s]) if book_c[s] else 0.0 for s in SECTIONS]
            out.append(x + [self.shape_score(state, book_id, u.text)] + usims + bsims)
        return units, vecs, out

    def probabilities(self, xs, weights):
        W, b, beta = weights
        return [
            dep.softmax(
                [
                    (sum(w * v for w, v in zip(row, x, strict=False)) + bb) / beta
                    for row, bb in zip(W, b, strict=False)
                ]
            )
            for x in xs
        ]

    # sugestão ------------------------------------------------------------------------------------

    def organize(self, state: dict | None, text: str, lines=None, book_id: str | None = None):
        """Sugestão com o estado do usuário; ``state=None`` é o v2 puro."""
        if state is None:
            return self.base.organize(text, lines or None)
        units, vecs, xs = self.analyse(state, text, lines, book_id)
        if not units:
            return {
                "sections": dict.fromkeys(SECTIONS, ""),
                "segments": [],
                "explicit_headings": False,
            }
        probs = self.probabilities(xs, self.weights(state))
        return self.base.decide(units, vecs, xs, dep.Options(), probs=probs)

    # aprendizado ---------------------------------------------------------------------------------

    def _step(self, state: dict, x: list[float], y: int, omega: float, lr: float) -> None:
        o = state["organizer"]
        W, b, beta = self.weights(state)
        z = [
            sum(w * v for w, v in zip(row, x, strict=False)) + bb
            for row, bb in zip(W, b, strict=False)
        ]
        p = dep.softmax([v / beta for v in z])
        mu = PARAMS["mu"]
        for c in range(4):
            g = omega * (p[c] - (c == y)) / beta
            row = o["delta_W"][c]
            for j, v in enumerate(x):
                row[j] -= lr * (g * v + mu * row[j])
            o["delta_b"][c] -= lr * (g + mu * o["delta_b"][c])
        g_beta = omega * (z[y] - sum(pc * zc for pc, zc in zip(p, z, strict=False))) / beta
        limit = math.log(PARAMS["beta_range"])
        o["log_beta_delta"] = max(
            -limit, min(limit, o["log_beta_delta"] - PARAMS["eta_beta"] * g_beta)
        )

    def _guard_measure(self, state, text, lines, book_id, outcomes) -> None:
        finals = {out.index: out.final for out in outcomes if out.final is not None}
        if not finals:
            return
        row = {}
        for name, current in (("adapter", state), ("static", None)):
            result = self.organize(current, text, lines, book_id)
            sections = {s["index"]: s["section"] for s in result["segments"]}
            hits = sum(sections.get(i) == final for i, final in finals.items())
            row[name] = round(hits / len(finals), 4)
        for name in ("adapter", "static"):
            history = state["guard"][name]
            history.append(row[name])
            del history[: max(0, len(history) - GUARD_WINDOW)]

    def learn(self, state: dict, document: dict, book_id: str | None = None) -> str:
        """Aprende com um registro ``leitorum-feedback/1``; devolve o código do que aconteceu."""
        organizer = document.get("organizer")
        if not organizer:
            return "no_organizer"
        o = state["organizer"]
        reverted = organizer["outcome"] == "reverted"
        o["behaviour"]["pages"] += 1
        if reverted:
            o["behaviour"]["reverted"] += 1
            state["updates"] += 1
            return "gated"
        state["reviewed"] += 1
        text, segments = organizer["text"], organizer["segments"]
        saved = organizer["saved_sections"]
        lines = organizer.get("lines")
        outcomes = dep.align_units(text, segments, saved)
        moved = sum(out.outcome == "moved" for out in outcomes)
        edited = sum(out.outcome == "edited" for out in outcomes)
        total = sum(s["end"] - s["start"] for s in segments) or 1
        kept_chars = sum(
            s["end"] - s["start"]
            for s, out in zip(segments, outcomes, strict=False)
            if out.outcome == "kept"
        )
        kinds = (document.get("reading") or {}).get("kinds")
        blind = (
            moved == 0
            and edited == 0
            and kinds is not None
            and kinds.get("same", 0) > 0
            and sum(v for k, v in kinds.items() if k != "same") == 0
        )
        if blind:
            o["behaviour"]["blind"] += 1
        pw = dep.page_weights(
            reverted=False,
            rating=None,
            corrections=moved + edited,
            blind=blind,
            retention=kept_chars / total,
            params=PARAMS,
        )
        if pw.gated:
            state["updates"] += 1
            return "gated"
        units, vecs, xs = self.analyse(state, text, lines, book_id)
        if [(u.start, u.end) for u in units] != [(s["start"], s["end"]) for s in segments]:
            state["updates"] += 1
            return "misaligned"
        self._guard_measure(state, text, lines, book_id, outcomes)
        book = dep.book_scope(state, book_id) if book_id is not None else None
        labels, weights = [], []
        for seg, out in zip(segments, outcomes, strict=False):
            if out.outcome == "deleted" or out.final is None:
                labels.append(None)
                weights.append(0.0)
                continue
            labels.append(SECTIONS.index(out.final))
            keep = pw.keep if seg.get("review") else pw.keep * PARAMS["unreviewed_factor"]
            weights.append({"kept": keep, "moved": pw.moved, "edited": pw.edited}[out.outcome])
        # E2: centróides e formas de linha (aditivos, ponderados)
        for u, vec, label, w in zip(units, vecs, labels, weights, strict=False):
            if w <= 0 or label is None:
                continue
            section = SECTIONS[label]
            dep.add_vector(o["user"], section, vec, w, dep.USER_KEEP)
            if book is not None:
                dep.add_vector(book, section, vec, w, dep.BOOK_KEEP)
            sig = dep.line_shape(u.text)
            tables = [o["ref_shapes"]["user"]]
            if book_id is not None:
                tables.append(o["ref_shapes"]["books"].setdefault(book_id, {}))
            for table in tables:
                for key in (sig, "__total__"):
                    r, other = table.get(key, (0.0, 0.0))
                    table[key] = (r + w, other) if section == "references" else (r, other + w)
        # E1: pesos e temperatura, com âncora L2 e projeção
        for x, label, w in zip(xs, labels, weights, strict=False):
            if w <= 0 or label is None:
                continue
            lr = PARAMS["eta0"] / math.sqrt(1 + o["steps"] / PARAMS["t0"])
            self._step(state, x, label, w, lr)
            o["steps"] += 1
        dep.project(o["delta_W"], o["delta_b"], PARAMS["delta_max"])
        state["updates"] += 1
        return "learned"
