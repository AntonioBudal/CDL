"""Processo filho do benchmark: carrega um adaptador e reconhece as linhas do manifesto.

Roda dentro do ambiente isolado do candidato; usa só a biblioteca padrão e é compatível com
Python 3.10. Comunica-se com o supervisor por linhas JSON prefixadas na saída padrão.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import random
import sys
import time
from pathlib import Path

PREFIX = "@@EXP001 "


def emit(event: str, **fields: object) -> None:
    sys.stdout.write(PREFIX + json.dumps({"event": event, **fields}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Worker de reconhecimento do EXP-001")
    parser.add_argument("--adapter", required=True, help="modulo:Classe")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--options", default="{}")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")
    emit("start", pid=os.getpid(), python=sys.version.split()[0])

    random.seed(args.seed)
    root = Path(args.root)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    lines = manifest["lines"]

    module_name, class_name = args.adapter.split(":")
    recognizer = getattr(importlib.import_module(module_name), class_name)()

    started = time.perf_counter_ns()
    recognizer.load({"manifest": manifest, "root": str(root), "options": json.loads(args.options)})
    load_ms = (time.perf_counter_ns() - started) / 1e6
    emit("loaded", load_ms=load_ms, describe=recognizer.describe())

    for line in lines[: args.warmup]:
        recognizer.recognize(str(root / line["image"]))
    emit("warmup_done", lines=min(args.warmup, len(lines)))

    for line in lines:
        started = time.perf_counter_ns()
        text = recognizer.recognize(str(root / line["image"]))
        elapsed_ms = (time.perf_counter_ns() - started) / 1e6
        emit("line", id=line["id"], text=text, elapsed_ms=elapsed_ms)

    emit("done", lines=len(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
