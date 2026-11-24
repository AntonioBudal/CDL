"""EXP-044 — monta as listas D1–D4 pelo catálogo (cada uma é um ciclo ``experimento``), as amostras
de 200 linhas de cada fonte nova (erro do leitor atual) e copia as medidas do EXP-031P. Ambiente do
subprojeto, PYTHONPATH no ``document-intelligence/``.

Uso: ``python prepare.py``
"""

from __future__ import annotations

import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pick

from tools.catalogo import Catalog

WORK = Path("D:/Leitorum-DI/trabalho/exp-044")
WORK031 = Path("D:/Leitorum-DI/trabalho/exp-031p")
SEED = "exp-044"
RECIPE = "exp-044 {steps} passos x 16, lr 5e-5, margem 640, semente 1234"
SIZES = {
    "D1": {"zenodo-traprinq": 8000},
    "D2": {"ufpr-bfl": 8000},
    "D3": {"zenodo-traprinq": 3000, "ufpr-bfl": 3000, "S": 2000},
}
SAMPLE = 200


def commit() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=False
    )
    return out.stdout.strip() or "?"


def pool(cat, source_id: str, charset: set[str]) -> list[dict]:
    statuses = ("APPROVED", "EXPERIMENT_ONLY")
    rows = cat.db.execute(
        "SELECT item_id, text, writer, extra, sha256 FROM items WHERE source_id = ?"
        " AND status IN (?, ?) AND sha256 IS NOT NULL ORDER BY item_id",
        (source_id, *statuses),
    )
    out = []
    for item_id, text, writer, extra, sha in rows:
        if not pick.groups.valid_text(text, charset):
            continue
        document = (json.loads(extra) if extra else {}).get("document")
        out.append({"id": item_id, "text": text, "writer": writer, "doc": document, "sha": sha})
    return out


def choose(cat, source_id: str, size: int, charset: set[str]) -> list[str]:
    rows = pool(cat, source_id, charset)
    if source_id == "zenodo-traprinq":
        tier = {18: 0, 19: 0, 17: 1}
        return pick.by_priority(
            [(r["id"], r["doc"], tier.get(pick.century(r["doc"] or ""), 2)) for r in rows],
            size,
            f"{SEED}-{source_id}",
        )
    return pick.by_key([(r["id"], r["writer"]) for r in rows], size, f"{SEED}-{source_id}")


def entries(cat, item_ids: list[str]) -> list[dict]:
    out = []
    for item_id in item_ids:
        row = cat.item(item_id)
        out.append({"id": item_id, "image": str(cat.file_path(row["sha256"])), "text": row["text"]})
    return out


def synthetic(size: int) -> list[dict]:
    items = json.loads((WORK031 / "sintetico.json").read_text(encoding="utf-8"))["items"]
    chosen = random.Random(f"{SEED}-S-{size}").sample(items, size)
    return [{"id": c["id"], "image": c["image"], "text": c["text"]} for c in chosen]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    charset = pick.groups.load_charset(WORK031 / "charset.json")
    (WORK / "listas").mkdir(parents=True, exist_ok=True)
    (WORK / "amostras").mkdir(exist_ok=True)
    shutil.copytree(WORK031 / "medida", WORK / "medida", dirs_exist_ok=True)
    report = {"runs": {}}
    cat = Catalog()
    try:
        for source_id in ("zenodo-traprinq", "ufpr-bfl"):
            rows = pool(cat, source_id, charset)
            sample = random.Random(f"{SEED}-amostra-{source_id}").sample(rows, SAMPLE)
            (WORK / "amostras" / f"{source_id}.json").write_text(
                json.dumps(entries(cat, sorted(r["id"] for r in sample)), ensure_ascii=False),
                "utf-8",
            )
            report[f"disponivel:{source_id}"] = len(rows)
        for condition, parts in SIZES.items():
            items, item_ids, counts = [], [], {}
            for source_id, size in parts.items():
                if source_id == "S":
                    chosen = synthetic(size)
                    items += chosen
                    counts["S"] = len(chosen)
                    continue
                ids = choose(cat, source_id, size, charset)
                item_ids += ids
                items += entries(cat, ids)
                counts[source_id] = len(ids)
            run_id = cat.start_run(
                "experimento",
                item_ids=item_ids,
                recipe=RECIPE.format(steps=392),
                commit=commit(),
                seed=1234,
                notes=f"EXP-044 {condition}: {counts}",
            )
            (WORK / "listas" / f"{condition}.json").write_text(
                json.dumps(items, ensure_ascii=False), "utf-8"
            )
            report["runs"][condition] = run_id
            report[condition] = {"lines": len(items), "parts": counts, "run_id": run_id}
        # D4: a mesma lista do C4 do EXP-031P, com 4× o orçamento.
        prepared031 = json.loads((WORK031 / "preparo.json").read_text(encoding="utf-8"))
        c4_ids = [r["item_id"] for r in cat.run_items(prepared031["runs"]["C4"])]
        run_id = cat.start_run(
            "experimento",
            item_ids=c4_ids,
            recipe=RECIPE.format(steps=1568),
            commit=commit(),
            seed=1234,
            notes=f"EXP-044 D4: lista do C4 do EXP-031P ({prepared031['runs']['C4']}), 4× passos",
        )
        shutil.copyfile(WORK031 / "listas" / "C4.json", WORK / "listas" / "D4.json")
        report["runs"]["D4"] = run_id
        report["D4"] = {"lines": 8000, "parts": {"C4": 8000}, "run_id": run_id}
    finally:
        cat.close()
    (WORK / "preparo.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
