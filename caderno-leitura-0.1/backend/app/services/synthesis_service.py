"""F0.11.11 (spec 113): cadernos de síntese com transclusão.

Marcas aceitas, cada uma sozinha na linha (fora de bloco de código):
- ``![[Título|id]]`` → estudo inteiro; ``![[Título|id#resumo]]`` → só a seção (``explicacao``, ``conceitos``,
  ``referencias``);
- ``![[destaque:123]]`` → um destaque.
A leitura resolve as marcas na hora, só com conteúdo do próprio leitor e fora da lixeira; nada é copiado.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models import Book, Chapter, Study, StudyHighlight
from app.models.synthesis_notebook import SynthesisNotebook
from app.schemas.synthesis import EmbedResolved, SynthesisCreate, SynthesisPatch, SynthesisRead, SynthesisSummary
from app.services.persistence import check_optimistic_version, commit_changes

TRASH_DAYS = 30
MAX_EMBEDS = 200
SECTIONS = {
    "resumo": ("summary", "Resumo"),
    "explicacao": ("explanation", "Explicação"),
    "conceitos": ("concepts", "Conceitos"),
    "referencias": ("references", "Referências"),
}
SECTION_ORDER = ("resumo", "explicacao", "conceitos", "referencias")
UNAVAILABLE = "Trecho indisponível (o estudo foi excluído ou não é seu)."

EMBED_LINE = re.compile(r"^\s*!\[\[(.+?)\]\]\s*$")
HIGHLIGHT_TARGET = re.compile(r"^\s*destaque\s*:\s*(\d+)\s*$", re.IGNORECASE)
STUDY_TARGET = re.compile(r"^(?P<title>.+)\|\s*(?P<id>\d+)\s*(?:#\s*(?P<section>[a-z]+))?\s*$", re.IGNORECASE)
FENCE = re.compile(r"^\s*(```|~~~)")


# ---------------------------------------------------------------------------- analisador (puro)

@dataclass(frozen=True)
class Embed:
    key: str
    kind: str  # "study" | "section" | "highlight"
    target_id: int
    section: str | None = None
    title: str = ""


@dataclass(frozen=True)
class Segment:
    type: str  # "text" | "embed" | "invalid"
    text: str
    embed: Embed | None = None


def parse_embed(inner: str) -> Embed | None:
    highlight = HIGHLIGHT_TARGET.match(inner)
    if highlight:
        hid = int(highlight.group(1))
        return Embed(key=f"highlight:{hid}", kind="highlight", target_id=hid) if hid > 0 else None
    study = STUDY_TARGET.match(inner)
    if not study:
        return None
    sid = int(study.group("id"))
    if sid <= 0:
        return None
    title = study.group("title").strip()
    section = (study.group("section") or "").lower() or None
    if section is not None and section not in SECTIONS:
        return None
    if section:
        return Embed(key=f"study:{sid}#{section}", kind="section", target_id=sid, section=section, title=title)
    return Embed(key=f"study:{sid}", kind="study", target_id=sid, title=title)


def split_body(body: str) -> list[Segment]:
    """Divide o texto em trechos de texto e marcas; linha com ``![[`` que não é marca vira ``invalid``."""
    segments: list[Segment] = []
    buffer: list[str] = []
    in_fence = False

    def flush():
        if buffer:
            segments.append(Segment(type="text", text="\n".join(buffer)))
            buffer.clear()

    for line in (body or "").split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            buffer.append(line)
            continue
        if in_fence or "![[" not in line:
            buffer.append(line)
            continue
        match = EMBED_LINE.match(line)
        embed = parse_embed(match.group(1)) if match else None
        flush()
        segments.append(Segment(type="embed", text=line, embed=embed) if embed else Segment(type="invalid", text=line))
    flush()
    return segments


def parse_embeds(body: str) -> list[Embed]:
    seen: dict[str, Embed] = {}
    for segment in split_body(body):
        if segment.embed and segment.embed.key not in seen:
            seen[segment.embed.key] = segment.embed
    return list(seen.values())


# ---------------------------------------------------------------------------- resolução

def _study_markdown(study: Study, section: str | None) -> tuple[str, str]:
    if section:
        attr, label = SECTIONS[section]
        return (getattr(study, attr) or "").strip(), label
    parts = []
    for slug in SECTION_ORDER:
        attr, label = SECTIONS[slug]
        text = (getattr(study, attr) or "").strip()
        if text:
            parts.append(f"#### {label}\n\n{text}")
    return "\n\n".join(parts), ""


def resolve_embeds(session: Session, user_id: str, embeds: list[Embed]) -> dict[str, EmbedResolved]:
    chosen = embeds[:MAX_EMBEDS]
    study_ids = {e.target_id for e in chosen if e.kind in ("study", "section")}
    highlight_ids = {e.target_id for e in chosen if e.kind == "highlight"}
    studies: dict[int, tuple[Study, Chapter, Book]] = {}
    if study_ids:
        for study, chapter, book in session.execute(
            select(Study, Chapter, Book)
            .join(Chapter, Study.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
            .where(
                Study.id.in_(study_ids),
                Study.user_id == user_id,
                Study.deleted_at.is_(None),
                Book.deleted_at.is_(None),
            )
        ).all():
            studies[study.id] = (study, chapter, book)
    highlights: dict[int, tuple[StudyHighlight, Study, Chapter, Book]] = {}
    if highlight_ids:
        for hl, study, chapter, book in session.execute(
            select(StudyHighlight, Study, Chapter, Book)
            .join(Study, StudyHighlight.study_id == Study.id)
            .join(Chapter, Study.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
            .where(
                StudyHighlight.id.in_(highlight_ids),
                StudyHighlight.user_id == user_id,
                Study.deleted_at.is_(None),
                Book.deleted_at.is_(None),
            )
        ).all():
            highlights[hl.id] = (hl, study, chapter, book)

    result: dict[str, EmbedResolved] = {}
    for embed in embeds:
        if embed.key in result:
            continue
        if embed not in chosen:
            result[embed.key] = EmbedResolved(key=embed.key, kind=embed.kind, available=False,
                                              markdown=f"Limite de {MAX_EMBEDS} trechos por caderno.")
            continue
        if embed.kind == "highlight":
            found = highlights.get(embed.target_id)
            if not found:
                result[embed.key] = EmbedResolved(key=embed.key, kind="highlight", available=False, markdown=UNAVAILABLE)
                continue
            hl, study, chapter, book = found
            result[embed.key] = EmbedResolved(
                key=embed.key, kind="highlight", available=True, study_id=study.id, book_id=book.id,
                title=study.title, book_title=book.title, chapter_name=chapter.name or "",
                markdown=hl.selected_text or "", note=(hl.note or "").strip(),
            )
            continue
        found_study = studies.get(embed.target_id)
        if not found_study:
            result[embed.key] = EmbedResolved(key=embed.key, kind=embed.kind, available=False, markdown=UNAVAILABLE)
            continue
        study, chapter, book = found_study
        markdown, label = _study_markdown(study, embed.section)
        result[embed.key] = EmbedResolved(
            key=embed.key, kind=embed.kind, available=True, study_id=study.id, book_id=book.id, title=study.title,
            book_title=book.title, chapter_name=chapter.name or "", section_label=label, markdown=markdown,
        )
    return result


def origin_line(item: EmbedResolved) -> str:
    parts = [p for p in (item.book_title, item.chapter_name, item.title) if p]
    if item.section_label:
        parts.append(item.section_label)
    return " · ".join(parts)


def export_markdown(notebook: SynthesisNotebook, resolved: dict[str, EmbedResolved]) -> str:
    out: list[str] = [f"# {notebook.title}", ""]
    for segment in split_body(notebook.body):
        if segment.type != "embed" or segment.embed is None:
            out.append(segment.text)
            continue
        item = resolved.get(segment.embed.key)
        # Linha em branco antes e depois: sem ela, a linha seguinte entraria na citação.
        if item is None or not item.available:
            out.extend(["", f"> {item.markdown if item else UNAVAILABLE}", ""])
            continue
        quoted = "\n".join(f"> {line}" if line else ">" for line in item.markdown.split("\n"))
        if item.note:
            quoted += f"\n>\n> Nota: {item.note}"
        out.extend(["", f"{quoted}\n>\n> — *{origin_line(item)}*", ""])
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return text.strip() + "\n"


# ---------------------------------------------------------------------------- CRUD e lixeira

def _purge_expired(session: Session, user_id: str) -> None:
    limit = utc_now() - timedelta(days=TRASH_DAYS)
    expired = session.scalars(
        select(SynthesisNotebook).where(
            SynthesisNotebook.user_id == user_id,
            SynthesisNotebook.deleted_at.is_not(None),
            SynthesisNotebook.deleted_at < limit,
        )
    ).all()
    for row in expired:
        session.delete(row)
    if expired:
        commit_changes(session)


def _get(session: Session, user_id: str, notebook_id: int, *, trashed: bool | None = False) -> SynthesisNotebook:
    row = session.get(SynthesisNotebook, notebook_id)
    if row is None or row.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caderno de síntese não encontrado.")
    if trashed is False and row.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caderno de síntese não encontrado.")
    if trashed is True and row.deleted_at is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caderno de síntese não está na lixeira.")
    return row


def to_read(row: SynthesisNotebook) -> SynthesisRead:
    return SynthesisRead.model_validate(row)


def to_summary(row: SynthesisNotebook) -> SynthesisSummary:
    return SynthesisSummary(id=row.id, title=row.title, embeds=len(parse_embeds(row.body)), created_at=row.created_at,
                            updated_at=row.updated_at, deleted_at=row.deleted_at)


def list_notebooks(session: Session, user_id: str, *, trash: bool = False) -> list[SynthesisSummary]:
    _purge_expired(session, user_id)
    condition = SynthesisNotebook.deleted_at.is_not(None) if trash else SynthesisNotebook.deleted_at.is_(None)
    rows = session.scalars(
        select(SynthesisNotebook)
        .where(SynthesisNotebook.user_id == user_id, condition)
        .order_by(SynthesisNotebook.updated_at.desc(), SynthesisNotebook.id.desc())
    ).all()
    return [to_summary(row) for row in rows]


def create_notebook(session: Session, user_id: str, payload: SynthesisCreate) -> SynthesisNotebook:
    row = SynthesisNotebook(user_id=user_id, title=payload.title, body=payload.body, version=1)
    session.add(row)
    commit_changes(session)
    session.refresh(row)
    return row


def get_notebook(session: Session, user_id: str, notebook_id: int) -> SynthesisNotebook:
    return _get(session, user_id, notebook_id)


def update_notebook(session: Session, user_id: str, notebook_id: int, payload: SynthesisPatch) -> SynthesisNotebook:
    row = _get(session, user_id, notebook_id)
    check_optimistic_version(
        current_version=row.version,
        expected_version=payload.version,
        entity_id=row.id,
        entity_type="synthesis",
        server_updated_at=row.updated_at,
        server_data={"title": row.title, "body": row.body},
        label="Caderno",
    )
    if payload.title is not None:
        row.title = payload.title
    if payload.body is not None:
        row.body = payload.body
    row.version = (row.version or 1) + 1
    commit_changes(session)
    session.refresh(row)
    return row


def trash_notebook(session: Session, user_id: str, notebook_id: int) -> None:
    row = _get(session, user_id, notebook_id)
    row.deleted_at = datetime.now(UTC)
    commit_changes(session)


def restore_notebook(session: Session, user_id: str, notebook_id: int) -> SynthesisNotebook:
    row = _get(session, user_id, notebook_id, trashed=True)
    row.deleted_at = None
    commit_changes(session)
    session.refresh(row)
    return row


def delete_notebook_permanently(session: Session, user_id: str, notebook_id: int) -> None:
    row = _get(session, user_id, notebook_id, trashed=True)
    session.delete(row)
    commit_changes(session)


def account_export_files(session: Session, user_id: str) -> list[tuple[str, str]]:
    """Para o pacote da conta (LGPD): ``sinteses/<título>.md`` com os trechos resolvidos."""
    from app.services.export_service import sanitize_folder_name

    rows = session.scalars(
        select(SynthesisNotebook)
        .where(SynthesisNotebook.user_id == user_id, SynthesisNotebook.deleted_at.is_(None))
        .order_by(SynthesisNotebook.id)
    ).all()
    files: list[tuple[str, str]] = []
    used: set[str] = set()
    for row in rows:
        name = sanitize_folder_name(row.title) or "sintese"
        path = f"sinteses/{name}.md"
        if path in used:
            path = f"sinteses/{name}-{row.id}.md"
        used.add(path)
        files.append((path, export_markdown(row, resolve_embeds(session, user_id, parse_embeds(row.body)))))
    return files
