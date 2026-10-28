"""Feature 090-C (C028): foto de conferência guardada com o estudo. Só imagens e textos fictícios."""

from __future__ import annotations

import io
import uuid

from PIL import Image

from app.models.encrypted_media import EncryptedMedia
from app.services.vault import media_path
from media_c_harness import OTHER, OWNER, harness, synthetic_photo  # noqa: F401

PLAIN_SIGNATURES = (b"RIFF", b"WEBP", b"\xff\xd8\xff", b"\x89PNG", b"JFIF", b"Exif", b"CameraDeTeste")


def send(client, study_id: int, data: bytes, name: str = "pagina.jpg", mime: str = "image/jpeg"):
    return client.post(f"/api/studies/{study_id}/media", files={"file": (name, data, mime)})


def test_photo_is_optimized_without_metadata_and_encrypted(harness):
    study_id = harness.study()
    res = send(harness.client(OWNER), study_id, synthetic_photo(with_gps=True))
    assert res.status_code == 201, res.text
    body = res.json()
    item = body["item"]
    assert item["kind"] == "notebook_page" and item["status"] == "active"
    assert item["study"]["id"] == study_id and item["study"]["title"] == "Estudo de Teste"
    assert item["book"]["title"] == "Livro de Teste"
    assert item["days_left"] == 30 and item["keep_forever"] is False
    assert (item["width"], item["height"]) == (2000, 1500)
    assert body["usage"]["user"]["count"] == 1

    blob = media_path(harness.vault_dir, uuid.UUID(item["id"])).read_bytes()
    assert not any(signature in blob for signature in PLAIN_SIGNATURES)

    served = harness.client(OWNER).get(f"/api/media/{item['id']}/content")
    assert served.status_code == 200 and "no-store" in served.headers["cache-control"]
    image = Image.open(io.BytesIO(served.content))
    image.load()
    assert image.format == "WEBP" and max(image.size) == 2000
    assert not image.info.get("exif") and b"CameraDeTeste" not in served.content


def test_only_the_owner_reads_lists_and_stores(harness):
    study_id = harness.study()
    item = send(harness.client(OWNER), study_id, synthetic_photo(800, 600)).json()["item"]
    other = harness.client(OTHER)

    assert other.get(f"/api/media/{item['id']}/content").status_code == 404
    assert other.get(f"/api/studies/{study_id}/media").status_code == 404
    assert send(other, study_id, synthetic_photo(800, 600)).status_code == 404

    listed = harness.client(OWNER).get(f"/api/studies/{study_id}/media")
    assert listed.status_code == 200
    assert [entry["id"] for entry in listed.json()["items"]] == [item["id"]]


def test_trashed_or_missing_study_gets_404(harness):
    trashed = harness.study(trashed=True)
    assert send(harness.client(OWNER), trashed, synthetic_photo(800, 600)).status_code == 404
    assert send(harness.client(OWNER), 999_999, synthetic_photo(800, 600)).status_code == 404


def test_invalid_files_are_refused(harness):
    study_id = harness.study()
    client = harness.client(OWNER)
    gif = io.BytesIO()
    Image.new("RGB", (50, 50)).save(gif, format="GIF")
    assert send(client, study_id, gif.getvalue(), "p.gif", "image/gif").status_code == 415
    assert send(client, study_id, b"\xff\xd8\xff nao e uma foto", "p.jpg").status_code == 422
    assert send(client, study_id, b"", "p.jpg").status_code == 422
    with harness.factory() as session:
        assert session.query(EncryptedMedia).count() == 0


def test_full_quota_keeps_the_study_intact(harness, monkeypatch):
    study_id = harness.study()
    before = harness.snapshot(study_id)
    monkeypatch.setenv("LEITORUM_USER_STORAGE_QUOTA_BYTES", "1")
    res = send(harness.client(OWNER), study_id, synthetic_photo(800, 600))
    assert res.status_code == 507 and res.json()["code"] == "user_quota"
    assert harness.snapshot(study_id) == before
