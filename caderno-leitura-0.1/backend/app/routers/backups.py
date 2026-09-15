from collections.abc import Iterator
from datetime import UTC, datetime
import logging
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from app.schemas.backups import RestoreResultResponse
from app.services.backups import create_backup_bundle, create_database_backup
from app.services.restore_service import restore_backup_package

router = APIRouter(tags=["Backup"])
logger = logging.getLogger(__name__)

DOWNLOAD_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
}


def temporary_backup(request: Request) -> Iterator[Path]:
    if "range" in request.headers:
        raise HTTPException(
            status_code=416,
            detail="Reinicie o download para baixar o backup completo.",
            headers=DOWNLOAD_HEADERS,
        )

    directory: TemporaryDirectory[str] | None = None

    try:
        try:
            directory = TemporaryDirectory(prefix="caderno-backup-")
            path = Path(directory.name) / "caderno.db"
            create_database_backup(path)

        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail="Banco não encontrado. Inicie o caderno normalmente e tente novamente.",
                headers=DOWNLOAD_HEADERS,
            ) from exc

        except TimeoutError as exc:
            raise HTTPException(
                status_code=503,
                detail="O banco está ocupado. Aguarde alguns segundos e tente novamente.",
                headers={
                    **DOWNLOAD_HEADERS,
                    "Retry-After": "5",
                },
            ) from exc

        except (OSError, sqlite3.Error) as exc:
            logger.exception("Não foi possível preparar o backup do caderno.")
            raise HTTPException(
                status_code=503,
                detail="Não foi possível gerar o backup. Consulte o terminal do servidor.",
                headers=DOWNLOAD_HEADERS,
            ) from exc

        yield path

    finally:
        if directory is not None:
            directory.cleanup()


def temporary_backup_bundle(request: Request) -> Iterator[Path]:
    if "range" in request.headers:
        raise HTTPException(
            status_code=416,
            detail="Reinicie o download para baixar o pacote completo.",
            headers=DOWNLOAD_HEADERS,
        )

    directory: TemporaryDirectory[str] | None = None

    try:
        try:
            directory = TemporaryDirectory(prefix="caderno-bundle-")
            ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            path = Path(directory.name) / f"caderno-backup-{ts}.zip"
            create_backup_bundle(path)

        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail="Banco de dados não encontrado.",
                headers=DOWNLOAD_HEADERS,
            ) from exc

        except TimeoutError as exc:
            raise HTTPException(
                status_code=503,
                detail="O banco está ocupado. Aguarde alguns segundos e tente novamente.",
                headers={**DOWNLOAD_HEADERS, "Retry-After": "5"},
            ) from exc

        except Exception as exc:
            logger.exception("Erro ao gerar pacote de backup universal.")
            raise HTTPException(
                status_code=503,
                detail="Não foi possível gerar o pacote de backup. Consulte o terminal do servidor.",
                headers=DOWNLOAD_HEADERS,
            ) from exc

        yield path

    finally:
        if directory is not None:
            directory.cleanup()


@router.get(
    "/backup",
    response_class=FileResponse,
    summary="Baixar backup do banco (.db)",
)
def download_backup(
    path: Annotated[Path, Depends(temporary_backup, scope="request")],
) -> FileResponse:
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%fZ")
    return FileResponse(
        path=path,
        filename=f"caderno-{timestamp}.db",
        media_type="application/octet-stream",
        headers={
            **DOWNLOAD_HEADERS,
            "Accept-Ranges": "none",
        },
    )


@router.get(
    "/backup/bundle",
    response_class=FileResponse,
    summary="Baixar pacote completo de backup (.zip com banco, capas e manifesto)",
)
def download_backup_bundle_endpoint(
    path: Annotated[Path, Depends(temporary_backup_bundle, scope="request")],
) -> FileResponse:
    return FileResponse(
        path=path,
        filename=path.name,
        media_type="application/zip",
        headers={
            **DOWNLOAD_HEADERS,
            "Accept-Ranges": "none",
        },
    )


@router.post(
    "/backup/restore",
    response_model=RestoreResultResponse,
    summary="Restaurar acervo a partir de pacote de backup (.zip ou .db)",
)
def restore_backup_endpoint(
    file: UploadFile = File(...),
) -> RestoreResultResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Arquivo não fornecido.",
        )

    with TemporaryDirectory(prefix="caderno-upload-restore-") as tmp_dir:
        temp_file = Path(tmp_dir) / file.filename
        try:
            with open(temp_file, "wb") as buffer:
                shutil_copy = file.file
                while chunk := shutil_copy.read(65536):
                    buffer.write(chunk)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falha ao receber arquivo enviado: {exc}",
            )

        if temp_file.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O arquivo enviado está vazio.",
            )

        try:
            return restore_backup_package(temp_file)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            )