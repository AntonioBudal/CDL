from __future__ import annotations

import hashlib
import logging
import secrets

import argon2
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

logger = logging.getLogger(__name__)

# Parâmetros padrão recomendados pela OWASP para Argon2id:
# - Type: Argon2id
# - Time cost: 2 iterações
# - Memory cost: 64 MiB (65536 KiB)
# - Parallelism: 1 thread
# - Hash len: 32 bytes
_hasher = argon2.PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    type=argon2.Type.ID,
)


def hash_password(password: str) -> str:
    """Gera um hash adaptativo e seguro da senha informada utilizando Argon2id."""
    if not password or len(password.strip()) == 0:
        raise ValueError("A senha não pode ser vazia.")
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash Argon2id armazenado."""
    if not password_hash or not password:
        return False
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception as exc:
        logger.warning("Erro inesperado durante verificação de senha: %s", exc)
        return False


def needs_rehash(password_hash: str) -> bool:
    """Verifica se os parâmetros do hash estão desatualizados e requerem re-derivação."""
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:
        return True


def generate_session_token() -> str:
    """Gera um identificador de sessão opaco, imprevisível e de alta entropia (256 bits)."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Gera o hash criptográfico SHA-256 para persistência segura do token de sessão no banco."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
