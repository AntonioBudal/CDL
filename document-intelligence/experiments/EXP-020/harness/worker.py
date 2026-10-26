"""Processo filho do benchmark de layout: carrega um adaptador e processa as páginas do manifesto.

Derivado do worker do EXP-001 (cópia do EXP-003). A falha de uma página é contada, não fatal. Roda
dentro do ambiente isolado do candidato; usa só a biblioteca
padrão e é compatível com Python 3.10. Comunica-se com o supervisor por linhas JSON prefixadas.
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

PREFIX = "@@EXP020 "


def emit(event: str, **fields: object) -> None:
    sys.stdout.write(PREFIX + json.dumps({"event": event, **fields}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Worker do EXP-020")
    parser.add_argument("--adapter", required=True, help="modulo:Classe")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--options", default="{}")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args(argv)

    sys.stdout.reconfigure(encoding="utf-8")
    emit("start", pid=os.getpid(), python=sys.version.split()[0])

    random.seed(args.seed)
    root = Path(args.root)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    pages = manifest["pages"]

    module_name, class_name = args.adapter.split(":")
    recognizer = getattr(importlib.import_module(module_name), class_name)()

    started = time.perf_counter_ns()
    recognizer.load({"manifest": manifest, "root": str(root), "options": json.loads(args.options)})
    load_ms = (time.perf_counter_ns() - started) / 1e6
    emit("loaded", load_ms=load_ms, describe=recognizer.describe())

    for page in pages[: args.warmup]:
        recognizer.predict(str(root / page["image"]))
    emit("warmup_done", pages=min(args.warmup, len(pages)))

    for page in pages:
        started = time.perf_counter_ns()
        try:
            result = recognizer.predict(str(root / page["image"]))
        except Exception as error:  # noqa: BLE001 - a falha de uma página é contada, não fatal
            result = {"lines": [], "blocks": [], "error": f"{type(error).__name__}: {error}"[:200]}
        elapsed_ms = (time.perf_counter_ns() - started) / 1e6
        emit("page", id=page["id"], result=result, elapsed_ms=elapsed_ms)

    emit("done", pages=len(pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
