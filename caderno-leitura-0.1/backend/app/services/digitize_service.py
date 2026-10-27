"""Digitalização de página manuscrita (feature 086); sem acesso ao banco.

O motor de leitura roda em outro ambiente Python (``motor/.venv``), num processo por pedido, chamado
pela linha de comando ``leitorum_motor`` (contrato ``motor-cli``). Este módulo valida e normaliza a
imagem, garante um pedido por vez e memória livre, encerra o motor por tempo limite ou desconexão do
cliente, apaga os arquivos temporários em qualquer desfecho e traduz a saída para a pré-visualização.
Nunca registra em log o texto lido nem caminhos temporários.
"""

from __future__ import annotations

import asyncio
import ctypes
import io
import json
import logging
import os
import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import (
    DIGITIZE_MAX_PIXELS,
    DIGITIZE_MAX_UPLOAD_BYTES,
    DIGITIZE_TIMEOUT_SECONDS,
    get_digitize_min_free_bytes,
    get_motor_config,
    get_motor_python,
)
from app.schemas.digitize import (
    DigitizeEngineRead,
    DigitizeLineRead,
    DigitizePreviewRead,
    DigitizeStatusRead,
    DigitizeWarningRead,
)

logger = logging.getLogger("leitorum.digitize")

ACCEPTED_FORMATS = {"JPEG", "PNG", "WEBP"}
MOTOR_SCHEMA = "leitorum-motor/1"
DEFAULT_LOW_CONFIDENCE = 0.75
CHECK_TIMEOUT_SECONDS = 60.0
POLL_SECONDS = 0.25
CLEANUP_SECONDS = 2.0
TEMP_PREFIX = "leitorum-digitize-"
EXIT_IMAGE, EXIT_INTEGRITY = 2, 3

WARNING_MESSAGES = {
    "draft": "Texto lido automaticamente. Pode conter erros: revise antes de salvar.",
    "no_text": "Nenhuma linha de texto foi encontrada. Fotografe a folha inteira, com boa luz e sem sombra.",
    "many_uncertain": "Mais da metade das linhas teve leitura incerta. Confira o texto com atenção ou tire outra foto.",
}

_busy = threading.Lock()
_status_cache: DigitizeStatusRead | None = None


class DigitizeError(Exception):
    def __init__(self, status: int, code: str, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail
        self.headers = headers


def _unavailable() -> DigitizeError:
    return DigitizeError(503, "unavailable", "A digitalização não está disponível nesta instalação.")


async def read_upload_limited(upload: UploadFile, limit: int | None = None) -> bytes:
    """Lê o upload em blocos e recusa acima do limite sem carregar o resto."""
    limit = limit or DIGITIZE_MAX_UPLOAD_BYTES
    buffer = bytearray()
    while chunk := await upload.read(1024 * 1024):
        buffer.extend(chunk)
        if len(buffer) > limit:
            raise DigitizeError(413, "too_large", "A imagem passa de 20 MB. Envie uma foto menor.")
    if not buffer:
        raise DigitizeError(422, "invalid_image", "Nenhuma imagem foi recebida.")
    return bytes(buffer)


def normalize_image(data: bytes, destination: Path, max_pixels: int | None = None) -> None:
    """Valida formato e tamanho, aplica a orientação gravada pela câmera e grava PNG RGB."""
    max_pixels = max_pixels or DIGITIZE_MAX_PIXELS
    try:
        image = Image.open(io.BytesIO(data))
    except (UnidentifiedImageError, Image.DecompressionBombError):
        raise DigitizeError(415, "unsupported_format", "Formato não suportado. Envie uma foto em JPEG, PNG ou WebP.")
    with image:
        if image.format not in ACCEPTED_FORMATS:
            raise DigitizeError(415, "unsupported_format", "Formato não suportado. Envie uma foto em JPEG, PNG ou WebP.")
        width, height = image.size
        if width * height > max_pixels:
            raise DigitizeError(413, "too_large", "A imagem tem resolução grande demais (acima de 40 megapixels).")
        try:
            image.load()
            ImageOps.exif_transpose(image).convert("RGB").save(destination, format="PNG")
        except (OSError, ValueError, SyntaxError):
            raise DigitizeError(422, "invalid_image", "A imagem está corrompida ou incompleta. Tente outra foto.")


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_memory_bytes() -> int | None:
    """Memória física livre do sistema, ou ``None`` quando não há como medir."""
    try:
        if os.name == "nt":
            status = _MemoryStatus()
            status.dwLength = ctypes.sizeof(_MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return int(status.ullAvailPhys)
            return None
        with open("/proc/meminfo", encoding="ascii") as meminfo:
            for line in meminfo:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError, AttributeError):
        return None
    return None


def _motor_command(*arguments: str) -> list[str]:
    return [str(get_motor_python()), "-I", "-m", "leitorum_motor", *arguments, "--config", str(get_motor_config())]


def _creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def engine_status(refresh: bool = False) -> DigitizeStatusRead:
    """Disponibilidade do motor; o ``check`` roda uma vez e fica em cache até falhar ou reiniciar."""
    global _status_cache
    if _status_cache is not None and not refresh:
        return _status_cache
    if not get_motor_python().is_file():
        _status_cache = DigitizeStatusRead(available=False, reason="not_installed")
        return _status_cache
    try:
        completed = subprocess.run(
            _motor_command("check"),
            capture_output=True,
            timeout=CHECK_TIMEOUT_SECONDS,
            creationflags=_creation_flags(),
        )
    except (OSError, subprocess.TimeoutExpired):
        _status_cache = DigitizeStatusRead(available=False, reason="not_installed")
        return _status_cache
    if completed.returncode == 0:
        _status_cache = DigitizeStatusRead(available=True, reason=None)
    elif completed.returncode == EXIT_INTEGRITY:
        _status_cache = DigitizeStatusRead(available=False, reason="integrity_failed")
    else:
        _status_cache = DigitizeStatusRead(available=False, reason="not_installed")
    return _status_cache


def reset_status_cache() -> None:
    global _status_cache
    _status_cache = None


def low_confidence_threshold() -> float:
    try:
        config = json.loads(get_motor_config().read_text(encoding="utf-8"))
        return float(config["low_confidence"])
    except (OSError, ValueError, KeyError, TypeError):
        return DEFAULT_LOW_CONFIDENCE


def _kill(process: subprocess.Popen) -> None:
    process.kill()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


async def run_engine(
    image: Path,
    output: Path,
    is_disconnected: Callable[[], Awaitable[bool]],
    timeout: float | None = None,
) -> int:
    """Roda o motor; encerra por tempo limite ou desconexão. Devolve o código de saída."""
    timeout = timeout or DIGITIZE_TIMEOUT_SECONDS
    workdir = image.parent
    try:
        with open(workdir / "motor.log", "wb") as log:
            process = subprocess.Popen(
                _motor_command("read", "--image", str(image), "--out", str(output)),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=log,
                cwd=workdir,
                creationflags=_creation_flags(),
            )
    except OSError:
        reset_status_cache()
        raise _unavailable()
    deadline = time.monotonic() + timeout
    while (code := process.poll()) is None:
        if time.monotonic() > deadline:
            _kill(process)
            raise DigitizeError(504, "timeout", "A leitura demorou demais e foi interrompida. Tente outra foto.")
        if await is_disconnected():
            _kill(process)
            raise DigitizeError(499, "cancelled", "Leitura cancelada.")
        await asyncio.sleep(POLL_SECONDS)
    return code


def _engine_failed() -> DigitizeError:
    return DigitizeError(500, "engine_failed", "O motor de leitura falhou nesta imagem. Tente outra foto.")


def to_preview(result: Any, threshold: float, elapsed_ms: int) -> DigitizePreviewRead:
    """Traduz a saída ``leitorum-motor/1``; levanta ``engine_failed`` se o formato não confere."""
    try:
        if result["schema"] != MOTOR_SCHEMA:
            raise ValueError
        raw_lines = [(str(line["text"]), float(line["confidence"])) for line in result["lines"]]
        engine = DigitizeEngineRead(**{key: str(result["engine"][key]) for key in ("name", "version", "reader", "license_status")})
    except (KeyError, TypeError, ValueError):
        raise _engine_failed()
    lines = [
        DigitizeLineRead(index=index, text=text, confidence=min(1.0, max(0.0, confidence)), low_confidence=confidence < threshold)
        for index, (text, confidence) in enumerate(raw_lines)
    ]
    uncertain = sum(line.low_confidence for line in lines)
    codes = ["draft"]
    if not lines:
        codes.append("no_text")
    elif uncertain > len(lines) / 2:
        codes.append("many_uncertain")
    return DigitizePreviewRead(
        text="\n".join(line.text for line in lines),
        lines=lines,
        low_confidence_count=uncertain,
        warnings=[DigitizeWarningRead(code=code, message=WARNING_MESSAGES[code]) for code in codes],
        engine=engine,
        elapsed_ms=elapsed_ms,
    )


def _remove(directory: Path) -> None:
    """Apaga a pasta temporária; o Windows pode segurar o arquivo por instantes após o processo morrer."""
    deadline = time.monotonic() + CLEANUP_SECONDS
    while True:
        shutil.rmtree(directory, ignore_errors=True)
        if not directory.exists() or time.monotonic() > deadline:
            break
        time.sleep(0.1)
    if directory.exists():
        logger.warning("digitize: pasta temporária não pôde ser removida")


async def preview(upload: UploadFile, is_disconnected: Callable[[], Awaitable[bool]]) -> DigitizePreviewRead:
    """Pedido completo: um por vez, memória livre, imagem normalizada, motor, limpeza garantida."""
    started = time.monotonic()
    if not _busy.acquire(blocking=False):
        raise DigitizeError(
            503, "busy", "Outra página está sendo lida agora. Tente de novo em instantes.", headers={"Retry-After": "15"}
        )
    workdir: Path | None = None
    code = "error"
    try:
        status = await asyncio.to_thread(engine_status)
        if not status.available:
            raise _unavailable()
        data = await read_upload_limited(upload)
        workdir = Path(tempfile.mkdtemp(prefix=TEMP_PREFIX))
        image, output = workdir / "pagina.png", workdir / "leitura.json"
        await asyncio.to_thread(normalize_image, data, image)
        del data
        free = free_memory_bytes()
        if free is not None and free < get_digitize_min_free_bytes():
            raise DigitizeError(503, "low_memory", "Pouca memória livre no computador agora. Feche outros programas e tente de novo.")
        exit_code = await run_engine(image, output, is_disconnected)
        if exit_code == EXIT_IMAGE:
            raise DigitizeError(422, "invalid_image", "A imagem não pôde ser lida. Tente outra foto.")
        if exit_code == EXIT_INTEGRITY:
            reset_status_cache()
            raise _unavailable()
        if exit_code != 0:
            raise _engine_failed()
        try:
            result = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise _engine_failed()
        response = to_preview(result, low_confidence_threshold(), round((time.monotonic() - started) * 1000))
        code = "ok"
        logger.info("digitize: ok, %d linhas, %d ms", len(response.lines), response.elapsed_ms)
        return response
    except DigitizeError as error:
        code = error.code
        raise
    finally:
        if workdir is not None:
            await asyncio.to_thread(_remove, workdir)
        _busy.release()
        if code != "ok":
            logger.info("digitize: %s, %d ms", code, round((time.monotonic() - started) * 1000))
