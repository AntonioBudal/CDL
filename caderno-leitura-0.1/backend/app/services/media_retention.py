"""Retenção e reconciliação do cofre de imagens (feature 090-C).

Roda na partida e a cada ``LEITORUM_MEDIA_JOB_INTERVAL_HOURS``. As regras, nesta ordem:

1. marca ``completed_seen_at`` nas fotos de estudos concluídos (e limpa se o estudo deixou de estar concluído);
2. apaga as fotos cujo estudo está concluído há mais que a espera (7 dias);
3. apaga as fotos vencidas por idade (``expires_at``);
4. dá 7 dias às fotos cujo estudo foi purgado da lixeira (``study_id`` nulo), encurtando ``expires_at``;
5. apaga linhas ``pending`` com mais de 24 h (sobra de gravação interrompida, de qualquer tipo);
6. tenta de novo as linhas ``deleting``;
7. reconcilia o cofre: ``.tmp`` velhos, arquivos sem linha (com mais de 24 h) e linhas sem arquivo (``missing``).

Fotos "Mantidas permanentemente", capas e avatares nunca expiram pelas regras 1 a 4. Apagar usa só
``media_service.delete()``: nenhuma regra toca em ``studies``. O log leva só contagens e bytes.
"""

from __future__ import annotations

import logging
import os
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.core import config
from app.db.types import utc_now
from app.models.encrypted_media import EncryptedMedia
from app.models.study import Study
from app.services import media_service

logger = logging.getLogger("leitorum.media")

BATCH = 200
ORPHAN_DAYS = 7
PENDING_MAX_AGE = timedelta(hours=24)
TMP_MAX_AGE_SECONDS = 3600
STRAY_FILE_MAX_AGE_SECONDS = 24 * 3600
LIVE = ("active", "missing")
PAGE = "notebook_page"


def effective_expiry(row: EncryptedMedia, *, grace_days: int | None = None,
                     delete_on_completed: bool | None = None) -> datetime | None:
    """Quando a foto sai: a menor entre a validade por idade e o fim da espera depois de concluído."""
    if row.kind != PAGE or row.keep_forever:
        return None
    if grace_days is None:
        grace_days = config.get_media_completed_grace_days()
    if delete_on_completed is None:
        delete_on_completed = config.get_media_delete_on_completed()
    candidates = [row.expires_at] if row.expires_at else []
    if delete_on_completed and row.completed_seen_at:
        candidates.append(row.completed_seen_at + timedelta(days=grace_days))
    return min(candidates) if candidates else None


def _chunks(ids: list[str]):
    for start in range(0, len(ids), BATCH):
        yield ids[start:start + BATCH]


def _delete_ids(session: Session, ids: list[str], counts: Counter, rule: str) -> None:
    for chunk in _chunks(ids):
        for row in session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk)).all():
            freed = media_service.delete(session, row)
            if row.status == "deleting" and freed == 0 and session.get(EncryptedMedia, row.id) is not None:
                counts["failed"] += 1
            else:
                counts[rule] += 1
                counts["freed_bytes"] += freed
        session.commit()


def _ids(query) -> list[str]:
    return [row_id for (row_id,) in query.with_entities(EncryptedMedia.id).all()]


def _pages(session: Session):
    return session.query(EncryptedMedia).filter(
        EncryptedMedia.kind == PAGE, EncryptedMedia.status.in_(LIVE), EncryptedMedia.keep_forever.is_(False)
    )


def _mark_completed(session: Session, now: datetime, counts: Counter) -> None:
    concluded = _pages(session).join(Study, Study.id == EncryptedMedia.study_id).filter(
        Study.reading_status == "concluido", EncryptedMedia.completed_seen_at.is_(None)
    )
    for chunk in _chunks(_ids(concluded)):
        session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk)).update(
            {EncryptedMedia.completed_seen_at: now}, synchronize_session=False
        )
        counts["completed_marked"] += len(chunk)
        session.commit()
    # Estudo que deixou de estar concluído (ou sumiu): a contagem recomeça quando ele voltar a "concluído".
    reopened = session.query(EncryptedMedia).outerjoin(Study, Study.id == EncryptedMedia.study_id).filter(
        EncryptedMedia.completed_seen_at.is_not(None),
        (Study.id.is_(None)) | (Study.reading_status != "concluido"),
    )
    for chunk in _chunks(_ids(reopened)):
        session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk)).update(
            {EncryptedMedia.completed_seen_at: None}, synchronize_session=False
        )
        counts["completed_cleared"] += len(chunk)
        session.commit()


def _shorten_orphans(session: Session, now: datetime, counts: Counter) -> None:
    limit = now + timedelta(days=ORPHAN_DAYS)
    orphans = _pages(session).filter(
        EncryptedMedia.study_id.is_(None),
        (EncryptedMedia.expires_at.is_(None)) | (EncryptedMedia.expires_at > limit),
    )
    for chunk in _chunks(_ids(orphans)):
        session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk)).update(
            {EncryptedMedia.expires_at: limit}, synchronize_session=False
        )
        counts["orphans_scheduled"] += len(chunk)
        session.commit()


def _vault_files(folder: Path) -> tuple[dict[str, list[Path]], list[Path]]:
    """Arquivos do cofre por id de mídia, mais os ``.tmp``. Nomes fora do formato são ignorados."""
    by_id: dict[str, list[Path]] = {}
    temporaries: list[Path] = []
    if not folder.is_dir():
        return by_id, temporaries
    for shard in os.scandir(folder):
        if not shard.is_dir() or len(shard.name) != 2:
            continue
        for entry in os.scandir(shard.path):
            if not entry.is_file():
                continue
            if entry.name.endswith(".tmp"):
                temporaries.append(Path(entry.path))
                continue
            stem = entry.name.removesuffix(".thumb.enc").removesuffix(".enc")
            if entry.name.endswith(".enc") and media_service.UUID_RE.match(stem):
                by_id.setdefault(stem, []).append(Path(entry.path))
    return by_id, temporaries


def _older_than(path: Path, seconds: int, clock: float) -> bool:
    try:
        return clock - path.stat().st_mtime > seconds
    except OSError:
        return False


def _reconcile(session: Session, folder: Path, counts: Counter, clock: float) -> None:
    by_id, temporaries = _vault_files(folder)
    for temporary in temporaries:
        if _older_than(temporary, TMP_MAX_AGE_SECONDS, clock):
            temporary.unlink(missing_ok=True)
            counts["tmp_removed"] += 1

    known: set[str] = set()
    ids = list(by_id)
    for chunk in _chunks(ids):
        known.update(_ids(session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk))))
    for media_id in ids:
        if media_id in known:
            continue
        # Sem linha no banco: só sai depois de 24 h (protege uma gravação em andamento e um backup recém-restaurado).
        paths = by_id[media_id]
        if all(_older_than(path, STRAY_FILE_MAX_AGE_SECONDS, clock) for path in paths):
            for path in paths:
                path.unlink(missing_ok=True)
            counts["stray_removed"] += 1

    # Vale o arquivo principal: sem ele, a miniatura sozinha não serve a imagem.
    present = {media_id for media_id, paths in by_id.items() if any(not p.name.endswith(".thumb.enc") for p in paths)}
    rows = session.query(EncryptedMedia.id, EncryptedMedia.status).filter(EncryptedMedia.status.in_(LIVE)).all()
    gone = [row_id for row_id, status in rows if status == "active" and row_id not in present]
    back = [row_id for row_id, status in rows if status == "missing" and row_id in present]
    for status, chosen, key in (("missing", gone, "marked_missing"), ("active", back, "found_again")):
        for chunk in _chunks(chosen):
            session.query(EncryptedMedia).filter(EncryptedMedia.id.in_(chunk)).update(
                {EncryptedMedia.status: status}, synchronize_session=False
            )
            counts[key] += len(chunk)
            session.commit()


def run(session: Session, now: datetime | None = None, clock: float | None = None) -> dict:
    """Aplica as regras 1 a 7. ``now`` (UTC) e ``clock`` (segundos, para a idade dos arquivos) são injetáveis."""
    now = now or utc_now()
    clock = time.time() if clock is None else clock
    counts: Counter = Counter()
    try:
        folder = media_service._vault_dir()
    except Exception:  # noqa: BLE001 — HD indisponível: nada é apagado sem conseguir remover o arquivo
        return {"skipped": "storage_unavailable"}

    delete_on_completed = config.get_media_delete_on_completed()
    grace = timedelta(days=config.get_media_completed_grace_days())
    if delete_on_completed:
        _mark_completed(session, now, counts)
        expired_completed = _pages(session).filter(EncryptedMedia.completed_seen_at <= now - grace)
        _delete_ids(session, _ids(expired_completed), counts, "deleted_completed")
    _delete_ids(session, _ids(_pages(session).filter(EncryptedMedia.expires_at <= now)), counts, "deleted_expired")
    _shorten_orphans(session, now, counts)
    stale = session.query(EncryptedMedia).filter(
        EncryptedMedia.status == "pending", EncryptedMedia.created_at <= now - PENDING_MAX_AGE
    )
    _delete_ids(session, _ids(stale), counts, "deleted_pending")
    retry = session.query(EncryptedMedia).filter(EncryptedMedia.status == "deleting")
    _delete_ids(session, _ids(retry), counts, "deleted_retried")
    _reconcile(session, folder, counts, clock)
    return dict(counts)


def run_once() -> dict:
    """Uma rodada com uma sessão do banco configurado, registrando só contagens e bytes."""
    from app.db.session import get_session
    from app.services.media_quota import human_bytes

    for session in get_session():
        result = run(session)
        if result.get("skipped"):
            logger.info("Retenção do cofre: não rodou (%s)", result["skipped"])
            return result
        deleted = sum(value for key, value in result.items() if key.startswith("deleted_"))
        if deleted or result.get("marked_missing") or result.get("stray_removed") or result.get("failed"):
            logger.info(
                "Retenção do cofre: %d apagadas (%s), %d marcadas como ausentes, %d arquivos soltos removidos, "
                "%d falhas",
                deleted, human_bytes(result.get("freed_bytes", 0)), result.get("marked_missing", 0),
                result.get("stray_removed", 0), result.get("failed", 0),
            )
        return result
    return {}
