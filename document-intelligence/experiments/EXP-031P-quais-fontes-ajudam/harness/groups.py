"""EXP-031P — composição dos grupos de treino: cotas por fonte (iguais, limitadas ao que a fonte
tem, sobra para as maiores, teto por fonte) e seleção determinística das linhas no catálogo,
descartando as que têm caractere fora do dicionário do leitor."""

from __future__ import annotations

import json
import random
from pathlib import Path

PER_GROUP = 8000
GROUPS = {
    "A": [
        "teklia-rimes-2011",
        "htru-moonshines",
        "htru-cremma-mss-20",
        "htru-dataset-celestine-doniau-danest",
        "htru-lectaurep-repertoires",
        "teklia-belfort",
        "teklia-popp",
        "teklia-norhand-v2",
    ],
    "B": [
        "teklia-home-alcar",
        "teklia-himanis",
        "htru-cremma-medieval",
        "htru-iforal-dataset",
    ],
}
MAX_SHARE = {"teklia-norhand-v2": 0.40}
# Volume disponível na fonte (EXP-043, divisão de treino ou catálogo do HTR-United).
AVAILABLE = {
    "teklia-rimes-2011": 10188,
    "htru-moonshines": 1016,
    "htru-cremma-mss-20": 224,
    "htru-dataset-celestine-doniau-danest": 144,
    "htru-lectaurep-repertoires": 29410,
    "teklia-belfort": 25800,
    "teklia-popp": 3835,
    "teklia-norhand-v2": 145009,
    "teklia-home-alcar": 59969,
    "teklia-himanis": 18504,
    "htru-cremma-medieval": 22848,
    "htru-iforal-dataset": 8009,
}
CONDITIONS = {
    "C1": {"A": 1.0},
    "C2": {"B": 1.0},
    "C3": {"S": 1.0},
    "C4": {"A": 0.5, "S": 0.5},
    "C5": {"A": 1 / 3, "B": 1 / 3, "S": 1 / 3},
}


def allocate(total: int, available: dict[str, int], max_share: dict[str, float] | None = None):
    """Cotas iguais, limitadas ao disponível e ao teto de cada fonte; a sobra vai para as que ainda
    têm espaço, das maiores para as menores, até fechar o total (ou acabar o disponível)."""
    max_share = max_share or {}
    caps = {s: min(n, int(total * max_share.get(s, 1.0))) for s, n in available.items()}
    quota = dict.fromkeys(caps, 0)
    remaining = total
    while remaining > 0:
        open_sources = [s for s in caps if quota[s] < caps[s]]
        if not open_sources:
            break
        share = max(1, remaining // len(open_sources))
        progressed = 0
        for source in sorted(open_sources, key=lambda s: -caps[s]):
            add = min(share, caps[source] - quota[source], remaining - progressed)
            quota[source] += add
            progressed += add
            if progressed >= remaining:
                break
        remaining -= progressed
        if progressed == 0:
            break
    return quota


def valid_text(text: str | None, charset: set[str]) -> bool:
    return bool(text and text.strip()) and all(c in charset for c in text)


def load_charset(path: Path) -> set[str]:
    return set(json.loads(path.read_text(encoding="utf-8"))["characters"])


def candidates(catalog, source_id: str, charset: set[str]) -> list[str]:
    """Itens aprovados com arquivo e texto válido, na ordem do id (a seleção sorteia depois)."""
    rows = catalog.db.execute(
        "SELECT item_id, text FROM items WHERE source_id = ? AND status = 'APPROVED'"
        " AND sha256 IS NOT NULL ORDER BY item_id",
        (source_id,),
    )
    return [r[0] for r in rows if valid_text(r[1], charset)]


def select(catalog, group: str, size: int, charset: set[str], seed: str) -> tuple[list[str], dict]:
    """Seleção determinística de ``size`` linhas do grupo, pelas cotas."""
    sources = GROUPS[group]
    pools = {s: candidates(catalog, s, charset) for s in sources}
    quota = allocate(size, {s: len(pools[s]) for s in sources}, MAX_SHARE)
    rng = random.Random(f"{seed}-{group}-{size}")
    chosen = []
    for source in sources:
        chosen += rng.sample(pools[source], quota[source])
    return sorted(chosen), quota
