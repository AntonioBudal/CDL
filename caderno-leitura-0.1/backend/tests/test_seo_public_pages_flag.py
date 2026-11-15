"""F0.10.10 (spec 102) → F0.12.02 (spec 115): a rota /compartilhado/{id} existe; o robots.txt a permite e o sitemap
lista só estudos **publicados na web** pelo dono. "Público" para a instalação (visibility) não basta."""
from app.core.config import DEFAULT_OWNER_ID
from app.db.types import utc_now
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.services import seo_service
from tests.test_seo_and_public_presence import seo_client  # noqa: F401  (fixture reaproveitada)


def test_shared_pages_exist_since_0_12():
    assert seo_service.PUBLIC_STUDY_PAGES_ENABLED is True


def test_robots_allows_shared_route(seo_client):  # noqa: F811
    client, _ = seo_client
    content = client.get("/robots.txt").text
    assert "Allow: /compartilhado/" in content
    assert "Disallow: /api/" in content


def test_sitemap_lists_only_published_studies(seo_client):  # noqa: F811
    client, session_factory = seo_client
    with session_factory() as session:
        book = Book(id=900, user_id=DEFAULT_OWNER_ID, title="Livro de Teste Público", visibility="public")
        chapter = Chapter(id=900, book_id=900, name="Capítulo 1")
        public_only = Study(id=900, user_id=DEFAULT_OWNER_ID, chapter_id=900, title="Estudo Público de Teste",
                            summary="Resumo fictício.", visibility="public")
        published = Study(id=901, user_id=DEFAULT_OWNER_ID, chapter_id=900, title="Estudo Publicado de Teste",
                          summary="Resumo fictício.", visibility="private", published_at=utc_now())
        session.add_all([book, chapter, public_only, published])
        session.commit()
    xml_text = client.get("/sitemap.xml").text
    assert "/compartilhado/900" not in xml_text, "público na instalação, mas não publicado na web"
    assert "/compartilhado/901</loc>" in xml_text
    for path in ("/</loc>", "/sobre</loc>", "/apoie</loc>"):
        assert path in xml_text
