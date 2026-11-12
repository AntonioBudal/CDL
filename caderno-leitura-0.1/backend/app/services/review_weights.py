"""F0.11.08 (spec 110): peso de dificuldade e fila da revisão (funções puras).

``peso = 0,5 × peso anterior + 0,5 × alvo`` (difícil 1, médio 0,5, fácil 0); sem avaliação, vale 0,5.
O intervalo até o item vencer sai do peso na hora; nada de data de vencimento guardada.
"""
from __future__ import annotations

from datetime import UTC, datetime

NEUTRAL_WEIGHT = 0.5
FRAGILE_WEIGHT = 0.6
RATING_TARGET = {"hard": 1.0, "medium": 0.5, "easy": 0.0}
LEGACY_WEIGHT = {"hard": 0.75, "medium": 0.5, "easy": 0.25}


def effective_weight(weight: float | None, last_rating: str | None) -> float | None:
    """Peso guardado; sem ele, o equivalente à última nota (como no preenchimento da migração 0037)."""
    if weight is not None:
        return float(weight)
    return LEGACY_WEIGHT.get(last_rating) if last_rating else None


def next_weight(previous: float | None, rating: str) -> float:
    prev = NEUTRAL_WEIGHT if previous is None else float(previous)
    return round(0.5 * prev + 0.5 * RATING_TARGET[rating], 6)


def interval_days(weight: float | None) -> int:
    w = NEUTRAL_WEIGHT if weight is None else weight
    if w >= 0.75:
        return 1
    if w >= 0.5:
        return 3
    if w >= 0.25:
        return 7
    return 14


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def is_due(weight: float | None, last_reviewed_at: datetime | None, now: datetime) -> bool:
    if last_reviewed_at is None:
        return True
    elapsed = (_aware(now) - _aware(last_reviewed_at)).total_seconds() / 86400
    return elapsed >= interval_days(weight)


def queue_key(weight: float | None, last_reviewed_at: datetime | None, now: datetime, tiebreak: int | str = 0):
    """Nunca revisados → vencidos → demais; dentro de cada grupo, o mais pesado e depois o revisado há mais tempo."""
    if last_reviewed_at is None:
        return (0, 0.0, 0.0, tiebreak)
    w = NEUTRAL_WEIGHT if weight is None else weight
    stamp = _aware(last_reviewed_at).timestamp()
    if is_due(weight, last_reviewed_at, now):
        return (1, -w, stamp, tiebreak)
    return (2, -w, stamp, tiebreak)
