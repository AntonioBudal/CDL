from pydantic import Field

from app.schemas.common import InputModel, OutputModel


class CoverUrlRequest(InputModel):
    url: str = Field(..., min_length=10, max_length=2048, description="URL pública direta da imagem")


class CoverResponse(OutputModel):
    book_id: int
    cover_image: str | None = None
    cover_url: str | None = None
    message: str = "Capa atualizada com sucesso."
