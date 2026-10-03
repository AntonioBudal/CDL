from __future__ import annotations

from typing import Generator
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DEFAULT_OWNER_ID, DEFAULT_OWNER_USERNAME
from app.db.base import Base
from app.db.session import get_session
from app.db.types import utc_now
from app.main import create_app
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.models.user import User


@pytest.fixture
def seo_client(tmp_path, monkeypatch) -> Generator[tuple[TestClient, sessionmaker], None, None]:
    """Cria um cliente de testes isolado com banco SQLite descartável em tmp_path."""
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    db_file = tmp_path / "test_seo.db"
    engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    with testing_session_local() as session:
        user = User(
            id=DEFAULT_OWNER_ID,
            username=DEFAULT_OWNER_USERNAME,
            display_name="Proprietário Teste",
            role="admin",
            status="ativo",
        )
        session.add(user)
        session.commit()

    application = create_app()

    def override_get_session():
        session = testing_session_local()
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
        yield client, testing_session_local

    application.dependency_overrides.clear()


def test_robots_txt_spec_compliance(seo_client):
    """Verifica se /robots.txt segue as regras de permissão de rotas públicas e bloqueio de rotas privadas."""
    client, _ = seo_client
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")

    content = response.text
    assert "User-agent: *" in content
    assert "Allow: /" in content
    assert "Allow: /sobre" in content
    assert "Allow: /apoie" in content
    assert "Allow: /compartilhado/" in content
    assert "Disallow: /api/" in content
    assert "Disallow: /dashboard" in content
    assert "Disallow: /livros" in content
    assert "Disallow: /admin" in content
    assert "Disallow: /estudos/" in content
    assert "Sitemap:" in content
    assert "/sitemap.xml" in content

    # robots.txt em si não deve ter X-Robots-Tag: noindex
    assert "X-Robots-Tag" not in response.headers


def test_site_webmanifest_endpoint(seo_client):
    """Verifica se /site.webmanifest retorna o manifesto da aplicação com metadados corretos."""
    client, _ = seo_client
    response = client.get("/site.webmanifest")
    assert response.status_code == 200
    assert "application/manifest+json" in response.headers.get("content-type", "")

    data = response.json()
    assert data["name"] == "Leitorum — Caderno de Leitura"
    assert data["short_name"] == "Leitorum"
    assert data["start_url"] == "/"
    assert len(data["icons"]) >= 2


def test_x_robots_tag_middleware_protection(seo_client):
    """Verifica se rotas da API emitem X-Robots-Tag: noindex, nofollow (Princípio I / Cenário 4 Quickstart)."""
    client, _ = seo_client
    response_health = client.get("/api/health")
    assert response_health.status_code == 200
    assert response_health.headers.get("X-Robots-Tag") == "noindex, nofollow"

    response_books = client.get("/api/books")
    assert response_books.status_code in (200, 401)
    assert response_books.headers.get("X-Robots-Tag") == "noindex, nofollow"


def test_sitemap_xml_generation_and_strict_privacy(seo_client):
    """Verifica a geração do sitemap.xml e a exclusão estrita de estudos privados ou excluídos."""
    client, session_maker = seo_client

    with session_maker() as session:
        # Livro 1: Privado
        book_priv = Book(
            id=10,
            user_id=DEFAULT_OWNER_ID,
            title="Livro Privado Secreto",
            visibility="private",
        )
        chap_priv = Chapter(id=100, book_id=10, name="Capítulo Privado", position=1)

        # Livro 2: Público
        book_pub = Book(
            id=20,
            user_id=DEFAULT_OWNER_ID,
            title="Livro Filosofia Aberta",
            visibility="public",
        )
        chap_pub = Chapter(id=200, book_id=20, name="Capítulo Aberto", position=1)

        # Estudo A: Estudo público direto (ID 1)
        study_pub = Study(
            id=1,
            user_id=DEFAULT_OWNER_ID,
            chapter_id=100,
            title="Estudo Público de Teste",
            summary="Resumo público",
            visibility="public",
        )

        # Estudo B: Estudo privado (ID 2)
        study_priv = Study(
            id=2,
            user_id=DEFAULT_OWNER_ID,
            chapter_id=100,
            title="Estudo Privado Pessoal",
            summary="Notas íntimas e privadas",
            visibility="private",
        )

        # Estudo C: Estudo herdado de livro público (ID 3)
        study_inherit_pub = Study(
            id=3,
            user_id=DEFAULT_OWNER_ID,
            chapter_id=200,
            title="Estudo Herdado Público",
            summary="Resumo herdado",
            visibility="inherit",
        )

        # Estudo D: Estudo herdado de livro privado (ID 4)
        study_inherit_priv = Study(
            id=4,
            user_id=DEFAULT_OWNER_ID,
            chapter_id=100,
            title="Estudo Herdado Privado",
            summary="Resumo privado",
            visibility="inherit",
        )

        # Estudo E: Estudo público na lixeira (ID 5)
        study_deleted = Study(
            id=5,
            user_id=DEFAULT_OWNER_ID,
            chapter_id=200,
            title="Estudo Deletado",
            summary="Resumo deletado",
            visibility="public",
            deleted_at=utc_now(),
        )

        session.add_all([
            book_priv,
            chap_priv,
            book_pub,
            chap_pub,
            study_pub,
            study_priv,
            study_inherit_pub,
            study_inherit_priv,
            study_deleted,
        ])
        session.commit()

    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("content-type", "")

    xml_text = response.text
    # Páginas institucionais canônicas
    assert "<loc>" in xml_text
    assert "/sobre</loc>" in xml_text
    assert "/apoie</loc>" in xml_text

    # Estudo público direto (ID 1) e Estudo herdado público (ID 3) DEVEM estar presentes
    assert "/compartilhado/1</loc>" in xml_text
    assert "/compartilhado/3</loc>" in xml_text

    # Estudo privado (ID 2), estudo herdado de livro privado (ID 4) e excluído (ID 5) NUNCA devem estar presentes
    assert "/compartilhado/2" not in xml_text
    assert "/compartilhado/4" not in xml_text
    assert "/compartilhado/5" not in xml_text

    # Nenhum título ou resumo do acervo deve vazar no XML
    assert "Estudo Privado Pessoal" not in xml_text
    assert "Notas íntimas e privadas" not in xml_text
    assert "Livro Privado Secreto" not in xml_text
