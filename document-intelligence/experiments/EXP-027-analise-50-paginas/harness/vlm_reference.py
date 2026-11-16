"""T005 — referência com um modelo visão-linguagem local (``llama.cpp`` + GGUF), em CPU.

Fala com um ``llama-server`` já em execução (API compatível com OpenAI, só em 127.0.0.1), manda
cada página como imagem e um prompt fixo, e grava ``processed/exp-027/<system>/pNN.json`` no mesmo
formato de linhas que o motor (uma linha de texto por linha devolvida; sem caixas). Retomável e
com espera de RAM: antes de cada página confere a memória disponível e espera se estiver abaixo
do mínimo. O prompt é fixo e foi escrito **antes** de qualquer página de teste ser vista.

Uso: ``python vlm_reference.py --system qwen3-vl-4b [--url http://127.0.0.1:8080]
[--min-free-mb 1500] [--max-side 1600]``
"""

from __future__ import annotations

import argparse
import base64
import ctypes
import json
import sys
import time
from datetime import UTC, datetime
from io import BytesIO
from urllib import request

from paths import MANIFEST, PHOTOS, PROCESSED

PROMPT = (
    "Transcreva fielmente todo o texto manuscrito desta página de caderno, em português, "
    "uma linha de texto por linha de saída, na ordem natural de leitura (de cima para baixo, "
    "esquerda para a direita). Mantenha acentos, maiúsculas e pontuação como estão escritos. "
    "Escreva fórmulas e símbolos matemáticos em LaTeX simples entre cifrões, por exemplo $x^2+1$. "
    "Para um desenho, diagrama ou tabela que não seja texto, escreva [figura] numa linha. "
    "Para um trecho ilegível, escreva [?]. Não explique, não resuma, não traduza, não corrija: "
    "devolva apenas a transcrição."
)


def available_mb() -> float | None:
    """Memória comprometível disponível no Windows (MB), como no serviço do Leitorum."""
    if sys.platform != "win32":
        return None

    class Status(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = Status()
    status.dwLength = ctypes.sizeof(Status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return status.ullAvailPhys / (1024 * 1024)


def encode_image(path, pid: str, max_side: int) -> str:
    from PIL import Image, ImageOps

    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        w, h = image.size
        factor = min(1.0, max_side / max(w, h))
        if factor < 1:
            image = image.resize((round(w * factor), round(h * factor)), Image.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, "JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def ask(url: str, image_b64: str, temperature: float, max_tokens: int) -> dict:
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = request.Request(
        f"{url}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=3600) as response:  # noqa: S310 — só 127.0.0.1
        return json.loads(response.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Referência VLM local do EXP-027")
    parser.add_argument("--system", required=True, help="nome da pasta de saída, ex.: qwen3-vl-4b")
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--min-free-mb", type=float, default=1500)
    parser.add_argument("--max-side", type=int, default=1600)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--only", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if not args.url.startswith(("http://127.0.0.1", "http://localhost")):
        print("só servidores locais são permitidos")
        return 2
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out_dir = PROCESSED / args.system
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(args.only.split(",")) if args.only else None
    runs_path = out_dir / "_runs.json"
    runs = json.loads(runs_path.read_text(encoding="utf-8")) if runs_path.is_file() else {}
    for pid, page in manifest["pages"].items():
        if wanted and pid not in wanted:
            continue
        target = out_dir / f"{pid}.json"
        if target.is_file() and not args.force:
            continue
        while (free := available_mb()) is not None and free < args.min_free_mb:
            print(
                f"{pid}: esperando RAM ({free:.0f} MB livres < {args.min_free_mb:.0f})", flush=True
            )
            time.sleep(60)
        started = time.perf_counter()
        source = PHOTOS / page["file"]
        if source.suffix.lower() in {".heic", ".heif"}:
            source = PROCESSED / "fotos-png" / f"{pid}.png"
        image_b64 = encode_image(source, pid, args.max_side)
        try:
            answer = ask(args.url, image_b64, args.temperature, args.max_tokens)
        except Exception as error:  # noqa: BLE001 — registra e segue
            runs[pid] = {"error": type(error).__name__, "at": datetime.now(UTC).isoformat()}
            runs_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
            print(f"{pid}: erro {type(error).__name__}", flush=True)
            continue
        text = answer["choices"][0]["message"]["content"]
        lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n") if line.strip()]
        usage = answer.get("usage", {})
        elapsed = round(time.perf_counter() - started, 1)
        target.write_text(
            json.dumps(
                {
                    "schema": "exp-027-vlm/1",
                    "system": args.system,
                    "model": answer.get("model"),
                    "prompt_sha256": __import__("hashlib").sha256(PROMPT.encode()).hexdigest(),
                    "max_side": args.max_side,
                    "temperature": args.temperature,
                    "lines": [{"text": line, "confidence": None, "bbox": None} for line in lines],
                    "usage": usage,
                    "elapsed_s": elapsed,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        runs[pid] = {"elapsed_s": elapsed, "tokens": usage, "at": datetime.now(UTC).isoformat()}
        runs_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
        print(f"{pid}: {len(lines)} linhas em {elapsed} s", flush=True)
    done = sum(1 for pid in manifest["pages"] if (out_dir / f"{pid}.json").is_file())
    print(json.dumps({"pages": len(manifest["pages"]), "read": done}))
    return 0 if done == len(manifest["pages"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
