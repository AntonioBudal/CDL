"""F0.10.10 (spec 102): enquanto /compartilhado/{id} não existir no frontend, robots.txt e sitemap não a anunciam."""
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.services import seo_service
from app.core.config import DEFAULT_OWNER_ID
from tests.test_seo_and_public_presence import seo_client  # noqa: F401  (fixture reaproveitada)


def test_flag_is_off_by_default():
    assert seo_service.PUBLIC_STUDY_PAGES_ENABLED is False


def test_robots_does_not_allow_shared_route_when_off(seo_client):  # noqa: F811
    client, _ = seo_client
    content = client.get("/robots.txt").text
    assert "/compartilhado/" not in content
    assert "Allow: /sobre" in content
    assert "Disallow: /api/" in content
    assert "Sitemap:" in content


def test_sitemap_lists_only_institutional_pages_when_off(seo_client):  # noqa: F811
    client, session_factory = seo_client
    with session_factory() as session:
        book = Book(id=900, user_id=DEFAULT_OWNER_ID, title="Livro de Teste Público", visibility="public")
        chapter = Chapter(id=900, book_id=900, name="Capítulo 1")
        study = Study(id=900, user_id=DEFAULT_OWNER_ID, chapter_id=900, title="Estudo Público de Teste",
                      summary="Resumo fictício.", visibility="public")
        session.add_all([book, chapter, study])
        session.commit()
    xml_text = client.get("/sitemap.xml").text
    assert "/compartilhado/" not in xml_text
    for path in ("/</loc>", "/sobre</loc>", "/apoie</loc>"):
        assert path in xml_text
