"""F0.12.02 (spec 115): estudos publicados na web (`/compartilhado/{id}`).

Publicar é uma escolha explícita do dono (``studies.published_at``), separada da visibilidade. A página pública mostra
**só**: título, as 4 seções (Resumo, Explicação, Conceitos, Referências), a referência do livro e o nome de exibição do
autor. Nunca: notas, fichamento da fonte, destaques, e-mail, nome de usuário. Indisponível → 404 igual para todos os
casos (não publicado, lixeira, livro na lixeira, conta inativa, id inexistente).
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_app_base_url
from app.models import Book, Chapter, Study, User
from app.services.persistence import commit_changes, get_user_resource_or_404
from app.services.public_markdown import excerpt, render_public_markdown

SECTIONS = (
    ("summary", "Resumo"),
    ("explanation", "Explicação"),
    ("concepts", "Conceitos"),
    ("references", "Referências"),
)
NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Página não encontrada.")


def public_path(study_id: int) -> str:
    return f"/compartilhado/{study_id}"


def has_content(study: Study) -> bool:
    return any((getattr(study, attr) or "").strip() for attr, _ in SECTIONS)


# ------------------------------------------------------------------------------- dono

def publish(session: Session, user_id: str, study_id: int) -> Study:
    study = get_user_resource_or_404(session, Study, study_id, user_id, "Estudo")
    if study.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")
    if not has_content(study):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Preencha ao menos uma das quatro seções antes de publicar.",
        )
    if study.published_at is None:
        study.published_at = datetime.now(UTC)
        commit_changes(session)
        session.refresh(study)
    return study


def unpublish(session: Session, user_id: str, study_id: int) -> None:
    study = get_user_resource_or_404(session, Study, study_id, user_id, "Estudo")
    if study.published_at is not None:
        study.published_at = None
        commit_changes(session)


def list_published(session: Session, user_id: str) -> list[tuple[Study, Book]]:
    return list(session.execute(
        select(Study, Book)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(Study.user_id == user_id, Study.published_at.is_not(None))
        .order_by(Study.published_at.desc(), Study.id.desc())
    ).all())


# ------------------------------------------------------------------------------- disponibilidade

def _available_query():
    return (
        select(Study, Chapter, Book, User)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .join(User, Study.user_id == User.id)
        .where(
            Study.published_at.is_not(None),
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
            User.status == "ativo",
        )
    )


def get_public_study(session: Session, study_id: int) -> tuple[Study, Chapter, Book, User]:
    row = session.execute(_available_query().where(Study.id == study_id)).first()
    if row is None:
        raise NOT_FOUND
    return row[0], row[1], row[2], row[3]


def available_published_ids(session: Session, ids: set[int]) -> set[int]:
    if not ids:
        return set()
    return {row[0].id for row in session.execute(_available_query().where(Study.id.in_(ids))).all()}


def list_available(session: Session) -> list[Study]:
    return [row[0] for row in session.execute(_available_query().order_by(Study.updated_at.desc())).all()]


# ------------------------------------------------------------------------------- página

def abnt_reference(book: Book) -> str:
    """Referência ABNT simples (NBR 6023): SOBRENOME, Prenome. *Título*: subtítulo. Local: Editora, ano."""
    parts: list[str] = []
    author = (book.author or "").strip()
    if author:
        first = author.split(";")[0].split(",")[0].strip()
        names = first.split()
        if len(names) > 1:
            parts.append(f"{names[-1].upper()}, {' '.join(names[:-1])}.")
        else:
            parts.append(f"{first.upper()}.")
    title = html.escape(book.title.strip())
    subtitle = (book.subtitle or "").strip()
    parts.append(f"<em>{title}</em>" + (f": {html.escape(subtitle)}." if subtitle else "."))
    place = (book.publication_place or "").strip() or "[S. l.]"
    publisher = (book.publisher or "").strip() or "[s. n.]"
    year = str(book.year) if book.year else "[s. d.]"
    parts.append(f"{html.escape(place)}: {html.escape(publisher)}, {year}.")
    if author:
        parts[0] = html.escape(parts[0])
    return " ".join(parts)


@dataclass
class PublicPage:
    html: str


STYLE = """
:root{color-scheme:light dark;--bg:#fbf8f2;--fg:#1f1b16;--muted:#5b5348;--line:#e3dccf;--link:#1d4fa8;--quote:#f1ece2}
@media (prefers-color-scheme:dark){:root{--bg:#1b1a19;--fg:#ece7df;--muted:#b9b0a3;--line:#3a3631;--link:#9cc0ff;--quote:#262421}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.65 Georgia,"Times New Roman",serif}
main{max-width:44rem;margin:0 auto;padding:2.5rem 1rem 3rem}header p,footer,.ref{color:var(--muted);font:15px/1.5 system-ui,sans-serif}
h1{font-size:2rem;line-height:1.2;margin:.2rem 0 .6rem}h2{font-size:1.3rem;margin:2rem 0 .5rem;border-bottom:1px solid var(--line);padding-bottom:.25rem}
h3,h4,h5,h6{font-size:1.1rem;margin:1.4rem 0 .4rem}a{color:var(--link)}blockquote{margin:1rem 0;padding:.5rem 1rem;background:var(--quote);border-left:4px solid var(--line)}
pre{overflow:auto;padding:.75rem;background:var(--quote);font-size:15px}code{font-size:.9em}hr{border:0;border-top:1px solid var(--line);margin:1.5rem 0}
.ref{margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--line)}footer{margin-top:2rem}
"""


def render_page(session: Session, study: Study, chapter: Chapter, book: Book, author: User) -> PublicPage:
    base = get_app_base_url()
    canonical = f"{base}{public_path(study.id)}"
    mention_ids: set[int] = set()
    for attr, _ in SECTIONS:
        mention_ids.update(int(m) for m in re.findall(r"\[\[[^\]|]+\|\s*(\d+)\s*\]\]", getattr(study, attr) or ""))
    published = available_published_ids(session, mention_ids)

    def link_for(study_id: int) -> str | None:
        return public_path(study_id) if study_id in published else None

    sections_html = []
    for attr, label in SECTIONS:
        text = (getattr(study, attr) or "").strip()
        if text:
            sections_html.append(f"<section><h2>{label}</h2>\n{render_public_markdown(text, link_for)}</section>")

    title = html.escape(study.title)
    author_name = html.escape(author.display_name)
    book_line = html.escape(book.title) + (f" — {html.escape(book.author)}" if book.author else "")
    if book.year:
        book_line += f", {book.year}"
    description = excerpt(study.summary or study.explanation or study.concepts or "", 160)
    published_iso = study.published_at.astimezone(UTC).isoformat() if study.published_at else ""
    modified_iso = study.updated_at.astimezone(UTC).isoformat() if study.updated_at else published_iso
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": study.title,
        "author": {"@type": "Person", "name": author.display_name},
        "datePublished": published_iso,
        "dateModified": modified_iso,
        "inLanguage": "pt-BR",
        "about": {"@type": "Book", "name": book.title, **({"author": book.author} if book.author else {})},
        "url": canonical,
    }, ensure_ascii=False).replace("</", "<\\/")
    desc_attr = html.escape(description, quote=True)
    page = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Leitorum</title>
<meta name="description" content="{desc_attr}">
<link rel="canonical" href="{html.escape(canonical, quote=True)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc_attr}">
<meta property="og:url" content="{html.escape(canonical, quote=True)}">
<meta property="og:site_name" content="Leitorum">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{json_ld}</script>
<style>{STYLE}</style>
</head>
<body>
<main>
<article>
<header>
<p>Estudo sobre <strong>{book_line}</strong></p>
<h1>{title}</h1>
<p>por {author_name}</p>
</header>
{chr(10).join(sections_html)}
<p class="ref">Referência: {abnt_reference(book)}</p>
</article>
<footer>Escrito no Leitorum, um caderno de leitura e fichamento.</footer>
</main>
</body>
</html>
"""
    return PublicPage(html=page)
