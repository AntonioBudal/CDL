"""Trava do servidor (feature 090-A): ``leitorum.lock`` existe enquanto o Leitorum está rodando.

O script de migração para o HD exige o servidor parado; a trava, junto da porta livre, é a prova. Uma
trava cujo processo já não existe (queda, desligamento brusco) é tratada como velha e ignorada.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[3]
LOCK_PATH = PROJECT_DIR / "leitorum.lock"


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def read_lock(path: Path = LOCK_PATH) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def active_lock(path: Path = LOCK_PATH) -> dict | None:
    """Conteúdo da trava se o processo dono ainda estiver vivo; ``None`` se não houver trava válida."""
    data = read_lock(path)
    if not data:
        return None
    try:
        pid = int(data.get("pid", 0))
    except (TypeError, ValueError):
        return None
    return data if process_alive(pid) else None


def acquire(port: int, path: Path = LOCK_PATH) -> None:
    """Cria a trava; recusa se outra instância viva já a tiver."""
    current = active_lock(path)
    if current and int(current.get("pid", 0)) != os.getpid():
        raise RuntimeError("Outra janela do Leitorum já está em execução.")
    body = {"pid": os.getpid(), "port": port, "started_at": datetime.now(UTC).isoformat(timespec="seconds")}
    path.write_text(json.dumps(body), encoding="utf-8")


def release(path: Path = LOCK_PATH) -> None:
    data = read_lock(path)
    if data and int(data.get("pid", 0)) == os.getpid():
        try:
            path.unlink()
        except OSError:
            pass
