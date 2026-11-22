"""EXP-043 — utilidades comuns da amostragem: acesso educado (User-Agent próprio, sem dado pessoal,
pausa entre requisições, sem contornar bloqueio), manifesto de procedência e medidas de linha.
Roda no ambiente do motor do produto (Pillow, NumPy)."""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

UA = "LeitorumDI-sampler/0.1 (non-commercial research; local handwriting recognition)"
ROOT = Path(os.environ.get("EXP043_ROOT") or "D:/Leitorum-DI/amostras/exp-043")
BUDGET_BYTES = 5 * 1024**3
PAUSE_S = 1.0
TARGET_HEIGHT = 64  # altura padronizada da linha no nosso formato
PT_ACCENTS = set("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ")

_last = [0.0]


class BlockedError(Exception):
    """A fonte recusou o acesso (403/429/desafio): não insistimos nem contornamos."""


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str, *, accept: str | None = None, timeout: int = 90, tries: int = 4) -> bytes:
    """GET educado; repete só erros temporários do servidor (5xx, rede), com espera crescente."""
    for attempt in range(tries):
        try:
            return _fetch_once(url, accept=accept, timeout=timeout)
        except urllib.error.HTTPError as error:
            if error.code < 500 or attempt == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(5 * (attempt + 1))
    raise RuntimeError("inalcançável")


def _fetch_once(url: str, *, accept: str | None, timeout: int) -> bytes:
    wait = PAUSE_S - (time.monotonic() - _last[0])
    if wait > 0:
        time.sleep(wait)
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=headers), timeout=timeout
        ) as r:
            body = r.read()
    except urllib.error.HTTPError as error:
        if error.code in (401, 403, 429):
            raise BlockedError(f"{error.code} {url}") from error
        raise
    finally:
        _last[0] = time.monotonic()
    if b"challenges.cloudflare.com" in body[:5000]:
        raise BlockedError(f"desafio {url}")
    return body


def fetch_json(url: str):
    return json.loads(fetch(url, accept="application/json"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def used_bytes() -> int:
    return sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file()) if ROOT.exists() else 0


def check_budget() -> None:
    if used_bytes() > BUDGET_BYTES:
        raise SystemExit(f"teto de amostras ({BUDGET_BYTES // 1024**3} GB) atingido em {ROOT}")


def store(source: str, data: bytes, suffix: str) -> Path:
    """Armazenamento por conteúdo: o nome é o SHA-256 (duplicata exata não ocupa espaço
    duas vezes)."""
    check_budget()
    digest = sha256(data)
    path = ROOT / source / "arquivos" / f"{digest}{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    return path


def record(source: str, entry: dict) -> None:
    path = ROOT / source / "manifesto.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"acquired_at": now(), **entry}, ensure_ascii=False) + "\n")


def save_terms(source: str, url: str) -> dict:
    """Cópia datada dos termos/licença da fonte (evidência), com hash."""
    try:
        body = fetch(url)
    except Exception as error:  # noqa: BLE001 — a falha também é evidência
        return {"terms_url": url, "terms_error": type(error).__name__}
    path = store(source, body, ".termos")
    return {"terms_url": url, "terms_sha256": path.stem, "terms_saved_at": now()}


def line_measures(image_bytes: bytes, text: str) -> dict:
    """Tamanho original e no nosso formato (cinza, altura 64 px, WebP sem perda); acentos do
    português."""
    from PIL import Image

    with Image.open(io.BytesIO(image_bytes)) as image:
        width, height = image.size
        gray = image.convert("L")
        new_width = max(1, round(width * TARGET_HEIGHT / max(1, height)))
        small = gray.resize((new_width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        small.save(out, "WEBP", lossless=True, method=6)
        lossy = io.BytesIO()
        small.save(lossy, "WEBP", quality=85, method=6)
    return {
        "width": width,
        "height": height,
        "bytes_original": len(image_bytes),
        "bytes_ours": len(out.getvalue()),
        "bytes_ours_lossy": len(lossy.getvalue()),
        "chars": len(text),
        "pt_accents": sum(1 for c in text if c in PT_ACCENTS),
        "usable": bool(text.strip()) and height >= 8 and width >= 16,
    }
