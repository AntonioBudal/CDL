"""Feature 090-C (C030): job de retenção e reconciliação do cofre, com relógio injetável (SC-009)."""

from __future__ import annotations

import logging
import os
import time
import uuid
from datetime import timedelta

import pytest
from sqlalchemy import text

from app.core.storage import StorageError
from app.db.types import utc_now
from app.models.encrypted_media import EncryptedMedia
from app.models.study import Study
from app.services import media_retention, media_service
from app.services.vault import media_path, thumb_path
from media_c_harness import OWNER, harness, small_webp  # noqa: F401

DAY = timedelta(days=1)


def run(harness, now, clock=None):
    with harness.factory() as session:
        return media_retention.run(session, now=now, clock=clock)


def row(harness, media_id):
    with harness.factory() as session:
        return session.get(EncryptedMedia, media_id)


def set_status(harness, study_id, status):
    with harness.factory() as session:
        session.get(Study, study_id).reading_status = status
        session.commit()


def files(harness, media_id):
    media_uuid = uuid.UUID(media_id)
    return [media_path(harness.vault_dir, media_uuid), thumb_path(harness.vault_dir, media_uuid)]


def test_age_expiry_deletes_files_and_keeps_kept_photos(harness):
    now = utc_now()
    study_id = harness.study()
    expired = harness.page(OWNER, study_id, expires_at=now - timedelta(seconds=1))
    fresh = harness.page(OWNER, study_id, expires_at=now + DAY)
    kept = harness.page(OWNER, study_id, keep_forever=True, expires_at=None)
    before = harness.snapshot(study_id)

    result = run(harness, now)

    assert result["deleted_expired"] == 1 and result["freed_bytes"] > 0
    assert row(harness, expired) is None and not any(path.exists() for path in files(harness, expired))
    assert row(harness, fresh) is not None and row(harness, kept) is not None
    assert harness.snapshot(study_id) == before


def test_completed_study_waits_seven_days_and_restarts_when_reopened(harness):
    start = utc_now()
    study_id = harness.study(status="concluido")
    page = harness.page(OWNER, study_id, expires_at=start + 60 * DAY)
    kept = harness.page(OWNER, study_id, keep_forever=True, expires_at=None)

    assert run(harness, start)["completed_marked"] == 1
    assert row(harness, page).completed_seen_at == start
    assert row(harness, kept).completed_seen_at is None
    run(harness, start + 6 * DAY)
    assert row(harness, page) is not None

    set_status(harness, study_id, "revisado")
    assert run(harness, start + 6 * DAY + timedelta(hours=1))["completed_cleared"] == 1
    set_status(harness, study_id, "concluido")
    run(harness, start + 8 * DAY)
    assert row(harness, page).completed_seen_at == start + 8 * DAY
    run(harness, start + 14 * DAY)
    assert row(harness, page) is not None  # a contagem recomeçou

    before = harness.snapshot(study_id)
    result = run(harness, start + 15 * DAY + timedelta(seconds=1))
    assert result["deleted_completed"] == 1 and row(harness, page) is None
    assert row(harness, kept) is not None
    assert harness.snapshot(study_id) == before


def test_completed_rule_can_be_turned_off(harness, monkeypatch):
    monkeypatch.setenv("LEITORUM_MEDIA_DELETE_ON_COMPLETED", "false")
    now = utc_now()
    page = harness.page(OWNER, harness.study(status="concluido"), expires_at=now + 60 * DAY)
    result = run(harness, now + 30 * DAY)
    assert "completed_marked" not in result and row(harness, page) is not None


def test_covers_and_avatars_never_expire(harness):
    old = utc_now() - 400 * DAY
    with harness.factory() as session:
        ids = []
        for kind in ("cover", "avatar"):
            media = media_service.store(session, user_id=OWNER, kind=kind, webp=small_webp())
            media.created_at = old
            ids.append(media.id)
        session.commit()
    run(harness, utc_now() + 400 * DAY)
    assert all(row(harness, media_id) is not None for media_id in ids)


def test_orphan_after_purge_gets_seven_days(harness):
    now = utc_now()
    study_id = harness.study()
    page = harness.page(OWNER, study_id, expires_at=now + 25 * DAY)
    with harness.factory() as session:  # purga definitiva da lixeira: a chave estrangeira zera study_id
        session.execute(text("DELETE FROM studies WHERE id = :id"), {"id": study_id})
        session.commit()
    assert row(harness, page).study_id is None

    assert run(harness, now)["orphans_scheduled"] == 1
    assert row(harness, page).expires_at == now + 7 * DAY
    run(harness, now + 6 * DAY)
    assert row(harness, page) is not None
    assert run(harness, now + 7 * DAY + timedelta(seconds=1))["deleted_expired"] == 1


def test_stale_pending_and_stuck_deleting_rows(harness):
    now = utc_now()
    with harness.factory() as session:
        stale = media_service.store(session, user_id=OWNER, kind="cover", webp=small_webp(), status="pending")
        stale.created_at = now - 25 * timedelta(hours=1)
        recent = media_service.store(session, user_id=OWNER, kind="cover", webp=small_webp(), status="pending")
        stuck = media_service.store(session, user_id=OWNER, kind="notebook_page", webp=small_webp())
        stuck.status = "deleting"
        session.commit()
        stale_id, recent_id, stuck_id = stale.id, recent.id, stuck.id

    result = run(harness, now)
    assert result["deleted_pending"] == 1 and result["deleted_retried"] == 1
    assert row(harness, stale_id) is None and row(harness, recent_id) is not None
    assert row(harness, stuck_id) is None and not any(path.exists() for path in files(harness, stuck_id))


def test_failed_removal_is_retried_on_the_next_run(harness, monkeypatch):
    now = utc_now()
    page = harness.page(OWNER, harness.study(), expires_at=now - DAY)
    original = media_service.vault.media_path

    def locked(folder, media_id):
        raise OSError("arquivo em uso simulado")

    monkeypatch.setattr(media_service.vault, "media_path", locked)
    first = run(harness, now)
    assert first["failed"] >= 1 and row(harness, page).status == "deleting"
    monkeypatch.setattr(media_service.vault, "media_path", original)
    assert run(harness, now)["deleted_retried"] == 1 and row(harness, page) is None


def test_reconciliation_of_tmp_stray_and_missing_files(harness):
    now = utc_now()
    clock = time.time()
    shard = harness.vault_dir / "ab"
    shard.mkdir(exist_ok=True)
    old_tmp, new_tmp = shard / "x.enc.tmp", shard / "y.enc.tmp"
    stray_old = shard / f"{uuid.UUID('ab' + '0' * 30)}.enc"
    stray_new = shard / f"{uuid.UUID('ab' + '1' * 30)}.enc"
    for path in (old_tmp, new_tmp, stray_old, stray_new):
        path.write_bytes(b"conteudo de teste")
    for path, age in ((old_tmp, 2 * 3600), (stray_old, 25 * 3600)):
        os.utime(path, (clock - age, clock - age))
    page = harness.page(OWNER, harness.study())
    main_file = files(harness, page)[0]
    saved = main_file.read_bytes()
    main_file.unlink()

    result = run(harness, now, clock=clock)
    assert result["tmp_removed"] == 1 and not old_tmp.exists() and new_tmp.exists()
    assert result["stray_removed"] == 1 and not stray_old.exists() and stray_new.exists()
    assert result["marked_missing"] == 1 and row(harness, page).status == "missing"

    main_file.write_bytes(saved)
    assert run(harness, now, clock=clock)["found_again"] == 1
    assert row(harness, page).status == "active"


def test_unavailable_storage_changes_nothing(harness, monkeypatch):
    now = utc_now()
    page = harness.page(OWNER, harness.study(), expires_at=now - DAY)

    def unavailable():
        raise StorageError("HD ausente simulado")

    monkeypatch.setattr(media_service, "_vault_dir", unavailable)
    assert run(harness, now) == {"skipped": "storage_unavailable"}
    assert row(harness, page) is not None


def test_run_once_logs_only_counts(harness, monkeypatch, caplog):
    now = utc_now()
    page = harness.page(OWNER, harness.study(title="Título Secreto de Teste"), expires_at=now - DAY)

    def sessions():
        with harness.factory() as session:
            yield session

    import app.db.session as db_session

    monkeypatch.setattr(db_session, "get_session", sessions)
    with caplog.at_level(logging.INFO, logger="leitorum.media"):
        result = media_retention.run_once()
    assert result["deleted_expired"] == 1
    log = caplog.text
    assert "1 apagadas" in log
    assert page not in log and "Título Secreto" not in log and "Livro de Teste" not in log


@pytest.mark.parametrize("keep", [True, False])
def test_effective_expiry(keep):
    now = utc_now()
    media = EncryptedMedia(kind="notebook_page", keep_forever=keep, expires_at=None if keep else now + 30 * DAY,
                           completed_seen_at=now)
    expiry = media_retention.effective_expiry(media, grace_days=7, delete_on_completed=True)
    assert expiry == (None if keep else now + 7 * DAY)
