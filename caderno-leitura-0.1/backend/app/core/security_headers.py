from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

DEFAULT_CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: https: blob:; "
    "connect-src 'self' https://accounts.google.com; "
    "frame-src 'self' https://accounts.google.com; "
    "frame-ancestors 'self'; "
    "base-uri 'self'; "
    "form-action 'self';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware HTTP para injeção incondicional de cabeçalhos de segurança consagrados e CSP."""

    def __init__(self, app, csp_policy: str = DEFAULT_CSP_POLICY):
        super().__init__(app)
        self.csp_policy = csp_policy

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Cabeçalhos de Segurança Obrigatórios (OWASP)
        response.headers["Content-Security-Policy"] = self.csp_policy
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # Blindagem de Rastreamento contra Indexação de Áreas Privadas
        path = request.url.path
        if (
            path.startswith("/api/")
            or path.startswith("/dashboard")
            or path.startswith("/livros")
            or path.startswith("/admin")
            or path.startswith("/estudos/")
        ):
            response.headers["X-Robots-Tag"] = "noindex, nofollow"

        return response
