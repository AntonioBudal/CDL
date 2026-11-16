"""T005a — sobe o ``llama-server`` local com a cópia exata guardada do VLM, depois de conferir o
SHA-256 de cada arquivo contra o ``MODEL.json`` da cópia (como o motor do produto faz). Só em
127.0.0.1. O processo fica em primeiro plano até Ctrl+C.

Uso: ``python vlm_server.py --copy <models/exp-027/qwen3-vl-4b> [--port 8080] [--ctx 6144]
[--threads 4]``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from paths import DATA_ROOT

MODELS = DATA_ROOT.parent / "models" / "exp-027"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(copy: Path) -> dict:
    """Confere os arquivos listados no ``MODEL.json``; levanta ``SystemExit`` se algo não bate."""
    meta = json.loads((copy / "MODEL.json").read_text(encoding="utf-8"))
    for item in meta["files"]:
        path = copy / item["file"]
        if not path.is_file():
            raise SystemExit(f"arquivo ausente: {item['file']}")
        if sha256(path) != item["sha256"]:
            raise SystemExit(f"SHA-256 não confere: {item['file']}")
    return meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="llama-server local para o baseline do EXP-027")
    parser.add_argument("--copy", default=str(MODELS / "qwen3-vl-4b"))
    parser.add_argument("--llama", default=str(MODELS / "llama.cpp-b12444"))
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--ctx", type=int, default=6144)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    copy = Path(args.copy)
    meta = verify(copy)
    model = next(copy / f["file"] for f in meta["files"] if f["role"] == "model")
    mmproj = next(copy / f["file"] for f in meta["files"] if f["role"] == "mmproj")
    server = Path(args.llama) / "llama-server.exe"
    if not server.is_file():
        raise SystemExit(f"llama-server ausente em {server}")
    command = [
        str(server),
        "-m",
        str(model),
        "--mmproj",
        str(mmproj),
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
        "-c",
        str(args.ctx),
        "-t",
        str(args.threads),
        "--temp",
        "0",
    ]
    revision = meta["source"]["revision"][:8]
    print(f"{meta['name']} ({revision}) em http://127.0.0.1:{args.port}/", flush=True)
    return subprocess.call(command, cwd=str(server.parent))


if __name__ == "__main__":
    raise SystemExit(main())
