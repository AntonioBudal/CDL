"""Servidor local da ferramenta de caixas e linhas: só ``127.0.0.1``, biblioteca padrão, sem rede
externa. A página (``static/``) edita; toda validação é do ``store``.

Uso, a partir de ``document-intelligence/``::

    uv run python -m tools.anotar.server [--port 8766]

e abrir http://127.0.0.1:8766/ no navegador.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from . import store
from .paths import STATIC, Paths, default_paths

LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_BODY = 5 * 1024 * 1024
PAGE = r"(p[0-9]{2,3})"
ROUTE_PAGE = re.compile(rf"^/api/pages/{PAGE}$")
ROUTE_DRAFT = re.compile(rf"^/api/pages/{PAGE}/draft$")
ROUTE_IMAGE = re.compile(rf"^/img/{PAGE}\.jpg$")
STATIC_FILES = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}


class Handler(BaseHTTPRequestHandler):
    server_version = "LeitorumAnotar/1"
    paths: Paths  # definido em make_server

    def log_message(self, format: str, *args) -> None:  # noqa: A002 — assinatura da base
        status = args[1] if len(args) > 1 else ""
        sys.stderr.write(f"{self.command} {urlparse(self.path).path} {status}\n")

    # ------------------------------------------------------------ respostas

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' blob:; style-src 'self'; script-src 'self'; "
            "connect-src 'self'; frame-ancestors 'none'",
        )
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json")

    def _error(self, status: HTTPStatus, message: str, **extra) -> None:
        self._json(status, {"error": message, **extra})

    def _body(self) -> dict | None:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            remaining = min(length, 16 * MAX_BODY)  # descarta, para a resposta chegar inteira
            while remaining > 0:
                chunk = self.rfile.read(min(remaining, 1 << 20))
                if not chunk:
                    break
                remaining -= len(chunk)
            self.close_connection = True
            self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "corpo grande demais")
            return None
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._error(HTTPStatus.BAD_REQUEST, "JSON inválido")
            return None
        if not isinstance(data, dict):
            self._error(HTTPStatus.BAD_REQUEST, "esperado um objeto JSON")
            return None
        return data

    def _path(self) -> str | None:
        raw = urlparse(self.path).path
        decoded = unquote(raw)
        if decoded != raw or ".." in decoded or "\\" in decoded:
            self._error(HTTPStatus.NOT_FOUND, "caminho inválido")
            return None
        return decoded

    def _guard_host(self) -> bool:
        """Recusa pedidos com ``Host`` de fora (proteção contra DNS rebinding)."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        if host not in LOCAL_HOSTS:
            self._error(HTTPStatus.FORBIDDEN, "host não permitido")
            return False
        return True

    # ------------------------------------------------------------ rotas

    def do_GET(self) -> None:  # noqa: N802 — nome da base
        if not self._guard_host():
            return
        path = self._path()
        if path is None:
            return
        try:
            if path in STATIC_FILES:
                file = STATIC / STATIC_FILES[path]
                kind = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                if kind.startswith("text/") or kind.endswith("javascript"):
                    kind += "; charset=utf-8"
                self._send(HTTPStatus.OK, file.read_bytes(), kind)
            elif path == "/api/pages":
                self._json(HTTPStatus.OK, {"pages": store.list_pages(self.paths)})
            elif match := ROUTE_PAGE.match(path):
                self._json(HTTPStatus.OK, store.load_page(self.paths, match.group(1)))
            elif match := ROUTE_IMAGE.match(path):
                image = store.image_path(self.paths, match.group(1))
                self._send(HTTPStatus.OK, image.read_bytes(), "image/jpeg")
            else:
                self._error(HTTPStatus.NOT_FOUND, "rota inexistente")
        except store.NotFoundError:
            self._error(HTTPStatus.NOT_FOUND, "página inexistente")
        except store.BlockedError:
            self._error(
                HTTPStatus.FORBIDDEN,
                "foto sem hash conferido: não é a página registrada pelo EXP-027",
            )

    def do_PUT(self) -> None:  # noqa: N802
        if not self._guard_host():
            return
        path = self._path()
        if path is None:
            return
        match = ROUTE_PAGE.match(path)
        if not match:
            self._error(HTTPStatus.NOT_FOUND, "rota inexistente")
            return
        body = self._body()
        if body is None:
            return
        version = body.get("version")
        if not isinstance(version, int):
            self._error(HTTPStatus.BAD_REQUEST, "falta a versão lida (version)")
            return
        try:
            doc = store.save_page(
                self.paths,
                match.group(1),
                body.get("doc"),
                expected_version=version,
                seconds_delta=body.get("seconds_delta"),
            )
            self._json(HTTPStatus.OK, {"doc": doc})
        except store.ConflictError as conflict:
            self._error(
                HTTPStatus.CONFLICT,
                "a página foi gravada em outra aba; recarregue",
                current_version=conflict.current_version,
            )
        except store.InvalidError as invalid:
            self._error(
                HTTPStatus.UNPROCESSABLE_ENTITY, "documento inválido", errors=invalid.errors
            )
        except store.NotFoundError:
            self._error(HTTPStatus.NOT_FOUND, "página inexistente")
        except store.BlockedError:
            self._error(HTTPStatus.FORBIDDEN, "foto sem hash conferido")

    def do_POST(self) -> None:  # noqa: N802
        if not self._guard_host():
            return
        path = self._path()
        if path is None:
            return
        match = ROUTE_DRAFT.match(path)
        if not match:
            self._error(HTTPStatus.NOT_FOUND, "rota inexistente")
            return
        body = self._body()
        if body is None:
            return
        text, label = body.get("text"), body.get("label") or "rascunho"
        if not isinstance(text, str) or not isinstance(label, str):
            self._error(HTTPStatus.BAD_REQUEST, "text e label precisam ser texto")
            return
        try:
            doc = body.get("doc") or store.load_page(self.paths, match.group(1))
            self._json(HTTPStatus.OK, {"doc": store.import_draft(doc, text, label)})
        except store.NotFoundError:
            self._error(HTTPStatus.NOT_FOUND, "página inexistente")
        except store.BlockedError:
            self._error(HTTPStatus.FORBIDDEN, "foto sem hash conferido")
        except (KeyError, TypeError):
            self._error(HTTPStatus.BAD_REQUEST, "documento malformado")


def make_server(paths: Paths, host: str = "127.0.0.1", port: int = 8766) -> ThreadingHTTPServer:
    if host not in LOCAL_HOSTS:
        raise ValueError("a ferramenta só escuta no próprio computador (127.0.0.1)")
    handler = type("BoundHandler", (Handler,), {"paths": paths})
    return ThreadingHTTPServer((host, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ferramenta local de caixas e linhas")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    paths = default_paths()
    httpd = make_server(paths, port=args.port)
    pages = store.list_pages(paths)
    blocked = sum(1 for page in pages if not page["hash_ok"])
    print(f"{len(pages)} páginas preparadas ({blocked} sem hash conferido)")
    print(f"Abra http://127.0.0.1:{args.port}/  (Ctrl+C para parar)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

