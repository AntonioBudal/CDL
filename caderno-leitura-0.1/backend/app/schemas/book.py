from datetime import date, datetime
from typing import Literal, Self
from pydantic import Field, field_validator, model_validator

from app.schemas.category import CategoryRead
from app.schemas.common import InputModel, NonBlankText, OutputModel
from app.schemas.sharing import ResourceOwnerSummary


# F0.11.01: estado de leitura do livro (nulo = sem estado).
BookReadingState = Literal["quero_ler", "lendo", "lido", "abandonado"]


class BookCreate(InputModel):
    title: NonBlankText
    author: str | None = None
    subtitle: str | None = None
    year: int | None = Field(default=None, ge=1000, le=2100)
    category_ids: list[str] = Field(default_factory=list)
    isbn: str | None = None
    publisher: str | None = Field(default=None, max_length=200)
    publication_place: str | None = Field(default=None, max_length=200)

    @field_validator("author", "subtitle", "publisher", "publication_place")
    @classmethod
    def normalize_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("isbn")
    @classmethod
    def normalize_isbn_field(cls, value: str | None) -> str | None:
        """F0.11.04: vazio limpa; senão grava o ISBN-13 sem separadores (ISBN-10 é convertido)."""
        if value is None or not value.strip():
            return None
        from app.services.isbn_service import InvalidIsbnError, normalize_isbn

        try:
            return normalize_isbn(value)
        except InvalidIsbnError as exc:
            raise ValueError(str(exc)) from exc


class BookPatch(InputModel):
    title: NonBlankText | None = None
    author: str | None = None
    subtitle: str | None = None
    year: int | None = Field(default=None, ge=1000, le=2100)
    cover_image: str | None = None
    category_ids: list[str] | None = None
    reading_state: BookReadingState | None = None
    reading_started_on: date | None = Field(default=None, strict=False)
    reading_finished_on: date | None = Field(default=None, strict=False)
    isbn: str | None = None
    publisher: str | None = Field(default=None, max_length=200)
    publication_place: str | None = Field(default=None, max_length=200)
    expected_updated_at: datetime | None = Field(default=None, strict=False)
    expected_version: int | None = Field(default=None, ge=1, strict=False, description="Versão esperada do livro para controle de concorrência")

    @field_validator("author", "subtitle")
    @classmethod
    def normalize_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or ""

    @field_validator("publisher", "publication_place")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("isbn")
    @classmethod
    def normalize_isbn_field(cls, value: str | None) -> str | None:
        """F0.11.04: vazio limpa; senão grava o ISBN-13 sem separadores (ISBN-10 é convertido)."""
        if value is None or not value.strip():
            return None
        from app.services.isbn_service import InvalidIsbnError, normalize_isbn

        try:
            return normalize_isbn(value)
        except InvalidIsbnError as exc:
            raise ValueError(str(exc)) from exc

    @model_validator(mode="after")
    def validate_has_changes(self) -> Self:
        payload_fields = self.model_fields_set - {"expected_updated_at", "expected_version"}
        if not payload_fields:
            raise ValueError("Envie pelo menos um campo para alterar.")
        return self


class BookRead(OutputModel):
    id: int
    title: str
    author: str | None = None
    subtitle: str | None = None
    year: int | None = None
    cover_image: str | None = None
    # Só o dono recebe estes três (o router zera para leitores de livros compartilhados).
    reading_state: BookReadingState | None = None
    reading_started_on: date | None = None
    reading_finished_on: date | None = None
    isbn: str | None = None
    publisher: str | None = None
    publication_place: str | None = None
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    categories: list[CategoryRead] = Field(default_factory=list)
    visibility: str = "private"
    can_edit: bool = True
    owner: ResourceOwnerSummary | None = None
