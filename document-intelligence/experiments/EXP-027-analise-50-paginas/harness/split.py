"""T002 — sorteio estratificado do conjunto de teste congelado (~20 páginas), com semente fixa, a
partir da classificação manual (escrita × fórmulas × foto). Grava ``splits/test-manifest.json``
(versionado: ids, SHA-256 e categorias) e recusa-se a rodar de novo se o manifesto já existir, para
que o teste não mude.

Uso: ``python split.py [--size 20] [--seed exp-027] [--force]``
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from datetime import UTC, datetime

from paths import CLASSIFICATION, MANIFEST, SPLITS

STRATA = ("escrita", "formulas", "foto")


def load_classes(pages: dict) -> dict[str, dict]:
    out = {}
    for pid in pages:
        path = CLASSIFICATION / f"{pid}.json"
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if all(data.get(key) for key in STRATA):
            out[pid] = {
                key: data[key] for key in ("escrita", "formulas", "foto", "papel", "layout")
            }
    return out


def allocate(groups: dict[tuple, list[str]], size: int, rng: random.Random) -> list[str]:
    """Pelo menos 1 por estrato não vazio; o resto proporcional (maiores restos)."""
    total = sum(len(v) for v in groups.values())
    size = min(size, total)
    keys = sorted(groups)
    quota = dict.fromkeys(keys, 1)
    remaining = size - len(keys)
    if remaining < 0:  # mais estratos que vagas: os maiores estratos ficam
        keys = sorted(keys, key=lambda k: -len(groups[k]))[:size]
        quota = dict.fromkeys(keys, 1)
        remaining = 0
    shares = {k: len(groups[k]) / total * (size - len(keys)) for k in keys}
    for k in keys:
        extra = min(int(shares[k]), len(groups[k]) - 1)
        quota[k] += extra
        remaining -= extra
    for k in sorted(keys, key=lambda k: -(shares[k] - int(shares[k]))):
        if remaining <= 0:
            break
        if quota[k] < len(groups[k]):
            quota[k] += 1
            remaining -= 1
    chosen = []
    for k in keys:
        chosen.extend(rng.sample(sorted(groups[k]), quota[k]))
    return sorted(chosen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Conjunto de teste congelado do EXP-027")
    parser.add_argument("--size", type=int, default=20)
    parser.add_argument("--seed", default="exp-027")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    target = SPLITS / "test-manifest.json"
    if target.is_file() and not args.force:
        print("o conjunto de teste já está congelado; nada feito")
        return 0
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    classes = load_classes(manifest["pages"])
    if len(classes) < len(manifest["pages"]):
        print(f"faltam classificações: {len(classes)} de {len(manifest['pages'])}")
        return 1
    groups: dict[tuple, list[str]] = defaultdict(list)
    for pid, data in classes.items():
        groups[tuple(data[key] for key in STRATA)].append(pid)
    rng = random.Random(args.seed)
    chosen = allocate(groups, args.size, rng)
    split = {
        "schema": "exp-027-test-split/1",
        "created_at": datetime.now(UTC).isoformat(),
        "seed": args.seed,
        "strata": list(STRATA),
        "size": len(chosen),
        "pages": {
            pid: {"sha256": manifest["pages"][pid]["sha256"], **classes[pid]} for pid in chosen
        },
        "dev_pages": sorted(set(manifest["pages"]) - set(chosen)),
        "strata_counts": {
            " × ".join(k): {"total": len(v), "test": sum(1 for p in v if p in chosen)}
            for k, v in sorted(groups.items())
        },
    }
    SPLITS.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(split, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"test": len(chosen), "dev": len(split["dev_pages"]), "strata": len(groups)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
