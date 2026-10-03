from __future__ import annotations

from collections import defaultdict, deque
import ipaddress
import math
from threading import Lock
import time
from typing import Tuple

from fastapi import HTTPException, Request, status

from app.core.config import (
    get_auth_failure_lockout_seconds,
    get_auth_max_attempts_per_minute,
    get_auth_max_consecutive_failures,
    get_rate_limit_max_attempts,
    get_rate_limit_window_seconds,
)


class InMemoryRateLimiter:
    """Gerenciador de taxa em memória com algoritmo de janela deslizante thread-safe."""

    def __init__(self, max_attempts: int | None = None, window_seconds: int | None = None):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    @property
    def max_attempts(self) -> int:
        return self._max_attempts if self._max_attempts is not None else get_auth_max_attempts_per_minute()

    @property
    def window_seconds(self) -> int:
        return self._window_seconds if self._window_seconds is not None else 60

    def check_rate_limit(
        self,
        key: str,
        max_attempts: int | None = None,
        window_seconds: int | None = None,
    ) -> Tuple[bool, int]:
        """
        Verifica se a chave excedeu o limite de requisições na janela deslizante.
        Retorna (is_allowed, retry_after_seconds).
        Se permitido, consome uma tentativa na janela.
        """
        now = time.time()
        window = window_seconds if window_seconds is not None else self.window_seconds
        limit = max_attempts if max_attempts is not None else self.max_attempts

        with self._lock:
            timestamps = self._hits[key]
            cutoff = now - window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= limit:
                oldest = timestamps[0]
                retry_after = max(1, math.ceil((oldest + window) - now))
                return False, retry_after

            timestamps.append(now)
            return True, 0

    def reset(self, key: str | None = None) -> None:
        """Limpa o histórico de uma chave específica ou de todas as chaves."""
        with self._lock:
            if key is not None:
                self._hits.pop(key, None)
            else:
                self._hits.clear()


class AuthFailureTracker:
    """Rastreador de falhas consecutivas de autenticação por IP para bloqueio escalonado (Q1: A)."""

    def __init__(self):
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._locked_until: dict[str, float] = {}
        self._lock = Lock()

    def is_locked(self, ip: str) -> Tuple[bool, int]:
        """Verifica se o IP está sob bloqueio temporário devido a falhas consecutivas."""
        now = time.time()
        with self._lock:
            locked_at = self._locked_until.get(ip)
            if locked_at is not None:
                if now < locked_at:
                    remaining = max(1, math.ceil(locked_at - now))
                    return True, remaining
                # Bloqueio expirou
                del self._locked_until[ip]
                self._failures.pop(ip, None)
            return False, 0

    def record_failure(self, ip: str) -> Tuple[bool, int]:
        """
        Registra uma falha de autenticação.
        Se acumular 5 falhas consecutivas dentro de 60s, aciona o bloqueio de 60s.
        Retorna (is_now_locked, retry_after).
        """
        now = time.time()
        max_failures = get_auth_max_consecutive_failures()
        lockout_duration = get_auth_failure_lockout_seconds()
        window = 60.0

        with self._lock:
            timestamps = self._failures[ip]
            cutoff = now - window
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            timestamps.append(now)

            if len(timestamps) >= max_failures:
                self._locked_until[ip] = now + lockout_duration
                return True, lockout_duration

            return False, 0

    def reset_failures(self, ip: str) -> None:
        """Zera o contador de falhas para o IP após login bem-sucedido."""
        with self._lock:
            self._failures.pop(ip, None)
            self._locked_until.pop(ip, None)

    def reset_all(self) -> None:
        """Limpa todo o estado do rastreador."""
        with self._lock:
            self._failures.clear()
            self._locked_until.clear()


# Singletons globais para proteção em processo único
auth_rate_limiter = InMemoryRateLimiter()
auth_failure_tracker = AuthFailureTracker()


def _sanitize_ip_string(candidate: str) -> str | None:
    """Limpa e valida sintaticamente um endereço IP (IPv4 ou IPv6), removendo portas se presentes."""
    if not candidate:
        return None
    val = candidate.strip()
    # Se contiver colchetes (ex: [2001:db8::1]:8080)
    if val.startswith("[") and "]" in val:
        val = val[1 : val.index("]")]
    # Se for IPv4 com porta (ex: 192.168.1.10:8080)
    elif ":" in val and val.count(":") == 1:
        val = val.split(":")[0]

    try:
        ip_obj = ipaddress.ip_address(val)
        return str(ip_obj)
    except ValueError:
        return None


def get_client_ip(request: Request) -> str:
    """Extrai e valida o IP real do cliente respeitando Cloudflare Tunnel e proxies confiáveis."""
    # 1. Cloudflare Tunnel / Edge header oficial
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        sanitized = _sanitize_ip_string(cf_ip)
        if sanitized:
            return sanitized

    # 2. X-Forwarded-For (primeiro IP da cadeia é o cliente original)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first_ip = forwarded.split(",")[0].strip()
        sanitized = _sanitize_ip_string(first_ip)
        if sanitized:
            return sanitized

    # 3. X-Real-IP
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        sanitized = _sanitize_ip_string(real_ip)
        if sanitized:
            return sanitized

    # 4. Socket direto
    if request.client and request.client.host:
        sanitized = _sanitize_ip_string(request.client.host)
        if sanitized:
            return sanitized

    # 5. Fallback seguro
    return "127.0.0.1"


async def rate_limit_auth_endpoint(request: Request) -> None:
    """
    Dependência FastAPI combinada para proteção de endpoints sensíveis:
    1. Bloqueia se o IP estiver em lockout de falhas consecutivas de senha.
    2. Aplica controle volumétrico geral (30 req/minuto por IP).
    """
    client_ip = get_client_ip(request)

    # 1. Verifica lockout por falhas consecutivas
    is_locked, retry_after = auth_failure_tracker.is_locked(client_ip)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas incorretas. Aguarde {retry_after} segundos antes de tentar novamente.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2. Verifica cota volumétrica geral de requisições de auth
    is_allowed, retry_after_vol = auth_rate_limiter.check_rate_limit(
        key=f"{client_ip}:auth_volumetric",
        max_attempts=get_auth_max_attempts_per_minute(),
        window_seconds=60,
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas requisições. Aguarde {retry_after_vol} segundos antes de tentar novamente.",
            headers={"Retry-After": str(retry_after_vol)},
        )


def record_auth_failure(request: Request) -> None:
    """Registra falha de credenciais para o IP da requisição. Se atingir o limite, bloqueia e levanta 429 imediatamente."""
    ip = get_client_ip(request)
    is_locked, retry_after = auth_failure_tracker.record_failure(ip)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas incorretas. Aguarde {retry_after} segundos antes de tentar novamente.",
            headers={"Retry-After": str(retry_after)},
        )


def record_auth_success(request: Request) -> None:
    """Zera o contador de falhas para o IP da requisição após autenticação válida."""
    ip = get_client_ip(request)
    auth_failure_tracker.reset_failures(ip)
