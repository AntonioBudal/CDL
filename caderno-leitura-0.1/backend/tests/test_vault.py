"""Feature 090-B (B017): formato .enc v1, chave mestra e código de recuperação. Só dados sintéticos."""

from __future__ import annotations

import os
import uuid

import pytest

from app.core import media_key
from app.core.media_key import MediaKeyError
from app.services import vault
from app.services.vault import VaultIntegrityError

USER_A = "11111111-1111-1111-1111-111111111111"
USER_B = "22222222-2222-2222-2222-222222222222"
PLAIN = b"RIFF\x00\x00\x00\x00WEBPVP8 imagem sintetica de teste" * 4


@pytest.fixture
def master() -> bytes:
    return os.urandom(32)


def test_roundtrip_and_header_layout(master):
    media_id = uuid.uuid4()
    blob = vault.encrypt(master, USER_A, media_id, PLAIN, epoch=3)

    assert blob[:4] == vault.MAGIC
    assert list(blob[4:8]) == [vault.FORMAT_VERSION, vault.CIPHER_AES_GCM, vault.KDF_HKDF, 3]
    assert blob[8:24] == media_id.bytes
    assert len(blob) == vault.HEADER_LEN + len(PLAIN) + 16
    assert PLAIN[:12] not in blob and b"WEBP" not in blob
    assert vault.decrypt(master, USER_A, media_id, blob) == PLAIN


def test_same_image_twice_gives_different_ciphertext(master):
    media_id = uuid.uuid4()
    assert vault.encrypt(master, USER_A, media_id, PLAIN) != vault.encrypt(master, USER_A, media_id, PLAIN)


def test_file_is_bound_to_user_media_and_key(master):
    media_id = uuid.uuid4()
    blob = vault.encrypt(master, USER_A, media_id, PLAIN)

    with pytest.raises(VaultIntegrityError):
        vault.decrypt(master, USER_B, media_id, blob)  # copiado para outro usuário
    with pytest.raises(VaultIntegrityError):
        vault.decrypt(master, USER_A, uuid.uuid4(), blob)  # renomeado para outra mídia
    with pytest.raises(VaultIntegrityError):
        vault.decrypt(os.urandom(32), USER_A, media_id, blob)  # chave errada


@pytest.mark.parametrize("position", [4, 7, 30, vault.HEADER_LEN + 2, -1])
def test_any_flipped_byte_is_rejected(master, position):
    media_id = uuid.uuid4()
    blob = bytearray(vault.encrypt(master, USER_A, media_id, PLAIN))
    blob[position] ^= 0x01
    with pytest.raises(VaultIntegrityError):
        vault.decrypt(master, USER_A, media_id, bytes(blob))


def test_truncated_or_foreign_file_is_rejected(master):
    media_id = uuid.uuid4()
    blob = vault.encrypt(master, USER_A, media_id, PLAIN)
    for bad in (blob[:20], b"", b"RIFF" + blob[4:], blob[:-1]):
        with pytest.raises(VaultIntegrityError):
            vault.decrypt(master, USER_A, media_id, bad)


def test_per_file_keys_differ(master):
    media_id = uuid.uuid4()
    keys = {
        vault.file_key(master, USER_A, media_id, 0),
        vault.file_key(master, USER_B, media_id, 0),
        vault.file_key(master, USER_A, uuid.uuid4(), 0),
        vault.file_key(master, USER_A, media_id, 1),
    }
    assert len(keys) == 4 and master not in keys


def test_thumbnail_variant_is_not_interchangeable(master):
    media_id = uuid.uuid4()
    main = vault.encrypt(master, USER_A, media_id, PLAIN)
    thumb = vault.encrypt(master, USER_A, media_id, PLAIN, variant=b"thumb")

    assert vault.decrypt(master, USER_A, media_id, thumb, variant=b"thumb") == PLAIN
    with pytest.raises(VaultIntegrityError):
        vault.decrypt(master, USER_A, media_id, thumb)
    with pytest.raises(VaultIntegrityError):
        vault.decrypt(master, USER_A, media_id, main, variant=b"thumb")
    assert vault.file_key(master, USER_A, media_id, 0) != vault.file_key(master, USER_A, media_id, 0, b"thumb")


def test_media_path_shards_by_prefix_and_write_is_atomic(tmp_path):
    media_id = uuid.uuid4()
    path = vault.media_path(tmp_path, media_id)
    assert path == tmp_path / media_id.hex[:2] / f"{media_id}.enc"

    vault.write_atomic(path, b"conteudo")
    vault.write_atomic(path, b"novo")
    assert path.read_bytes() == b"novo"
    assert [p.name for p in path.parent.iterdir()] == [path.name]  # nenhum .tmp sobra


def test_recovery_code_roundtrip_and_typo_detection():
    key = media_key.generate_key()
    code = media_key.recovery_code(key)

    assert media_key.key_from_recovery(code) == key
    assert media_key.key_from_recovery(code.lower().replace("-", " ")) == key
    typo = ("B" if code[0] != "B" else "C") + code[1:]
    with pytest.raises(MediaKeyError):
        media_key.key_from_recovery(typo)
    with pytest.raises(MediaKeyError):
        media_key.key_from_recovery("abc")


def test_fingerprint_is_stable_short_and_does_not_reveal_key():
    key = media_key.generate_key()
    assert media_key.fingerprint(key) == media_key.fingerprint(key)
    assert len(media_key.fingerprint(key)) == 16
    assert media_key.fingerprint(key) != media_key.fingerprint(media_key.generate_key())
    assert media_key.fingerprint(key) not in key.hex()


def test_env_key_validation(monkeypatch):
    monkeypatch.setenv("LEITORUM_MEDIA_MASTER_KEY", "nao-e-base64!!")
    with pytest.raises(MediaKeyError):
        media_key.load_master_key()
    monkeypatch.setenv("LEITORUM_MEDIA_MASTER_KEY", "AAAA")
    with pytest.raises(MediaKeyError):
        media_key.load_master_key()


def test_missing_key_returns_none(tmp_path, monkeypatch):
    monkeypatch.delenv("LEITORUM_MEDIA_MASTER_KEY", raising=False)
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(tmp_path / "nao-existe.key"))
    assert media_key.load_master_key() is None


def test_key_file_is_refused_inside_storage_root(tmp_path, monkeypatch):
    root = tmp_path / "HD"
    root.mkdir()
    monkeypatch.setenv("LEITORUM_STORAGE_ROOT", str(root))
    with pytest.raises(MediaKeyError):
        media_key.write_key_file(media_key.generate_key(), root / "chave" / "media-master.key")
    assert not (root / "chave").exists()


def test_dpapi_protects_in_machine_scope_for_the_windows_service():
    # O serviço (LocalSystem) e o terminal do usuário precisam abrir o mesmo arquivo de chave.
    assert media_key.PROTECT_FLAGS & media_key.CRYPTPROTECT_LOCAL_MACHINE
    assert media_key.PROTECT_FLAGS & media_key.CRYPTPROTECT_UI_FORBIDDEN
    assert not media_key.UNPROTECT_FLAGS & media_key.CRYPTPROTECT_LOCAL_MACHINE


def test_key_file_path_comes_from_env(tmp_path, monkeypatch):
    path = tmp_path / "Leitorum" / "media-master.key"
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(path))
    assert media_key.key_file_path() == path
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", "relativo\\media-master.key")
    with pytest.raises(MediaKeyError):
        media_key.key_file_path()


@pytest.mark.skipif(os.name != "nt", reason="DPAPI só existe no Windows")
def test_dpapi_key_file_roundtrip_and_no_overwrite(tmp_path, monkeypatch):
    monkeypatch.delenv("LEITORUM_MEDIA_MASTER_KEY", raising=False)
    monkeypatch.delenv("LEITORUM_STORAGE_ROOT", raising=False)
    path = tmp_path / "Leitorum" / "media-master.key"
    monkeypatch.setenv("LEITORUM_MEDIA_KEY_FILE", str(path))
    key = media_key.generate_key()

    media_key.write_key_file(key)
    raw = path.read_bytes()
    assert raw.startswith(media_key.FILE_PREFIX) and key not in raw
    assert media_key.load_master_key() == key
    with pytest.raises(MediaKeyError):
        media_key.write_key_file(media_key.generate_key())
    assert media_key.load_master_key() == key
