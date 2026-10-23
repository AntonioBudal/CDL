"""Sorteio de páginas inteiras do treino (EXP-018)."""

from __future__ import annotations

import random


def page_of(item_id: str) -> str:
    """``0214-006-01-01`` → ``0214-006`` (página do BRESSAY)."""
    return "-".join(item_id.split("-")[:2])


def pick_pages(items: list[dict], pages: int, seed: int) -> list[dict]:
    """Todas as linhas de ``pages`` páginas sorteadas (ordem dos itens preservada).

    Com a mesma semente, os sorteios são encaixados: as páginas de um ponto menor da curva estão
    todas no ponto maior.
    """
    names = sorted({page_of(it["id"]) for it in items})
    if pages >= len(names):
        return list(items)
    random.Random(seed).shuffle(names)
    chosen = set(names[:pages])
    return [it for it in items if page_of(it["id"]) in chosen]
