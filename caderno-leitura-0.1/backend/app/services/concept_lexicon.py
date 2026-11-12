"""Léxico de conceitos derivado dos estudos (F0.11.06, spec 108).

Sem tabela própria: o léxico é montado na hora a partir da seção **Conceitos** e das menções ``[[conceito:Termo]]``
dos estudos do próprio leitor (fora da lixeira). Editar o estudo atualiza o léxico.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study

MAX_TERM_LENGTH = 80
TEXT_SECTIONS = ("summary", "explanation", "concepts", "references", "notes")

# Linhas de definição aceitas (com marcador de lista opcional):
#   **Termo**: definição  |  **Termo** — definição  |  Termo: definição  |  Termo – definição
_BULLET = r"^\s*(?:[-*+•]|\d+[.)])?\s*"
_BOLD_DEF = re.compile(_BULLET + r"\*\*(?P<term>[^*\n]+?)\*\*\s*(?:[:：]|[—–-])\s*(?P<def>\S.*)$")
_PLAIN_DEF = re.compile(_BULLET + r"(?P<term>[^:\n*#\[\]]+?)\s*(?:[:：]|\s[—–]\s)\s*(?P<def>\S.*)$")
_HEADING = re.compile(r"^\s*#{2,6}\s+(?P<term>.+?)\s*#*\s*$")
_MENTION = re.compile(r"\[\[\s*conceito\s*:\s*([^\]|]+?)\s*\]\]", re.IGNORECASE)


def _strip_accents(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))


def concept_key(term: str) -> str:
    """Chave estável: sem acento, minúsculas, só letras/dígitos separados por hífen ("Mímese" → "mimese")."""
    base = _strip_accents(term or "").casefold()
    return re.sub(r"[^0-9a-z]+", "-", base).strip("-")


def _clean_term(raw: str) -> str:
    term = re.sub(r"[*_`]+", "", raw or "").strip().strip(".;,")
    return re.sub(r"\s+", " ", term)


def _valid_term(term: str) -> bool:
    return 0 < len(term) <= MAX_TERM_LENGTH and bool(concept_key(term)) and len(term.split()) <= 8


def parse_concepts(text: str | None) -> list[tuple[str, str]]:
    """Pares (termo, definição) da seção Conceitos. Linhas fora dos formatos aceitos são ignoradas."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    result: list[tuple[str, str]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        heading = _HEADING.match(line)
        if heading:
            term = _clean_term(heading.group("term"))
            body: list[str] = []
            index += 1
            while index < len(lines) and not _HEADING.match(lines[index]):
                if lines[index].strip():
                    body.append(lines[index].strip())
                elif body:
                    break
                index += 1
            definition = " ".join(body).strip()
            if _valid_term(term) and definition:
                result.append((term, definition))
            continue
        match = _BOLD_DEF.match(line) or _PLAIN_DEF.match(line)
        if match:
            term = _clean_term(match.group("term"))
            definition = match.group("def").strip()
            if _valid_term(term) and definition and not term.lower().startswith(("http", "www")):
                result.append((term, definition))
        index += 1
    return result


def extract_concept_mentions(text: str | None, max_len: int = 180) -> list[tuple[str, str]]:
    """Menções ``[[conceito:Termo]]`` com um trecho de contexto."""
    content = text or ""
    found: list[tuple[str, str]] = []
    for match in _MENTION.finditer(content):
        term = _clean_term(match.group(1))
        if not _valid_term(term):
            continue
        start = max(0, match.start() - max_len // 2)
        end = min(len(content), match.end() + max_len // 2)
        snippet = re.sub(r"\s+", " ", content[start:end]).strip()
        # Trecho legível: [[conceito:Termo]] → Termo; [[Título|id]] → Título.
        snippet = _MENTION.sub(lambda m: m.group(1).strip(), snippet)
        snippet = re.sub(r"\[\[([^\]|]+?)(?:\s*\|\s*[^\]]+?)?\]\]", lambda m: m.group(1).strip(), snippet)
        found.append((term, ("…" if start else "") + snippet + ("…" if end < len(content) else "")))
    return found


@dataclass
class ConceptOccurrence:
    term: str
    text: str  # definição ou trecho
    study_id: int
    study_title: str
    book_id: int
    book_title: str
    chapter_name: str
    chapter_id: int = 0  # F0.11.08: filtro por capítulo dos cartões de conceito


@dataclass
class ConceptEntry:
    key: str
    labels: Counter = field(default_factory=Counter)
    definitions: list[ConceptOccurrence] = field(default_factory=list)
    mentions: list[ConceptOccurrence] = field(default_factory=list)

    @property
    def term(self) -> str:
        # Grafia mais frequente; empate → a primeira em ordem alfabética.
        return sorted(self.labels.items(), key=lambda item: (-item[1], item[0]))[0][0]

    @property
    def books(self) -> set[int]:
        return {o.book_id for o in self.definitions + self.mentions}


def _studies(session: Session, user_id: str):
    return session.execute(
        select(
            Study.id, Study.title, Study.summary, Study.explanation, Study.concepts, Study.references,
            Study.notes, Book.id, Book.title, Chapter.name, Chapter.id,
        )
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .where(Study.user_id == user_id, Study.deleted_at.is_(None), Book.deleted_at.is_(None))
        .order_by(Book.title, Chapter.position, Study.position, Study.id)
    ).all()


def build_lexicon(session: Session, user_id: str) -> dict[str, ConceptEntry]:
    entries: dict[str, ConceptEntry] = {}

    def entry_for(term: str) -> ConceptEntry:
        key = concept_key(term)
        entry = entries.setdefault(key, ConceptEntry(key=key))
        entry.labels[term] += 1
        return entry

    for (study_id, title, summary, explanation, concepts, references, notes, book_id, book_title,
         chapter_name, chapter_id) in _studies(session, user_id):
        base = dict(study_id=study_id, study_title=title, book_id=book_id, book_title=book_title,
                    chapter_name=chapter_name or "", chapter_id=chapter_id)
        for term, definition in parse_concepts(concepts):
            entry_for(term).definitions.append(ConceptOccurrence(term=term, text=definition, **base))
        for section in (summary, explanation, concepts, references, notes):
            for term, snippet in extract_concept_mentions(section):
                entry_for(term).mentions.append(ConceptOccurrence(term=term, text=snippet, **base))

    return _merge_simple_plurals(entries)


def _merge_simple_plurals(entries: dict[str, ConceptEntry]) -> dict[str, ConceptEntry]:
    """Funde "conceitos" em "conceito" só quando a forma sem o "s" final também existe."""
    for key in sorted(entries.keys(), key=len, reverse=True):
        if key.endswith("s") and len(key) > 3 and key[:-1] in entries and key in entries:
            target = entries[key[:-1]]
            source = entries.pop(key)
            target.labels.update(source.labels)
            target.definitions.extend(source.definitions)
            target.mentions.extend(source.mentions)
    return entries


def _matches(entry: ConceptEntry, query: str) -> bool:
    needle = concept_key(query)
    return not needle or needle in entry.key or any(needle in concept_key(label) for label in entry.labels)


def list_concepts(session: Session, user_id: str, query: str = "") -> list[ConceptEntry]:
    lexicon = build_lexicon(session, user_id)
    items = [entry for entry in lexicon.values() if _matches(entry, query)]
    return sorted(items, key=lambda entry: concept_key(entry.term))


def get_concept(session: Session, user_id: str, key: str) -> ConceptEntry | None:
    return build_lexicon(session, user_id).get(concept_key(key))
