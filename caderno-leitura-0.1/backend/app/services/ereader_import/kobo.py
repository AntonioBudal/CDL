"""Leitura do ``KoboReader.sqlite`` do aparelho Kobo (F0.11.03).

O arquivo enviado é gravado numa cópia temporária, aberto **somente leitura** (``mode=ro``), conferido com
``quick_check`` e lido só com ``SELECT`` nas tabelas ``Bookmark`` e ``content``. A cópia é apagada no fim.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime
from pathlib import Path

from app.services.ereader_import import (
    SQLITE_MAGIC,
    EreaderBook,
    EreaderEntry,
    EreaderFormatError,
    EreaderParseResult,
)

MAX_BOOKMARKS = 50_000
_NOT_KOBO = "Não reconheci este arquivo como KoboReader.sqlite do Kobo."


def _parse_kobo_date(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def parse_kobo_database(data: bytes) -> EreaderParseResult:
    if not data.startswith(SQLITE_MAGIC):
        raise EreaderFormatError(_NOT_KOBO)

    handle, temp_name = tempfile.mkstemp(prefix="leitorum-kobo-", suffix=".sqlite")
    temp_path = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as temp_file:
            temp_file.write(data)
        uri = temp_path.resolve().as_uri() + "?mode=ro"
        try:
            with closing(sqlite3.connect(uri, uri=True, timeout=2.0)) as conn:
                return _read(conn)
        except sqlite3.DatabaseError as exc:
            raise EreaderFormatError(_NOT_KOBO) from exc
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _read(conn: sqlite3.Connection) -> EreaderParseResult:
    if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
        raise EreaderFormatError("O arquivo do Kobo parece corrompido.")
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    if not {"Bookmark", "content"} <= tables:
        raise EreaderFormatError(_NOT_KOBO)
    bookmark_cols = _columns(conn, "Bookmark")
    content_cols = _columns(conn, "content")
    if not {"VolumeID", "Text"} <= bookmark_cols or not {"ContentID", "Title"} <= content_cols:
        raise EreaderFormatError(_NOT_KOBO)

    annotation = "b.Annotation" if "Annotation" in bookmark_cols else "NULL"
    created = "b.DateCreated" if "DateCreated" in bookmark_cols else "NULL"
    chapter_id = "b.ContentID" if "ContentID" in bookmark_cols else "NULL"
    author = "v.Attribution" if "Attribution" in content_cols else "NULL"
    rows = conn.execute(
        f"""
        SELECT b.VolumeID, v.Title, {author}, b.Text, {annotation}, {created}, ch.Title
        FROM Bookmark b
        LEFT JOIN content v ON v.ContentID = b.VolumeID
        LEFT JOIN content ch ON ch.ContentID = {chapter_id} AND ch.ContentID <> b.VolumeID
        ORDER BY b.VolumeID, {created}
        LIMIT ?
        """,
        (MAX_BOOKMARKS,),
    ).fetchall()

    books: dict[str, EreaderBook] = {}
    skipped = 0
    for volume_id, title, attribution, text, note, date_created, chapter_title in rows:
        text = (text or "").strip()
        note = (note or "").strip()
        if not text and not note:
            skipped += 1  # marcador sem texto
            continue
        book = books.get(volume_id)
        if book is None:
            book = EreaderBook(title=(title or "").strip() or "Livro sem título (Kobo)", author=(attribution or "").strip() or None)
            books[volume_id] = book
        book.entries.append(
            EreaderEntry(
                kind="highlight" if text else "note",
                text=text,
                note=note,
                chapter=(chapter_title or "").strip() or None,
                created_at=_parse_kobo_date(date_created),
            )
        )
    return EreaderParseResult(source="kobo", books=list(books.values()), skipped=skipped)
