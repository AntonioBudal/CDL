"""Aplicacao local do Caderno de Leitura."""
from __future__ import annotations

from pathlib import Path

# F0.12.01 (spec 114): fonte única da versão, no padrão SemVer 2.0.0 (``caderno-leitura-0.1/VERSION``).
_VERSION_FILE = Path(__file__).resolve().parents[2] / "VERSION"


def _read_version() -> str:
    try:
        text = _VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0-desconhecida"
    return text or "0.0.0-desconhecida"


__version__ = _read_version()
