"""Rotas controladas para servir arquivos estáticos de capas (/api/covers)."""
import os
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import get_covers_dir

router = APIRouter(prefix="/covers", tags=["covers"])

SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-]+\.(webp|jpg|jpeg|png)$", re.IGNORECASE)


@router.get("/{filename}", summary="Servir arquivo de capa de livro")
def get_cover_image(filename: str) -> FileResponse:
    """Retorna o arquivo de imagem da capa armazenado no servidor com cache HTTP.

    Aplica validação rígida contra path traversal e sanitização de nome.
    """
    # 1. Valida nome seguro contra path traversal e caracteres perigosos
    if not SAFE_FILENAME_REGEX.match(filename) or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")

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

    return FileResponse(
        path=file_path,
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=86400",
        },
    )
