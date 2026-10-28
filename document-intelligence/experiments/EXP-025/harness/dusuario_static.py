"""EXP-025, F03 (H3): v1 contra v2, estáticos, nos estudos reais do usuário. Só números.

Reaproveita as travas do EXP-024 (``dusuario_continual``): a origem é aberta em ``mode=ro`` e
copiada pela API de backup para uma pasta temporária, apagada no fim; nenhum texto sai;
``check`` confere a saída. Todos os estudos elegíveis (pelo menos 2 seções) entram, sem histórico.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \\
        experiments/EXP-025/harness/dusuario_static.py --db "D:/Leitorum/db/caderno.db" --out <json>
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (HERE, EXPS / "EXP-023" / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))

import dusuario_continual as du  # noqa: E402  (EXP-024)
import metrics  # noqa: E402
import organizer as org  # noqa: E402
import organizer_v2 as v2  # noqa: E402

V1 = EXPS / "EXP-023" / "artifacts" / "organizer-v1.json"

ALLOWED = {
    "studies_total",
    "studies_eligible",
    "users",
    "v1",
    "v2",
    "gain_macro_f1",
} | du.ALLOWED_KEYS


def load_v1() -> org.Organizer:
    return org.Organizer(org.Model.from_json(json.loads(V1.read_text(encoding="utf-8"))))


def evaluate(studies: list[dict]) -> dict:
    engines = {"v1": load_v1(), "v2": v2.load()}
    scores = {name: metrics.Scores() for name in engines}
    eligible = [s for s in studies if sum(bool(v.strip()) for v in s["columns"].values()) >= 2]
    for study in eligible:
        text, labels, units = du.pseudo_page(study["columns"])
        for name, engine in engines.items():
            scores[name].add(text, labels, units, engine.organize(text))
    report = {
        "studies_total": len(studies),
        "studies_eligible": len(eligible),
        "users": len({s["user"] for s in studies}),
    }
    if eligible:
        for name in engines:
            report[name] = du.summarize(scores[name])
        report["gain_macro_f1"] = round(report["v2"]["macro_f1"] - report["v1"]["macro_f1"], 4)
    return report


def check(obj, path="") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key not in ALLOWED:
                raise ValueError(f"chave não permitida: {path}/{key}")
            check(value, f"{path}/{key}")
    elif not (obj is None or isinstance(obj, (int, float, bool))):
        raise ValueError(f"valor não numérico: {path}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    studies: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="exp025-dusuario-") as folder:
        copy = du.copy_database(Path(args.db), Path(folder))
        try:
            studies = du.load_studies(copy)
            report = evaluate(studies)
        finally:
            studies.clear()
            copy.unlink(missing_ok=True)
    check(report)
    text = json.dumps(report, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
