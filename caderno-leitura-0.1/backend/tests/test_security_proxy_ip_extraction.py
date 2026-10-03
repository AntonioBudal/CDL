import pytest
from starlette.requests import Request

from app.core.rate_limiter import _sanitize_ip_string, get_client_ip


def make_dummy_request(headers: dict[str, str] | None = None, client_host: str | None = None) -> Request:
    """Cria um objeto Request isolado para testes rápidos de cabeçalhos."""
    header_list = []
    if headers:
        for k, v in headers.items():
            header_list.append((k.lower().encode("latin-1"), v.encode("latin-1")))

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/test",
        "headers": header_list,
        "client": (client_host, 12345) if client_host else None,
    }
    return Request(scope)


def test_sanitize_ip_string():
    """Valida limpeza e verificação sintática de IPs."""
    assert _sanitize_ip_string("192.168.1.1") == "192.168.1.1"
    assert _sanitize_ip_string("  10.0.0.5  ") == "10.0.0.5"
    assert _sanitize_ip_string("172.16.0.1:8080") == "172.16.0.1"
    assert _sanitize_ip_string("[2001:db8::1]:443") == "2001:db8::1"
    assert _sanitize_ip_string("2001:db8::1") == "2001:db8::1"

    # Valores inválidos ou maliciosos devem retornar None
    assert _sanitize_ip_string("invalid-ip") is None
    assert _sanitize_ip_string("192.168.1.300") is None
    assert _sanitize_ip_string("127.0.0.1; DROP TABLE") is None
    assert _sanitize_ip_string("") is None
    assert _sanitize_ip_string(None) is None


def test_cf_connecting_ip_has_highest_precedence():
    """Garante que CF-Connecting-IP (Cloudflare Tunnel) tenha prioridade máxima sobre X-Forwarded-For."""
    req = make_dummy_request(
        headers={
            "cf-connecting-ip": "203.0.113.195",
            "x-forwarded-for": "198.51.100.1, 10.0.0.1",
            "x-real-ip": "10.0.0.2",
        },
        client_host="127.0.0.1",
    )
    assert get_client_ip(req) == "203.0.113.195"


def test_x_forwarded_for_first_client_ip():
    """Garante extração do primeiro IP da cadeia de proxies no X-Forwarded-For."""
    req = make_dummy_request(
        headers={
            "x-forwarded-for": "198.51.100.42, 10.0.0.1, 172.16.0.2",
            "x-real-ip": "10.0.0.1",
        },
        client_host="127.0.0.1",
    )
    assert get_client_ip(req) == "198.51.100.42"


def test_x_real_ip_when_no_forwarded():
    """Garante que X-Real-IP seja usado caso X-Forwarded-For e CF não existam."""
    req = make_dummy_request(
        headers={"x-real-ip": "192.0.2.1"},
        client_host="127.0.0.1",
    )
    assert get_client_ip(req) == "192.0.2.1"


def test_client_host_fallback():
    """Garante fallback para o socket direto do cliente se nenhum header de proxy estiver presente."""
    req = make_dummy_request(client_host="192.168.0.50")
    assert get_client_ip(req) == "192.168.0.50"


def test_malicious_proxy_header_safe_fallback():
    """Garante que tentativas de injeção em cabeçalhos de proxy resultem no fallback 127.0.0.1 ou socket."""
    req = make_dummy_request(
        headers={"cf-connecting-ip": "attack-string'; SELECT 1--"},
        client_host=None,
    )
    assert get_client_ip(req) == "127.0.0.1"
