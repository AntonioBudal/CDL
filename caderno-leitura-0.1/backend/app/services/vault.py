"""Formato ``.enc`` v1 do cofre de imagens (feature 090-B): AES-256-GCM com chave por arquivo via HKDF.

Cabeçalho fixo de 36 bytes (research R2):

    0  4  magic "LMV1"      4  1  versão (1)     5  1  cifra (1 = AES-256-GCM)
    6  1  KDF (1 = HKDF)    7  1  época da chave 8  16 media_id (UUID)   24 12 nonce

seguido do texto cifrado com a tag GCM de 16 bytes no fim. Os dados associados são o cabeçalho mais o
``user_id``: um arquivo copiado para outro usuário ou outra mídia não abre. A miniatura guardada
(``<uuid>.thumb.enc``) usa a variante ``thumb`` na derivação e nos dados associados, então não pode ser
trocada pelo arquivo principal.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MAGIC = b"LMV1"
FORMAT_VERSION = 1
CIPHER_AES_GCM = 1
KDF_HKDF = 1
HEADER_LEN = 36
SALT = b"leitorum-media-v1"


class VaultIntegrityError(RuntimeError):
    """Arquivo adulterado, corrompido, de outra mídia ou aberto com a chave errada."""


def file_key(master: bytes, user_id: str, media_id: uuid.UUID, epoch: int, variant: bytes = b"") -> bytes:
    info = b"media|" + user_id.encode("utf-8") + b"|" + str(media_id).encode("ascii") + b"|" + str(epoch).encode("ascii")
    if variant:
        info += b"|" + variant
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=SALT, info=info).derive(master)


def header(media_id: uuid.UUID, nonce: bytes, epoch: int) -> bytes:
    return MAGIC + bytes([FORMAT_VERSION, CIPHER_AES_GCM, KDF_HKDF, epoch]) + media_id.bytes + nonce


def _aad(head: bytes, user_id: str, variant: bytes) -> bytes:
    return head + user_id.encode("utf-8") + (b"|" + variant if variant else b"")


def encrypt(master: bytes, user_id: str, media_id: uuid.UUID, plaintext: bytes, epoch: int = 0,
            variant: bytes = b"") -> bytes:
    nonce = os.urandom(12)
    head = header(media_id, nonce, epoch)
    key = file_key(master, user_id, media_id, epoch, variant)
    return head + AESGCM(key).encrypt(nonce, plaintext, _aad(head, user_id, variant))


def decrypt(master: bytes, user_id: str, media_id: uuid.UUID, blob: bytes, variant: bytes = b"") -> bytes:
    if len(blob) < HEADER_LEN + 16 or blob[:4] != MAGIC:
        raise VaultIntegrityError("Arquivo do cofre com formato desconhecido.")
    version, cipher, kdf, epoch = blob[4], blob[5], blob[6], blob[7]
    if (version, cipher, kdf) != (FORMAT_VERSION, CIPHER_AES_GCM, KDF_HKDF):
        raise VaultIntegrityError("Versão do arquivo do cofre não suportada.")
    if uuid.UUID(bytes=blob[8:24]) != media_id:
        raise VaultIntegrityError("O arquivo do cofre pertence a outra mídia.")
    head, nonce = blob[:HEADER_LEN], blob[24:HEADER_LEN]
    try:
        key = file_key(master, user_id, media_id, epoch, variant)
        return AESGCM(key).decrypt(nonce, blob[HEADER_LEN:], _aad(head, user_id, variant))
    except InvalidTag as error:
        raise VaultIntegrityError("O arquivo do cofre não passou na autenticação.") from error


def media_path(vault_dir: Path, media_id: uuid.UUID) -> Path:
    return vault_dir / media_id.hex[:2] / f"{media_id}.enc"


def thumb_path(vault_dir: Path, media_id: uuid.UUID) -> Path:
    return vault_dir / media_id.hex[:2] / f"{media_id}.thumb.enc"


def write_atomic(path: Path, data: bytes) -> None:
    """Grava em ``.tmp`` na mesma pasta, faz ``fsync`` e troca de uma vez."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with open(temporary, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
