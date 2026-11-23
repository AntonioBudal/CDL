"""EXP-031P — monta as listas de treino de cada condição (pelo catálogo, com o ciclo registrado) e
os conjuntos de medida (BRESSAY teste, GNHK teste, 62 linhas do autor). Ambiente do subprojeto.

Uso: ``python prepare.py``
"""

from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import groups
from PIL import Image

from tools.catalogo import Catalog

DI_MAIN = Path("C:/Users/User/caderno/document-intelligence")
WORK = Path("D:/Leitorum-DI/trabalho/exp-031p")
SEED = "exp-031p"
BRESSAY_TEST_SIZE = 2000
AUTHOR_PAGES = ("p10", "p11", "p14", "p15")  # p16 fora: imagem é uma faixa da página (EXP-028A)
SIZES = {
    "C1": {"A": 8000},
    "C2": {"B": 8000},
    "C3": {"S": 8000},
    "C4": {"A": 4000, "S": 4000},
    "C5": {"A": 2667, "B": 2667, "S": 2666},
}


def commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
            check=False,
        ).stdout.strip()
    except OSError:
        return "?"


def synthetic(size: int) -> list[dict]:
    data = json.loads((WORK / "sintetico.json").read_text(encoding="utf-8"))
    items = data["items"]
    rng = random.Random(f"{SEED}-S-{size}")
    return sorted(rng.sample(items, size), key=lambda i: i["id"])


def clean_author(text: str) -> str:
    return " ".join(text.replace("[?]", "").replace("$", "").split())


def author_lines(out: Path) -> list[dict]:
    """62 linhas do autor: recorte da caixa (512 px) e o texto da 1ª passada, sem as marcas."""
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for pid in AUTHOR_PAGES:
        doc = json.loads((DI_MAIN / "dataset/raw/anotacao" / f"{pid}.json").read_text("utf-8"))
        with Image.open(DI_MAIN / "dataset/processed/anotacao/imagens" / f"{pid}.jpg") as image:
            for line in sorted(doc["lines"], key=lambda ln: ln["order"]):
                xs = [p[0] for p in line["polygon"]]
                ys = [p[1] for p in line["polygon"]]
                box = (int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1)
                path = out / f"{pid}-{line['line_id']}.png"
                image.crop(box).convert("L").save(path)
                items.append(
                    {
                        "id": f"{pid}:{line['line_id']}",
                        "image": str(path),
                        "text": clean_author(line["pass1"]["text"]),
                    }
                )
    return items


def repeat(spec: str) -> int:
    """Repete uma condição já preparada com outra semente de treino (regra de ruído do plano):
    mesma lista, ciclo novo no catálogo. ``spec`` = ``C1:4321`` → lista ``C1-s4321``."""
    condition, seed = spec.split(":")
    name = f"{condition}-s{seed}"
    path = WORK / "preparo.json"
    prepared = json.loads(path.read_text(encoding="utf-8"))
    original = prepared["runs"][condition]
    cat = Catalog()
    try:
        item_ids = [row["item_id"] for row in cat.run_items(original)]
        run_id = cat.start_run(
            "experimento",
            item_ids=item_ids or None,
            recipe=f"exp-031p 392 passos x 16, lr 5e-5, margem 640, semente {seed}",
            commit=commit(),
            seed=int(seed),
            notes=f"EXP-031P {name}: repetição de {condition} ({original}) com outra semente",
        )
    finally:
        cat.close()
    lists = WORK / "listas"
    (lists / f"{name}.json").write_bytes((lists / f"{condition}.json").read_bytes())
    prepared["runs"][name] = run_id
    prepared[name] = {**prepared[condition], "run_id": run_id, "seed": int(seed)}
    path.write_text(json.dumps(prepared, indent=2), "utf-8")
    print(json.dumps({name: prepared[name]}, indent=1))
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--so-medida", action="store_true", help="só os conjuntos de medida")
    parser.add_argument("--conds", default=",".join(SIZES), help="condições a preparar")
    parser.add_argument("--repetir", help="repete uma condição com outra semente (ex.: C1:4321)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.repetir:
        return repeat(args.repetir)
    charset = groups.load_charset(WORK / "charset.json")
    lists, evals = WORK / "listas", WORK / "medida"
    lists.mkdir(parents=True, exist_ok=True)
    evals.mkdir(parents=True, exist_ok=True)
    cat = Catalog()
    runs, report = {}, {}
    try:
        wanted = [] if args.so_medida else args.conds.split(",")
        for condition, parts in ((c, SIZES[c]) for c in wanted):
            items, item_ids, quotas, synthetic_count = [], [], {}, 0
            for group, size in parts.items():
                if group == "S":
                    chosen = synthetic(size)
                    synthetic_count = len(chosen)
                    items += [
                        {"id": c["id"], "image": c["image"], "text": c["text"]} for c in chosen
                    ]
                    continue
                ids, quota = groups.select(cat, group, size, charset, SEED)
                quotas[group] = quota
                item_ids += ids
                for item_id in ids:
                    row = cat.item(item_id)
                    items.append(
                        {
                            "id": item_id,
                            "image": str(cat.file_path(row["sha256"])),
                            "text": row["text"],
                        }
                    )
            notes = (
                f"EXP-031P {condition}: {len(item_ids)} linhas do catálogo + {synthetic_count}"
                " sintéticas (synth.py, semente exp-031p-sintetico; amostra semente"
                f" {SEED}-S-{synthetic_count})"
            )
            run_id = cat.start_run(
                "experimento",
                item_ids=item_ids or None,
                recipe="exp-031p 392 passos x 16, lr 5e-5, margem 640, semente 1234",
                commit=commit(),
                seed=1234,
                notes=notes,
            )
            runs[condition] = run_id
            (lists / f"{condition}.json").write_text(json.dumps(items, ensure_ascii=False), "utf-8")
            report[condition] = {
                "lines": len(items),
                "catalog": len(item_ids),
                "synthetic": synthetic_count,
                "quotas": quotas,
                "run_id": run_id,
            }
    finally:
        cat.close()
    bressay = json.loads((DI_MAIN / "dataset/processed/exp-014/test-all.json").read_text("utf-8"))
    rng = random.Random(f"{SEED}-bressay")
    bressay = sorted(rng.sample(bressay, BRESSAY_TEST_SIZE), key=lambda i: i["id"])
    gnhk_pages = json.loads(
        (DI_MAIN / "dataset/processed/exp-009/lines-gnhk-worker.json").read_text("utf-8")
    )["pages"]
    gnhk_refs = json.loads(
        (DI_MAIN / "dataset/processed/exp-009/lines-gnhk-refs.json").read_text("utf-8")
    )["refs"]
    sets = {
        "bressay": [
            {"id": i["id"], "image": str(DI_MAIN / i["image"]), "text": i["text"]} for i in bressay
        ],
        "gnhk": [
            {"id": p["id"], "image": str(DI_MAIN / p["image"]), "text": gnhk_refs[p["id"]]}
            for p in gnhk_pages
            if p["id"] in gnhk_refs
        ],
        "autor": author_lines(evals / "autor"),
    }
    for name, content in sets.items():
        (evals / f"{name}.json").write_text(json.dumps(content, ensure_ascii=False), "utf-8")
    report["eval"] = {k: len(v) for k, v in sets.items()}
    if not args.so_medida:  # acumula: condições preparadas em rodadas diferentes
        path = WORK / "preparo.json"
        previous = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"runs": {}}
        previous["runs"].update(runs)
        previous.update(report)
        path.write_text(json.dumps(previous, indent=2), "utf-8")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
