from pydantic import field_validator

from app.schemas.common import InputModel, NonBlankText, OutputModel


class BookCreate(InputModel):
    title: NonBlankText
    author: str | None = None

    @field_validator("author")
    @classmethod
    def normalize_author(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class BookRead(OutputModel):
    id: int
    title: str
    author: str | None
