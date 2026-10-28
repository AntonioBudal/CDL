"""EXP-024: estado de aprendizado por usuário (schema ``leitorum-learning-state/1``).

O estado guarda só o que o motor aprendeu com o próprio leitor:

- somas esparsas dos vetores L0 por seção, no usuário e em cada livro, com contagens ponderadas;
- o desvio dos pesos em relação à âncora (``organizer-v1.json``), a temperatura e as transições;
- formas de linha de referência, léxico, confusões de leitura e calibração de ``low_confidence``;
- o snapshot "último bom" para o rollback do portão-sombra.

A atualização custa O(tamanho da página), independente do histórico. As somas são podadas de forma
determinística (maior magnitude, desempate pelo *hash*) quando passam de 2K entradas.
"""

from __future__ import annotations

import copy
import json

SCHEMA = "leitorum-learning-state/1"
SECTIONS = ("summary", "explanation", "concepts", "references")
USER_KEEP = 2000
BOOK_KEEP = 300


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


def snapshot(state: dict) -> dict:
    org = state["organizer"]
    return copy.deepcopy(
        {
            "delta_W": org["delta_W"],
            "delta_b": org["delta_b"],
            "log_beta_delta": org["log_beta_delta"],
            "transitions": org["transitions"],
        }
    )


def restore(state: dict, snap: dict) -> None:
    org = state["organizer"]
    for key, value in copy.deepcopy(snap).items():
        org[key] = value


# --- serialização ---------------------------------------------------------------------------------


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
