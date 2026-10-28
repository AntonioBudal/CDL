# ruff: noqa: N803, N806 — nomes em maiúscula seguem a notação da spec (W, T, A, S)
"""EXP-024 (E1–E5): Organizador das 4 seções que aprende com o próprio leitor.

Reaproveita a segmentação, as pistas, o vetor L0 e a coesão do EXP-023 (sem alterar nada lá) e
acrescenta:

- centróides do leitor e do livro, com somas incrementais por estudo salvo. As semelhanças com eles
  entram como **colunas novas** (peso 0 na âncora): as colunas ``sim_*`` da âncora continuam medidas
  contra os centróides-semente, para os pesos do EXP-023 manterem o sentido (achado da F03);
- pistas novas de referência (lista Markdown, link, URL, "Título (Autor, ano)") e a forma de linha
  aprendida (``ref_shape_user``), também com peso 0 na âncora;
- regressão logística online com âncora L2 em ``organizer-v1.json``, projeção e portão-sombra;
- transição pessoal ``T_user`` e temperatura adaptativa;
- ordem de conferência por informação e re-decodificação depois de 1 clique (E4).

Só biblioteca padrão. O texto nunca é reescrito: só trechos são atribuídos a seções.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
EXP023 = EXP.parent / "EXP-023"
for path in (HERE, EXP023 / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import diff_signal  # noqa: E402
import organizer as org  # noqa: E402
import safety_gate  # noqa: E402
import state as st  # noqa: E402

ANCHOR = EXP023 / "artifacts" / "organizer-v1.json"
PROTOTYPES = EXP023 / "data" / "semente" / "prototipos.json"
SECTIONS = org.SECTIONS
NEG_INF = float("-inf")
CENTROID_KEEP = 5000

EXTRA_FEATURES = [
    "ref_md_title_author",
    "ref_md_link",
    "ref_url_line",
    "ref_title_author_year",
    "ref_shape_user",
    *[f"usim_{s}" for s in SECTIONS],
    *[f"bsim_{s}" for s in SECTIONS],
]
REF_MD_TITLE_AUTHOR = re.compile(r"^\s*(?:[-*•]|\d{1,2}[.)])\s+\S.{0,120}?\s[—–]\s+\S")
REF_MD_LINK = re.compile(r"\[[^\]\n]{2,}\]\((?:https?://|www\.)[^)\s]+\)")
REF_URL_LINE = re.compile(r"^\s*(?:[-*•]\s+)?(?:https?://|www\.)\S+\s*$")
REF_TITLE_AUTHOR_YEAR = re.compile(r"\([A-ZÁ-Ú][^()\n]{2,60},\s*(?:1[5-9]\d\d|20\d\d)\)\s*\.?\s*$")

DEFAULTS = {
    # regressão logística online com âncora (spec §4.6)
    "eta0": 0.3,
    "t0": 50.0,
    "mu": 0.02,
    "delta_max": 4.0,
    "eta_beta": 0.02,
    "beta_range": 1.5,
    # centróides do leitor e do livro (colunas novas)
    "scope_min_units": 3.0,  # contagem ponderada mínima numa seção para o centróide existir
    "contrast": 0.0,  # quanto da média das 4 seções sai de cada centróide (0 = desligado)
    # transição pessoal
    "use_T": True,
    "kappa_T": 30.0,
    "alpha_T": 1.0,
    # pesos dos sinais (spec §6.3)
    "omega_keep": 1.0,
    "keep_blind": 0.1,
    "rating_none": 0.5,
    "omega_moved": 1.0,
    "omega_edited": 0.5,
    "omega_click": 1.0,
    "unreviewed_factor": 0.2,  # mantido sem marca "conferir": é a própria previsão (autotreino)
    "retention_min": 0.3,
    # forma de linha de referência
    "shape_alpha": 1.0,
    "shape_scale": 3.0,
    # conferência e clique
    "review_boost": 0.3,
    "local_step_weight": 3.0,
    # portão-sombra (semente) e replay das últimas correções do próprio leitor
    "shadow": True,
    "eps_step": 0.05,
    "eps_total": 0.15,
    "replay": True,
    "replay_size": 120,
    "replay_min_weight": 0.5,
    "eps_replay": 0.02,
    # chaves dos componentes (ablações)
    "learn_weights": True,
    "learn_centroids": True,
    "use_book": True,
    "use_extra_cues": True,
    "use_gating": True,
}


# --- utilidades --------------------------------------------------------------------------------


def softmax(values: list[float]) -> list[float]:
    m = max(values)
    exps = [math.exp(v - m) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def normalized(vector: dict[int, float]) -> dict[int, float]:
    norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
    return {h: v / norm for h, v in vector.items()}


def top(vector: dict[int, float], keep: int) -> dict[int, float]:
    if len(vector) <= keep:
        return vector
    return dict(sorted(vector.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:keep])


def line_shape(text: str) -> str:
    """Forma abstrata da linha: classes de token, até 6, mais o fim. Ex.: ``M T D T``."""
    out: list[str] = []
    for token in text.split():
        if re.match(r"^\[.*\]\(", token) or token.startswith(("http://", "https://", "www.")):
            cls = "U"
        elif token in ("-", "*", "•") or re.match(r"^\d{1,2}[.)]$", token):
            cls = "M"
        elif token in ("—", "–"):
            cls = "D"
        elif re.match(r"^\(?(1[5-9]\d\d|20\d\d)\)?[.,]?$", token):
            cls = "Y"
        elif token[:1] in '"“«':
            cls = "Q"
        elif token[:1] == "(":
            cls = "P"
        elif token[:1].isdigit():
            cls = "N"
        elif token[:1].isupper():
            cls = "A" if token.rstrip(",.").isupper() and len(token) > 2 else "T"
        else:
            cls = "t"
        if not out or out[-1] != cls:
            out.append(cls)
        if len(out) == 6:
            break
    end = text.rstrip()[-1:] if text.strip() else ""
    return " ".join(out) + ("|." if end == "." else "|")


def decode(A, S, T, start, lam):
    """Viterbi exato com custo de troca ponderado por S e transição dada; marginais por FB."""
    n = len(A)

    def trans(i, a, b):
        return T[a][b] - (lam * S.get((i - 1, i), 0.0) if a != b else 0.0)

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
    fwd = [[start[j] + A[0][j] for j in range(4)]]
    for i in range(1, n):
        fwd.append(
            [
                org.logsumexp([fwd[-1][a] + trans(i, a, b) for a in range(4)]) + A[i][b]
                for b in range(4)
            ]
        )
    bwd = [[0.0] * 4 for _ in range(n)]
    for i in range(n - 2, -1, -1):
        bwd[i] = [
            org.logsumexp([trans(i + 1, a, b) + A[i + 1][b] + bwd[i + 1][b] for b in range(4)])
            for a in range(4)
        ]
    marginals = []
    for i in range(n):
        row = [fwd[i][j] + bwd[i][j] for j in range(4)]
        z = org.logsumexp(row)
        marginals.append([math.exp(v - z) if z != NEG_INF else 0.25 for v in row])
    return path, marginals


def entropy(p: list[float]) -> float:
    return -sum(v * math.log(v) for v in p if v > 0)


# --- motor ------------------------------------------------------------------------------------


class AdaptiveOrganizer:
    """Um motor por processo, com um estado por ``user_id`` (isolados)."""

    def __init__(self, params: dict | None = None) -> None:
        self.params = {**DEFAULTS, **(params or {})}
        raw = ANCHOR.read_bytes()
        self.anchor_sha256 = hashlib.sha256(raw).hexdigest()
        self.model = org.Model.from_json(json.loads(raw))
        self.base = org.Organizer(self.model)
        self.names = list(self.model.feature_names) + EXTRA_FEATURES
        self.n_base = len(self.model.feature_names)
        self.sim_index = [self.model.feature_names.index(f"sim_{s}") for s in SECTIONS]
        self.W0 = [list(row) + [0.0] * len(EXTRA_FEATURES) for row in self.model.weights]
        self.b0 = list(self.model.bias)
        self.beta0 = self.model.params.get("beta", 1.0)
        self.base_params = dict(self.model.params)
        self.users: dict[str, dict] = {}
        self._cache: dict = {}
        self.gate = safety_gate.ShadowGate(
            safety_gate.seed_sample(PROTOTYPES), self.params["eps_step"], self.params["eps_total"]
        )
        self._seed = self._prepare_seed()

    # estado ------------------------------------------------------------------------------------

    def state_for(self, user_id: str) -> dict:
        if user_id not in self.users:
            self.users[user_id] = st.new_state(user_id, self.anchor_sha256, 4, len(self.names))
        return self.users[user_id]

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

    # centróides --------------------------------------------------------------------------------

    def centroids(self, state: dict | None, book_id: str | None) -> dict[str, dict[int, float]]:
        """Centróides das colunas ``sim_*`` da âncora: sempre os da semente."""
        return self.model.seed_centroids

    def scope_centroids(self, state: dict | None, book_id: str | None):
        """Centróides do leitor e do livro (para as colunas ``usim_*`` e ``bsim_*``)."""
        empty = {s: {} for s in SECTIONS}
        if state is None or not self.params["learn_centroids"]:
            return empty, empty
        user = state["organizer"]["user"]
        book = state["organizer"]["books"].get(book_id) if self.params["use_book"] else None
        key = ("c", state["user_id"], user["version"], book_id, book["version"] if book else -1)
        if key not in self._cache:
            if len(self._cache) > 256:
                self._cache.clear()
            self._cache[key] = (self._scope(user), self._scope(book) if book else empty)
        return self._cache[key]

    def _scope(self, scope: dict) -> dict[str, dict[int, float]]:
        """Centróide normalizado por seção; com ``contrast``, menos a média das 4 (o assunto)."""
        minimum = self.params["scope_min_units"]
        unit = {
            s: normalized(top(scope["sums"][s], CENTROID_KEEP))
            if scope["counts"][s] >= minimum
            else {}
            for s in SECTIONS
        }
        present = [s for s in SECTIONS if unit[s]]
        if len(present) < 2 or self.params["contrast"] <= 0:
            return unit
        mean: Counter = Counter()
        for s in present:
            for h, v in unit[s].items():
                mean[h] += v / len(present)
        out = {}
        for s in SECTIONS:
            if not unit[s]:
                out[s] = {}
                continue
            diff = {h: v - self.params["contrast"] * mean.get(h, 0.0) for h, v in unit[s].items()}
            out[s] = normalized({h: v for h, v in diff.items() if v > 0})
        return out

    # pistas novas ------------------------------------------------------------------------------

    def shape_score(self, state: dict | None, book_id: str | None, text: str) -> float:
        if state is None:
            return 0.0
        shapes = state["organizer"]["ref_shapes"]
        tables = [shapes["user"]]
        if self.params["use_book"] and book_id in shapes["books"]:
            tables.append(shapes["books"][book_id])
        sig = line_shape(text)
        c_ref = c_oth = tot_ref = tot_oth = 0.0
        for table in tables:
            r, o = table.get(sig, (0.0, 0.0))
            c_ref, c_oth = c_ref + r, c_oth + o
            tr, to = table.get("__total__", (0.0, 0.0))
            tot_ref, tot_oth = tot_ref + tr, tot_oth + to
        if c_ref + c_oth == 0:
            return 0.0
        a = self.params["shape_alpha"]
        prior = (tot_ref + 1) / (tot_ref + tot_oth + 2)
        lo = math.log((c_ref + a * prior) / (c_oth + a * (1 - prior))) - math.log(
            prior / (1 - prior)
        )
        return math.tanh(lo / self.params["shape_scale"])

    def extras(
        self, state: dict | None, book_id: str | None, text: str, vec: dict[int, float]
    ) -> list[float]:
        cues = [0.0] * 5
        if self.params["use_extra_cues"]:
            cues = [
                float(bool(REF_MD_TITLE_AUTHOR.match(text))),
                float(bool(REF_MD_LINK.search(text))),
                float(bool(REF_URL_LINE.match(text))),
                float(bool(REF_TITLE_AUTHOR_YEAR.search(text))),
                self.shape_score(state, book_id, text),
            ]
        user_c, book_c = self.scope_centroids(state, book_id)
        usims = [org.cosine(vec, user_c[s]) if user_c[s] else 0.0 for s in SECTIONS]
        bsims = [org.cosine(vec, book_c[s]) if book_c[s] else 0.0 for s in SECTIONS]
        return cues + usims + bsims

    # análise e decisão ---------------------------------------------------------------------------

    def analyse(self, state, text, layout, book_id):
        cents = self.centroids(state, book_id)
        units, _lines, vecs, xs = self.base.analyse(text, layout, org.Options(), cents)
        xs = [
            x + self.extras(state, book_id, u.text, v)
            for x, u, v in zip(xs, units, vecs, strict=False)
        ]
        return units, vecs, xs

    def probabilities(self, xs, W, b, beta):
        return [
            softmax(
                [
                    (sum(w * v for w, v in zip(row, x, strict=False)) + bb) / beta
                    for row, bb in zip(W, b, strict=False)
                ]
            )
            for x in xs
        ]

    def transition(self, state: dict | None, use_T: bool | None = None):
        use = self.params["use_T"] if use_T is None else use_T
        uniform = math.log(0.25)
        flat = [[uniform] * 4 for _ in range(4)]
        if state is None or not use:
            return flat, [uniform] * 4
        tr = state["organizer"]["transitions"]
        zeta = tr["n"] / (tr["n"] + self.params["kappa_T"]) if tr["n"] > 0 else 0.0
        if zeta == 0:
            return flat, [uniform] * 4
        a = self.params["alpha_T"]
        T = []
        for i in range(4):
            row_total = sum(tr["counts"][i])
            T.append(
                [
                    zeta * math.log((tr["counts"][i][j] + a * 0.25) / (row_total + a))
                    + (1 - zeta) * uniform
                    for j in range(4)
                ]
            )
        start_total = sum(tr["start"])
        start = [
            zeta * math.log((tr["start"][j] + a * 0.25) / (start_total + a)) + (1 - zeta) * uniform
            for j in range(4)
        ]
        return T, start

    def organize(self, user_id, text, layout=None, book_id=None, *, adaptive=True, use_T=None):
        """Sugestão das 4 seções; ``adaptive=False`` é o V4 estático do EXP-023."""
        state = self.state_for(user_id) if adaptive else None
        units, vecs, xs = self.analyse(state, text, layout, book_id)
        if not units:
            return {
                "sections": dict.fromkeys(SECTIONS, ""),
                "segments": [],
                "review_order": [],
                "ctx": None,
            }
        W, b, beta = self.weights(state)
        probs = self.probabilities(xs, W, b, beta)
        S = org.coupling(units, vecs, self.base_params)
        A = [[math.log(max(p, 1e-12)) for p in row] for row in probs]
        T, start = self.transition(state, use_T)
        ctx = {
            "user_id": user_id,
            "book_id": book_id,
            "adaptive": adaptive,
            "units": units,
            "vecs": vecs,
            "xs": xs,
            "S": S,
            "A": A,
            "T": T,
            "start": start,
            "clamps": {},
        }
        return self._decide(ctx, state)

    def _decide(self, ctx, state):
        units, A = ctx["units"], [row[:] for row in ctx["A"]]
        for i, u in enumerate(units):
            if u.heading:
                j = SECTIONS.index(u.heading)
                A[i] = [0.0 if k == j else NEG_INF for k in range(4)]
        for i, j in ctx["clamps"].items():
            A[i] = [0.0 if k == j else NEG_INF for k in range(4)]
        lam = self.base_params.get("lambda", 1.0)
        path, marginals = decode(A, ctx["S"], ctx["T"], ctx["start"], lam)
        margin_threshold = self.base_params.get("review_margin", 0.2)
        if state is not None:
            behaviour = state["organizer"]["behaviour"]
            rejection = behaviour["reverted"] / behaviour["pages"] if behaviour["pages"] else 0.0
            margin_threshold = min(0.5, margin_threshold + self.params["review_boost"] * rejection)
        segments, sections = [], {s: [] for s in SECTIONS}
        gains = []
        for i, (u, j) in enumerate(zip(units, path, strict=False)):
            ranked = sorted(marginals[i], reverse=True)
            margin = ranked[0] - ranked[1]
            coupling = sum(
                ctx["S"].get((i, k), 0.0) for k in range(max(0, i - 3), min(len(units), i + 4))
            )
            gains.append(entropy(marginals[i]) * (1 + coupling))
            segments.append(
                {
                    "index": i,
                    "start": u.start,
                    "end": u.end,
                    "section": SECTIONS[j],
                    "confidence": round(marginals[i][j], 4),
                    "margin": round(margin, 4),
                    "review": margin < margin_threshold and i not in ctx["clamps"],
                }
            )
            sections[SECTIONS[j]].append(u.text)
        order = sorted(range(len(units)), key=lambda i: (-gains[i], i))
        return {
            "sections": {s: "\n".join(v) for s, v in sections.items()},
            "segments": segments,
            "review_order": order,
            "margin_order": sorted(range(len(units)), key=lambda i: (segments[i]["margin"], i)),
            "marginals": marginals,
            "ctx": ctx,
        }

    def click(self, result: dict, index: int, section: str, *, local: bool = False) -> dict:
        """O leitor move o trecho ``index`` para ``section``: restrição rígida e novo Viterbi."""
        ctx = result["ctx"]
        ctx["clamps"][index] = SECTIONS.index(section)
        state = self.state_for(ctx["user_id"]) if ctx["adaptive"] else None
        if local:
            temp = st.new_state("__local__", self.anchor_sha256, 4, len(self.names))
            if state is not None:
                temp["organizer"]["delta_W"] = copy.deepcopy(state["organizer"]["delta_W"])
                temp["organizer"]["delta_b"] = list(state["organizer"]["delta_b"])
                temp["organizer"]["log_beta_delta"] = state["organizer"]["log_beta_delta"]
            for i, j in ctx["clamps"].items():
                self._step(
                    temp, ctx["xs"][i], j, self.params["local_step_weight"], self.params["eta0"]
                )
            W, b, beta = self.weights(temp)
            probs = self.probabilities(ctx["xs"], W, b, beta)
            ctx["A"] = [[math.log(max(p, 1e-12)) for p in row] for row in probs]
        return self._decide(ctx, state)

    # aprendizado ---------------------------------------------------------------------------------

    def _step(self, state, x, y, omega, lr):
        o = state["organizer"]
        W, b, beta = self.weights(state)
        z = [
            sum(w * v for w, v in zip(row, x, strict=False)) + bb
            for row, bb in zip(W, b, strict=False)
        ]
        p = softmax([v / beta for v in z])
        mu = self.params["mu"]
        for c in range(4):
            g = omega * (p[c] - (c == y)) / beta
            row = o["delta_W"][c]
            for j, v in enumerate(x):
                row[j] -= lr * (g * v + mu * row[j])
            o["delta_b"][c] -= lr * (g + mu * o["delta_b"][c])
        g_beta = omega * (z[y] - sum(pc * zc for pc, zc in zip(p, z, strict=False))) / beta
        limit = math.log(self.params["beta_range"])
        o["log_beta_delta"] = max(
            -limit, min(limit, o["log_beta_delta"] - self.params["eta_beta"] * g_beta)
        )

    def _seed_xs(self, state, book_id):
        """Vetores dos protótipos com os centróides e as formas atuais (uma vez por checagem)."""
        return [
            list(x_base) + self.extras(state, book_id, text, vec)
            for x_base, vec, text in self._seed
        ]

    @staticmethod
    def _argmax_all(xs, weights):
        W, b, _beta = weights
        preds = []
        for x in xs:
            z = [
                sum(w * v for w, v in zip(row, x, strict=False)) + bb
                for row, bb in zip(W, b, strict=False)
            ]
            preds.append(max(range(4), key=lambda c: z[c]))
        return preds

    def _prepare_seed(self):
        out = []
        for text, _label in self.gate.units:
            units, _lines, vecs, xs = self.base.analyse(
                text, None, org.Options(), self.model.seed_centroids
            )
            # o protótipo inteiro como uma unidade: usa a primeira (são frases curtas)
            out.append((xs[0], vecs[0], units[0].text))
        return out

    def _shadow(self, state, book_id, previous_weights) -> tuple[bool, str, float]:
        gold = self.gate.gold
        xs = self._seed_xs(state, book_id)
        f1_new = safety_gate.macro_f1(gold, self._argmax_all(xs, self.weights(state)))
        f1_prev = safety_gate.macro_f1(gold, self._argmax_all(xs, previous_weights))
        f1_anchor = safety_gate.macro_f1(gold, self._argmax_all(xs, (self.W0, self.b0, self.beta0)))
        ok, reason = self.gate.accept(f1_new, f1_prev, f1_anchor)
        return ok, reason, f1_new

    @staticmethod
    def _replay_accuracy(replay, weights) -> float:
        W, b, _beta = weights
        right = total = 0.0
        for x, y, w in replay:
            z = [
                sum(a * v for a, v in zip(row, x, strict=False)) + bb
                for row, bb in zip(W, b, strict=False)
            ]
            right += w * (max(range(4), key=lambda c: z[c]) == y)
            total += w
        return right / total if total else 1.0

    def learn_labels(self, state, book_id, units, vecs, xs, labels, weights, sequence_weight=0.0):
        """Aplica rótulos (seção por unidade, peso por unidade) ao estado, com as travas."""
        p = self.params
        o = state["organizer"]
        report = {"labels": sum(1 for w in weights if w > 0), "accepted": True, "reason": ""}
        if report["labels"] == 0:
            return report
        # 1. centróides e formas de linha (aditivos, ponderados)
        book = st.book_scope(state, book_id) if book_id else None
        for u, vec, label, w in zip(units, vecs, labels, weights, strict=False):
            if w <= 0 or label is None:
                continue
            section = SECTIONS[label]
            if p["learn_centroids"]:
                st.add_vector(o["user"], section, vec, w, st.USER_KEEP)
                if book is not None:
                    st.add_vector(book, section, vec, w, st.BOOK_KEEP)
            sig = line_shape(u.text)
            tables = [o["ref_shapes"]["user"]]
            if book_id:
                tables.append(o["ref_shapes"]["books"].setdefault(book_id, {}))
            for table in tables:
                for key in (sig, "__total__"):
                    r, other = table.get(key, (0.0, 0.0))
                    table[key] = (r + w, other) if section == "references" else (r, other + w)
        # 2. pesos, temperatura e transição, sob o portão-sombra
        previous = st.snapshot(state)
        previous_weights = self.weights(state)
        if sequence_weight > 0:
            tr = o["transitions"]
            seq = [
                lab for lab, w in zip(labels, weights, strict=False) if lab is not None and w > 0
            ]
            if seq:
                tr["start"][seq[0]] += sequence_weight
                for a, b in zip(seq, seq[1:], strict=False):
                    tr["counts"][a][b] += sequence_weight
                tr["n"] += sequence_weight
        if p["learn_weights"]:
            for x, label, w in zip(xs, labels, weights, strict=False):
                if w <= 0 or label is None:
                    continue
                lr = p["eta0"] / math.sqrt(1 + o["steps"] / p["t0"])
                self._step(state, x, label, w, lr)
                o["steps"] += 1
            safety_gate.project(o["delta_W"], o["delta_b"], p["delta_max"])
            ok, reason = True, ""
            replay = o.setdefault("replay", [])
            if p["replay"] and replay:
                before = self._replay_accuracy(replay, previous_weights)
                after = self._replay_accuracy(replay, self.weights(state))
                if after < before - p["eps_replay"]:
                    ok, reason = False, "replay_regression"
            if ok and p["shadow"]:
                ok, reason, _f1 = self._shadow(state, book_id, previous_weights)
            if not ok:
                st.restore(state, previous)
                o["behaviour"]["rejected_updates"] += 1
                report.update(accepted=False, reason=reason)
            # as correções confiáveis desta página entram no replay (depois de decidir)
            for x, label, w in zip(xs, labels, weights, strict=False):
                if label is not None and w >= p["replay_min_weight"]:
                    replay.append([[round(v, 4) for v in x], label, round(w, 3)])
            del replay[: max(0, len(replay) - p["replay_size"])]
        state["updates"] += 1
        return report

    def learn(self, feedback: dict) -> dict:
        """Aprende com uma página revisada e salva (pacote ``leitorum-feedback/1``)."""
        state = self.state_for(feedback["user_id"])
        o = state["organizer"]
        organizer = feedback["organizer"]
        book_id = feedback.get("book_id")
        o["behaviour"]["pages"] += 1
        if organizer.get("reverted"):
            o["behaviour"]["reverted"] += 1
        text, segments = organizer["text"], organizer["suggested"]["segments"]
        outcomes = diff_signal.align_units(text, segments, feedback["saved"])
        clicked = {c["index"] for c in organizer.get("clicks", [])}
        moved = sum(out.outcome == "moved" for out in outcomes)
        edited = sum(out.outcome == "edited" for out in outcomes)
        total = sum(s["end"] - s["start"] for s in segments) or 1
        kept_chars = sum(
            s["end"] - s["start"]
            for s, out in zip(segments, outcomes, strict=False)
            if out.outcome == "kept"
        )
        reading = feedback.get("reading", {})
        blind = (
            moved == 0
            and edited == 0
            and not clicked
            and reading.get("shown_lines") is not None
            and organizer["text"] == "\n".join(reading["shown_lines"])
        )
        if blind:
            o["behaviour"]["blind"] += 1
        if self.params["use_gating"]:
            pw = safety_gate.page_weights(
                reverted=bool(organizer.get("reverted")),
                rating=feedback.get("rating"),
                corrections=moved + edited + len(clicked),
                blind=blind,
                retention=kept_chars / total,
                params=self.params,
            )
        else:
            pw = safety_gate.PageWeights(
                0.0 if organizer.get("reverted") else 1.0,
                1.0,
                1.0,
                1.0,
                bool(organizer.get("reverted")),
                "",
            )
        if pw.gated:
            state["updates"] += 1
            return {"labels": 0, "accepted": True, "reason": pw.reason, "gated": True}
        units, vecs, xs = self.analyse(state, text, organizer.get("layout"), book_id)
        if [(u.start, u.end) for u in units] != [(s["start"], s["end"]) for s in segments]:
            # a análise mudou entre sugerir e salvar: não arrisca rótulos desalinhados
            state["updates"] += 1
            return {"labels": 0, "accepted": True, "reason": "misaligned", "gated": True}
        labels, weights = [], []
        for seg, out in zip(segments, outcomes, strict=False):
            if out.outcome == "deleted" or out.final is None:
                labels.append(None)
                weights.append(0.0)
                continue
            labels.append(SECTIONS.index(out.final))
            keep = pw.keep if seg.get("review") else pw.keep * self.params["unreviewed_factor"]
            w = {"kept": keep, "moved": pw.moved, "edited": pw.edited}[out.outcome]
            if out.index in clicked:
                w = max(w, pw.click)
            weights.append(w)
        corrected = moved + edited + len(clicked) > 0
        seq_weight = 1.0 if corrected else pw.keep
        report = self.learn_labels(state, book_id, units, vecs, xs, labels, weights, seq_weight)
        report["gated"] = False
        return report

    def learn_study(self, user_id: str, book_id: str | None, columns: dict[str, str]) -> dict:
        """Aprende com um estudo salvo sem sugestão (importado ou antigo): rótulos pelas colunas.

        Não alimenta a transição: as colunas não guardam a ordem dos trechos na página.
        """
        state = self.state_for(user_id)
        parts, labels_by_char = [], []
        for s in SECTIONS:
            body = (columns.get(s) or "").strip()
            if not body:
                continue
            if parts:
                parts.append("\n")
                labels_by_char.append(SECTIONS.index(s))
            parts.append(body)
            labels_by_char.extend([SECTIONS.index(s)] * len(body))
        text = "".join(parts)
        if not text:
            return {"labels": 0, "accepted": True, "reason": "empty"}
        units, vecs, xs = self.analyse(state, text, None, book_id)
        labels = [Counter(labels_by_char[u.start : u.end]).most_common(1)[0][0] for u in units]
        return self.learn_labels(state, book_id, units, vecs, xs, labels, [1.0] * len(units), 0.0)
