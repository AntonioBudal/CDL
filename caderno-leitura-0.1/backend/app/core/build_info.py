"""Identificação do build (F0.10.03): commit do código em execução e revisão de banco esperada.

O serviço roda pelo NSSM e pode não ter o `git` no PATH; por isso o commit vem de LEITORUM_BUILD_COMMIT ou da
leitura direta do .git (HEAD, ref solta, packed-refs ou HEAD destacado), sem processo externo.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_SEARCH_START = BACKEND_DIR
SHORT_LENGTH = 7
# O repositório fica 2 níveis acima de backend/ (caderno/ ← caderno-leitura-0.1/ ← backend/); subir mais acharia
# repositórios alheios (ex.: um .git na pasta do usuário).
MAX_PARENT_DEPTH = 3
_SHA = re.compile(r"^[0-9a-f]{7,64}$")


def _find_git_dir(start: Path) -> Path | None:
    for folder in (start, *list(start.parents)[:MAX_PARENT_DEPTH]):
        candidate = folder / ".git"
        if candidate.is_dir():
            return candidate
        if candidate.is_file():
            # Worktree ou submódulo: o arquivo .git aponta para a pasta real ("gitdir: <caminho>").
            content = candidate.read_text(encoding="utf-8", errors="replace").strip()
            if content.startswith("gitdir:"):
                target = Path(content.split(":", 1)[1].strip())
                target = target if target.is_absolute() else (folder / target)
                return target if target.is_dir() else None
    return None


def _resolve_ref(git_dir: Path, ref: str) -> str | None:
    loose = git_dir / ref
    if loose.is_file():
        return loose.read_text(encoding="utf-8", errors="replace").strip()
    packed = git_dir / "packed-refs"
    if packed.is_file():
        for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    return None


def read_build_commit(start: Path) -> str | None:
    """Commit curto (7 caracteres) do código a partir de ``start``, ou None quando não dá para saber."""
    configured = os.environ.get("LEITORUM_BUILD_COMMIT", "").strip().lower()
    if configured:
        return configured[:SHORT_LENGTH] if _SHA.match(configured) else None
    try:
        git_dir = _find_git_dir(start)
        if git_dir is None:
            return None
        head = (git_dir / "HEAD").read_text(encoding="utf-8", errors="replace").strip()
        sha = _resolve_ref(git_dir, head.split(":", 1)[1].strip()) if head.startswith("ref:") else head
    except OSError:
        return None
    sha = (sha or "").strip().lower()
    return sha[:SHORT_LENGTH] if _SHA.match(sha) else None


@lru_cache(maxsize=1)
def get_build_commit() -> str | None:
    """Commit do servidor em execução; o cache dura o processo, porque o código só muda com o reinício."""
    return read_build_commit(REPO_SEARCH_START)


def get_expected_schema_revisions() -> list[str]:
    """Cabeça(s) das migrações do código, lidas dos arquivos do Alembic (sem tocar no banco)."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    return sorted(ScriptDirectory.from_config(config).get_heads())
