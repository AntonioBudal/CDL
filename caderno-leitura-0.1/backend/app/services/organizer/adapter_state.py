# Cópia literal de funções de document-intelligence/experiments/EXP-024/harness (commit 070c9e8):
# ``adaptive_organizer.py`` (softmax, normalized, top, line_shape), ``safety_gate.py`` (PageWeights,
# page_weights, frobenius, project) e ``state.py`` (estado por usuário e serialização), sem mudança de
# lógica. É o ``adapter_deps`` do EXP-025 no produto: ``adapter.py`` importa daqui.
# A paridade é conferida por tests/test_adapter_parity.py. Não editar sem repetir no experimento.
"""Utilidades do adaptador do organizador (feature 091-C): estado por usuário, gating e projeção."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

from app.services.organizer.engine import Options, cosine  # noqa: F401  (usados pelo adapter)
from app.services.organizer.feedback_signal import align_units  # noqa: F401  (usado pelo adapter)

SCHEMA = "leitorum-learning-state/1"
SECTIONS = ("summary", "explanation", "concepts", "references")
USER_KEEP = 2000
BOOK_KEEP = 300

# --- adaptive_organizer.py ----------------------------------------------------------------------


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


# --- safety_gate.py ----------------------------------------------------------------------------


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


# --- state.py ----------------------------------------------------------------------------------


def empty_scope() -> dict:
    return {"sums": {s: {} for s in SECTIONS}, "counts": dict.fromkeys(SECTIONS, 0.0), "version": 0}


def new_state(user_id: str, anchor_sha256: str, n_classes: int, n_features: int) -> dict:
    return {
        "schema": SCHEMA,
        "anchor_sha256": anchor_sha256,
        "user_id": user_id,
        "updates": 0,
        "organizer": {
            "user": empty_scope(),
            "books": {},
            "delta_W": [[0.0] * n_features for _ in range(n_classes)],
            "delta_b": [0.0] * n_classes,
            "log_beta_delta": 0.0,
            "steps": 0,
            "transitions": {
                "counts": [[0.0] * n_classes for _ in range(n_classes)],
                "start": [0.0] * n_classes,
                "n": 0.0,
            },
            "ref_shapes": {"user": {}, "books": {}},
            "behaviour": {"pages": 0, "reverted": 0, "blind": 0, "rejected_updates": 0},
            "last_good": None,
        },
        "reading": {
            "lexicon": {"user": {}, "books": {}},
            "confusions": {},
            "low_confidence": {"a": 0.0, "b": 0.0, "n": 0, "threshold": None, "hist": [0] * 20},
        },
    }


def prune(sums: dict[int, float], keep: int) -> dict[int, float]:
    """Poda determinística: mantém as ``keep`` maiores magnitudes; desempate pelo menor *hash*."""
    if len(sums) <= 2 * keep:
        return sums
    top = sorted(sums.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:keep]
    return dict(top)


def add_vector(
    scope: dict, section: str, vector: dict[int, float], weight: float, keep: int
) -> None:
    if weight <= 0:
        return
    sums = scope["sums"][section]
    for h, v in vector.items():
        sums[h] = sums.get(h, 0.0) + weight * v
    scope["sums"][section] = prune(sums, keep)
    scope["counts"][section] += weight
    scope["version"] += 1


def book_scope(state: dict, book_id: str) -> dict:
    books = state["organizer"]["books"]
    if book_id not in books:
        books[book_id] = empty_scope()
    return books[book_id]


def _keys_to_str(obj):
    if isinstance(obj, dict):
        return {str(k): _keys_to_str(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_keys_to_str(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 5)
    return obj


def dumps(state: dict) -> str:
    return json.dumps(
        _keys_to_str(state), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )


def _int_keys(sums: dict) -> dict[int, float]:
    return {int(h): v for h, v in sums.items()}


def loads(text: str) -> dict:
    state = json.loads(text)
    if state.get("schema") != SCHEMA:
        raise ValueError(f"schema desconhecido: {state.get('schema')}")
    org = state["organizer"]
    for scope in [org["user"], *org["books"].values()]:
        scope["sums"] = {s: _int_keys(v) for s, v in scope["sums"].items()}
    return state


def size_bytes(state: dict) -> int:
    return len(dumps(state).encode("utf-8"))
