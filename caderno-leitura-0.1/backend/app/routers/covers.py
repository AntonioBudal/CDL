"""Rotas controladas para servir arquivos estáticos de capas (/api/covers)."""
import os
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import get_covers_dir
from app.dependencies import CurrentUser, DatabaseSession

router = APIRouter(prefix="/covers", tags=["covers"])

SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+\.(webp|jpg|jpeg|png)$", re.IGNORECASE)


@router.get("/{filename}", summary="Servir a capa do livro (cofre cifrado ou arquivo legado)")
def get_cover_image(filename: str, current_user: CurrentUser, session: DatabaseSession):
    """Exige sessão (feature 090-B). A capa é servida a quem pode ler um livro que a usa; senão, 404."""
    from app.models.book import Book
    from app.routers.media import IMAGE_HEADERS, media_response
    from app.services import media_service
    from app.services.sharing_service import can_read_book

    row = media_service.by_reference(session, filename)
    if row is not None:
        if row.kind != "cover" or not media_service.can_view(session, current_user.id, row):
            raise HTTPException(status_code=404, detail="Capa não encontrada.")
        return media_response(session, row)

    # 1. Valida nome seguro contra path traversal e caracteres perigosos (arquivo legado em claro)
    if not SAFE_FILENAME_REGEX.match(filename) or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")
    books = session.query(Book).filter(Book.cover_image == filename, Book.deleted_at.is_(None)).all()
    if not any(can_read_book(session, current_user.id, book) for book in books):
        raise HTTPException(status_code=404, detail="Capa não encontrada.")

    # 2. Localiza arquivo no diretório dedicado de capas
    covers_dir = get_covers_dir()
    file_path = (covers_dir / os.path.basename(filename)).resolve()

    # 3. Garante confinamento estrito dentro do diretório de capas
    if not str(file_path).startswith(str(covers_dir)):
        raise HTTPException(status_code=400, detail="Acesso não autorizado.")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Capa não encontrada.")

    # 4. Determina Content-Type adequado
    ext = file_path.suffix.lower()
    media_type = "image/webp"
    if ext in (".jpg", ".jpeg"):
        media_type = "image/jpeg"
    elif ext == ".png":
        media_type = "image/png"

    return FileResponse(path=file_path, media_type=media_type, headers=IMAGE_HEADERS)
