"""Feature 090-C (C027): cotas do cofre por usuário, global e espaço livre real, inclusive com concorrência."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import func

from app.models.encrypted_media import EncryptedMedia
from app.models.study import Study
from app.services import media_quota, media_service, vault
from app.services.media_quota import QuotaExceeded
from media_c_harness import ADMIN, OTHER, OWNER, harness, small_webp, synthetic_photo  # noqa: F401

MARGIN = 2 * 1024**3


def page_size(harness) -> int:
    """Tamanho em disco (imagem + miniatura cifradas) da página sintética padrão: é determinístico."""
    with harness.factory() as session:
        row = media_service.store(session, user_id=ADMIN, kind="notebook_page", webp=small_webp())
        session.commit()
        size = row.byte_size
        media_service.delete(session, row)
        session.commit()
    return size


def store(harness, uid=OWNER):
    with harness.factory() as session:
        row = media_service.store(session, user_id=uid, kind="notebook_page", webp=small_webp())
        session.commit()
        return row


def test_user_quota_exact_limit(harness, monkeypatch):
    size = page_size(harness)
    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", str(2 * size))
    store(harness)
    store(harness)  # chega exatamente na cota
    with pytest.raises(QuotaExceeded) as refused:
        store(harness)
    assert refused.value.code == "user_quota"
    assert refused.value.usage["user"]["used_bytes"] == 2 * size
    assert refused.value.usage["user"]["level"] == "full"
    assert "used_bytes" not in refused.value.usage["server"]  # usuário comum só vê o nível do servidor

    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", str(size - 1))
    with pytest.raises(QuotaExceeded):
        store(harness, OTHER)  # não cabe por 1 byte
    assert media_quota.pending_reservations() == 0


def test_global_quota_and_free_space_margin(harness, monkeypatch):
    size = page_size(harness)
    store(harness, OTHER)
    monkeypatch.setenv("LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES", str(2 * size - 1))
    with pytest.raises(QuotaExceeded) as refused:
        store(harness)
    assert refused.value.code == "server_quota"
    monkeypatch.setenv("LEITORUM_GLOBAL_STORAGE_QUOTA_BYTES", str(2 * size))
    monkeypatch.setenv("LEITORUM_STORAGE_FREE_MARGIN_BYTES", str(MARGIN))

    harness.free = MARGIN + size - 1
    with pytest.raises(QuotaExceeded) as refused:
        store(harness)
    assert refused.value.code == "server_quota"
    harness.free = MARGIN + size
    store(harness)

    with harness.factory() as session:
        assert media_quota.usage(session, OWNER)["server"]["level"] == "full"


def test_concurrent_writes_never_pass_the_quota(harness, monkeypatch):
    size = page_size(harness)
    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", str(5 * size))

    def attempt(_):
        session = harness.factory()
        try:
            media_service.store(session, user_id=OWNER, kind="notebook_page", webp=small_webp())
            session.commit()
            return "ok"
        except QuotaExceeded:
            session.rollback()
            return "refused"
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(pool.map(attempt, range(20)))

    assert results.count("ok") == 5 and results.count("refused") == 15
    with harness.factory() as session:
        used = session.query(func.sum(EncryptedMedia.byte_size)).filter(EncryptedMedia.user_id == OWNER).scalar()
    assert used == 5 * size
    assert media_quota.pending_reservations() == 0


def test_reservation_is_released_on_rollback_and_on_write_error(harness, monkeypatch):
    with harness.factory() as session:
        media_service.store(session, user_id=OWNER, kind="notebook_page", webp=small_webp())
        assert media_quota.pending_reservations() == 1
        session.rollback()
    assert media_quota.pending_reservations() == 0

    def broken(_path, _data):
        raise OSError("disco cheio simulado")

    monkeypatch.setattr(vault, "write_atomic", broken)
    with harness.factory() as session:
        with pytest.raises(OSError):
            media_service.store(session, user_id=OWNER, kind="notebook_page", webp=small_webp())
        session.rollback()
    assert media_quota.pending_reservations() == 0
    with harness.factory() as session:
        assert media_quota.usage(session, OWNER)["user"]["used_bytes"] == 0


def test_routes_answer_507_with_code_and_usage(harness, monkeypatch):
    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", "1")
    client = harness.client(OWNER)
    study_id = harness.study()
    with harness.factory() as session:
        book_id = session.get(Study, study_id).book_id

    jpeg = synthetic_photo(800, 600)
    answers = [
        client.post(f"/api/books/{book_id}/cover", files={"file": ("c.jpg", jpeg, "image/jpeg")}),
        client.post("/api/profile/avatar", files={"file": ("a.jpg", jpeg, "image/jpeg")}),
        client.post(f"/api/studies/{study_id}/media", files={"file": ("p.jpg", jpeg, "image/jpeg")}),
    ]
    for res in answers:
        assert res.status_code == 507, res.text
        body = res.json()
        assert body["code"] == "user_quota"
        assert "Minhas Imagens e Espaço" in body["detail"]
        assert body["usage"]["user"]["quota_bytes"] == 1
        assert set(body["usage"]["server"]) == {"level"}
    with harness.factory() as session:
        assert session.query(EncryptedMedia).count() == 0
    assert media_quota.pending_reservations() == 0
