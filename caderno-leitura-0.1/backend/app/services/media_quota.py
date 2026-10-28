"""Cotas do cofre de imagens (feature 090-C): por usuário, global e espaço livre real do disco.

A verificação é atômica dentro do processo (o servidor é de processo único): ``reserve()`` soma, sob um lock, o
uso já gravado no banco e as reservas em andamento, que ficam em memória até a transação de quem gravou
terminar. Assim, entre gravar o arquivo e confirmar a linha, nenhuma outra requisição vê um uso menor que o real.
Nada aqui registra em log ids ou nomes; só tipos de erro.
"""

from __future__ import annotations

import shutil
import threading

from sqlalchemy import event, func
from sqlalchemy.orm import Session

from app.core import config
from app.models.encrypted_media import EncryptedMedia

COUNTED_STATUSES = ("pending", "active", "deleting")
HIGH_PERCENT = 85
SESSION_KEY = "leitorum_media_reservations"

_lock = threading.Lock()
_reservations: dict[str, tuple[str, int]] = {}  # media_id: (user_id, bytes)


class QuotaExceeded(RuntimeError):
    """Gravação recusada: ``code`` é ``user_quota`` ou ``server_quota``; ``usage`` é o de ``usage()``."""

    def __init__(self, code: str, detail: str, usage: dict) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.usage = usage


def human_bytes(value: int) -> str:
    """Tamanho como o Windows mostra (base 1024, rótulos MB e GB), com vírgula decimal."""
    if value >= config.GIB:
        return f"{value / config.GIB:.1f} GB".replace(".", ",").replace(",0 GB", " GB")
    return f"{max(value, 0) / 1024**2:.0f} MB" if value >= 1024**2 else f"{max(value, 0) / 1024:.0f} KB"


def disk_free(path) -> int | None:
    try:
        return shutil.disk_usage(path).free
    except OSError:
        return None


def _level(used: int, quota: int, *, out_of_space: bool = False) -> tuple[float, str]:
    percent = round(used * 100 / quota, 1) if quota else 100.0
    if out_of_space or used >= quota:
        return percent, "full"
    return percent, "high" if percent >= HIGH_PERCENT else "normal"


def _sums(session: Session, user_id: str, exclude: list[str]) -> tuple[int, int, int]:
    """(uso do usuário, imagens ativas do usuário, uso global) já confirmados no banco, sem as reservas.

    A soma roda numa sessão curta e separada: na sessão de quem vai gravar, essa leitura abriria um retrato do
    banco, e o INSERT seguinte seria recusado pelo SQLite ("database is locked") se outra gravação terminasse
    no meio. O que ainda não foi confirmado está nas reservas em memória.
    """
    with Session(session.get_bind()) as fresh:
        counted = fresh.query(EncryptedMedia).filter(EncryptedMedia.status.in_(COUNTED_STATUSES))
        if exclude:
            counted = counted.filter(EncryptedMedia.id.notin_(exclude))
        user_used = counted.filter(EncryptedMedia.user_id == user_id).with_entities(
            func.coalesce(func.sum(EncryptedMedia.byte_size), 0)
        ).scalar()
        server_used = counted.with_entities(func.coalesce(func.sum(EncryptedMedia.byte_size), 0)).scalar()
        count = fresh.query(func.count(EncryptedMedia.id)).filter(
            EncryptedMedia.user_id == user_id, EncryptedMedia.status == "active"
        ).scalar()
    return int(user_used), int(count), int(server_used)


def _usage_locked(session: Session, user_id: str) -> dict:
    from app.services import media_service

    reserved = list(_reservations)
    user_used, count, server_used = _sums(session, user_id, reserved)
    user_used += sum(size for owner, size in _reservations.values() if owner == user_id)
    server_used += sum(size for _owner, size in _reservations.values())
    try:
        free = disk_free(media_service._vault_dir())
    except Exception:  # noqa: BLE001 — HD indisponível: o estado do cofre já explica
        free = None
    margin = config.get_storage_free_margin_bytes()
    user_quota, server_quota = config.get_user_storage_quota_bytes(), config.get_global_storage_quota_bytes()
    user_percent, user_level = _level(user_used, user_quota)
    server_percent, server_level = _level(server_used, server_quota, out_of_space=free is not None and free <= margin)
    return {
        "user": {"used_bytes": user_used, "quota_bytes": user_quota, "count": count, "percent": user_percent,
                 "level": user_level},
        "server": {"used_bytes": server_used, "quota_bytes": server_quota, "disk_free_bytes": free,
                   "margin_bytes": margin, "percent": server_percent, "level": server_level},
    }


def usage(session: Session, user_id: str) -> dict:
    with _lock:
        return _usage_locked(session, user_id)


def view_for(current: dict, *, is_admin: bool) -> dict:
    """Uso como cada um pode ver: só o administrador vê os números do servidor; os demais, o nível (C-Q4)."""
    if is_admin:
        return current
    return {"user": current["user"], "server": {"level": current["server"]["level"]}}


def reserve(session: Session, user_id: str, media_id: str, nbytes: int) -> None:
    """Reserva ``nbytes`` para a gravação, ou levanta ``QuotaExceeded``. Liberada quando a transação termina."""
    with _lock:
        current = _usage_locked(session, user_id)
        user, server = current["user"], current["server"]
        if user["used_bytes"] + nbytes > user["quota_bytes"]:
            raise QuotaExceeded(
                "user_quota",
                f"Seu espaço está cheio: {human_bytes(user['used_bytes'])} de {human_bytes(user['quota_bytes'])}. "
                "Libere espaço em Minhas Imagens e Espaço.",
                view_for(current, is_admin=False),
            )
        free = server["disk_free_bytes"]
        if server["used_bytes"] + nbytes > server["quota_bytes"] or (
            free is not None and free - nbytes < server["margin_bytes"]
        ):
            raise QuotaExceeded(
                "server_quota",
                "O servidor está sem espaço para novas imagens. Libere espaço em Minhas Imagens e Espaço ou "
                "avise o administrador.",
                view_for(current, is_admin=False),
            )
        _reservations[media_id] = (user_id, nbytes)
        session.info.setdefault(SESSION_KEY, set()).add(media_id)


def pending_reservations() -> int:
    """Quantas reservas estão em andamento (para os testes)."""
    with _lock:
        return len(_reservations)


@event.listens_for(Session, "after_transaction_end")
def _release(session: Session, transaction) -> None:
    # Commit, rollback ou fechamento da sessão: a linha já está no banco (ou não existe mais).
    if transaction.parent is not None:
        return
    held = session.info.pop(SESSION_KEY, None)
    if held:
        with _lock:
            for media_id in held:
                _reservations.pop(media_id, None)
