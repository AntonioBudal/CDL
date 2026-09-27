import math
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Tuple

from fastapi import HTTPException, Request, status

from app.core.config import (
    get_rate_limit_max_attempts,
    get_rate_limit_window_seconds,
)


class InMemoryRateLimiter:
    """Gerenciador de taxa em memória com algoritmo de janela deslizante."""

    def __init__(self, max_attempts: int | None = None, window_seconds: int | None = None):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    @property
    def max_attempts(self) -> int:
        return self._max_attempts if self._max_attempts is not None else get_rate_limit_max_attempts()

    @property
    def window_seconds(self) -> int:
        return self._window_seconds if self._window_seconds is not None else get_rate_limit_window_seconds()

    def check_rate_limit(self, key: str) -> Tuple[bool, int]:
        """
        Verifica se a chave excedeu o limite de requisições na janela deslizante.
        Retorna (is_allowed, retry_after_seconds).
        Se permitido, consome uma tentativa na janela.
        """
        now = time.time()
        window = self.window_seconds
        max_attempts = self.max_attempts

        with self._lock:
            timestamps = self._hits[key]
            # Remove timestamps fora da janela deslizante
            cutoff = now - window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= max_attempts:
                # Calcula quantos segundos faltam para o timestamp mais antigo sair da janela
                oldest = timestamps[0]
                retry_after = max(1, math.ceil((oldest + window) - now))
                return False, retry_after

            # Registra a tentativa
            timestamps.append(now)
            return True, 0

    def reset(self, key: str | None = None) -> None:
        """Limpa o histórico de uma chave específica ou de todas as chaves."""
        with self._lock:
            if key is not None:
                self._hits.pop(key, None)
            else:
                self._hits.clear()


# Singleton global para proteção de autenticação em processo único
auth_rate_limiter = InMemoryRateLimiter()


def get_client_ip(request: Request) -> str:
    """Extrai o IP do cliente respeitando cabeçalhos de proxy reverso se presentes."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Pega o primeiro IP da lista (cliente real original)
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


async def rate_limit_auth_endpoint(request: Request) -> None:
    """
    Dependência FastAPI para aplicar rate limiting por IP e endpoint de autenticação.
    Levanta HTTPException(429) com cabeçalho Retry-After quando o limite é excedido.
    """
    client_ip = get_client_ip(request)
    path = request.url.path
    key = f"{client_ip}:{path}"

    is_allowed, retry_after = auth_rate_limiter.check_rate_limit(key)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Aguarde {retry_after} segundos antes de tentar novamente.",
            headers={"Retry-After": str(retry_after)},
        )
