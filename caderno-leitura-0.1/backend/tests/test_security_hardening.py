"""F0.10.02 — CSP sem domínios externos, rotas públicas do X-Robots-Tag, conferência de origem e security.txt."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.user import User


@pytest.fixture
def hardening_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    """Cliente hermético com banco SQLite descartável em tmp_path, sem Google configurado."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("LEITORUM_TRUSTED_ORIGINS", raising=False)
    monkeypatch.delenv("LEITORUM_SECURITY_CONTACT", raising=False)
    engine = create_engine(f"sqlite:///{(tmp_path / 'hardening.db').as_posix()}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
    with local() as session:
        session.add(User(id=DEFAULT_OWNER_ID, username=DEFAULT_OWNER_USERNAME, display_name="Dona Fictícia", role="admin", status="ativo"))
        session.commit()

    application = create_app()

    def override_get_session():
        session = local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application.dependency_overrides[get_session] = override_get_session
    with TestClient(application) as client:
        yield client


def _directive(csp: str, name: str) -> str:
    for part in csp.split(";"):
        part = part.strip()
        if part.startswith(name + " ") or part == name:
            return part
    return ""


# --- US1: CSP -----------------------------------------------------------------------------------------------------


def test_csp_without_google_has_no_external_domain(hardening_client):
    csp = hardening_client.get("/api/health").headers["Content-Security-Policy"]
    assert "https://" not in csp, csp
    assert _directive(csp, "script-src") == "script-src 'self'"
    assert _directive(csp, "img-src") == "img-src 'self' data: blob:"
    assert _directive(csp, "connect-src") == "connect-src 'self'"
    assert _directive(csp, "frame-src") == "frame-src 'self'"
    assert _directive(csp, "object-src") == "object-src 'none'"
    assert "fonts.googleapis.com" not in csp and "fonts.gstatic.com" not in csp


def test_csp_with_google_adds_only_accounts_google(hardening_client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cliente-ficticio.apps.googleusercontent.com")
    csp = hardening_client.get("/api/health").headers["Content-Security-Policy"]
    for name in ("script-src", "connect-src", "frame-src"):
        assert _directive(csp, name) == f"{name} 'self' https://accounts.google.com", csp
    externals = {token for token in csp.replace(";", " ").split() if token.startswith("https://")}
    assert externals == {"https://accounts.google.com"}
    assert "'unsafe-inline'" not in _directive(csp, "script-src")


def test_referrer_policy_is_same_origin(hardening_client):
    assert hardening_client.get("/api/health").headers["Referrer-Policy"] == "same-origin"


# --- US3: X-Robots-Tag por lista de rotas públicas --------------------------------------------------------------


@pytest.mark.parametrize("path", ["/", "/sobre", "/apoie", "/compartilhado/1", "/robots.txt", "/sitemap.xml", "/.well-known/security.txt"])
def test_public_routes_are_indexable(hardening_client, path):
    response = hardening_client.get(path)
    assert "X-Robots-Tag" not in response.headers, path


@pytest.mark.parametrize("path", ["/destaques", "/revisao", "/inbox", "/ajustes", "/login", "/@alguem", "/rota-que-nao-existe", "/api/health"])
def test_private_routes_are_noindex(hardening_client, path):
    assert hardening_client.get(path).headers.get("X-Robots-Tag") == "noindex, nofollow", path


# --- US4: conferência de origem ---------------------------------------------------------------------------------


def _count_books(client: TestClient) -> int:
    return len(client.get("/api/books").json())


def test_post_from_foreign_origin_is_rejected_and_nothing_is_saved(hardening_client):
    before = _count_books(hardening_client)
    response = hardening_client.post("/api/books", json={"title": "Livro de Teste"}, headers={"Origin": "https://malicioso.example"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Origem do pedido não autorizada."}
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert _count_books(hardening_client) == before


def test_post_from_same_origin_passes(hardening_client):
    response = hardening_client.post("/api/books", json={"title": "Livro de Teste"}, headers={"Origin": "http://testserver"})
    assert response.status_code == 201


def test_post_behind_proxy_with_forwarded_host_passes(hardening_client):
    response = hardening_client.post(
        "/api/books",
        json={"title": "Livro de Teste"},
        headers={"Origin": "https://pc-ficticio.tailnet.ts.net", "X-Forwarded-Host": "pc-ficticio.tailnet.ts.net"},
    )
    assert response.status_code == 201


def test_post_without_origin_but_cross_site_fetch_is_rejected(hardening_client):
    response = hardening_client.post("/api/books", json={"title": "Livro de Teste"}, headers={"Sec-Fetch-Site": "cross-site"})
    assert response.status_code == 403


def test_post_without_origin_and_fetch_metadata_passes(hardening_client):
    assert hardening_client.post("/api/books", json={"title": "Livro de Teste"}).status_code == 201


def test_null_origin_is_rejected(hardening_client):
    response = hardening_client.post("/api/books", json={"title": "Livro de Teste"}, headers={"Origin": "null"})
    assert response.status_code == 403


def test_get_from_foreign_origin_is_not_checked(hardening_client):
    assert hardening_client.get("/api/books", headers={"Origin": "https://malicioso.example"}).status_code == 200


def test_trusted_origin_from_env_passes(hardening_client, monkeypatch):
    monkeypatch.setenv("LEITORUM_TRUSTED_ORIGINS", "https://leitura.exemplo.test, https://outro.exemplo.test")
    response = hardening_client.post("/api/books", json={"title": "Livro de Teste"}, headers={"Origin": "https://outro.exemplo.test"})
    assert response.status_code == 201


# --- US5: security.txt ------------------------------------------------------------------------------------------


def _fields(body: str) -> dict[str, str]:
    out = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return out


def test_security_txt_default_contact_and_expiry(hardening_client):
    response = hardening_client.get("/.well-known/security.txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    fields = _fields(response.text)
    assert fields["Contact"] == "https://github.com/AntonioBudal/CDL/security/advisories/new"
    expires = datetime.strptime(fields["Expires"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    now = datetime.now(UTC)
    assert now < expires <= now + timedelta(days=366)
    assert fields["Preferred-Languages"] == "pt, en"
    assert fields["Canonical"] == "http://testserver/.well-known/security.txt"


def test_security_txt_contact_from_env(hardening_client, monkeypatch):
    monkeypatch.setenv("LEITORUM_SECURITY_CONTACT", "mailto:seguranca@exemplo.test")
    assert _fields(hardening_client.get("/.well-known/security.txt").text)["Contact"] == "mailto:seguranca@exemplo.test"
