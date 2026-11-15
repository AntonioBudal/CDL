from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_app_base_url
from app.schemas.seo import SitemapItem

# F0.12.02: /compartilhado/{id} existe (HTML do servidor). O sitemap lista só estudos **publicados** pelo dono e
# disponíveis (fora da lixeira, conta ativa); "público" para a instalação não basta.
PUBLIC_STUDY_PAGES_ENABLED = True


def generate_robots_txt(base_url: str | None = None) -> str:
    """Gera o conteúdo de texto puro do arquivo robots.txt com regras estritas de rastreamento."""
    base = (base_url or get_app_base_url()).rstrip("/")
    shared_rule = (
        "Allow: /compartilhado/\nAllow: /feed.xml\nAllow: /feed.atom\nAllow: /feed.json\n"  # F0.12.04
        if PUBLIC_STUDY_PAGES_ENABLED else ""
    )
    return f"""User-agent: *
Allow: /
Allow: /sobre
Allow: /apoie
{shared_rule}Disallow: /api/
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

    if not PUBLIC_STUDY_PAGES_ENABLED:
        return items

    from app.services.public_study_service import list_available

    public_studies = list_available(session)
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
