from pathlib import Path

from fastapi import FastAPI
from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import get_database_path, get_frontend_dist_path

RESERVED_PREFIXES = {"api", "docs", "redoc", "openapi.json"}
BUILD_MISSING = (
    "A interface ainda não está compilada. Na pasta frontend, execute "
    "npm run build e abra novamente este endereço."
)


def accepts_html(headers: Headers) -> bool:
    for item in headers.get("accept", "").split(","):
        media_type, *parameters = item.lower().strip().split(";")
        if media_type.strip() not in {"text/html", "application/xhtml+xml"}:
            continue
        quality = 1.0
        for parameter in parameters:
            name, separator, value = parameter.strip().partition("=")
            if separator and name == "q":
                try:
                    quality = float(value)
                except ValueError:
                    quality = 0.0
        if 0 < quality <= 1:
            return True
    return False


class LocalFrontend:
    """Serve somente o build, depois de o roteador verificar todas as rotas."""

    def __init__(self, directory: Path, not_found: ASGIApp) -> None:
        self.files = StaticFiles(directory=directory, html=False, check_dir=False, follow_symlink=False)
        self.not_found = not_found

    async def index_response(self, scope: Scope) -> Response:
        try:
            response = await self.files.get_response("index.html", scope)
        except HTTPException as error:
            if error.status_code != 404:
                raise
            raise HTTPException(503, detail=BUILD_MISSING, headers={"Cache-Control": "no-store"}) from error
        # O HTML deve apontar sempre para os arquivos do build atual.
        response.headers["Cache-Control"] = "no-store"
        return response

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.not_found(scope, receive, send)
            return

        path = scope["path"].lstrip("/")
        parts = path.split("/")
        if (
            scope["method"] not in {"GET", "HEAD"}
            or parts[0].casefold() in RESERVED_PREFIXES
            or any(part.startswith(".") for part in parts if part)
            or any(character in path for character in ("\\", "\x00", ":"))
        ):
            await self.not_found(scope, receive, send)
            return

        if path in {"", "index.html"}:
            response = await self.index_response(scope)
        else:
            try:
                # StaticFiles resolve o caminho e impede escapar da pasta pública,
                # inclusive por links simbólicos para arquivos fora dela.
                response = await self.files.get_response(path, scope)
            except HTTPException as error:
                if error.status_code != 404:
                    raise
                # Arquivo ausente não recebe HTML no lugar de JS/CSS/imagem.
                if parts[0] == "assets" or any("." in part for part in parts) or not accepts_html(Headers(scope=scope)):
                    await self.not_found(scope, receive, send)
                    return
                response = await self.index_response(scope)

        if "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        await response(scope, receive, send)


def register_frontend(application: FastAPI, directory: Path | None = None) -> None:
    public_directory = (directory if directory is not None else get_frontend_dist_path()).resolve()
    if get_database_path().resolve().is_relative_to(public_directory):
        raise ValueError("O banco de dados deve ficar fora de frontend/dist, que é a pasta pública.")
    # O default só é usado após rotas, erros 405 e redirecionamentos da API.
    # Não acrescenta um catch-all que possa esconder um método inválido da API.
    application.router.default = LocalFrontend(public_directory, application.router.default)
