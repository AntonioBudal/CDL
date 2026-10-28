# ruff: noqa: N806 — W e C seguem a notação da spec
"""EXP-025, F02: treina o ``organizer-v2`` em lote, só em treino e validação, e exporta o artefato.

1. Dados: treino e validação do D-sintético do EXP-023, mais as páginas dos fluxos de VALIDAÇÃO
   do EXP-024 (adaptação no treino, *holdout* na validação). Cada página em 6 versões: CER 0, 10 e
   25 %, com e sem geometria. O teste do EXP-023 e os fluxos de teste do EXP-024 não são tocados.
2. Vetor de cada unidade: as 41 colunas do v1 mais as 4 pistas fixas de referência.
3. Dois modos, escolhidos na validação:
   - ``full``: regressão logística em todas as 45 colunas (procedimento do EXP-023), com C e
     temperatura na validação e margem de "conferir" reajustada;
   - ``cues``: pesos, viés, temperatura e margem do v1 **congelados**; só os pesos das 4 colunas
     novas são aprendidos, somados aos *logits* do v1 (L2 escolhida na validação). Onde as pistas
     não disparam, o v2 é idêntico ao v1.
4. Parâmetros relacionais do v1 mantidos.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \
        experiments/EXP-025/harness/train.py --mode cues
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (HERE, EXPS / "EXP-023" / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))  # no fim: não sombreia o evaluate do EXP-023

import organizer as org  # noqa: E402
import organizer_v2 as v2  # noqa: E402
import pages  # noqa: E402  (EXP-023)
import streams  # noqa: E402  (EXP-024)
import train as t23  # noqa: E402  (EXP-023: analyse_all, fit, versions, review_margin)

ART = HERE.parent / "artifacts"
V1 = EXPS / "EXP-023" / "artifacts" / "organizer-v1.json"
NAMES = t23.FEATURE_SETS["full"] + v2.EXTRA_NAMES


def exp024_pages(role: str) -> list[dict]:
    """Páginas dos fluxos de VALIDAÇÃO do EXP-024: ``adapt`` (treino) ou ``holdout`` (validação)."""
    out = []
    for st in streams.all_streams("val").values():
        if role == "adapt":
            out.extend(st["adapt"])
        else:
            out.extend(p for book_pages in st["holdout"].values() for p in book_pages)
    return out


def with_cues(analysed: list[dict]) -> list[dict]:
    for a in analysed:
        a["xs"] = [x + v2.cue_values(u.text) for x, u in zip(a["xs"], a["units"], strict=False)]
    return analysed


def build_sets(engine: org.Organizer) -> tuple[list[dict], list[dict]]:
    noise = json.loads(t23.NOISE.read_text(encoding="utf-8"))
    built = pages.build_pages()
    train = t23.analyse_all(engine, t23.versions(built["train"] + exp024_pages("adapt"), noise))
    val = t23.analyse_all(engine, t23.versions(built["val"] + exp024_pages("holdout"), noise))
    return with_cues(train), with_cues(val)


def fit_cues(train, val, base: org.Model) -> tuple[list[list[float]], float]:
    """Pesos só das 4 colunas novas, com os logits do v1 como deslocamento fixo."""
    n_base = len(base.feature_names)

    def arrays(analysed):
        x = np.array([xx for a in analysed for xx in a["xs"]], dtype=float)
        y = np.array([g for a in analysed for g in a["gold"]])
        w = np.array([wt for a in analysed for wt in a["weights"]], dtype=float)
        offset = x[:, :n_base] @ np.array(base.weights).T + np.array(base.bias)
        return x[:, n_base:], offset, y, w

    xt, ot, yt, wt = arrays(train)
    xv, ov, yv, wv = arrays(val)
    counts = np.bincount(yt, weights=wt, minlength=4)
    wt = wt * (counts.sum() / (4 * counts))[yt]  # classes balanceadas, como no EXP-023
    beta = base.params["beta"]
    onehot = np.eye(4)[yt]
    best = None
    for reg in (0.001, 0.01, 0.1, 1.0):
        v = np.zeros((4, xt.shape[1]))
        for _ in range(3000):
            z = (ot + xt @ v.T) / beta
            z -= z.max(axis=1, keepdims=True)
            p = np.exp(z)
            p /= p.sum(axis=1, keepdims=True)
            grad = ((p - onehot) * wt[:, None]).T @ xt / (beta * wt.sum()) + reg * v
            v -= 0.5 * grad
        pred = (ov + xv @ v.T).argmax(axis=1)
        f1s = []
        for c in range(4):
            tp = wv[(pred == c) & (yv == c)].sum()
            fp = wv[(pred == c) & (yv != c)].sum()
            fn = wv[(pred != c) & (yv == c)].sum()
            f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
        score = float(np.mean(f1s))
        print(f"  cues reg={reg}: macro-F1 por unidade na validação {score:.4f}")
        if best is None or score > best[0]:
            best = (score, reg, v)
    return best[2].tolist(), best[1]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("full", "cues"), default="cues")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    started = time.time()
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    base = org.Model.from_json(v1)
    engine = org.Organizer(base)  # análise com os centróides-semente e o IDF do v1
    train, val = build_sets(engine)
    n_train, n_val = sum(len(a["units"]) for a in train), sum(len(a["units"]) for a in val)
    print(f"unidades: treino {n_train}, validação {n_val}")
    if args.mode == "full":
        W, b, C, beta = t23.fit(train, val, NAMES, NAMES)
        model = org.Model(
            NAMES,
            W,
            b,
            {**base.params, "beta": beta},
            base.seed_centroids,
            base.idf,
            base.default_idf,
        )
        margin = t23.review_margin(org.Organizer(model), val, model.params)
        model.params["review_margin"] = margin
        print(f"C={C} beta={beta} review_margin={margin}")
    else:
        extra, reg = fit_cues(train, val, base)
        W = [list(row) + list(e) for row, e in zip(base.weights, extra, strict=False)]
        b, C = list(base.bias), {"v1": v1["C"], "cues_l2": reg}
        model = org.Model(
            NAMES, W, b, dict(base.params), base.seed_centroids, base.idf, base.default_idf
        )
        print(f"modo cues: L2={reg}; pesos das pistas {[[round(x, 2) for x in e] for e in extra]}")
    sums = (
        "EXP-023/data:\n"
        + (EXPS / "EXP-023" / "data" / "SHA256SUMS").read_text(encoding="utf-8")
        + "EXP-024/data:\n"
        + (EXPS / "EXP-024" / "data" / "SHA256SUMS").read_text(encoding="utf-8")
    ).replace("\r\n", "\n")
    artifact = {
        **{k: v1[k] for k in ("name", "hashing", "cues", "seed_centroids", "idf", "default_idf")},
        "version": "2",
        "created_by": f"EXP-025 harness/train.py --mode {args.mode}",
        "license": (
            "MIT — pesos ajustados só em dados fictícios"
            " (EXP-023 D-semente e D-sintético; EXP-024 fluxos de validação)"
        ),
        "data_sha256sums": sums,
        "feature_names": NAMES,
        "extra_cues": {name: {"pattern": p, "mode": m} for name, (p, m) in v2.EXTRA_CUES.items()},
        "weights": W,
        "bias": b,
        "params": model.params,
        "C": C,
    }
    body = json.dumps(artifact, ensure_ascii=False, sort_keys=True)
    ART.mkdir(exist_ok=True)
    (ART / "organizer-v2.json").write_text(body, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (ART / "organizer-v2.sha256").write_text(sha + "\n", encoding="utf-8", newline="\n")
    print(f"exportado em {time.time() - started:.0f} s; {len(body) / 1e6:.2f} MB; sha256 {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
