"""EXP-044 — roda o ``train.py`` e o ``evaluate.py`` do EXP-031P, sem alterá-los, com os caminhos do
EXP-044. Ambiente do EXP-014 (``envs/ft``).

Uso:
    python run.py train --cond D1 [--steps 1568]
    python run.py evaluate --conds D1,D2
    python run.py amostra   # erro do leitor atual em 200 linhas de cada fonte nova
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HARNESS031 = Path(__file__).resolve().parents[2] / "EXP-031P-quais-fontes-ajudam/harness"
WORK = Path("D:/Leitorum-DI/trabalho/exp-044")
MODELS = Path("D:/Leitorum-DI/modelos/exp-044")


def configure(module, work: Path, models: Path) -> None:
    module.WORK = work
    module.MODELS = models


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"exp031p_{name}", HARNESS031 / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    configure(module, WORK, MODELS)
    return module


def amostra() -> int:
    evaluate = _load("evaluate")
    import torch

    torch.set_num_threads(4)
    evaluate.wait_ram(1.5e9)
    model, characters = evaluate.load()
    evaluate.freeze_batchnorm(model)
    out = {}
    for path in sorted((WORK / "amostras").glob("*.json")):
        items = json.loads(path.read_text(encoding="utf-8"))
        out[path.stem] = evaluate.measure(model, characters, items)
        print(path.stem, json.dumps(out[path.stem]), flush=True)
    (WORK / "amostras-c0.json").write_text(json.dumps(out, indent=1), "utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command, rest = argv[0], argv[1:]
    if command == "amostra":
        return amostra()
    return _load({"train": "train", "evaluate": "evaluate"}[command]).main(rest)


if __name__ == "__main__":
    raise SystemExit(main())
