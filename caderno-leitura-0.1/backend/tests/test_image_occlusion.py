"""F0.12.06 (spec 119): oclusão de imagem. Só dados fictícios (imagem sintética) em banco descartável (tmp_path)."""
from __future__ import annotations

import sqlite3
from contextlib import closing

from alembic import command
from alembic.config import Config

from app.core.config import BACKEND_DIR
from app.db.types import utc_now
from app.models import EncryptedMedia, ImageOcclusionCard, Study
from app.services.image_occlusion_service import normalize_box
from media_c_harness import OTHER, OWNER, harness  # noqa: F401

BOX = {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.1}


def _url(study_id, media_id):
    return f"/api/studies/{study_id}/media/{media_id}/occlusions"


def _setup(harness, **page_fields):  # noqa: F811
    study_id = harness.study()
    media_id = harness.page(OWNER, study_id, expires_at=utc_now(), **page_fields)
    return study_id, media_id, harness.client(OWNER)


def test_normalize_box_clamps_and_rejects_tiny():
    assert normalize_box(-0.2, 0.5, 0.5, 0.8) == (0.0, 0.5, 0.3, 0.5)
    for bad in ((0.5, 0.5, 0.005, 0.2), (1.2, 0.1, 0.3, 0.3)):
        try:
            normalize_box(*bad)
        except Exception as error:  # HTTPException 422
            assert getattr(error, "status_code", None) == 422
        else:
            raise AssertionError(bad)


def test_save_list_edit_delete_and_keep_forever(harness):  # noqa: F811
    study_id, media_id, client = _setup(harness)
    assert client.get(_url(study_id, media_id)).json()["cards"] == []

    saved = client.put(_url(study_id, media_id), json={"cards": [
        {**BOX, "label": "  Ventrículo esquerdo  "},
        {"x": 0.9, "y": 0.9, "width": 0.5, "height": 0.5, "label": ""},
    ]})
    assert saved.status_code == 200, saved.text
    body = saved.json()
    first, second = body["cards"]
    assert first["label"] == "Ventrículo esquerdo" and first["position"] == 0
    assert (second["x"], second["width"]) == (0.9, 0.1), "recortado aos limites"
    assert body["media"]["keep_forever"] is True
    with harness.factory() as session:
        media = session.get(EncryptedMedia, media_id)
        assert media.keep_forever and media.expires_at is None

    # A foto com cartões não volta a expirar.
    assert client.patch(f"/api/media/{media_id}", json={"keep_forever": False}).status_code == 409
    listed = client.get(f"/api/studies/{study_id}/media").json()["items"]
    assert listed[0]["occlusion_count"] == 2

    # Avaliar o primeiro, depois editar: o histórico fica; o que sumiu da lista é apagado.
    assert client.post(f"/api/review/images/{first['id']}/record", json={"rating": "hard"}).status_code == 200
    edited = client.put(_url(study_id, media_id), json={"cards": [
        {"id": first["id"], "x": 0.2, "y": 0.2, "width": 0.2, "height": 0.2, "label": "Átrio"},
        {**BOX},
    ]}).json()["cards"]
    assert edited[0]["id"] == first["id"] and edited[0]["review_count"] == 1 and edited[0]["label"] == "Átrio"
    assert second["id"] not in {card["id"] for card in edited}
    assert client.put(_url(study_id, media_id), json={"cards": [{**BOX, "id": 999999}]}).status_code == 422
    assert client.put(_url(study_id, media_id), json={"cards": [BOX] * 51}).status_code == 422
    assert client.put(_url(study_id, media_id), json={"cards": [{**BOX, "width": 0.001}]}).status_code == 422

    # Apagar a imagem leva os cartões.
    assert client.delete(f"/api/media/{media_id}").status_code == 200
    with harness.factory() as session:
        assert session.query(ImageOcclusionCard).count() == 0


def test_isolation(harness):  # noqa: F811
    study_id, media_id, _ = _setup(harness)
    other = harness.client(OTHER)
    assert other.get(_url(study_id, media_id)).status_code == 404
    assert other.put(_url(study_id, media_id), json={"cards": [BOX]}).status_code == 404
    other_study = harness.study(OTHER)
    assert harness.client(OWNER).get(_url(other_study, media_id)).status_code == 404, "imagem de outro estudo"


def test_review_queue_buckets_rating_and_trash(harness):  # noqa: F811
    study_id, media_id, client = _setup(harness)
    cards = client.put(_url(study_id, media_id), json={"cards": [
        {**BOX, "label": "Área A"}, {"x": 0.5, "y": 0.5, "width": 0.2, "height": 0.2, "label": "Área B"},
    ]}).json()["cards"]

    items = client.get("/api/review/items", params={"kind": "image"}).json()
    assert len(items) == 2 and {item["kind"] for item in items} == {"image"}
    item = items[0]
    assert item["media_id"] == media_id and item["occlusion_id"] == item["id"]
    assert len(item["regions"]) == 2 and item["expected_answer"] in ("Área A", "Área B")
    assert item["question_text"] == "O que está na área destacada?"

    stats = client.get("/api/review/stats", params={"kind": "image"}).json()
    assert stats["buckets"]["new"] == 2 and stats["total_eligible"] == 2 and stats["total_images"] == 2
    all_stats = client.get("/api/review/stats").json()
    assert all_stats["total_images"] == 2 and all_stats["buckets"]["new"] >= 2
    assert any(book["items_count"] >= 2 for book in all_stats["books"])
    assert {i["kind"] for i in client.get("/api/review/items").json()} >= {"image"}, "Todos inclui imagens"

    assert client.post(f"/api/review/images/{cards[0]['id']}/record", json={"rating": "easy"}).status_code == 200
    stats = client.get("/api/review/stats", params={"kind": "image"}).json()
    assert stats["buckets"]["easy"] == 1 and stats["reviewed_today"] == 1
    easy = client.get("/api/review/items", params={"kind": "image", "bucket": "easy"}).json()
    assert [i["id"] for i in easy] == [cards[0]["id"]]
    assert harness.client(OTHER).post(f"/api/review/images/{cards[0]['id']}/record",
                                      json={"rating": "easy"}).status_code == 404

    with harness.factory() as session:
        session.get(Study, study_id).deleted_at = utc_now()
        session.commit()
    assert client.get("/api/review/items", params={"kind": "image"}).json() == []
    assert client.post(f"/api/review/images/{cards[0]['id']}/record", json={"rating": "easy"}).status_code == 404


def test_migration_0041_up_and_down(tmp_path):
    db = tmp_path / "migracao" / "caderno.db"
    db.parent.mkdir()
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["database_path"] = db
    command.upgrade(cfg, "head")
    with closing(sqlite3.connect(db)) as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(image_occlusion_cards)")}
    assert {"media_id", "x", "y", "width", "height", "label", "difficulty_weight"} <= columns
    command.downgrade(cfg, "0040_study_published_at")
    with closing(sqlite3.connect(db)) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "image_occlusion_cards" not in tables
