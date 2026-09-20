from datetime import datetime
from typing import Self
from pydantic import Field, field_validator, model_validator

from app.schemas.category import CategoryRead
from app.schemas.common import InputModel, NonBlankText, OutputModel


class BookCreate(InputModel):
    title: NonBlankText
    author: str | None = None
    subtitle: str | None = None
    year: int | None = Field(default=None, ge=1000, le=2100)
    category_ids: list[str] = Field(default_factory=list)

    @field_validator("author", "subtitle")
    @classmethod
    def normalize_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class BookPatch(InputModel):
    title: NonBlankText | None = None
    author: str | None = None
    subtitle: str | None = None
    year: int | None = Field(default=None, ge=1000, le=2100)
    cover_image: str | None = None
    category_ids: list[str] | None = None
    expected_updated_at: datetime | None = Field(default=None, strict=False)

    @field_validator("author", "subtitle")
    @classmethod
    def normalize_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or ""

    @model_validator(mode="after")
    def validate_has_changes(self) -> Self:
        payload_fields = self.model_fields_set - {"expected_updated_at"}
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    categories: list[CategoryRead] = Field(default_factory=list)
