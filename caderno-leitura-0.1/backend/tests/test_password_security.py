from __future__ import annotations

import pytest

from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    needs_rehash,
    verify_password,
)
from app.core.user_agent import parse_device_name


def test_hash_password_produces_argon2id_format():
    password = "SenhaSuperSecreta123!"
    h = hash_password(password)

    # Verifica se o hash gerado é uma string válida no formato Argon2id da especificação OWASP
    assert isinstance(h, str)
    assert h.startswith("$argon2id$v=19$m=65536,t=2,p=1$")


def test_verify_password_success_and_failure():
    password = "OutraSenhaDeTeste456@"
    h = hash_password(password)

    assert verify_password(h, password) is True
    assert verify_password(h, "SenhaIncorreta123") is False
    assert verify_password(h, "") is False
    assert verify_password("", password) is False
    assert verify_password("hash_corrompido_invalido", password) is False


def test_hash_password_empty_raises_value_error():
    with pytest.raises(ValueError, match="A senha não pode ser vazia"):
        hash_password("")

    with pytest.raises(ValueError, match="A senha não pode ser vazia"):
        hash_password("   ")


def test_needs_rehash():
    password = "TesteDeRehash789#"
    h = hash_password(password)
    assert needs_rehash(h) is False
    assert needs_rehash("hash_invalido") is True


def test_session_token_generation_and_hashing():
    token1 = generate_session_token()
    token2 = generate_session_token()

    assert isinstance(token1, str)
    assert len(token1) >= 40  # secrets.token_urlsafe(32) gera 43 caracteres
    assert token1 != token2

    h1 = hash_session_token(token1)
    h2 = hash_session_token(token2)

    assert len(h1) == 64  # SHA-256 hexadecimal
    assert len(h2) == 64
    assert h1 != h2
    assert hash_session_token(token1) == h1  # Determinístico para o mesmo token


def test_device_name_parsing():
    # Windows + Chrome
    ua_win_chrome = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    assert parse_device_name(ua_win_chrome) == "Chrome no Windows"

    # iPhone + Safari
    ua_iphone = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    assert parse_device_name(ua_iphone) == "Safari no iPhone"

    # Android + Chrome
    ua_android = "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36"
    assert parse_device_name(ua_android) == "Chrome no Android"

    # Linux + Firefox
    ua_linux_ff = "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
    assert parse_device_name(ua_linux_ff) == "Firefox no Linux"

    # Cliente de Teste / Script
    assert parse_device_name("pytest/8.0.0") == "Cliente de Teste / API"
    assert parse_device_name("python-httpx/0.27.0") == "Cliente de Teste / API"

    # Vazio / Desconhecido
    assert parse_device_name("") == "Dispositivo Desconhecido"
    assert parse_device_name(None) == "Dispositivo Desconhecido"
