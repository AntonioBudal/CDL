"""EXP-044 — seleção determinística de linhas com cota igual por chave (documento na TraPrInq,
pessoa na BFL), reaproveitando a divisão de cotas do EXP-031P."""

from __future__ import annotations

import importlib.util
import random
import re
from collections import defaultdict
from pathlib import Path

_GROUPS = Path(__file__).resolve().parents[2] / "EXP-031P-quais-fontes-ajudam/harness/groups.py"
_spec = importlib.util.spec_from_file_location("exp031p_groups", _GROUPS)
groups = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(groups)


def by_key(rows: list[tuple[str, str]], size: int, seed: str) -> list[str]:
    """``rows`` = (item_id, chave). Cotas iguais por chave, limitadas ao que cada uma tem."""
    pools = defaultdict(list)
    for item_id, key in rows:
        pools[key].append(item_id)
    quota = groups.allocate(size, {k: len(v) for k, v in sorted(pools.items())})
    rng = random.Random(f"{seed}-{size}")
    chosen = []
    for key in sorted(pools):
        chosen += rng.sample(sorted(pools[key]), quota[key])
    return sorted(chosen)


def by_priority(rows: list[tuple[str, str, int]], size: int, seed: str) -> list[str]:
    """``rows`` = (item_id, chave, camada). Camadas menores primeiro, inteiras enquanto couberem; a
    camada que não cabe inteira é sorteada com cota igual por chave."""
    tiers = defaultdict(list)
    for item_id, key, tier in rows:
        tiers[tier].append((item_id, key))
    chosen: list[str] = []
    for tier in sorted(tiers):
        room = size - len(chosen)
        if room <= 0:
            break
        members = tiers[tier]
        if len(members) <= room:
            chosen += [item_id for item_id, _ in members]
        else:
            chosen += by_key(members, room, f"{seed}-camada{tier}")
    return sorted(chosen)


def century(document: str) -> int | None:
    """Século pelo primeiro ano entre parênteses no nome do documento da TraPrInq."""
    match = re.search(r"\((\d{4})", document)
    return int(match.group(1)) // 100 + 1 if match else None


def candidates(catalog, source_id: str, charset: set[str], statuses=("APPROVED",)):
    """(item_id, texto, id nativo) dos itens com arquivo e texto dentro do dicionário."""
    marks = ",".join("?" * len(statuses))
    rows = catalog.db.execute(
        f"SELECT item_id, text, native_id FROM items WHERE source_id = ? AND status IN ({marks})"
        " AND sha256 IS NOT NULL ORDER BY item_id",
        (source_id, *statuses),
    )
    return [(r[0], r[1], r[2]) for r in rows if groups.valid_text(r[1], charset)]
