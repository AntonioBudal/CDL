"""F0.12.04 (spec 117): feeds RSS 2.0, Atom 1.0 e JSON Feed 1.1 dos estudos publicados na web.

Só o que já é público (estudos publicados e disponíveis, regra da F0.12.02) e só os campos da página pública. XML gerado
com `xml.etree.ElementTree` (escape garantido, inclusive `]]>`), nunca por concatenação de texto.
"""
from __future__ import annotations

import hashlib
import html
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import format_datetime

from sqlalchemy.orm import Session

from app.core.config import get_app_base_url
from app.services.public_markdown import excerpt
from app.services.public_study_service import list_feed_rows, public_path, render_sections

FEED_TITLE = "Leitorum — estudos publicados"
FEED_DESCRIPTION = "Estudos de leitura publicados na web a partir do Leitorum."
FEED_LIMIT = 50
ATOM_NS = "http://www.w3.org/2005/Atom"


@dataclass
class FeedItem:
    id: str
    url: str
    title: str
    author: str
    summary: str
    content_html: str
    published: datetime
    updated: datetime


def _utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime(1970, 1, 1, tzinfo=UTC)
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def feed_items(session: Session, limit: int = FEED_LIMIT) -> list[FeedItem]:
    base = get_app_base_url()
    items: list[FeedItem] = []
    for study, _chapter, book, author in list_feed_rows(session, limit):
        url = f"{base}{public_path(study.id)}"
        sections = render_sections(session, study, base=base)
        published = _utc(study.published_at)
        updated = max(published, _utc(study.updated_at))
        items.append(FeedItem(
            id=url,
            url=url,
            title=study.title,
            author=author.display_name,
            summary=excerpt(study.summary or study.explanation or study.concepts or "", 280),
            content_html=f"<p>Estudo sobre {_escape_text(book.title)}</p>\n" + "\n".join(sections),
            published=published,
            updated=updated,
        ))
    return items


def _escape_text(text: str) -> str:
    return html.escape(text or "")


def _feed_updated(items: list[FeedItem]) -> datetime:
    return max((i.updated for i in items), default=datetime(1970, 1, 1, tzinfo=UTC))


def _sub(parent: ET.Element, tag: str, text: str | None = None, **attrs: str) -> ET.Element:
    element = ET.SubElement(parent, tag, attrs)
    if text is not None:
        element.text = text
    return element


def build_rss(items: list[FeedItem]) -> str:
    base = get_app_base_url()
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")
    ET.register_namespace("atom", ATOM_NS)
    ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
    rss = ET.Element("rss", {"version": "2.0"})
    channel = _sub(rss, "channel")
    _sub(channel, "title", FEED_TITLE)
    _sub(channel, "link", f"{base}/")
    _sub(channel, "description", FEED_DESCRIPTION)
    _sub(channel, "language", "pt-BR")
    _sub(channel, f"{{{ATOM_NS}}}link", href=f"{base}/feed.xml", rel="self", type="application/rss+xml")
    if items:
        _sub(channel, "lastBuildDate", format_datetime(_feed_updated(items)))
    for item in items:
        node = _sub(channel, "item")
        _sub(node, "title", item.title)
        _sub(node, "link", item.url)
        _sub(node, "guid", item.id, isPermaLink="true")
        _sub(node, "pubDate", format_datetime(item.published))
        _sub(node, "description", item.summary)
        _sub(node, "{http://purl.org/rss/1.0/modules/content/}encoded", item.content_html)
        _sub(node, "{http://purl.org/dc/elements/1.1/}creator", item.author)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding="unicode")


def build_atom(items: list[FeedItem]) -> str:
    base = get_app_base_url()
    # Nomes simples com o xmlns declarado na raiz: não registra o Atom como espaço de nomes padrão do processo inteiro
    # (isso afetaria o RSS gerado depois).
    feed = ET.Element("feed", {"xmlns": ATOM_NS, "xml:lang": "pt-BR"})
    _sub(feed, "id", f"{base}/feed.atom")
    _sub(feed, "title", FEED_TITLE)
    _sub(feed, "subtitle", FEED_DESCRIPTION)
    _sub(feed, "updated", _feed_updated(items).isoformat())
    _sub(feed, "link", href=f"{base}/feed.atom", rel="self", type="application/atom+xml")
    _sub(feed, "link", href=f"{base}/", rel="alternate", type="text/html")
    for item in items:
        entry = _sub(feed, "entry")
        _sub(entry, "id", item.id)
        _sub(entry, "title", item.title)
        _sub(entry, "link", href=item.url, rel="alternate", type="text/html")
        _sub(entry, "published", item.published.isoformat())
        _sub(entry, "updated", item.updated.isoformat())
        author = _sub(entry, "author")
        _sub(author, "name", item.author)
        _sub(entry, "summary", item.summary)
        _sub(entry, "content", item.content_html, type="html")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(feed, encoding="unicode")


def build_json_feed(items: list[FeedItem]) -> str:
    base = get_app_base_url()
    data = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": FEED_TITLE,
        "description": FEED_DESCRIPTION,
        "home_page_url": f"{base}/",
        "feed_url": f"{base}/feed.json",
        "language": "pt-BR",
        "items": [
            {
                "id": item.id,
                "url": item.url,
                "title": item.title,
                "summary": item.summary,
                "content_html": item.content_html,
                "date_published": item.published.isoformat(),
                "date_modified": item.updated.isoformat(),
                "authors": [{"name": item.author}],
            }
            for item in items
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def etag_for(body: str) -> str:
    return '"' + hashlib.sha256(body.encode("utf-8")).hexdigest()[:32] + '"'
