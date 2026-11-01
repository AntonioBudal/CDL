from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import is_google_auth_enabled

GOOGLE_ACCOUNTS = "https://accounts.google.com"

# Rotas que os buscadores podem indexar (F0.10.02); todo o resto recebe noindex, inclusive rotas novas.
PUBLIC_INDEXABLE_PATHS = frozenset({"/", "/sobre", "/apoie", "/robots.txt", "/sitemap.xml"})
PUBLIC_INDEXABLE_PREFIXES = ("/compartilhado/", "/.well-known/")


def build_csp(google_enabled: bool) -> str:
    """CSP sem domínios externos; com o login com Google ativo, só accounts.google.com, e só onde o botão precisa.

    style-src mantém 'unsafe-inline' (estilos dinâmicos do Vue); script-src não, porque o bootstrap de aparência é
    servido como arquivo (appearance-bootstrap.js) desde a F0.10.02.
    """
    google = f" {GOOGLE_ACCOUNTS}" if google_enabled else ""
    return (
        "default-src 'self'; "
        f"script-src 'self'{google}; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "img-src 'self' data: blob:; "
        f"connect-src 'self'{google}; "
        f"frame-src 'self'{google}; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )


def is_public_indexable(path: str) -> bool:
    return path in PUBLIC_INDEXABLE_PATHS or path.startswith(PUBLIC_INDEXABLE_PREFIXES)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware HTTP para injeção incondicional de cabeçalhos de segurança consagrados e CSP."""

    def __init__(self, app, csp_policy: str | None = None):
        super().__init__(app)
        # Política fixa só quando passada explicitamente; o padrão acompanha a configuração do Google a cada pedido.
        self.csp_policy = csp_policy

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Cabeçalhos de Segurança Obrigatórios (OWASP)
        response.headers["Content-Security-Policy"] = self.csp_policy or build_csp(is_google_auth_enabled())
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Blindagem de rastreamento: só as rotas públicas ficam indexáveis.
        if not is_public_indexable(request.url.path):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"

        return response
