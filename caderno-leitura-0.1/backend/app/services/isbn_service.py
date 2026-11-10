"""Busca de dados do livro pelo ISBN, só sob demanda (F0.11.04, spec 106).

Sai do **servidor** (o navegador continua falando só com o Leitorum), só para dois domínios fixos, com o ISBN
validado como única informação enviada, sem cookies e com ``User-Agent`` genérico. ``LEITORUM_ISBN_LOOKUP=off`` desliga.
Ordem: BrasilAPI (boa cobertura de livros brasileiros, traz editora e cidade) e, se não achar, Open Library.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import httpx

BRASILAPI_URL = "https://brasilapi.com.br/api/isbn/v1/{isbn}"
OPENLIBRARY_URL = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=5.0)
MAX_RESPONSE_BYTES = 512 * 1024
HEADERS = {"User-Agent": "Leitorum", "Accept": "application/json"}

# Transporte trocável nos testes (httpx.MockTransport); em produção, None = rede de verdade.
_transport: httpx.BaseTransport | None = None


def set_transport(transport: httpx.BaseTransport | None) -> None:
    global _transport
    _transport = transport


def isbn_lookup_enabled() -> bool:
    return os.environ.get("LEITORUM_ISBN_LOOKUP", "").strip().lower() not in {"off", "0", "false", "nao", "não"}


class InvalidIsbnError(ValueError):
    pass


class IsbnServiceUnavailable(RuntimeError):
    pass


def _isbn10_valid(digits: str) -> bool:
    if not re.fullmatch(r"\d{9}[\dX]", digits):
        return False
    total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(digits))
    return total % 11 == 0


def _isbn13_check(first12: str) -> str:
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(first12))
    return str((10 - total % 10) % 10)


def normalize_isbn(raw: str | None) -> str:
    """ISBN-10 ou 13, com ou sem hífens/espaços → ISBN-13 sem separadores. Lança ``InvalidIsbnError``."""
    digits = re.sub(r"[\s\-\.]", "", (raw or "")).upper()
    if len(digits) == 10:
        if not _isbn10_valid(digits):
            raise InvalidIsbnError("ISBN-10 inválido (confira os dígitos).")
        first12 = "978" + digits[:9]
        return first12 + _isbn13_check(first12)
    if len(digits) == 13 and digits.isdigit() and digits[:3] in {"978", "979"}:
        if _isbn13_check(digits[:12]) != digits[12]:
            raise InvalidIsbnError("ISBN-13 inválido (confira os dígitos).")
        return digits
    raise InvalidIsbnError("Use um ISBN de 10 ou 13 dígitos.")


@dataclass
class IsbnResult:
    isbn: str
    source: str  # "brasilapi" ou "openlibrary"
    title: str = ""
    subtitle: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    publisher: str = ""
    place: str = ""


def _year_from(value: object) -> int | None:
    match = re.search(r"\b(1[0-9]{3}|20[0-9]{2}|2100)\b", str(value or ""))
    return int(match.group(1)) if match else None


def _clean(value: object, limit: int = 500) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _get_json(client: httpx.Client, url: str) -> object | None:
    """GET sem seguir redirecionamentos; 404 → None; outros erros → ``IsbnServiceUnavailable``."""
    try:
        response = client.get(url)
    except httpx.HTTPError as exc:
        raise IsbnServiceUnavailable(str(exc)) from exc
    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise IsbnServiceUnavailable(f"HTTP {response.status_code}")
    if len(response.content) > MAX_RESPONSE_BYTES:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def _from_brasilapi(isbn: str, data: object) -> IsbnResult | None:
    if not isinstance(data, dict) or not _clean(data.get("title")):
        return None
    authors = data.get("authors") if isinstance(data.get("authors"), list) else []
    return IsbnResult(
        isbn=isbn,
        source="brasilapi",
        title=_clean(data.get("title")),
        subtitle=_clean(data.get("subtitle")),
        authors=[_clean(a, 200) for a in authors if _clean(a)][:10],
        year=_year_from(data.get("year")),
        publisher=_clean(data.get("publisher"), 200),
        place=_clean(data.get("location"), 200),
    )


def _from_openlibrary(isbn: str, data: object) -> IsbnResult | None:
    if not isinstance(data, dict):
        return None
    book = data.get(f"ISBN:{isbn}")
    if not isinstance(book, dict) or not _clean(book.get("title")):
        return None

    def names(key: str) -> list[str]:
        items = book.get(key) if isinstance(book.get(key), list) else []
        return [_clean(item.get("name"), 200) for item in items if isinstance(item, dict) and _clean(item.get("name"))]

    publishers = names("publishers")
    places = names("publish_places")
    return IsbnResult(
        isbn=isbn,
        source="openlibrary",
        title=_clean(book.get("title")),
        subtitle=_clean(book.get("subtitle")),
        authors=names("authors")[:10],
        year=_year_from(book.get("publish_date")),
        publisher=publishers[0] if publishers else "",
        place=places[0] if places else "",
    )


def lookup_isbn(isbn13: str) -> IsbnResult | None:
    """Consulta BrasilAPI e, se não achar, Open Library. ``None`` = não encontrado nas duas.

    Lança ``IsbnServiceUnavailable`` só quando nenhuma das duas respondeu.
    """
    if not re.fullmatch(r"97[89]\d{10}", isbn13):
        raise InvalidIsbnError("ISBN inválido.")
    failures = 0
    with httpx.Client(timeout=TIMEOUT, follow_redirects=False, headers=HEADERS, transport=_transport) as client:
        for url, mapper in ((BRASILAPI_URL, _from_brasilapi), (OPENLIBRARY_URL, _from_openlibrary)):
            try:
                data = _get_json(client, url.format(isbn=isbn13))
            except IsbnServiceUnavailable:
                failures += 1
                continue
            result = mapper(isbn13, data) if data is not None else None
            if result is not None:
                return result
    if failures == 2:
        raise IsbnServiceUnavailable("Nenhum serviço respondeu.")
    return None
