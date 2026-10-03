from __future__ import annotations

import json
from fastapi import APIRouter, Request, Response

from app.dependencies import DatabaseSession
from app.services.seo_service import generate_robots_txt, generate_sitemap_xml

router = APIRouter(tags=["SEO"], include_in_schema=False)


@router.get("/robots.txt", response_class=Response, summary="Instruções para robôs de busca")
def get_robots_txt(request: Request) -> Response:
    """Retorna as regras de rastreamento do robots.txt permitindo rotas públicas e bloqueando áreas privadas."""
    base_url = str(request.base_url).rstrip("/")
    content = generate_robots_txt(base_url=base_url)
    return Response(content=content, media_type="text/plain; charset=utf-8")


@router.get("/sitemap.xml", response_class=Response, summary="Mapa dinâmico do site (Sitemap XML)")
def get_sitemap_xml(session: DatabaseSession, request: Request) -> Response:
    """Gera mapa XML dinâmico contendo apenas páginas públicas e estudos com visibilidade pública ativa."""
    base_url = str(request.base_url).rstrip("/")
    content = generate_sitemap_xml(session=session, base_url=base_url)
    return Response(content=content, media_type="application/xml; charset=utf-8")


@router.get("/site.webmanifest", response_class=Response, summary="Manifesto da aplicação web")
def get_site_webmanifest() -> Response:
    """Retorna metadados para instalação e identidade de atalho em navegadores móveis e desktop."""
    manifest_data = {
        "name": "Leitorum — Caderno de Leitura",
        "short_name": "Leitorum",
        "description": "Caderno pessoal de leitura e estudos em camadas.",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#09090b",
        "theme_color": "#09090b",
        "icons": [
            {
                "src": "/favicon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
            },
            {
                "src": "/favicon-48x48.png",
                "sizes": "48x48",
                "type": "image/png",
            },
            {
                "src": "/apple-touch-icon.png",
                "sizes": "180x180",
                "type": "image/png",
            },
        ],
    }
    return Response(
        content=json.dumps(manifest_data, ensure_ascii=False, indent=2),
        media_type="application/manifest+json; charset=utf-8",
    )
