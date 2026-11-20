"""T002 — sorteios do EXP-028A, gravados antes de qualquer medida e nunca refeitos:

* ``second-pass.json``: 5 das 20 páginas de teste para a 2ª passada **cega** (piso de ruído humano);
* ``dev-val-manifest.json``: 10 das 31 páginas de desenvolvimento como validação, que ficam fora
  de qualquer treino (anotação pendente até haver imagens).

Estratos escrita × fórmulas (as classes manuais do EXP-027), alocação do ``split.allocate`` do
EXP-027 e semente fixa. Só ids, classes e hashes vão para os arquivos.

Uso: ``python draws.py [--force]``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import UTC, datetime

import common
from split import allocate

STRATA = ("escrita", "formulas")
SECOND_PASS_SIZE = 5
DEV_VAL_SIZE = 10


def classes_of(pids: list[str]) -> dict[str, dict]:
    out = {}
    for pid in pids:
        path = common.CLASSIFICATION / f"{pid}.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            out[pid] = {key: data.get(key) for key in STRATA}
    return out


def draw(pids: list[str], size: int, salt: str) -> tuple[list[str], dict[str, dict]]:
    classes = classes_of(pids)
    if len(classes) != len(pids):
        raise SystemExit(f"faltam classes: {len(classes)} de {len(pids)}")
    groups: dict[tuple, list[str]] = defaultdict(list)
    for pid, data in classes.items():
        groups[tuple(data[key] for key in STRATA)].append(pid)
    chosen = allocate(groups, size, random.Random(f"{common.SEED}-{salt}"))
    return chosen, classes


def digest(ids: list[str]) -> str:
    return hashlib.sha256(",".join(sorted(ids)).encode()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sorteios do EXP-028A")
    parser.add_argument("--force", action="store_true", help="só para testes")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    test = json.loads((common.SPLITS / "test-manifest.json").read_text(encoding="utf-8"))
    targets = {
        "second-pass.json": (sorted(test["pages"]), SECOND_PASS_SIZE, "segunda-passada"),
        "dev-val-manifest.json": (sorted(test["dev_pages"]), DEV_VAL_SIZE, "dev-val"),
    }
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = {}
    for name, (pool, size, salt) in targets.items():
        target = common.SPLITS / name
        if target.is_file() and not args.force:
            report[name] = "já sorteado; nada feito"
            continue
        chosen, classes = draw(pool, size, salt)
        payload = {
            "schema": f"exp-028a-{salt}/1",
            "created_at": now,
            "created_by": "EXP-028A",
            "seed": f"{common.SEED}-{salt}",
            "strata": list(STRATA),
            "pool": len(pool),
            "size": len(chosen),
            "ids_sha256": digest(chosen),
            "pages": {pid: classes[pid] for pid in chosen},
        }
        if name == "second-pass.json":
            payload["mode"] = "cego"
            payload["min_days_after_pass1"] = 2
        else:
            payload["annotation"] = "pendente: sem imagens das páginas de desenvolvimento"
            payload["rule"] = "nunca entra em treino, limiar, dicionário ou ajuste de rascunho"
        common.SPLITS.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", "utf-8")
        report[name] = {"size": len(chosen), "pool": len(pool)}
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
