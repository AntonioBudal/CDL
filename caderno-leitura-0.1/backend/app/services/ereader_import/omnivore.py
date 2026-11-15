"""ZIP de exportação do Omnivore (F0.12.03, spec 116).

Estrutura (código do Omnivore): `metadata_<a>_to_<b>.json` (lista de itens: `slug`, `title`, `author`, `savedAt`, …) e
`highlights/<slug>.md` (blocos `> trecho`, rótulos `#nome` e a nota depois de uma linha em branco). Lido **na
memória**, só os nomes esperados, com limites contra arquivo malicioso (nada extraído no disco).
"""
from __future__ import annotations

import io
import json
import re
import zipfile

from app.services.ereader_import import EreaderBook, EreaderEntry, EreaderFormatError, EreaderParseResult

ZIP_MAGIC = b"PK\x03\x04"
MAX_ZIP_BYTES = 50 * 1024 * 1024
MAX_UNCOMPRESSED = 200 * 1024 * 1024
MAX_MEMBERS = 5000
MAX_MEMBER_BYTES = 20 * 1024 * 1024
METADATA = re.compile(r"^(?:[^/]+/)?metadata_\d+_to_\d+\.json$")
HIGHLIGHTS = re.compile(r"^(?:[^/]+/)?highlights/([^/]+)\.md$")
LABELS_ONLY = re.compile(r"^(#\S+\s*)+$")


def _open(data: bytes) -> zipfile.ZipFile:
    if len(data) > MAX_ZIP_BYTES:
        raise EreaderFormatError("O ZIP do Omnivore passa de 50 MB.")
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise EreaderFormatError("O arquivo ZIP está corrompido.") from exc
    infos = archive.infolist()
    if len(infos) > MAX_MEMBERS:
        raise EreaderFormatError("O ZIP tem arquivos demais.")
    if sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
        raise EreaderFormatError("O ZIP descompactado passa de 200 MB.")
    return archive


def looks_like_omnivore(data: bytes) -> bool:
    if not data.startswith(ZIP_MAGIC):
        return False
    try:
        names = [i.filename for i in _open(data).infolist()]
    except EreaderFormatError:
        return True  # é ZIP; o erro de limite aparece na leitura, com a mensagem certa
    return any(METADATA.match(n) for n in names)


def _read(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    if info.file_size > MAX_MEMBER_BYTES:
        raise EreaderFormatError("Um arquivo dentro do ZIP é grande demais.")
    with archive.open(info) as handle:
        raw = handle.read(MAX_MEMBER_BYTES + 1)
    if len(raw) > MAX_MEMBER_BYTES:
        raise EreaderFormatError("Um arquivo dentro do ZIP é grande demais.")
    return raw.decode("utf-8", errors="replace")


def parse_highlights_markdown(text: str) -> list[tuple[str, str]]:
    """`> trecho` (+ nota no bloco seguinte) → [(trecho, nota)]; nota solta → ("", nota)."""
    result: list[tuple[str, str]] = []
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if b.strip()]
    last_was_quote = False
    for block in blocks:
        lines = block.split("\n")
        if lines[0].startswith(">"):
            quote = "\n".join(re.sub(r"^>\s?", "", line) for line in lines if line.startswith(">")).strip()
            result.append((quote, ""))
            last_was_quote = True
            continue
        if LABELS_ONLY.match(block.strip()):
            continue
        note = block.strip()
        if last_was_quote and result and not result[-1][1]:
            result[-1] = (result[-1][0], note)
        else:
            result.append(("", note))
        last_was_quote = False
    return [(q, n) for q, n in result if q or n]


def parse_omnivore_zip(data: bytes) -> EreaderParseResult:
    archive = _open(data)
    items: dict[str, dict] = {}
    highlight_files: dict[str, zipfile.ZipInfo] = {}
    for info in archive.infolist():
        if METADATA.match(info.filename):
            try:
                batch = json.loads(_read(archive, info))
            except ValueError as exc:
                raise EreaderFormatError("Um metadata_*.json do Omnivore está inválido.") from exc
            for item in batch if isinstance(batch, list) else []:
                if isinstance(item, dict) and item.get("slug"):
                    items[str(item["slug"])] = item
        else:
            match = HIGHLIGHTS.match(info.filename)
            if match:
                highlight_files[match.group(1)] = info
    if not items:
        raise EreaderFormatError("Não encontrei os arquivos metadata_*.json do Omnivore neste ZIP.")
    books: list[EreaderBook] = []
    skipped = 0
    for slug, info in sorted(highlight_files.items()):
        item = items.get(slug, {})
        title = str(item.get("title") or slug).strip() or slug
        author = str(item.get("author") or "").strip() or None
        book = EreaderBook(title=title[:500], author=author)
        for quote, note in parse_highlights_markdown(_read(archive, info)):
            book.entries.append(EreaderEntry(kind="note" if note and not quote else "highlight", text=quote, note=note))
        if book.entries:
            books.append(book)
        else:
            skipped += 1
    return EreaderParseResult(source="omnivore", books=books, skipped=skipped)
