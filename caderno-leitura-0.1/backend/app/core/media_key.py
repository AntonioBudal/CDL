"""Chave mestra do cofre de imagens (feature 090-B): fora do HD, protegida pelo Windows (DPAPI).

Ordem de carga:
1. ``LEITORUM_MEDIA_MASTER_KEY`` (base64 de 32 bytes), para ambientes sem DPAPI;
2. arquivo ``LEITORUM_MEDIA_KEY_FILE`` (padrão ``%LOCALAPPDATA%\\Leitorum\\media-master.key``),
   protegido por DPAPI no escopo da máquina.

Escopo da máquina porque o servidor roda como serviço do Windows (``LocalSystem``) e os scripts de instalação
rodam com o usuário: com o escopo do usuário, o serviço não abriria a chave. Quem protege o arquivo é a pasta do
perfil (só o usuário, ``SYSTEM`` e administradores leem). Por isso o ``.env`` deve fixar
``LEITORUM_MEDIA_KEY_FILE``: o ``%LOCALAPPDATA%`` do serviço é outro.

A chave nunca pode ficar dentro de ``LEITORUM_STORAGE_ROOT`` (o HD): quem copiar o disco não leva a chave.
Nada aqui registra a chave ou o código de recuperação em log.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

KEY_BYTES = 32
FILE_PREFIX = b"LMKEY1"
SALT = b"leitorum-media-v1"
CRYPTPROTECT_UI_FORBIDDEN = 0x01
CRYPTPROTECT_LOCAL_MACHINE = 0x04
# O escopo fica gravado no próprio blob: a leitura não precisa (nem aceita) o flag de máquina, e blobs antigos
# no escopo do usuário continuam abrindo para esse usuário.
PROTECT_FLAGS = CRYPTPROTECT_UI_FORBIDDEN | CRYPTPROTECT_LOCAL_MACHINE
UNPROTECT_FLAGS = CRYPTPROTECT_UI_FORBIDDEN


class MediaKeyError(RuntimeError):
    """Chave ausente, ilegível, no lugar proibido ou com código de recuperação inválido."""


# --- DPAPI (Windows) ----------------------------------------------------------------------------


def _dpapi(data: bytes, protect: bool) -> bytes:
    if os.name != "nt":
        raise MediaKeyError("A proteção DPAPI só existe no Windows; use LEITORUM_MEDIA_MASTER_KEY.")
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    buffer = ctypes.create_string_buffer(data, len(data))
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char)))
    target = Blob()
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    if protect:
        ok = crypt32.CryptProtectData(ctypes.byref(source), "Leitorum", None, None, None, PROTECT_FLAGS,
                                      ctypes.byref(target))
    else:
        ok = crypt32.CryptUnprotectData(ctypes.byref(source), None, None, None, None, UNPROTECT_FLAGS,
                                        ctypes.byref(target))
    if not ok:
        raise MediaKeyError("O Windows não conseguiu proteger ou abrir a chave (DPAPI).")
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel32.LocalFree(target.pbData)


# --- localização e barreira "fora do HD" -------------------------------------------------------


def key_file_path() -> Path:
    import app.core.config  # noqa: F401 — garante o .env carregado (LEITORUM_MEDIA_KEY_FILE) também nos scripts

    configured = os.environ.get("LEITORUM_MEDIA_KEY_FILE", "").strip()
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise MediaKeyError("LEITORUM_MEDIA_KEY_FILE deve ser um caminho absoluto.")
        return path
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "Leitorum" / "media-master.key"


def ensure_outside_storage(path: Path) -> None:
    """Recusa qualquer caminho de chave dentro da raiz de armazenamento (HD)."""
    from app.core.config import get_storage_root

    root = get_storage_root()
    if root is None:
        return
    resolved = os.path.normcase(str(path.resolve()))
    root_resolved = os.path.normcase(str(root.resolve()))
    if resolved == root_resolved or resolved.startswith(root_resolved.rstrip("\\/") + os.sep):
        raise MediaKeyError("A chave do cofre não pode ficar dentro da pasta de armazenamento (HD).")


# --- carga, geração e recuperação --------------------------------------------------------------


def load_master_key() -> bytes | None:
    """Chave mestra, ou ``None`` se nenhuma estiver configurada. Configuração inválida levanta erro."""
    from app.core.config import BACKEND_DIR

    configured = os.environ.get("LEITORUM_MEDIA_MASTER_KEY", "").strip()
    if configured:
        for env_file in (BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"):
            if env_file.is_file():
                ensure_outside_storage(env_file)
        try:
            key = base64.b64decode(configured, validate=True)
        except (binascii.Error, ValueError) as error:
            raise MediaKeyError("LEITORUM_MEDIA_MASTER_KEY não é base64 válido.") from error
        if len(key) != KEY_BYTES:
            raise MediaKeyError("LEITORUM_MEDIA_MASTER_KEY precisa ter 32 bytes.")
        return key
    path = key_file_path()
    if not path.is_file():
        return None
    ensure_outside_storage(path)
    raw = path.read_bytes()
    if not raw.startswith(FILE_PREFIX):
        raise MediaKeyError("O arquivo da chave do cofre está ilegível.")
    key = _dpapi(raw[len(FILE_PREFIX):], protect=False)
    if len(key) != KEY_BYTES:
        raise MediaKeyError("O arquivo da chave do cofre está ilegível.")
    return key


def write_key_file(key: bytes, path: Path | None = None) -> Path:
    """Grava a chave protegida por DPAPI; recusa sobrescrever e recusa caminho dentro do HD."""
    path = path or key_file_path()
    ensure_outside_storage(path)
    if path.exists():
        raise MediaKeyError("Já existe um arquivo de chave; não será sobrescrito.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(FILE_PREFIX + _dpapi(key, protect=True))
    os.replace(temporary, path)
    return path


def generate_key() -> bytes:
    return os.urandom(KEY_BYTES)


def fingerprint(key: bytes) -> str:
    """Impressão digital curta (16 hex) para conferir a chave sem guardá-la."""
    return HKDF(algorithm=hashes.SHA256(), length=8, salt=SALT, info=b"fingerprint").derive(key).hex()


def recovery_code(key: bytes) -> str:
    """Código de recuperação: chave + 2 bytes de verificação, em base32, em grupos de 4."""
    payload = key + hashlib.sha256(key).digest()[:2]
    text = base64.b32encode(payload).decode("ascii").rstrip("=")
    return "-".join(text[i:i + 4] for i in range(0, len(text), 4))


def key_from_recovery(code: str) -> bytes:
    text = "".join(ch for ch in code.upper() if ch.isalnum())
    text += "=" * (-len(text) % 8)
    try:
        payload = base64.b32decode(text)
    except (binascii.Error, ValueError) as error:
        raise MediaKeyError("Código de recuperação inválido.") from error
    key, check = payload[:KEY_BYTES], payload[KEY_BYTES:]
    if len(key) != KEY_BYTES or hashlib.sha256(key).digest()[:2] != check:
        raise MediaKeyError("Código de recuperação inválido (conferência falhou).")
    return key
