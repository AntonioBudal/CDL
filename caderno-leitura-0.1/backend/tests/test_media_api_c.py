"""Feature 090-C (C029): uso por papel, lista enriquecida, "manter" e apagamento em lote sem tocar nos estudos."""

from __future__ import annotations

from datetime import timedelta

from app.db.types import utc_now
from app.models.encrypted_media import EncryptedMedia
from app.services import media_service
from media_c_harness import ADMIN, OTHER, OWNER, harness, small_webp  # noqa: F401


def test_usage_shows_server_numbers_only_to_the_admin(harness):
    harness.page(OWNER, harness.study())
    user_view = harness.client(OWNER).get("/api/media/usage").json()
    assert user_view["user"]["count"] == 1 and user_view["user"]["level"] == "normal"
    assert user_view["user"]["quota_bytes"] == 1024**3
    assert user_view["server"] == {"level": "normal"}
    assert user_view["vault"] == {"state": "ready"}

    admin_view = harness.client(ADMIN).get("/api/media/usage").json()
    assert admin_view["server"]["used_bytes"] == user_view["user"]["used_bytes"]
    assert admin_view["server"]["quota_bytes"] == 900 * 1024**3
    assert admin_view["server"]["disk_free_bytes"] == harness.free
    assert admin_view["user"]["count"] == 0


def test_list_has_book_study_validity_filters_and_sorting(harness):
    study_id = harness.study()
    soon = harness.page(OWNER, study_id, expires_at=utc_now() + timedelta(days=3))
    later = harness.page(OWNER, study_id, expires_at=utc_now() + timedelta(days=20))
    kept = harness.page(OWNER, study_id, keep_forever=True, expires_at=None)
    with harness.factory() as session:
        big = media_service.store(session, user_id=OWNER, kind="cover", webp=small_webp(1600, 1200, (1, 2, 3)))
        session.commit()
        big_id = big.id
    client = harness.client(OWNER)

    items = client.get("/api/media", params={"sort": "expires_asc"}).json()["items"]
    assert [item["id"] for item in items[:2]] == [soon, later]
    first = items[0]
    assert first["study"] == {"id": study_id, "title": "Estudo de Teste", "reading_status": "rascunho",
                              "in_trash": False}
    assert first["book"]["title"] == "Livro de Teste" and first["days_left"] == 3
    kept_item = next(item for item in items if item["id"] == kept)
    assert kept_item["days_left"] is None and kept_item["expires_at"] is None

    covers = client.get("/api/media", params={"kind": "cover"}).json()["items"]
    assert [item["id"] for item in covers] == [big_id]
    assert covers[0]["days_left"] is None
    assert client.get("/api/media", params={"sort": "size_desc"}).json()["items"][0]["id"] == big_id
    book_id = first["book"]["id"]
    assert len(client.get("/api/media", params={"book_id": book_id}).json()["items"]) == 3
    assert harness.client(OTHER).get("/api/media").json()["items"] == []


def test_completed_study_shortens_the_shown_validity(harness):
    study_id = harness.study(status="concluido")
    page = harness.page(OWNER, study_id, expires_at=utc_now() + timedelta(days=25),
                        completed_seen_at=utc_now() - timedelta(days=2))
    item = harness.client(OWNER).get("/api/media").json()["items"][0]
    assert item["id"] == page and item["days_left"] == 5


def test_keep_forever_toggle(harness):
    study_id = harness.study()
    page = harness.page(OWNER, study_id, expires_at=utc_now() + timedelta(days=4))
    client = harness.client(OWNER)

    kept = client.patch(f"/api/media/{page}", json={"keep_forever": True})
    assert kept.status_code == 200
    assert kept.json()["keep_forever"] is True and kept.json()["days_left"] is None
    released = client.patch(f"/api/media/{page}", json={"keep_forever": False}).json()
    assert released["keep_forever"] is False and released["days_left"] == 30

    assert harness.client(OTHER).patch(f"/api/media/{page}", json={"keep_forever": True}).status_code == 404
    with harness.factory() as session:
        cover = media_service.store(session, user_id=OWNER, kind="cover", webp=small_webp())
        session.commit()
    assert client.patch(f"/api/media/{cover.id}", json={"keep_forever": True}).status_code == 404


def test_bulk_delete_preview_filters_and_ids_without_touching_studies(harness):
    done = harness.study(status="concluido", title="Estudo concluído")
    open_study = harness.study(title="Estudo aberto")
    old = utc_now() - timedelta(days=40)
    completed_page = harness.page(OWNER, done)
    old_page = harness.page(OWNER, open_study, created_at=old)
    kept_old = harness.page(OWNER, open_study, created_at=old, keep_forever=True, expires_at=None)
    recent = harness.page(OWNER, open_study)
    others = harness.page(OTHER, harness.study(OTHER))
    before = {study_id: harness.snapshot(study_id) for study_id in (done, open_study)}
    client = harness.client(OWNER)

    preview = client.post("/api/media/bulk-delete", json={"filter": "completed_studies", "dry_run": True}).json()
    assert preview["matched"] == 1 and preview["deleted"] == 0 and preview["freed_bytes"] > 0
    with harness.factory() as session:
        assert session.get(EncryptedMedia, completed_page) is not None

    gone = client.post("/api/media/bulk-delete", json={"filter": "completed_studies", "dry_run": False}).json()
    assert gone["deleted"] == 1 and gone["freed_bytes"] == preview["freed_bytes"]

    aged = client.post("/api/media/bulk-delete",
                       json={"filter": "older_than_days", "days": 30, "dry_run": False}).json()
    assert aged["deleted"] == 1  # a mantida fica de fora do filtro

    chosen = client.post("/api/media/bulk-delete", json={"ids": [kept_old, others], "dry_run": False}).json()
    assert chosen["matched"] == 1 and chosen["deleted"] == 1  # a foto de outro usuário é ignorada

    with harness.factory() as session:
        remaining = {row.id for row in session.query(EncryptedMedia).all()}
    assert remaining == {recent, others}
    assert old_page not in remaining
    for study_id, snapshot in before.items():
        assert harness.snapshot(study_id) == snapshot


def test_bulk_delete_validation(harness):
    client = harness.client(OWNER)
    assert client.post("/api/media/bulk-delete", json={"dry_run": True}).status_code == 422
    assert client.post("/api/media/bulk-delete",
                       json={"filter": "completed_studies", "ids": ["x"], "dry_run": True}).status_code == 422
    assert client.post("/api/media/bulk-delete", json={"filter": "older_than_days"}).status_code == 422
    assert client.post("/api/media/bulk-delete", json={"ids": ["x"] * 501}).status_code == 422


def test_single_delete_keeps_the_study_identical(harness):
    study_id = harness.study()
    page = harness.page(OWNER, study_id)
    before = harness.snapshot(study_id)
    res = harness.client(OWNER).delete(f"/api/media/{page}")
    assert res.status_code == 200 and res.json()["freed_bytes"] > 0
    assert harness.snapshot(study_id) == before
    assert harness.client(OWNER).get(f"/api/studies/{study_id}/media").json()["items"] == []
