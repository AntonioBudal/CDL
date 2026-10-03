from __future__ import annotations

from typing import Any
from pydantic import Field

from app.schemas.common import OutputModel


class SitemapItem(OutputModel):
    loc: str
    lastmod: str | None = None
    changefreq: str = "monthly"
    priority: float = Field(default=0.8, ge=0.0, le=1.0)


class SitemapData(OutputModel):
    items: list[SitemapItem]


class PublicSeoMeta(OutputModel):
    title: str
    description: str
    canonical_url: str
    og_image: str
    og_type: str = "website"
    robots: str = "index, follow"
    json_ld: dict[str, Any] | None = None
