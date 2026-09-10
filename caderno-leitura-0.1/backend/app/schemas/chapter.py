from pydantic import Field

from app.schemas.common import InputModel, NonBlankText, OutputModel, Position


class ChapterCreate(InputModel):
    name: NonBlankText
    position: Position | None = Field(
        default=None, description="Se omitida, a posição será após o último capítulo do livro."
    )


class ChapterRead(OutputModel):
    id: int
    book_id: int
    name: str
    position: int
