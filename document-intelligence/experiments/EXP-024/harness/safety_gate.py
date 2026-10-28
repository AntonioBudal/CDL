"""EXP-024: travas de segurança do aprendizado contínuo (spec §5).

- ``page_weights``: peso de cada tipo de rótulo de uma página, a partir do comportamento (E3) e da
  nota opcional (E6). É o *reward gating*: reversão, ou nota 1–2 sem correção, não ensinam nada.
- ``project``: mantém ``‖W − W0‖_F ≤ Δmax`` (âncora L2).
- ``ShadowGate``: confere em memória, a cada atualização, se os protótipos-semente continuam bem
  classificados. Uma piora maior que ε em relação ao passo anterior, ou em relação à âncora,
  desfaz a
  atualização (rollback). O canário (páginas fictícias do EXP-023) roda a cada N atualizações.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

SECTIONS = ("summary", "explanation", "concepts", "references")
SEED_PER_SECTION = 10


@dataclass(frozen=True)
class PageWeights:
    keep: float
    moved: float
    edited: float
    click: float
    gated: bool
    reason: str


def page_weights(
    *,
    reverted: bool,
    rating: int | None,
    corrections: int,
    blind: bool,
    retention: float,
    params: dict,
) -> PageWeights:
    """Pesos dos rótulos de uma página (spec §6.3)."""
    if reverted:
        return PageWeights(0.0, 0.0, 0.0, 0.0, True, "reverted")
    if rating is not None and rating <= 2 and corrections == 0:
        return PageWeights(0.0, 0.0, 0.0, 0.0, True, "low_rating_without_corrections")
    if corrections == 0 and retention < params["retention_min"] and not blind:
        return PageWeights(0.0, 0.0, 0.0, 0.0, True, "low_retention")
    omega0 = params["omega_keep"]
    if blind:
        keep = params["keep_blind"]
    elif rating is None:
        keep = params["rating_none"] * omega0
    else:
        keep = (rating - 1) / 4 * omega0
    return PageWeights(
        keep, params["omega_moved"], params["omega_edited"], params["omega_click"], False, ""
    )


def frobenius(delta_w: list[list[float]], delta_b: list[float]) -> float:
    return math.sqrt(sum(v * v for row in delta_w for v in row) + sum(v * v for v in delta_b))


def project(delta_w: list[list[float]], delta_b: list[float], radius: float) -> bool:
    """Projeta (ΔW, Δb) na bola de raio ``radius``; devolve True se precisou encolher."""
    norm = frobenius(delta_w, delta_b)
    if norm <= radius or norm == 0:
        return False
    scale = radius / norm
    for row in delta_w:
        for j in range(len(row)):
            row[j] *= scale
    for j in range(len(delta_b)):
        delta_b[j] *= scale
    return True


def macro_f1(gold: list[int], pred: list[int], weights: list[float] | None = None) -> float:
    weights = weights or [1.0] * len(gold)
    scores = []
    for c in range(len(SECTIONS)):
        tp = sum(w for g, p, w in zip(gold, pred, weights, strict=False) if g == c and p == c)
        fp = sum(w for g, p, w in zip(gold, pred, weights, strict=False) if g != c and p == c)
        fn = sum(w for g, p, w in zip(gold, pred, weights, strict=False) if g == c and p != c)
        if tp + fp + fn > 0:
            scores.append(2 * tp / (2 * tp + fp + fn))
    return sum(scores) / len(scores) if scores else 0.0


def seed_sample(prototypes_path: Path) -> list[tuple[str, int]]:
    """10 protótipos por seção, escolhidos por *hash* (determinístico)."""
    data = json.loads(prototypes_path.read_text(encoding="utf-8"))
    out = []
    for c, section in enumerate(SECTIONS):
        ranked = sorted(data[section], key=lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest())
        out.extend((text, c) for text in ranked[:SEED_PER_SECTION])
    return out


class ShadowGate:
    """Portão-sombra sobre os protótipos-semente (macro-F1 das previsões e critério de aceite)."""

    def __init__(self, units: list[tuple[str, int]], eps_step: float, eps_total: float) -> None:
        self.units = units
        self.gold = [c for _, c in units]
        self.eps_step = eps_step
        self.eps_total = eps_total

    def score(self, predict) -> float:
        """``predict()`` devolve a seção prevista de cada protótipo, na ordem de ``units``."""
        return macro_f1(self.gold, predict())

    def accept(self, f1_new: float, f1_previous: float, f1_anchor: float) -> tuple[bool, str]:
        if f1_new < f1_previous - self.eps_step:
            return False, "step_regression"
        if f1_new < f1_anchor - self.eps_total:
            return False, "total_regression"
        return True, ""
