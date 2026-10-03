from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_app_base_url
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study
from app.schemas.seo import SitemapItem


def generate_robots_txt(base_url: str | None = None) -> str:
    """Gera o conteúdo de texto puro do arquivo robots.txt com regras estritas de rastreamento."""
    base = (base_url or get_app_base_url()).rstrip("/")
    return f"""User-agent: *
Allow: /
Allow: /sobre
Allow: /apoie
Allow: /compartilhado/
Disallow: /api/
Disallow: /dashboard
Disallow: /livros
Disallow: /admin
Disallow: /estudos/
Sitemap: {base}/sitemap.xml
"""


def get_public_sitemap_items(session: Session, base_url: str | None = None) -> list[SitemapItem]:
    """Retorna a lista de URLs públicas indexáveis (páginas institucionais e estudos públicos ativos).

    Garante exclusão estrita de estudos privados ou marcados como deletados (Princípio I).
    """
    base = (base_url or get_app_base_url()).rstrip("/")

    items: list[SitemapItem] = [
        SitemapItem(loc=f"{base}/", changefreq="weekly", priority=1.0),
        SitemapItem(loc=f"{base}/sobre", changefreq="monthly", priority=0.8),
        SitemapItem(loc=f"{base}/apoie", changefreq="monthly", priority=0.8),
    ]

    stmt = (
        select(Study)
        .join(Chapter, Study.chapter_id == Chapter.id, isouter=True)
        .join(Book, Chapter.book_id == Book.id, isouter=True)
        .where(
            Study.deleted_at.is_(None),
            or_(
                Study.visibility == "public",
                (Study.visibility == "inherit") & (Book.visibility == "public"),
            ),
            or_(Book.id.is_(None), Book.deleted_at.is_(None)),
        )
        .order_by(Study.updated_at.desc())
    )

    public_studies = session.scalars(stmt).all()
    for study in public_studies:
        lastmod = study.updated_at.strftime("%Y-%m-%d") if study.updated_at else None
        items.append(
            SitemapItem(
                loc=f"{base}/compartilhado/{study.id}",
                lastmod=lastmod,
                changefreq="weekly",
                priority=0.7,
            )
        )

    return items


def generate_sitemap_xml(session: Session, base_url: str | None = None) -> str:
    """Gera o documento XML padrão sitemaps.org com as URLs públicas do sistema."""
    items = get_public_sitemap_items(session, base_url=base_url)

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for item in items:
        lines.append("  <url>")
        lines.append(f"    <loc>{item.loc}</loc>")
        if item.lastmod:
            lines.append(f"    <lastmod>{item.lastmod}</lastmod>")
        lines.append(f"    <changefreq>{item.changefreq}</changefreq>")
        lines.append(f"    <priority>{item.priority:.1f}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>\n")
    return "\n".join(lines)
