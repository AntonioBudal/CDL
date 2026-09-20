from datetime import datetime
from typing import Literal, Self
from pydantic import Field, model_validator

from app.schemas.common import InputModel, NonBlankText, OutputModel, Position


class ChapterCreate(InputModel):
    name: NonBlankText
    position: Position | None = Field(
        default=None, description="Se omitida, a posição será após o último capítulo do livro."
    )


class ChapterPatch(InputModel):
    name: NonBlankText | None = None
    expected_updated_at: datetime | None = Field(default=None, strict=False)

    @model_validator(mode="after")
    def validate_has_changes(self) -> Self:
        payload_fields = self.model_fields_set - {"expected_updated_at"}
        if not payload_fields:
            raise ValueError("Envie pelo menos um campo para alterar.")
        return self


class ChapterMove(InputModel):
    direction: Literal["up", "down"]


class ChapterRead(OutputModel):
    id: int
    book_id: int
    name: str
    position: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
