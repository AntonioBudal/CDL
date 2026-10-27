"""Motor falso para os testes da feature 086: segue o contrato ``motor-cli`` sem bibliotecas pesadas.

Modo em ``FAKE_MOTOR_MODE``: ok, empty, uncertain, slow, crash, bad_schema, integrity, unreadable.
Se ``FAKE_MOTOR_TRACE`` estiver definido, grava ali a pasta e o tamanho da imagem recebida, para os
testes conferirem orientação e limpeza. Textos sempre fictícios.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

ENGINE = {
    "name": "leitorum-motor",
    "version": "0.0.0-teste",
    "detector": "falso",
    "reader": "Leitor de Teste",
    "reader_sha256": "0" * 64,
    "license_status": "VERIFIED",
}
LINES = {
    "ok": [("Capítulo 1 do Livro de Teste", 0.95), ("linha fictícia incerta", 0.42)],
    "empty": [],
    "uncertain": [("linha um", 0.30), ("linha dois", 0.40), ("linha três", 0.97)],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--image")
    parser.add_argument("--out")
    parser.add_argument("--config")
    args = parser.parse_args()
    mode = os.environ.get("FAKE_MOTOR_MODE", "ok")

    if args.command == "check":
        if mode == "integrity":
            print(json.dumps({"ok": False, "reason": "integrity_failed"}))
            return 3
        print(json.dumps({"ok": True, "engine": ENGINE}))
        return 0

    trace = os.environ.get("FAKE_MOTOR_TRACE")
    if trace:
        from PIL import Image

        with Image.open(args.image) as image:
            size = list(image.size)
        Path(trace).write_text(json.dumps({"workdir": str(Path(args.image).parent), "size": size, "pid": os.getpid()}))
    if mode == "slow":
        time.sleep(60)
    if mode == "crash":
        print("RuntimeError", file=sys.stderr)
        return 1
    if mode == "integrity":
        return 3
    if mode == "unreadable":
        return 2
    if mode == "bad_schema":
        Path(args.out).write_text(json.dumps({"schema": "outro/9"}))
        return 0
    result = {
        "schema": "leitorum-motor/1",
        "image": {"width": 10, "height": 10},
        "lines": [{"text": text, "confidence": conf, "bbox": [0, 0, 10, 10]} for text, conf in LINES[mode]],
        "page_scale": 1,
        "engine": ENGINE,
        "elapsed_ms": 1,
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
