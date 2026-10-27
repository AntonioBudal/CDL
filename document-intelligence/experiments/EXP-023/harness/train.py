# ruff: noqa: N803, N806, N815 — nomes em maiúscula seguem a notação da spec (A, S, T, F, W, X)
"""EXP-023, F04: ajuste dos pesos e parâmetros só em treino e validação; exporta
``organizer-v1.json``.

1. Centróides-semente e IDF a partir dos protótipos (D-semente).
2. Vetores das unidades das páginas de treino (limpo, CER 10 % e 25 %; com e sem geometria).
3. Regressão logística multinomial (escala dobrada nos pesos) para três conjuntos de pistas:
   estrutura + léxico (pipeline), só estrutura (B2) e só léxico (B3). C escolhido na validação.
4. Temperatura beta pela verossimilhança na validação.
5. Parâmetros relacionais (tau, omega, lambda, alpha, sigma_g, eta) por busca em grade na validação.
6. Margem de "conferir": menor margem com acerto >= 90 % das unidades acima dela, na validação.

O conjunto de teste não é tocado aqui.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections import Counter
from itertools import product
from pathlib import Path

import numpy as np
import organizer as org
from metrics import CODE, Scores
from pages import DATA, build_pages, layout, page_text, with_noise
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ART = HERE.parent / "artifacts"
NOISE = ROOT / "dataset" / "processed" / "exp-023" / "noise-model.json"
CERS = (0.0, 0.10, 0.25)
DEFAULT_PARAMS = {
    "tau": 1.0,
    "omega": 0.25,
    "lambda": 1.0,
    "alpha": 0.5,
    "sigma_g": 1.5,
    "eta": 1.0,
    "w": 3,
    "sim_floor": 0.05,
    "beta": 1.0,
    "kappa": 50.0,
    "gap_break": 1.6,
    "review_margin": 0.3,
}
FEATURE_SETS = {
    "full": org.FEATURES + [f"sim_{s}" for s in org.SECTIONS],
    "features": list(org.FEATURES),
    "lexical": [f"sim_{s}" for s in org.SECTIONS],
}


def seed_model() -> org.Model:
    protos = json.loads((DATA / "semente" / "prototipos.json").read_text(encoding="utf-8"))
    docs = [p for s in org.SECTIONS for p in protos[s]]
    idf, default_idf = org.build_idf(docs)
    cents = {
        s: org.centroid([org.tfidf(p, idf, default_idf) for p in protos[s]]) for s in org.SECTIONS
    }
    names = FEATURE_SETS["full"]
    return org.Model(
        names,
        [[0.0] * len(names) for _ in range(4)],
        [0.0] * 4,
        dict(DEFAULT_PARAMS),
        cents,
        idf,
        default_idf,
    )


def versions(pages: list[dict], model_noise: dict) -> list[tuple[dict, float, bool]]:
    return [
        (with_noise(p, model_noise, cer), cer, geo)
        for p in pages
        for cer in CERS
        for geo in (True, False)
    ]


def analyse_all(organizer: org.Organizer, items, options: org.Options | None = None) -> list[dict]:
    out = []
    for page, cer, geo in items:
        text, labels, units_gold = page_text(page)
        opts = options or org.Options(use_layout=geo)
        opts.use_layout = geo
        units, _lines, vecs, xs = organizer.analyse(text, layout(page) if geo else None, opts)
        gold = []
        weights = []
        for u in units:
            span = [labels[i] for i in range(u.start, u.end) if not text[i].isspace()]
            gold.append(org.SECTIONS.index(CODE[Counter(span).most_common(1)[0][0]]) if span else 1)
            weights.append(max(1, len(span)))
        out.append(
            {
                "page": page,
                "cer": cer,
                "geo": geo,
                "text": text,
                "labels": labels,
                "units_gold": units_gold,
                "units": units,
                "vecs": vecs,
                "xs": xs,
                "gold": gold,
                "weights": weights,
            }
        )
    return out


def matrix(analysed, names: list[str], all_names: list[str]):
    idx = [all_names.index(n) for n in names]
    X = np.array([[x[i] for i in idx] for a in analysed for x in a["xs"]], dtype=float)
    y = np.array([g for a in analysed for g in a["gold"]])
    w = np.array([wt for a in analysed for wt in a["weights"]], dtype=float)
    return X, y, w


def fit(train, val, names, all_names) -> tuple[list[list[float]], list[float], float, float]:
    Xt, yt, wt = matrix(train, names, all_names)
    Xv, yv, wv = matrix(val, names, all_names)
    mu, sd = Xt.mean(axis=0), Xt.std(axis=0)
    sd[sd < 1e-9] = 1.0
    best = None
    for C in (0.03, 0.1, 0.3, 1.0, 3.0):
        clf = LogisticRegression(C=C, max_iter=3000, class_weight="balanced")
        clf.fit((Xt - mu) / sd, yt, sample_weight=wt)
        pred = clf.predict((Xv - mu) / sd)
        f1s = []
        for c in range(4):
            tp = wv[(pred == c) & (yv == c)].sum()
            fp = wv[(pred == c) & (yv != c)].sum()
            fn = wv[(pred != c) & (yv == c)].sum()
            f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
        score = float(np.mean(f1s))
        if best is None or score > best[0]:
            best = (score, C, clf)
    _, C, clf = best
    W = clf.coef_ / sd
    b = clf.intercept_ - (clf.coef_ * mu / sd).sum(axis=1)
    # temperatura na validação
    logits = Xv @ W.T + b
    best_beta, best_nll = 1.0, math.inf
    for beta in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0):
        z = logits / beta
        z = z - z.max(axis=1, keepdims=True)
        logp = z - np.log(np.exp(z).sum(axis=1, keepdims=True))
        nll = -(logp[np.arange(len(yv)), yv] * wv).sum() / wv.sum()
        if nll < best_nll:
            best_beta, best_nll = beta, nll
    return W.tolist(), b.tolist(), C, best_beta


def expand(W, b, names, all_names):
    """Pesos de um subconjunto de pistas levados ao vetor completo (zero nas demais pistas)."""
    full = [[0.0] * len(all_names) for _ in range(4)]
    for k, n in enumerate(names):
        for c in range(4):
            full[c][all_names.index(n)] = W[c][k]
    return full, b


def evaluate(
    organizer: org.Organizer,
    analysed,
    options: org.Options,
    params: dict,
    probs_cache=None,
    sims_cache=None,
) -> dict:
    scores = Scores()
    for k, a in enumerate(analysed):
        probs = probs_cache[k] if probs_cache else None
        sims = sims_cache[k] if sims_cache else None
        result = organizer.decide(
            a["units"], a["vecs"], a["xs"], options, params, probs=probs, pair_sims=sims
        )
        scores.add(a["text"], a["labels"], a["units_gold"], result)
    return scores.report()


def pair_sims(a, w=4) -> dict:
    out = {}
    v = a["vecs"]
    for i in range(len(v)):
        for k in range(i + 1, min(len(v), i + w + 1)):
            out[(i, k)] = out[(k, i)] = org.cosine(v[i], v[k])
    return out


def objective(report: dict) -> float:
    return report["macro_f1_chars"] - 0.05 * report["windowdiff"]


def tune(organizer: org.Organizer, val) -> tuple[dict, list]:
    probs = [org.affinities(a["xs"], organizer.model) for a in val]
    sims = [pair_sims(a) for a in val]
    params = dict(organizer.model.params)
    full = org.Options()
    log = []

    def run(trial: dict) -> float:
        report = evaluate(organizer, val, full, {**params, **trial}, probs, sims)
        log.append(
            {**trial, "macro_f1": report["macro_f1_chars"], "windowdiff": report["windowdiff"]}
        )
        return objective(report)

    best = max(
        (
            {"tau": t, "omega": o, "lambda": lam, "alpha": 0.0}
            for t, o, lam in product(
                (0.0, 0.5, 1.0, 1.5, 2.0, 3.0), (0.0, 0.25, 0.5), (0.0, 0.5, 1.0, 2.0, 4.0)
            )
        ),
        key=run,
    )
    params.update(best)
    best = max(
        (
            {"alpha": a, "sigma_g": s, "eta": e}
            for a, s, e in product((0.0, 0.2, 0.4, 0.6, 0.8), (0.75, 1.5, 3.0), (0.0, 1.0, 2.0))
        ),
        key=run,
    )
    params.update(best)
    for _ in range(4):  # refina tau e lambda até lambda cair no interior da grade
        grid = (params["lambda"] / 2, params["lambda"], params["lambda"] * 2)
        best = max(
            (
                {"tau": t, "lambda": lam}
                for t, lam in product(
                    (params["tau"] - 0.5, params["tau"], params["tau"] + 0.5), grid
                )
                if t >= 0
            ),
            key=run,
        )
        params.update(best)
        if best["lambda"] != grid[-1]:
            break
    return params, log


def review_margin(organizer: org.Organizer, val, params: dict) -> float:
    pairs = []
    for a in val:
        result = organizer.decide(a["units"], a["vecs"], a["xs"], org.Options(), params)
        for seg, g in zip(result["segments"], a["gold"], strict=False):
            pairs.append((seg["margin"], org.SECTIONS.index(seg["section"]) == g))
    for m in [x / 20 for x in range(0, 20)]:
        above = [ok for margin, ok in pairs if margin >= m]
        if above and sum(above) / len(above) >= 0.9:
            return m
    return 0.95


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    started = time.time()
    noise_model = json.loads(NOISE.read_text(encoding="utf-8"))
    pages = build_pages()
    model = seed_model()
    organizer = org.Organizer(model)
    train = analyse_all(organizer, versions(pages["train"], noise_model))
    val = analyse_all(organizer, versions(pages["val"], noise_model))
    print(
        f"unidades: treino {sum(len(a['units']) for a in train)},"
        f" validação {sum(len(a['units']) for a in val)}"
    )
    all_names = FEATURE_SETS["full"]
    fitted = {}
    for name, names in FEATURE_SETS.items():
        W, b, C, beta = fit(train, val, names, all_names)
        fitted[name] = {
            "weights": expand(W, b, names, all_names)[0],
            "bias": b,
            "C": C,
            "beta": beta,
        }
        print(f"{name}: C={C} beta={beta}")
    model.weights, model.bias = fitted["full"]["weights"], fitted["full"]["bias"]
    model.params["beta"] = fitted["full"]["beta"]
    params, log = tune(organizer, val)
    model.params.update(params)
    model.params["review_margin"] = review_margin(organizer, val, model.params)
    print(
        "parâmetros:",
        {
            k: model.params[k]
            for k in ("tau", "omega", "lambda", "alpha", "sigma_g", "eta", "beta", "review_margin")
        },
    )
    ART.mkdir(exist_ok=True)
    sums = (DATA / "SHA256SUMS").read_text(encoding="utf-8")
    artifact = {
        "name": "leitorum-organizer",
        "version": "1",
        "created_by": "EXP-023 harness/train.py",
        "license": "MIT — pesos ajustados só em dados fictícios (D-semente, D-sintético)",
        "data_sha256sums": sums,
        "hashing": {
            "dim": org.HASH_DIM,
            "ngrams": list(org.NGRAMS),
            "hash": "zlib.crc32 de n-gramas de ' palavra ' sem acento e minúscula",
        },
        "cues": org.CUES,
        "feature_names": all_names,
        "weights": model.weights,
        "bias": model.bias,
        "params": model.params,
        "baselines": {name: dict(f.items()) for name, f in fitted.items() if name != "full"},
        "C": fitted["full"]["C"],
        "seed_centroids": {
            s: {str(h): round(v, 6) for h, v in c.items()} for s, c in model.seed_centroids.items()
        },
        "idf": {str(h): round(v, 5) for h, v in model.idf.items()},
        "default_idf": model.default_idf,
    }
    body = json.dumps(artifact, ensure_ascii=False, sort_keys=True)
    (ART / "organizer-v1.json").write_text(body, encoding="utf-8")
    (ART / "organizer-v1.sha256").write_text(
        hashlib.sha256(body.encode("utf-8")).hexdigest() + "\n", encoding="utf-8"
    )
    (ART / "tuning-log.json").write_text(json.dumps(log, indent=0), encoding="utf-8")
    print(f"exportado em {time.time() - started:.0f} s; {len(body) / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
