"""Feature 086: API de digitalização com motor falso e banco descartável em tmp_path.

O cliente é criado sem ``with`` para não rodar a manutenção de inicialização (lifespan), que não usa
a sessão substituída dos testes.
"""

import asyncio
import io
import json
import os
import sys
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import UploadFile
from fastapi.testclient import TestClient
from PIL import Image
import pytest
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, get_digitize_min_free_bytes
from app.db.session import create_sqlite_engine, get_session
from app.main import create_app
from app.services import digitize_service
from app.services.digitize_service import DigitizeError

FAKE_MOTOR = Path(__file__).with_name("fake_motor.py")


def image_bytes(fmt: str = "PNG", size: tuple[int, int] = (60, 40), orientation: int | None = None) -> bytes:
    buffer = io.BytesIO()
    image = Image.new("RGB", size, "white")
    if orientation:
        exif = Image.Exif()
        exif[0x0112] = orientation
        image.save(buffer, format=fmt, exif=exif)
    else:
        image.save(buffer, format=fmt)
    return buffer.getvalue()


def leftover_dirs() -> set[str]:
    return {p.name for p in Path(tempfile.gettempdir()).glob(digitize_service.TEMP_PREFIX + "*")}


@pytest.fixture
def client(tmp_path):
    path = tmp_path / "acervo-digitalizar.db"
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_path"] = path
    command.upgrade(config, "head")
    engine = create_sqlite_engine(path)
    application = create_app()

    def test_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    application.dependency_overrides[get_session] = test_session
    try:
        yield TestClient(application)
    finally:
        engine.dispose()


@pytest.fixture
def motor(monkeypatch, tmp_path):
    """Motor falso: devolve uma função que escolhe o modo e o caminho do rastro."""
    trace = tmp_path / "rastro.json"
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"low_confidence": 0.80}))
    monkeypatch.setenv("LEITORUM_MOTOR_PYTHON", sys.executable)
    monkeypatch.setenv("LEITORUM_DIGITIZE_MIN_FREE_MB", "0")
    monkeypatch.setenv("FAKE_MOTOR_TRACE", str(trace))
    monkeypatch.setattr(digitize_service, "get_motor_config", lambda: config)
    monkeypatch.setattr(digitize_service, "_motor_command", lambda *args: [sys.executable, str(FAKE_MOTOR), *args])
    digitize_service.reset_status_cache()

    def use(mode: str = "ok") -> Path:
        monkeypatch.setenv("FAKE_MOTOR_MODE", mode)
        digitize_service.reset_status_cache()
        return trace

    use("ok")
    yield use
    digitize_service.reset_status_cache()


def post_image(client, data: bytes, name: str = "pagina.png", content_type: str = "image/png"):
    return client.post("/api/digitize/preview", files={"file": (name, data, content_type)})


def assert_cleaned(trace: Path) -> None:
    assert trace.is_file(), "o motor falso deveria ter sido chamado"
    assert not Path(json.loads(trace.read_text())["workdir"]).exists()


# --- US1: status e pré-visualização ----------------------------------------------------------


def test_status_available(client, motor):
    response = client.get("/api/digitize/status")
    assert response.status_code == 200
    assert response.json() == {"available": True, "reason": None}
    assert response.headers["cache-control"] == "no-store"


def test_status_not_installed(client, motor, monkeypatch, tmp_path):
    monkeypatch.setenv("LEITORUM_MOTOR_PYTHON", str(tmp_path / "ausente" / "python.exe"))
    digitize_service.reset_status_cache()
    assert client.get("/api/digitize/status").json() == {"available": False, "reason": "not_installed"}
    response = post_image(client, image_bytes())
    assert response.status_code == 503
    assert response.json()["code"] == "unavailable"


def test_status_integrity_failed(client, motor):
    motor("integrity")
    assert client.get("/api/digitize/status").json() == {"available": False, "reason": "integrity_failed"}
    assert post_image(client, image_bytes()).json()["code"] == "unavailable"


def test_preview_returns_lines_confidence_and_draft_warning(client, motor):
    trace = motor("ok")
    response = post_image(client, image_bytes())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["text"] == "Capítulo 1 do Livro de Teste\nlinha fictícia incerta"
    assert [line["low_confidence"] for line in body["lines"]] == [False, True]
    assert [line["index"] for line in body["lines"]] == [0, 1]
    assert body["low_confidence_count"] == 1
    assert [w["code"] for w in body["warnings"]] == ["draft"]
    assert body["engine"] == {"name": "leitorum-motor", "version": "0.0.0-teste", "reader": "Leitor de Teste", "license_status": "VERIFIED"}
    assert "bbox" not in json.dumps(body)
    assert response.headers["cache-control"] == "no-store"
    assert_cleaned(trace)


def test_preview_without_text_warns(client, motor):
    motor("empty")
    body = post_image(client, image_bytes()).json()
    assert body["lines"] == [] and body["text"] == ""
    assert [w["code"] for w in body["warnings"]] == ["draft", "no_text"]


def test_preview_many_uncertain_warns(client, motor):
    motor("uncertain")
    body = post_image(client, image_bytes()).json()
    assert body["low_confidence_count"] == 2
    assert "many_uncertain" in [w["code"] for w in body["warnings"]]


def test_preview_accepts_jpeg_and_webp(client, motor):
    assert post_image(client, image_bytes("JPEG"), "foto.jpg", "image/jpeg").status_code == 200
    assert post_image(client, image_bytes("WEBP"), "foto.webp", "image/webp").status_code == 200


def test_preview_applies_camera_orientation(client, motor):
    trace = motor("ok")
    response = post_image(client, image_bytes("JPEG", (60, 40), orientation=6), "foto.jpg", "image/jpeg")
    assert response.status_code == 200
    assert json.loads(trace.read_text())["size"] == [40, 60]


@pytest.mark.parametrize(
    "data",
    [b"%PDF-1.4\n%fake\n", "apenas um texto de teste".encode(), None],
    ids=["pdf", "texto-renomeado", "gif"],
)
def test_preview_rejects_unsupported_format(client, motor, data):
    if data is None:
        data = image_bytes("GIF")
    response = post_image(client, data, "pagina.jpg", "image/jpeg")
    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_format"


def test_preview_rejects_truncated_image(client, motor):
    before = leftover_dirs()
    data = image_bytes("JPEG", (400, 300))
    response = post_image(client, data[: len(data) // 2], "foto.jpg", "image/jpeg")
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_image"
    assert leftover_dirs() <= before


def test_preview_rejects_file_over_size_limit(client, motor, monkeypatch):
    monkeypatch.setattr(digitize_service, "DIGITIZE_MAX_UPLOAD_BYTES", 1024)
    response = post_image(client, image_bytes(size=(400, 400)) + b"\0" * 2048)
    assert response.status_code == 413
    assert response.json()["code"] == "too_large"


def test_preview_rejects_image_over_pixel_limit(client, motor, monkeypatch):
    monkeypatch.setattr(digitize_service, "DIGITIZE_MAX_PIXELS", 100)
    response = post_image(client, image_bytes(size=(20, 20)))
    assert response.status_code == 413
    assert response.json()["code"] == "too_large"


@pytest.mark.parametrize("mode", ["crash", "bad_schema"])
def test_preview_engine_failure(client, motor, mode):
    trace = motor(mode)
    response = post_image(client, image_bytes())
    assert response.status_code == 500
    assert response.json()["code"] == "engine_failed"
    assert_cleaned(trace)


def test_preview_unreadable_by_engine(client, motor):
    trace = motor("unreadable")
    response = post_image(client, image_bytes())
    assert response.status_code == 422
    assert_cleaned(trace)


def test_preview_requires_authentication(client, motor, monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    assert client.get("/api/digitize/status").status_code == 401
    assert post_image(client, image_bytes()).status_code == 401


# --- US2: salvar como Estudo -----------------------------------------------------------------


def test_reviewed_text_saves_as_draft_study(client, motor):
    book = client.post("/api/books", json={"title": "Livro de Teste", "author": "Autor de Teste"}).json()
    chapter = client.post(f"/api/books/{book['id']}/chapters", json={"name": "Capítulo 1"}).json()
    preview = post_image(client, image_bytes()).json()
    reviewed = "Capítulo 1 do Livro de Teste\nlinha fictícia revisada"
    payload = {
        "chapter_id": chapter["id"],
        "title": "Página digitalizada de teste",
        "location": "",
        "source_response": preview["text"],
        "summary": "",
        "explanation": reviewed,
        "concepts": "",
        "references": "",
        "notes": "",
    }
    response = client.post("/api/studies", json=payload)
    assert response.status_code == 201, response.text
    study = response.json()
    assert study["reading_status"] == "rascunho"
    assert study["explanation"] == reviewed
    assert study["summary"] == ""
    assert study["source_response"] == preview["text"]

    empty = client.post("/api/studies", json={**payload, "explanation": "   "})
    assert empty.status_code in (409, 422)


# --- US3: um por vez, memória, limpeza, logs ------------------------------------------------------


def test_second_request_while_busy_is_refused(client, motor):
    trace = motor("ok")
    assert digitize_service._busy.acquire(blocking=False)
    try:
        response = post_image(client, image_bytes())
    finally:
        digitize_service._busy.release()
    assert response.status_code == 503
    assert response.json()["code"] == "busy"
    assert response.headers["retry-after"] == "15"
    assert not trace.exists()


def test_low_memory_is_refused_before_engine(client, motor, monkeypatch):
    trace = motor("ok")
    monkeypatch.setenv("LEITORUM_DIGITIZE_MIN_FREE_MB", "2048")
    monkeypatch.setattr(digitize_service, "available_memory", lambda: digitize_service.MemoryReading("commit", 1024))
    before = leftover_dirs()
    response = post_image(client, image_bytes())
    assert response.status_code == 503
    assert response.json()["code"] == "low_memory"
    assert not trace.exists()
    assert leftover_dirs() <= before


def test_unmeasurable_memory_does_not_block(client, motor, monkeypatch):
    monkeypatch.setenv("LEITORUM_DIGITIZE_MIN_FREE_MB", "2048")
    monkeypatch.setattr(digitize_service, "available_memory", lambda: None)
    assert post_image(client, image_bytes()).status_code == 200


def test_free_memory_is_measured_on_this_machine():
    reading = digitize_service.available_memory()
    assert reading is None or reading.available > 0
    if reading is not None and os.name == "nt":
        assert reading.measure == "commit"


# --- Feature 088: memória comprometível no Windows e motivo no log ----------------------------

MB = 2**20


@pytest.fixture
def windows_memory(monkeypatch):
    """Simula o Windows com RAM física e memória comprometível disponíveis em MB."""

    def use(physical_mb: int, commit_mb: int) -> None:
        status = digitize_service._MemoryStatus()
        status.ullAvailPhys = physical_mb * MB
        status.ullAvailPageFile = commit_mb * MB
        monkeypatch.setattr(digitize_service, "IS_WINDOWS", True)
        monkeypatch.setattr(digitize_service, "_windows_memory_status", lambda: status)

    return use


def test_windows_low_physical_but_ample_commit_reads(client, motor, monkeypatch, windows_memory):
    """A causa do relato: ~1,2 GB de RAM física livre recusava toda leitura com o mínimo de 2 GiB."""
    trace = motor("ok")
    monkeypatch.delenv("LEITORUM_DIGITIZE_MIN_FREE_MB")
    windows_memory(physical_mb=1200, commit_mb=18000)
    response = post_image(client, image_bytes())
    assert response.status_code == 200, response.text
    assert trace.is_file(), "o motor deveria ter sido chamado"


def test_windows_low_commit_is_refused_and_logged(client, motor, monkeypatch, windows_memory, caplog):
    trace = motor("ok")
    monkeypatch.delenv("LEITORUM_DIGITIZE_MIN_FREE_MB")
    windows_memory(physical_mb=6000, commit_mb=1024)
    with caplog.at_level("INFO", logger="leitorum.digitize"):
        response = post_image(client, image_bytes())
    assert response.status_code == 503
    assert response.json()["code"] == "low_memory"
    assert not trace.exists()
    assert "low_memory" in caplog.text
    assert "commit" in caplog.text
    assert "1024 MB" in caplog.text
    assert "2304 MB" in caplog.text


def test_min_free_env_applies_to_commit(client, motor, monkeypatch, windows_memory):
    monkeypatch.setenv("LEITORUM_DIGITIZE_MIN_FREE_MB", "20000")
    windows_memory(physical_mb=6000, commit_mb=18000)
    assert post_image(client, image_bytes()).json()["code"] == "low_memory"


def test_default_min_free_is_peak_plus_reserve(monkeypatch):
    monkeypatch.delenv("LEITORUM_DIGITIZE_MIN_FREE_MB", raising=False)
    assert get_digitize_min_free_bytes() == 2304 * MB


def test_engine_failure_logs_exit_code_and_type(client, motor, caplog):
    motor("crash")
    with caplog.at_level("INFO", logger="leitorum.digitize"):
        assert post_image(client, image_bytes()).status_code == 500
    assert "código 1" in caplog.text
    assert "RuntimeError" in caplog.text


def test_engine_failure_log_ignores_noisy_stderr(client, motor, caplog):
    motor("noisy_crash")
    with caplog.at_level("INFO", logger="leitorum.digitize"):
        assert post_image(client, image_bytes()).status_code == 500
    assert "ValueError" in caplog.text
    assert "Livro de Teste" not in caplog.text
    assert "modelos-ficticios" not in caplog.text


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (None, "desconhecido"),
        (b"", "desconhecido"),
        (b"[INFO] Using C:\\modelos-ficticios\\detector.onnx\nLivro de Teste\n", "desconhecido"),
        (b"\x1b[32m[INFO] aviso\x1b[0m\nIntegrityError\n\n", "IntegrityError"),
        (b"aviso qualquer\nnumpy.core._exceptions._ArrayMemoryError\n", "numpy.core._exceptions._ArrayMemoryError"),
    ],
)
def test_motor_error_type(tmp_path, content, expected):
    log = tmp_path / "motor.log"
    if content is not None:
        log.write_bytes(content)
    assert digitize_service.motor_error_type(log) == expected


@pytest.fixture
def killed(monkeypatch):
    """Registra os processos encerrados à força e confirma que terminaram."""
    processes = []
    original = digitize_service._kill

    def kill(process):
        original(process)
        processes.append(process.poll())

    monkeypatch.setattr(digitize_service, "_kill", kill)
    return processes


def test_timeout_kills_engine_and_cleans(client, motor, monkeypatch, killed):
    trace = motor("slow")
    monkeypatch.setattr(digitize_service, "DIGITIZE_TIMEOUT_SECONDS", 1.5)
    response = post_image(client, image_bytes())
    assert response.status_code == 504
    assert response.json()["code"] == "timeout"
    assert len(killed) == 1 and killed[0] is not None
    assert_cleaned(trace)


def test_client_disconnect_kills_engine_and_cleans(motor, killed):
    trace = motor("slow")
    calls = 0

    async def disconnected() -> bool:
        nonlocal calls
        calls += 1
        return calls > 2

    upload = UploadFile(file=io.BytesIO(image_bytes()), filename="pagina.png")
    with pytest.raises(DigitizeError) as error:
        asyncio.run(digitize_service.preview(upload, disconnected))
    assert error.value.code == "cancelled"
    assert len(killed) == 1 and killed[0] is not None
    assert_cleaned(trace)
    assert not digitize_service._busy.locked()


def test_logs_have_no_text_nor_temp_paths(client, motor, caplog):
    trace = motor("ok")
    with caplog.at_level("DEBUG"):
        assert post_image(client, image_bytes()).status_code == 200
        motor("crash")
        assert post_image(client, image_bytes()).status_code == 500
    workdir = json.loads(trace.read_text())["workdir"]
    assert "Livro de Teste" not in caplog.text
    assert "fictícia" not in caplog.text
    assert workdir not in caplog.text
    assert digitize_service.TEMP_PREFIX not in caplog.text
