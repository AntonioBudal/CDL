"""Conferência de origem dos pedidos que alteram dados (F0.10.02, defesa contra CSRF além do SameSite=Lax).

Em POST, PUT, PATCH e DELETE sob /api/:
- com Origin: aceita se o host da origem for o Host do pedido, o X-Forwarded-Host (proxy na frente, ex.: Tailscale
  com HTTPS) ou uma origem confiável (CADERNO_CORS_ORIGINS e LEITORUM_TRUSTED_ORIGINS); "null" é recusado;
- sem Origin: recusa só se Sec-Fetch-Site disser cross-site ou same-site. Clientes sem esses cabeçalhos (scripts
  locais, TestClient) seguem passando, e o cookie SameSite=Lax continua valendo para eles.
"""
from __future__ import annotations

import logging
from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_cors_allowed_origins, get_trusted_origins

logger = logging.getLogger(__name__)

PROTECTED_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
REJECTED_FETCH_SITES = frozenset({"cross-site", "same-site"})
REJECTION = {"detail": "Origem do pedido não autorizada."}


def _netloc(value: str) -> str:
    return urlsplit(value).netloc.lower() if "://" in value else value.strip().lower()


def is_origin_allowed(request: Request) -> bool:
    origin = request.headers.get("origin")
    if origin is None:
        return request.headers.get("sec-fetch-site", "").lower() not in REJECTED_FETCH_SITES
    if origin.strip().lower() == "null":
        return False

    origin_host = _netloc(origin)
    if not origin_host:
        return False
    hosts = {request.headers.get("host", "").lower()}
    forwarded = request.headers.get("x-forwarded-host")
    if forwarded:
        hosts.add(forwarded.split(",")[0].strip().lower())
    if origin_host in hosts:
        return True
    trusted = {_netloc(item) for item in [*get_cors_allowed_origins(), *get_trusted_origins()]}
    return origin_host in trusted


class OriginGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method in PROTECTED_METHODS and request.url.path.startswith("/api/") and not is_origin_allowed(request):
            # Só método, caminho e origem: nunca corpo, cookies ou cabeçalhos de autenticação.
            logger.warning(
                "Pedido recusado pela conferência de origem: %s %s (Origin=%r, Sec-Fetch-Site=%r)",
                request.method,
                request.url.path,
                request.headers.get("origin"),
                request.headers.get("sec-fetch-site"),
            )
            return JSONResponse(status_code=403, content=REJECTION)
        return await call_next(request)
