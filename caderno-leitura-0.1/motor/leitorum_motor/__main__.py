"""Linha de comando do motor (contrato ``motor-cli`` da feature 086).

``check``: confere bibliotecas, modelos e licença; ``read``: lê uma página e grava o JSON em ``--out``.
Códigos de saída: 0 ok, 2 imagem ilegível, 3 integridade/licença, 1 erro inesperado. O ``stderr`` traz
só o tipo da exceção, nunca texto lido.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXIT_OK, EXIT_ERROR, EXIT_IMAGE, EXIT_INTEGRITY = 0, 1, 2, 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="leitorum_motor", description="Motor de leitura do Leitorum")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Conferir ambiente, modelos e licença")
    check.add_argument("--config")
    read = commands.add_parser("read", help="Ler uma página")
    read.add_argument("--image", required=True)
    read.add_argument("--out", required=True)
    read.add_argument("--config")
    args = parser.parse_args(argv)

    try:
        from .pipeline import IntegrityError, PagePipeline, describe, load_config, verify

        config = load_config(args.config)
        if args.command == "check":
            verify(config)
            print(json.dumps({"ok": True, "engine": describe(config)}, ensure_ascii=False))
            return EXIT_OK
        result = PagePipeline(config).read(args.image)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        return EXIT_OK
    except IntegrityError:
        if args.command == "check":
            print(json.dumps({"ok": False, "reason": "integrity_failed"}))
        print("IntegrityError", file=sys.stderr)
        return EXIT_INTEGRITY
    except ValueError as error:
        print(type(error).__name__, file=sys.stderr)
        return EXIT_IMAGE
    except Exception as error:  # noqa: BLE001 — o backend só precisa do código e do tipo
        print(type(error).__name__, file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
